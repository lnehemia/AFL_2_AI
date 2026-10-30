import pygame
import sys
import threading
import csv
import os

from config import *
from algorithms import solve_cryptarithm_dfs_fast, solve_cryptarithm_dfs_realtime
from agent import AIAgent

class Game:
    def __init__(self, layar):
        self.layar = layar
        self.running = True
        self.font_judul = pygame.font.SysFont("consolas", 60, bold=True)
        self.font_besar = pygame.font.SysFont("consolas", 45, bold=True)
        self.font_sedang = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_kecil = pygame.font.SysFont("consolas", 20)
        
        self.state = "LOGIN"
        
        self.ai = AIAgent()
        self.username = ""
        self.total_skor = 0
        self.puzzle_idx = 0
        
        self.waktu_maksimal = 10 * 60 * 1000  # 10 Menit Global
        self.global_waktu_mulai = 0
        self.is_saved = False
        self.current_diff = None

    def simpan_ke_csv(self):
        file_exists = os.path.isfile("leaderboard.csv")
        with open("leaderboard.csv", "a", newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Username_Kelompok", "Total_Skor"])
            writer.writerow([self.username, self.total_skor])
        self.is_saved = True

    def muat_soal(self):
        soal, diff = ALL_PUZZLES[self.puzzle_idx]
        self.current_diff = diff
        
        w1, w2, w3 = soal
        solusi_dfs, urutan_efisien_dfs = solve_cryptarithm_dfs_fast(w1, w2, w3)
        
        self.w1, self.w2, self.w3 = w1, w2, w3
        self.solusi = solusi_dfs
        self.huruf_unik = urutan_efisien_dfs.copy() 
        
        self.player_inputs = {h: None for h in self.huruf_unik}
        self.selected_idx = 0
        
        self.ai.setup_round()
        delay_ai = self.current_diff.value[1]
        
        # Jalankan AI di Background
        ai_thread = threading.Thread(
            target=solve_cryptarithm_dfs_realtime, 
            args=(self.w1, self.w2, self.w3, self.ai, delay_ai)
        )
        ai_thread.daemon = True
        ai_thread.start()
        
        self.state = "PLAYING"
        self.pesan_akhir = ""
        self.warna_akhir = TEKS
        self.skor_akhir = 0

    def mulai_pertandingan(self, now):
        self.total_skor = 0
        self.puzzle_idx = 0
        self.global_waktu_mulai = now
        self.is_saved = False
        self.muat_soal()

    def kalkulasi_poin(self, menang):
        multiplier = self.current_diff.value[0]
        base_poin = 10
        return (base_poin * multiplier) if menang else (-base_poin * multiplier)

    def evaluasi_pemain(self):
        if None in self.player_inputs.values():
            return False, "GAGAL: Masih ada huruf yang kosong! (-Poin)"
            
        angka_terpakai = set(self.player_inputs.values())
        if len(angka_terpakai) != len(self.huruf_unik):
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
            self.mulai_pertandingan(now)
                
        elif self.state == "PLAYING":
            if event.key == pygame.K_LEFT:
                self.selected_idx = (self.selected_idx - 1) % len(self.huruf_unik)
            elif event.key == pygame.K_RIGHT:
                self.selected_idx = (self.selected_idx + 1) % len(self.huruf_unik)
            elif event.unicode.isnumeric():
                huruf_aktif = self.huruf_unik[self.selected_idx]
                self.player_inputs[huruf_aktif] = int(event.unicode)
                self.selected_idx = (self.selected_idx + 1) % len(self.huruf_unik)
            elif event.key == pygame.K_BACKSPACE:
                huruf_aktif = self.huruf_unik[self.selected_idx]
                self.player_inputs[huruf_aktif] = None
            elif event.key == pygame.K_TAB: 
                self.ai.is_playing = False
                self.skor_akhir = 0
                self.pesan_akhir = "ANDA MELAKUKAN SKIP! (Tidak ada pengurangan poin)"
                self.warna_akhir = KUNING
                self.state = "ROUND_OVER"
            elif event.key == pygame.K_RETURN: 
                is_win, msg = self.evaluasi_pemain()
                self.ai.is_playing = False 
                
                self.skor_akhir = self.kalkulasi_poin(True) if is_win else self.kalkulasi_poin(False)
                self.warna_akhir = HIJAU if is_win else MERAH
                self.total_skor += self.skor_akhir
                self.pesan_akhir = msg
                self.state = "ROUND_OVER"
                    
        elif self.state == "ROUND_OVER":
            if event.key == pygame.K_SPACE:
                self.puzzle_idx += 1
                if self.puzzle_idx >= len(ALL_PUZZLES):
                    self.state = "MATCH_OVER"
                    if not self.is_saved: self.simpan_ke_csv()
                else:
                    self.muat_soal()
            elif event.key == pygame.K_ESCAPE:
                self.state = "MATCH_OVER"
                if not self.is_saved: self.simpan_ke_csv()
        
        elif self.state == "MATCH_OVER" and event.key == pygame.K_SPACE:
            self.state = "LOGIN"
            self.username = ""

    def update(self, now):
        if self.state not in ["PLAYING", "ROUND_OVER"]:
            return
            
        durasi_berjalan = now - self.global_waktu_mulai
        sisa_waktu = max(0, self.waktu_maksimal - durasi_berjalan)
        
        if sisa_waktu <= 0:
            self.ai.is_playing = False
            self.state = "MATCH_OVER"
            if not self.is_saved: self.simpan_ke_csv()
            return
                
        if self.state == "PLAYING" and self.ai.answer_found:
            self.ai.is_playing = False
            self.skor_akhir = self.kalkulasi_poin(False)
            self.total_skor += self.skor_akhir
            self.pesan_akhir = "AI MEMECAHKAN TEKA-TEKI LEBIH DULU! (-Poin)"
            self.warna_akhir = PINK
            self.state = "ROUND_OVER"

    def draw_text(self, text, font, color, x, y, anchor="topleft"):
        surf = font.render(text, True, color)
        rect = surf.get_rect(**{anchor: (x, y)})
        self.screen.blit(surf, rect)
        return rect

    def render(self, now):
        self.screen.fill(BG)
        
        if self.state == "LOGIN":
            self.draw_text("CRYPTARITHM DUEL", self.title_font, CYAN, LEBAR//2, 200, "midtop")
            self.draw_text("Masukkan Username Kelompok Anda:", self.medium_font, ABU, LEBAR//2, 300, "midtop")
            pygame.draw.rect(self.screen, PANEL, (LEBAR//2 - 250, 360, 500, 60), border_radius=8)
            pygame.draw.rect(self.screen, GARIS, (LEBAR//2 - 250, 360, 500, 60), 2, border_radius=8)
            
            display_name = self.username + ("|" if (now // 500) % 2 == 0 else " ")
            self.draw_text(display_name, self.large_font, TEKS, LEBAR//2, 365, "midtop")
            
            self.draw_text("Tekan ENTER untuk Lanjut", self.small_font, CYAN, LEBAR//2, 450, "midtop")
            return
            
        if self.state == "MENU":
            self.draw_text("ATURAN MAIN", self.title_font, CYAN, LEBAR//2, 160, "midtop")
            instructions = [
                "1. Game berlangsung maksimal 10 MENIT untuk menyelesaikan 15 Soal.",
                "2. Soal akan muncul berurutan (5 Easy, 5 Medium, 5 Hard).",
                "3. Setiap kemenangan memberikan (+10/+20/+30) poin.",
                "4. Salah jawab atau didahului AI akan (-10/-20/-30) poin.",
                "5. Hanya ada 1 KESEMPATAN Submit (ENTER) per soal.",
                "6. Anda BISA SKIP soal (TAB) tanpa pengurangan poin.",
                "7. Anda BISA BERHENTI & SIMPAN SKOR di akhir setiap ronde (ESC).",
                "Tekan ENTER untuk Memulai Pertandingan!"
            ]
            for i, text in enumerate(instructions):
                self.draw_text(text, self.small_font, ABU, LEBAR//2, 250 + (i*35), "midtop")
            return

        duration = now - self.global_countdown
        time_remaining = max(0, self.max_time - duration)
        seconds_remaining = time_remaining // 1000
        
        self.draw_text(f"SOAL {self.puzzle_idx + 1}/15 - {self.current_diff.name}", self.small_font, KUNING, 20, 20, "topleft")
        self.draw_text("TIMER", self.small_font, ABU, LEBAR//2, 10, "midtop")
        self.draw_text(f"{seconds_remaining // 60:02d}:{seconds_remaining % 60:02d}", self.title_font, MERAH if time_remaining < 60000 else CYAN, LEBAR//2, 35, "midtop")
        self.draw_text(f"TOTAL SKOR: {self.total_score}", self.medium_font, HIJAU if self.total_score >= 0 else MERAH, LEBAR - 20, 20, "topright")
        pygame.draw.line(self.screen, GARIS, (0, 100), (LEBAR, 100), 2)

        if self.state == "MATCH_OVER":
            self.draw_text("PERTANDINGAN SELESAI!", self.title_font, CYAN, LEBAR//2, 250, "midtop")
            self.draw_text(f"Tim: {self.username}", self.large_font, ABU, LEBAR//2, 330, "midtop")
            self.draw_text(f"SKOR AKHIR ANDA: {self.total_score}", self.title_font, HIJAU if self.total_score >= 0 else MERAH, LEBAR//2, 390, "midtop")
            self.draw_text("Tekan SPACE untuk kembali", self.small_font, KUNING, LEBAR//2, 500, "midtop")
            return

        self.draw_text("Teka-Teki:", self.small_font, ABU, LEBAR//2, 120, "midtop")
        self.draw_text(f"{self.w1} + {self.w2} = {self.w3}", self.title_font, TEKS, LEBAR//2, 145, "midtop")

        letter_count = len(self.unique_letters)
        box_width, box_height, gap = 60, 80, 15
        start_x = LEBAR//2 - ((letter_count * box_width) + ((letter_count - 1) * gap))//2

        self.draw_text("AI:", self.small_font, PINK, LEBAR//2, 240, "midtop")
        for i, letter in enumerate(self.unique_letters):
            x = start_x + (i * (box_width + gap))
            pygame.draw.rect(self.screen, PANEL, (x, 270, box_width, box_height), border_radius=8)
            pygame.draw.rect(self.screen, GARIS, (x, 270, box_width, box_height), 2, border_radius=8)
            self.draw_text(letter, self.small_font, ABU, x + box_width//2, 280, "midtop")
            pygame.draw.circle(self.screen, HIJAU if letter in self.ai.ai_found else HITAM_BULAT, (x + box_width//2, 325), 15)

        self.draw_text("Anda:", self.small_font, CYAN, LEBAR//2, 400, "midtop")
        for i, letter in enumerate(self.unique_letters):
            x = start_x + (i * (box_width + gap))
            active = (i == self.selected_idx and self.state == "PLAYING")
            
            pygame.draw.rect(self.screen, CYAN if active else PANEL, (x, 430, box_width, box_height), 3 if active else 0, border_radius=8)
            if not active: pygame.draw.rect(self.screen, GARIS, (x, 430, box_width, box_height), 2, border_radius=8)
            self.draw_text(letter, self.small_font, ABU, x + box_width//2, 440, "midtop")
            val = self.player_inputs[letter]
            self.draw_text(str(val) if val is not None else "_", self.large_font, TEKS, x + box_width//2, 465, "midtop")

        if self.state == "PLAYING":
            self.draw_text("Panah: Pindah | Angka: Isi | ENTER: Submit | TAB: Skip Soal", self.small_font, ABU, LEBAR//2, 550, "midtop")

        if self.state == "ROUND_OVER":
            overlay = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            self.screen.blit(overlay, (0, 0))
            
            self.draw_text("RONDE SELESAI", self.title_font, self.final_color, LEBAR//2, 150, "midtop")
            self.draw_text(self.final_message, self.medium_font, TEKS, LEBAR//2, 220, "midtop")
            
            score_color = HIJAU if self.final_score > 0 else (KUNING if self.final_score == 0 else MERAH)
            score_text = f"SKOR: +{self.final_score}" if self.final_score > 0 else f"SKOR: {self.final_score}"
            self.draw_text(score_text, self.large_font, score_color, LEBAR//2, 270, "midtop")
            self.draw_text("Kunci Jawaban:", self.small_font, ABU, LEBAR//2, 340, "midtop")
            self.draw_text(" ".join([f"{k}:{v}" for k, v in self.solution.items()]), self.medium_font, HIJAU, LEBAR//2, 370, "midtop")
            
            self.draw_text("SPACE : Lanjut Soal Berikutnya", self.medium_font, CYAN, LEBAR//2, 480, "midtop")
            self.draw_text("ESC   : Akhiri Game", self.small_font, PINK, LEBAR//2, 530, "midtop")

def main():
    pygame.init()
    screen = pygame.display.set_mode((LEBAR, TINGGI))
    pygame.display.set_caption("Cryptarithm Duel")
    clock = pygame.time.Clock()
    game = Game(screen)

    while game.running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            game.process_event(event, now)
        game.update(now)
        game.render(now)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()