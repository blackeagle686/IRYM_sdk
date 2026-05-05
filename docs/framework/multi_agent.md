# 🤖 Multi-Agent Framework Layer

The Phoenix Multi-Agent layer allows you to orchestrate teams of autonomous agents to solve complex tasks through collaboration, parallel execution, and structured pipelines.

## 🌟 Key Concepts

### 1. The Multi-Agent Manager
The `MultiAgentManager` is the central orchestrator. It manages the lifecycle of multiple agents and provides high-level patterns for agent interaction.

### 2. Orchestration Patterns

#### 📡 Broadcast (Parallel)
The same prompt is sent to all agents in the team simultaneously. This is ideal for brainstorming, getting multiple perspectives, or distributed processing.
- **Method:** `await manager.broadcast(prompt)`
- **Behavior:** Parallel execution using `asyncio.gather`.

#### 🔗 Pipeline (Sequential)
Agents are executed in a predefined sequence, where the output of one agent becomes the input for the next. This is perfect for review cycles or multi-stage workflows.
- **Method:** `await manager.run_pipeline(prompt, ["AgentA", "AgentB"])`
- **Behavior:** Sequential hand-off.

#### 🎯 Targeted
Send a prompt directly to a specific agent within the team.
- **Method:** `await manager.run_targeted("AgentName", prompt)`

---

## 🛠️ Configuration

Multi-agent teams are defined using a structured configuration schema:

```python
from phoenix.framework import MultiAgentConfig, AgentConfig

config = MultiAgentConfig(
    team_name="Hashira-OS Team",
    agents=[
        AgentConfig(
            name="Giyu",
            profile="profiles/giyu.json",  # Identity & Role
            llm_type="openai"
        ),
        AgentConfig(
            name="Shinobu",
            profile="profiles/shinobu.json",
            llm_type="local"  # Mixing different LLMs is supported!
        )
    ]
)
```

---

## 🚀 Example Usage

```python
from phoenix.framework import MultiAgentManager

# 1. Initialize the team
manager = MultiAgentManager(config)

# 2. Run a "Dev & Review" pipeline
result = await manager.run_pipeline(
    prompt="Design a secure authentication module",
    agent_sequence=["Giyu", "Shinobu"]
)

print(f"Final Outcome: {result}")
```

---

## 🏗️ Architecture

Every agent created by the manager follows the full **Phoenix Agent Architecture**:
- **Thinker:** Objective deconstruction.
- **Planner:** Multi-step tool selection.
- **Actor:** Parallel tool execution.
- **Reflector:** Success verification and learning.

By leveraging the `AgentProfile` system, each agent in the team maintains its unique personality and follows its specific set of rules during the entire collaboration.
