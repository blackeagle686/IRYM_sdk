import asyncio
import os
from phoenix.framework.chatbot import ChatBot

# Import modular NLP steps (Each handled by a different team member)
from svu_bot.nlp.step1_cleaner import TextCleaner
from svu_bot.nlp.step2_intent import IntentDetector
from svu_bot.nlp.step3_entities import EntityExtractor
from svu_bot.nlp.step4_adapter import OutputAdapter
from svu_bot.nlp.step5_auditor import InteractionAuditor

# Calculate absolute path for data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data")

class SVUBot:
    """
    SVU Bot Orchestrator.
    Maintained by Member 1 of the Core Team.
    Integrates the high-level Phoenix framework with a modular NLP pipeline.
    """
    def __init__(self):
        # Configure the bot instance
        self.bot_instance = (
            ChatBot(local=False)
            .with_openai(
                api_key="ak_2yp3Xw1Ny7ky2pF7er9x93ZO9jj6G",
                base_url="https://api.longcat.chat/openai"
            )
            .with_model(llm="LongCat-Flash-Lite")
            .with_rag(data_to_insight_path=DATA_PATH)
            .with_memory()
            .with_system_prompt("You are a helpful assistant for South Vally University (SVU) students.")
            .build()
        )

    async def chat(self, prompt: str, session_id: str = "svu_session"):
        """Runs a chat interaction through the 5-step NLP and Framework layers."""
        
        # Step 1: Cleaning (Member 1)
        cleaned_prompt = TextCleaner.process(prompt)
        
        # Step 2: Intent Detection (Member 2)
        intent = IntentDetector.process(cleaned_prompt)
        
        # Step 3: Entity Extraction (Member 3)
        entities = EntityExtractor.process(cleaned_prompt)
        
        # Framework Generation
        self.bot_instance.set_session(session_id)
        raw_response = await self.bot_instance.chat(text=cleaned_prompt)
        
        # Step 4: Output Adaptation (Member 4)
        final_response = OutputAdapter.process(raw_response)
        
        # Step 5: Team Auditing (Member 5)
        InteractionAuditor.process(session_id, cleaned_prompt, final_response, intent)
        
        return final_response

if __name__ == "__main__":
    bot = SVUBot()
    async def run_test():
        response = await bot.chat("Tell me about the BAIT program.")
        print(f"Bot: {response}")
    
    asyncio.run(run_test())
