import asyncio
from typing import Dict, List, Any, Optional, Union
from phoenix.framework.agent.core.agent import Agent
from phoenix.framework.multi_agent.config import MultiAgentConfig, AgentConfig
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
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all agents based on the multi-agent configuration."""
        for agent_cfg in self.config.agents:
            # Setup LLM based on config
            llm = self._setup_llm(agent_cfg)
            
            # Instantiate the standard Phoenix Agent
            agent = Agent(
                llm=llm,
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
                "mission": agent.profile.role.mission if agent.profile else "None"
            })
        return overview
