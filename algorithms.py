OPERASI_VALID = ("+", "-", "*", ":")

def cek_relasi(op, n1, n2, n3):
    if op == "+":
        return n1 + n2 == n3
    if op == "-":
        return n1 - n2 == n3
    if op == "*":
        return n1 * n2 == n3
    if op == ":":
        return n2 != 0 and n1 == n2 * n3
    return False

def angka(kata, assignment):
    n = 0
    for c in kata:
        n = n * 10 + assignment[c]
    return n

class Masalah:
    def __init__(self, w1, op, w2, w3):
        if op not in OPERASI_VALID:
            raise ValueError(f"Operasi tidak dikenal: {op}")
        self.w1, self.op, self.w2, self.w3 = w1, op, w2, w3
        self.huruf_awal = {w1[0], w2[0], w3[0]}
        semua = list(dict.fromkeys(w1 + w2 + w3))
        self.linear = op in ("+", "-")

        if self.linear:
            tanda = (1, 1, -1) if op == "+" else (1, -1, -1)
            self.bobot = {c: 0 for c in semua}
            for kata, t in zip((w1, w2, w3), tanda):
                for i, c in enumerate(reversed(kata)):
                    self.bobot[c] += t * 10 ** i
            self.huruf_unik = sorted(semua, key=lambda c: abs(self.bobot[c]), reverse=True)
            self.max_sisa = [
                sum(abs(self.bobot[c]) for c in self.huruf_unik[i:])
                for i in range(len(self.huruf_unik))
            ]
        else:
            if op == "*":
                self.hasil, self.f1, self.f2 = w3, w1, w2
            else:
                self.hasil, self.f1, self.f2 = w1, w2, w3
            faktor = list(dict.fromkeys(self.f1 + self.f2))
            sisa = [c for c in dict.fromkeys(self.hasil) if c not in faktor]
            self.huruf_unik = faktor + sisa
            self.n_faktor = len(faktor)

    def _wajib(self, assignment):
        s = str(angka(self.f1, assignment) * angka(self.f2, assignment))
        if len(s) != len(self.hasil):
            return None
        terpakai = set(assignment.values())
        wajib = {}
        for c, d in zip(self.hasil, s):
            d = int(d)
            if c in assignment:
                if assignment[c] != d:
                    return None
            else:
                if wajib.setdefault(c, d) != d:
                    return None
                if d in terpakai:
                    return None
        if len(set(wajib.values())) != len(wajib):
            return None
        return wajib

    def kandidat(self, index, assignment):
        if self.linear:
            jumlah = sum(self.bobot[c] * d for c, d in assignment.items())
            if abs(jumlah) > self.max_sisa[index] * 9:
                return ()
            return range(10)

        if index < self.n_faktor:
            return range(10)
        wajib = self._wajib(assignment)
        if wajib is None:
            return ()
        return (wajib[self.huruf_unik[index]],)

    def tujuan(self, assignment):
        return cek_relasi(
            self.op,
            angka(self.w1, assignment),
            angka(self.w2, assignment),
            angka(self.w3, assignment),
        )


def solve_cryptarithm_dfs_fast(w1, op, w2, w3):
    m = Masalah(w1, op, w2, w3)
    huruf = m.huruf_unik

    def backtrack(index, used_digits, assignment):
        if index == len(huruf):
            return assignment.copy() if m.tujuan(assignment) else None

        char = huruf[index]
        for digit in m.kandidat(index, assignment):
            if digit in used_digits or (digit == 0 and char in m.huruf_awal):
                continue
            assignment[char] = digit
            used_digits.add(digit)
            hasil = backtrack(index + 1, used_digits, assignment)
            if hasil:
                return hasil
            del assignment[char]
            used_digits.remove(digit)
        return None

    solusi = backtrack(0, set(), {})
    return solusi, huruf


def solve_cryptarithm_dfs_realtime(w1, op, w2, w3, ai_agent, delay_per_step):
    m = Masalah(w1, op, w2, w3)
    huruf = m.huruf_unik

    def backtrack(index, used_digits, assignment):
        if not ai_agent.is_playing:
            return None

        if index == len(huruf):
            if m.tujuan(assignment):
                ai_agent.jawaban_ditemukan = True
                return assignment.copy()
            return None

        char = huruf[index]
        for digit in m.kandidat(index, assignment):
            if not ai_agent.is_playing:
                return None

            if digit in used_digits or (digit == 0 and char in m.huruf_awal):
                continue

            assignment[char] = digit
            used_digits.add(digit)
            if char not in ai_agent.ai_ditemukan:
                ai_agent.ai_ditemukan.append(char)

            if not ai_agent.tunggu(delay_per_step):
                return None

            hasil = backtrack(index + 1, used_digits, assignment)
            if hasil:
                return hasil

            del assignment[char]
            used_digits.remove(digit)

        if char in ai_agent.ai_ditemukan:
            ai_agent.ai_ditemukan.remove(char)
        return None

    backtrack(0, set(), {})


def hitung_langkah(w1, op, w2, w3, batas=None):
    m = Masalah(w1, op, w2, w3)
    huruf = m.huruf_unik
    langkah = 0
    berhenti = False

    def backtrack(index, used_digits, assignment):
        nonlocal langkah, berhenti
        if index == len(huruf):
            return m.tujuan(assignment)

        char = huruf[index]
        for digit in m.kandidat(index, assignment):
            if digit in used_digits or (digit == 0 and char in m.huruf_awal):
                continue
            langkah += 1
            if batas is not None and langkah > batas:
                berhenti = True
                return False
            assignment[char] = digit
            used_digits.add(digit)
            if backtrack(index + 1, used_digits, assignment):
                return True
            del assignment[char]
            used_digits.remove(digit)
            if berhenti:
                return False
        return False

    backtrack(0, set(), {})
    return langkah


def cari_semua_solusi(w1, op, w2, w3, maks=None):
    m = Masalah(w1, op, w2, w3)
    huruf = m.huruf_unik
    hasil = []

    def backtrack(index, used_digits, assignment):
        if index == len(huruf):
            if m.tujuan(assignment):
                hasil.append(assignment.copy())
            return

        char = huruf[index]
        for digit in m.kandidat(index, assignment):
            if maks is not None and len(hasil) > maks:
                return
            if digit in used_digits or (digit == 0 and char in m.huruf_awal):
                continue
            assignment[char] = digit
            used_digits.add(digit)
            backtrack(index + 1, used_digits, assignment)
            del assignment[char]
            used_digits.remove(digit)

    backtrack(0, set(), {})
    return hasil