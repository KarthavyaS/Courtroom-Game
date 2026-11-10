"""Interactive Case Board Screen for LOGIC COURTROOM.
Visualizes case connections, suspect ties, forensic links, and physical contradictions
using an interactive detective corkboard layout with colored yarn links.
"""

import pygame
import math
from typing import Callable, Optional, List, Dict, Tuple
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

class CaseBoardNode:
    """Represents a pin card on the case board."""
    def __init__(self, node_id: str, title: str, category: str, x: int, y: int, width: int = 150, height: int = 70):
        self.node_id = node_id
        self.title = title
        self.category = category  # 'suspect', 'evidence', 'contradiction', 'timeline'
        self.rect = pygame.Rect(x, y, width, height)

class CaseBoard:
    """Interactive corkboard visualizer for case deductions and timeline analysis."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        on_nav_dashboard: Callable[[], None],
        on_nav_briefing: Callable[[], None],
        on_nav_scene: Callable[[], None],
        on_nav_suspects: Callable[[], None],
        on_nav_evidence: Callable[[], None],
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
        self.on_nav_evidence = on_nav_evidence
        self.on_nav_notebook = on_nav_notebook
        self.on_nav_arguments = on_nav_arguments
        self.on_nav_courtroom = on_nav_courtroom
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service()

        self.anim_tick = 0
        self.selected_node_id: Optional[str] = None
        self.filter_mode = "ALL"  # 'ALL', 'CONFIRMED', 'CONTRADICTIONS'

        # Timeline Scrubber state
        self.time_slots = [
            {"time": "09:30 PM", "label": "Arrival", "desc": "Victim Lord Blackwood was seen entering study. Household retired."},
            {"time": "10:15 PM", "label": "Dinner Alibi", "desc": "Suspects claim dinner concluded. Servants cleared dining room."},
            {"time": "11:00 PM", "label": "★ CRIME WINDOW", "desc": "Loud struggle heard. Security alarms bypassed via Master Cipher."},
            {"time": "11:20 PM", "label": "Escape / CCTV", "desc": "Dark sedan filmed departing north gate without headlights."},
            {"time": "12:00 AM", "label": "Discovery", "desc": "Butler discovered open safe and alerted Scotland Yard."}
        ]
        self.selected_time_idx = 2  # Default to Crime Window

        # Record case board viewed
        self.game_state.progress.record_case_board_opened()
        self.save_service.save_active_game(self.game_state)

        # Top Navigation Bar
        self.nav_bar = NavigationBar(
            current_stage="case_board",
            game_state=self.game_state,
            on_nav_dashboard=self.on_nav_dashboard,
            on_nav_briefing=self.on_nav_briefing,
            on_nav_scene=self.on_nav_scene,
            on_nav_suspects=self.on_nav_suspects,
            on_nav_evidence=self.on_nav_evidence,
            on_nav_board=None,
            on_nav_notebook=self.on_nav_notebook,
            on_nav_arguments=self.on_nav_arguments,
            on_nav_courtroom=self.on_nav_courtroom
        )

        # Filter buttons
        self.btn_filter_all = AnimatedButton(50, 70, 95, 30, "ALL LINKS", font_size=10, bg_color=(130, 85, 45), on_click=lambda: self._set_filter("ALL"))
        self.btn_filter_conf = AnimatedButton(155, 70, 130, 30, "CONFIRMED LINKS", font_size=10, bg_color=(45, 65, 45), on_click=lambda: self._set_filter("CONFIRMED"))
        self.btn_filter_cont = AnimatedButton(295, 70, 155, 30, "CONTRADICTIONS ⚡", font_size=10, bg_color=(75, 35, 35), on_click=lambda: self._set_filter("CONTRADICTIONS"))

        # Proceed to Arguments button
        self.btn_proceed = AnimatedButton(
            SCREEN_WIDTH - 240, 68, 200, 34,
            "PREPARE ARGUMENTS ➔", font_size=11, bg_color=(130, 60, 40),
            on_click=self.on_nav_arguments
        )

        # Board Nodes & Links
        self.nodes: List[CaseBoardNode] = []
        self.links: List[Dict[str, Any]] = []
        self._build_board()

    def _set_filter(self, mode: str) -> None:
        self.filter_mode = mode
        self.sound_service.play("click")

    def _build_board(self) -> None:
        self.nodes.clear()
        self.links.clear()
        case = self.game_state.current_case
        if not case:
            return

        # Position Suspects on Left
        sy = 135
        for s in case.suspects:
            self.nodes.append(CaseBoardNode(s.id, s.name, "suspect", 60, sy, 160, 58))
            sy += 75

        # Position Evidence in Center/Right
        ey = 135
        for i, ev in enumerate(case.evidence_list):
            col = i % 2
            row = i // 2
            self.nodes.append(CaseBoardNode(ev.id, ev.name, "evidence", 260 + col * 170, 135 + row * 75, 155, 58))

        # Position Contradictions and Target Claim on Far Right
        self.nodes.append(CaseBoardNode("CLAIM_OBJ", f"CLAIM: {case.solution_conclusion[:20]}...", "claim", 640, 135, 230, 60))

        if case.id == "CASE001":
            self.nodes.append(CaseBoardNode("CONTRA_1", "CCTV vs Cinema Alibi", "contradiction", 640, 215, 230, 58))
            self.nodes.append(CaseBoardNode("WEAPON_LINK", "Latent Prints on Knife", "confirmed", 640, 295, 230, 58))

            # Links
            self.links.append({"from": "SUS-001", "to": "CONTRA_1", "type": "contradiction"})
            self.links.append({"from": "EVD-006", "to": "CONTRA_1", "type": "confirmed"})
            self.links.append({"from": "SUS-001", "to": "EVD-002", "type": "confirmed"})
            self.links.append({"from": "EVD-002", "to": "WEAPON_LINK", "type": "confirmed"})
            self.links.append({"from": "WEAPON_LINK", "to": "CLAIM_OBJ", "type": "confirmed"})
            self.links.append({"from": "CONTRA_1", "to": "CLAIM_OBJ", "type": "confirmed"})
        else:
            # Generic links for other cases
            if case.suspects and case.evidence_list:
                s0 = case.suspects[0].id
                e0 = case.evidence_list[0].id
                self.links.append({"from": s0, "to": e0, "type": "confirmed"})
                self.links.append({"from": e0, "to": "CLAIM_OBJ", "type": "confirmed"})

    def handle_events(self, events) -> None:
        self.nav_bar.handle_events(events)
        for event in events:
            self.btn_filter_all.handle_event(event)
            self.btn_filter_conf.handle_event(event)
            self.btn_filter_cont.handle_event(event)
            self.btn_proceed.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check corkboard nodes
                for node in self.nodes:
                    if node.rect.collidepoint(event.pos):
                        self.selected_node_id = node.node_id
                        self.sound_service.play("click")
                        break

                # Check timeline slots
                timeline_y = 570
                slot_w = (SCREEN_WIDTH - 120) // len(self.time_slots)
                for i in range(len(self.time_slots)):
                    slot_rect = pygame.Rect(60 + i * slot_w, timeline_y, slot_w - 10, 60)
                    if slot_rect.collidepoint(event.pos):
                        self.selected_time_idx = i
                        self.sound_service.play("click")
                        break

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.nav_bar.update(dt)
        self.btn_filter_all.update(dt)
        self.btn_filter_conf.update(dt)
        self.btn_filter_cont.update(dt)
        self.btn_proceed.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Top Navigation
        self.nav_bar.draw(self.screen)

        # Filter Chips & Proceed button
        self.btn_filter_all.draw(self.screen)
        self.btn_filter_conf.draw(self.screen)
        self.btn_filter_cont.draw(self.screen)
        self.btn_proceed.draw(self.screen)

        # Corkboard Canvas Area
        board_rect = pygame.Rect(40, 115, 850, 420)
        pygame.draw.rect(self.screen, (42, 32, 25), board_rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 60, 45), board_rect, 3, border_radius=10)

        # Right Inspector Panel
        insp_rect = pygame.Rect(900, 115, 160, 420)
        pygame.draw.rect(self.screen, CARD_BG, insp_rect, border_radius=8)
        pygame.draw.rect(self.screen, GOLD_LIGHT, insp_rect, 1, border_radius=8)
        self.screen.blit(get_font(11, bold=True).render("NODE DETAILS", True, GOLD), (insp_rect.x + 10, insp_rect.y + 12))

        if self.selected_node_id:
            sel_node = next((n for n in self.nodes if n.node_id == self.selected_node_id), None)
            if sel_node:
                self.screen.blit(get_font(10, bold=True).render(sel_node.title[:18], True, WHITE), (insp_rect.x + 10, insp_rect.y + 36))
                self.screen.blit(get_font(9).render(f"Type: {sel_node.category.upper()}", True, GOLD), (insp_rect.x + 10, insp_rect.y + 56))
                self.screen.blit(get_font(9).render("Status: Active Pin", True, LIGHT_PARCHMENT), (insp_rect.x + 10, insp_rect.y + 76))
                desc = "Connected across deduction paths."
                if sel_node.category == "contradiction":
                    desc = "Direct conflict between witness statement and physical evidence."
                words = desc.split(" ")
                lines, cur = [], []
                for w in words:
                    if get_font(8).size(" ".join(cur + [w]))[0] > 140:
                        lines.append(" ".join(cur))
                        cur = [w]
                    else:
                        cur.append(w)
                if cur:
                    lines.append(" ".join(cur))
                dy = insp_rect.y + 105
                for l in lines:
                    self.screen.blit(get_font(8).render(l, True, LIGHT_PARCHMENT), (insp_rect.x + 10, dy))
                    dy += 14
        else:
            self.screen.blit(get_font(9).render("Click any pin on\nthe board to inspect\nconnections.", True, MUTED_TEXT), (insp_rect.x + 10, insp_rect.y + 40))

        # Render Connecting Lines (Yarn Threads)
        node_map = {n.node_id: n for n in self.nodes}
        pulse = (math.sin(self.anim_tick * 0.06) + 1.0) * 0.5

        for link in self.links:
            l_type = link["type"]
            if self.filter_mode == "CONFIRMED" and l_type != "confirmed":
                continue
            if self.filter_mode == "CONTRADICTIONS" and l_type != "contradiction":
                continue

            n_from = node_map.get(link["from"])
            n_to = node_map.get(link["to"])
            if n_from and n_to:
                p1 = n_from.rect.center
                p2 = n_to.rect.center

                if l_type == "contradiction":
                    line_col = ACCENT_RED
                    line_w = 3
                else:
                    line_col = (int(190 + 50 * pulse), int(150 + 40 * pulse), 50)
                    line_w = 2

                pygame.draw.line(self.screen, line_col, p1, p2, line_w)

        # Render Cards (Pins)
        for node in self.nodes:
            is_sel = (node.node_id == self.selected_node_id)
            bg_col = (50, 40, 32) if not is_sel else (65, 52, 40)
            pygame.draw.rect(self.screen, bg_col, node.rect, border_radius=6)

            # Border color by category
            if node.category == "contradiction":
                bdr_col = ACCENT_RED
            elif node.category == "claim":
                bdr_col = ACCENT_GREEN
            elif node.category == "suspect":
                bdr_col = GOLD
            else:
                bdr_col = GOLD_LIGHT if is_sel else (100, 80, 65)

            pygame.draw.rect(self.screen, bdr_col, node.rect, 2 if is_sel else 1, border_radius=6)

            # Pin icon on top of card
            pin_col = ACCENT_RED if node.category == "contradiction" else GOLD
            pygame.draw.circle(self.screen, pin_col, (node.rect.centerx, node.rect.y + 4), 4)

            # Text
            t_font = get_font(10, bold=True)
            self.screen.blit(t_font.render(node.title[:22], True, WHITE), (node.rect.x + 8, node.rect.y + 12))

            cat_font = get_font(9)
            cat_txt = f"[{node.category.upper()}]"
            self.screen.blit(cat_font.render(cat_txt, True, LIGHT_PARCHMENT), (node.rect.x + 8, node.rect.y + 32))

        # Bottom 24-Hour Timeline Scrubber Area
        t_bar_rect = pygame.Rect(40, 545, SCREEN_WIDTH - 80, 95)
        pygame.draw.rect(self.screen, (28, 22, 18), t_bar_rect, border_radius=8)
        pygame.draw.rect(self.screen, (65, 50, 40), t_bar_rect, 1, border_radius=8)

        self.screen.blit(get_font(10, bold=True).render("⏱ 24-HOUR FORENSIC TIMELINE SCRUBBER (CLICK TO JUMP):", True, GOLD), (t_bar_rect.x + 15, t_bar_rect.y + 6))

        slot_w = (t_bar_rect.width - 30) // len(self.time_slots)
        for i, slot in enumerate(self.time_slots):
            is_cur = (i == self.selected_time_idx)
            slot_rect = pygame.Rect(t_bar_rect.x + 15 + i * slot_w, t_bar_rect.y + 26, slot_w - 8, 60)
            s_bg = (55, 42, 32) if is_cur else (38, 30, 25)
            s_bdr = GOLD if is_cur else (60, 48, 40)

            pygame.draw.rect(self.screen, s_bg, slot_rect, border_radius=5)
            pygame.draw.rect(self.screen, s_bdr, slot_rect, 2 if is_cur else 1, border_radius=5)

            # Time header
            t_col = GOLD if is_cur else LIGHT_PARCHMENT
            self.screen.blit(get_font(10, bold=True).render(slot["time"], True, t_col), (slot_rect.x + 6, slot_rect.y + 4))
            self.screen.blit(get_font(8, bold=True).render(slot["label"], True, ACCENT_RED if "CRIME" in slot["label"] else WHITE), (slot_rect.x + 6, slot_rect.y + 18))

            # Description snippet
            desc_snip = slot["desc"][:26] + "..." if len(slot["desc"]) > 26 else slot["desc"]
            self.screen.blit(get_font(7).render(desc_snip, True, LIGHT_PARCHMENT), (slot_rect.x + 6, slot_rect.y + 36))
