"""Suspect Interrogation and Profile Dossier Screen for LOGIC COURTROOM.
Features interactive character selector cards, tabbed dossiers (Profile, Motive, Alibi,
Statement, Facts, Contradictions), 5 predefined interview questions with case-specific
responses, animated character expressions, and interview summaries.
"""
#pyright: ignore
import pygame
import math
from typing import Callable, Optional, List, Dict
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, GOLD_DARK, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, get_font
)
from models.suspect import Suspect
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.character_sprite import CharacterSprite
from components.navigation_bar import NavigationBar
from components.tab_panel import TabPanel

PREDEFINED_QUESTIONS = [
    ("Q1", "Where were you at the time of the incident?"),
    ("Q2", "What was your relationship with the victim?"),
    ("Q3", "Did you see anyone near the crime scene?"),
    ("Q4", "Why were you present at the location?"),
    ("Q5", "Can you explain the inconsistencies in your story?")
]

class SuspectDetails:
    """Dedicated suspect interrogation and dossier analysis screen."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        on_nav_dashboard: Callable[[], None],
        on_nav_briefing: Callable[[], None],
        on_nav_scene: Callable[[], None],
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
        self.on_nav_scene = on_nav_scene
        self.on_nav_evidence = on_nav_evidence
        self.on_nav_board = on_nav_board
        self.on_nav_notebook = on_nav_notebook
        self.on_nav_arguments = on_nav_arguments
        self.on_nav_courtroom = on_nav_courtroom
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service()

        self.anim_tick = 0
        self.active_tab = "PROFILE"
        self.current_response_text = ""
        self.selected_question_text = ""
        self.selected_question_id = None
        self.questions_minimized = False
        self.dossier_minimized = False
        self.character_sprite = CharacterSprite()
        self.suspect_stress: Dict[str, float] = {}

        # Navigation Bar
        self.nav_bar = NavigationBar(
            current_stage="suspects",
            game_state=self.game_state,
            on_nav_dashboard=self.on_nav_dashboard,
            on_nav_briefing=self.on_nav_briefing,
            on_nav_scene=self.on_nav_scene,
            on_nav_suspects=None,
            on_nav_evidence=self.on_nav_evidence,
            on_nav_board=self.on_nav_board,
            on_nav_notebook=self.on_nav_notebook,
            on_nav_arguments=self.on_nav_arguments,
            on_nav_courtroom=self.on_nav_courtroom
        )

        # Tab Panel for Suspect Dossier
        dossier_tabs = [
            ("PROFILE", "PROFILE"),
            ("MOTIVE", "MOTIVE"),
            ("ALIBI", "ALIBI"),
            ("STATEMENT", "TESTIMONY"),
            ("CONTRADICTIONS", "CONTRADICTIONS ⚡"),
            ("INTERVIEW", "INTERROGATE 💬")
        ]
        self.tab_panel = TabPanel(
            x=335, y=68, tab_items=dossier_tabs, active_id="PROFILE",
            on_tab_changed=self._on_tab_changed,
            tab_width=92, tab_height=34, font_size=9
        )

        # Flexible Minimize Controls
        self.btn_toggle_dossier = AnimatedButton(
            910, 127, 145, 26, "− MINIMIZE DOSSIER", font_size=10,
            bg_color=(50, 36, 30), border_color=GOLD, on_click=self._toggle_dossier_minimized
        )
        self.btn_toggle_questions = AnimatedButton(
            875, 172, 180, 26, "− MINIMIZE QUESTIONS", font_size=10,
            bg_color=(50, 40, 32), border_color=GOLD, on_click=self._toggle_questions_minimized
        )

        # Predefined Question Buttons for Interview tab
        self.question_buttons: List[AnimatedButton] = []
        self._build_question_buttons()

        # Summary / Action button
        self.btn_next_stage = AnimatedButton(
            915, 68, 150, 34,
            "CASE BOARD ➔", font_size=10, bg_color=(40, 85, 140),
            border_color=(120, 190, 255), on_click=self.on_nav_board
        )

    def _toggle_dossier_minimized(self) -> None:
        self.dossier_minimized = not self.dossier_minimized
        self.btn_toggle_dossier.text = "+ EXPAND DOSSIER" if self.dossier_minimized else "− MINIMIZE DOSSIER"
        self.sound_service.play("click")

    def _toggle_questions_minimized(self) -> None:
        self.questions_minimized = not self.questions_minimized
        self.btn_toggle_questions.text = "+ EXPAND QUESTIONS" if self.questions_minimized else "− MINIMIZE QUESTIONS"
        self.sound_service.play("click")

    def _on_tab_changed(self, tab_id: str) -> None:
        self.active_tab = tab_id
        if self.dossier_minimized:
            self._toggle_dossier_minimized()
        self.sound_service.play("click")

    def _build_question_buttons(self) -> None:
        self.question_buttons.clear()
        qy = 204
        btn_h = 30
        gap = 4
        for q_id, q_text in PREDEFINED_QUESTIONS:
            def make_handler(qid=q_id, qtxt=q_text):
                def handler():
                    self._ask_question(qid, qtxt)
                return handler

            btn = AnimatedButton(
                350, qy, 700, btn_h, f"• {q_id}: {q_text}",
                font_size=11, bg_color=(45, 36, 30), on_click=make_handler()
            )
            self.question_buttons.append(btn)
            qy += btn_h + gap

    def _ask_question(self, q_id: str, q_text: str) -> None:
        suspect = self.game_state.get_selected_suspect()
        if not suspect:
            return

        cur_stress = self.suspect_stress.get(suspect.id, 20.0)

        # Case specific response logic & Stress Spikes
        if q_id == "Q1":  # Where were you?
            self.current_response_text = f'"{suspect.alibi}"'
            if suspect.is_guilty or suspect.contradictions:
                self.character_sprite.set_expression("nervous")
                cur_stress = min(95.0, cur_stress + 35.0)
            else:
                self.character_sprite.set_expression("calm")
        elif q_id == "Q2":  # Relationship?
            self.current_response_text = f'"{suspect.motive}"'
            self.character_sprite.set_expression("defensive" if suspect.is_guilty else "calm")
            cur_stress = min(95.0, cur_stress + 15.0)
        elif q_id == "Q3":  # Did you see anyone?
            self.current_response_text = f'"{suspect.statement}"'
            self.character_sprite.set_expression("surprised" if suspect.is_guilty else "calm")
            cur_stress = min(95.0, cur_stress + 10.0)
        elif q_id == "Q4":  # Why were you present?
            self.current_response_text = f'"I had legitimate business matters concerning {suspect.occupation}."'
            self.character_sprite.set_expression("calm")
        elif q_id == "Q5":  # Explain inconsistencies?
            if suspect.contradictions:
                self.current_response_text = f'"That is preposterous! {suspect.contradictions[0]}"'
                self.character_sprite.set_expression("nervous")
                cur_stress = min(100.0, cur_stress + 45.0)
            else:
                self.current_response_text = '"My statements are completely truthful and verified by physical logs."'
                self.character_sprite.set_expression("calm")

        self.suspect_stress[suspect.id] = cur_stress

        # Record progress
        tot_sus = len(self.game_state.current_case.suspects) if self.game_state.current_case else 1
        self.game_state.progress.record_suspect_interview(suspect.id, q_id, tot_sus)
        self.save_service.save_active_game(self.game_state)
        self.sound_service.play("typewriter")

    def handle_events(self, events) -> None:
        self.nav_bar.handle_events(events)
        for event in events:
            self.btn_next_stage.handle_event(event)
            self.tab_panel.handle_events([event])
            self.btn_toggle_dossier.handle_event(event)

            # Suspect selector clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_state.current_case:
                    for i, s in enumerate(self.game_state.current_case.suspects):
                        s_rect = pygame.Rect(35, 115 + i * 115, 280, 105)
                        if s_rect.collidepoint(event.pos):
                            self.game_state.selected_suspect_id = s.id
                            self.current_response_text = ""
                            self.selected_question_id = None
                            self.selected_question_text = ""
                            self.character_sprite.set_expression("calm")
                            self.sound_service.play("click")
                            break

            if self.active_tab == "INTERVIEW" and not self.dossier_minimized:
                self.btn_toggle_questions.handle_event(event)
                if not self.questions_minimized:
                    for qb in self.question_buttons:
                        qb.handle_event(event)

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.nav_bar.update(dt)
        self.tab_panel.update(dt)
        self.btn_next_stage.update(dt)
        self.btn_toggle_dossier.update(dt)
        self.character_sprite.update(dt)
        if self.active_tab == "INTERVIEW" and not self.dossier_minimized:
            self.btn_toggle_questions.update(dt)
            if not self.questions_minimized:
                for qb in self.question_buttons:
                    qb.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Top Navigation
        self.nav_bar.draw(self.screen)

        case = self.game_state.current_case
        if not case:
            return

        # Header Strip
        self.btn_next_stage.draw(self.screen)
        self.tab_panel.draw(self.screen)

        # Left Column: Suspect Cards
        for i, s in enumerate(case.suspects):
            is_selected = (s.id == self.game_state.selected_suspect_id)
            is_interviewed = (s.id in self.game_state.progress.interviewed_suspect_ids)

            card_rect = pygame.Rect(35, 115 + i * 115, 280, 105)
            bg_col = (45, 35, 30) if is_selected else CARD_BG
            pygame.draw.rect(self.screen, bg_col, card_rect, border_radius=8)
            bdr_col = GOLD if is_selected else (80, 60, 50)
            pygame.draw.rect(self.screen, bdr_col, card_rect, 2 if is_selected else 1, border_radius=8)

            # Avatar Box
            av_rect = pygame.Rect(card_rect.x + 10, card_rect.y + 12, 60, 80)
            pygame.draw.rect(self.screen, (30, 22, 18), av_rect, border_radius=6)
            self.character_sprite.draw(self.screen, av_rect.x + 5, av_rect.y + 10, 50, 65, role=s.avatar_type, expression="calm")

            # Details
            info_x = card_rect.x + 78
            self.screen.blit(get_font(12, bold=True).render(s.name, True, GOLD if is_selected else WHITE), (info_x, card_rect.y + 12))
            self.screen.blit(get_font(10).render(s.occupation[:24], True, LIGHT_PARCHMENT), (info_x, card_rect.y + 34))
            self.screen.blit(get_font(10).render(f"Rel: {s.relationship[:20]}", True, MUTED_TEXT), (info_x, card_rect.y + 52))

            # Status Badge
            stat_col = ACCENT_GREEN if is_interviewed else (140, 100, 40)
            stat_txt = "INTERVIEWED ✓" if is_interviewed else "NOT QUESTIONED"
            stat_rect = pygame.Rect(info_x, card_rect.y + 74, 110, 18)
            pygame.draw.rect(self.screen, stat_col, stat_rect, border_radius=3)
            self.screen.blit(get_font(8, bold=True).render(stat_txt, True, WHITE), (stat_rect.x + 6, stat_rect.y + 3))

        # Right Column: Detailed Dossier Panel (with flexible minimize)
        dossier_h = 50 if self.dossier_minimized else 545
        dossier_rect = pygame.Rect(335, 115, 730, dossier_h)
        pygame.draw.rect(self.screen, CARD_BG, dossier_rect, border_radius=8)
        pygame.draw.rect(self.screen, GOLD_LIGHT, dossier_rect, 1, border_radius=8)

        suspect = self.game_state.get_selected_suspect()
        if suspect:
            self._draw_suspect_dossier(dossier_rect, suspect)

    def _draw_suspect_dossier(self, rect: pygame.Rect, suspect: Suspect) -> None:
        """Renders the active tab for the selected suspect."""
        # Header banner inside dossier
        pygame.draw.rect(self.screen, (35, 28, 24), (rect.x, rect.y, rect.width, 50), border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(self.screen, GOLD_LIGHT, (rect.x, rect.y + 50), (rect.right, rect.y + 50), 1)

        self.screen.blit(get_font(13, bold=True).render(f"DOSSIER: {suspect.name.upper()}", True, GOLD), (rect.x + 18, rect.y + 14))

        # Galvanic Demeanor & Heartbeat Stress Meter in header
        stress_val = self.suspect_stress.get(suspect.id, 20.0)
        meter_rect = pygame.Rect(rect.x + 280, rect.y + 11, 230, 28)
        pygame.draw.rect(self.screen, (25, 18, 14), meter_rect, border_radius=4)
        pygame.draw.rect(self.screen, ACCENT_RED if stress_val > 60 else GOLD, meter_rect, 1, border_radius=4)

        pulse_h = math.sin(self.anim_tick * (0.15 if stress_val < 50 else 0.35)) * (4.0 if stress_val < 50 else 9.0)
        mid_y = meter_rect.centery
        pts = [
            (meter_rect.x + 8, mid_y),
            (meter_rect.x + 22, mid_y),
            (meter_rect.x + 32, mid_y - pulse_h),
            (meter_rect.x + 42, mid_y + pulse_h * 1.2),
            (meter_rect.x + 50, mid_y - pulse_h * 0.8),
            (meter_rect.x + 58, mid_y),
            (meter_rect.x + 75, mid_y)
        ]
        pygame.draw.lines(self.screen, (255, 80, 70) if stress_val > 60 else (100, 255, 150), False, pts, 2)
        self.screen.blit(get_font(9, bold=True).render(f"STRESS: {int(stress_val)}%", True, WHITE), (meter_rect.x + 85, meter_rect.y + 7))

        # Dossier minimize/expand toggle button
        self.btn_toggle_dossier.orig_rect.topleft = (rect.right - 160, rect.y + 11)
        self.btn_toggle_dossier.rect.topleft = (rect.right - 160, rect.y + 11)
        self.btn_toggle_dossier.draw(self.screen)

        if self.dossier_minimized:
            return

        content_y = rect.y + 60
        content_w = rect.width - 36
        cx = rect.x + 18

        if self.active_tab == "PROFILE":
            self.screen.blit(get_font(12, bold=True).render("PERSONAL PROFILE & OCCUPATION", True, GOLD), (cx, content_y))
            self.screen.blit(get_font(11).render(f"Full Legal Name: {suspect.name}", True, WHITE), (cx, content_y + 28))
            self.screen.blit(get_font(11).render(f"Profession / Role: {suspect.occupation}", True, WHITE), (cx, content_y + 52))
            self.screen.blit(get_font(11).render(f"Relationship to Victim: {suspect.relationship}", True, WHITE), (cx, content_y + 76))

            # Avatar Portrait
            p_rect = pygame.Rect(rect.right - 180, content_y + 10, 140, 170)
            pygame.draw.rect(self.screen, (30, 22, 18), p_rect, border_radius=8)
            pygame.draw.rect(self.screen, GOLD, p_rect, 1, border_radius=8)
            self.character_sprite.draw(self.screen, p_rect.x + 20, p_rect.y + 20, 100, 130, role=suspect.avatar_type, expression=self.character_sprite.expression)

        elif self.active_tab == "MOTIVE":
            self.screen.blit(get_font(12, bold=True).render("ALLEGED MOTIVE / PECUNIARY INTEREST", True, GOLD), (cx, content_y))
            box = pygame.Rect(cx, content_y + 28, content_w, 120)
            pygame.draw.rect(self.screen, (35, 28, 24), box, border_radius=6)
            self._render_wrapped_text(suspect.motive, cx + 14, content_y + 42, content_w - 28, get_font(11), WHITE)

        elif self.active_tab == "ALIBI":
            self.screen.blit(get_font(12, bold=True).render("STATED ALIBI AT TIME OF INCIDENT", True, GOLD), (cx, content_y))
            box = pygame.Rect(cx, content_y + 28, content_w, 120)
            pygame.draw.rect(self.screen, (35, 28, 24), box, border_radius=6)
            self._render_wrapped_text(suspect.alibi, cx + 14, content_y + 42, content_w - 28, get_font(11), WHITE)

        elif self.active_tab == "STATEMENT":
            self.screen.blit(get_font(12, bold=True).render("SWORN POLICE TESTIMONY", True, GOLD), (cx, content_y))
            box = pygame.Rect(cx, content_y + 28, content_w, 140)
            pygame.draw.rect(self.screen, (35, 28, 24), box, border_radius=6)
            self._render_wrapped_text(f'"{suspect.statement}"', cx + 14, content_y + 42, content_w - 28, get_font(11), LIGHT_PARCHMENT)

        elif self.active_tab == "CONTRADICTIONS":
            self.screen.blit(get_font(12, bold=True).render("DISCOVERED CONTRADICTIONS & INCONSISTENCIES ⚡", True, ACCENT_RED), (cx, content_y))
            if suspect.contradictions:
                cy = content_y + 32
                for contra in suspect.contradictions:
                    c_box = pygame.Rect(cx, cy, content_w, 65)
                    pygame.draw.rect(self.screen, (55, 25, 25), c_box, border_radius=6)
                    pygame.draw.rect(self.screen, ACCENT_RED, c_box, 1, border_radius=6)
                    self._render_wrapped_text(f"• {contra}", cx + 12, cy + 12, content_w - 24, get_font(11), WHITE)
                    cy += 75
            else:
                self.screen.blit(get_font(11).render("No verified physical contradictions detected in this statement.", True, MUTED_TEXT), (cx, content_y + 36))

        elif self.active_tab == "INTERVIEW":
            # Header Row for Interrogation
            self.screen.blit(get_font(12, bold=True).render("INTERROGATION QUESTIONS:", True, GOLD), (cx, content_y + 4))

            # Toggle Questions Minimize Button
            self.btn_toggle_questions.orig_rect.topleft = (rect.right - 198, content_y)
            self.btn_toggle_questions.rect.topleft = (rect.right - 198, content_y)
            self.btn_toggle_questions.draw(self.screen)

            if not self.questions_minimized:
                # Render Question Buttons (Non-overlapping, top section)
                for qb in self.question_buttons:
                    qb.draw(self.screen)
                resp_box_y = 378
                resp_box_h = 268
            else:
                # Compact question status bar
                active_q_box = pygame.Rect(cx, content_y + 30, content_w, 30)
                pygame.draw.rect(self.screen, (38, 28, 22), active_q_box, border_radius=6)
                pygame.draw.rect(self.screen, GOLD_DARK, active_q_box, 1, border_radius=6)
                q_summary = self.selected_question_text or "No question selected yet. Expand questions above."
                self.screen.blit(get_font(10, bold=True).render(f"Active Question: {q_summary[:85]}", True, GOLD_LIGHT), (active_q_box.x + 12, active_q_box.y + 7))

                resp_box_y = content_y + 68
                resp_box_h = 415

            # Response Display Panel (Completely separate, guaranteed zero overlap)
            resp_box = pygame.Rect(cx, resp_box_y, content_w, resp_box_h)
            pygame.draw.rect(self.screen, (30, 24, 20), resp_box, border_radius=8)
            pygame.draw.rect(self.screen, GOLD, resp_box, 1, border_radius=8)

            # Response Sub-header Bar
            header_sub = pygame.Rect(resp_box.x, resp_box.y, resp_box.width, 32)
            pygame.draw.rect(self.screen, (40, 30, 24), header_sub, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.line(self.screen, GOLD_DARK, (header_sub.x, header_sub.bottom), (header_sub.right, header_sub.bottom), 1)

            self.screen.blit(get_font(11, bold=True).render(f"💬 {suspect.name.upper()} RESPONSE & TESTIMONY:", True, GOLD), (header_sub.x + 14, header_sub.y + 8))

            expr = self.character_sprite.expression.upper()
            tag_col = ACCENT_RED if expr in ("NERVOUS", "DEFENSIVE") else ACCENT_GREEN
            self.screen.blit(get_font(9, bold=True).render(f"DEMEANOR: {expr}", True, tag_col), (header_sub.right - 145, header_sub.y + 9))

            # Response wrapped text
            text_area_y = resp_box.y + 42
            if self.current_response_text:
                self._render_wrapped_text(self.current_response_text, resp_box.x + 16, text_area_y, resp_box.width - 32, get_font(11), WHITE)
            else:
                self.screen.blit(get_font(11, italic=True).render("(Select an interrogation question above to observe suspect's verbal statement and demeanor.)", True, MUTED_TEXT), (resp_box.x + 16, text_area_y))

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
            y += 22
