# main.py
import pygame
import sys
import threading
import csv
import os
import math

from agent import AIAgent
from config import *
from algorithms import solve_cryptarithm_dfs_fast, solve_cryptarithm_dfs_realtime

class Game:
    def __init__(self, layar):
        self.layar = layar
        self.running = True
        self.font_judul = pygame.font.SysFont("consolas", 60, bold=True)
        self.font_besar = pygame.font.SysFont("consolas", 45, bold=True)
        self.font_sedang = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_kecil = pygame.font.SysFont("consolas", 20)

        # States: LOGIN -> MENU -> PLAYING (mode TRIAL, loops forever) -> PLAYING (mode MATCH) -> MATCH_OVER
        self.state = "LOGIN"
        self.mode = "TRIAL"
        self.puzzles = TRIAL_PUZZLES

        self.ai = AIAgent()
        self.ai_thread = None
        self.jeda_ai_sampai = 0
        self.username = ""
        self.total_skor = 0
        self.puzzle_idx = 0

        self.waktu_maksimal = 10 * 60 * 1000  # 10 minutes global
        self.global_waktu_mulai = 0
        self.durasi_akhir = 0                  # frozen elapsed time once the match ends
        self.is_saved = False
        self.current_diff = None

        # Answer history of all match puzzles (list of dict)
        self.riwayat = []
        self.review_open = False
        self.review_page = 0

        # Short notification (not a popup, does not pause the game)
        self.notif_teks = ""
        self.notif_warna = TEKS
        self.notif_sampai = 0

    # ---------------------------------------------------------
    # UTILITIES
    # ---------------------------------------------------------
    def simpan_ke_csv(self):
        file_exists = os.path.isfile("leaderboard.csv")
        with open("leaderboard.csv", "a", newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Username_Kelompok", "Total_Skor"])
            writer.writerow([self.username, self.total_skor])
        self.is_saved = True

    def hentikan_ai(self):
        """Hentikan AI ronde lama. Thread langsung bangun & keluar sendiri."""
        self.ai.is_playing = False

    def set_notif(self, teks, warna, durasi=2500):
        self.notif_teks = teks
        self.notif_warna = warna
        self.notif_sampai = pygame.time.get_ticks() + durasi

    def catat_hasil(self, status, skor, pesan, warna):
        """Record the result of the current puzzle. In TRIAL mode only a notification is shown."""
        if self.mode == "MATCH":
            self.riwayat.append({
                "no": self.puzzle_idx + 1,
                "diff": self.current_diff.name,
                "soal": f"{self.w1} + {self.w2} = {self.w3}",
                "huruf": list(self.huruf_unik),
                "jawaban_pemain": dict(self.player_inputs),
                "kunci_ai": dict(self.solusi) if self.solusi else {},
                "status": status,
                "skor": skor,
                "pesan": pesan,
            })
            self.total_skor += skor
        self.set_notif(f"Puzzle {self.puzzle_idx + 1}: {pesan}", warna)

    def selesai_pertandingan(self):
        self.hentikan_ai()
        # Freeze the timer the moment the match ends
        self.durasi_akhir = min(pygame.time.get_ticks() - self.global_waktu_mulai, self.waktu_maksimal)
        self.state = "MATCH_OVER"
        self.review_open = False
        self.review_page = 0
        if not self.is_saved:
            self.simpan_ke_csv()

    def lanjut_soal(self):
        self.puzzle_idx += 1
        if self.mode == "TRIAL":
            # Trial loops forever
            self.puzzle_idx %= len(self.puzzles)
            self.muat_soal()
        elif self.puzzle_idx >= len(self.puzzles):
            self.selesai_pertandingan()
        else:
            self.muat_soal()

    # ---------------------------------------------------------
    # GAME LOGIC
    # ---------------------------------------------------------
    def muat_soal(self):
        # Hentikan AI lama, lalu pakai objek AIAgent BARU.
        # Thread lama tetap memegang objek lamanya, jadi tidak bisa
        # mengotori indikator / jawaban_ditemukan milik soal baru.
        self.hentikan_ai()
        self.ai = AIAgent()
        self.jeda_ai_sampai = 0

        soal, diff, delay_ai = self.puzzles[self.puzzle_idx]
        self.current_diff = diff

        w1, w2, w3 = soal
        solusi_dfs, urutan_efisien_dfs = solve_cryptarithm_dfs_fast(w1, w2, w3)

        self.w1, self.w2, self.w3 = w1, w2, w3
        self.solusi = solusi_dfs
        self.huruf_unik = urutan_efisien_dfs.copy()

        self.player_inputs = {h: None for h in self.huruf_unik}
        self.selected_idx = 0

        self.ai.setup_round()

        self.ai_thread = threading.Thread(
            target=solve_cryptarithm_dfs_realtime,
            args=(self.w1, self.w2, self.w3, self.ai, delay_ai)
        )
        self.ai_thread.daemon = True
        self.ai_thread.start()

        self.state = "PLAYING"

    def mulai_trial(self):
        self.mode = "TRIAL"
        self.puzzles = TRIAL_PUZZLES
        self.puzzle_idx = 0
        self.notif_teks = ""
        self.muat_soal()

    def mulai_pertandingan(self, now):
        self.hentikan_ai()
        self.mode = "MATCH"
        self.puzzles = ALL_PUZZLES
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
        if None in self.player_inputs.values():
            return False, "FAILED: Some boxes are still empty!"

        angka_terpakai = set(self.player_inputs.values())
        if len(angka_terpakai) != len(self.huruf_unik):
            return False, "FAILED: Every letter must have a unique digit!"

        try:
            n1 = int("".join(str(self.player_inputs[c]) for c in self.w1))
            n2 = int("".join(str(self.player_inputs[c]) for c in self.w2))
            n3 = int("".join(str(self.player_inputs[c]) for c in self.w3))

            if self.player_inputs[self.w1[0]] == 0 or self.player_inputs[self.w2[0]] == 0 or self.player_inputs[self.w3[0]] == 0:
                return False, "FAILED: The first letter cannot be 0!"

            if n1 + n2 == n3:
                return True, "CORRECT! Accurate calculation."
            else:
                return False, f"FAILED: {n1} + {n2} != {n3}"
        except Exception:
            return False, "FAILED: Invalid format."

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
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
            # AI sudah menang: abaikan input sampai soal berganti
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
                    # In practice mode there is no match to end, so just move to the next trial puzzle
                    self.catat_hasil("SURRENDER", 0, "You surrendered (trial only)", KUNING)
                    self.lanjut_soal()
                else:
                    # SURRENDER: the whole match ends right now. The current puzzle is recorded
                    # with 0 points, the remaining puzzles are never shown or played,
                    # and the player keeps the score they have so far.
                    self.catat_hasil("SURRENDER", 0, "You surrendered (match ended, score kept)", KUNING)
                    self.selesai_pertandingan()
            elif event.key == pygame.K_RETURN:
                # SUBMIT: only allowed when every box is filled
                if None in self.player_inputs.values():
                    self.set_notif("Fill in ALL boxes before submitting!", KUNING, 1800)
                    return
                is_win, msg = self.evaluasi_pemain()
                self.ai.is_playing = False
                skor = self.kalkulasi_poin(is_win)
                self.catat_hasil("CORRECT" if is_win else "WRONG", skor, msg, HIJAU if is_win else MERAH)
                self.lanjut_soal()
            elif event.key == pygame.K_ESCAPE:
                if self.mode == "TRIAL":
                    # END TRIAL: start the real match
                    self.mulai_pertandingan(now)
                else:
                    # STOP & SAVE SCORE (current puzzle is recorded with no points)
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

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------
    def update(self, now):
        if self.state != "PLAYING":
            return

        # AI menemukan solusi: skor langsung dicatat, lalu jeda agar hijau terlihat
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

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def draw_teks(self, teks, font, warna, x, y, anchor="topleft"):
        surf = font.render(teks, True, warna)
        rect = surf.get_rect(**{anchor: (x, y)})
        self.layar.blit(surf, rect)
        return rect

    # --- Answer review popup ---
    ENTRY_H = 90

    def per_page_review(self):
        panel_h = TINGGI - 100
        return max(1, (panel_h - 130) // self.ENTRY_H)

    def total_halaman_review(self):
        return max(1, math.ceil(len(self.riwayat) / self.per_page_review()))

    def render_review(self):
        # Dim the screen behind the popup
        dim = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        self.layar.blit(dim, (0, 0))

        panel_w, panel_h = LEBAR - 120, TINGGI - 100
        px, py = (LEBAR - panel_w) // 2, (TINGGI - panel_h) // 2

        # Semi-transparent panel
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
            self.draw_teks(f"You : {jawab}", self.font_kecil, wrn if r["status"] in ("CORRECT", "WRONG") else ABU, px + 25, y + 28, "topleft")
            self.draw_teks(f"AI  : {kunci}", self.font_kecil, HIJAU, px + 25, y + 54, "topleft")
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
            self.draw_teks("HOW TO PLAY", self.font_judul, CYAN, LEBAR//2, 120, "midtop")
            instruksi = [
                "1. You start with a TRIAL ROUND: practice puzzles that loop endlessly.",
                "2. Press ESC during the trial whenever you are ready to start the real match.",
                "3. The match lasts at most 10 MINUTES for 15 puzzles (5 Easy, 5 Medium, 5 Hard).",
                "4. Each win gives (+10/+20/+30) points.",
                "5. A wrong answer or being beaten by the AI costs (-10/-20/-30) points.",
                "6. You get only 1 submit (ENTER) per puzzle, and ALL boxes must be filled.",
                "7. Press S to SURRENDER: the match ends and you keep your current score.",
                "8. You can STOP & SAVE your score at any time during the match (ESC).",
                "9. Once finished, press R to review your answers and the AI's key.",
                "Press ENTER to Start the Trial Round!"
            ]
            for i, teks in enumerate(instruksi):
                warna = CYAN if i == len(instruksi) - 1 else ABU
                self.draw_teks(teks, self.font_kecil, warna, LEBAR//2, 215 + (i*35), "midtop")
            return

        # HEADER & TIMER
        if self.state == "MATCH_OVER":
            durasi = self.durasi_akhir          # timer is frozen
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
                self.draw_teks(f"PUZZLE {self.puzzle_idx + 1}/{len(ALL_PUZZLES)} - {self.current_diff.name}", self.font_kecil, KUNING, 20, 20, "topleft")

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

        # PUZZLE & LAYOUT
        self.draw_teks("Puzzle:", self.font_kecil, ABU, LEBAR//2, 120, "midtop")
        self.draw_teks(f"{self.w1} + {self.w2} = {self.w3}", self.font_judul, TEKS, LEBAR//2, 145, "midtop")

        jum_huruf = len(self.huruf_unik)
        k_w, k_h, spasi = 60, 80, 15
        start_x = LEBAR//2 - ((jum_huruf * k_w) + ((jum_huruf - 1) * spasi))//2

        # RENDER AI
        self.draw_teks("AI:", self.font_kecil, PINK, LEBAR//2, 240, "midtop")
        final = self.ai.jawaban_ditemukan
        for i, huruf in enumerate(self.huruf_unik):
            x = start_x + (i * (k_w + spasi))
            pygame.draw.rect(self.layar, PANEL, (x, 270, k_w, k_h), border_radius=8)
            pygame.draw.rect(self.layar, GARIS, (x, 270, k_w, k_h), 2, border_radius=8)
            self.draw_teks(huruf, self.font_kecil, ABU, x + k_w//2, 280, "midtop")

            if final:
                warna_bulat = HIJAU
            elif huruf in self.ai.ai_ditemukan:
                warna_bulat = KUNING
            else:
                warna_bulat = HITAM_BULAT
            pygame.draw.circle(self.layar, warna_bulat, (x + k_w//2, 325), 15)

        # RENDER PLAYER
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

        # Result of the previous puzzle (small text, does not pause the game)
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