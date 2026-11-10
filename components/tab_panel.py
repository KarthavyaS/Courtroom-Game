"""Reusable Tab Panel Component for LOGIC COURTROOM.
Used for clean category switching in Case Selection, Suspect Dossiers, Notebook, and Settings.
"""

import pygame
from typing import List, Tuple, Callable
from config import CARD_BG, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT, get_font
from components.animated_button import AnimatedButton

class TabPanel:
    """Renders a series of horizontal tab buttons and tracks the active selection."""

    def __init__(
        self,
        x: int,
        y: int,
        tab_items: List[Tuple[str, str]],  # List of (tab_id, tab_label)
        active_id: str,
        on_tab_changed: Callable[[str], None],
        tab_width: int = 110,
        tab_height: int = 32,
        font_size: int = 11
    ):
        self.x = x
        self.y = y
        self.tab_items = tab_items
        self.active_id = active_id
        self.on_tab_changed = on_tab_changed
        self.tab_width = tab_width
        self.tab_height = tab_height
        self.font_size = font_size
        self.buttons: List[AnimatedButton] = []
        self._build_tabs()

    def _build_tabs(self) -> None:
        self.buttons.clear()
        curr_x = self.x
        for tab_id, label in self.tab_items:
            is_active = (tab_id == self.active_id)
            bg = (145, 90, 35) if is_active else (42, 34, 30)
            bdr = (255, 215, 0) if is_active else (110, 85, 65)
            txt_col = (255, 255, 255) if is_active else (235, 220, 205)

            # Create closure for each tab button
            def make_click(tid=tab_id):
                def on_click():
                    self.set_active(tid)
                return on_click

            btn = AnimatedButton(
                curr_x, self.y, self.tab_width, self.tab_height, label,
                font_size=self.font_size,
                bg_color=bg,
                border_color=bdr,
                text_color=txt_col,
                on_click=make_click()
            )
            btn.is_selected = is_active
            self.buttons.append(btn)
            curr_x += self.tab_width + 4

    def set_active(self, tab_id: str) -> None:
        if self.active_id != tab_id:
            self.active_id = tab_id
            self._build_tabs()
            if self.on_tab_changed:
                self.on_tab_changed(tab_id)

    def handle_events(self, events) -> None:
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event)

    def update(self, dt: float = 0.016) -> None:
        for btn in self.buttons:
            btn.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        for btn in self.buttons:
            btn.draw(surface)
