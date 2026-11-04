# cek_delay.py - alat bantu: lihat soal acak yang dibuat generator beserta delay & waktu AI-nya
from config import *
from generator import buat_daftar_soal
from algorithms import hitung_langkah, cari_semua_solusi, angka

MENIT_MATCH = 15

for nama, komposisi in (("TRIAL", TRIAL_KOMPOSISI), ("MATCH", MATCH_KOMPOSISI)):
    print(f"--- {nama} ---")
    total = 0
    for (w1, op, w2, w3), diff, delay in buat_daftar_soal(komposisi):
        n = hitung_langkah(w1, op, w2, w3)
        kunci = cari_semua_solusi(w1, op, w2, w3)
        k = kunci[0]
        contoh = f"{angka(w1, k)} {OP_TAMPIL[op]} {angka(w2, k)} = {angka(w3, k)}"
        waktu = n * delay
        total += waktu
        print(f"[{diff.name:<6}] {w1} {OP_TAMPIL[op]} {w2} = {w3:<6} ({contoh}) | "
            f"{len(set(w1 + w2 + w3))} huruf | {n:>3} langkah x {delay:.3f}s = {waktu:5.1f} dtk | {len(kunci)} kunci")
    print(f"Total waktu AI jika menang semua: {total:.0f} dtk ({total / 60:.1f} menit)\n")
print(f"Batas waktu match: {MENIT_MATCH} menit")