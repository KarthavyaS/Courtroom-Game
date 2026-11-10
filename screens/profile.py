"""Player Profile & Career Statistics Screen for LOGIC COURTROOM.
Allows players to customize their advocate name, select avatar persona,
and view career win/loss statistics, accuracy ratings, and achievements
with high-contrast vibrant styling for 1100x680 resolution.
"""

import pygame
from typing import Callable, Optional
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, GOLD_DARK, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, get_font
)
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.text_box import TextBox
from components.character_sprite import CharacterSprite
from components.animation import ParticleSystem

class ProfileScreen:
    """Player Profile & Career Dossier Screen."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        save_service: SaveService,
        on_back: Callable[[], None]
    ):
        self.screen = screen
        self.game_state = game_state
        self.save_service = save_service
        self.on_back = on_back
        self.sound_service = get_sound_service()

        self.btn_back = AnimatedButton(30, 16, 110, 36, "← HUB", font_size=11, bg_color=(55, 42, 35), on_click=self.on_back)
        self.btn_save = AnimatedButton(SCREEN_WIDTH - 180, 16, 150, 36, "SAVE PROFILE 💾", font_size=11, bg_color=ACCENT_GREEN, on_click=self._save_profile)

        # Name text box
        self.tb_name = TextBox(55, 270, 310, 38, placeholder="Enter Advocate Name...", font_size=13, initial_text=self.game_state.profile.name)

        # Character avatar preview
        self.avatar_sprite = CharacterSprite(character_type=self.game_state.profile.avatar_id or "lawyer", name=self.game_state.profile.name)

        # Avatar selections
        self.avatars = ["lawyer", "socialite", "butler", "doctor"]
        self.avatar_buttons = []
        for i, av in enumerate(self.avatars):
            def make_handler(aid=av):
                def handler():
                    self._select_avatar(aid)
                return handler
            btn = AnimatedButton(45 + (i * 85), 455, 80, 32, av.capitalize(), font_size=10, bg_color=(50, 38, 30), border_color=(120, 95, 70), on_click=make_handler())
            self.avatar_buttons.append(btn)

        self.particles = ParticleSystem(max_particles=20)
        self.anim_time = 0.0

    def _select_avatar(self, aid: str):
        self.game_state.profile.avatar_id = aid
        self.avatar_sprite.character_type = aid
        self.sound_service.play("click")
        self.game_state.set_notification(f"Avatar updated to {aid.replace('_', ' ').title()}!", category="INFO")

    def _save_profile(self):
        new_name = self.tb_name.get_text().strip()
        if new_name:
            self.game_state.profile.name = new_name
            self.game_state.player_name = new_name
            self.avatar_sprite.name = new_name
        self.save_service.save_profile(self.game_state.profile)
        self.sound_service.play("evidence")
        self.game_state.set_notification("Barrister Profile Saved Successfully!", category="SUCCESS")

    def handle_events(self, events):
        for event in events:
            self.btn_back.handle_event(event)
            self.btn_save.handle_event(event)
            self.tb_name.handle_event(event)
            for btn in self.avatar_buttons:
                btn.handle_event(event)

    def update(self, dt: float = 0.016):
        self.anim_time += dt
        self.particles.update(dt)
        self.avatar_sprite.update(dt)
        self.btn_back.update(dt)
        self.btn_save.update(dt)
        self.tb_name.update(dt)
        for btn in self.avatar_buttons:
            btn.update(dt)

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.particles.draw(self.screen)

        # Header Bar
        pygame.draw.rect(self.screen, WOOD_BROWN, (0, 0, SCREEN_WIDTH, 56))
        pygame.draw.line(self.screen, GOLD, (0, 56), (SCREEN_WIDTH, 56), 2)

        # Header Title
        t_surf = get_font(18, bold=True).render("BARRISTER DOSSIER & PROFILE", True, GOLD)
        self.screen.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 28)))

        self.btn_back.draw(self.screen)
        self.btn_save.draw(self.screen)

        # Left Column: Identity & Avatar (x: 35, y: 70, w: 350, h: 575)
        id_rect = pygame.Rect(35, 75, 350, 575)
        self._draw_identity_card(id_rect)

        # Right Column: Career Statistics & Honors (x: 405, y: 70, w: 660, h: 575)
        stats_rect = pygame.Rect(405, 75, 660, 575)
        self._draw_career_card(stats_rect)

    def _draw_identity_card(self, rect: pygame.Rect):
        pygame.draw.rect(self.screen, CARD_BG, rect, border_radius=10)
        pygame.draw.rect(self.screen, GOLD_LIGHT, rect, width=1, border_radius=10)

        header = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, 34)
        pygame.draw.rect(self.screen, (45, 32, 25), header, border_top_left_radius=8, border_top_right_radius=8)
        self.screen.blit(get_font(12, bold=True).render("ADVOCATE IDENTITY", True, GOLD), (header.x + 14, header.y + 8))

        # Animated Avatar Display
        portrait_rect = pygame.Rect(rect.centerx - 45, rect.y + 45, 90, 95)
        self.avatar_sprite.draw(self.screen, portrait_rect)

        # Name label
        lbl_font = get_font(11, bold=True)
        self.screen.blit(lbl_font.render("ADVOCATE FULL NAME:", True, GOLD), (rect.x + 20, rect.y + 155))
        self.tb_name.rect.x = rect.x + 20
        self.tb_name.rect.y = rect.y + 175
        self.tb_name.rect.width = rect.width - 40
        self.tb_name.draw(self.screen)

        # Rank badge
        rank_str = self.game_state.profile.get_rank()
        self.screen.blit(lbl_font.render("OFFICIAL JUDICIAL RANK:", True, GOLD), (rect.x + 20, rect.y + 225))

        rank_badge = pygame.Rect(rect.x + 20, rect.y + 245, rect.width - 40, 36)
        pygame.draw.rect(self.screen, (48, 35, 28), rank_badge, border_radius=6)
        pygame.draw.rect(self.screen, GOLD, rank_badge, width=1, border_radius=6)
        r_surf = get_font(12, bold=True).render(f"👑 {rank_str}", True, GOLD_LIGHT)
        self.screen.blit(r_surf, r_surf.get_rect(center=rank_badge.center))

        # Avatar Choice buttons
        self.screen.blit(lbl_font.render("SELECT COURTROOM AVATAR PERSONA:", True, GOLD), (rect.x + 20, rect.y + 295))
        for i, btn in enumerate(self.avatar_buttons):
            btn.rect.x = rect.x + 15 + (i * 80)
            btn.rect.y = rect.y + 320
            btn.is_selected = (self.game_state.profile.avatar_id == self.avatars[i])
            btn.draw(self.screen)

        # Motto Box
        motto_box = pygame.Rect(rect.x + 15, rect.bottom - 170, rect.width - 30, 150)
        pygame.draw.rect(self.screen, (30, 22, 18), motto_box, border_radius=6)
        pygame.draw.rect(self.screen, (80, 60, 45), motto_box, width=1, border_radius=6)

        self.screen.blit(get_font(11, bold=True).render("⚖ HIGH COURT CREED:", True, GOLD), (motto_box.x + 10, motto_box.y + 8))
        motto_lines = [
            '"In this chamber, accusations mean nothing',
            ' without sound logical deduction.',
            ' Truth is entailed by evidence and verified facts."'
        ]
        m_y = motto_box.y + 35
        for line in motto_lines:
            self.screen.blit(get_font(10, italic=True).render(line, True, WHITE), (motto_box.x + 10, m_y))
            m_y += 24

    def _draw_career_card(self, rect: pygame.Rect):
        pygame.draw.rect(self.screen, CARD_BG, rect, border_radius=10)
        pygame.draw.rect(self.screen, GOLD_LIGHT, rect, width=1, border_radius=10)

        header = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, 34)
        pygame.draw.rect(self.screen, (45, 32, 25), header, border_top_left_radius=8, border_top_right_radius=8)
        self.screen.blit(get_font(12, bold=True).render("CAREER COURTROOM PERFORMANCE & HONORS", True, GOLD), (header.x + 14, header.y + 8))

        prof = self.game_state.profile

        # 4 Performance Metric Cards
        metric_boxes = [
            ("TOTAL SCORE", f"{prof.total_score} PTS", GOLD_LIGHT, (48, 38, 30)),
            ("CASES WON", f"{prof.cases_won} / {prof.cases_completed}", ACCENT_GREEN, (30, 48, 32)),
            ("HIGHEST SCORE", f"{prof.highest_score} PTS", ACCENT_BLUE, (30, 40, 55)),
            ("WIN RATIO", f"{int((prof.cases_won / max(1, prof.cases_completed)) * 100)}%", GOLD, (48, 38, 30))
        ]

        bw = (rect.width - 60) // 2
        bh = 80
        for i, (label, val, col, bg_c) in enumerate(metric_boxes):
            bx = rect.x + 20 + (i % 2) * (bw + 20)
            by = rect.y + 55 + (i // 2) * (bh + 15)
            m_rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(self.screen, bg_c, m_rect, border_radius=8)
            pygame.draw.rect(self.screen, col, m_rect, width=1, border_radius=8)

            self.screen.blit(get_font(10, bold=True).render(label, True, LIGHT_PARCHMENT), (bx + 12, by + 12))
            self.screen.blit(get_font(20, bold=True).render(val, True, col), (bx + 12, by + 36))

        # Achievements Section
        ach_y = rect.y + 260
        self.screen.blit(get_font(13, bold=True).render("HONORS & BARRISTER ACHIEVEMENTS:", True, GOLD), (rect.x + 20, ach_y))

        achievements_list = [
            ("Bar Examination Gold Medal", "Mastered fundamental propositional deduction principles.", True),
            ("Counsel of the Crown", "Achieved over 500 cumulative points in judicial hearings.", prof.total_score >= 500),
            ("Master of Inference", "Successfully refuted suspect alibis with forensic evidence.", prof.cases_won >= 2),
            ("Lord Chief Justice's Gavel", "Solved all master-level complex homicides.", prof.total_score >= 1200)
        ]

        ay = ach_y + 30
        for name, desc, unlocked in achievements_list:
            a_rect = pygame.Rect(rect.x + 20, ay, rect.width - 40, 58)
            a_bg = (35, 42, 35) if unlocked else (30, 24, 20)
            pygame.draw.rect(self.screen, a_bg, a_rect, border_radius=6)
            bdr = ACCENT_GREEN if unlocked else (70, 55, 45)
            pygame.draw.rect(self.screen, bdr, a_rect, width=1, border_radius=6)

            icon_str = "🏆" if unlocked else "🔒"
            self.screen.blit(get_font(14).render(icon_str, True, GOLD if unlocked else MUTED_TEXT), (a_rect.x + 12, a_rect.y + 14))

            t_col = GOLD if unlocked else MUTED_TEXT
            self.screen.blit(get_font(11, bold=True).render(name, True, t_col), (a_rect.x + 40, a_rect.y + 8))
            self.screen.blit(get_font(10).render(desc, True, WHITE if unlocked else (150, 140, 130)), (a_rect.x + 40, a_rect.y + 30))

            ay += 68
