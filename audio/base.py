from IRYM_sdk.core.base import BaseService

class BaseSTT(BaseService):
    async def transcribe(self, audio_path: str) -> str:
        """Transcribe speech to text from an audio file."""
        raise NotImplementedError

class BaseTTS(BaseService):
    async def synthesize(self, text: str, output_path: str) -> str:
        """Synthesize text to speech and save to output_path."""
        raise NotImplementedError
