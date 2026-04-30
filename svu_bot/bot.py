import asyncio
import os
from phoenix.framework.chatbot import ChatBot
from svu_bot.nlp.pipeline import SVUNLPProcessor

# Calculate absolute path for data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data")

class SVUBot:
    """
    SVU Bot Orchestrator.
    Integrates the high-level Phoenix framework with a custom 5-step NLP pipeline.
    """
    def __init__(self):
        # NLP Processor for team-specific logic
        self.nlp = SVUNLPProcessor()
        
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
            .with_system_prompt("You are a helpful assistant for Syrian Virtual University (SVU) students.")
            .build()
        )

    async def chat(self, prompt: str, session_id: str = "svu_session"):
        """Runs a chat interaction through the NLP and Framework layers."""
        
        # 1. Pre-processing: Inbound NLP (Clean, Intent, Entities)
        nlp_data = self.nlp.process_input(prompt)
        cleaned_prompt = nlp_data["text"]
        intent = nlp_data["intent"]
        
        # 2. Phoenix Framework Generation (RAG + Memory)
        self.bot_instance.set_session(session_id)
        raw_response = await self.bot_instance.chat(text=cleaned_prompt)
        
        # 3. Post-processing: Output Adaptation
        final_response = self.nlp.adapt_output(raw_response)
        
        # 4. Team Auditing
        self.nlp.log_interaction(session_id, cleaned_prompt, final_response, intent)
        
        return final_response

if __name__ == "__main__":
    bot = SVUBot()
    async def run_test():
        response = await bot.chat("Tell me about the BAIT program.")
        print(f"Bot: {response}")
    
    asyncio.run(run_test())
