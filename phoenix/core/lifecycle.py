from typing import List, Callable, Awaitable

class LifecycleManager:
    def __init__(self):
        self._startup_hooks: List[Callable[[], Awaitable[None]]] = []
        self._shutdown_hooks: List[Callable[[], Awaitable[None]]] = []

    def on_startup(self, hook: Callable[[], Awaitable[None]]):
        self._startup_hooks.append(hook)

    def on_shutdown(self, hook: Callable[[], Awaitable[None]]):
        self._shutdown_hooks.append(hook)

    async def startup(self):
        for hook in self._startup_hooks:
            await hook()

    async def shutdown(self):
        for hook in self._shutdown_hooks:
            await hook()

lifecycle = LifecycleManager()
