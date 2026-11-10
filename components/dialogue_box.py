"""Dialogue Box Component with Typewriter Animation, Speaker Badges,
and Safe Text Wrapping for Courtroom Proceedings.
"""

import pygame
import math
from typing import Optional, List
from config import (
    WOOD_BROWN, DARK_BROWN, GOLD, GOLD_LIGHT, WHITE, BLACK,
    ACCENT_RED, ACCENT_BLUE, ACCENT_GREEN, MUTED_TEXT, get_font
)

class DialogueBox:
    """An animated, typewriter-style dialogue panel for courtroom interactions."""

    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.speaker: str = "Judge"
        self.full_text: str = ""
        self.displayed_text: str = ""
        self.char_index: float = 0.0
        self.typewriter_speed: float = 45.0  # chars per second
        self.is_finished: bool = True
        self.anim_time: float = 0.0
        self.speaker_color = GOLD
        self.accent_color = GOLD_LIGHT
        self.pre_wrapped_lines: List[str] = []

    def set_message(self, speaker: str, text: str, instant: bool = False):
        """Sets a new message, pre-wraps lines, and initiates typewriter reveal."""
        self.speaker = speaker
        self.full_text = text
        self.char_index = 0.0 if not instant else float(len(text))
        self.displayed_text = "" if not instant else text
        self.is_finished = instant

        font_body = get_font(17, bold=False)
        max_width = self.rect.width - 44
        self.pre_wrapped_lines = self._wrap_text(self.full_text, font_body, max_width)

        if "judge" in speaker.lower() or "magistrate" in speaker.lower():
            self.speaker_color = GOLD
            self.accent_color = (255, 235, 120)
        elif "counsel" in speaker.lower() or "lawyer" in speaker.lower() or "player" in speaker.lower():
            self.speaker_color = ACCENT_BLUE
            self.accent_color = (135, 206, 250)
        elif "warning" in speaker.lower() or "bailiff" in speaker.lower():
            self.speaker_color = ACCENT_RED
            self.accent_color = (255, 120, 120)
        else:
            self.speaker_color = ACCENT_GREEN
            self.accent_color = (144, 238, 144)

    def skip_animation(self):
        """Instantly finishes displaying the full text."""
        self.char_index = float(len(self.full_text))
        self.displayed_text = self.full_text
        self.is_finished = True

    def update(self, dt: float = 0.016):
        self.anim_time += dt
        if not self.is_finished:
            self.char_index += self.typewriter_speed * dt
            target_len = min(len(self.full_text), int(self.char_index))
            self.displayed_text = self.full_text[:target_len]
            if target_len >= len(self.full_text):
                self.is_finished = True

    def draw(self, surface: pygame.Surface):
        self.update()

        from components.ui_shapes import draw_chamfered_rect, draw_ribbon_badge
        r = self.rect

        # 1. Main Innovative Chamfered Background Panel with Inner Glow
        draw_chamfered_rect(
            surface=surface,
            rect=r,
            bg_color=(20, 13, 9),
            border_color=self.speaker_color,
            cut=12,
            border_width=2,
            corner_brackets=True,
            inner_glow=True
        )

        # 2. Innovative Speaker Ribbon Header Badge
        header_w = 230
        header_h = 34
        header_rect = pygame.Rect(r.x + 20, r.y - 17, header_w, header_h)
        draw_ribbon_badge(
            surface=surface,
            rect=header_rect,
            text=self.speaker.upper(),
            bg_color=(38, 22, 14),
            border_color=self.speaker_color,
            text_color=self.accent_color,
            font_size=14
        )

        # 3. Render Pre-wrapped Text Lines with stable heights & high contrast
        font_body = get_font(17, bold=False)
        line_height = font_body.get_linesize() + 5
        chars_remaining = int(self.char_index)

        line_y = r.y + 26
        for line in self.pre_wrapped_lines:
            if line_y + font_body.get_linesize() > r.bottom - 6:
                break

            if chars_remaining <= 0:
                break

            visible_count = min(len(line), chars_remaining)
            visible_line = line[:visible_count]
            chars_remaining -= (len(line) + 1)

            # High-contrast text shadow
            shadow_surf = font_body.render(visible_line, True, (8, 6, 4))
            surface.blit(shadow_surf, (r.x + 23, line_y + 1))
            txt_surf = font_body.render(visible_line, True, WHITE)
            surface.blit(txt_surf, (r.x + 22, line_y))
            line_y += line_height

        # 4. Blinking Advance Indicator Prompt
        if self.is_finished:
            blink = int(math.sin(self.anim_time * 6.0) * 128 + 127)
            if blink > 80:
                font_hint = get_font(13, bold=True)
                hint_surf = font_hint.render("▼ [READY / SPACE]", True, GOLD_LIGHT)
                surface.blit(hint_surf, (r.right - 155, r.bottom - 24))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        words = text.split(" ")
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

