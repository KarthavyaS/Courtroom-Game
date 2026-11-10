"""Welcome and Onboarding Screen for LOGIC COURTROOM.
Features animated title, tagline, introductory lore, player profile naming onboarding,
and seamless continuation of saved progress.
"""
#pyright: ignore
import pygame
import math
from typing import Callable, Optional
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, get_font
)
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.text_box import TextBox

class WelcomeScreen:
    """Welcome and initial player onboarding screen."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        save_service: SaveService,
        on_start_game: Callable[[], None],
        on_continue_game: Callable[[], None]
    ):
        self.screen = screen
        self.game_state = game_state
        self.save_service = save_service
        self.on_start_game = on_start_game
        self.on_continue_game = on_continue_game
        self.sound_service = get_sound_service()

        self.anim_tick = 0
        self.has_active_save = self.save_service.has_active_save()
        self.active_save_summary = self.save_service.get_active_save_summary()

        # Onboarding modal state
        self.show_onboarding_modal = not self.game_state.profile.onboarded
        self.name_box = TextBox(
            (SCREEN_WIDTH - 320) // 2, 380, 320, 42,
            initial_text=self.game_state.profile.name,
            placeholder="Enter your lawyer name..."
        )

        # Welcome buttons
        btn_y = 480
        self.btn_start = AnimatedButton(
            (SCREEN_WIDTH - 240) // 2 if not self.has_active_save else (SCREEN_WIDTH - 420) // 2,
            btn_y, 190, 46, "ENTER COURT ➔", font_size=13,
            bg_color=ACCENT_GREEN, on_click=self._handle_start
        )
        self.btn_continue = AnimatedButton(
            (SCREEN_WIDTH + 40) // 2,
            btn_y, 190, 46, "CONTINUE CASE ➔", font_size=13,
            bg_color=(130, 85, 45), on_click=self._handle_continue
        )
        self.btn_save_name = AnimatedButton(
            (SCREEN_WIDTH - 180) // 2, 450, 180, 40,
            "BEGIN CAREER ➔", font_size=12, bg_color=ACCENT_GREEN,
            on_click=self._confirm_onboarding
        )

    def _handle_start(self) -> None:
        if self.show_onboarding_modal:
            return
        self.sound_service.play("gavel")
        self.on_start_game()

    def _handle_continue(self) -> None:
        self.sound_service.play("gavel")
        self.on_continue_game()

    def _confirm_onboarding(self) -> None:
        chosen_name = self.name_box.text.strip()
        if chosen_name:
            self.game_state.profile.name = chosen_name
            self.game_state.player_name = chosen_name
        self.game_state.profile.onboarded = True
        self.save_service.save_profile(self.game_state.profile)
        self.show_onboarding_modal = False
        self.sound_service.play("click")
        self.on_start_game()

    def handle_events(self, events) -> None:
        for event in events:
            if self.show_onboarding_modal:
                self.name_box.handle_event(event)
                self.btn_save_name.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self._confirm_onboarding()
            else:
                self.btn_start.handle_event(event)
                if self.has_active_save:
                    self.btn_continue.handle_event(event)

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        if self.show_onboarding_modal:
            self.btn_save_name.update(dt)
        else:
            self.btn_start.update(dt)
            if self.has_active_save:
                self.btn_continue.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Background decorative pillars and gavel glow
        pulse = (math.sin(self.anim_tick * 0.04) + 1.0) * 0.5

        # Backdrop panel
        card_w, card_h = 860, 560
        card_x, card_y = (SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        pygame.draw.rect(self.screen, CARD_BG, card_rect, border_radius=12)
        pygame.draw.rect(self.screen, GOLD_LIGHT, card_rect, 2, border_radius=12)

        # Scales / Gavel crest
        crest_y = card_y + 40
        crest_font = get_font(32)
        crest_surf = crest_font.render("⚖", True, GOLD)
        self.screen.blit(crest_surf, (card_x + (card_w - crest_surf.get_width()) // 2, crest_y))

        # Title
        title_font = get_font(28, bold=True)
        title_surf = title_font.render("LOGIC COURTROOM", True, GOLD)
        self.screen.blit(title_surf, (card_x + (card_w - title_surf.get_width()) // 2, crest_y + 48))

        # Tagline
        tag_font = get_font(13)
        tag_surf = tag_font.render("Where Logic Decides the Verdict", True, LIGHT_PARCHMENT)
        self.screen.blit(tag_surf, (card_x + (card_w - tag_surf.get_width()) // 2, crest_y + 88))

        # Decorative line
        line_w = 400
        line_x = card_x + (card_w - line_w) // 2
        pygame.draw.line(self.screen, GOLD, (line_x, crest_y + 115), (line_x + line_w, crest_y + 115), 1)

        if not self.show_onboarding_modal:
            # Concise introductory prompt
            intro_lines = [
                "Investigate crime scenes, question suspects, and discover forensic clues.",
                "Construct deductive arguments before the AI Judge. Pure logic decides the verdict."
            ]
            intro_font = get_font(12)
            iy = crest_y + 155
            for line in intro_lines:
                ls = intro_font.render(line, True, LIGHT_PARCHMENT)
                self.screen.blit(ls, (card_x + (card_w - ls.get_width()) // 2, iy))
                iy += 26

            # Active save notification if present
            if self.has_active_save and self.active_save_summary:
                sav = self.active_save_summary
                sav_rect = pygame.Rect(card_x + 120, iy + 25, card_w - 240, 58)
                pygame.draw.rect(self.screen, (40, 32, 28), sav_rect, border_radius=8)
                pygame.draw.rect(self.screen, (120, 90, 50), sav_rect, 1, border_radius=8)

                sav_font = get_font(11, bold=True)
                s1 = sav_font.render(f"UNFINISHED CASE: {sav['case_title'].upper()} ({sav['progress_pct']}% Done)", True, GOLD)
                s2 = get_font(10).render(f"Saved: {sav['timestamp']} • Clues: {sav['collected_count']}/{sav['total_evidence']}", True, MUTED_TEXT)
                self.screen.blit(s1, (sav_rect.x + 16, sav_rect.y + 12))
                self.screen.blit(s2, (sav_rect.x + 16, sav_rect.y + 32))

            # Buttons
            self.btn_start.draw(self.screen)
            if self.has_active_save:
                self.btn_continue.draw(self.screen)
        else:
            # Onboarding naming view
            onb_lines = [
                "WELCOME, COUNSELOR",
                "Before stepping into the Bar of Justice, please enter your legal name."
            ]
            self.screen.blit(get_font(16, bold=True).render(onb_lines[0], True, GOLD), (card_x + (card_w - 240) // 2, crest_y + 145))
            self.screen.blit(get_font(12).render(onb_lines[1], True, LIGHT_PARCHMENT), (card_x + (card_w - 520) // 2, crest_y + 180))

            # Name Input Box
            self.name_box.draw(self.screen)
            self.btn_save_name.draw(self.screen)
