import httpx
from IRYM_sdk.llm.base import BaseLLM
from IRYM_sdk.core.config import config

class LocalLLM(BaseLLM):
    _model_cache = {}

    def __init__(self):
        self.model = config.LOCAL_LLM_TEXT_MODEL or "Qwen/Qwen2-1.5B-Instruct"
        self.base_url = "http://localhost:11434/api/generate"
        self.hf_model = None
        self.tokenizer = None
        self.is_ollama = False

    def is_available(self) -> bool:
        return bool(self.model)

    async def init(self):
        if not self.model:
            return

        if self.model not in LocalLLM._model_cache:
            print(f"[*] Initializing Local LLM Model: {self.model}...")
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
                
                quant_kwargs = {}
                try:
                    import bitsandbytes
                    quant_kwargs = {"load_in_4bit": True}
                    print("[*] bitsandbytes available. Enabling 4-bit quantization for LLM...")
                except ImportError:
                    pass

                tokenizer = AutoTokenizer.from_pretrained(self.model, trust_remote_code=True)
                hf_model = AutoModelForCausalLM.from_pretrained(
                    self.model, device_map="auto", torch_dtype="auto", trust_remote_code=True, **quant_kwargs
                )
                
                LocalLLM._model_cache[self.model] = {
                    "hf_model": hf_model,
                    "tokenizer": tokenizer,
                    "type": "transformers"
                }
                print("[+] LLM Loaded into memory cache.")
            except ImportError as ie:
                print(f"[!] {ie}. Falling back to Ollama.")
                LocalLLM._model_cache[self.model] = {"type": "ollama"}
            except Exception as e:
                print(f"[!] Failed to load LLM locally: {e}. Falling back to Ollama.")
                LocalLLM._model_cache[self.model] = {"type": "ollama"}

        cached = LocalLLM._model_cache[self.model]
        if cached["type"] == "transformers":
            self.hf_model = cached["hf_model"]
            self.tokenizer = cached["tokenizer"]
        else:
            self.is_ollama = True
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(f"{self.base_url.replace('/api/generate', '')}/api/tags")
                    if resp.status_code != 200:
                        print(f"Warning: Ollama not responding at {self.base_url}")
            except Exception:
                print("Warning: Could not connect to local Ollama. Ensure it is running.")

    async def generate(self, prompt: str) -> str:
        if not self.hf_model and not self.is_ollama:
            await self.init()
            
        if self.is_ollama:
            return await self._ollama_generate(prompt)

        try:
            import torch
            messages = [{"role": "user", "content": prompt}]
            
            if hasattr(self.tokenizer, "apply_chat_template"):
                text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = self.tokenizer(text, return_tensors="pt").to(self.hf_model.device)
            else:
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.hf_model.device)
                
            with torch.no_grad():
                generated_ids = self.hf_model.generate(**inputs, max_new_tokens=512)
                
            generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
            output = self.tokenizer.batch_decode(generated_ids_trimmed, skip_special_tokens=True)
            return output[0]
        except Exception as e:
            raise RuntimeError(f"LocalLLM transformers generate failed: {e}")

    async def _ollama_generate(self, prompt: str) -> str:
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                return response.json().get("response", "")
        except Exception as e:
            raise RuntimeError(f"LocalLLM (Ollama) call failed: {e}")
