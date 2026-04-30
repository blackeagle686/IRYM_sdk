import asyncio
from phoenix.agent.agent import Agent
from phoenix.llm.openai import OpenAILLM
from phoenix import init_phoenix, startup_phoenix
import os

class SVUBot:
    """
    SVU Chatbot built using the Phoenix AI Framework.
    Supports RAG-based insights from the svu_bot/data directory.
    """
    def __init__(self):
        # Configure the bot with LongCat LLM
        self.llm = OpenAILLM(
            api_key="ak_2yp3Xw1Ny7ky2pF7er9x93ZO9jj6G",
            base_url="https://api.longcat.chat/openai",
            model="LongCat-Flash-Lite"
        )
        self.agent = None

    async def initialize(self):
        print("Initializing SVU Bot services...")
        init_phoenix()
        await startup_phoenix()
        
        # Initialize Agent with our custom LLM
        self.agent = Agent(llm=self.llm)
        await self.llm.init()
        print("SVU Bot is ready.")

    async def chat(self, prompt: str, session_id: str = "svu_session"):
        """Runs a chat interaction."""
        if not self.agent:
            await self.initialize()
        
        # The agent naturally uses its memory layers (STM/LTM) 
        # which can be primed with data from the data/ folder.
        return await self.agent.run(prompt, session_id=session_id)

    async def stream_chat(self, prompt: str, session_id: str = "svu_session"):
        """Streams a chat interaction."""
        if not self.agent:
            await self.initialize()
            
        async for event in self.agent.run_stream(prompt, session_id=session_id):
            yield event

if __name__ == "__main__":
    # Quick local test
    bot = SVUBot()
    async def run_test():
        await bot.initialize()
        response = await bot.chat("Hello SVU Bot!")
        print(f"Bot: {response}")
    
    asyncio.run(run_test())
