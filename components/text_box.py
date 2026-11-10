"""Interactive Single and Multiline Text Input Component for LOGIC COURTROOM.
"""
#pyright: ignore
import pygame
import time
from typing import Optional, Tuple, List
from config import (
    CARD_BG, LIGHT_PARCHMENT, DARK_BROWN, WOOD_BROWN, GOLD,
    MUTED_TEXT, WHITE, get_font
)

class TextBox:
    """An interactive editable text box with cursor, selection, and multiline support."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        placeholder: str = "Type here...",
        font_size: int = 16,
        is_multiline: bool = False,
        border_radius: int = 8,
        initial_text: str = ""
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.font_size = font_size
        self.font = get_font("Georgia", font_size)
        self.is_multiline = is_multiline
        self.border_radius = border_radius
        self.text = initial_text
        self.is_active = False
        self.cursor_visible = True
        self.last_cursor_toggle = time.time()
        self.cursor_pos = len(initial_text)

    def update(self, dt: float = 0.016) -> None:
        """Updates internal cursor blink animation timer."""
        if time.time() - self.last_cursor_toggle > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = time.time()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_active = True
                self.cursor_pos = len(self.text)
                return True
            else:
                self.is_active = False

        if self.is_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                return True
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                return True
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
                return True
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
                return True
            elif event.key == pygame.K_RETURN:
                if self.is_multiline:
                    self.text = self.text[:self.cursor_pos] + "\n" + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
                else:
                    self.is_active = False
                return True
            elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                # Clipboard paste
                try:
                    if hasattr(pygame, "scrap") and pygame.scrap.get_init():
                        clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                        if clip:
                            clip_text = clip.decode('utf-8').rstrip('\x00')
                            self.text = self.text[:self.cursor_pos] + clip_text + self.text[self.cursor_pos:]
                            self.cursor_pos += len(clip_text)
                except Exception:
                    pass
                return True
            else:
                # Add typed character
                if event.unicode and (event.unicode.isprintable() or event.unicode == ' '):
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
                    return True
        return False

    def get_text(self) -> str:
        return self.text

    def set_text(self, text: str) -> None:
        self.text = text
        self.cursor_pos = len(text)

    def draw(self, surface: pygame.Surface) -> None:
        # Toggle cursor blink every 500ms
        if time.time() - self.last_cursor_toggle > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = time.time()

        # Background & Border
        bg_color = (38, 28, 22) if self.is_active else (28, 20, 16)
        border_color = (255, 215, 65) if self.is_active else (140, 100, 60)

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, border_color, self.rect, width=2 if self.is_active else 1, border_radius=self.border_radius)

        pad_x = 12
        pad_y = 10

        if not self.text and not self.is_active:
            # Draw placeholder text in soft readable silver-cream
            ph_surf = self.font.render(self.placeholder, True, (175, 160, 145))
            surface.blit(ph_surf, (self.rect.x + pad_x, self.rect.y + pad_y))
            return

        # Render text (handle multiline wrapping)
        lines = self.text.split("\n")
        max_width = self.rect.width - (pad_x * 2)

        draw_y = self.rect.y + pad_y
        cursor_drawn = False

        for line_idx, line in enumerate(lines):
            # Wrap long single lines
            words = line.split(" ")
            current_line = ""
            for word in words:
                test = current_line + (" " if current_line else "") + word
                if self.font.size(test)[0] > max_width and current_line:
                    # Draw current wrapped line in pure crisp white
                    line_surf = self.font.render(current_line, True, WHITE)
                    surface.blit(line_surf, (self.rect.x + pad_x, draw_y))
                    draw_y += self.font.get_linesize()
                    current_line = word
                else:
                    current_line = test

            # Draw the remaining text for this line in pure crisp white
            line_surf = self.font.render(current_line, True, WHITE)
            surface.blit(line_surf, (self.rect.x + pad_x, draw_y))

            # Cursor at the end of active line if focused
            if self.is_active and self.cursor_visible and not cursor_drawn and line_idx == len(lines) - 1:
                cur_x = self.rect.x + pad_x + line_surf.get_width() + 2
                pygame.draw.line(surface, (255, 215, 65), (cur_x, draw_y + 2), (cur_x, draw_y + self.font.get_height() - 2), 2)
                cursor_drawn = True

            draw_y += self.font.get_linesize()
            if draw_y > self.rect.bottom - pad_y:
                break

        if self.is_active and self.cursor_visible and not cursor_drawn:
            pygame.draw.line(
                surface, DARK_BROWN,
                (self.rect.x + pad_x, self.rect.y + pad_y + 2),
                (self.rect.x + pad_x, self.rect.y + pad_y + self.font.get_height() - 2),
                2
            )
