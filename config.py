from enum import Enum

LEBAR, TINGGI = 1200, 700
FPS = 60
BG = (15, 15, 20)
PANEL = (30, 32, 40)
GARIS = (60, 65, 80)
TEKS = (240, 240, 240)
CYAN = (0, 200, 255)
PINK = (255, 50, 150)
HIJAU = (50, 220, 100)
KUNING = (255, 200, 0)
MERAH = (220, 40, 40)
ABU = (100, 100, 110)
HITAM = (10, 10, 10)

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

OPERASI = {
    Difficulty.EASY:   ["+", "-"],
    Difficulty.MEDIUM: ["*"],
    Difficulty.HARD:   [":"],
}

OP_TAMPIL = {"+": "+", "-": "-", "*": "x", ":": ":"}

HURUF_MIN = {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}
HURUF_MAKS = {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}

WAKTU_AI = {
    Difficulty.EASY:   (20, 35),
    Difficulty.MEDIUM: (30, 50),
    Difficulty.HARD:   (45, 75),
}

LANGKAH = {
    Difficulty.EASY:   (10, 300),
    Difficulty.MEDIUM: (15, 500),
    Difficulty.HARD:   (30, 800),
}

DELAY_MIN = 0.05
DELAY_MAX = 3.0

MAKS_SOLUSI = 6

MAKS_PERCOBAAN = 4000

TRIAL_KOMPOSISI = [Difficulty.EASY, Difficulty.EASY]
MATCH_KOMPOSISI = (
    [Difficulty.EASY] * 5
    + [Difficulty.MEDIUM] * 5
    + [Difficulty.HARD] * 5
)