from IRYM_sdk.audio.base import BaseSTT, BaseTTS

class LocalSTT(BaseSTT):
    def __init__(self):
        self.model = None

    async def init(self):
        self.model = "MockSTTModel"

    async def transcribe(self, audio_path: str) -> str:
        if not self.model:
            raise RuntimeError("LocalSTT is not initialized.")
        return f"[Mock STT Transcription for: {audio_path}]"

class LocalTTS(BaseTTS):
    def __init__(self):
        self.model = None

    async def init(self):
        self.model = "MockTTSModel"

    async def synthesize(self, text: str, output_path: str) -> str:
        if not self.model:
            raise RuntimeError("LocalTTS is not initialized.")
        with open(output_path, "wb") as f:
            f.write(b"Mock audio data")
        return output_path
