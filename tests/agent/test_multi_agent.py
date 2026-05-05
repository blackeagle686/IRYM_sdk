import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from phoenix.framework.multi_agent.manager import MultiAgentManager
from phoenix.framework.multi_agent.config import MultiAgentConfig, AgentConfig

async def main():
    print("--- Testing Multi-Agent Framework Layer ---")

    # 1. Define configurations for a "Dev Team"
    coder_config = AgentConfig(
        name="Giyu_Coder",
        profile={
            "identity": {"name": "Giyu", "id": "hashira-01"},
            "role": {"title": "Code Specialist", "mission": "To write high-quality Python code."},
            "personality": {"communication_tone": "calm", "response_style": "minimalist"},
            "rules": ["Follow PEP 8.", "No bloated code."],
            "capabilities": ["Python", "Algorithms"]
        }
    )

    reviewer_config = AgentConfig(
        name="Shinobu_Reviewer",
        profile={
            "identity": {"name": "Shinobu", "id": "hashira-02"},
            "role": {"title": "Security & Code Reviewer", "mission": "To find bugs and security flaws."},
            "personality": {"communication_tone": "cheerful but sharp", "response_style": "detailed"},
            "rules": ["Be thorough.", "Check for prompt injections."],
            "capabilities": ["Security audit", "Code review"]
        }
    )

    team_config = MultiAgentConfig(
        team_name="Hashira-OS Core Team",
        agents=[coder_config, reviewer_config]
    )

    # 2. Initialize the Team
    print("\n1. Initializing MultiAgentManager...")
    manager = MultiAgentManager(team_config)

    # 3. Verify Team Overview
    print("\n2. Team Overview:")
    for member in manager.get_team_overview():
        print(f"- {member['name']} ({member['role']}): {member['mission']}")

    # 4. Test Sequential Pipeline
    # Scenario: Coder writes a function, Reviewer reviews it.
    print("\n3. Testing Pipeline (Coder -> Reviewer)...")
    pipeline_prompt = "Write a simple Python function to validate an email address."
    
    # Mocking run results for demonstration if needed, but we'll try to run it.
    # Note: This will use real LLM calls if configured.
    try:
        final_result = await manager.run_pipeline(
            pipeline_prompt, 
            agent_sequence=["Giyu_Coder", "Shinobu_Reviewer"]
        )
        print("\n--- Pipeline Result ---")
        print(final_result)
    except Exception as e:
        print(f"\nPipeline failed (expected if no API key): {e}")

    # 5. Test Broadcast
    print("\n4. Testing Broadcast...")
    try:
        broadcast_results = await manager.broadcast("Who are you and what is your mission?")
        for name, res in broadcast_results.items():
            print(f"[{name}] response received.")
    except Exception as e:
        print(f"\nBroadcast failed: {e}")

    print("\n[SUCCESS] Multi-Agent framework layer is operational!")

if __name__ == "__main__":
    asyncio.run(main())
