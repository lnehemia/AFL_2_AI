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
HITAM_BULAT = (10, 10, 10)

class Difficulty(Enum):
    EASY = (1, 1.2)   
    MEDIUM = (2, 0.6) 
    HARD = (3, 0.15)  

ALL_PUZZLES = [
    (("A", "BB", "ACC"), Difficulty.EASY),
    (("AB", "A", "BCC"), Difficulty.EASY),
    (("AB", "AB", "BCC"), Difficulty.EASY),
    (("A", "BB", "BC"), Difficulty.EASY),
    (("A", "B", "CC"), Difficulty.EASY),
    (("AB", "CB", "BDA"), Difficulty.MEDIUM),
    (("AA", "BC", "BBB"), Difficulty.MEDIUM),
    (("AB", "BA", "CC"), Difficulty.MEDIUM),
    (("A", "BC", "CB"), Difficulty.MEDIUM),
    (("A", "B", "CD"), Difficulty.MEDIUM),
    (("AB", "CD", "EBE"), Difficulty.HARD),
    (("AB", "CD", "EBA"), Difficulty.HARD),
    (("ABC", "ABC", "BDE"), Difficulty.HARD),
    (("AB", "BC", "CAD"), Difficulty.HARD),
    (("AB", "C", "DED"), Difficulty.HARD)
]