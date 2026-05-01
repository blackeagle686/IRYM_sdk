import os
import re

ROOT = "/home/tlk/Documents/Projects/my_AItools/IRYM_sdk"

# Patterns to replace in code blocks
replacements = [
    # STT/TTS
    (r"from phoenix\.audio\.local import LocalAudioService", "from phoenix.services.audio.local import LocalSTT, LocalTTS"),
    (r"from phoenix\.audio\.openai import OpenAISTT, OpenAITTS", "from phoenix.services.audio.openai import OpenAISTT, OpenAITTS"),
    
    # Observability
    (r"from phoenix\.observability\.logger import get_logger", "from phoenix.services.observability.logger import get_logger"),
    
    # Exceptions
    (r"from phoenix\.core\.exceptions import Phoenix AIError", "from phoenix.core.exceptions import PhoenixAIError"),
    
    # VLM
    (r"from phoenix import init_phoenix_full, get_vlm_pipeline", "from phoenix import init_phoenix_full, get_vlm_pipeline"), # Already good
    
    # ChatBot (Simplified usage)
    (r"ChatBot\(local=True, vlm=True, tts=True, stt=True\)", "ChatBot(local=True, vlm=True)"),
    (r"ChatBot\(local=False\)\.with_openai\(\"sk-\.\.\.\"\)", "ChatBot(local=False).with_openai(api_key=\"ak-...\")"),
]

def fix_md(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for pattern, replacement in replacements:
        new_content = re.sub(pattern, replacement, new_content)
    
    # Specific fix for Agent imports in docs
    if "Agent" in new_content:
        new_content = re.sub(r"from phoenix\.framework\.agent\.agent import Agent", "from phoenix import Agent", new_content)
        new_content = re.sub(r"from phoenix\.framework\.agent import Agent", "from phoenix import Agent", new_content)

    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated docs: {path}")

for root, _, files in os.walk(ROOT):
    if ".git" in root or "node_modules" in root:
        continue
    for file in files:
        if file.endswith(".md"):
            fix_md(os.path.join(root, file))
