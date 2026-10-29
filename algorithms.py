import time

def solve_cryptarithm_dfs_fast(w1, w2, w3):
    huruf_unik_raw = list(dict.fromkeys(w1 + w2 + w3))
    huruf_awal = {w1[0], w2[0], w3[0]}

    weights = {char: 0 for char in huruf_unik_raw}
    for i, char in enumerate(reversed(w1)): weights[char] += 10**i
    for i, char in enumerate(reversed(w2)): weights[char] += 10**i
    for i, char in enumerate(reversed(w3)): weights[char] -= 10**i

    huruf_unik = sorted(huruf_unik_raw, key=lambda c: abs(weights[c]), reverse=True)
    max_sisa_bobot = [sum(abs(weights[c]) for c in huruf_unik[i:]) for i in range(len(huruf_unik))]

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
            hasil = backtrack(index + 1, current_sum + (weight * digit), used_digits, assignment)
            if hasil: return hasil
            del assignment[char]
            used_digits.remove(digit)
        return None

    solusi = backtrack(0, 0, set(), {})
    return solusi, huruf_unik

def solve_cryptarithm_dfs_realtime(w1, w2, w3, ai_agent, delay_per_step):
    huruf_unik_raw = list(dict.fromkeys(w1 + w2 + w3))
    huruf_awal = {w1[0], w2[0], w3[0]}

    weights = {char: 0 for char in huruf_unik_raw}
    for i, char in enumerate(reversed(w1)): weights[char] += 10**i
    for i, char in enumerate(reversed(w2)): weights[char] += 10**i
    for i, char in enumerate(reversed(w3)): weights[char] -= 10**i

    huruf_unik = sorted(huruf_unik_raw, key=lambda c: abs(weights[c]), reverse=True)
    max_sisa_bobot = [sum(abs(weights[c]) for c in huruf_unik[i:]) for i in range(len(huruf_unik))]

    def backtrack(index, current_sum, used_digits, assignment):
        if not ai_agent.is_playing: return None

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
            if not ai_agent.is_playing: return None 

            time.sleep(delay_per_step)

            if digit in used_digits or (digit == 0 and char in huruf_awal):
                continue

            assignment[char] = digit
            used_digits.add(digit)

            if char not in ai_agent.ai_ditemukan:
                ai_agent.ai_ditemukan.append(char)

            hasil = backtrack(index + 1, current_sum + (weight * digit), used_digits, assignment)
            if hasil: return hasil

            del assignment[char]
            used_digits.remove(digit)
            if char in ai_agent.ai_ditemukan:
                ai_agent.ai_ditemukan.remove(char)

        return None

    backtrack(0, 0, set(), {})