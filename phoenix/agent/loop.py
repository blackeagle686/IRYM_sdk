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
        # Step 1: Think (understand objective)
        objective = await self.thinker.analyze(prompt, memory, session_id)
        
        # Store in session state
        memory.session.set("current_objective", objective)
        await memory.add_interaction(session_id, "system", f"Identified Objective: {objective}")

        # Step 2: Analyze (understand project structure)
        analysis = await self.analyzer.analyze_workspace(prompt)
        memory.session.set("project_analysis", analysis)
        await memory.add_interaction(session_id, "system", f"Project Analysis Complete: Identified tech stack as {analysis['tech_stack']}")

        previous_results = ""
        final_answer = ""

        for i in range(max_iterations):
            # Step 3: Plan (select actions)
            plan = await self.planner.plan(objective, previous_results)
            
            # Step 4: Act (execute tools in parallel)
            actions = plan.get("actions", [])
            if not actions and "tool" in plan:
                actions = [{"tool": plan["tool"]}]
                
            if any(a.get("tool") == "finish" for a in actions):
                final_answer = previous_results or "Task completed without actions."
                break
                
            action_result = await self.actor.execute(plan)
            
            # Step 5: Reflect (evaluate progress)
            reflection = await self.reflector.reflect(objective, plan, action_result)
            
            # Update memory
            memory.reflection.add_reflection(reflection["reflection"])
            await memory.consolidate_reflections(self.reflector.llm)
            
            await memory.add_interaction(
                session_id, 
                "system", 
                f"Action: {plan}\nResult: {action_result}\nReflection: {reflection['reflection']}"
            )
            
            previous_results += f"\nAction: {plan}\nResult: {action_result}\n"
            
            if reflection["is_complete"]:
                final_answer = action_result
                break

        if not final_answer:
            final_answer = "Agent stopped after reaching maximum iterations without completing the objective."

        await memory.add_interaction(session_id, "assistant", final_answer)
        return final_answer
