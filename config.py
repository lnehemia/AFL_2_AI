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

TRIAL_PUZZLES = [
    (("BB", "A", "ACC"), Difficulty.EASY, 0.65),       #  99  + 1   = 100
    (("NO", "NO", "TOO"), Difficulty.EASY, 0.65),      #  50  + 50  = 100
]

ALL_PUZZLES = [
    (("SS", "SS", "HSU"), Difficulty.EASY, 0.65),      #  99  + 99  = 198
    (("AB", "A", "BCC"), Difficulty.EASY, 0.65),       #  91  + 9   = 100
    (("GO", "GO", "OFF"), Difficulty.EASY, 0.65),      #  61  + 61  = 122
    (("A", "BAB", "CDD"), Difficulty.EASY, 0.65),      #  9   + 191 = 200
    (("TO", "SO", "TOO"), Difficulty.EASY, 0.65),      #  10  + 90  = 100

    (("AB", "BA", "DAD"), Difficulty.MEDIUM, 0.40),    #  29  + 92  = 121
    (("UI", "IU", "MIT"), Difficulty.MEDIUM, 0.40),    #  98  + 89  = 187
    (("US", "AS", "ALL"), Difficulty.MEDIUM, 0.40),    #  85  + 15  = 100
    (("GG", "GI", "IGA"), Difficulty.MEDIUM, 0.40),    #  99  + 91  = 190
    (("AIR", "AR", "IRA"), Difficulty.MEDIUM, 0.40),   #  673 + 63  = 736


    (("AB", "CBC", "ADA"), Difficulty.HARD, 0.23),     #  91  + 818 = 909
    (("ABC", "ABC", "BDD"), Difficulty.HARD, 0.23),    #  372 + 372 = 744
    (("ABC", "ABC", "DCD"), Difficulty.HARD, 0.23),    #  237 + 237 = 474
    (("ADD", "DAD", "BCA"), Difficulty.HARD, 0.23),    #  266 + 626 = 892
    (("ARA", "ABA", "BAR"), Difficulty.HARD, 0.23),     #  363 + 373 = 736

]