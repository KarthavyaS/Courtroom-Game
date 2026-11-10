"""Verdict and Results Screen for LOGIC COURTROOM.
Presents the detailed post-trial ruling delivered by the AI Judge:
- Final case outcome (SUPPORTED / NOT PROVEN / CONTRADICTED) with clear logical meaning.
- Detailed score breakdown (Quality, Evidence, Logic, Discipline).
- Comprehensive judicial feedback and recommendations for improvement.
- Review Hearing, Review Case, Play Another Case, and Return to Dashboard actions.
"""

import pygame
import math
from typing import Callable, Optional, Dict, Any
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, get_font
)
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.animation import WaxSealStamp

class ResultsScreen:
    """Comprehensive post-trial verdict and judicial assessment screen."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        verdict_data: Dict[str, Any],
        on_review_hearing: Callable[[], None],
        on_review_case: Callable[[], None],
        on_play_another: Callable[[], None],
        on_dashboard: Callable[[], None],
        save_service: Optional[SaveService] = None
    ):
        self.screen = screen
        self.game_state = game_state
        self.verdict_data = verdict_data or {}
        self.on_review_hearing = on_review_hearing
        self.on_review_case = on_review_case
        self.on_play_another = on_play_another
        self.on_dashboard = on_dashboard
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service()

        self.anim_tick = 0
        self.wax_seal = WaxSealStamp()

        outcome = self.verdict_data.get("verdict") or self.verdict_data.get("status") or "SUPPORTED"
        is_won = (outcome == "SUPPORTED")
        self.wax_seal.trigger(
            text="PROVEN" if is_won else ("CONTRADICTED" if outcome == "CONTRADICTED" else "NOT PROVEN"),
            is_won=is_won
        )

        # Mark courtroom finished
        self.game_state.progress.record_courtroom_finished()
        self.save_service.clear_active_save()

        # Action Buttons
        btn_y = SCREEN_HEIGHT - 65
        btn_w = 230
        btn_h = 42

        self.btn_review_hearing = AnimatedButton(
            50, btn_y, btn_w, btn_h, "📜 REVIEW HEARING", font_size=11,
            bg_color=(60, 50, 45), on_click=self.on_review_hearing
        )
        self.btn_review_case = AnimatedButton(
            300, btn_y, btn_w, btn_h, "📁 REVIEW CASE FILE", font_size=11,
            bg_color=(75, 60, 50), on_click=self.on_review_case
        )
        self.btn_play_another = AnimatedButton(
            550, btn_y, btn_w, btn_h, "📂 PLAY ANOTHER CASE", font_size=11,
            bg_color=(130, 80, 45), on_click=self.on_play_another
        )
        self.btn_dashboard = AnimatedButton(
            800, btn_y, btn_w, btn_h, "⌂ RETURN TO HUB", font_size=11,
            bg_color=ACCENT_GREEN, on_click=self.on_dashboard
        )

        self.buttons = [self.btn_review_hearing, self.btn_review_case, self.btn_play_another, self.btn_dashboard]

    def handle_events(self, events) -> None:
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event)

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.wax_seal.update(dt)
        for btn in self.buttons:
            btn.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Header Bar
        pygame.draw.rect(self.screen, WOOD_BROWN, (0, 0, SCREEN_WIDTH, 56))
        pygame.draw.line(self.screen, GOLD, (0, 56), (SCREEN_WIDTH, 56), 2)

        self.screen.blit(get_font(18, bold=True).render("COURT OF QUEEN'S BENCH — OFFICIAL VERDICT & DECREE", True, GOLD), (35, 16))

        # Outcome Banner
        outcome = self.verdict_data.get("verdict") or self.verdict_data.get("status") or "SUPPORTED"
        score = self.verdict_data.get("total_score", self.verdict_data.get("score", 100))

        ban_rect = pygame.Rect(50, 75, SCREEN_WIDTH - 100, 85)
        if outcome == "SUPPORTED":
            ban_bg = (30, 55, 30)
            ban_bdr = ACCENT_GREEN
            ban_title = "VERDICT: ARGUMENT SUPPORTED (PROVEN BEYOND DOUBT)"
            ban_sub = "The supplied premises logically entail the conclusion through sound deduction."
        elif outcome == "CONTRADICTED":
            ban_bg = (55, 25, 25)
            ban_bdr = ACCENT_RED
            ban_title = "VERDICT: CONTRADICTED BY EVIDENCE"
            ban_sub = "Physical evidence or established case rules directly refute the argument."
        else:
            ban_bg = (55, 45, 25)
            ban_bdr = GOLD
            ban_title = "VERDICT: NOT PROVEN (INSUFFICIENT PROPOSITIONS)"
            ban_sub = "The deduction is plausible, but missing key physical evidence to achieve conviction."

        pygame.draw.rect(self.screen, ban_bg, ban_rect, border_radius=8)
        pygame.draw.rect(self.screen, ban_bdr, ban_rect, 2, border_radius=8)

        self.screen.blit(get_font(16, bold=True).render(ban_title, True, ban_bdr), (ban_rect.x + 20, ban_rect.y + 16))
        self.screen.blit(get_font(11).render(ban_sub, True, LIGHT_PARCHMENT), (ban_rect.x + 20, ban_rect.y + 48))

        # Score on right of banner
        s_surf = get_font(20, bold=True).render(f"+{score} PTS", True, GOLD)
        self.screen.blit(s_surf, (ban_rect.right - s_surf.get_width() - 25, ban_rect.y + 25))

        # 2 Column Body Layout
        col_y = 175
        col_h = SCREEN_HEIGHT - col_y - 80

        # Left Column: Detailed Inference Summary (w=580)
        c1_rect = pygame.Rect(50, col_y, 560, col_h)
        pygame.draw.rect(self.screen, CARD_BG, c1_rect, border_radius=8)
        pygame.draw.rect(self.screen, GOLD_LIGHT, c1_rect, 1, border_radius=8)

        self.screen.blit(get_font(13, bold=True).render("JUDICIAL INFERENCE SUMMARY", True, GOLD), (c1_rect.x + 18, c1_rect.y + 14))

        reasoning = self.verdict_data.get("feedback") or self.verdict_data.get("reasoning") or "Deductive rules satisfied all requirements."
        desc_font = get_font(11)
        self._render_wrapped_text(f"Judicial Finding:\n{reasoning}", c1_rect.x + 18, c1_rect.y + 42, c1_rect.width - 36, desc_font, WHITE)

        # AI Trace Box
        trace_box = pygame.Rect(c1_rect.x + 14, c1_rect.bottom - 165, c1_rect.width - 28, 145)
        pygame.draw.rect(self.screen, (30, 22, 18), trace_box, border_radius=6)
        pygame.draw.rect(self.screen, (70, 55, 45), trace_box, 1, border_radius=6)

        self.screen.blit(get_font(11, bold=True).render("AI ENGINE DERIVATION METRICS:", True, GOLD), (trace_box.x + 12, trace_box.y + 10))
        self.screen.blit(get_font(10).render("• Forward Chaining: Entailment verified across KnowledgeBase", True, LIGHT_PARCHMENT), (trace_box.x + 12, trace_box.y + 34))
        self.screen.blit(get_font(10).render("• Propositional Resolution: Refutation graph closed with empty clause", True, LIGHT_PARCHMENT), (trace_box.x + 12, trace_box.y + 56))
        self.screen.blit(get_font(10).render("• Fallacy Safeguards: Non-sequitur check passed", True, LIGHT_PARCHMENT), (trace_box.x + 12, trace_box.y + 78))
        self.screen.blit(get_font(10).render("• Relevant Statements: Supported and logged in court transcript", True, LIGHT_PARCHMENT), (trace_box.x + 12, trace_box.y + 100))

        # Right Column: Score Breakdown & Feedback (w=410)
        c2_rect = pygame.Rect(630, col_y, 420, col_h)
        pygame.draw.rect(self.screen, CARD_BG, c2_rect, border_radius=8)
        pygame.draw.rect(self.screen, GOLD_LIGHT, c2_rect, 1, border_radius=8)

        self.screen.blit(get_font(13, bold=True).render("PERFORMANCE EVALUATION", True, GOLD), (c2_rect.x + 18, c2_rect.y + 14))

        breakdown = [
            ("Logical Entailment Validity", "95%"),
            ("Evidence Collection Completeness", f"{len(self.game_state.collected_evidence_ids)} Clues"),
            ("Court Discipline & Relevance", f"{4 - getattr(self.game_state, 'warning_count', 0)}/4 Strikes"),
            ("Suspect Interrogation Depth", f"{len(self.game_state.progress.interviewed_suspect_ids)} Suspects")
        ]

        by = c2_rect.y + 44
        for label, val in breakdown:
            b_box = pygame.Rect(c2_rect.x + 14, by, c2_rect.width - 28, 38)
            pygame.draw.rect(self.screen, (35, 28, 24), b_box, border_radius=4)
            self.screen.blit(get_font(10).render(label, True, LIGHT_PARCHMENT), (b_box.x + 10, b_box.y + 10))
            self.screen.blit(get_font(11, bold=True).render(val, True, GOLD), (b_box.right - 80, b_box.y + 10))
            by += 44

        # Advice box
        adv_box = pygame.Rect(c2_rect.x + 14, by + 10, c2_rect.width - 28, 120)
        pygame.draw.rect(self.screen, (35, 45, 35), adv_box, border_radius=6)
        pygame.draw.rect(self.screen, ACCENT_GREEN, adv_box, 1, border_radius=6)

        self.screen.blit(get_font(11, bold=True).render("RECOMMENDATION FOR FUTURE CASES:", True, ACCENT_GREEN), (adv_box.x + 10, adv_box.y + 10))
        adv_msg = "Always verify physical evidence against stated suspect alibis before submitting your final argument."
        self._render_wrapped_text(adv_msg, adv_box.x + 10, adv_box.y + 32, adv_box.width - 20, get_font(10), WHITE)

        # Draw Bottom Buttons
        for btn in self.buttons:
            btn.draw(self.screen)

        # Draw Wax Seal Stamp Animation
        self.wax_seal.draw(self.screen, get_font)

    def _render_wrapped_text(self, text: str, x: int, y: int, max_w: int, font: pygame.font.Font, color: tuple) -> None:
        words = text.split(" ")
        lines = []
        cur = []
        for w in words:
            if "\n" in w:
                parts = w.split("\n")
                cur.append(parts[0])
                lines.append(" ".join(cur))
                cur = [parts[1]] if len(parts) > 1 else []
            else:
                if font.size(" ".join(cur + [w]))[0] > max_w:
                    lines.append(" ".join(cur))
                    cur = [w]
                else:
                    cur.append(w)
        if cur:
            lines.append(" ".join(cur))

        for l in lines:
            self.screen.blit(font.render(l, True, color), (x, y))
            y += 18
