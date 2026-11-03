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
    EASY = (1, 0.3)   
    MEDIUM = (2, 0.2) 
    HARD = (3, 0.15)  

TRIAL_PUZZLES = [
    (("A", "A", "BC"), Difficulty.EASY),
    (("A", "B", "CC"), Difficulty.EASY),
    (("AB", "A", "BC"), Difficulty.EASY),
    (("AA", "B", "AC"), Difficulty.EASY),
    (("AB", "B", "CA"), Difficulty.EASY),
]

ALL_PUZZLES = [
    (("A", "BB", "ACC"), Difficulty.EASY),   # 1 + 99 = 100
    (("BB", "A", "ACC"), Difficulty.EASY),   # 99 + 1 = 100
    (("AB", "AB", "BCC"), Difficulty.EASY),  # 61 + 61 = 122
    (("AA", "AA", "BAC"), Difficulty.EASY),  # 99 + 99 = 198
    (("AA", "BB", "CBC"), Difficulty.EASY),  # 99 + 22 = 121

    (("AB", "C", "ADD"), Difficulty.MEDIUM),     # 98 + 2 = 100
    (("AB", "CB", "ADD"), Difficulty.MEDIUM),    # 15 + 85 = 100
    (("AB", "BC", "ADD"), Difficulty.MEDIUM),    # 18 + 82 = 100
    (("BA", "CA", "BDD"), Difficulty.MEDIUM),    # 15 + 85 = 100 (B=1, A=5, C=8, D=0)
    (("ABB", "A", "CDD"), Difficulty.MEDIUM),    # 199 + 1 = 200

    (("TWO", "TWO", "FOUR"), Difficulty.HARD),       # 734 + 734 = 1468
    (("EAT", "THAT", "APPLE"), Difficulty.HARD),     # 819 + 9219 = 10038
    (("BASE", "BALL", "GAMES"), Difficulty.HARD),    # 7483 + 7455 = 14938
    (("CROSS", "ROADS", "DANGER"), Difficulty.HARD), # 96233 + 62513 = 158746
    (("SEND", "MORE", "MONEY"), Difficulty.HARD)     # 9567 + 1085 = 10652
]