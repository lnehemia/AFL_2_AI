import pygame
import sys
import threading
import csv
import os

from config import *
from algorithms import solve_cryptarithm_dfs_fast, solve_cryptarithm_dfs_realtime
from agent import AIAgent

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.title_font = pygame.font.SysFont("consolas", 60, bold=True)
        self.large_font = pygame.font.SysFont("consolas", 45, bold=True)
        self.medium_font = pygame.font.SysFont("consolas", 30, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 20)
        
        self.state = "LOGIN"
        
        self.ai = AIAgent()
        self.username = ""
        self.total_score = 0
        self.puzzle_idx = 0
        
        self.max_time = 10 * 60 * 1000
        self.global_countdown = 0
        self.is_saved = False
        self.current_diff = None

    def save_to_csv(self):
        file_exists = os.path.isfile("leaderboard.csv")
        with open("leaderboard.csv", "a", newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Group_Username", "Total_Score"])
            writer.writerow([self.username, self.total_score])
        self.is_saved = True

    def load_question(self):
        puzzle, diff = ALL_PUZZLES[self.puzzle_idx]
        self.current_diff = diff
        
        w1, w2, w3 = puzzle
        dfs_solution, dfs_efficient_order = solve_cryptarithm_dfs_fast(w1, w2, w3)
        
        self.w1, self.w2, self.w3 = w1, w2, w3
        self.solution = dfs_solution
        self.unique_letters = dfs_efficient_order.copy() 
        
        self.player_inputs = {letter: None for letter in self.unique_letters}
        self.selected_idx = 0
        
        self.ai.setup_round()
        ai_delay = self.current_diff.value[1]
        
        ai_thread = threading.Thread(
            target=solve_cryptarithm_dfs_realtime, 
            args=(self.w1, self.w2, self.w3, self.ai, ai_delay)
        )
        ai_thread.daemon = True
        ai_thread.start()
        
        self.state = "PLAYING"
        self.final_message = ""
        self.final_color = TEKS
        self.final_score = 0

    def start_game(self, now):
        self.total_score = 0
        self.puzzle_idx = 0
        self.global_countdown = now
        self.is_saved = False
        self.load_question()

    def point_calculation(self, win):
        multiplier = self.current_diff.value[0]
        base_points = 10
        return (base_points * multiplier) if win else (-base_points * multiplier)

    def evaluate_player(self):
        if None in self.player_inputs.values():
            return False, "GAGAL: Masih ada huruf yang kosong! (-Poin)"
            
        used_numbers = set(self.player_inputs.values())
        if len(used_numbers) != len(self.unique_letters):
            return False, "GAGAL: Setiap huruf harus memiliki angka unik! (-Poin)"

        try:
            n1 = int("".join(str(self.player_inputs[c]) for c in self.w1))
            n2 = int("".join(str(self.player_inputs[c]) for c in self.w2))
            n3 = int("".join(str(self.player_inputs[c]) for c in self.w3))
            
            if self.player_inputs[self.w1[0]] == 0 or self.player_inputs[self.w2[0]] == 0 or self.player_inputs[self.w3[0]] == 0:
                return False, "GAGAL: Huruf awal tidak boleh bernilai 0! (-Poin)"
                
            if n1 + n2 == n3:
                return True, "ANDA MENANG! Kalkulasi Akurat."
            else:
                return False, f"GAGAL: {n1} + {n2} != {n3} (-Poin)"
        except:
            return False, "GAGAL: Format tidak valid."

    def process_event(self, event, now):
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
            self.start_game(now)
                
        elif self.state == "PLAYING":
            if event.key == pygame.K_LEFT:
                self.selected_idx = (self.selected_idx - 1) % len(self.unique_letters)
            elif event.key == pygame.K_RIGHT:
                self.selected_idx = (self.selected_idx + 1) % len(self.unique_letters)
            elif event.unicode.isnumeric():
                active_letter = self.unique_letters[self.selected_idx]
                self.player_inputs[active_letter] = int(event.unicode)
                self.selected_idx = (self.selected_idx + 1) % len(self.unique_letters)
            elif event.key == pygame.K_BACKSPACE:
                active_letter = self.unique_letters[self.selected_idx]
                self.player_inputs[active_letter] = None
            elif event.key == pygame.K_TAB: 
                self.ai.is_playing = False
                self.final_score = 0
                self.final_message = "ANDA MELAKUKAN SKIP! (Tidak ada pengurangan poin)"
                self.final_color = KUNING
                self.state = "ROUND_OVER"
            elif event.key == pygame.K_RETURN: 
                is_win, msg = self.evaluate_player()
                self.ai.is_playing = False 
                
                self.final_score = self.point_calculation(True) if is_win else self.point_calculation(False)
                self.final_color = HIJAU if is_win else MERAH
                self.total_score += self.final_score
                self.final_message = msg
                self.state = "ROUND_OVER"
                    
        elif self.state == "ROUND_OVER":
            if event.key == pygame.K_SPACE:
                self.puzzle_idx += 1
                if self.puzzle_idx >= len(ALL_PUZZLES):
                    self.state = "MATCH_OVER"
                    if not self.is_saved: self.save_to_csv()
                else:
                    self.load_question()
            elif event.key == pygame.K_ESCAPE:
                self.state = "MATCH_OVER"
                if not self.is_saved: self.save_to_csv()
        
        elif self.state == "MATCH_OVER" and event.key == pygame.K_SPACE:
            self.state = "LOGIN"
            self.username = ""

    def update(self, now):
        if self.state not in ["PLAYING", "ROUND_OVER"]:
            return
            
        elapsed_duration = now - self.global_countdown
        time_remaining = max(0, self.max_time - elapsed_duration)
        
        if time_remaining <= 0:
            self.ai.is_playing = False
            self.state = "MATCH_OVER"
            if not self.is_saved: self.save_to_csv()
            return
                
        if self.state == "PLAYING" and self.ai.answer_found:
            self.ai.is_playing = False
            self.final_score = self.point_calculation(False)
            self.total_score += self.final_score
            self.final_message = "AI MEMECAHKAN TEKA-TEKI LEBIH DULU! (-Poin)"
            self.final_color = PINK
            self.state = "ROUND_OVER"

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
        for i, huruf in enumerate(self.huruf_unik):
            x = start_x + (i * (k_w + spasi))
            pygame.draw.rect(self.layar, PANEL, (x, 270, k_w, k_h), border_radius=8)
            pygame.draw.rect(self.layar, GARIS, (x, 270, k_w, k_h), 2, border_radius=8)
            self.draw_teks(huruf, self.font_kecil, ABU, x + k_w//2, 280, "midtop")
            pygame.draw.circle(self.layar, HIJAU if huruf in self.ai.ai_ditemukan else HITAM_BULAT, (x + k_w//2, 325), 15)

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