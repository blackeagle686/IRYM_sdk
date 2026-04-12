import base64
from IRYM_sdk.llm.base import BaseVLM
from IRYM_sdk.core.config import config
from openai import OpenAI
import os
import mimetypes

class OpenAIVLM(BaseVLM):
    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        self.base_url = config.OPENAI_BASE_URL
        self.client = None

    async def init(self):
        if not self.api_key:
            print("Warning: OPENAI_API_KEY is missing. Operating in mock mode.")
        self.client = OpenAI(
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
            raise RuntimeError("OpenAIVLM is not initialized.")
        if not self.api_key:
            return f"[Mock OpenAI VLM Response (No API Key) to: {prompt} with image: {image_path}]"

        base64_image = self._encode_image(image_path)
        mime_type = self._get_mime_type(image_path)
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
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
        text = response.choices[0].message.content
        return text
