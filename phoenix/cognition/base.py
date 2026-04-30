class BaseThinker():
    def __init__(self, agent):
        self.agent = agent

    def think(self):
        raise NotImplementedError