import os
import re

def refactor_imports():
    root_dir = "/home/tlk/Documents/Projects/my_AItools/IRYM_sdk"
    
    # Mapping of old import segments to new ones
    replacements = [
        (r"phoenix\.framework\.agent\.memory\.manager", "phoenix.framework.chatbot.memory.manager"),
        (r"phoenix\.framework\.agent\.memory\.hybrid", "phoenix.framework.agent.memory.hybrid"),
        (r"phoenix\.framework\.agent\.memory\.semantic", "phoenix.framework.chatbot.memory.semantic"),
        (r"phoenix\.framework\.agent\.memory\.short_term", "phoenix.framework.agent.memory.short_term"),
        (r"phoenix\.framework\.agent\.memory\.long_term", "phoenix.framework.agent.memory.long_term"),
        (r"phoenix\.framework\.agent\.memory\.base", "phoenix.framework.agent.memory.base"),
        (r"phoenix\.framework\.agent\.memory\.persistence", "phoenix.framework.chatbot.memory.persistence"),
    ]
    
    moved_files_dirs = [
        "phoenix/framework/chatbot/memory",
        "phoenix/framework/chatbot/memory/hybrid",
        "phoenix/framework/chatbot/memory/semantic",
        "phoenix/framework/chatbot/memory/short_term",
        "phoenix/framework/chatbot/memory/long_term",
        "phoenix/framework/chatbot/memory/base",
        "phoenix/framework/chatbot/memory/persistence",
    ]

    for dirpath, _, filenames in os.walk(root_dir):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
            
        rel_dir = os.path.relpath(dirpath, root_dir)
        is_moved_dir = rel_dir in moved_files_dirs or rel_dir.replace("\\", "/") in moved_files_dirs

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
                
                # Apply relative import fixes for moved files
                if is_moved_dir:
                    if rel_dir.endswith("memory"):
                        new_content = re.sub(r"from \.(reflection|session|adapter|task_memory|utils)", r"from phoenix.framework.agent.memory.\1", new_content)
                    else:
                        new_content = re.sub(r"from \.\.(reflection|session|adapter|task_memory|utils)", r"from phoenix.framework.agent.memory.\1", new_content)

                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Refactored: {filepath}")

if __name__ == "__main__":
    refactor_imports()
