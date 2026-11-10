"""Crime Scene Investigation Screen for LOGIC COURTROOM.
Features an interactive 2D investigation room with clickable forensic artifacts,
subtle glowing highlights, evidence inspector with Inspect vs Collect choices,
evidence discovery/collection counters, and seamless navigation.
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
from models.evidence import Evidence
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.navigation_bar import NavigationBar
from components.illustrations import draw_evidence_icon

class CrimeScene:
    """Interactive 2D crime scene exploration and forensic inspection screen."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        on_nav_dashboard: Callable[[], None],
        on_nav_briefing: Callable[[], None],
        on_nav_suspects: Callable[[], None],
        on_nav_evidence: Callable[[], None],
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
        self.on_nav_suspects = on_nav_suspects
        self.on_nav_evidence = on_nav_evidence
        self.on_nav_board = on_nav_board
        self.on_nav_notebook = on_nav_notebook
        self.on_nav_arguments = on_nav_arguments
        self.on_nav_courtroom = on_nav_courtroom
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service()

        self.selected_evidence: Optional[Evidence] = None
        self.anim_tick = 0
        self.hovered_evidence: Optional[Evidence] = None
        self.active_forensic_tool = "MAGNIFIER"  # 'MAGNIFIER', 'LUMINOL', 'POWDER'

        # Top Navigation Bar
        self.nav_bar = NavigationBar(
            current_stage="crime_scene",
            game_state=self.game_state,
            on_nav_dashboard=self.on_nav_dashboard,
            on_nav_briefing=self.on_nav_briefing,
            on_nav_scene=None,
            on_nav_suspects=self.on_nav_suspects,
            on_nav_evidence=self.on_nav_evidence,
            on_nav_board=self.on_nav_board,
            on_nav_notebook=self.on_nav_notebook,
            on_nav_arguments=self.on_nav_arguments,
            on_nav_courtroom=self.on_nav_courtroom
        )

        # Forensic Tool Switcher Buttons
        self.btn_tool_mag = AnimatedButton(260, 66, 130, 38, "🔍 LENS [1]", font_size=13, bg_color=(120, 85, 45), on_click=lambda: self._select_tool("MAGNIFIER"))
        self.btn_tool_uv = AnimatedButton(400, 66, 150, 38, "💡 UV LIGHT [2]", font_size=13, bg_color=(50, 45, 80), on_click=lambda: self._select_tool("LUMINOL"))
        self.btn_tool_powder = AnimatedButton(560, 66, 160, 38, "🖌 DUST POWDER [3]", font_size=13, bg_color=(60, 65, 75), on_click=lambda: self._select_tool("POWDER"))

        # Inspector Panel Buttons
        self.btn_inspect = AnimatedButton(765, 606, 135, 44, "INSPECT 🔍", font_size=13, bg_color=(60, 75, 95), on_click=self._inspect_selected_evidence)
        self.btn_collect = AnimatedButton(910, 606, 155, 44, "COLLECT CLUE ➔", font_size=13, bg_color=ACCENT_GREEN, on_click=self._collect_selected_evidence)
        self.btn_continue = AnimatedButton(SCREEN_WIDTH - 230, 66, 190, 38, "SUSPECTS ➔", font_size=13, bg_color=(130, 85, 45), on_click=self._handle_continue)

    def _select_tool(self, tool_name: str) -> None:
        self.active_forensic_tool = tool_name
        self.sound_service.play("click")
        if tool_name == "LUMINOL":
            self.game_state.set_notification("UV Luminol Light Active: Latent organic & blood traces now luminesce!", category="INFO")
        elif tool_name == "POWDER":
            self.game_state.set_notification("Fingerprint Dust Powder Active: Ridge patterns highlighted!", category="INFO")
        else:
            self.game_state.set_notification("Forensic Magnifying Lens Active: Standard optical inspection.", category="INFO")

    def _inspect_selected_evidence(self) -> None:
        if self.selected_evidence:
            self.game_state.progress.record_evidence_inspected(self.selected_evidence.id)
            self.sound_service.play("click")
            self.game_state.set_notification(f"Inspected '{self.selected_evidence.name}'.", category="INFO")
            self.save_service.save_active_game(self.game_state)

    def _collect_selected_evidence(self) -> None:
        if self.selected_evidence:
            if not self.game_state.is_evidence_collected(self.selected_evidence.id):
                self.game_state.collect_evidence(self.selected_evidence.id)
                self.sound_service.play("evidence")
                self.game_state.set_notification(f"Evidence Collected: '{self.selected_evidence.name}'!", category="SUCCESS")
                self.save_service.save_active_game(self.game_state)
            else:
                self.game_state.set_notification("Evidence already in your legal inventory.", category="INFO")

    def _handle_continue(self) -> None:
        if len(self.game_state.collected_evidence_ids) == 0:
            self.game_state.set_notification("Tip: You haven't collected any physical evidence yet!", category="WARNING")
        self.sound_service.play("click")
        self.on_nav_suspects()

    def _get_evidence_rect(self, ev: Evidence) -> pygame.Rect:
        x, y, w, h = ev.scene_pos
        # Clamp within viewport (35..740 on X, 120..650 on Y)
        w = max(40, min(180, w))
        h = max(40, min(140, h))
        clamped_x = max(45, min(730 - w, x))
        clamped_y = max(130, min(640 - h, y))
        return pygame.Rect(clamped_x, clamped_y, w, h)

    def handle_events(self, events) -> None:
        self.nav_bar.handle_events(events)
        for event in events:
            self.btn_continue.handle_event(event)
            self.btn_tool_mag.handle_event(event)
            self.btn_tool_uv.handle_event(event)
            self.btn_tool_powder.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self._select_tool("MAGNIFIER")
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self._select_tool("LUMINOL")
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self._select_tool("POWDER")

            if self.selected_evidence:
                self.btn_inspect.handle_event(event)
                self.btn_collect.handle_event(event)

            # Check Hotspot Clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_state.current_case:
                    for ev in self.game_state.current_case.evidence_list:
                        hs_rect = self._get_evidence_rect(ev)
                        if hs_rect.collidepoint(event.pos):
                            self.selected_evidence = ev
                            self.game_state.progress.record_evidence_inspected(ev.id)
                            self.sound_service.play("click")
                            self.save_service.save_active_game(self.game_state)
                            break

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.nav_bar.update(dt)
        self.btn_continue.update(dt)
        self.btn_tool_mag.update(dt)
        self.btn_tool_uv.update(dt)
        self.btn_tool_powder.update(dt)

        # Update button highlights
        self.btn_tool_mag.is_selected = (self.active_forensic_tool == "MAGNIFIER")
        self.btn_tool_uv.is_selected = (self.active_forensic_tool == "LUMINOL")
        self.btn_tool_powder.is_selected = (self.active_forensic_tool == "POWDER")

        if self.selected_evidence:
            self.btn_inspect.update(dt)
            self.btn_collect.update(dt)

        # Check mouse hover on hotspots
        mpos = pygame.mouse.get_pos()
        self.hovered_evidence = None
        if self.game_state.current_case:
            for ev in self.game_state.current_case.evidence_list:
                if self._get_evidence_rect(ev).collidepoint(mpos):
                    self.hovered_evidence = ev
                    break

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Navigation Bar
        self.nav_bar.draw(self.screen)

        case = self.game_state.current_case
        if not case:
            return

        # Header Info Strip & Tool Selector
        self.btn_continue.draw(self.screen)
        self.btn_tool_mag.draw(self.screen)
        self.btn_tool_uv.draw(self.screen)
        self.btn_tool_powder.draw(self.screen)

        hdr_font = get_font(12, bold=True)
        self.screen.blit(hdr_font.render(f"LOCATION: {case.scene_name.upper()}", True, GOLD), (40, 72))

        disc_count = len(self.game_state.progress.inspected_evidence_ids)
        coll_count = len(self.game_state.collected_evidence_ids)
        tot_count = len(case.evidence_list)
        stats_txt = f"Inspected: {disc_count}/{tot_count} • Collected: {coll_count}/{tot_count}"
        self.screen.blit(get_font(10).render(stats_txt, True, LIGHT_PARCHMENT), (40, 92))

        # Scene Viewport (Left Area)
        view_rect = pygame.Rect(35, 118, 705, 535)
        pygame.draw.rect(self.screen, (28, 22, 18), view_rect, border_radius=8)
        pygame.draw.rect(self.screen, GOLD_LIGHT, view_rect, 1, border_radius=8)

        # Draw Decorative Room Backdrop Elements (Walls, Desk, Rug, Balcony)
        self._draw_room_environment(view_rect, case.scene_type)

        # UV Luminol Dark Filter Overlay if active
        if self.active_forensic_tool == "LUMINOL":
            uv_overlay = pygame.Surface((view_rect.width, view_rect.height), pygame.SRCALPHA)
            uv_overlay.fill((20, 10, 50, 140))
            self.screen.blit(uv_overlay, (view_rect.x, view_rect.y))

        # Render Evidence Hotspots - Hidden until swept by active tool cursor
        pulse = (math.sin(self.anim_tick * 0.08) + 1.0) * 0.5
        mpos = pygame.mouse.get_pos()
        cursor_in_view = view_rect.collidepoint(mpos)

        for ev in case.evidence_list:
            hs_rect = self._get_evidence_rect(ev)
            is_collected = self.game_state.is_evidence_collected(ev.id)
            is_inspected = ev.id in self.game_state.progress.inspected_evidence_ids
            is_selected = (self.selected_evidence and self.selected_evidence.id == ev.id)

            # Distance from tool cursor to hotspot center
            dist_to_cursor = math.hypot(mpos[0] - hs_rect.centerx, mpos[1] - hs_rect.centery)
            is_swept = cursor_in_view and (dist_to_cursor < 75)

            if is_collected or is_inspected:
                # Discovered Clue - Draw clean marker
                hs_bg = (35, 55, 38, 160) if is_collected else (45, 38, 30, 160)
                bdr_col = ACCENT_GREEN if is_collected else GOLD
                hs_surf = pygame.Surface((hs_rect.width, hs_rect.height), pygame.SRCALPHA)
                hs_surf.fill(hs_bg)
                self.screen.blit(hs_surf, (hs_rect.x, hs_rect.y))
                pygame.draw.rect(self.screen, bdr_col, hs_rect, 2 if is_selected else 1, border_radius=6)
                draw_evidence_icon(self.screen, ev.icon_type, hs_rect.x + 8, hs_rect.y + 8, hs_rect.width - 16, hs_rect.height - 16)

                lbl_txt = f"✓ {ev.name}" if is_collected else f"🔍 {ev.name}"
                lbl_surf = get_font(9, bold=True).render(lbl_txt, True, WHITE)
                lbl_bg = pygame.Rect(hs_rect.x - 2, hs_rect.bottom + 2, lbl_surf.get_width() + 6, 16)
                pygame.draw.rect(self.screen, (20, 15, 12), lbl_bg, border_radius=3)
                self.screen.blit(lbl_surf, (lbl_bg.x + 3, lbl_bg.y + 2))

            elif is_swept:
                # Hidden clue being illuminated under tool!
                if self.active_forensic_tool == "LUMINOL":
                    glow_col = (100, 255, 230)
                    glow_alpha = int(180 + 75 * pulse)
                elif self.active_forensic_tool == "POWDER":
                    glow_col = (210, 230, 255)
                    glow_alpha = int(160 + 80 * pulse)
                else:
                    glow_col = (255, 225, 90)
                    glow_alpha = int(170 + 70 * pulse)

                glow_surf = pygame.Surface((hs_rect.width + 10, hs_rect.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*glow_col, glow_alpha), (0, 0, hs_rect.width + 10, hs_rect.height + 10), 2, border_radius=8)
                self.screen.blit(glow_surf, (hs_rect.x - 5, hs_rect.y - 5))

                # Shimmer particle stars
                for k in range(3):
                    sang = (k / 3.0) * math.pi * 2 + (self.anim_tick * 0.1)
                    sx = hs_rect.centerx + math.cos(sang) * (hs_rect.width // 3)
                    sy = hs_rect.centery + math.sin(sang) * (hs_rect.height // 3)
                    pygame.draw.circle(self.screen, glow_col, (int(sx), int(sy)), 3)

                shimmer_lbl = get_font(9, bold=True).render("★ CLUE DETECTED! [CLICK]", True, glow_col)
                self.screen.blit(shimmer_lbl, (hs_rect.centerx - shimmer_lbl.get_width() // 2, hs_rect.y - 18))
            else:
                # Completely hidden in environment
                pass
        # Draw Forensic Cursor Lens / Beam when hovering viewport
        mpos = pygame.mouse.get_pos()
        if view_rect.collidepoint(mpos):
            mx, my = mpos
            if self.active_forensic_tool == "LUMINOL":
                # Glowing violet/cyan UV spotlight
                spot_surf = pygame.Surface((180, 180), pygame.SRCALPHA)
                pygame.draw.circle(spot_surf, (80, 120, 255, 65), (90, 90), 85)
                pygame.draw.circle(spot_surf, (140, 220, 255, 110), (90, 90), 55)
                pygame.draw.circle(spot_surf, (220, 255, 255, 160), (90, 90), 20)
                self.screen.blit(spot_surf, (mx - 90, my - 90))
                pygame.draw.circle(self.screen, (100, 200, 255), (mx, my), 88, 1)
            elif self.active_forensic_tool == "POWDER":
                # Dusting brush reticle
                pygame.draw.circle(self.screen, (220, 230, 245), (mx, my), 32, 1)
                pygame.draw.circle(self.screen, (180, 190, 210), (mx, my), 12, 1)
                for i in range(4):
                    ang = (i / 4.0) * math.pi * 2 + (self.anim_tick * 0.05)
                    dx = mx + math.cos(ang) * 36
                    dy = my + math.sin(ang) * 36
                    pygame.draw.circle(self.screen, (200, 215, 240), (int(dx), int(dy)), 2)
            else:
                # Magnifying lens glass ring
                pygame.draw.circle(self.screen, GOLD, (mx, my), 48, 2)
                pygame.draw.circle(self.screen, (255, 240, 180), (mx, my), 44, 1)
                pygame.draw.line(self.screen, GOLD_LIGHT, (mx - 15, my), (mx + 15, my), 1)
                pygame.draw.line(self.screen, GOLD_LIGHT, (mx, my - 15), (mx, my + 15), 1)
                pygame.draw.line(self.screen, WOOD_BROWN, (mx + 34, my + 34), (mx + 56, my + 56), 6)

        from components.ui_shapes import draw_chamfered_rect, wrap_text_fully

        # Right Inspector Panel with Chamfered Tech Geometry
        insp_rect = pygame.Rect(755, 118, 310, 535)
        draw_chamfered_rect(self.screen, insp_rect, CARD_BG, GOLD_LIGHT, cut=12, border_width=1, corner_brackets=True, inner_glow=True)

        self._draw_evidence_inspector(insp_rect)

    def _draw_room_environment(self, view_rect: pygame.Rect, scene_type: str) -> None:
        """Draws procedural 2D interior perspective for the scene."""
        # Floor perspective
        floor_y = view_rect.y + int(view_rect.height * 0.6)
        pygame.draw.rect(self.screen, (38, 28, 22), (view_rect.x, floor_y, view_rect.width, view_rect.bottom - floor_y), border_bottom_left_radius=8, border_bottom_right_radius=8)
        pygame.draw.line(self.screen, (60, 45, 35), (view_rect.x, floor_y), (view_rect.right, floor_y), 2)

        # Floor planks
        for px in range(view_rect.x, view_rect.right, 70):
            pygame.draw.line(self.screen, (32, 24, 18), (px, floor_y), (px - 30, view_rect.bottom), 1)

        # Wall paneling
        for wx in range(view_rect.x, view_rect.right, 140):
            pygame.draw.line(self.screen, (40, 32, 26), (wx, view_rect.y), (wx, floor_y), 1)

        # Window / Arch in background
        win_rect = pygame.Rect(view_rect.x + 120, view_rect.y + 40, 150, 160)
        pygame.draw.rect(self.screen, (15, 20, 30), win_rect, border_top_left_radius=75, border_top_right_radius=75)
        pygame.draw.rect(self.screen, (65, 50, 40), win_rect, 3, border_top_left_radius=75, border_top_right_radius=75)
        pygame.draw.line(self.screen, (65, 50, 40), (win_rect.centerx, win_rect.y), (win_rect.centerx, win_rect.bottom), 2)
        pygame.draw.line(self.screen, (65, 50, 40), (win_rect.x, win_rect.y + 80), (win_rect.right, win_rect.y + 80), 2)

    def _draw_evidence_inspector(self, rect: pygame.Rect) -> None:
        """Renders detailed forensic inspector for the selected evidence."""
        from components.ui_shapes import draw_chamfered_rect, wrap_text_fully
        if not self.selected_evidence:
            # Placeholder instructions
            self.screen.blit(get_font(16, bold=True).render("EVIDENCE INSPECTOR", True, GOLD), (rect.x + 20, rect.y + 20))
            self.screen.blit(get_font(13).render("Sweep with Forensic Tools [1, 2, 3]", True, LIGHT_PARCHMENT), (rect.x + 20, rect.y + 54))
            self.screen.blit(get_font(13).render("to detect and unlock hidden clues.", True, LIGHT_PARCHMENT), (rect.x + 20, rect.y + 78))

            # Magnifier Graphic
            self.screen.blit(get_font(52).render("🔬", True, (120, 95, 75)), (rect.centerx - 26, rect.centery - 40))
            return

        ev = self.selected_evidence
        is_collected = self.game_state.is_evidence_collected(ev.id)

        # Header Title
        self.screen.blit(get_font(16, bold=True).render(ev.name, True, GOLD), (rect.x + 16, rect.y + 14))

        # Status badge
        stat_color = ACCENT_GREEN if is_collected else (140, 100, 40)
        stat_txt = "COLLECTED (IN INVENTORY)" if is_collected else "UNCOLLECTED ARTIFACT"
        stat_rect = pygame.Rect(rect.x + 16, rect.y + 42, rect.width - 32, 26)
        draw_chamfered_rect(self.screen, stat_rect, stat_color, GOLD, cut=4, border_width=1)
        self.screen.blit(get_font(12, bold=True).render(stat_txt, True, WHITE), (stat_rect.x + 10, stat_rect.y + 4))

        # Category & Metrics
        my = rect.y + 74
        self.screen.blit(get_font(13, bold=True).render(f"Category: {ev.category.capitalize()} Evidence", True, LIGHT_PARCHMENT), (rect.x + 16, my))
        my += 22
        self.screen.blit(get_font(13, bold=True).render(f"Reliability: {int(ev.reliability * 100)}% • Relevance: {int(ev.relevance * 100)}%", True, ACCENT_BLUE), (rect.x + 16, my))

        # Description
        my += 26
        self.screen.blit(get_font(13, bold=True).render("FIELD OBSERVATION:", True, GOLD_LIGHT), (rect.x + 16, my))
        my += 20
        lines = wrap_text_fully(ev.description, get_font(12), rect.width - 32)
        for l in lines:
            self.screen.blit(get_font(12).render(l, True, WHITE), (rect.x + 16, my))
            my += 18

        # Lab Details / Facts Unlocked
        my += 10
        f_box = pygame.Rect(rect.x + 12, my, rect.width - 24, 155)
        draw_chamfered_rect(self.screen, f_box, (30, 22, 18), (75, 60, 50), cut=8, border_width=1)

        self.screen.blit(get_font(13, bold=True).render("FORENSIC LAB ANALYSIS:", True, GOLD), (f_box.x + 10, f_box.y + 8))
        if ev.details:
            d_lines = wrap_text_fully(ev.details, get_font(12), f_box.width - 20)
            for di, dline in enumerate(d_lines[:2]):
                self.screen.blit(get_font(12).render(dline, True, LIGHT_PARCHMENT), (f_box.x + 10, f_box.y + 28 + di * 18))

        self.screen.blit(get_font(13, bold=True).render("UNLOCKED PROPOSITIONS:", True, ACCENT_GREEN), (f_box.x + 10, f_box.y + 70))
        fy = f_box.y + 92
        for f in ev.facts_unlocked:
            self.screen.blit(get_font(12).render(f"• {f}", True, (210, 235, 210)), (f_box.x + 10, fy))
            fy += 18

        # Buttons
        self.btn_inspect.draw(self.screen)
        self.btn_collect.draw(self.screen)