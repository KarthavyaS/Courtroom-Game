"""Create Case Screen for LOGIC COURTROOM.
Allows players to author, validate, and publish custom fictional investigation cases
with responsive layout for 1100x680 resolution.
"""
#pyright: ignore
import pygame
import uuid
from typing import Callable, Optional, List
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, get_font
)
from models.case import Case
from models.suspect import Suspect
from models.evidence import Evidence
from services.case_service import CaseService
from services.game_state import GameState
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.text_box import TextBox

class CreateCase:
    """Screen for creating and publishing custom courtroom cases."""

    def __init__(
        self,
        screen: pygame.Surface,
        case_service: CaseService,
        game_state: GameState,
        on_back: Callable[[], None],
        on_case_created: Callable[[Case], None]
    ):
        self.screen = screen
        self.case_service = case_service
        self.game_state = game_state
        self.on_back = on_back
        self.on_case_created = on_case_created
        self.sound_service = get_sound_service()

        self.btn_back = AnimatedButton(30, 18, 100, 36, "← BACK", font_size=12, on_click=self.on_back)
        self.btn_save = AnimatedButton(SCREEN_WIDTH - 250, 18, 220, 36, "SAVE & PUBLISH CASE ➔", font_size=12, bg_color=ACCENT_GREEN, on_click=self._save_case)

        # Form Fields - 1100x680 Layout
        # Row 1: Title, Type, Difficulty
        self.tb_title = TextBox(30, 95, 480, 36, placeholder="Case Title (e.g., The Manor Mystery)...", font_size=13)
        self.tb_type = TextBox(530, 95, 270, 36, placeholder="Type (e.g. Theft, Murder)...", font_size=13, initial_text="Theft Investigation")
        self.tb_diff = TextBox(820, 95, 250, 36, placeholder="Difficulty (EASY/MED/HARD)...", font_size=13, initial_text="MEDIUM")

        # Row 2: Description
        self.tb_desc = TextBox(30, 155, 1040, 54, placeholder="Case Description & Background Story...", font_size=12, is_multiline=True)

        # Row 3: Suspects (Two columns)
        self.tb_s1_name = TextBox(30, 255, 230, 34, placeholder="Suspect 1 Name...", font_size=12, initial_text="Lord Reginald")
        self.tb_s1_stmt = TextBox(30, 298, 490, 52, placeholder="Suspect 1 Statement & Alibi...", font_size=11, is_multiline=True, initial_text="I was in the cellar all evening tasting vintage wines.")

        self.tb_s2_name = TextBox(550, 255, 230, 34, placeholder="Suspect 2 Name...", font_size=12, initial_text="Lady Beatrice")
        self.tb_s2_stmt = TextBox(550, 298, 490, 52, placeholder="Suspect 2 Statement & Alibi...", font_size=11, is_multiline=True, initial_text="I was in the drawing room reading under the gaslight.")

        # Row 4: Evidence (Two columns)
        self.tb_e1_name = TextBox(30, 395, 230, 34, placeholder="Evidence 1 Name...", font_size=12, initial_text="Stained Glove")
        self.tb_e1_desc = TextBox(30, 438, 490, 52, placeholder="Evidence 1 Forensic Description...", font_size=11, is_multiline=True, initial_text="Silk glove matching Reginald found by the unlocked window.")

        self.tb_e2_name = TextBox(550, 395, 230, 34, placeholder="Evidence 2 Name...", font_size=12, initial_text="Broken Lock")
        self.tb_e2_desc = TextBox(550, 438, 490, 52, placeholder="Evidence 2 Forensic Description...", font_size=11, is_multiline=True, initial_text="Lock picked cleanly from outside without structural damage.")

        self.text_boxes = [
            self.tb_title, self.tb_type, self.tb_diff, self.tb_desc,
            self.tb_s1_name, self.tb_s1_stmt,
            self.tb_s2_name, self.tb_s2_stmt,
            self.tb_e1_name, self.tb_e1_desc,
            self.tb_e2_name, self.tb_e2_desc
        ]

    def _save_case(self):
        title = self.tb_title.get_text().strip()
        case_type = self.tb_type.get_text().strip() or "Custom Investigation"
        diff = self.tb_diff.get_text().strip().upper()
        if diff not in ["EASY", "MEDIUM", "HARD"]:
            diff = "MEDIUM"
        desc = self.tb_desc.get_text().strip()

        s1_name = self.tb_s1_name.get_text().strip()
        s1_stmt = self.tb_s1_stmt.get_text().strip()
        s2_name = self.tb_s2_name.get_text().strip()
        s2_stmt = self.tb_s2_stmt.get_text().strip()

        e1_name = self.tb_e1_name.get_text().strip()
        e1_desc = self.tb_e1_desc.get_text().strip()
        e2_name = self.tb_e2_name.get_text().strip()
        e2_desc = self.tb_e2_desc.get_text().strip()

        if not title:
            self.game_state.set_notification("Please enter a Case Title!", category="WARNING")
            return
        if not desc:
            self.game_state.set_notification("Please provide a Case Description!", category="WARNING")
            return
        if not s1_name or not s2_name:
            self.game_state.set_notification("Please provide at least two suspects!", category="WARNING")
            return
        if not e1_name or not e2_name:
            self.game_state.set_notification("Please provide at least two evidence items!", category="WARNING")
            return

        new_id = f"CASE-{uuid.uuid4().hex[:4].upper()}"

        suspects = [
            Suspect(
                id="SUS-001",
                name=s1_name,
                occupation="Custom Role",
                relationship="Associate",
                motive="Custom motive for investigation.",
                alibi=s1_stmt,
                statement=s1_stmt,
                known_facts=["suspect_1_present"],
                contradictions=[],
                avatar_type="partner",
                is_guilty=True
            ),
            Suspect(
                id="SUS-002",
                name=s2_name,
                occupation="Witness Role",
                relationship="Colleague",
                motive="Secondary motive.",
                alibi=s2_stmt,
                statement=s2_stmt,
                known_facts=["suspect_2_present"],
                contradictions=[],
                avatar_type="heir",
                is_guilty=False
            )
        ]

        evidence_list = [
            Evidence(
                id="EVD-001",
                name=e1_name,
                description=e1_desc,
                category="Physical",
                reliability=0.9,
                relevance=0.85,
                collected=False,
                scene_pos=[320, 260, 60, 60],
                icon_type="glass",
                facts_unlocked=["evidence_1_verified"],
                details=e1_desc
            ),
            Evidence(
                id="EVD-002",
                name=e2_name,
                description=e2_desc,
                category="Direct",
                reliability=0.85,
                relevance=0.9,
                collected=False,
                scene_pos=[550, 360, 60, 60],
                icon_type="document",
                facts_unlocked=["evidence_2_verified"],
                details=e2_desc
            )
        ]

        new_case = Case(
            id=new_id,
            title=title,
            type=case_type,
            description=desc,
            difficulty=diff,
            reward=300,
            scene_name="Custom Manor Chamber",
            scene_type="manor",
            solution_suspect_id="SUS-001",
            solution_conclusion="suspect_guilty_beyond_reasonable_doubt",
            solution_summary=f"Accused {s1_name} was proven guilty by forensic connections.",
            suspects=suspects,
            evidence_list=evidence_list,
            initial_facts=["crime_committed", "suspect_1_present"],
            rules=[]
        )

        success = self.case_service.create_case(new_case)
        if success:
            self.sound_service.play("evidence")
            self.game_state.set_notification(f"Case '{title}' created and published successfully!", category="SUCCESS")
            self.on_case_created(new_case)
        else:
            self.game_state.set_notification("Failed to save custom case to disk.", category="ERROR")

    def handle_events(self, events):
        for event in events:
            self.btn_back.handle_event(event)
            self.btn_save.handle_event(event)
            for tb in self.text_boxes:
                tb.handle_event(event)

    def update(self, dt: float = 0.016):
        self.btn_back.update(dt)
        self.btn_save.update(dt)

    def draw(self):
        self.screen.fill(BACKGROUND)

        # Header Bar
        pygame.draw.rect(self.screen, WOOD_BROWN, (0, 0, SCREEN_WIDTH, 62))
        pygame.draw.line(self.screen, GOLD, (0, 62), (SCREEN_WIDTH, 62), 2)

        self.btn_back.draw(self.screen)
        self.btn_save.draw(self.screen)

        t_surf = get_font(18, bold=True).render("AUTHOR NEW INVESTIGATION CASE", True, GOLD)
        self.screen.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 31)))

        # Section Labels
        font_sec = get_font(11, bold=True)
        self.screen.blit(font_sec.render("CASE DOSSIER & PARTICULARS:", True, GOLD), (30, 75))
        self.screen.blit(font_sec.render("CASE BACKGROUND NARRATIVE:", True, GOLD), (30, 137))
        self.screen.blit(font_sec.render("PERSONS OF INTEREST & SWORN STATEMENTS:", True, GOLD), (30, 233))
        self.screen.blit(font_sec.render("CRIME SCENE FORENSIC EVIDENCE:", True, GOLD), (30, 373))

        for tb in self.text_boxes:
            tb.draw(self.screen)
