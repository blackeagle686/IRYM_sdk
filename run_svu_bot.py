import asyncio
from svu_bot.bot import SVUBot

async def main():
    bot = SVUBot()
    
    print("\n" + "="*30)
    print("Welcome to SVU Bot (Framework Mode)")
    print("Type 'exit' to quit")
    print("="*30 + "\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            print("\nSVU Bot is thinking...", end="\r")
            # The ChatBot framework handles its own lazy initialization
            response = await bot.chat(user_input)
            print(f"SVU Bot: {response}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
