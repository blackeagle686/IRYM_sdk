import asyncio
from typing import Dict, List, Any, Optional, Union
from phoenix.framework.agent.core.agent import Agent
from phoenix.framework.multi_agent.config import MultiAgentConfig, AgentConfig
from phoenix.framework.agent.memory.hybrid import HybridMemory
from phoenix.framework.agent.utils import parse_llm_json
from phoenix.services.llm.openai import OpenAILLM
from phoenix.services.llm.local import LocalLLM
from phoenix.services.observability.logger import get_logger

logger = get_logger("Phoenix AI.MultiAgent")

class MultiAgentManager:
    """
    Orchestrates a team of Phoenix Agents.
    Supports parallel execution, broadcasting, and sequenced pipelines.
    """
    def __init__(self, config: MultiAgentConfig):
        self.config = config
        self.agents: Dict[str, Agent] = {}
        self.shared_memory = HybridMemory() if self.config.shared_memory else None
        
        # Internal LLM for routing/manager tasks
        self._router_llm = OpenAILLM()
        
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all agents based on the multi-agent configuration."""
        for agent_cfg in self.config.agents:
            # Setup LLM based on config
            llm = self._setup_llm(agent_cfg)
            
            # Instantiate the standard Phoenix Agent
            agent = Agent(
                llm=llm,
                memory=self.shared_memory,
                profile=agent_cfg.profile,
                **agent_cfg.component_overrides
            )
            
            self.agents[agent_cfg.name] = agent
            logger.info(f"Initialized agent '{agent_cfg.name}' for team '{self.config.team_name}'")

    def _setup_llm(self, agent_cfg: AgentConfig):
        """Internal helper to setup LLM provider from config."""
        if agent_cfg.llm_type == "openai":
            return OpenAILLM(**agent_cfg.llm_params)
        elif agent_cfg.llm_type == "local":
            return LocalLLM(**agent_cfg.llm_params)
        return None

    def get_agent(self, name: str) -> Optional[Agent]:
        """Retrieve an agent by name."""
        return self.agents.get(name)

    async def broadcast(self, prompt: str, session_id: str = None) -> Dict[str, str]:
        """Send the same prompt to all agents in the team in parallel."""
        tasks = []
        names = list(self.agents.keys())
        for name in names:
            tasks.append(self.agents[name].run(prompt, session_id=session_id))
        
        results = await asyncio.gather(*tasks)
        return dict(zip(names, results))

    async def run_pipeline(self, prompt: str, agent_sequence: List[str], session_id: str = None) -> str:
        """
        Execute a sequenced pipeline where each agent's output becomes the input for the next.
        
        Example: [ 'Researcher', 'Writer', 'Proofreader' ]
        """
        current_data = prompt
        for agent_name in agent_sequence:
            agent = self.get_agent(agent_name)
            if not agent:
                logger.error(f"Agent '{agent_name}' not found in pipeline.")
                continue
            
            logger.info(f"Pipeline Step: {agent_name} is processing...")
            current_data = await agent.run(current_data, session_id=session_id)
            
        return current_data

    async def run_targeted(self, agent_name: str, prompt: str, session_id: str = None) -> str:
        """Run a specific agent by name."""
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found.")
        return await agent.run(prompt, session_id=session_id)

    def get_team_overview(self) -> List[Dict[str, Any]]:
        """Return a summary of all agents in the team."""
        overview = []
        for name, agent in self.agents.items():
            overview.append({
                "name": name,
                "role": agent.profile.role.title if agent.profile else "Unknown",
                "mission": agent.profile.role.mission if agent.profile else "None",
                "capabilities": agent.profile.capabilities if agent.profile else []
            })
        return overview

    async def run_autonomous(self, prompt: str, session_id: str = None) -> str:
        """
        Lead Router: Automatically determines the best agent for the task and delegates it.
        """
        overview = self.get_team_overview()
        
        system_prompt = f"""
        You are the Lead Orchestrator for a team of autonomous agents.
        Your job is to read the user's prompt and decide which agent is best suited to handle it.
        
        Available Agents:
        {overview}
        
        Respond ONLY with a valid JSON object:
        {{
            "selected_agent": "Exact Name of the Agent",
            "reason": "Brief reason why"
        }}
        """
        
        # Make sure router LLM is initialized
        if hasattr(self._router_llm, "client") and self._router_llm.client is None:
            if hasattr(self._router_llm, "init"):
                await self._router_llm.init()
                
        response = await self._router_llm.generate(f"{system_prompt}\n\nUser Prompt: {prompt}", session_id=None)
        data = parse_llm_json(response)
        
        if not data or "selected_agent" not in data:
            logger.error("Failed to parse router output, falling back to first agent.")
            selected = list(self.agents.keys())[0]
        else:
            selected = data["selected_agent"]
            
        logger.info(f"Router selected '{selected}' to handle the task.")
        return await self.run_targeted(selected, prompt, session_id=session_id)

    async def run_with_review(self, prompt: str, doer: str, reviewer: str, max_loops: int = 3, session_id: str = None) -> str:
        """
        Runs a self-correcting loop where a doer executes, and a reviewer checks the work.
        If the reviewer rejects the work, it goes back to the doer with feedback.
        """
        doer_agent = self.get_agent(doer)
        reviewer_agent = self.get_agent(reviewer)
        
        if not doer_agent or not reviewer_agent:
            raise ValueError("Doer or Reviewer agent not found.")
            
        current_prompt = prompt
        history_context = ""
        
        for loop in range(max_loops):
            logger.info(f"[Review Loop {loop+1}/{max_loops}] {doer} is working...")
            
            # The doer does the work
            doer_output = await doer_agent.run(current_prompt, session_id=session_id)
            
            logger.info(f"[Review Loop {loop+1}/{max_loops}] {reviewer} is reviewing...")
            # The reviewer reviews the work
            review_prompt = f"""
            You are reviewing the output of another agent.
            Original Objective: {prompt}
            Previous Feedback Context: {history_context}
            
            Agent Output:
            {doer_output}
            
            Provide a strict review. Your response MUST be valid JSON:
            {{
                "is_approved": boolean,
                "feedback": "If approved, a short final summary. If not approved, explicit instructions on what must be fixed."
            }}
            """
            
            # Use raw LLM for reviewer to guarantee strict JSON formatting without full Agent overhead
            if hasattr(reviewer_agent.llm, "client") and reviewer_agent.llm.client is None:
                if hasattr(reviewer_agent.llm, "init"):
                    await reviewer_agent.llm.init()
            
            review_response = await reviewer_agent.llm.generate(review_prompt, session_id=None)
            review_data = parse_llm_json(review_response)
            
            if not review_data:
                logger.warning("Failed to parse review JSON. Assuming approved.")
                return doer_output
                
            if review_data.get("is_approved", False):
                logger.info("Reviewer approved the output!")
                return doer_output
            else:
                feedback = review_data.get("feedback", "Unknown errors. Please revise.")
                logger.warning(f"Reviewer rejected. Feedback: {feedback}")
                
                # Setup next iteration
                history_context += f"\\nFailed Attempt {loop+1}: {feedback}"
                current_prompt = f"Your previous output was rejected. Please fix these specific issues:\n{feedback}\n\nOriginal prompt: {prompt}"
                
        logger.error(f"Max review loops ({max_loops}) reached. Returning last output.")
        return doer_output
