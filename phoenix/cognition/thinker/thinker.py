"""
    - Thinker must recongize all of the following from user prompt.
    
    - semantic cache uset the main_objective to find relevant memory entries to pass back to thinker as context for better understanding of user prompt and workspace state.
    
    - Thinker in planning mode must generate a tasks files containe on: 
        use uuid_task_file_date_time as file name to avoid conflicts and make it unique.
        for example: "2024-06-01T12-00-00Z_task_file.json"
        the content of this file must be like this:
        {
            "task_id":{
                "description": "what the task is about",
                "dependencies": ["other_task_id"],
                "tools_required": ["tool_name"],
                "priority": "high/medium/low"
                "status": "pending/in_progress/done/field"
            },
            
        }
        task file must be updated by thinker and planner to update the status of each task and add new tasks if needed.
        
    - Thinker must return response like this: 
    { 
        "main_objective": "Refined main goal based on user prompt",
        "sub_objectives": [],
        "context_memory": [last_n relevant memory entries to the prompt],
        "summary_answer": "A concise summary of the user's request and the core objectives",
        "files":{
            "file_name": {
                "file_path": "path/to/file",
                "task": "edit/append/create",
            },  
        }, 
        "tasks": {
            "task_name": {
                "description": "What the task is about",
                "dependencies": ["other_task_name"],
                "tools_required": ["tool_name"],
                "periority": "high/medium/low"
            }
        }
    }

"""
from .base import BaseThinker

