"""Settings and Accessibility Screen for LOGIC COURTROOM.
Allows configuring Sound FX, Victorian Courtroom Ambient Music, Volume,
replaying the Academy Interactive Tutorial, and resetting all player progress.
"""

import pygame
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
from components.confirmation_dialog import ConfirmationDialog

class SettingsScreen:
    """Settings and audio configuration screen."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        save_service: SaveService,
        on_back: Callable[[], None],
        on_replay_tutorial: Callable[[], None]
    ):
        self.screen = screen
        self.game_state = game_state
        self.save_service = save_service
        self.on_back = on_back
        self.on_replay_tutorial = on_replay_tutorial
        self.sound_service = get_sound_service()

        self.anim_tick = 0
        self.confirm_dialog: Optional[ConfirmationDialog] = None

        # Back Button
        self.btn_back = AnimatedButton(40, 16, 120, 36, "← DASHBOARD", font_size=11, bg_color=(60, 45, 38), on_click=self.on_back)

        # Setting Controls
        self._build_controls()

    def _build_controls(self) -> None:
        cx = 320
        y = 130

        # Sound FX Toggle
        sfx_txt = "SOUND FX: ENABLED [ON]" if self.game_state.profile.sound_enabled else "SOUND FX: MUTED [OFF]"
        sfx_bg = ACCENT_GREEN if self.game_state.profile.sound_enabled else (75, 40, 35)
        self.btn_sfx = AnimatedButton(cx, y, 460, 44, sfx_txt, font_size=12, bg_color=sfx_bg, on_click=self._toggle_sfx)

        # Music Toggle
        y += 60
        mus_txt = "COURTROOM MUSIC: PLAYING [ON]" if self.game_state.profile.music_enabled else "COURTROOM MUSIC: MUTED [OFF]"
        mus_bg = ACCENT_GREEN if self.game_state.profile.music_enabled else (75, 40, 35)
        self.btn_mus = AnimatedButton(cx, y, 460, 44, mus_txt, font_size=12, bg_color=mus_bg, on_click=self._toggle_music)

        # Volume Adjust
        y += 60
        vol_pct = int(self.game_state.profile.volume * 100)
        self.btn_vol_down = AnimatedButton(cx, y, 140, 40, "VOLUME -", font_size=11, bg_color=(60, 50, 45), on_click=self._volume_down)
        self.btn_vol_up = AnimatedButton(cx + 320, y, 140, 40, "VOLUME +", font_size=11, bg_color=(60, 50, 45), on_click=self._volume_up)

        # Replay Tutorial
        y += 75
        self.btn_tutorial = AnimatedButton(cx, y, 460, 44, "🎓 REPLAY INTERACTIVE TUTORIAL", font_size=12, bg_color=(50, 70, 85), on_click=self._replay_tut)

        # Reset Progress Button
        y += 65
        self.btn_reset = AnimatedButton(cx, y, 460, 44, "⚠ RESET ALL SAVED PROGRESS", font_size=12, bg_color=(100, 35, 30), on_click=self._prompt_reset)

        self.buttons = [self.btn_sfx, self.btn_mus, self.btn_vol_down, self.btn_vol_up, self.btn_tutorial, self.btn_reset]

    def _toggle_sfx(self) -> None:
        self.game_state.profile.sound_enabled = not self.game_state.profile.sound_enabled
        self.sound_service.set_sound_enabled(self.game_state.profile.sound_enabled)
        self.save_service.save_profile(self.game_state.profile)
        self._build_controls()
        self.sound_service.play("click")

    def _toggle_music(self) -> None:
        self.game_state.profile.music_enabled = not self.game_state.profile.music_enabled
        self.sound_service.set_music_enabled(self.game_state.profile.music_enabled)
        self.save_service.save_profile(self.game_state.profile)
        self._build_controls()
        self.sound_service.play("click")

    def _volume_down(self) -> None:
        self.game_state.profile.volume = max(0.0, round(self.game_state.profile.volume - 0.1, 1))
        self.sound_service.set_volume(self.game_state.profile.volume)
        self.save_service.save_profile(self.game_state.profile)
        self.sound_service.play("click")

    def _volume_up(self) -> None:
        self.game_state.profile.volume = min(1.0, round(self.game_state.profile.volume + 0.1, 1))
        self.sound_service.set_volume(self.game_state.profile.volume)
        self.save_service.save_profile(self.game_state.profile)
        self.sound_service.play("click")

    def _replay_tut(self) -> None:
        self.sound_service.play("click")
        self.on_replay_tutorial()

    def _prompt_reset(self) -> None:
        self.sound_service.play("click")
        self.confirm_dialog = ConfirmationDialog(
            title="RESET ALL PROGRESS?",
            message="This will erase all career statistics, high scores, and unfinished investigation saves.",
            on_confirm=self._execute_reset,
            on_cancel=self._cancel_reset,
            confirm_text="ERASE DATA",
            cancel_text="CANCEL",
            confirm_color=ACCENT_RED
        )

    def _execute_reset(self) -> None:
        self.save_service.reset_all_progress()
        self.game_state.profile = self.save_service.load_profile()
        self.confirm_dialog = None
        self.sound_service.play("gavel")
        self.game_state.set_notification("All progress has been reset to defaults.", category="WARNING")
        self._build_controls()

    def _cancel_reset(self) -> None:
        self.confirm_dialog = None
        self.sound_service.play("click")

    def handle_events(self, events) -> None:
        if self.confirm_dialog:
            self.confirm_dialog.handle_events(events)
            return

        for event in events:
            self.btn_back.handle_event(event)
            for btn in self.buttons:
                btn.handle_event(event)

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.btn_back.update(dt)
        if self.confirm_dialog:
            self.confirm_dialog.update(dt)
        else:
            for btn in self.buttons:
                btn.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Header Bar
        pygame.draw.rect(self.screen, WOOD_BROWN, (0, 0, SCREEN_WIDTH, 56))
        pygame.draw.line(self.screen, GOLD, (0, 56), (SCREEN_WIDTH, 56), 2)

        self.btn_back.draw(self.screen)
        self.screen.blit(get_font(16, bold=True).render("PREFERENCES & SYSTEM SETTINGS", True, GOLD), (180, 18))

        # Main Card Panel
        card_rect = pygame.Rect(260, 85, 580, 530)
        pygame.draw.rect(self.screen, CARD_BG, card_rect, border_radius=10)
        pygame.draw.rect(self.screen, GOLD_LIGHT, card_rect, 1, border_radius=10)

        # Volume level indicator in center
        vol_pct = int(self.game_state.profile.volume * 100)
        vol_surf = get_font(12, bold=True).render(f"Volume: {vol_pct}%", True, GOLD)
        self.screen.blit(vol_surf, (SCREEN_WIDTH // 2 - vol_surf.get_width() // 2, 260))

        # Render Controls
        for btn in self.buttons:
            btn.draw(self.screen)

        # Confirmation Dialog if active
        if self.confirm_dialog:
            self.confirm_dialog.draw(self.screen)
