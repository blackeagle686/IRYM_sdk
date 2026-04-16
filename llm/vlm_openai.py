import base64
from IRYM_sdk.llm.base import BaseVLM
from IRYM_sdk.core.config import config
from openai import AsyncOpenAI
import os
import mimetypes

from IRYM_sdk.observability.tracing import tracer

class OpenAIVLM(BaseVLM):
    def __init__(self):
        self.api_key = getattr(config, "OPENAI_VLM_API_KEY", "") or getattr(config, "OPENAI_API_KEY", "")
        self.base_url = getattr(config, "OPENAI_VLM_BASE_URL", "") or getattr(config, "OPENAI_BASE_URL", "")
        self.model = getattr(config, "OPENAI_VLM_MODEL", "")
        self.client = None

    def is_available(self) -> bool:
        return bool(self.api_key) and not self.api_key.startswith("ak_") and bool(self.model)

    async def init(self):
        if not self.api_key:
            print("Warning: OPENAI_API_KEY is missing. Operating in mock mode.")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _get_mime_type(self, image_path: str) -> str:
        mime_type, _ = mimetypes.guess_type(image_path)
        return mime_type or "image/jpeg"

    async def generate_with_image(self, prompt: str, image_path: str) -> str:
        if not self.client:
            await self.init()
            
        # Mock mode
        if not self.api_key:
            return f"[Mock OpenAI VLM Response (No API Key) to: {prompt} with image: {image_path}]"
            
        if not self.model:
            raise RuntimeError("OpenAIVLM model is not configured (model field is empty).")

        span_id = tracer.start_span("OpenAIVLM.generate_with_image", {"model": self.model})
        try:
            base64_image = self._encode_image(image_path)
            mime_type = self._get_mime_type(image_path)
            
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            )

            if not resp or not resp.choices:
                tracer.end_span(span_id, status="error", error="Empty response from OpenAI VLM")
                raise RuntimeError("Empty response from OpenAI VLM API.")

            usage = {
                "prompt_tokens": resp.usage.prompt_tokens,
                "completion_tokens": resp.usage.completion_tokens,
                "total_tokens": resp.usage.total_tokens
            }
            
            content = resp.choices[0].message.content
            tracer.end_span(span_id, status="success", usage=usage)
            return content

        except Exception as e:
            tracer.end_span(span_id, status="error", error=str(e))
            raise RuntimeError(f"OpenAIVLM API call failed: {e}")
