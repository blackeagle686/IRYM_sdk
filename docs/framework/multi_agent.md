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

## 🧠 Full Complex Example

Here is a complete, runable example demonstrating how to set up a powerful 3-agent team ("Architect", "Coder", and "Reviewer") that collaborates to solve a complex software engineering problem. 

In this example, the **Architect** designs the solution, the **Coder** writes the implementation, and the **Reviewer** performs a security and code quality audit. Because each agent inherits the full Phoenix cognitive loop, they autonomously utilize tools (like web search or file writing) if required.

```python
import asyncio
from phoenix.framework.multi_agent.manager import MultiAgentManager
from phoenix.framework.multi_agent.config import MultiAgentConfig, AgentConfig

async def run_hashira_team():
    # 1. Define the specific Agent Profiles
    architect_config = AgentConfig(
        name="Tengen_Architect",
        llm_type="openai",
        profile={
            "identity": {"name": "Tengen", "id": "hashira-arch-01"},
            "role": {"title": "System Architect", "mission": "Design robust and scalable software architectures."},
            "personality": {"communication_tone": "flamboyant and direct", "response_style": "detailed"},
            "rules": ["Always outline a clear step-by-step plan."],
            "capabilities": ["System Design", "Architecture"],
            "tool_access": ["web_search"]
        }
    )

    coder_config = AgentConfig(
        name="Giyu_Coder",
        llm_type="openai", 
        profile={
            "identity": {"name": "Giyu", "id": "hashira-code-02"},
            "role": {"title": "Lead Developer", "mission": "Write precise, bug-free Python code based on architectural plans."},
            "personality": {"communication_tone": "calm and quiet", "response_style": "code-heavy"},
            "rules": ["Follow PEP 8.", "Do not write bloated code.", "Always include type hints."],
            "capabilities": ["Python", "Algorithms", "Implementation"],
            "tool_access": ["python_repl", "file_write"]
        }
    )

    reviewer_config = AgentConfig(
        name="Shinobu_Reviewer",
        llm_type="openai",
        profile={
            "identity": {"name": "Shinobu", "id": "hashira-rev-03"},
            "role": {"title": "Security & Code Reviewer", "mission": "Find bugs, security flaws, and test the provided code."},
            "personality": {"communication_tone": "cheerful but sharp", "response_style": "analytical"},
            "rules": ["Be thorough in code reviews.", "Highlight any potential edge cases."],
            "capabilities": ["Security audit", "Code review", "Testing"],
            "tool_access": ["python_repl"]
        }
    )

    # 2. Group them into a Team Configuration
    team_config = MultiAgentConfig(
        team_name="Hashira-OS Task Force",
        agents=[architect_config, coder_config, reviewer_config]
    )

    # 3. Initialize the Manager
    manager = MultiAgentManager(team_config)

    # 4. Define the complex problem
    problem_statement = (
        "We need a Python implementation of a Thread-Safe LRU (Least Recently Used) Cache. "
        "It needs to have `get`, `put`, and `get_cache_size` methods. "
        "Please provide the full code and a security/performance review."
    )
    
    # 5. Run the collaborative pipeline!
    # Tengen creates the plan -> Giyu writes the code -> Shinobu reviews it.
    print("Launching Pipeline...")
    final_result = await manager.run_pipeline(
        prompt=problem_statement, 
        agent_sequence=["Tengen_Architect", "Giyu_Coder", "Shinobu_Reviewer"]
    )
    
    print("\n--- Final Output from Shinobu (Reviewer) ---")
    print(final_result)

if __name__ == "__main__":
    asyncio.run(run_hashira_team())
```

---

## 🏗️ Architecture

Every agent created by the manager follows the full **Phoenix Agent Architecture**:
- **Thinker:** Objective deconstruction.
- **Planner:** Multi-step tool selection.
- **Actor:** Parallel tool execution.
- **Reflector:** Success verification and learning.

By leveraging the `AgentProfile` system, each agent in the team maintains its unique personality and follows its specific set of rules during the entire collaboration.
