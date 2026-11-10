"""Personal Investigation Notebook Screen for LOGIC COURTROOM.
Serves as the player's personal detective binder:
- Tab 1: Case Overview & Timeline
- Tab 2: Suspect Dossiers & Contradictions
- Tab 3: Discovered & Collected Evidence Log
- Tab 4: Player Scratchpad Notes (editable with auto-save)
"""

import pygame
from typing import Callable, Optional, List
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, get_font
)
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.navigation_bar import NavigationBar
from components.tab_panel import TabPanel
from components.text_box import TextBox

class InvestigationNotebook:
    """Personal detective notebook with editable notes and case reference logs."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        on_nav_dashboard: Callable[[], None],
        on_nav_briefing: Callable[[], None],
        on_nav_scene: Callable[[], None],
        on_nav_suspects: Callable[[], None],
        on_nav_evidence: Callable[[], None],
        on_nav_board: Callable[[], None],
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
        self.on_nav_evidence = on_nav_evidence
        self.on_nav_board = on_nav_board
        self.on_nav_arguments = on_nav_arguments
        self.on_nav_courtroom = on_nav_courtroom
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service()

        self.anim_tick = 0
        self.active_tab = "OVERVIEW"

        # Top Navigation Bar
        self.nav_bar = NavigationBar(
            current_stage="notebook",
            game_state=self.game_state,
            on_nav_dashboard=self.on_nav_dashboard,
            on_nav_briefing=self.on_nav_briefing,
            on_nav_scene=self.on_nav_scene,
            on_nav_suspects=self.on_nav_suspects,
            on_nav_evidence=self.on_nav_evidence,
            on_nav_board=self.on_nav_board,
            on_nav_notebook=None,
            on_nav_arguments=self.on_nav_arguments,
            on_nav_courtroom=self.on_nav_courtroom
        )

        # Tab Panel for Notebook Sections
        notebook_tabs = [
            ("OVERVIEW", "CASE DOSSIER"),
            ("SUSPECTS", "SUSPECTS & ALIBIS"),
            ("EVIDENCE", "EVIDENCE LOG"),
            ("NOTES", "MY NOTES ✍")
        ]
        self.tab_panel = TabPanel(
            x=45, y=68, tab_items=notebook_tabs, active_id="OVERVIEW",
            on_tab_changed=self._on_tab_changed,
            tab_width=165, tab_height=34, font_size=10
        )

        # Action Button to next stage
        self.btn_proceed = AnimatedButton(
            SCREEN_WIDTH - 245, 68, 200, 34,
            "PREPARE ARGUMENTS ➔", font_size=10, bg_color=(135, 65, 35),
            border_color=(255, 200, 80), on_click=self.on_nav_arguments
        )

        # Player Notes TextBox
        self.notes_box = TextBox(
            75, 175, SCREEN_WIDTH - 150, 390,
            initial_text=self.game_state.progress.player_notes,
            placeholder="Type your personal observations, theories, and notes here (auto-saved)...",
            is_multiline=True
        )

        # Save Notes Button
        self.btn_save_notes = AnimatedButton(
            SCREEN_WIDTH - 240, 580, 165, 38,
            "SAVE NOTES 💾", font_size=11, bg_color=ACCENT_GREEN,
            on_click=self._save_notes
        )

    def _on_tab_changed(self, tab_id: str) -> None:
        self.active_tab = tab_id
        self.sound_service.play("click")

    def _save_notes(self) -> None:
        self.game_state.progress.player_notes = self.notes_box.text
        self.save_service.save_active_game(self.game_state)
        self.sound_service.play("typewriter")
        self.game_state.set_notification("Detective notes saved successfully!", category="SUCCESS")

    def handle_events(self, events) -> None:
        self.nav_bar.handle_events(events)
        for event in events:
            self.tab_panel.handle_events([event])
            self.btn_proceed.handle_event(event)
            if self.active_tab == "NOTES":
                self.notes_box.handle_event(event)
                self.btn_save_notes.handle_event(event)

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.nav_bar.update(dt)
        self.tab_panel.update(dt)
        self.btn_proceed.update(dt)
        if self.active_tab == "NOTES":
            self.notes_box.update(dt)
            self.btn_save_notes.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Navigation Bar
        self.nav_bar.draw(self.screen)

        # Notebook tabs & proceed button
        self.tab_panel.draw(self.screen)
        self.btn_proceed.draw(self.screen)

        case = self.game_state.current_case
        if not case:
            return

        # Main Binder Surface
        binder_rect = pygame.Rect(45, 115, SCREEN_WIDTH - 90, 535)
        pygame.draw.rect(self.screen, CARD_BG, binder_rect, border_radius=10)
        pygame.draw.rect(self.screen, GOLD_LIGHT, binder_rect, 1, border_radius=10)

        cx = binder_rect.x + 30
        cy = binder_rect.y + 24
        cw = binder_rect.width - 60

        if self.active_tab == "OVERVIEW":
            self.screen.blit(get_font(14, bold=True).render(f"CASE OVERVIEW: {case.title.upper()} ({case.id})", True, GOLD), (cx, cy))
            self.screen.blit(get_font(11).render(f"Category: {case.type} • Crime Location: {case.scene_name}", True, LIGHT_PARCHMENT), (cx, cy + 26))

            # Narrative box
            box = pygame.Rect(cx, cy + 55, cw, 140)
            pygame.draw.rect(self.screen, (35, 28, 24), box, border_radius=6)
            self._render_wrapped_text(case.description, cx + 16, cy + 70, cw - 32, get_font(11), WHITE)

            # Target Objective
            obj_box = pygame.Rect(cx, cy + 215, cw, 100)
            pygame.draw.rect(self.screen, (35, 45, 35), obj_box, border_radius=6)
            pygame.draw.rect(self.screen, ACCENT_GREEN, obj_box, 1, border_radius=6)
            self.screen.blit(get_font(11, bold=True).render("LEGAL PROPOSITION TARGET:", True, ACCENT_GREEN), (obj_box.x + 16, obj_box.y + 12))
            self.screen.blit(get_font(12, bold=True).render(f"'{case.solution_conclusion}'", True, WHITE), (obj_box.x + 16, obj_box.y + 36))
            self.screen.blit(get_font(10).render("Must be proven before the AI Judge using forward inference rules.", True, LIGHT_PARCHMENT), (obj_box.x + 16, obj_box.y + 64))

        elif self.active_tab == "SUSPECTS":
            self.screen.blit(get_font(14, bold=True).render("PERSONS OF INTEREST & RECORDED STATEMENTS", True, GOLD), (cx, cy))
            sy = cy + 35
            for s in case.suspects:
                s_box = pygame.Rect(cx, sy, cw, 88)
                pygame.draw.rect(self.screen, (35, 28, 24), s_box, border_radius=6)
                pygame.draw.rect(self.screen, (75, 60, 50), s_box, 1, border_radius=6)

                self.screen.blit(get_font(11, bold=True).render(f"{s.name} ({s.occupation})", True, GOLD), (s_box.x + 14, s_box.y + 10))
                self.screen.blit(get_font(10).render(f"Alibi: {s.alibi}", True, WHITE), (s_box.x + 14, s_box.y + 32))
                self.screen.blit(get_font(10).render(f"Statement: \"{s.statement[:85]}...\"", True, LIGHT_PARCHMENT), (s_box.x + 14, s_box.y + 52))
                sy += 98

        elif self.active_tab == "EVIDENCE":
            self.screen.blit(get_font(14, bold=True).render(f"FORENSIC LOG ({len(self.game_state.collected_evidence_ids)} Collected)", True, GOLD), (cx, cy))
            ey = cy + 35
            for ev in case.evidence_list:
                is_coll = self.game_state.is_evidence_collected(ev.id)
                e_box = pygame.Rect(cx, ey, cw, 68)
                pygame.draw.rect(self.screen, (32, 42, 32) if is_coll else (35, 28, 24), e_box, border_radius=6)
                bdr = ACCENT_GREEN if is_coll else (75, 60, 50)
                pygame.draw.rect(self.screen, bdr, e_box, 1, border_radius=6)

                stat_txt = "[COLLECTED]" if is_coll else "[NOT COLLECTED]"
                self.screen.blit(get_font(11, bold=True).render(f"{ev.name} — {stat_txt}", True, GOLD if is_coll else MUTED_TEXT), (e_box.x + 14, e_box.y + 10))
                self.screen.blit(get_font(10).render(f"Category: {ev.category} • Reliability: {int(ev.reliability*100)}% • Unlocks: {', '.join(ev.facts_unlocked)}", True, LIGHT_PARCHMENT), (e_box.x + 14, e_box.y + 34))
                ey += 78

        elif self.active_tab == "NOTES":
            self.screen.blit(get_font(14, bold=True).render("PERSONAL INVESTIGATION SCRATCHPAD", True, GOLD), (cx, cy))
            self.screen.blit(get_font(10).render("Record your theories, suspect motives, and trial strategies here. Auto-saved across sessions.", True, LIGHT_PARCHMENT), (cx, cy + 24))

            self.notes_box.draw(self.screen)
            self.btn_save_notes.draw(self.screen)

    def _render_wrapped_text(self, text: str, x: int, y: int, max_w: int, font: pygame.font.Font, color: tuple) -> None:
        words = text.split(" ")
        lines = []
        cur = []
        for w in words:
            if font.size(" ".join(cur + [w]))[0] > max_w:
                lines.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(" ".join(cur))

        for l in lines:
            self.screen.blit(font.render(l, True, color), (x, y))
            y += 20
