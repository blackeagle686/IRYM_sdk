import os
import re

def refactor_imports():
    root_dir = "/home/tlk/Documents/Projects/my_AItools/IRYM_sdk"
    
    # Mapping of paths that moved from chatbot back to agent
    replacements = [
        (r"phoenix\.framework\.chatbot\.memory\.base", "phoenix.framework.agent.memory.base"),
        (r"phoenix\.framework\.chatbot\.memory\.hybrid", "phoenix.framework.agent.memory.hybrid"),
        (r"phoenix\.framework\.chatbot\.memory\.short_term", "phoenix.framework.agent.memory.short_term"),
        (r"phoenix\.framework\.chatbot\.memory\.long_term", "phoenix.framework.agent.memory.long_term"),
    ]
    
    # Files in these dirs might need to fix relative imports
    agent_mem_dirs = [
        "phoenix/framework/agent/memory/base",
        "phoenix/framework/agent/memory/hybrid",
        "phoenix/framework/agent/memory/short_term",
        "phoenix/framework/agent/memory/long_term",
    ]

    for dirpath, _, filenames in os.walk(root_dir):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
            
        rel_dir = os.path.relpath(dirpath, root_dir)
        is_agent_mem_dir = rel_dir in agent_mem_dirs or rel_dir.replace("\\", "/") in agent_mem_dirs

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
                    continue
                
                new_content = content
                
                # Apply standard replacements
                for pattern, subst in replacements:
                    new_content = re.sub(pattern, subst, new_content)
                
                # Fix specific cross-imports if they were made absolute previously
                # (My previous script might have made them absolute)
                # Actually, absolute is fine. But if they were "from phoenix.framework.agent.memory.reflection"
                # in a file that is now in "phoenix/framework/agent/memory/hybrid", it works perfectly.
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Refactored: {filepath}")

if __name__ == "__main__":
    refactor_imports()
