"""Case Selection and Dossier Preview Screen for LOGIC COURTROOM.
Features category filter tabs, rich Case File cards with difficulty/suspect/evidence metrics,
and a comprehensive Case Preview Modal before entering the investigation.
"""
#pyright: ignore
import pygame
import math
from typing import Callable, List, Optional
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, get_font
)
from models.case import Case
from services.case_service import CaseService
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.tab_panel import TabPanel

class CaseSelection:
    """Case browser with categorization and detailed preview modal."""

    def __init__(
        self,
        screen: pygame.Surface,
        case_service: CaseService,
        on_back: Callable[[], None],
        on_investigate: Callable[[Case], None],
        save_service: Optional[SaveService] = None
    ):
        self.screen = screen
        self.case_service = case_service
        self.on_back = on_back
        self.on_investigate = on_investigate
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service()

        self.anim_tick = 0
        self.cases = self.case_service.get_all_cases()
        self.active_filter = "ALL"
        self.preview_case: Optional[Case] = None

        # Difficulty & Status Filter Tabs
        filter_tabs = [
            ("ALL", "ALL CASES"),
            ("EASY", "🟢 EASY"),
            ("MEDIUM", "🟡 MEDIUM"),
            ("HARD", "🔴 HARD"),
            ("IN_PROGRESS", "IN PROGRESS"),
            ("COMPLETED", "COMPLETED")
        ]
        self.tab_panel = TabPanel(
            x=50, y=70, tab_items=filter_tabs, active_id="ALL",
            on_tab_changed=self._on_filter_changed,
            tab_width=115, tab_height=32, font_size=11
        )

        # Back button
        self.btn_back = AnimatedButton(40, 16, 120, 36, "← DASHBOARD", font_size=11, bg_color=(60, 45, 38), on_click=self.on_back)

        # Preview Modal Buttons
        self.btn_start_investigation = AnimatedButton(
            SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 120, 240, 44,
            "START INVESTIGATION ➔", font_size=12, bg_color=ACCENT_GREEN,
            on_click=self._handle_start_investigation
        )
        self.btn_close_preview = AnimatedButton(
            SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT - 120, 240, 44,
            "← BACK TO CASE FILES", font_size=12, bg_color=(70, 50, 45),
            on_click=self._close_preview
        )

    def _on_filter_changed(self, filter_id: str) -> None:
        self.active_filter = filter_id
        self.sound_service.play("click")

    def _get_filtered_cases(self) -> List[Case]:
        active_save = self.save_service.load_active_game()
        active_id = active_save.get("case_id") if active_save else None
        completed_ids = [r.get("case_id") for r in self.save_service.get_leaderboard() if r.get("verdict") == "SUPPORTED"]

        filtered = []
        for c in self.cases:
            diff = (c.difficulty or "").upper()
            if self.active_filter == "ALL":
                filtered.append(c)
            elif self.active_filter in ("EASY", "MEDIUM", "HARD") and diff == self.active_filter:
                filtered.append(c)
            elif self.active_filter == "IN_PROGRESS" and c.id == active_id:
                filtered.append(c)
            elif self.active_filter == "COMPLETED" and c.id in completed_ids:
                filtered.append(c)
        return filtered

    def _get_case_status(self, case_id: str) -> str:
        active_save = self.save_service.load_active_game()
        if active_save and active_save.get("case_id") == case_id:
            return "IN PROGRESS"
        completed_ids = [r.get("case_id") for r in self.save_service.get_leaderboard() if r.get("verdict") == "SUPPORTED"]
        if case_id in completed_ids:
            return "COMPLETED"
        return "NEW"

    def _open_preview(self, case: Case) -> None:
        self.preview_case = case
        self.sound_service.play("dossier")

    def _close_preview(self) -> None:
        self.preview_case = None
        self.sound_service.play("click")

    def _handle_start_investigation(self) -> None:
        if self.preview_case:
            self.sound_service.play("gavel")
            self.on_investigate(self.preview_case)

    def handle_events(self, events) -> None:
        for event in events:
            if self.preview_case:
                self.btn_start_investigation.handle_event(event)
                self.btn_close_preview.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._close_preview()
            else:
                self.btn_back.handle_event(event)
                self.tab_panel.handle_events([event])

                # Check card clicks
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    cases = self._get_filtered_cases()
                    for i, case in enumerate(cases):
                        card_rect = self._get_card_rect(i)
                        if card_rect.collidepoint(event.pos):
                            self._open_preview(case)
                            break

    def _get_card_rect(self, index: int) -> pygame.Rect:
        col_w = 310
        row_h = 240
        cols = 3
        gap_x = 30
        gap_y = 20
        start_x = 50
        start_y = 115

        col = index % cols
        row = index // cols
        return pygame.Rect(start_x + col * (col_w + gap_x), start_y + row * (row_h + gap_y), col_w, row_h)

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.btn_back.update(dt)
        self.tab_panel.update(dt)
        if self.preview_case:
            self.btn_start_investigation.update(dt)
            self.btn_close_preview.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Header Bar
        pygame.draw.rect(self.screen, WOOD_BROWN, (0, 0, SCREEN_WIDTH, 56))
        pygame.draw.line(self.screen, GOLD, (0, 56), (SCREEN_WIDTH, 56), 2)

        self.btn_back.draw(self.screen)

        title_font = get_font(16, bold=True)
        t_surf = title_font.render("SCOTLAND YARD & CROWN ARCHIVES — SELECT A CASE FILE", True, GOLD)
        self.screen.blit(t_surf, (180, 18))

        # Filter Tabs
        self.tab_panel.draw(self.screen)

        # Render Case Cards
        cases = self._get_filtered_cases()
        mouse_pos = pygame.mouse.get_pos()

        if not cases:
            empty_font = get_font(13)
            self.screen.blit(empty_font.render("No case files matching this filter.", True, MUTED_TEXT), (SCREEN_WIDTH // 2 - 120, 280))

        for i, case in enumerate(cases):
            card_rect = self._get_card_rect(i)
            is_hover = card_rect.collidepoint(mouse_pos)

            # Card Background
            bg_color = (48, 38, 32) if is_hover else CARD_BG
            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=8)
            border_col = GOLD if is_hover else GOLD_LIGHT
            pygame.draw.rect(self.screen, border_col, card_rect, 2 if is_hover else 1, border_radius=8)

            # Top Status Badge (Left)
            status = self._get_case_status(case.id)
            stat_color = ACCENT_GREEN if status == "COMPLETED" else ((180, 120, 40) if status == "IN PROGRESS" else (50, 75, 110))
            badge_rect = pygame.Rect(card_rect.x + 12, card_rect.y + 10, 95, 22)
            pygame.draw.rect(self.screen, stat_color, badge_rect, border_radius=4)
            self.screen.blit(get_font(10, bold=True).render(status, True, WHITE), (badge_rect.x + 8, badge_rect.y + 4))

            # Difficulty Pill Badge (Top Right)
            diff = (case.difficulty or "MEDIUM").upper()
            if diff == "EASY":
                diff_col = (40, 140, 60)
                diff_txt = "🟢 EASY"
            elif diff == "HARD":
                diff_col = (160, 45, 45)
                diff_txt = "🔴 HARD"
            else:
                diff_col = (160, 115, 30)
                diff_txt = "🟡 MEDIUM"

            diff_pill = pygame.Rect(card_rect.right - 95, card_rect.y + 10, 83, 22)
            pygame.draw.rect(self.screen, diff_col, diff_pill, border_radius=4)
            self.screen.blit(get_font(10, bold=True).render(diff_txt, True, WHITE), (diff_pill.x + 6, diff_pill.y + 4))

            # Title
            t_font = get_font(15, bold=True)
            self.screen.blit(t_font.render(case.title, True, WHITE), (card_rect.x + 12, card_rect.y + 38))

            # Type & Reward (Short & punchy)
            type_font = get_font(11, bold=True)
            self.screen.blit(type_font.render(f"{case.type} • Reward: £{case.reward}", True, GOLD_LIGHT), (card_rect.x + 12, card_rect.y + 62))

            # Description (wrapped)
            desc_font = get_font(11)
            words = case.description.split(" ")
            lines = []
            cur = []
            for w in words:
                if desc_font.size(" ".join(cur + [w]))[0] > (card_rect.width - 24):
                    lines.append(" ".join(cur))
                    cur = [w]
                else:
                    cur.append(w)
            if cur:
                lines.append(" ".join(cur))

            dy = card_rect.y + 86
            for line in lines[:3]:
                self.screen.blit(desc_font.render(line, True, (215, 205, 195)), (card_rect.x + 12, dy))
                dy += 18

            # Metrics Footer Box
            f_box = pygame.Rect(card_rect.x + 10, card_rect.bottom - 46, card_rect.width - 20, 36)
            pygame.draw.rect(self.screen, (30, 22, 18), f_box, border_radius=5)

            m_font = get_font(11, bold=True)
            sus_txt = f"👥 {len(case.suspects)} Suspects"
            ev_txt = f"🔍 {len(case.evidence_list)} Clues"
            id_txt = f"#{case.id}"

            self.screen.blit(m_font.render(sus_txt, True, LIGHT_PARCHMENT), (f_box.x + 10, f_box.y + 10))
            self.screen.blit(m_font.render(ev_txt, True, LIGHT_PARCHMENT), (f_box.x + 125, f_box.y + 10))
            self.screen.blit(m_font.render(id_txt, True, GOLD), (f_box.x + 225, f_box.y + 10))

        # Render Case Preview Modal if open
        if self.preview_case:
            self._draw_case_preview_modal()

    def _draw_case_preview_modal(self) -> None:
        """Renders comprehensive dossier preview popup before entering investigation."""
        # Dimmer
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 190))
        self.screen.blit(dim, (0, 0))

        case = self.preview_case
        modal_w, modal_h = 820, 530
        mx = (SCREEN_WIDTH - modal_w) // 2
        my = (SCREEN_HEIGHT - modal_h) // 2 - 20
        m_rect = pygame.Rect(mx, my, modal_w, modal_h)

        pygame.draw.rect(self.screen, CARD_BG, m_rect, border_radius=10)
        pygame.draw.rect(self.screen, GOLD, m_rect, 2, border_radius=10)

        # Header
        pygame.draw.rect(self.screen, (45, 30, 22), (mx, my, modal_w, 56), border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.line(self.screen, GOLD_LIGHT, (mx, my + 56), (mx + modal_w, my + 56), 1)

        diff = (case.difficulty or "MEDIUM").upper()
        diff_badge = "🟢 EASY" if diff == "EASY" else ("🔴 HARD" if diff == "HARD" else "🟡 MEDIUM")

        self.screen.blit(get_font(17, bold=True).render(f"DOSSIER: {case.title.upper()}", True, GOLD), (mx + 20, my + 15))
        self.screen.blit(get_font(12, bold=True).render(f"Case {case.id}  •  {diff_badge}", True, LIGHT_PARCHMENT), (mx + modal_w - 230, my + 18))

        # Left Column: Summary, Scene & Report
        left_x = mx + 25
        left_w = 370
        content_y = my + 72

        self.screen.blit(get_font(14, bold=True).render("INCIDENT SUMMARY", True, GOLD), (left_x, content_y))
        # Description
        desc_font = get_font(13)
        words = case.description.split(" ")
        lines = []
        cur = []
        for w in words:
            if desc_font.size(" ".join(cur + [w]))[0] > left_w:
                lines.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(" ".join(cur))

        dy = content_y + 26
        for l in lines:
            self.screen.blit(desc_font.render(l, True, WHITE), (left_x, dy))
            dy += 20

        # Location & Scene details
        dy += 8
        self.screen.blit(get_font(13, bold=True).render(f"Scene: {case.scene_name} ({case.scene_type})", True, LIGHT_PARCHMENT), (left_x, dy))

        # Objective Box
        obj_box = pygame.Rect(left_x, dy + 28, left_w, 115)
        pygame.draw.rect(self.screen, (35, 45, 35), obj_box, border_radius=6)
        pygame.draw.rect(self.screen, ACCENT_GREEN, obj_box, 1, border_radius=6)

        self.screen.blit(get_font(13, bold=True).render("INVESTIGATION OBJECTIVE:", True, ACCENT_GREEN), (obj_box.x + 12, obj_box.y + 10))
        obj_text = (
            f"Prove legal proposition:\n'{case.solution_conclusion}'\n"
            f"Present verifiable evidence and refute false alibis in court."
        )
        oy = obj_box.y + 34
        for ol in obj_text.split("\n"):
            self.screen.blit(get_font(12, bold=True).render(ol, True, WHITE), (obj_box.x + 12, oy))
            oy += 20

        # Right Column: Known Suspects & Clue Count
        right_x = left_x + left_w + 30
        right_w = 360

        self.screen.blit(get_font(14, bold=True).render(f"KNOWN PERSONS OF INTEREST ({len(case.suspects)})", True, GOLD), (right_x, content_y))

        sy = content_y + 26
        for s in case.suspects[:4]:
            s_rect = pygame.Rect(right_x, sy, right_w, 52)
            pygame.draw.rect(self.screen, (35, 28, 24), s_rect, border_radius=5)
            pygame.draw.rect(self.screen, (80, 60, 50), s_rect, 1, border_radius=5)

            self.screen.blit(get_font(13, bold=True).render(s.name, True, WHITE), (s_rect.x + 10, s_rect.y + 6))
            self.screen.blit(get_font(12).render(f"{s.occupation} • {s.relationship}", True, LIGHT_PARCHMENT), (s_rect.x + 10, s_rect.y + 28))
            sy += 58

        # Initial Evidence Overview
        ey = sy + 6
        self.screen.blit(get_font(13, bold=True).render(f"FORENSIC ARTIFACTS: {len(case.evidence_list)} Items to Inspect", True, GOLD_LIGHT), (right_x, ey))

        # Draw Modal Action Buttons
        self.btn_close_preview.draw(self.screen)
        self.btn_start_investigation.draw(self.screen)