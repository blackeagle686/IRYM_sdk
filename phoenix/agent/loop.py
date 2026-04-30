from phoenix.cognition.thinker import Thinker
from phoenix.cognition.planner import Planner
from phoenix.cognition.reflector import Reflector
from phoenix.cognition.analyzer import Analyzer
from phoenix.execution.actor import Actor
import asyncio

class AgentLoop:
    """Coordinates the Think -> Plan -> Act -> Reflect cycle."""
    def __init__(self, thinker: Thinker, planner: Planner, actor: Actor, reflector: Reflector, analyzer: Analyzer):
        self.thinker = thinker
        self.planner = planner
        self.actor = actor
        self.reflector = reflector
        self.analyzer = analyzer

    async def run(self, prompt: str, memory, session_id: str, max_iterations: int = 5) -> str:
        # Step 1 & 2: Parallel Awareness (Think + Analyze)
        think_task = self.thinker.analyze(prompt, memory, session_id)
        analyze_task = self.analyzer.analyze_workspace(prompt)
        
        # Concurrent execution of the initial cognitive steps
        objective, analysis = await asyncio.gather(think_task, analyze_task)
        
        # Store results in session state
        memory.session.set("current_objective", objective)
        memory.session.set("project_analysis", analysis)
        
        # Concurrent system logging
        await asyncio.gather(
            memory.add_interaction(session_id, "system", f"Identified Objective: {objective}"),
            memory.add_interaction(session_id, "system", f"Project Analysis: {analysis['tech_stack']}")
        )

        previous_results = ""
        final_answer = ""
        actions_taken = 0

        for i in range(max_iterations):
            # Step 3: Plan (select actions)
            plan = await self.planner.plan(objective, previous_results)
            
            # Step 4: Act (execute tools in parallel)
            actions = plan.get("actions", [])
            if not actions and "tool" in plan:
                actions = [{"tool": plan["tool"]}]
                
            if any(a.get("tool") == "finish" for a in actions):
                if actions_taken == 0:
                    previous_results += (
                        "\nPlanner attempted to finish without executing any tool actions. "
                        "Completion is not yet validated.\n"
                    )
                    continue
                final_answer = previous_results or "Task completed."
                break
                
            action_result = await self.actor.execute(plan)
            actions_taken += len([a for a in actions if a.get("tool") != "finish"])
            
            # Step 5: Reflect (evaluate progress)
            reflection = await self.reflector.reflect(objective, plan, action_result)
            
            # Parallel update of memory and reflection state
            memory.reflection.add_reflection(reflection["reflection"])
            await asyncio.gather(
                memory.consolidate_reflections(self.reflector.llm),
                memory.add_interaction(
                    session_id, 
                    "system", 
                    f"Action: {plan}\nResult: {action_result}\nReflection: {reflection['reflection']}"
                )
            )
            
            previous_results += f"\nAction: {plan}\nResult: {action_result}\n"
            
            if reflection["is_complete"]:
                final_answer = action_result
                break

        if not final_answer:
            final_answer = "Agent stopped after reaching maximum iterations without completing the objective."

        await memory.add_interaction(session_id, "assistant", final_answer)
        return final_answer

    async def run_stream(self, prompt: str, memory, session_id: str, max_iterations: int = 5):
        """
        Streaming run mode:
        - emits {'type': 'status', 'content': ...} for cognition/execution updates
        - emits {'type': 'chunk', 'content': ...} for final user-visible response chunks
        """
        yield {"type": "status", "content": "Analyzing objective and workspace..."}
        think_task = self.thinker.analyze(prompt, memory, session_id)
        analyze_task = self.analyzer.analyze_workspace(prompt)
        objective, analysis = await asyncio.gather(think_task, analyze_task)

        memory.session.set("current_objective", objective)
        memory.session.set("project_analysis", analysis)
        await asyncio.gather(
            memory.add_interaction(session_id, "system", f"Identified Objective: {objective}"),
            memory.add_interaction(session_id, "system", f"Project Analysis: {analysis['tech_stack']}")
        )

        previous_results = ""
        final_answer = ""
        actions_taken = 0

        for i in range(max_iterations):
            yield {"type": "status", "content": f"Planner thinking (iteration {i + 1})..."}
            async for thought in self.planner.stream_thinking(objective, previous_results):
                yield {"type": "chunk", "content": thought}
            yield {"type": "chunk", "content": "\n"}

            plan = await self.planner.plan(objective, previous_results)
            actions = plan.get("actions", [])
            if not actions and "tool" in plan:
                actions = [{"tool": plan["tool"]}]

            if any(a.get("tool") == "finish" for a in actions):
                if actions_taken == 0:
                    previous_results += (
                        "\nPlanner attempted to finish without executing any tool actions. "
                        "Completion is not yet validated.\n"
                    )
                    continue
                final_answer = previous_results or "Task completed."
                break

            yield {"type": "status", "content": "Executing planned actions..."}
            action_result = await self.actor.execute(plan)
            actions_taken += len([a for a in actions if a.get("tool") != "finish"])

            reflection = await self.reflector.reflect(objective, plan, action_result)
            memory.reflection.add_reflection(reflection["reflection"])
            await asyncio.gather(
                memory.consolidate_reflections(self.reflector.llm),
                memory.add_interaction(
                    session_id,
                    "system",
                    f"Action: {plan}\nResult: {action_result}\nReflection: {reflection['reflection']}"
                )
            )

            previous_results += f"\nAction: {plan}\nResult: {action_result}\n"
            if reflection["is_complete"]:
                final_answer = action_result
                break

        if not final_answer:
            final_answer = "Agent stopped after reaching maximum iterations without completing the objective."

        await memory.add_interaction(session_id, "assistant", final_answer)
        yield {"type": "status", "content": "Preparing final response..."}
        for line in final_answer.splitlines() or [final_answer]:
            yield {"type": "chunk", "content": f"{line}\n"}
