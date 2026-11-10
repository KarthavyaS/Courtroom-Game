"""Case Briefing Screen for LOGIC COURTROOM.
Presents an official detective dossier narrative before stepping into the crime scene.
Explains What Happened, Where, When, Who is Involved, Known Facts, and the Target Legal Objective.
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
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.navigation_bar import NavigationBar

class CaseBriefing:
    """Classified police briefing and narrative breakdown."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        on_nav_dashboard: Callable[[], None],
        on_enter_crime_scene: Callable[[], None],
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
        self.on_enter_crime_scene = on_enter_crime_scene
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service()

        self.anim_tick = 0

        # Mark briefing read in progress
        self.game_state.progress.mark_briefing_read()
        self.save_service.save_active_game(self.game_state)

        # Top Navigation Bar
        self.nav_bar = NavigationBar(
            current_stage="briefing",
            game_state=self.game_state,
            on_nav_dashboard=self.on_nav_dashboard,
            on_nav_briefing=None,
            on_nav_scene=self.on_enter_crime_scene,
            on_nav_suspects=on_nav_suspects,
            on_nav_evidence=on_nav_evidence,
            on_nav_board=on_nav_board,
            on_nav_notebook=on_nav_notebook,
            on_nav_arguments=on_nav_arguments,
            on_nav_courtroom=on_nav_courtroom
        )

        # Primary Action Button
        self.btn_enter_scene = AnimatedButton(
            SCREEN_WIDTH - 300, SCREEN_HEIGHT - 65, 260, 44,
            "ENTER CRIME SCENE ➔", font_size=12, bg_color=ACCENT_GREEN,
            on_click=self._handle_enter_scene
        )

    def _handle_enter_scene(self) -> None:
        self.sound_service.play("click")
        self.on_enter_crime_scene()

    def handle_events(self, events) -> None:
        self.nav_bar.handle_events(events)
        for event in events:
            self.btn_enter_scene.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._handle_enter_scene()

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.nav_bar.update(dt)
        self.btn_enter_scene.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)

        # Navigation Bar
        self.nav_bar.draw(self.screen)

        case = self.game_state.current_case
        if not case:
            return

        # Main Dossier Card
        card_w = SCREEN_WIDTH - 80
        card_h = SCREEN_HEIGHT - 145
        card_x = 40
        card_y = 68
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(self.screen, CARD_BG, card_rect, border_radius=8)
        pygame.draw.rect(self.screen, GOLD_LIGHT, card_rect, 1, border_radius=8)

        # Header Title
        h_font = get_font(18, bold=True)
        title_text = f"CASE BRIEFING: {case.id} — {case.title.upper()}"
        self.screen.blit(h_font.render(title_text, True, GOLD), (card_x + 24, card_y + 18))

        sub_font = get_font(11)
        sub_txt = f"Classification: {case.type} • Priority: {case.difficulty} • Reward: £{case.reward}"
        self.screen.blit(sub_font.render(sub_txt, True, LIGHT_PARCHMENT), (card_x + 24, card_y + 44))

        # 3-Card Layout
        c1_w = 320
        c2_w = 320
        c3_w = card_w - c1_w - c2_w - 56
        panel_y = card_y + 72
        panel_h = card_h - 90

        # Panel 1: What, Where & When Happened
        p1 = pygame.Rect(card_x + 20, panel_y, c1_w, panel_h)
        pygame.draw.rect(self.screen, (35, 28, 24), p1, border_radius=6)
        pygame.draw.rect(self.screen, (80, 60, 50), p1, 1, border_radius=6)

        self.screen.blit(get_font(12, bold=True).render("1. INCIDENT REPORT", True, GOLD), (p1.x + 14, p1.y + 14))

        # Incident narrative
        desc_font = get_font(11)
        words = case.description.split(" ")
        lines = []
        cur = []
        for w in words:
            if desc_font.size(" ".join(cur + [w]))[0] > (c1_w - 28):
                lines.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(" ".join(cur))

        dy = p1.y + 42
        for l in lines:
            self.screen.blit(desc_font.render(l, True, WHITE), (p1.x + 14, dy))
            dy += 20

        dy += 15
        self.screen.blit(get_font(11, bold=True).render("INCIDENT LOCATION:", True, LIGHT_PARCHMENT), (p1.x + 14, dy))
        dy += 18
        self.screen.blit(get_font(11).render(f"• {case.scene_name}", True, WHITE), (p1.x + 14, dy))
        dy += 26
        self.screen.blit(get_font(11, bold=True).render("INITIAL DISPATCH:", True, LIGHT_PARCHMENT), (p1.x + 14, dy))
        dy += 18
        self.screen.blit(get_font(11).render("• Emergency response at 00:15 AM", True, WHITE), (p1.x + 14, dy))
        dy += 18
        self.screen.blit(get_font(11).render("• Crime scene secured by detectives", True, WHITE), (p1.x + 14, dy))

        # Panel 2: Who is Involved? (Suspects)
        p2 = pygame.Rect(p1.right + 14, panel_y, c2_w, panel_h)
        pygame.draw.rect(self.screen, (35, 28, 24), p2, border_radius=6)
        pygame.draw.rect(self.screen, (80, 60, 50), p2, 1, border_radius=6)

        self.screen.blit(get_font(12, bold=True).render(f"2. PERSONS OF INTEREST ({len(case.suspects)})", True, GOLD), (p2.x + 14, p2.y + 14))

        sy = p2.y + 42
        for s in case.suspects[:4]:
            s_box = pygame.Rect(p2.x + 10, sy, p2.width - 20, 52)
            pygame.draw.rect(self.screen, (28, 22, 18), s_box, border_radius=4)
            self.screen.blit(get_font(11, bold=True).render(s.name, True, WHITE), (s_box.x + 8, s_box.y + 6))
            self.screen.blit(get_font(10).render(f"{s.occupation} • {s.relationship}", True, LIGHT_PARCHMENT), (s_box.x + 8, s_box.y + 26))
            sy += 58

        # Panel 3: Objectives & Initial Known Facts
        p3 = pygame.Rect(p2.right + 14, panel_y, c3_w, panel_h)
        pygame.draw.rect(self.screen, (35, 28, 24), p3, border_radius=6)
        pygame.draw.rect(self.screen, (80, 60, 50), p3, 1, border_radius=6)

        self.screen.blit(get_font(12, bold=True).render("3. LEGAL OBJECTIVE", True, GOLD), (p3.x + 14, p3.y + 14))

        # Objective box
        obj_rect = pygame.Rect(p3.x + 10, p3.y + 40, p3.width - 20, 110)
        pygame.draw.rect(self.screen, (35, 45, 35), obj_rect, border_radius=6)
        pygame.draw.rect(self.screen, ACCENT_GREEN, obj_rect, 1, border_radius=6)

        self.screen.blit(get_font(11, bold=True).render("CLAIM TO PROVE IN COURT:", True, ACCENT_GREEN), (obj_rect.x + 10, obj_rect.y + 10))
        self.screen.blit(get_font(11, bold=True).render(f"'{case.solution_conclusion}'", True, WHITE), (obj_rect.x + 10, obj_rect.y + 34))
        self.screen.blit(get_font(10).render("Build deductive premises from evidence.", True, LIGHT_PARCHMENT), (obj_rect.x + 10, obj_rect.y + 64))
        self.screen.blit(get_font(10).render("Refute false statements with CCTV/forensics.", True, LIGHT_PARCHMENT), (obj_rect.x + 10, obj_rect.y + 84))

        # Initial Known Facts
        fy = obj_rect.bottom + 16
        self.screen.blit(get_font(11, bold=True).render("INITIAL KNOWN FACTS:", True, GOLD), (p3.x + 14, fy))
        fy += 24
        for fact in case.initial_facts:
            clean_fact = fact.replace("_", " ").title()
            self.screen.blit(get_font(10).render(f"• {clean_fact}", True, LIGHT_PARCHMENT), (p3.x + 14, fy))
            fy += 20

        # Draw Bottom Action Button
        self.btn_enter_scene.draw(self.screen)
