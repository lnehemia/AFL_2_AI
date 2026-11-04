import threading

class AIAgent:
    def __init__(self):
        self.ai_ditemukan = []
        self.jawaban_ditemukan = False
        self._stop = threading.Event()
        self._stop.set()

    @property
    def is_playing(self):
        return not self._stop.is_set()

    @is_playing.setter
    def is_playing(self, nilai):
        if nilai:
            self._stop.clear()
        else:
            self._stop.set()

    def setup_round(self):
        self.ai_ditemukan = []
        self.jawaban_ditemukan = False
        self.is_playing = True

    def tunggu(self, detik):
        """Pengganti time.sleep yang bisa diinterupsi.
        Return False kalau AI dihentikan saat menunggu."""
        return not self._stop.wait(detik)