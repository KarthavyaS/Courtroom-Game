"""Modal Confirmation Dialog Component for LOGIC COURTROOM.
Used for confirming destructive actions, exiting without saving, resetting progress, etc.
"""

import pygame
from typing import Callable, Optional
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CARD_BG, GOLD, GOLD_LIGHT,
    WHITE, MUTED_TEXT, ACCENT_RED, ACCENT_GREEN, get_font
)
from components.animated_button import AnimatedButton

class ConfirmationDialog:
    """Renders a modal overlay prompting the user for confirmation."""

    def __init__(
        self,
        title: str,
        message: str,
        on_confirm: Callable[[], None],
        on_cancel: Callable[[], None],
        confirm_text: str = "CONFIRM",
        cancel_text: str = "CANCEL",
        confirm_color: tuple = ACCENT_RED
    ):
        self.title = title
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        self.width = 460
        self.height = 220
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        btn_w = 140
        btn_h = 38
        btn_y = self.y + self.height - 54

        self.btn_cancel = AnimatedButton(
            self.x + 60, btn_y, btn_w, btn_h, cancel_text,
            font_size=12, bg_color=(60, 50, 45), on_click=self.on_cancel
        )
        self.btn_confirm = AnimatedButton(
            self.x + self.width - 60 - btn_w, btn_y, btn_w, btn_h, confirm_text,
            font_size=12, bg_color=confirm_color, on_click=self.on_confirm
        )

    def handle_events(self, events) -> bool:
        """Returns True if the event was consumed by the dialog."""
        for event in events:
            self.btn_cancel.handle_event(event)
            self.btn_confirm.handle_event(event)
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                return True
        return True

    def update(self, dt: float = 0.016) -> None:
        self.btn_cancel.update(dt)
        self.btn_confirm.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        # Dark dimming background
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        surface.blit(dim_surf, (0, 0))

        # Modal box
        pygame.draw.rect(surface, CARD_BG, self.rect, border_radius=10)
        pygame.draw.rect(surface, GOLD, self.rect, 2, border_radius=10)

        # Title
        t_font = get_font(15, bold=True)
        t_surf = t_font.render(self.title, True, GOLD)
        surface.blit(t_surf, (self.x + (self.width - t_surf.get_width()) // 2, self.y + 20))

        # Message (multiline support)
        m_font = get_font(12)
        words = self.message.split(" ")
        lines = []
        cur_line = []
        for w in words:
            test_line = " ".join(cur_line + [w])
            if m_font.size(test_line)[0] > (self.width - 40):
                lines.append(" ".join(cur_line))
                cur_line = [w]
            else:
                cur_line.append(w)
        if cur_line:
            lines.append(" ".join(cur_line))

        line_y = self.y + 65
        for line in lines:
            line_surf = m_font.render(line, True, WHITE)
            surface.blit(line_surf, (self.x + (self.width - line_surf.get_width()) // 2, line_y))
            line_y += 22

        # Buttons
        self.btn_cancel.draw(surface)
        self.btn_confirm.draw(surface)
