import base64
import httpx
from IRYM_sdk.llm.base import BaseVLM
from IRYM_sdk.core.config import config

class LocalVLM(BaseVLM):
    _model_cache = {}

    def __init__(self):
        self.model = config.LOCAL_VLM_MODEL or "moondream"
        self.base_url = "http://localhost:11434/api/generate"
        self.hf_model = None
        self.processor = None
        self.is_ollama = False

    def is_available(self) -> bool:
        return bool(self.model)

    async def init(self):
        if not self.model:
            return

        if self.model not in LocalVLM._model_cache:
            print(f"[*] Initializing Local VLM Model: {self.model}...")
            try:
                from transformers import AutoProcessor, AutoConfig, AutoModelForCausalLM
                processor = AutoProcessor.from_pretrained(self.model, trust_remote_code=True)
                
                # Check config architecture to dynamically load the right class if Auto breaks
                config_opt = AutoConfig.from_pretrained(self.model, trust_remote_code=True)
                architectures = getattr(config_opt, "architectures", [])
                
                hf_model = None
                
                # Check for bitsandbytes
                quant_kwargs = {}
                try:
                    import bitsandbytes
                    quant_kwargs = {"load_in_4bit": True}
                    print("[*] bitsandbytes available. Enabling 4-bit quantization to prevent OOM...")
                except ImportError:
                    print("[-] bitsandbytes not found. Loading model in standard precision (may cause OOM on small GPUs).")

                # Explicit Qwen3/Qwen2 VL support
                if "Qwen3VLForConditionalGeneration" in architectures:
                    try:
                        from transformers.models.qwen3_vl.modeling_qwen3_vl import Qwen3VLForConditionalGeneration
                        hf_model = Qwen3VLForConditionalGeneration.from_pretrained(self.model, device_map="auto", torch_dtype="auto", trust_remote_code=True, **quant_kwargs)
                    except ImportError:
                        try:
                            from transformers import AutoModelForVision2Seq
                            hf_model = AutoModelForVision2Seq.from_pretrained(self.model, device_map="auto", torch_dtype="auto", trust_remote_code=True, **quant_kwargs)
                        except ImportError:
                            hf_model = AutoModelForCausalLM.from_pretrained(self.model, device_map="auto", torch_dtype="auto", trust_remote_code=True, **quant_kwargs)
                elif "Qwen2VLForConditionalGeneration" in architectures:
                    from transformers import Qwen2VLForConditionalGeneration
                    hf_model = Qwen2VLForConditionalGeneration.from_pretrained(self.model, device_map="auto", torch_dtype="auto", trust_remote_code=True, **quant_kwargs)
                else:
                    try:
                        from transformers import AutoModelForVision2Seq
                        hf_model = AutoModelForVision2Seq.from_pretrained(self.model, device_map="auto", torch_dtype="auto", trust_remote_code=True, **quant_kwargs)
                    except (ImportError, ValueError):
                        hf_model = AutoModelForCausalLM.from_pretrained(self.model, device_map="auto", torch_dtype="auto", trust_remote_code=True, **quant_kwargs)
                
                LocalVLM._model_cache[self.model] = {
                    "hf_model": hf_model,
                    "processor": processor,
                    "type": "transformers"
                }
                print("[+] VLM Loaded into memory cache.")
            except ImportError as ie:
                print(f"[!] {ie}. Falling back to Ollama.")
                LocalVLM._model_cache[self.model] = {"type": "ollama"}
            except Exception as e:
                print(f"[!] Failed to load model locally: {e}. Falling back to Ollama.")
                LocalVLM._model_cache[self.model] = {"type": "ollama"}

        cached = LocalVLM._model_cache[self.model]
        if cached["type"] == "transformers":
            self.hf_model = cached["hf_model"]
            self.processor = cached["processor"]
        else:
            self.is_ollama = True
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get("http://localhost:11434/api/tags")
                    if resp.status_code != 200:
                        print(f"Warning: Ollama not responding at {self.base_url}.")
            except Exception:
                print("Warning: Could not connect to local Ollama. Ensure it is running.")

    async def generate_with_image(self, prompt: str, image_path: str) -> str:
        if not self.hf_model and not self.is_ollama:
            await self.init()

        if self.is_ollama:
            return await self._ollama_generate(prompt, image_path)
            
        try:
            from PIL import Image
            import torch
            image = Image.open(image_path).convert("RGB")
            
            # Simple generic transformers interface
            messages = [
                {"role": "user", "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt}
                ]}
            ]
            
            # Use processor apply_chat_template if available, else plain text
            if hasattr(self.processor, "apply_chat_template"):
                text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
                inputs = self.processor(text=[text], images=[image], padding=True, return_tensors="pt").to(self.hf_model.device)
            else:
                inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.hf_model.device)

            with torch.no_grad():
                generated_ids = self.hf_model.generate(**inputs, max_new_tokens=512)
                
            generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
            output = self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            return output[0]
        except Exception as e:
            raise RuntimeError(f"LocalVLM transformers execution failed: {e}")

    async def generate(self, prompt: str) -> str:
        """Text-only generation fallback for VLMs."""
        if not self.hf_model and not self.is_ollama:
            await self.init()
            
        if self.is_ollama:
            return await self._ollama_generate(prompt, image_path=None)

        try:
            import torch
            messages = [{"role": "user", "content": prompt}]
            if hasattr(self.processor, "apply_chat_template"):
                text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
                inputs = self.processor(text=[text], return_tensors="pt").to(self.hf_model.device)
            else:
                inputs = self.processor(text=prompt, return_tensors="pt").to(self.hf_model.device)
                
            with torch.no_grad():
                generated_ids = self.hf_model.generate(**inputs, max_new_tokens=512)
                
            generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
            output = self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            return output[0]
        except Exception as e:
            raise RuntimeError(f"LocalVLM text generate failed: {e}")

    async def _ollama_generate(self, prompt: str, image_path: str = None) -> str:
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            if image_path:
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                payload["images"] = [image_data]
                
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                return response.json().get("response", "")
        except Exception as e:
            raise RuntimeError(f"LocalVLM (Ollama) call failed: {e}")
