import random
import string

from config import *
from algorithms import hitung_langkah, cari_semua_solusi


def _angka_acak(panjang_min, panjang_maks, nilai_min=1):
    """Bilangan acak dengan jumlah digit panjang_min..panjang_maks (tanpa nol di depan)."""
    p = random.randint(panjang_min, panjang_maks)
    batas_bawah = max(10 ** (p - 1) if p > 1 else 1, nilai_min)
    return random.randint(batas_bawah, 10 ** p - 1)


def _bilangan_soal(op):
    """Buat tiga bilangan (a, b, c) yang memenuhi 'a op b = c'. None kalau di luar batas."""
    if op == "+":
        a, b = _angka_acak(1, 3), _angka_acak(1, 3)
        c = a + b
        return (a, b, c) if c <= 999 else None
    if op == "-":
        a, b = _angka_acak(2, 3), _angka_acak(1, 2)
        c = a - b
        return (a, b, c) if c >= 1 else None
    if op == "*":
        a, b = _angka_acak(2, 3, 2), _angka_acak(1, 2, 2)
        c = a * b
        return (a, b, c) if c <= 9999 else None
    # ":"  ->  a : b = c  (a dibuat dari b * c supaya pasti habis dibagi)
    b, c = _angka_acak(1, 2, 2), _angka_acak(2, 3, 2)
    return (b * c, b, c)


def _ke_huruf(bilangan):
    """Ganti tiap digit dengan huruf unik (digit sama = huruf sama)."""
    digit = sorted(set("".join(map(str, bilangan))))
    huruf = random.sample(string.ascii_uppercase, len(digit))
    peta = dict(zip(digit, huruf))
    return ["".join(peta[d] for d in str(x)) for x in bilangan]


def _pola(w1, op, w2, w3):
    """Bentuk soal tanpa memandang huruf apa yang dipakai (untuk mencegah soal kembar)."""
    urut = {}
    for c in w1 + w2 + w3:
        urut.setdefault(c, len(urut))
    return op, tuple(tuple(urut[c] for c in w) for w in (w1, w2, w3))


def _hitung_delay(diff, langkah):
    target = random.uniform(*WAKTU_AI[diff])          # target detik AI menyelesaikan soal
    delay = target / max(1, langkah)
    return round(min(max(delay, DELAY_MIN), DELAY_MAX), 3)


def buat_soal(diff, sudah=None):
    """Buat satu soal acak untuk tingkat 'diff'.
    Return: ((w1, op, w2, w3), diff, delay_per_langkah)

    Syarat soal: jumlah huruf unik sesuai tingkat, langkah DFS dalam rentang LANGKAH,
    dan jumlah kunci jawaban 1..MAKS_SOLUSI. 'sudah' = himpunan pola yang sudah dipakai."""
    huruf_min, huruf_maks = HURUF_MIN[diff], HURUF_MAKS[diff]
    langkah_min, langkah_maks = LANGKAH[diff]

    for ketat in (True, False):          # tahap 2 (longgar) hanya jika tahap 1 gagal
        for _ in range(MAKS_PERCOBAAN * (1 if ketat else 3)):
            op = random.choice(OPERASI[diff])
            bil = _bilangan_soal(op)
            if bil is None:
                continue
            if not huruf_min <= len(set("".join(map(str, bil)))) <= huruf_maks:
                continue

            w1, w2, w3 = _ke_huruf(bil)
            pola = _pola(w1, op, w2, w3)
            if sudah is not None and pola in sudah:
                continue

            langkah = hitung_langkah(w1, op, w2, w3, batas=langkah_maks if ketat else None)
            if ketat and not langkah_min <= langkah <= langkah_maks:
                continue

            jumlah = len(cari_semua_solusi(w1, op, w2, w3, maks=MAKS_SOLUSI))
            if not 1 <= jumlah <= MAKS_SOLUSI:
                continue

            if sudah is not None:
                sudah.add(pola)
            return (w1, op, w2, w3), diff, _hitung_delay(diff, langkah)

    raise RuntimeError(f"Gagal membuat soal {diff.name}. Longgarkan pengaturan di config.py")


def buat_daftar_soal(komposisi):
    """Buat daftar soal sesuai urutan tingkat di 'komposisi' (tanpa soal kembar)."""
    sudah = set()
    return [buat_soal(diff, sudah) for diff in komposisi]