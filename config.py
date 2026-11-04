from enum import Enum

# ---------------------------------------------------------
# TAMPILAN
# ---------------------------------------------------------
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
    # nilai = pengali skor
    EASY = 1
    MEDIUM = 2
    HARD = 3


# ---------------------------------------------------------
# PEMBUATAN SOAL OTOMATIS
# ---------------------------------------------------------
# Operasi per tingkat: "+" tambah, "-" kurang, "*" kali, ":" bagi
OPERASI = {
    Difficulty.EASY:   ["+", "-"],
    Difficulty.MEDIUM: ["*"],
    Difficulty.HARD:   [":"],
}

# Simbol operasi saat ditampilkan di layar
OP_TAMPIL = {"+": "+", "-": "-", "*": "x", ":": ":"}

# Jumlah huruf unik per soal (min dan maks). Default: min = maks supaya
# tingkat kesulitannya konsisten. Longgarkan min kalau ingin soal lebih bervariasi.
HURUF_MIN = {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}
HURUF_MAKS = {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}

# Target waktu AI menyelesaikan satu soal (detik): (terendah, tertinggi) per tingkat.
# Delay per langkah dihitung otomatis: delay = target / hitung_langkah(soal)
WAKTU_AI = {
    Difficulty.EASY:   (20, 35),
    Difficulty.MEDIUM: (30, 50),
    Difficulty.HARD:   (45, 75),
}

# Rentang jumlah langkah DFS yang diterima generator per tingkat. Soal di luar
# rentang dibuang supaya delay tidak terlalu kecil (animasi tidak terlihat)
# atau terlalu besar.
LANGKAH = {
    Difficulty.EASY:   (10, 300),
    Difficulty.MEDIUM: (15, 500),
    Difficulty.HARD:   (30, 800),
}

# Batas aman delay per langkah (detik)
DELAY_MIN = 0.05
DELAY_MAX = 3.0

# Soal boleh punya beberapa kunci jawaban, tapi tidak lebih dari ini
MAKS_SOLUSI = 6

# Banyak percobaan acak untuk membuat satu soal
MAKS_PERCOBAAN = 4000

# Susunan soal
TRIAL_KOMPOSISI = [Difficulty.EASY, Difficulty.EASY]
MATCH_KOMPOSISI = (
    [Difficulty.EASY] * 5
    + [Difficulty.MEDIUM] * 5
    + [Difficulty.HARD] * 5
)