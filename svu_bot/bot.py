import asyncio
from phoenix.framework.chatbot import ChatBot
import os

class SVUBot:
    """
    SVU Chatbot built using the Phoenix AI Framework Builder.
    Supports RAG-based insights from the svu_bot/data directory.
    Uses the official ChatBot high-level API.
    """
    def __init__(self):
        # Configure the bot using the high-level Builder
        self.bot_instance = (
            ChatBot(local=False)
            .with_openai(
                api_key="ak_2yp3Xw1Ny7ky2pF7er9x93ZO9jj6G",
                base_url="https://api.longcat.chat/openai"
            )
            .with_model(llm="LongCat-Flash-Lite")
            .with_rag(data_to_insight_path="./svu_bot/data")
            .with_memory()
            .with_system_prompt("You are a helpful assistant for Syrian Virtual University (SVU) students.")
            .build()
        )

    async def chat(self, prompt: str, session_id: str = "svu_session"):
        """Runs a chat interaction."""
        self.bot_instance.set_session(session_id)
        return await self.bot_instance.chat(text=prompt)

if __name__ == "__main__":
    bot = SVUBot()
    async def run_test():
        # ChatBotInstance handles startup internally during first chat
        response = await bot.chat("Tell me about SVU programs.")
        print(f"Bot: {response}")
    
    asyncio.run(run_test())
