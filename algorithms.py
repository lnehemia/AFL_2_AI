def _siapkan(w1, w2, w3):
    """Bagian yang dipakai bersama oleh kedua versi DFS,
    supaya urutan huruf & pruning dijamin identik."""
    huruf_unik_raw = list(dict.fromkeys(w1 + w2 + w3))
    huruf_awal = {w1[0], w2[0], w3[0]}

    weights = {char: 0 for char in huruf_unik_raw}
    for i, char in enumerate(reversed(w1)): weights[char] += 10**i
    for i, char in enumerate(reversed(w2)): weights[char] += 10**i
    for i, char in enumerate(reversed(w3)): weights[char] -= 10**i

    huruf_unik = sorted(huruf_unik_raw, key=lambda c: abs(weights[c]), reverse=True)
    max_sisa_bobot = [sum(abs(weights[c]) for c in huruf_unik[i:]) for i in range(len(huruf_unik))]
    return huruf_unik, huruf_awal, weights, max_sisa_bobot


def solve_cryptarithm_dfs_fast(w1, w2, w3):
    """DFS tanpa delay: dipakai untuk kunci jawaban & urutan huruf di UI."""
    huruf_unik, huruf_awal, weights, max_sisa_bobot = _siapkan(w1, w2, w3)

    def backtrack(index, current_sum, used_digits, assignment):
        if index == len(huruf_unik):
            return assignment.copy() if current_sum == 0 else None

        char = huruf_unik[index]
        weight = weights[char]

        if abs(current_sum) > max_sisa_bobot[index] * 9:
            return None

        for digit in range(10):
            if digit in used_digits or (digit == 0 and char in huruf_awal):
                continue
            assignment[char] = digit
            used_digits.add(digit)
            hasil = backtrack(index + 1, current_sum + weight * digit, used_digits, assignment)
            if hasil: return hasil
            del assignment[char]
            used_digits.remove(digit)
        return None

    solusi = backtrack(0, 0, set(), {})
    return solusi, huruf_unik


def solve_cryptarithm_dfs_realtime(w1, w2, w3, ai_agent, delay_per_step):
    """DFS yang sama persis dengan versi fast, tapi tiap percobaan digit
    ditampilkan lewat ai_agent.ai_ditemukan dan diberi delay.

    Aturan "1 langkah":
      - 1 langkah = 1 digit yang benar-benar di-assign (digit yang di-skip tidak dihitung)
      - huruf menyala SELAMA delay langkah itu berjalan
      - huruf baru padam setelah semua digit di levelnya habis dicoba (backtrack ke atas)
    """
    huruf_unik, huruf_awal, weights, max_sisa_bobot = _siapkan(w1, w2, w3)

    def backtrack(index, current_sum, used_digits, assignment):
        if not ai_agent.is_playing:
            return None

        if index == len(huruf_unik):
            if current_sum == 0:
                ai_agent.jawaban_ditemukan = True
                return assignment.copy()
            return None

        char = huruf_unik[index]
        weight = weights[char]

        if abs(current_sum) > max_sisa_bobot[index] * 9:
            return None

        for digit in range(10):
            if not ai_agent.is_playing:
                return None

            # digit yang di-skip tidak dihitung sebagai langkah (tanpa delay)
            if digit in used_digits or (digit == 0 and char in huruf_awal):
                continue

            # assign dulu, baru tunggu: hijau terlihat selama delay
            assignment[char] = digit
            used_digits.add(digit)
            if char not in ai_agent.ai_ditemukan:
                ai_agent.ai_ditemukan.append(char)

            if not ai_agent.tunggu(delay_per_step):   # dihentikan saat menunggu
                return None

            hasil = backtrack(index + 1, current_sum + weight * digit, used_digits, assignment)
            if hasil:
                return hasil   # solusi ketemu: semua huruf tetap hijau

            del assignment[char]
            used_digits.remove(digit)

        # semua digit di level ini sudah dicoba -> huruf padam, balik ke level atas
        if char in ai_agent.ai_ditemukan:
            ai_agent.ai_ditemukan.remove(char)
        return None

    backtrack(0, 0, set(), {})


def hitung_langkah(w1, w2, w3):
    """(Opsional) Hitung jumlah langkah DFS realtime tanpa delay.
    Berguna untuk menentukan delay: waktu AI ≈ langkah × delay."""
    huruf_unik, huruf_awal, weights, max_sisa_bobot = _siapkan(w1, w2, w3)
    langkah = 0

    def backtrack(index, current_sum, used_digits):
        nonlocal langkah
        if index == len(huruf_unik):
            return current_sum == 0
        char = huruf_unik[index]
        if abs(current_sum) > max_sisa_bobot[index] * 9:
            return False
        for digit in range(10):
            if digit in used_digits or (digit == 0 and char in huruf_awal):
                continue
            langkah += 1
            used_digits.add(digit)
            if backtrack(index + 1, current_sum + weights[char] * digit, used_digits):
                return True
            used_digits.remove(digit)
        return False

    backtrack(0, 0, set())
    return langkah