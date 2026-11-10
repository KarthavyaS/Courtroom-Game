"""Interactive Tutorial Screen for LOGIC COURTROOM.
Presents a guided 7-step walkthrough of all game mechanics with interactive illustrations.
"""

import pygame
import math
from typing import Callable
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, get_font
)
from services.tutorial_service import TutorialService
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton

class TutorialScreen:
    """Interactive 7-step game walkthrough screen."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        save_service: SaveService,
        on_finish: Callable[[], None]
    ):
        self.screen = screen
        self.game_state = game_state
        self.save_service = save_service
        self.on_finish = on_finish
        self.tutorial_service = TutorialService()
        self.sound_service = get_sound_service()

        self.anim_tick = 0

        # Navigation Buttons
        btn_y = 605
        self.btn_prev = AnimatedButton(60, btn_y, 130, 42, "← PREVIOUS", font_size=11, bg_color=(60, 50, 45), on_click=self._handle_prev)
        self.btn_next = AnimatedButton(730, btn_y, 140, 42, "NEXT STEP ➔", font_size=11, bg_color=ACCENT_GREEN, on_click=self._handle_next)
        self.btn_finish = AnimatedButton(730, btn_y, 140, 42, "START PLAYING ➔", font_size=11, bg_color=ACCENT_GREEN, on_click=self._handle_finish)
        self.btn_skip = AnimatedButton(910, btn_y, 130, 42, "SKIP TUTORIAL", font_size=11, bg_color=(80, 40, 35), on_click=self._handle_finish)

    def _handle_next(self) -> None:
        self.sound_service.play("click")
        self.tutorial_service.next_step()

    def _handle_prev(self) -> None:
        self.sound_service.play("click")
        self.tutorial_service.prev_step()

    def _handle_finish(self) -> None:
        self.sound_service.play("gavel")
        self.game_state.profile.tutorial_completed = True
        self.save_service.save_profile(self.game_state.profile)
        self.on_finish()

    def handle_events(self, events) -> None:
        for event in events:
            self.btn_skip.handle_event(event)
            if self.tutorial_service.current_step_index > 0:
                self.btn_prev.handle_event(event)

            if self.tutorial_service.current_step_index < self.tutorial_service.total_steps - 1:
                self.btn_next.handle_event(event)
            else:
                self.btn_finish.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_SPACE):
                    if self.tutorial_service.current_step_index < self.tutorial_service.total_steps - 1:
                        self._handle_next()
                    else:
                        self._handle_finish()
                elif event.key == pygame.K_LEFT:
                    if self.tutorial_service.current_step_index > 0:
                        self._handle_prev()
                elif event.key == pygame.K_ESCAPE:
                    self._handle_finish()

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.btn_prev.update(dt)
        self.btn_next.update(dt)
        self.btn_finish.update(dt)
        self.btn_skip.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Header Bar
        pygame.draw.rect(self.screen, WOOD_BROWN, (0, 0, SCREEN_WIDTH, 52))
        pygame.draw.line(self.screen, GOLD, (0, 52), (SCREEN_WIDTH, 52), 2)

        header_font = get_font(16, bold=True)
        h_surf = header_font.render("ACADEMY OF LAW — INTERACTIVE TUTORIAL", True, GOLD)
        self.screen.blit(h_surf, (30, 16))

        step_data = self.tutorial_service.current_step_data
        idx = self.tutorial_service.current_step_index
        tot = self.tutorial_service.total_steps

        step_ind_surf = get_font(12, bold=True).render(f"STAGE {idx + 1} OF {tot}", True, LIGHT_PARCHMENT)
        self.screen.blit(step_ind_surf, (SCREEN_WIDTH - step_ind_surf.get_width() - 30, 18))

        # Main Content Card
        card_rect = pygame.Rect(60, 75, SCREEN_WIDTH - 120, 510)
        pygame.draw.rect(self.screen, CARD_BG, card_rect, border_radius=10)
        pygame.draw.rect(self.screen, GOLD_LIGHT, card_rect, 1, border_radius=10)

        # Step Progress Pills
        pill_w = (card_rect.width - 40 - (tot - 1) * 8) // tot
        for i in range(tot):
            px = card_rect.x + 20 + i * (pill_w + 8)
            py = card_rect.y + 18
            p_rect = pygame.Rect(px, py, pill_w, 8)
            if i == idx:
                pygame.draw.rect(self.screen, GOLD, p_rect, border_radius=4)
            elif i < idx:
                pygame.draw.rect(self.screen, ACCENT_GREEN, p_rect, border_radius=4)
            else:
                pygame.draw.rect(self.screen, (55, 45, 40), p_rect, border_radius=4)

        # Step Title & Subtitle
        t_font = get_font(20, bold=True)
        t_surf = t_font.render(step_data["title"], True, GOLD)
        self.screen.blit(t_surf, (card_rect.x + 35, card_rect.y + 42))

        sub_font = get_font(13)
        sub_surf = sub_font.render(step_data["subtitle"], True, LIGHT_PARCHMENT)
        self.screen.blit(sub_surf, (card_rect.x + 35, card_rect.y + 72))

        # Two-column layout: Left = Description & Tip; Right = Visual Demonstration Graphic
        left_w = 460
        right_w = card_rect.width - left_w - 90
        left_x = card_rect.x + 35
        right_x = left_x + left_w + 20
        content_y = card_rect.y + 110

        # Description text
        desc_font = get_font(12)
        words = step_data["description"].split(" ")
        lines = []
        cur_line = []
        for w in words:
            if "\n" in w:
                parts = w.split("\n")
                cur_line.append(parts[0])
                lines.append(" ".join(cur_line))
                cur_line = [parts[1]] if len(parts) > 1 else []
            else:
                test_line = " ".join(cur_line + [w])
                if desc_font.size(test_line)[0] > left_w:
                    lines.append(" ".join(cur_line))
                    cur_line = [w]
                else:
                    cur_line.append(w)
        if cur_line:
            lines.append(" ".join(cur_line))

        dy = content_y
        for line in lines:
            line_surf = desc_font.render(line, True, WHITE)
            self.screen.blit(line_surf, (left_x, dy))
            dy += 24

        # Key Takeaway Box
        tip_rect = pygame.Rect(left_x, card_rect.bottom - 110, left_w, 75)
        pygame.draw.rect(self.screen, (40, 48, 38), tip_rect, border_radius=6)
        pygame.draw.rect(self.screen, ACCENT_GREEN, tip_rect, 1, border_radius=6)

        tip_font = get_font(11, bold=True)
        tip_lines = step_data["key_takeaway"].split("Key Tip:")
        self.screen.blit(tip_font.render("LEGAL PRINCIPLE:", True, ACCENT_GREEN), (tip_rect.x + 12, tip_rect.y + 10))

        tip_text = tip_lines[1].strip() if len(tip_lines) > 1 else step_data["key_takeaway"]
        tip_body_font = get_font(11)
        # Wrap tip text
        t_words = tip_text.split(" ")
        t_lines = []
        t_cur = []
        for tw in t_words:
            if tip_body_font.size(" ".join(t_cur + [tw]))[0] > (tip_rect.width - 24):
                t_lines.append(" ".join(t_cur))
                t_cur = [tw]
            else:
                t_cur.append(tw)
        if t_cur:
            t_lines.append(" ".join(t_cur))

        ty = tip_rect.y + 30
        for tl in t_lines:
            self.screen.blit(tip_body_font.render(tl, True, LIGHT_PARCHMENT), (tip_rect.x + 12, ty))
            ty += 18

        # Right Graphic Panel
        demo_rect = pygame.Rect(right_x, content_y - 10, right_w, 370)
        pygame.draw.rect(self.screen, (30, 22, 18), demo_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 75, 55), demo_rect, 1, border_radius=8)

        self._draw_step_demonstration(demo_rect, idx)

        # Draw Bottom Action Buttons
        if idx > 0:
            self.btn_prev.draw(self.screen)
        if idx < tot - 1:
            self.btn_next.draw(self.screen)
        else:
            self.btn_finish.draw(self.screen)
        self.btn_skip.draw(self.screen)

    def _draw_step_demonstration(self, rect: pygame.Rect, step_idx: int) -> None:
        """Renders rich procedural visual infographics for each tutorial step."""
        cx = rect.centerx
        cy = rect.centery

        pulse = (math.sin(self.anim_tick * 0.05) + 1.0) * 0.5
        font_s = get_font(11)
        font_b = get_font(12, bold=True)

        if step_idx == 0:  # Understand Case Briefing
            d_rect = pygame.Rect(cx - 140, cy - 130, 280, 260)
            pygame.draw.rect(self.screen, (45, 36, 30), d_rect, border_radius=6)
            pygame.draw.rect(self.screen, GOLD, d_rect, 1, border_radius=6)
            self.screen.blit(font_b.render("OFFICIAL POLICE DOSSIER", True, GOLD), (d_rect.x + 35, d_rect.y + 16))
            pygame.draw.line(self.screen, GOLD_LIGHT, (d_rect.x + 20, d_rect.y + 40), (d_rect.right - 20, d_rect.y + 40), 1)

            self.screen.blit(font_s.render("INCIDENT: Midnight Homicide", True, WHITE), (d_rect.x + 20, d_rect.y + 55))
            self.screen.blit(font_s.render("LOCATION: Vance Manor Study", True, WHITE), (d_rect.x + 20, d_rect.y + 85))
            self.screen.blit(font_s.render("SUSPECTS: 4 Persons Present", True, WHITE), (d_rect.x + 20, d_rect.y + 115))

            obj_box = pygame.Rect(d_rect.x + 15, d_rect.y + 155, d_rect.width - 30, 80)
            pygame.draw.rect(self.screen, (25, 20, 15), obj_box, border_radius=4)
            self.screen.blit(font_b.render("PRIMARY OBJECTIVE:", True, ACCENT_GREEN), (obj_box.x + 10, obj_box.y + 10))
            self.screen.blit(font_s.render("Prove beyond reasonable doubt", True, LIGHT_PARCHMENT), (obj_box.x + 10, obj_box.y + 32))
            self.screen.blit(font_s.render("that Suspect committed crime.", True, LIGHT_PARCHMENT), (obj_box.x + 10, obj_box.y + 52))

        elif step_idx == 1:  # Crime Scene
            # Magnifying glass on hotspot
            hs_rect = pygame.Rect(cx - 70, cy - 70, 140, 140)
            pygame.draw.rect(self.screen, (50, 40, 30), hs_rect, border_radius=8)
            glow_col = (int(180 + 75 * pulse), int(140 + 60 * pulse), 40)
            pygame.draw.rect(self.screen, glow_col, hs_rect, 2, border_radius=8)

            self.screen.blit(get_font(28).render("🔍", True, WHITE), (cx - 18, cy - 50))
            self.screen.blit(font_b.render("Bloody Chef Knife", True, GOLD), (cx - 60, cy + 5))
            self.screen.blit(font_s.render("[Click to Inspect]", True, LIGHT_PARCHMENT), (cx - 50, cy + 30))

            # Inspect vs Collect pill
            pill = pygame.Rect(cx - 120, cy + 100, 240, 36)
            pygame.draw.rect(self.screen, ACCENT_GREEN, pill, border_radius=6)
            self.screen.blit(font_b.render("COLLECT EVIDENCE ➔", True, WHITE), (pill.x + 35, pill.y + 8))

        elif step_idx == 2:  # Suspects & Contradictions
            s_box = pygame.Rect(cx - 130, cy - 130, 260, 120)
            pygame.draw.rect(self.screen, (40, 30, 25), s_box, border_radius=6)
            pygame.draw.rect(self.screen, GOLD_LIGHT, s_box, 1, border_radius=6)
            self.screen.blit(font_b.render("SUSPECT ALIBI:", True, GOLD), (s_box.x + 15, s_box.y + 12))
            self.screen.blit(font_s.render('"I was at the cinema downtown!"', True, WHITE), (s_box.x + 15, s_box.y + 38))

            c_box = pygame.Rect(cx - 130, cy + 15, 260, 120)
            pygame.draw.rect(self.screen, (60, 25, 25), c_box, border_radius=6)
            pygame.draw.rect(self.screen, ACCENT_RED, c_box, 1, border_radius=6)
            self.screen.blit(font_b.render("PHYSICAL CONTRADICTION ⚡", True, ACCENT_RED), (c_box.x + 15, c_box.y + 12))
            self.screen.blit(font_s.render("CCTV camera records suspect", True, LIGHT_PARCHMENT), (c_box.x + 15, c_box.y + 38))
            self.screen.blit(font_s.render("entering mansion at 11:50 PM.", True, LIGHT_PARCHMENT), (c_box.x + 15, c_box.y + 60))

        elif step_idx == 3:  # Collect & Analyze Evidence
            e_box = pygame.Rect(cx - 130, cy - 120, 260, 240)
            pygame.draw.rect(self.screen, (35, 30, 40), e_box, border_radius=6)
            pygame.draw.rect(self.screen, ACCENT_BLUE, e_box, 1, border_radius=6)
            self.screen.blit(font_b.render("FORENSIC EVIDENCE", True, ACCENT_BLUE), (e_box.x + 15, e_box.y + 15))
            self.screen.blit(font_s.render("Name: Autopsy Medical Report", True, WHITE), (e_box.x + 15, e_box.y + 45))
            self.screen.blit(font_s.render("Reliability: 100% (Conclusive)", True, ACCENT_GREEN), (e_box.x + 15, e_box.y + 75))

            f_box = pygame.Rect(e_box.x + 12, e_box.y + 110, e_box.width - 24, 100)
            pygame.draw.rect(self.screen, (20, 20, 30), f_box, border_radius=4)
            self.screen.blit(font_b.render("UNLOCKED PROPOSITIONS:", True, GOLD), (f_box.x + 8, f_box.y + 8))
            self.screen.blit(font_s.render("• victim_cause_of_death_stab", True, LIGHT_PARCHMENT), (f_box.x + 8, f_box.y + 32))
            self.screen.blit(font_s.render("• time_of_death_midnight", True, LIGHT_PARCHMENT), (f_box.x + 8, f_box.y + 56))

        elif step_idx == 4:  # Build Logical Argument
            # Syllogism tree
            p1 = pygame.Rect(cx - 130, cy - 120, 260, 45)
            p2 = pygame.Rect(cx - 130, cy - 65, 260, 45)
            c = pygame.Rect(cx - 130, cy + 35, 260, 60)

            pygame.draw.rect(self.screen, (40, 35, 30), p1, border_radius=4)
            pygame.draw.rect(self.screen, (40, 35, 30), p2, border_radius=4)
            pygame.draw.rect(self.screen, (30, 50, 35), c, border_radius=6)
            pygame.draw.rect(self.screen, ACCENT_GREEN, c, 1, border_radius=6)

            self.screen.blit(font_s.render("PREMISE 1: Fingerprints on knife", True, WHITE), (p1.x + 10, p1.y + 12))
            self.screen.blit(font_s.render("PREMISE 2: Prints match Victor", True, WHITE), (p2.x + 10, p2.y + 12))

            pygame.draw.line(self.screen, GOLD, (cx, cy - 15), (cx, cy + 30), 2)
            self.screen.blit(font_b.render("CONCLUSION (DEDUCTION):", True, ACCENT_GREEN), (c.x + 10, c.y + 8))
            self.screen.blit(font_s.render("Victor had contact with weapon.", True, LIGHT_PARCHMENT), (c.x + 10, c.y + 30))

        elif step_idx == 5:  # Enter Courtroom
            court_box = pygame.Rect(cx - 130, cy - 120, 260, 240)
            pygame.draw.rect(self.screen, (45, 25, 25), court_box, border_radius=6)
            pygame.draw.rect(self.screen, GOLD, court_box, 1, border_radius=6)

            self.screen.blit(font_b.render("AI JUDGE HEARING", True, GOLD), (court_box.x + 15, court_box.y + 15))
            self.screen.blit(font_s.render('Judge: "Present your reasoning."', True, LIGHT_PARCHMENT), (court_box.x + 15, court_box.y + 50))
            self.screen.blit(font_s.render('Lawyer: "CCTV refutes the alibi."', True, WHITE), (court_box.x + 15, court_box.y + 85))

            eval_box = pygame.Rect(court_box.x + 12, court_box.y + 125, court_box.width - 24, 95)
            pygame.draw.rect(self.screen, (20, 15, 15), eval_box, border_radius=4)
            self.screen.blit(font_b.render("AI INFERENCE ENGINE:", True, ACCENT_GREEN), (eval_box.x + 8, eval_box.y + 8))
            self.screen.blit(font_s.render("Forward Chaining: 100% Match", True, LIGHT_PARCHMENT), (eval_box.x + 8, eval_box.y + 32))
            self.screen.blit(font_s.render("Resolution: Sound Derivation", True, LIGHT_PARCHMENT), (eval_box.x + 8, eval_box.y + 56))

        elif step_idx == 6:  # Verdicts
            v_box = pygame.Rect(cx - 130, cy - 120, 260, 240)
            pygame.draw.rect(self.screen, (30, 25, 20), v_box, border_radius=6)
            pygame.draw.rect(self.screen, GOLD, v_box, 1, border_radius=6)

            r1 = pygame.Rect(v_box.x + 15, v_box.y + 20, v_box.width - 30, 55)
            r2 = pygame.Rect(v_box.x + 15, v_box.y + 88, v_box.width - 30, 55)
            r3 = pygame.Rect(v_box.x + 15, v_box.y + 156, v_box.width - 30, 55)

            pygame.draw.rect(self.screen, (30, 55, 30), r1, border_radius=4)
            pygame.draw.rect(self.screen, (55, 45, 25), r2, border_radius=4)
            pygame.draw.rect(self.screen, (55, 25, 25), r3, border_radius=4)

            self.screen.blit(font_b.render("✓ SUPPORTED", True, ACCENT_GREEN), (r1.x + 10, r1.y + 8))
            self.screen.blit(font_s.render("Deduction logically proven.", True, LIGHT_PARCHMENT), (r1.x + 10, r1.y + 28))

            self.screen.blit(font_b.render("? NOT PROVEN", True, GOLD), (r2.x + 10, r2.y + 8))
            self.screen.blit(font_s.render("Plausible but insufficient facts.", True, LIGHT_PARCHMENT), (r2.x + 10, r2.y + 28))

            self.screen.blit(font_b.render("✗ CONTRADICTED", True, ACCENT_RED), (r3.x + 10, r3.y + 8))
            self.screen.blit(font_s.render("Refuted by rules or evidence.", True, LIGHT_PARCHMENT), (r3.x + 10, r3.y + 28))
