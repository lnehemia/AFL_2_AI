class AIAgent:
    def __init__(self):
        self.ai_ditemukan = []
        self.jawaban_ditemukan = False
        self.is_playing = False

    def setup_round(self):
        self.ai_ditemukan = []
        self.jawaban_ditemukan = False
        self.is_playing = True