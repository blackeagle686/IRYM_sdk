import os
import re

ROOT = "/home/tlk/Documents/Projects/my_AItools/IRYM_sdk"

replacements = [
    # Fix SemanticSearch location
    (r"from \.\.\.semantic\.semantic_search import SemanticSearch", "from phoenix.framework.chatbot.memory.semantic.semantic_search import SemanticSearch"),
    (r"from \.\.semantic\.semantic_search import SemanticSearch", "from phoenix.framework.chatbot.memory.semantic.semantic_search import SemanticSearch"),
    (r"from \.semantic\.semantic_search import SemanticSearch", "from phoenix.framework.chatbot.memory.semantic.semantic_search import SemanticSearch"),
    
    # Fix BaseMemory location (now in agent/memory/base)
    (r"from \.\.base\.base_memory import BaseMemory", "from phoenix.framework.agent.memory.base.base_memory import BaseMemory"),
    (r"from \.base\.base_memory import BaseMemory", "from phoenix.framework.agent.memory.base.base_memory import BaseMemory"),
    
    # Fix ShortTermMemoryManager location (now in agent/memory/short_term)
    (r"from \.short_term\.stm_manager import ShortTermMemoryManager", "from phoenix.framework.agent.memory.short_term.stm_manager import ShortTermMemoryManager"),
    (r"from \.\.short_term\.stm_manager import ShortTermMemoryManager", "from phoenix.framework.agent.memory.short_term.stm_manager import ShortTermMemoryManager"),
    
    # Fix LongTermMemoryManager location (now in agent/memory/long_term)
    (r"from \.long_term\.ltm_manager import LongTermMemoryManager", "from phoenix.framework.agent.memory.long_term.ltm_manager import LongTermMemoryManager"),
    (r"from \.\.long_term\.ltm_manager import LongTermMemoryManager", "from phoenix.framework.agent.memory.long_term.ltm_manager import LongTermMemoryManager"),
    
    # Generic fixes for the new arch
    (r"phoenix\.framework\.agent\.agent\.agent", "phoenix.framework.agent.core.agent"),
    (r"phoenix\.framework\.agent\.agent\.", "phoenix.framework.agent.core."),
]

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for pattern, replacement in replacements:
        new_content = re.sub(pattern, replacement, new_content)
    
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed: {path}")

for root, _, files in os.walk(os.path.join(ROOT, "phoenix/framework")):
    for file in files:
        if file.endswith(".py"):
            fix_file(os.path.join(root, file))

# Also check tests
for root, _, files in os.walk(os.path.join(ROOT, "tests")):
    for file in files:
        if file.endswith(".py"):
            fix_file(os.path.join(root, file))
