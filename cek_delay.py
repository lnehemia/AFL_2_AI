from config import ALL_PUZZLES, TRIAL_PUZZLES
from algorithms import hitung_langkah

for nama, daftar in (("TRIAL", TRIAL_PUZZLES), ("MATCH", ALL_PUZZLES)):
    print(f"--- {nama} ---")
    for (w1, w2, w3), diff, delay in daftar:
        n = hitung_langkah(w1, w2, w3)
        print(f"{w1}+{w2}={w3} [{diff.name}]: {n} langkah, AI selesai ≈ {n * delay:.1f} detik")