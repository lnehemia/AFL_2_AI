# main.py
import pygame
import sys
import threading
import csv
import os
import math

from agent import AIAgent
from config import *
from algorithms import (
    solve_cryptarithm_dfs_fast,
    solve_cryptarithm_dfs_realtime,
    cari_semua_solusi,
    cek_relasi,
)
from generator import buat_daftar_soal


class Game:
    def __init__(self, layar):
        self.layar = layar
        self.running = True
        self.font_judul = pygame.font.SysFont("consolas", 60, bold=True)
        self.font_besar = pygame.font.SysFont("consolas", 45, bold=True)
        self.font_sedang = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_kecil = pygame.font.SysFont("consolas", 20)

        # States: LOGIN -> MENU -> PLAYING (mode TRIAL, soal baru terus) -> PLAYING (mode MATCH) -> MATCH_OVER
        self.state = "LOGIN"
        self.mode = "TRIAL"
        self.puzzles = []                # diisi oleh buat_daftar_soal() saat trial / match dimulai

        self.ai = AIAgent()
        self.ai_thread = None
        self.jeda_ai_sampai = 0
        self.username = ""
        self.total_skor = 0
        self.puzzle_idx = 0

        self.waktu_maksimal = 15 * 60 * 1000
        self.global_waktu_mulai = 0
        self.durasi_akhir = 0
        self.is_saved = False
        self.current_diff = None

        # Data soal yang sedang dimainkan
        self.w1 = self.w2 = self.w3 = ""
        self.op = "+"
        self.solusi = None               # kunci jawaban pertama (yang ditemukan DFS fast)
        self.jml_solusi = 1              # jumlah seluruh kunci jawaban yang valid

        self.riwayat = []
        self.review_open = False
        self.review_page = 0

        self.notif_teks = ""
        self.notif_warna = TEKS
        self.notif_sampai = 0

    def simpan_ke_csv(self):
        file_exists = os.path.isfile("leaderboard.csv")
        with open("leaderboard.csv", "a", newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Username_Kelompok", "Total_Skor"])
            writer.writerow([self.username, self.total_skor])
        self.is_saved = True

    def hentikan_ai(self):
        self.ai.is_playing = False

    def set_notif(self, teks, warna, durasi=2500):
        self.notif_teks = teks
        self.notif_warna = warna
        self.notif_sampai = pygame.time.get_ticks() + durasi

    def catat_hasil(self, status, skor, pesan, warna):
        if self.mode == "MATCH":
            self.riwayat.append({
                "no": self.puzzle_idx + 1,
                "diff": self.current_diff.name,
                "soal": f"{self.w1} {OP_TAMPIL[self.op]} {self.w2} = {self.w3}",
                "huruf": list(self.huruf_unik),
                "jawaban_pemain": dict(self.player_inputs),
                "kunci_ai": dict(self.solusi) if self.solusi else {},
                "jml_kunci": self.jml_solusi,
                "status": status,
                "skor": skor,
                "pesan": pesan,
            })
            self.total_skor += skor
        self.set_notif(f"Puzzle {self.puzzle_idx + 1}: {pesan}", warna)

    def selesai_pertandingan(self):
        self.hentikan_ai()
        self.durasi_akhir = min(pygame.time.get_ticks() - self.global_waktu_mulai, self.waktu_maksimal)
        self.state = "MATCH_OVER"
        self.review_open = False
        self.review_page = 0
        if not self.is_saved:
            self.simpan_ke_csv()

    def lanjut_soal(self):
        self.puzzle_idx += 1
        if self.mode == "TRIAL":
            # Trial tidak pernah habis: setelah soal terakhir, buat soal-soal baru
            if self.puzzle_idx >= len(self.puzzles):
                self.puzzles = buat_daftar_soal(TRIAL_KOMPOSISI)
                self.puzzle_idx = 0
            self.muat_soal()
        elif self.puzzle_idx >= len(self.puzzles):
            self.selesai_pertandingan()
        else:
            self.muat_soal()

    def muat_soal(self):
        self.hentikan_ai()
        self.ai = AIAgent()
        self.jeda_ai_sampai = 0

        soal, diff, delay_ai = self.puzzles[self.puzzle_idx]
        self.current_diff = diff

        w1, op, w2, w3 = soal
        solusi_dfs, urutan_efisien_dfs = solve_cryptarithm_dfs_fast(w1, op, w2, w3)

        self.w1, self.op, self.w2, self.w3 = w1, op, w2, w3
        self.solusi = solusi_dfs
        self.jml_solusi = max(1, len(cari_semua_solusi(w1, op, w2, w3, maks=MAKS_SOLUSI)))
        self.huruf_unik = urutan_efisien_dfs.copy()

        self.player_inputs = {h: None for h in self.huruf_unik}
        self.selected_idx = 0

        self.ai.setup_round()

        self.ai_thread = threading.Thread(
            target=solve_cryptarithm_dfs_realtime,
            args=(self.w1, self.op, self.w2, self.w3, self.ai, delay_ai)
        )
        self.ai_thread.daemon = True
        self.ai_thread.start()

        self.state = "PLAYING"

    def mulai_trial(self):
        self.mode = "TRIAL"
        self.puzzles = buat_daftar_soal(TRIAL_KOMPOSISI)
        self.puzzle_idx = 0
        self.notif_teks = ""
        self.muat_soal()

    def mulai_pertandingan(self, now):
        self.hentikan_ai()
        self.mode = "MATCH"
        self.puzzles = buat_daftar_soal(MATCH_KOMPOSISI)
        self.total_skor = 0
        self.puzzle_idx = 0
        self.global_waktu_mulai = now
        self.durasi_akhir = 0
        self.is_saved = False
        self.riwayat = []
        self.review_open = False
        self.review_page = 0
        self.notif_teks = ""
        self.muat_soal()

    def kalkulasi_poin(self, menang):
        multiplier = self.current_diff.value
        base_poin = 10
        return (base_poin * multiplier) if menang else (-base_poin * multiplier)

    def evaluasi_pemain(self):
        kosong = [h for h in self.huruf_unik if self.player_inputs[h] is None]
        if kosong:
            return None, "Fill in ALL boxes first!"

        huruf_awal = {self.w1[0], self.w2[0], self.w3[0]}
        nol = [h for h in self.huruf_unik if h in huruf_awal and self.player_inputs[h] == 0]
        if nol:
            return None, f"The first letter cannot be 0! ({', '.join(nol)})"

        pemakai = {}
        for h in self.huruf_unik:
            pemakai.setdefault(self.player_inputs[h], []).append(h)
        for digit, daftar in pemakai.items():
            if len(daftar) > 1:
                return None, f"Digit {digit} is used by more than one letter! ({', '.join(daftar)})"

        # Dinilai dengan hitungan, BUKAN dengan membandingkan ke kunci DFS,
        # sehingga semua kunci jawaban yang valid dianggap benar.
        n1 = int("".join(str(self.player_inputs[c]) for c in self.w1))
        n2 = int("".join(str(self.player_inputs[c]) for c in self.w2))
        n3 = int("".join(str(self.player_inputs[c]) for c in self.w3))

        if cek_relasi(self.op, n1, n2, n3):
            return True, "CORRECT! Accurate calculation."
        return False, f"FAILED: {n1} {OP_TAMPIL[self.op]} {n2} != {n3}"

    def proses_event(self, event, now):
        if event.type == pygame.QUIT:
            self.running = False
            self.ai.is_playing = False
            return

        if event.type != pygame.KEYDOWN:
            return

        if self.state == "LOGIN":
            if event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.key == pygame.K_RETURN and len(self.username.strip()) > 0:
                self.state = "MENU"
            else:
                if event.unicode.isalnum() or event.unicode in [" ", "_", "-"]:
                    if len(self.username) < 20:
                        self.username += event.unicode

        elif self.state == "MENU" and event.key == pygame.K_RETURN:
            self.mulai_trial()

        elif self.state == "PLAYING":
            if self.jeda_ai_sampai:
                return

            if event.key == pygame.K_LEFT:
                self.selected_idx = (self.selected_idx - 1) % len(self.huruf_unik)
            elif event.key == pygame.K_RIGHT:
                self.selected_idx = (self.selected_idx + 1) % len(self.huruf_unik)
            elif event.unicode and event.unicode in "0123456789":
                huruf_aktif = self.huruf_unik[self.selected_idx]
                self.player_inputs[huruf_aktif] = int(event.unicode)
                self.selected_idx = (self.selected_idx + 1) % len(self.huruf_unik)
            elif event.key == pygame.K_BACKSPACE:
                huruf_aktif = self.huruf_unik[self.selected_idx]
                self.player_inputs[huruf_aktif] = None
            elif event.key == pygame.K_s:
                self.ai.is_playing = False
                if self.mode == "TRIAL":
                    self.catat_hasil("SURRENDER", 0, "You surrendered (trial only)", KUNING)
                    self.lanjut_soal()
                else:
                    self.catat_hasil("SURRENDER", 0, "You surrendered (match ended, score kept)", KUNING)
                    self.selesai_pertandingan()
            elif event.key == pygame.K_RETURN:
                is_win, msg = self.evaluasi_pemain()

                # None = input belum valid: tampilkan pesan, tahan Enter (tanpa skor, soal tidak berganti)
                if is_win is None:
                    self.set_notif(msg, KUNING, 2500)
                    return

                self.ai.is_playing = False
                skor = self.kalkulasi_poin(is_win)
                self.catat_hasil("CORRECT" if is_win else "WRONG", skor, msg, HIJAU if is_win else MERAH)
                self.lanjut_soal()
            elif event.key == pygame.K_ESCAPE:
                if self.mode == "TRIAL":
                    self.mulai_pertandingan(now)
                else:
                    self.ai.is_playing = False
                    self.catat_hasil("STOPPED", 0, "Game stopped", KUNING)
                    self.selesai_pertandingan()

        elif self.state == "MATCH_OVER":
            if event.key == pygame.K_r:
                self.review_open = not self.review_open
                self.review_page = 0
            elif self.review_open and event.key == pygame.K_RIGHT:
                self.review_page = min(self.review_page + 1, self.total_halaman_review() - 1)
            elif self.review_open and event.key == pygame.K_LEFT:
                self.review_page = max(self.review_page - 1, 0)
            elif self.review_open and event.key == pygame.K_ESCAPE:
                self.review_open = False
            elif event.key == pygame.K_SPACE:
                self.review_open = False
                self.state = "LOGIN"
                self.username = ""

    def update(self, now):
        if self.state != "PLAYING":
            return

        if self.ai.jawaban_ditemukan:
            if self.jeda_ai_sampai == 0:
                self.jeda_ai_sampai = now + 1200
                skor = self.kalkulasi_poin(False)
                self.catat_hasil("AI FIRST", skor, "The AI solved the puzzle first!", PINK)
            elif now >= self.jeda_ai_sampai:
                self.jeda_ai_sampai = 0
                self.lanjut_soal()
            return

        if self.mode == "MATCH":
            durasi_berjalan = now - self.global_waktu_mulai
            sisa_waktu = max(0, self.waktu_maksimal - durasi_berjalan)

            if sisa_waktu <= 0:
                self.ai.is_playing = False
                self.catat_hasil("TIME UP", 0, "Time is up", MERAH)
                self.selesai_pertandingan()
                return

    def draw_teks(self, teks, font, warna, x, y, anchor="topleft"):
        surf = font.render(teks, True, warna)
        rect = surf.get_rect(**{anchor: (x, y)})
        self.layar.blit(surf, rect)
        return rect

    ENTRY_H = 90

    def per_page_review(self):
        panel_h = TINGGI - 100
        return max(1, (panel_h - 130) // self.ENTRY_H)

    def total_halaman_review(self):
        return max(1, math.ceil(len(self.riwayat) / self.per_page_review()))

    def render_review(self):
        dim = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        self.layar.blit(dim, (0, 0))

        panel_w, panel_h = LEBAR - 120, TINGGI - 100
        px, py = (LEBAR - panel_w) // 2, (TINGGI - panel_h) // 2

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 24, 36, 225), (0, 0, panel_w, panel_h), border_radius=12)
        self.layar.blit(panel, (px, py))
        pygame.draw.rect(self.layar, GARIS, (px, py, panel_w, panel_h), 2, border_radius=12)

        self.draw_teks("ANSWER REVIEW", self.font_sedang, CYAN, LEBAR // 2, py + 15, "midtop")
        pygame.draw.line(self.layar, GARIS, (px + 20, py + 60), (px + panel_w - 20, py + 60), 1)

        warna_status = {
            "CORRECT": HIJAU, "WRONG": MERAH, "SURRENDER": KUNING,
            "AI FIRST": PINK, "TIME UP": MERAH, "STOPPED": KUNING,
        }

        per_page = self.per_page_review()
        total_hal = self.total_halaman_review()
        self.review_page = max(0, min(self.review_page, total_hal - 1))
        mulai = self.review_page * per_page
        tampil = self.riwayat[mulai:mulai + per_page]

        if not self.riwayat:
            self.draw_teks("No puzzles were attempted.", self.font_kecil, ABU, LEBAR // 2, py + 100, "midtop")

        y = py + 70
        for r in tampil:
            wrn = warna_status.get(r["status"], TEKS)
            skor_txt = f"+{r['skor']}" if r["skor"] > 0 else str(r["skor"])
            self.draw_teks(f"#{r['no']} [{r['diff']}] {r['soal']}", self.font_kecil, TEKS, px + 25, y, "topleft")
            self.draw_teks(f"{r['status']} ({skor_txt})", self.font_kecil, wrn, px + panel_w - 25, y, "topright")

            jawab = " ".join(
                f"{h}:{r['jawaban_pemain'][h] if r['jawaban_pemain'][h] is not None else '_'}"
                for h in r["huruf"]
            )
            kunci = " ".join(f"{h}:{r['kunci_ai'].get(h, '?')}" for h in r["huruf"])
            ekstra = f"   (+{r['jml_kunci'] - 1} other valid keys)" if r["jml_kunci"] > 1 else ""
            self.draw_teks(f"You : {jawab}", self.font_kecil, wrn if r["status"] in ("CORRECT", "WRONG") else ABU, px + 25, y + 28, "topleft")
            self.draw_teks(f"AI  : {kunci}{ekstra}", self.font_kecil, HIJAU, px + 25, y + 54, "topleft")
            y += self.ENTRY_H

        footer = f"Page {self.review_page + 1}/{total_hal}  |  <- / -> : Change Page  |  R : Close"
        self.draw_teks(footer, self.font_kecil, ABU, LEBAR // 2, py + panel_h - 35, "midtop")

    def render(self, now):
        self.layar.fill(BG)

        if self.state == "LOGIN":
            self.draw_teks("CRYPTARITHM DUEL", self.font_judul, CYAN, LEBAR//2, 200, "midtop")
            self.draw_teks("Enter Your Team Username:", self.font_sedang, ABU, LEBAR//2, 300, "midtop")
            pygame.draw.rect(self.layar, PANEL, (LEBAR//2 - 250, 360, 500, 60), border_radius=8)
            pygame.draw.rect(self.layar, GARIS, (LEBAR//2 - 250, 360, 500, 60), 2, border_radius=8)

            tampil_nama = self.username + ("|" if (now // 500) % 2 == 0 else " ")
            self.draw_teks(tampil_nama, self.font_besar, TEKS, LEBAR//2, 365, "midtop")

            self.draw_teks("Press ENTER to Continue", self.font_kecil, CYAN, LEBAR//2, 450, "midtop")
            return

        if self.state == "MENU":
            n_easy = MATCH_KOMPOSISI.count(Difficulty.EASY)
            n_med = MATCH_KOMPOSISI.count(Difficulty.MEDIUM)
            n_hard = MATCH_KOMPOSISI.count(Difficulty.HARD)
            self.draw_teks("HOW TO PLAY", self.font_judul, CYAN, LEBAR//2, 120, "midtop")
            instruksi = [
                "1. You start with a TRIAL ROUND: practice puzzles that never run out.",
                "2. Press ESC during the trial whenever you are ready to start the real match.",
                f"3. The match lasts at most {self.waktu_maksimal // 60000} MINUTES for {len(MATCH_KOMPOSISI)} puzzles ({n_easy} Easy, {n_med} Medium, {n_hard} Hard).",
                "4. Puzzles are random. Easy: + and -   Medium: x   Hard: : (exact division).",
                "5. Each win gives (+10/+20/+30) points.",
                "6. A wrong answer or being beaten by the AI costs (-10/-20/-30) points.",
                "7. Only 1 submit (ENTER) per puzzle. ALL boxes must be filled. Any valid key counts.",
                "8. Press S to SURRENDER: the match ends and you keep your current score.",
                "9. You can STOP & SAVE your score at any time during the match (ESC).",
                "10. Once finished, press R to review your answers and the AI's key.",
                "Press ENTER to Start the Trial Round!"
            ]
            for i, teks in enumerate(instruksi):
                warna = CYAN if i == len(instruksi) - 1 else ABU
                self.draw_teks(teks, self.font_kecil, warna, LEBAR//2, 215 + (i*35), "midtop")
            return

        if self.state == "MATCH_OVER":
            durasi = self.durasi_akhir
        else:
            durasi = now - self.global_waktu_mulai
        sisa_waktu = max(0, self.waktu_maksimal - durasi)
        detik_sisa = sisa_waktu // 1000

        if self.state == "PLAYING":
            if self.mode == "TRIAL":
                self.draw_teks(f"TRIAL ROUND - {self.current_diff.name}", self.font_kecil, KUNING, 20, 20, "topleft")
                self.draw_teks("PRACTICE MODE", self.font_sedang, CYAN, LEBAR//2, 30, "midtop")
                self.draw_teks("No timer, score not counted", self.font_kecil, ABU, LEBAR//2, 68, "midtop")
                self.draw_teks("Press ESC to start the real match", self.font_kecil, HIJAU, LEBAR - 20, 20, "topright")
            else:
                self.draw_teks(f"PUZZLE {self.puzzle_idx + 1}/{len(self.puzzles)} - {self.current_diff.name}", self.font_kecil, KUNING, 20, 20, "topleft")

        if self.state == "MATCH_OVER" or self.mode == "MATCH":
            self.draw_teks("TIMER", self.font_kecil, ABU, LEBAR//2, 10, "midtop")
            warna_timer = MERAH if (sisa_waktu < 60000 and self.state != "MATCH_OVER") else CYAN
            self.draw_teks(f"{detik_sisa // 60:02d}:{detik_sisa % 60:02d}", self.font_judul, warna_timer, LEBAR//2, 35, "midtop")
            self.draw_teks(f"TOTAL SCORE: {self.total_skor}", self.font_sedang, HIJAU if self.total_skor >= 0 else MERAH, LEBAR - 20, 20, "topright")
        pygame.draw.line(self.layar, GARIS, (0, 100), (LEBAR, 100), 2)

        if self.state == "MATCH_OVER":
            self.draw_teks("MATCH FINISHED!", self.font_judul, CYAN, LEBAR//2, 250, "midtop")
            self.draw_teks(f"Team: {self.username}", self.font_besar, ABU, LEBAR//2, 330, "midtop")
            self.draw_teks(f"YOUR FINAL SCORE: {self.total_skor}", self.font_judul, HIJAU if self.total_skor >= 0 else MERAH, LEBAR//2, 390, "midtop")
            self.draw_teks("Press R to see the correct answers", self.font_sedang, CYAN, LEBAR//2, 470, "midtop")
            self.draw_teks("Press SPACE to go back", self.font_kecil, KUNING, LEBAR//2, 520, "midtop")

            if self.review_open:
                self.render_review()
            return

        self.draw_teks("Puzzle:", self.font_kecil, ABU, LEBAR//2, 120, "midtop")
        self.draw_teks(f"{self.w1} {OP_TAMPIL[self.op]} {self.w2} = {self.w3}", self.font_judul, TEKS, LEBAR//2, 145, "midtop")

        jum_huruf = len(self.huruf_unik)
        k_w, k_h, spasi = 60, 80, 15
        start_x = LEBAR//2 - ((jum_huruf * k_w) + ((jum_huruf - 1) * spasi))//2

        self.draw_teks("AI:", self.font_kecil, PINK, LEBAR//2, 240, "midtop")
        final = self.ai.jawaban_ditemukan
        for i, huruf in enumerate(self.huruf_unik):
            x = start_x + (i * (k_w + spasi))
            pygame.draw.rect(self.layar, PANEL, (x, 270, k_w, k_h), border_radius=8)
            pygame.draw.rect(self.layar, GARIS, (x, 270, k_w, k_h), 2, border_radius=8)
            self.draw_teks(huruf, self.font_kecil, ABU, x + k_w//2, 280, "midtop")

            # hitam = belum dicoba, kuning = digit tentatif (bisa di-backtrack), hijau = jawaban fixed
            if final:
                warna_bulat = HIJAU
            elif huruf in self.ai.ai_ditemukan:
                warna_bulat = KUNING
            else:
                warna_bulat = HITAM
            pygame.draw.circle(self.layar, warna_bulat, (x + k_w//2, 325), 15)

        self.draw_teks("You:", self.font_kecil, CYAN, LEBAR//2, 400, "midtop")
        for i, huruf in enumerate(self.huruf_unik):
            x = start_x + (i * (k_w + spasi))
            aktif = (i == self.selected_idx and self.state == "PLAYING")

            pygame.draw.rect(self.layar, CYAN if aktif else PANEL, (x, 430, k_w, k_h), 3 if aktif else 0, border_radius=8)
            if not aktif:
                pygame.draw.rect(self.layar, GARIS, (x, 430, k_w, k_h), 2, border_radius=8)
            self.draw_teks(huruf, self.font_kecil, ABU, x + k_w//2, 440, "midtop")
            val = self.player_inputs[huruf]
            self.draw_teks(str(val) if val is not None else "_", self.font_besar, TEKS, x + k_w//2, 465, "midtop")

        if self.state == "PLAYING":
            if self.mode == "TRIAL":
                hint = "Arrows: Move | Digits: Fill | ENTER: Submit | S: Surrender | ESC: Start Match"
            else:
                hint = "Arrows: Move | Digits: Fill | ENTER: Submit | S: Surrender (End Match) | ESC: Stop & Save"
            self.draw_teks(hint, self.font_kecil, ABU, LEBAR//2, 550, "midtop")

        if self.notif_teks and now < self.notif_sampai:
            self.draw_teks(self.notif_teks, self.font_kecil, self.notif_warna, LEBAR//2, TINGGI - 12, "midbottom")


def main():
    pygame.init()
    layar = pygame.display.set_mode((LEBAR, TINGGI))
    pygame.display.set_caption("Cryptarithm Duel")
    clock = pygame.time.Clock()
    game = Game(layar)

    while game.running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            game.proses_event(event, now)
        game.update(now)
        game.render(now)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()