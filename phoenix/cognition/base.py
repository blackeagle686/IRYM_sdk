class BaseThinker():
    def __init__(self, llm):
        self.agent = agent

    def think(self):
        raise NotImplementedError
    
    def generate_task(self):
        raise NotImplementedError
    
    def generate_sub_objectives(self):
        raise NotImplementedError
    
    def generate_main_objective(self):
        raise NotImplementedError
    
    def generate_file_tasks(self, file_path: str, task: str) -> dict:
        """
        Generates a structured representation of a file-related task.
        """
        raise NotImplementedError
    
    