class BaseThinker():
    def __init__(self, agent):
        self.agent = agent

    def think(self):
        raise NotImplementedError
    
    def generate_tasks(self):
        raise NotImplementedError
    
    def generate_sub_objectives(self):
        raise NotImplementedError
    
    def generate_main_objective(self):
        raise NotImplementedError
    
    def 