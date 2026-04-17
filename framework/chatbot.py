import asyncio
from typing import Optional, Union, List, Dict, Any
from IRYM_sdk.IRYM import (
    init_irym, 
    startup_irym, 
    get_rag_pipeline, 
    get_insight_engine, 
    get_vlm_pipeline,
    container
)
from IRYM_sdk.core.config import config
from IRYM_sdk.observability.logger import get_logger

logger = get_logger("IRYM.Framework")

class ChatBot:
    """
    High-level Builder for IRYM ChatBots.
    Enables one-liner creation of complex AI agents.
    """
    def __init__(self, local: bool = True, vlm: bool = False, tts: bool = False, stt: bool = False):
        self.local = local
        self.vlm_enabled = vlm
        self.tts_enabled = tts
        self.stt_enabled = stt
        self._rag_path: Optional[str] = None
        self._memory_enabled: bool = False
        self._session_id: str = "default_session"

    def with_rag(self, data_to_insight_path: str):
        """Enable RAG and specify the data path for ingestion."""
        self._rag_path = data_to_insight_path
        return self

    def with_memory(self):
        """Enable conversation history and semantic memory."""
        self._memory_enabled = True
        return self

    def set_session(self, session_id: str):
        """Set a specific session ID for memory."""
        self._session_id = session_id
        return self

    def build(self):
        """Initialize the SDK and return a functional ChatBot instance."""
        # 1. Initialize Registry (Sync)
        # We might want to override config based on 'local' flag
        if not self.local:
            # Force OpenAI if not local
            config.LOCAL_LLM_TEXT_MODEL = ""
            config.LOCAL_VLM_MODEL = ""
        
        init_irym()
        
        return ChatBotInstance(self)

class ChatBotInstance:
    """
    The operational ChatBot instance.
    Handles the interaction orchestration.
    """
    def __init__(self, builder: ChatBot):
        self.builder = builder
        self._initialized = False
        self._rag_pipeline = None
        self._vlm_pipeline = None
        self._memory = None
        self._stt = None
        self._tts = None

    async def _lazy_init(self):
        if self._initialized:
            return

        # 1. Startup Services (Async)
        await startup_irym()

        # 2. Setup Components
        if self.builder._rag_path:
            self._rag_pipeline = get_rag_pipeline()
            await self._rag_pipeline.ingest(self.builder._rag_path)
        
        if self.builder.vlm_enabled:
            self._vlm_pipeline = get_vlm_pipeline(prefer_local=self.builder.local)

        if self.builder._memory_enabled:
            self._memory = container.get("memory")

        # if self.builder.stt_enabled:
        #     self._stt = container.get("stt_local") if self.builder.local else container.get("stt_openai")
        # 
        # if self.builder.tts_enabled:
        #     self._tts = container.get("tts_local") if self.builder.local else container.get("tts_openai")

        self._initialized = True
        logger.info("ChatBotInstance lazily initialized.")

    async def chat(self, 
                   text: Optional[str] = None, 
                   image_path: Optional[str] = None, 
                   audio_path: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """
        Send a message to the bot.
        Returns the text response, or a dict if multiple modalities are involved.
        """
        await self._lazy_init()

        # 1. Handle Audio Input (STT) - Temporarily Disabled
        # input_text = text
        # if audio_path and self._stt:
        #     logger.info(f"Transcribing audio: {audio_path}")
        #     input_text = await self._stt.transcribe(audio_path)
        #     if not text:
        #         text = input_text

        if not text and not image_path:
            raise ValueError("Either text, image_path, or audio_path must be provided.")

        # 2. Context Retrieval (Memory)
        context = ""
        if self._memory:
            # Get short-term and semantic context
            history = await self._memory.get_context(self.builder._session_id)
            past_facts = await self._memory.search_memory(self.builder._session_id, text)
            context = f"{past_facts}\n\nRecent History:\n{history}"

        # 3. Decision Logic: VLM vs LLM/RAG
        response_text = ""
        if image_path and self._vlm_pipeline:
            # VLM path
            response_text = await self._vlm_pipeline.ask(
                text, 
                image_path, 
                use_rag=bool(self._rag_pipeline),
                session_id=self.builder._session_id
            )
        elif self._rag_pipeline:
            # RAG path
            # Inject memory context into RAG if needed, or RAG handles it?
            # Existing RAG query doesn't take context easily, let's prepend to question
            query_with_context = f"Context:\n{context}\n\nUser Question: {text}"
            response_text = await self._rag_pipeline.query(query_with_context)
        else:
            # Simple LLM path
            llm = container.get("llm")
            full_prompt = f"System: Use the following context if relevant.\n{context}\n\nUser: {text}"
            response_text = await llm.generate(full_prompt)

        # 4. Handle Memory Update
        if self._memory:
            await self._memory.add_interaction(self.builder._session_id, text, response_text)

        # 5. Handle Audio Output (TTS) - Temporarily Disabled
        # response_audio = None
        # if self.builder.tts_enabled and self._tts:
        #     logger.info("Generating TTS response...")
        #     # The SDK currently uses 'synthesize' instead of 'generate'
        #     # response_audio = await self._tts.synthesize(response_text, "response.wav")

        # 6. Final Output
        # if self.builder.tts_enabled:
        #     return {
        #         "text": response_text,
        #         "audio": response_audio
        #     }
        
        return response_text
