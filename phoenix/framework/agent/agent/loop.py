from phoenix.framework.agent.cognition.thinker import Thinker
from phoenix.framework.agent.cognition.planner import Planner
from phoenix.framework.agent.cognition.reflector import Reflector
from phoenix.framework.agent.cognition.analyzer import Analyzer
from phoenix.framework.agent.cognition.actor import Actor
from phoenix.framework.agent.cognition.utils import generate_unique_id
import asyncio

class AgentLoop:
    """
    Coordinates the autonomous workflow:
    Think -> Analyze -> Plan -> Act -> Reflect
    """
    def __init__(self, thinker: Thinker, planner: Planner, actor: Actor, reflector: Reflector, analyzer: Analyzer):
        self.thinker = thinker
        self.planner = planner
        self.actor = actor
        self.reflector = reflector
        self.analyzer = analyzer
        self._background_tasks = set()

    def _schedule_background(self, coro):
        task = asyncio.create_task(coro)
        self._background_tasks.add(task)

        def _on_done(t):
            self._background_tasks.discard(t)
            try:
                _ = t.exception()
            except Exception:
                pass

        task.add_done_callback(_on_done)

    async def run(self, prompt: str, memory, session_id: str, max_iterations: int = 5) -> str:
        """
        Executes the cognitive loop.
        Workflow: prompt -> Thinker(STM) -> Analyzer(Cache) -> Planner(Task Update) -> Actor -> Reflector(LTM)
        """
        # Step 1: Thinker (Uses Short-Term Memory via memory.get_full_context)
        # Step 2: Analyzer (Uses cached file analysis)
        think_task = self.thinker.analyze(prompt, memory, session_id)
        analyze_task = self.analyzer.analyze_workspace(prompt)
        
        objective, analysis = await asyncio.gather(think_task, analyze_task)
        
        # Initialize task tracking
        task_file_id = generate_unique_id()
        memory.session.set("current_objective", objective)
        memory.session.set("project_analysis", analysis)
        memory.session.set("task_file_id", task_file_id)
        
        previous_results = ""
        final_answer = ""
        actions_taken = 0

        for i in range(max_iterations):
            # Step 3: Planner (Updates task status via task_file_id)
            plan = await self.planner.plan(objective, task_file_id=task_file_id, previous_results=previous_results)
            
            actions = plan.get("actions", [])
            if not actions and "tool" in plan:
                actions = [{"tool": plan["tool"]}]
                
            if any(a.get("tool") == "finish" for a in actions):
                if actions_taken == 0:
                    previous_results += "\nPlanner attempted to finish without actions. Validating...\n"
                    continue
                final_answer = previous_results or "Task completed successfully."
                break
            
            # Step 4: Actor (Execute tools)
            action_result = await self.actor.execute(plan)
            actions_taken += len([a for a in actions if a.get("tool") != "finish"])
            
            # Step 5: Reflector (Evaluation + LTM storage)
            reflection = await self.reflector.reflect(objective, plan, action_result)
            
            # Save to Memory (Short-Term + Long-Term)
            memory.reflection.add_reflection(reflection["reflection"])
            
            async def memory_updates():
                await asyncio.gather(
                    memory.add_interaction(session_id, "system", f"Action Result: {action_result}"),
                    # Step 6: Reflector adds to Long-Term Memory
                    memory.long_term.add(session_id, f"Learned from {objective}: {reflection['reflection']}"),
                    memory.consolidate_reflections(self.reflector.llm)
                )

            self._schedule_background(memory_updates())
            
            previous_results += f"\nAction: {plan}\nResult: {action_result}\nReflection: {reflection['reflection']}\n"
            
            if reflection["is_complete"]:
                final_answer = action_result
                break

        if not final_answer:
            final_answer = "Maximum iterations reached without full completion."

        await memory.add_interaction(session_id, "assistant", final_answer)
        return final_answer

    async def run_stream(self, prompt: str, memory, session_id: str, max_iterations: int = 5):
        """
        Streaming version of the workflow.
        """
        yield {"type": "status", "content": "🤔 Thinking & Analyzing..."}
        think_task = self.thinker.analyze(prompt, memory, session_id)
        analyze_task = self.analyzer.analyze_workspace(prompt)
        objective, analysis = await asyncio.gather(think_task, analyze_task)

        task_file_id = generate_unique_id()
        memory.session.set("current_objective", objective)
        memory.session.set("project_analysis", analysis)
        
        previous_results = ""
        final_answer = ""
        actions_taken = 0

        for i in range(max_iterations):
            yield {"type": "status", "content": f"📋 Planning step {i + 1}..."}
            
            # Stream the thinking part of the planner
            async for thought in self.planner.stream_thinking(objective, task_file_id=task_file_id, previous_results=previous_results):
                yield {"type": "chunk", "content": thought}
            
            plan = await self.planner.plan(objective, task_file_id=task_file_id, previous_results=previous_results)
            actions = plan.get("actions", [])
            if not actions and "tool" in plan:
                actions = [{"tool": plan["tool"]}]

            if any(a.get("tool") == "finish" for a in actions):
                if actions_taken == 0:
                    previous_results += "\nWaiting for concrete tool results...\n"
                    continue
                final_answer = previous_results or "Done."
                break

            yield {"type": "status", "content": "🛠️ Executing actions..."}
            action_result = await self.actor.execute(plan)
            actions_taken += len([a for a in actions if a.get("tool") != "finish"])

            yield {"type": "status", "content": "🧐 Reflecting..."}
            reflection = await self.reflector.reflect(objective, plan, action_result)
            memory.reflection.add_reflection(reflection["reflection"])
            
            async def memory_updates():
                await asyncio.gather(
                    memory.add_interaction(session_id, "system", f"Result: {action_result}"),
                    memory.long_term.add(session_id, reflection["reflection"]),
                    memory.consolidate_reflections(self.reflector.llm)
                )
            self._schedule_background(memory_updates())

            previous_results += f"\nResult: {action_result}\n"
            if reflection["is_complete"]:
                final_answer = action_result
                break

        yield {"type": "status", "content": "✅ Finalizing..."}
        await memory.add_interaction(session_id, "assistant", final_answer)
        for chunk in final_answer.split():
            yield {"type": "chunk", "content": chunk + " "}
