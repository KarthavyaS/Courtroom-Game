"""Evidence Review Dashboard Screen for LOGIC COURTROOM.
Displays collected artifacts, category classification, reliability vs relevance analysis,
and unlocked logical propositions with unified NavigationBar.
"""
#pyright: ignore
import pygame
from typing import Callable, Optional, List
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, get_font
)
from models.evidence import Evidence
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.navigation_bar import NavigationBar
from components.illustrations import draw_evidence_icon

class EvidenceView:
    """Evidence review dashboard with forensic filtering and reliability analysis."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        on_nav_dashboard: Callable[[], None],
        on_nav_briefing: Callable[[], None],
        on_nav_scene: Callable[[], None],
        on_nav_suspects: Callable[[], None],
        on_nav_board: Callable[[], None],
        on_nav_notebook: Callable[[], None],
        on_nav_arguments: Callable[[], None],
        on_nav_courtroom: Callable[[], None],
        save_service: Optional[SaveService] = None
    ):
        self.screen = screen
        self.game_state = game_state
        self.on_nav_dashboard = on_nav_dashboard
        self.on_nav_briefing = on_nav_briefing
        self.on_nav_scene = on_nav_scene
        self.on_nav_suspects = on_nav_suspects
        self.on_nav_board = on_nav_board
        self.on_nav_notebook = on_nav_notebook
        self.on_nav_arguments = on_nav_arguments
        self.on_nav_courtroom = on_nav_courtroom
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service()

        self.selected_category = "ALL"
        self.selected_evidence: Optional[Evidence] = None

        # Top Navigation Bar
        self.nav_bar = NavigationBar(
            current_stage="evidence",
            game_state=self.game_state,
            on_nav_dashboard=self.on_nav_dashboard,
            on_nav_briefing=self.on_nav_briefing,
            on_nav_scene=self.on_nav_scene,
            on_nav_suspects=self.on_nav_suspects,
            on_nav_evidence=None,
            on_nav_board=self.on_nav_board,
            on_nav_notebook=self.on_nav_notebook,
            on_nav_arguments=self.on_nav_arguments,
            on_nav_courtroom=self.on_nav_courtroom
        )

        # Category Filter Tabs
        self.filter_buttons: List[AnimatedButton] = []
        self._init_filter_buttons()

    def _init_filter_buttons(self) -> None:
        self.filter_buttons.clear()
        categories = ["ALL", "PHYSICAL", "DIGITAL", "DIRECT", "TESTIMONIAL", "CIRCUMSTANTIAL"]
        start_x = 25
        for i, cat in enumerate(categories):
            def make_handler(c=cat):
                def handler():
                    self._set_filter(c)
                return handler

            is_cur = (cat == self.selected_category)
            btn = AnimatedButton(
                start_x + (i * 118), 64, 112, 28, cat,
                font_size=10,
                bg_color=(145, 95, 55) if is_cur else WOOD_BROWN,
                on_click=make_handler()
            )
            self.filter_buttons.append(btn)

    def _set_filter(self, cat: str) -> None:
        self.selected_category = cat
        self.sound_service.play("click")
        self._init_filter_buttons()

    def _get_filtered_evidence(self) -> List[Evidence]:
        if not self.game_state.current_case:
            return []
        all_ev = self.game_state.current_case.evidence_list
        if self.selected_category == "ALL":
            return all_ev
        return [e for e in all_ev if e.category.upper() == self.selected_category]

    def handle_events(self, events) -> None:
        self.nav_bar.handle_events(events)
        for event in events:
            for btn in self.filter_buttons:
                btn.handle_event(event)

            # Check clicking evidence cards in grid
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_state.current_case:
                    filtered = self._get_filtered_evidence()
                    for i, ev in enumerate(filtered):
                        col = i % 3
                        row = i // 3
                        card_rect = pygame.Rect(25 + col * 235, 102 + row * 270, 225, 260)
                        if card_rect.collidepoint(event.pos):
                            self.selected_evidence = ev
                            self.sound_service.play("click")
                            break

    def update(self, dt: float = 0.016) -> None:
        self.nav_bar.update(dt)
        for btn in self.filter_buttons:
            btn.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Navigation Bar
        self.nav_bar.draw(self.screen)

        # Filters
        for btn in self.filter_buttons:
            btn.draw(self.screen)

        # Evidence Cards Grid (Left 730px)
        filtered = self._get_filtered_evidence()
        for i, ev in enumerate(filtered[:6]):
            col = i % 3
            row = i // 3
            card_rect = pygame.Rect(25 + col * 235, 102 + row * 270, 225, 260)
            is_collected = self.game_state.is_evidence_collected(ev.id)
            is_selected = (self.selected_evidence and self.selected_evidence.id == ev.id)

            bg_col = (45, 35, 28) if is_selected else CARD_BG
            pygame.draw.rect(self.screen, bg_col, card_rect, border_radius=8)
            bdr_col = GOLD if is_selected else (GOLD_LIGHT if is_collected else (70, 55, 45))
            pygame.draw.rect(self.screen, bdr_col, card_rect, 2 if is_selected else 1, border_radius=8)

            # Icon Box
            icon_rect = pygame.Rect(card_rect.x + 10, card_rect.y + 10, card_rect.width - 20, 90)
            pygame.draw.rect(self.screen, (30, 22, 18), icon_rect, border_radius=6)
            draw_evidence_icon(self.screen, ev.icon_type, icon_rect.x + 40, icon_rect.y + 10, icon_rect.width - 80, 70)

            # Details
            self.screen.blit(get_font(11, bold=True).render(ev.name[:24], True, GOLD if is_collected else WHITE), (card_rect.x + 10, card_rect.y + 110))
            self.screen.blit(get_font(9).render(f"Category: {ev.category}", True, LIGHT_PARCHMENT), (card_rect.x + 10, card_rect.y + 130))

            # Status Badge
            stat_col = ACCENT_GREEN if is_collected else (120, 80, 40)
            stat_txt = "COLLECTED ✓" if is_collected else "UNCOLLECTED"
            stat_rect = pygame.Rect(card_rect.x + 10, card_rect.y + 155, 100, 20)
            pygame.draw.rect(self.screen, stat_col, stat_rect, border_radius=4)
            self.screen.blit(get_font(8, bold=True).render(stat_txt, True, WHITE), (stat_rect.x + 6, stat_rect.y + 4))

        # Right Detail Inspection Panel (x=735, w=340)
        p_rect = pygame.Rect(735, 102, 340, 550)
        pygame.draw.rect(self.screen, CARD_BG, p_rect, border_radius=8)
        pygame.draw.rect(self.screen, GOLD_LIGHT, p_rect, 1, border_radius=8)

        if self.selected_evidence:
            ev = self.selected_evidence
            self.screen.blit(get_font(14, bold=True).render(ev.name, True, GOLD), (p_rect.x + 18, p_rect.y + 18))
            self.screen.blit(get_font(11).render(f"Reliability: {int(ev.reliability * 100)}% • Relevance: {int(ev.relevance * 100)}%", True, ACCENT_BLUE), (p_rect.x + 18, p_rect.y + 45))

            desc_y = p_rect.y + 75
            self.screen.blit(get_font(11, bold=True).render("DESCRIPTION:", True, LIGHT_PARCHMENT), (p_rect.x + 18, desc_y))
            desc_y += 20

            words = ev.description.split(" ")
            lines = []
            cur = []
            for w in words:
                if get_font(10).size(" ".join(cur + [w]))[0] > (p_rect.width - 36):
                    lines.append(" ".join(cur))
                    cur = [w]
                else:
                    cur.append(w)
            if cur:
                lines.append(" ".join(cur))

            for l in lines:
                self.screen.blit(get_font(10).render(l, True, WHITE), (p_rect.x + 18, desc_y))
                desc_y += 18

            # Unlocked Facts
            desc_y += 15
            f_box = pygame.Rect(p_rect.x + 14, desc_y, p_rect.width - 28, 160)
            pygame.draw.rect(self.screen, (30, 22, 18), f_box, border_radius=6)
            self.screen.blit(get_font(10, bold=True).render("UNLOCKED PROPOSITIONS:", True, ACCENT_GREEN), (f_box.x + 10, f_box.y + 10))
            fy = f_box.y + 35
            for f in ev.facts_unlocked:
                self.screen.blit(get_font(9).render(f"• {f}", True, (200, 220, 200)), (f_box.x + 10, fy))
                fy += 18
        else:
            self.screen.blit(get_font(12, bold=True).render("SELECT EVIDENCE TO INSPECT", True, GOLD), (p_rect.x + 20, p_rect.y + 25))
            self.screen.blit(get_font(10).render("Click any evidence card to review forensic analysis.", True, LIGHT_PARCHMENT), (p_rect.x + 20, p_rect.y + 55))
