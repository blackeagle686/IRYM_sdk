import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from IRYM_sdk.core.config import config
from IRYM_sdk.observability.logger import get_logger

logger = get_logger("IRYM.Core.Utils")

_executor = ThreadPoolExecutor(max_workers=1)

async def async_confirm(message: str) -> bool:
    """
    Prompts the user for confirmation in an async-friendly way.
    If config.AUTO_ACCEPT_FALLBACK is True, it returns True immediately.
    """
    if getattr(config, "AUTO_ACCEPT_FALLBACK", False):
        return True
    
    # Check if we are in an interactive terminal
    if not sys.stdin.isatty():
        logger.warning("No interactive terminal detected. Defaulting to REJECT for fallback.")
        return False

    def _sync_input():
        while True:
            choice = input(f"\n[IRYM WARNING] {message} (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                return True
            if choice in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'.")

    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(_executor, _sync_input)
    except Exception as e:
        logger.error(f"Error during interactive confirmation: {e}")
        return False
