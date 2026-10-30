class AIAgent:
    def __init__(self):
        self.ai_found = []
        self.answer_found = False
        self.is_playing = False
        
    def setup_round(self):
        self.ai_found = []
        self.answer_found = False
        self.is_playing = True