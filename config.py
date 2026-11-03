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
    # (score multiplier, delay per DFS attempt in seconds)
    EASY = (1, 0.65)
    MEDIUM = (2, 1.54)
    HARD = (3, 0.23)

TRIAL_PUZZLES = [
    (("BB", "A", "ACC"), Difficulty.EASY),       #  99  + 1   = 100
    (("NO", "NO", "TOO"), Difficulty.EASY),      #  50  + 50  = 100
]

ALL_PUZZLES = [
    (("SS", "SS", "HSU"), Difficulty.EASY),      #  99  + 99  = 198
    (("AB", "A", "BCC"), Difficulty.EASY),       #  91  + 9   = 100
    (("GO", "GO", "OFF"), Difficulty.EASY),      #  61  + 61  = 122
    (("A", "BAB", "CDD"), Difficulty.EASY),      #  9   + 191 = 200
    (("TO", "SO", "TOO"), Difficulty.EASY),      #  10  + 90  = 100

    (("AB", "BA", "DAD"), Difficulty.MEDIUM),    #  29  + 92  = 121
    (("UI", "IU", "MIT"), Difficulty.MEDIUM),    #  98  + 89  = 187
    (("US", "AS", "ALL"), Difficulty.MEDIUM),    #  85  + 15  = 100
    (("GG", "GI", "IGA"), Difficulty.MEDIUM),    #  99  + 91  = 190
    (("AIR", "AR", "IRA"), Difficulty.MEDIUM),   #  673 + 63  = 736


    (("AB", "CBC", "ADA"), Difficulty.HARD),     #  91  + 818 = 909
    (("ABC", "ABC", "BDD"), Difficulty.HARD),    #  372 + 372 = 744
    (("ABC", "ABC", "DCD"), Difficulty.HARD),    #  237 + 237 = 474
    (("ADD", "DAD", "BCA"), Difficulty.HARD),    #  266 + 626 = 892
    (("ARA", "ABA", "BAR"), Difficulty.HARD)     #  363 + 373 = 736

]