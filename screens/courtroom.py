"""Interactive, Fully Animated AI Courtroom Trial Screen for LOGIC COURTROOM.
Features an uncluttered, spacious stage layout tailored for 1100x680 resolution:
- Elevated central bench for AI Magistrate
- Left-side Advocate podium with listening & speaking animations
- Right-side Suspect Dock with illuminated circular Suspect Ring
- Spacious typewriter dialogue box with generous padding
- Streamlined pleading console and quick forensic exhibits
- Courtroom Discipline Warning Meter
"""
#pyright: ignore
import pygame
import math
from typing import Callable, Optional, Dict, Any, List
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, GOLD_DARK, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, ACCENT_ORANGE, get_font
)
from models.argument import Argument
from models.suspect import Suspect
from models.evidence import Evidence
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from services.courtroom_session import CourtroomSession
from components.character_sprite import CharacterSprite
from components.suspect_ring import SuspectRing
from components.dialogue_box import DialogueBox
from components.animated_button import AnimatedButton
from components.text_box import TextBox
from components.animation import (
    ParticleSystem, ScreenShake, ObjectionBanner, VolumetricLightRays, ScalesOfJustice,
    CrowdMurmur, CourtroomChandelier, CourtroomGallery, CredibilityHeartbeatGauge, WaxSealStamp
)
from ai_engine.scoring import ScoringEngine

class Courtroom:
    """The animated interactive AI Judge Courtroom trial chamber with dynamic motion and combat effects."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        save_service: SaveService,
        on_navigate_case_file: Optional[Callable[[], None]] = None,
        on_navigate_crime_scene: Optional[Callable[[], None]] = None,
        on_navigate_suspects: Optional[Callable[[], None]] = None,
        on_navigate_evidence: Optional[Callable[[], None]] = None,
        on_navigate_arguments: Optional[Callable[[], None]] = None,
        on_case_selection: Optional[Callable[[], None]] = None,
        on_view_leaderboard: Optional[Callable[[], None]] = None,
        on_view_results: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.screen = screen
        self.game_state = game_state
        self.save_service = save_service
        self.sound_service = get_sound_service()

        # Navigation callbacks
        self.on_nav_case_file = on_navigate_case_file
        self.on_nav_crime_scene = on_navigate_crime_scene
        self.on_nav_suspects = on_navigate_suspects
        self.on_nav_evidence = on_navigate_evidence
        self.on_nav_arguments = on_navigate_arguments
        self.on_case_selection = on_case_selection
        self.on_view_leaderboard = on_view_leaderboard
        self.on_view_results = on_view_results

        # Core Trial Session & AI
        self.session: Optional[CourtroomSession] = None
        self.scoring_engine = ScoringEngine()
        self.evaluation_result: Optional[Dict[str, Any]] = None
        self.is_trial_concluded = False
        self.score_saved = False

        # Interactive Jury & Composure Dynamics
        self.jury_persuasion = 50.0  # 0 to 100%
        self.suspect_composure = 100.0  # 100% down to 0%
        self.logic_combo = 0
        self.screen_shake = ScreenShake()
        self.objection_banner = ObjectionBanner()
        self.watson_hint_message: Optional[str] = None
        self.watson_hint_timer = 0.0

        # Live Background Atmospheric Motion
        self.light_rays = VolumetricLightRays()
        self.scales_of_justice = ScalesOfJustice(x=550, y=46)
        self.crowd_murmur = CrowdMurmur()
        self.chandelier_left = CourtroomChandelier(x=220, y=44, length=55, swing_speed=1.1, phase=0.0)
        self.chandelier_right = CourtroomChandelier(x=880, y=44, length=55, swing_speed=0.9, phase=1.5)
        self.gallery = CourtroomGallery(start_x=240, start_y=46, count=7)
        self.discipline_gauge = CredibilityHeartbeatGauge(x=680, y=58, width=175, height=52)
        self.wax_seal = WaxSealStamp()

        # Floating Combat Numbers (Damage / Jury swing / Combos)
        self.floating_popups: List[Dict[str, Any]] = []

        # Interactive Cross-Examination Mode State
        self.testimony_statements: List[str] = []
        self.current_testimony_idx = 0
        self.show_evidence_tray = False

        # Visual Entities & Animated Sprites
        self.judge_sprite = CharacterSprite(character_type="judge", name="AI Magistrate")
        self.lawyer_sprite = CharacterSprite(character_type=self.game_state.profile.avatar_id or "lawyer", name=self.game_state.profile.name)
        self.suspect_sprite = CharacterSprite(character_type="heir", name="Suspect")
        self.suspect_ring = SuspectRing(center_x=960, center_y=180, radius_x=65, radius_y=22)

        # Dialogue Component (Roomy, Clean & Centered with Zero Overlap)
        self.dialogue_box = DialogueBox(pygame.Rect(50, 235, 1000, 145))

        # Ambient Particles
        self.particles = ParticleSystem(max_particles=30)
        self.anim_time = 0.0
        self.gavel_slam_timer = 0.0

        # Interactive Cross-Examination Action Buttons
        self.btn_prev_stmt = AnimatedButton(
            x=50, y=390, width=125, height=40,
            text="◀ PREV [Q]", font_size=13, bg_color=(50, 40, 35),
            tooltip="Cycle to previous witness statement (Q or Left Arrow)",
            on_click=self._prev_statement
        )
        self.btn_next_stmt = AnimatedButton(
            x=180, y=390, width=125, height=40,
            text="NEXT ▶ [W]", font_size=13, bg_color=(50, 40, 35),
            tooltip="Cycle to next witness statement (W or Right Arrow)",
            on_click=self._next_statement
        )
        self.btn_submit_reading = AnimatedButton(
            x=310, y=390, width=245, height=40,
            text="📖 SUBMIT FOR READING [SPACE]", font_size=13, bg_color=(140, 95, 30),
            border_color=(255, 215, 100),
            tooltip="Submit active statement to the court record for cross-examination scrutiny! (Space)",
            on_click=self._submit_statement_for_reading
        )
        self.btn_press_witness = AnimatedButton(
            x=560, y=390, width=180, height=40,
            text="⚡ PRESS WITNESS [P]", font_size=13, bg_color=(125, 75, 35),
            border_color=(255, 200, 100),
            tooltip="Press the suspect for details and shake their composure (P)",
            on_click=self._press_current_statement
        )
        self.btn_objection = AnimatedButton(
            x=745, y=390, width=155, height=40,
            text="💥 OBJECTION! [O]", font_size=13, bg_color=(175, 45, 30),
            border_color=(255, 150, 120),
            tooltip="Interject with dramatic contradiction evidence! (O)",
            on_click=self._trigger_objection
        )
        self.btn_rest_case = AnimatedButton(
            x=905, y=390, width=145, height=40,
            text="⚖ DEMAND VERDICT", font_size=13, bg_color=ACCENT_GREEN,
            tooltip="Conclude trial pleadings and request final judgment (R)",
            on_click=self._conclude_trial
        )

        # Tactical Watson Hint
        self.btn_watson_hint = AnimatedButton(
            x=895, y=565, width=155, height=34,
            text="💡 WATSON HINT [H]",
            font_size=12,
            bg_color=(40, 85, 130),
            border_color=(120, 190, 255),
            tooltip="Consult Clerk Watson on missing legal pillars (H)",
            on_click=self._trigger_watson_hint
        )

        # Top Navigation Bar Buttons
        self.nav_buttons: List[AnimatedButton] = []
        self._init_top_nav()

        # Permanent Evidence Court Record Buttons (Directly below testimony)
        self.evidence_court_buttons: List[AnimatedButton] = []
        self.evidence_page = 0

        # Concluded / Terminated Buttons
        self.btn_view_results = AnimatedButton(50, 580, 230, 44, "📜 VIEW RESULTS & METRICS", 14, bg_color=ACCENT_GREEN, on_click=self._on_click_view_results)
        self.btn_save_score = AnimatedButton(300, 580, 230, 44, "★ RECORD SCORE", 14, bg_color=ACCENT_BLUE, on_click=self._save_score)
        self.btn_restart_hearing = AnimatedButton(550, 580, 230, 44, "↺ RESTART HEARING", 14, bg_color=(160, 60, 40), on_click=self._restart_hearing)
        self.btn_next_case = AnimatedButton(800, 580, 250, 44, "SELECT NEXT CASE ➔", 14, bg_color=WOOD_BROWN, on_click=self._on_click_next_case)
        self.btn_leaderboard = AnimatedButton(800, 580, 250, 44, "VIEW LEADERBOARD", 14, bg_color=WOOD_BROWN, on_click=self._on_click_leaderboard)

        # Initialize session with current case & suspect
        self._refresh_session()

    def _init_top_nav(self):
        nav_items = [
            ("CASE FILE", self.on_nav_case_file),
            ("CRIME SCENE", self.on_nav_crime_scene),
            ("SUSPECTS", self.on_nav_suspects),
            ("EVIDENCE", self.on_nav_evidence),
            ("ARGUMENTS", self.on_nav_arguments),
            ("COURTROOM", None)
        ]
        self.nav_buttons.clear()
        start_x = 50
        btn_w = 150
        gap = 18
        for i, (label, callback) in enumerate(nav_items):
            is_active = (label == "COURTROOM")
            bg_col = (130, 95, 35) if is_active else (45, 30, 20)
            btn = AnimatedButton(
                x=start_x + i * (btn_w + gap),
                y=10,
                width=btn_w,
                height=30,
                text=label,
                font_size=12,
                bg_color=bg_col,
                is_disabled=is_active or (callback is None),
                on_click=callback if callback else (lambda: None)
            )
            self.nav_buttons.append(btn)

    def _refresh_session(self):
        suspect = self.game_state.get_selected_suspect()
        if suspect:
            self.suspect_sprite.character_type = suspect.avatar_type or "heir"
            self.suspect_sprite.name = suspect.name
            # Build Testimony Statements from statements & alibis
            self.testimony_statements = [
                f'"{suspect.statement}"',
                f'"My alibi is airtight: {suspect.alibi}"',
                f'"I had no reason or motive to be anywhere near the crime scene!"'
            ]
            if suspect.contradictions:
                self.testimony_statements.append(f'"Any claim that I was seen on cameras or leaving traces is mistaken!"')
        else:
            self.suspect_sprite.character_type = "heir"
            self.suspect_sprite.name = "Unknown Suspect"
            self.testimony_statements = [
                '"I am completely innocent of all allegations brought before the Queen\'s Bench!"',
                '"I was nowhere near the scene at the time of the incident!"'
            ]

        self.current_testimony_idx = 0

        self.session = CourtroomSession(
            case_data=self.game_state.current_case,
            selected_suspect=suspect
        )
        self._init_evidence_court_record()
        if self.session.messages:
            first_msg = self.session.messages[0]
            self.dialogue_box.set_message(first_msg.speaker, first_msg.text)
            self.judge_sprite.set_expression("speaking", is_speaking=True)

    def _init_evidence_court_record(self):
        """Constructs permanent interactive Evidence Record buttons displayed directly below the testimony box."""
        self.evidence_court_buttons.clear()
        collected = self.game_state.get_collected_evidence_objects()
        
        category_icons = {
            "physical": "🗡",
            "forensic": "🔬",
            "document": "📄",
            "digital": "💾",
            "testimonial": "🗣",
            "alibi": "⏰"
        }

        # Render up to 5 items in the bottom evidence dock
        display_items = collected[self.evidence_page * 5 : (self.evidence_page + 1) * 5]
        start_x = 50
        card_w = 192
        gap = 10

        for i, ev in enumerate(display_items):
            def make_handler(evidence: Evidence):
                return lambda: self._present_evidence_card(evidence)

            icon = category_icons.get(ev.category.lower(), "📂")
            short_title = f"{icon} {ev.name[:16]}"
            cat_tag = f"[{ev.category.upper()}]"
            btn_text = f"{short_title}\n{cat_tag}"

            btn = AnimatedButton(
                x=start_x + i * (card_w + gap),
                y=486,
                width=card_w,
                height=82,
                text=btn_text,
                font_size=12,
                bg_color=(45, 32, 24),
                border_color=(255, 215, 65),
                border_radius=8,
                tooltip=f"PRESENT EXHIBIT: {ev.name} ({ev.description[:60]}...)",
                on_click=make_handler(ev)
            )
            self.evidence_court_buttons.append(btn)

    def _prev_statement(self):
        if self.testimony_statements:
            self.current_testimony_idx = (self.current_testimony_idx - 1) % len(self.testimony_statements)
            self.sound_service.play("click")

    def _next_statement(self):
        if self.testimony_statements:
            self.current_testimony_idx = (self.current_testimony_idx + 1) % len(self.testimony_statements)
            self.sound_service.play("click")

    def _submit_statement_for_reading(self):
        """Submits the selected witness statement to be read aloud in the Courtroom dialogue box with live animations."""
        if not self.testimony_statements:
            return

        suspect = self.game_state.get_selected_suspect()
        s_name = suspect.name if suspect else "Suspect"
        total_stmts = len(self.testimony_statements)
        cur_stmt = self.testimony_statements[self.current_testimony_idx % total_stmts]

        self.sound_service.play("page_turn")
        self.suspect_sprite.set_expression("speaking", is_speaking=True)
        self.dialogue_box.set_message(s_name, f"TESTIMONY (Statement #{self.current_testimony_idx + 1}): {cur_stmt}")
        self._spawn_floating_popup("📖 STATEMENT ENTERED FOR SCRUTINY!", GOLD_LIGHT, 550, 380)
        self.game_state.set_notification(f"Entered Statement #{self.current_testimony_idx + 1} into Court Record!", category="INFO")

    def _press_current_statement(self):
        """Advocate presses the witness on their active testimony statement!"""
        if not self.session or self.session.is_hearing_terminated:
            return

        suspect = self.game_state.get_selected_suspect()
        s_name = suspect.name if suspect else "Suspect"
        self.sound_service.play("page_turn")
        self.lawyer_sprite.set_expression("pointing", is_speaking=True)
        self.suspect_sprite.set_expression("nervous")
        self.screen_shake.trigger(duration=0.25, intensity=5.0)

        # Combo increment & crowd murmur
        self.logic_combo += 1
        self.crowd_murmur.trigger_reaction("PRESS!", 260, 110, (255, 215, 120))
        self.crowd_murmur.trigger_reaction("SWEAT!", 960, 130, (255, 120, 100))

        # Shake composure & swing jury
        dmg = 10.0
        self.suspect_composure = max(0.0, self.suspect_composure - dmg)
        self.jury_persuasion = min(100.0, self.jury_persuasion + 5.0)
        self._spawn_floating_popup(f"-{int(dmg)} COMPOSURE", (255, 100, 90), 960, 160)
        self._spawn_floating_popup("+5% JURY", ACCENT_GREEN, 320, 100)
        if self.logic_combo > 1:
            self._spawn_floating_popup(f"🔥 LOGIC COMBO x{self.logic_combo}!", GOLD_LIGHT, 550, 190)

        press_responses = [
            f"{s_name}: 'I... well, I was only stepping outside for a breath of fresh evening air!'",
            f"{s_name}: 'Why are you interrogating my exact whereabouts? You have no right!'",
            f"{s_name}: 'I may have passed near the corridor, but I never touched the door lock!'"
        ]
        resp = press_responses[self.current_testimony_idx % len(press_responses)]
        self.dialogue_box.set_message(s_name, resp)
        self.game_state.set_notification(f"Pressed {s_name}! Composure weakened!", category="SUCCESS")

    def _present_evidence_card(self, ev: Evidence):
        """Presents a physical evidence exhibit directly against the active testimony statement."""
        if not self.session or self.session.is_hearing_terminated:
            return

        text = f"OBJECTION! Physical Exhibit {ev.id} ({ev.name}) completely contradicts the testimony: {ev.description}"
        self.screen_shake.trigger(duration=0.5, intensity=9.0)
        self.objection_banner.trigger(text="OBJECTION!", speaker=self.game_state.profile.name)
        self.sound_service.play("objection")
        self.lawyer_sprite.set_expression("pointing", is_speaking=True)

        # Combo increment & crowd murmur
        self.logic_combo += 1
        self.crowd_murmur.trigger_reaction("OBJECTION!", 150, 90, (255, 100, 90))
        self.crowd_murmur.trigger_reaction("CONTRADICTION!", 960, 110, (255, 220, 100))

        # Deal heavy composure damage
        dmg = 25.0
        self.suspect_composure = max(0.0, self.suspect_composure - dmg)
        self.jury_persuasion = min(100.0, self.jury_persuasion + 15.0)
        self._spawn_floating_popup(f"-{int(dmg)} COMPOSURE!", (255, 50, 40), 960, 160)
        self._spawn_floating_popup("+15% JURY PERSUASION!", ACCENT_GREEN, 320, 100)
        self._spawn_floating_popup(f"💥 DECISIVE COMBO x{self.logic_combo}!", GOLD_LIGHT, 550, 180)
        self._process_argument(text)


    def _spawn_floating_popup(self, text: str, color: tuple, x: int, y: int):
        self.floating_popups.append({
            "text": text,
            "color": color,
            "x": float(x),
            "y": float(y),
            "alpha": 255,
            "timer": 1.4
        })


    def _trigger_objection(self):
        """Triggers dynamic OBJECTION interjection with screen shake, sound stinger, and contradiction exposure."""
        if not self.session or self.session.is_hearing_terminated:
            return

        suspect = self.game_state.get_selected_suspect()
        self.screen_shake.trigger(duration=0.5, intensity=9.0)
        self.objection_banner.trigger(text="OBJECTION!", speaker=self.game_state.profile.name)
        self.sound_service.play("objection")
        self.lawyer_sprite.set_expression("pointing", is_speaking=True)

        # Find contradicting evidence or formulate confrontation
        if suspect and suspect.contradictions:
            contradiction_arg = f"OBJECTION! {suspect.name}'s statement is directly contradicted: {suspect.contradictions[0]}"
            self._process_argument(contradiction_arg)
        else:
            collected = self.game_state.get_collected_evidence_objects()
            if collected:
                top_ev = collected[0]
                self._process_argument(f"OBJECTION! The court must examine Exhibit {top_ev.id} ({top_ev.name}): {top_ev.description}")
            else:
                self._process_argument("OBJECTION, Your Honor! The accused's timeline contains material factual inconsistencies!")

    def _trigger_watson_hint(self):
        """Generates intelligent legal pillar guidance from Clerk Watson."""
        self.sound_service.play("evidence")
        unlocked = self.game_state.get_unlocked_facts()

        has_means = any("knife" in f or "weapon" in f or "vault" in f or "signature" in f for f in unlocked)
        has_opp = any("cctv" in f or "present" in f or "opportunity" in f or "entry" in f for f in unlocked)
        has_mot = any("debt" in f or "inheritance" in f or "motive" in f or "fraud" in f for f in unlocked)

        if not has_opp:
            self.watson_hint_message = "WATSON: 'Sir! We lack proof of Opportunity! Check the CCTV logs or entry footprints to refute their alibi!'"
        elif not has_means:
            self.watson_hint_message = "WATSON: 'Counsel! We need physical proof of Means! Inspect latent fingerprints on the murder weapon or vault!'"
        elif not has_mot:
            self.watson_hint_message = "WATSON: 'Clerk Advice: Connect their financial motives or debt messages to establish intent!'"
        else:
            self.watson_hint_message = "WATSON: 'Splendid! All legal pillars are substantiated! Request final deliberation now!'"

        self.watson_hint_timer = 5.0
        self.game_state.set_notification("Clerk Watson provided investigative advice!", category="INFO")

    def _process_argument(self, text: str):
        if not self.session:
            return

        self.lawyer_sprite.set_expression("speaking", is_speaking=True)
        eval_result = self.session.submit_argument(text)

        # Dynamic Jury & Suspect Composure updates
        if eval_result.category == "RELEVANT_SUPPORTED":
            self.jury_persuasion = min(100.0, self.jury_persuasion + 15.0)
            self.suspect_composure = max(0.0, self.suspect_composure - 25.0)
            self.sound_service.play("evidence")
        elif eval_result.category == "RELEVANT_INSUFFICIENT":
            self.jury_persuasion = min(100.0, self.jury_persuasion + 6.0)
            self.suspect_composure = max(0.0, self.suspect_composure - 10.0)
        elif eval_result.is_unwanted:
            self.jury_persuasion = max(0.0, self.jury_persuasion - 15.0)
            self.screen_shake.trigger(0.4, 7.0)

        # Update Judge & Suspect Expressions
        self.judge_sprite.set_expression(eval_result.judge_expression, is_speaking=True)
        if self.suspect_composure <= 20.0:
            self.suspect_sprite.set_expression("breakdown")
        else:
            self.suspect_sprite.set_expression(eval_result.suspect_expression)

        # Update Dialogue Box
        self.dialogue_box.set_message("Judge", eval_result.judge_dialogue)

        # Gavel strike if stern/terminating
        if eval_result.judge_expression == "angry" or self.session.is_hearing_terminated:
            self.gavel_slam_timer = 0.6
            self.screen_shake.trigger(0.4, 8.0)

        # Record in game state trial transcript
        self.game_state.trial_transcript.append({
            "speaker": "Player Counsel",
            "text": text,
            "type": "lawyer"
        })
        self.game_state.trial_transcript.append({
            "speaker": "Judge",
            "text": eval_result.judge_dialogue,
            "type": "judge"
        })

    def _conclude_trial(self):
        if not self.session:
            return

        self.is_trial_concluded = True
        self.gavel_slam_timer = 1.0
        self.sound_service.play("gavel")

        all_premises = []
        if self.session.arguments_submitted:
            for arg_entry in self.session.arguments_submitted:
                if not arg_entry.get("is_unwanted", False):
                    all_premises.append(arg_entry["text"])
        elif self.game_state.current_argument and self.game_state.current_argument.premises:
            all_premises = list(self.game_state.current_argument.premises)
        else:
            all_premises = list(self.game_state.get_unlocked_facts())

        suspect = self.game_state.get_selected_suspect()
        collected_ev = self.game_state.get_collected_evidence_objects()

        final_argument = Argument(
            suspect_id=suspect.id if suspect else "SUS-001",
            premises=all_premises,
            conclusion=self.game_state.current_case.solution_conclusion if self.game_state.current_case else "suspect_guilty_beyond_reasonable_doubt",
            selected_evidence_ids=[e.id for e in collected_ev]
        )

        self.evaluation_result = self.scoring_engine.evaluate_argument(
            argument=final_argument,
            kb=self.session.kb,
            collected_evidence=collected_ev,
            suspect=suspect
        )

        base_score = self.evaluation_result.get("total_score", 0)
        final_score = max(0, min(100, base_score + self.session.cumulative_score))
        self.evaluation_result["total_score"] = final_score
        self.game_state.last_verdict_result = self.evaluation_result

        self.game_state.profile.arguments_submitted += len(self.session.arguments_submitted)
        self.game_state.profile.cases_completed += 1
        self.game_state.profile.highest_score = max(self.game_state.profile.highest_score, final_score)
        if self.evaluation_result["verdict"] == "SUPPORTED":
            self.game_state.profile.cases_won += 1
            self.game_state.profile.total_score += final_score
            self.game_state.set_notification(f"VERDICT: GUILT PROVEN! Score: {final_score}/100", category="SUCCESS")
            self.judge_sprite.set_expression("satisfied")
            self.suspect_sprite.set_expression("nervous")
            self.wax_seal.trigger(text="PROVEN BEYOND DOUBT", is_won=True)
        else:
            self.game_state.profile.total_score += final_score
            self.game_state.set_notification(f"VERDICT: {self.evaluation_result['verdict']}. Score: {final_score}/100", category="WARNING")
            self.judge_sprite.set_expression("thinking")
            self.suspect_sprite.set_expression("surprised")
            self.wax_seal.trigger(text="INSUFFICIENT PROOF", is_won=False)

        self.save_service.save_profile(self.game_state.profile)

    def _restart_hearing(self):
        self.is_trial_concluded = False
        self.score_saved = False
        self.evaluation_result = None
        if self.session:
            self.session.restart_hearing()
            if self.session.messages:
                first_msg = self.session.messages[0]
                self.dialogue_box.set_message(first_msg.speaker, first_msg.text)
        self.game_state.set_notification("Hearing restarted. All unwanted argument penalties reset.", category="INFO")

    def _save_score(self):
        if self.score_saved or not self.evaluation_result or not self.game_state.current_case:
            return
        success = self.save_service.record_score(
            player_name=self.game_state.profile.name,
            case_id=self.game_state.current_case.id,
            case_title=self.game_state.current_case.title,
            score=self.evaluation_result["total_score"],
            verdict=self.evaluation_result["verdict"]
        )
        if success:
            self.score_saved = True
            self.sound_service.play("evidence")
            self.game_state.set_notification("Score recorded to Hall of Fame!", category="SUCCESS")

    def _on_click_view_results(self):
        if self.on_view_results and self.evaluation_result:
            self.on_view_results(self.evaluation_result)

    def _on_click_next_case(self):
        if self.on_case_selection:
            self.on_case_selection()

    def _on_click_leaderboard(self):
        if self.on_view_leaderboard:
            self.on_view_leaderboard()

    def handle_events(self, events):
        for event in events:
            for btn in self.nav_buttons:
                btn.handle_event(event)

            if not self.is_trial_concluded and (not self.session or not self.session.is_hearing_terminated):
                self.btn_prev_stmt.handle_event(event)
                self.btn_next_stmt.handle_event(event)
                self.btn_submit_reading.handle_event(event)
                self.btn_press_witness.handle_event(event)
                self.btn_objection.handle_event(event)
                self.btn_rest_case.handle_event(event)
                self.btn_watson_hint.handle_event(event)

                for eb in self.evidence_court_buttons:
                    eb.handle_event(event)

                # Hotkeys
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self._submit_statement_for_reading()
                    elif event.key == pygame.K_p:
                        self._press_current_statement()
                    elif event.key == pygame.K_o:
                        self._trigger_objection()
                    elif event.key == pygame.K_h:
                        self._trigger_watson_hint()
                    elif event.key == pygame.K_r:
                        self._conclude_trial()
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_q:
                        self._prev_statement()
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_w:
                        self._next_statement()
            else:
                self.btn_view_results.handle_event(event)
                self.btn_save_score.handle_event(event)
                self.btn_next_case.handle_event(event)
                self.btn_restart_hearing.handle_event(event)
                self.btn_leaderboard.handle_event(event)

    def update(self, dt: float = 0.016):
        self.anim_time += dt
        self.light_rays.update(dt)
        self.scales_of_justice.update(dt, self.jury_persuasion)
        self.crowd_murmur.update(dt)
        self.chandelier_left.update(dt)
        self.chandelier_right.update(dt)
        self.gallery.update(dt)
        strikes = self.session.unwanted_argument_count if self.session else 0
        self.discipline_gauge.update(dt, max(0.0, 100.0 - strikes * 33.3))
        self.wax_seal.update(dt)
        self.particles.update(dt)
        self.screen_shake.update(dt)
        self.objection_banner.update(dt)

        # Update floating damage numbers
        surviving_popups = []
        for pop in self.floating_popups:
            pop["timer"] -= dt
            pop["y"] -= dt * 35.0
            pop["alpha"] = max(0, int((pop["timer"] / 1.4) * 255))
            if pop["timer"] > 0:
                surviving_popups.append(pop)
        self.floating_popups = surviving_popups

        if self.watson_hint_timer > 0:
            self.watson_hint_timer -= dt
            if self.watson_hint_timer <= 0:
                self.watson_hint_message = None

        if self.gavel_slam_timer > 0:
            self.gavel_slam_timer -= dt

        self.judge_sprite.update(dt)
        self.lawyer_sprite.update(dt)
        self.suspect_sprite.update(dt)
        self.suspect_ring.update(dt)
        self.dialogue_box.update(dt)

        for btn in self.nav_buttons:
            btn.update(dt)
        if not self.is_trial_concluded and (not self.session or not self.session.is_hearing_terminated):
            self.btn_prev_stmt.update(dt)
            self.btn_next_stmt.update(dt)
            self.btn_submit_reading.update(dt)
            self.btn_press_witness.update(dt)
            self.btn_objection.update(dt)
            self.btn_rest_case.update(dt)
            self.btn_watson_hint.update(dt)
            for eb in self.evidence_court_buttons:
                eb.update(dt)
        else:
            self.btn_view_results.update(dt)
            self.btn_save_score.update(dt)
            self.btn_restart_hearing.update(dt)
            self.btn_next_case.update(dt)
            self.btn_leaderboard.update(dt)

    def draw(self):
        # Create shake offset
        ox, oy = self.screen_shake.get_offset()

        self.screen.fill(BACKGROUND)

        # Live Background Atmospheric Motion: Volumetric Sunbeams & Scales of Justice
        self.light_rays.draw(self.screen)
        self.scales_of_justice.draw(self.screen)
        self.gallery.draw(self.screen)
        self.chandelier_left.draw(self.screen)
        self.chandelier_right.draw(self.screen)
        self.particles.draw(self.screen)

        # 1. Outer Frame
        pygame.draw.rect(self.screen, DARK_BROWN, (16 + ox, 44 + oy, SCREEN_WIDTH - 32, SCREEN_HEIGHT - 52), 3, border_radius=12)
        pygame.draw.rect(self.screen, GOLD, (22 + ox, 50 + oy, SCREEN_WIDTH - 44, SCREEN_HEIGHT - 64), 1, border_radius=10)

        # 2. Top Navigation Bar
        for btn in self.nav_buttons:
            btn.draw(self.screen)

        # 3. Stage: Center Elevated Bench
        bench_rect = pygame.Rect(440 + ox, 58 + oy, 220, 150)
        self._draw_judge_bench(bench_rect)

        # 4. Stage: Left Advocate Podium
        podium_rect = pygame.Rect(70 + ox, 75 + oy, 170, 140)
        self._draw_lawyer_podium(podium_rect)

        # 5. Stage: Right Accused Suspect Dock & Composure
        self._draw_suspect_dock(ox, oy)

        # 6. Discipline Warning Badge & 12-Juror Box
        strikes = self.session.unwanted_argument_count if self.session else 0
        self.discipline_gauge.rect.x = 680 + ox
        self.discipline_gauge.rect.y = 58 + oy
        self.discipline_gauge.draw(self.screen, get_font, strikes=strikes)
        self._draw_jury_box(x=255 + ox, y=58 + oy)

        # 7. Roomy Dialogue Box
        self.dialogue_box.draw(self.screen)

        # 8. Bottom Workspace / Controls
        if self.session and self.session.is_hearing_terminated:
            self._draw_hearing_terminated_panel()
            self.btn_restart_hearing.draw(self.screen)
            self.btn_next_case.draw(self.screen)
            self.btn_leaderboard.draw(self.screen)
        elif self.is_trial_concluded:
            self._draw_verdict_card()
            self.btn_view_results.draw(self.screen)
            self.btn_save_score.draw(self.screen)
            self.btn_restart_hearing.draw(self.screen)
            self.btn_next_case.draw(self.screen)
        else:
            self._draw_pleading_workspace()

        # 9. Crowd Murmur & Comic Reaction Bubbles
        self.crowd_murmur.draw(self.screen, get_font)

        # 10. Floating Combat Popups
        for pop in self.floating_popups:
            p_surf = get_font(16, bold=True).render(pop["text"], True, pop["color"])
            p_surf.set_alpha(pop["alpha"])
            self.screen.blit(p_surf, (int(pop["x"] - p_surf.get_width() // 2), int(pop["y"])))

        # 11. Watson Hint Bubble Overlay
        if self.watson_hint_message and self.watson_hint_timer > 0:
            self._draw_watson_hint_popup()

        # 12. Dramatic Wax Seal Stamp on Verdict
        if self.wax_seal.active:
            self.wax_seal.draw(self.screen, get_font)

        # 13. Dramatic Objection Banner
        self.objection_banner.draw(self.screen, get_font)

    def _draw_pleading_workspace(self):
        from components.ui_shapes import draw_chamfered_rect

        # Action Buttons Row
        self.btn_prev_stmt.draw(self.screen)
        self.btn_next_stmt.draw(self.screen)
        self.btn_submit_reading.draw(self.screen)
        self.btn_press_witness.draw(self.screen)
        self.btn_objection.draw(self.screen)
        self.btn_rest_case.draw(self.screen)

        # Innovative Evidence Court Record Rack directly below testimony
        ev_header_y = 452
        total_stmts = max(1, len(self.testimony_statements))
        cur_stmt = self.testimony_statements[self.current_testimony_idx % total_stmts] if self.testimony_statements else "No statement available."
        
        # Statement indicator ribbon bar
        stmt_ribbon_rect = pygame.Rect(50, ev_header_y - 14, 1000, 32)
        draw_chamfered_rect(self.screen, stmt_ribbon_rect, (32, 20, 14), GOLD, cut=6, border_width=1)
        self.screen.blit(get_font(14, bold=True).render(f"ACTIVE TESTIMONY #{self.current_testimony_idx + 1}/{total_stmts}: {cur_stmt}", True, GOLD_LIGHT), (stmt_ribbon_rect.x + 14, stmt_ribbon_rect.y + 6))

        self.screen.blit(get_font(14, bold=True).render("📂 COURT EVIDENCE RECORD (CLICK AN EXHIBIT TO SLAM CONTRADICTION ON ACCUSED):", True, WHITE), (50, ev_header_y + 24))

        # Render Evidence Buttons
        for eb in self.evidence_court_buttons:
            eb.draw(self.screen)

        if not self.evidence_court_buttons:
            no_ev_rect = pygame.Rect(50, 490, 1000, 82)
            draw_chamfered_rect(self.screen, no_ev_rect, (32, 22, 16), GOLD, cut=10, border_width=1)
            self.screen.blit(get_font(15, bold=True).render("NO EVIDENCE COLLECTED YET! Visit CRIME SCENE with Forensic Tools to discover clues.", True, ACCENT_ORANGE), (no_ev_rect.x + 20, no_ev_rect.y + 28))

        # Bottom Hint Bar
        hint_text = "HOTKEYS: [Q/W] Select Statement  |  [SPACE] Submit for Reading  |  [P] Press Witness  |  [O] Objection  |  [R] Demand Verdict"
        self.screen.blit(get_font(13, bold=True).render(hint_text, True, MUTED_TEXT), (50, 584))
        self.btn_watson_hint.draw(self.screen)

    def _draw_watson_hint_popup(self):
        """Draws glowing Clerk Watson tactical advice bubble overlay with innovative chamfered geometry."""
        if not self.watson_hint_message:
            return

        from components.ui_shapes import draw_chamfered_rect
        hint_w = 840
        hint_h = 84
        hint_x = (SCREEN_WIDTH - hint_w) // 2
        hint_y = 195
        r = pygame.Rect(hint_x, hint_y, hint_w, hint_h)

        # Innovative Chamfered Panel & Glow Border
        draw_chamfered_rect(self.screen, r, (20, 35, 55), (100, 190, 255), cut=12, border_width=2, corner_brackets=True, inner_glow=True)

        # Header Badge
        header_surf = get_font(13, bold=True).render("💡 CLERK WATSON'S INVESTIGATIVE ADVICE:", True, (140, 215, 255))
        self.screen.blit(header_surf, (r.x + 18, r.y + 10))

        # Advice Text
        body_surf = get_font(14, bold=True).render(self.watson_hint_message, True, WHITE)
        self.screen.blit(body_surf, (r.x + 18, r.y + 38))

    def _draw_jury_box(self, x: int, y: int):
        """Renders animated 12-Member Jury Box with dynamic Persuasion Gauge."""
        from components.ui_shapes import draw_chamfered_rect
        w, h = 175, 145
        r = pygame.Rect(x, y, w, h)
        draw_chamfered_rect(self.screen, r, (34, 24, 18), GOLD, cut=8, border_width=1, corner_brackets=True)

        # Header
        f_lbl = get_font(13, bold=True)
        self.screen.blit(f_lbl.render("JURY (12 MEMBERS)", True, GOLD_LIGHT), (x + 12, y + 6))

        # 12 Juror Avatar Dots / Mini-heads (2 rows of 6)
        juror_lean = self.jury_persuasion / 100.0
        for i in range(12):
            col = i % 6
            row = i // 6
            jx = x + 14 + col * 26
            jy = y + 26 + row * 34

            is_convinced = (i / 12.0) < juror_lean
            head_col = (235, 195, 165)
            pygame.draw.circle(self.screen, head_col, (jx + 8, jy + 8), 7)
            # Hair
            pygame.draw.arc(self.screen, (60, 40, 30) if i % 2 == 0 else (180, 160, 130), (jx + 2, jy, 12, 10), 0, math.pi, 4)

            # Sentiment Expression
            if is_convinced:
                pygame.draw.circle(self.screen, ACCENT_GREEN, (jx + 8, jy + 18), 3)
            else:
                pygame.draw.circle(self.screen, (150, 60, 50), (jx + 8, jy + 18), 3)

        # Dynamic Persuasion Bar
        bar_y = y + 102
        bar_rect = pygame.Rect(x + 10, bar_y, w - 20, 14)
        draw_chamfered_rect(self.screen, bar_rect, (20, 15, 12), GOLD_LIGHT, cut=4, border_width=1)
        fill_w = int(bar_rect.width * (self.jury_persuasion / 100.0))
        bar_col = ACCENT_GREEN if self.jury_persuasion >= 60 else (ACCENT_BLUE if self.jury_persuasion >= 40 else ACCENT_RED)
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_rect.height)
            draw_chamfered_rect(self.screen, fill_rect, bar_col, None, cut=3)

        pct_surf = get_font(12, bold=True).render(f"Persuasion: {int(self.jury_persuasion)}%", True, WHITE)
        self.screen.blit(pct_surf, (x + 12, bar_y + 18))

    def _draw_judge_bench(self, rect: pygame.Rect):
        from components.ui_shapes import draw_chamfered_rect
        draw_chamfered_rect(self.screen, rect, (38, 24, 16), GOLD, cut=10, border_width=2, corner_brackets=True, inner_glow=True)

        # Judge Sprite
        judge_avatar_rect = pygame.Rect(rect.centerx - 45, rect.y + 10, 90, 95)
        self.judge_sprite.draw(self.screen, judge_avatar_rect)

        # Ledge
        ledge_rect = pygame.Rect(rect.x + 6, rect.bottom - 38, rect.width - 12, 32)
        draw_chamfered_rect(self.screen, ledge_rect, WOOD_BROWN, GOLD_LIGHT, cut=5, border_width=1)

        # Gavel Visual
        gavel_x = ledge_rect.right - 28
        gavel_y = ledge_rect.centery - 4
        if self.gavel_slam_timer > 0:
            pygame.draw.line(self.screen, GOLD_DARK, (gavel_x, gavel_y), (gavel_x - 12, gavel_y - 12), 4)
            pygame.draw.circle(self.screen, GOLD_LIGHT, (gavel_x, gavel_y), 6)
        else:
            pygame.draw.line(self.screen, GOLD, (gavel_x, gavel_y), (gavel_x - 8, gavel_y - 8), 3)
            pygame.draw.circle(self.screen, GOLD, (gavel_x, gavel_y), 5)

        f = get_font(14, bold=True)
        t_surf = f.render("AI MAGISTRATE", True, WHITE)
        self.screen.blit(t_surf, (ledge_rect.x + 10, ledge_rect.y + 6))

    def _draw_lawyer_podium(self, rect: pygame.Rect):
        from components.ui_shapes import draw_chamfered_rect
        lawyer_avatar_rect = pygame.Rect(rect.centerx - 45, rect.y + 8, 90, 95)
        self.lawyer_sprite.draw(self.screen, lawyer_avatar_rect)

        podium_stand = pygame.Rect(rect.x + 8, rect.bottom - 32, rect.width - 16, 28)
        draw_chamfered_rect(self.screen, podium_stand, (40, 28, 20), GOLD, cut=5, border_width=1)

        f = get_font(13, bold=True)
        t_surf = f.render(f"COUNSEL: {self.game_state.profile.name}", True, GOLD_LIGHT)
        self.screen.blit(t_surf, t_surf.get_rect(center=podium_stand.center))

    def _draw_suspect_dock(self, ox: int = 0, oy: int = 0):
        from components.ui_shapes import draw_chamfered_rect
        suspect = self.game_state.get_selected_suspect()
        s_name = suspect.name if suspect else "Accused Suspect"
        s_type = suspect.avatar_type if suspect else "accused"

        self.suspect_ring.center_x = 960 + ox
        self.suspect_ring.center_y = 210 + oy
        self.suspect_ring.draw(self.screen, suspect_name=s_name, suspect_type=s_type)
        avatar_rect = pygame.Rect(self.suspect_ring.center_x - 45, self.suspect_ring.center_y - 105, 90, 95)
        self.suspect_sprite.draw(self.screen, avatar_rect)

        # Suspect Composure Gauge
        comp_w = 145
        comp_x = avatar_rect.centerx - (comp_w // 2)
        comp_y = avatar_rect.y - 24
        comp_rect = pygame.Rect(comp_x, comp_y, comp_w, 18)
        draw_chamfered_rect(self.screen, comp_rect, (25, 18, 14), GOLD_LIGHT, cut=4, border_width=1)
        c_fill = int(comp_w * (self.suspect_composure / 100.0))
        c_col = ACCENT_GREEN if self.suspect_composure >= 60 else (ACCENT_ORANGE if self.suspect_composure >= 30 else ACCENT_RED)
        if c_fill > 0:
            c_fill_rect = pygame.Rect(comp_x, comp_y, c_fill, comp_rect.height)
            draw_chamfered_rect(self.screen, c_fill_rect, c_col, None, cut=3)

        lbl = get_font(12, bold=True).render(f"COMPOSURE: {int(self.suspect_composure)}%", True, WHITE)
        self.screen.blit(lbl, lbl.get_rect(center=comp_rect.center))

    def _draw_hearing_terminated_panel(self):
        from components.ui_shapes import draw_chamfered_rect
        r = pygame.Rect(50, 420, 1000, 155)
        draw_chamfered_rect(self.screen, r, (45, 15, 12), ACCENT_RED, cut=14, border_width=2, corner_brackets=True, inner_glow=True)

        t_font = get_font(20, bold=True)
        self.screen.blit(t_font.render("⚖ CONTEMPT OF COURT • HEARING TERMINATED", True, ACCENT_RED), (r.x + 20, r.y + 14))

        msg1 = "The Magistrate has terminated this hearing due to repeated submission of irrelevant and frivolous claims."
        msg2 = "The case has been marked DISCLOSED / HEARING TERMINATED. Review your evidence and restart the hearing."

        f_b = get_font(15, bold=True)
        self.screen.blit(f_b.render(msg1, True, WHITE), (r.x + 20, r.y + 50))
        self.screen.blit(f_b.render(msg2, True, GOLD_LIGHT), (r.x + 20, r.y + 80))

        f_note = get_font(14, italic=True)
        self.screen.blit(f_note.render("Click 'RESTART HEARING' below to begin a fresh, clean deliberation.", True, MUTED_TEXT), (r.x + 20, r.y + 118))

    def _draw_verdict_card(self):
        if not self.evaluation_result:
            return
        from components.ui_shapes import draw_chamfered_rect
        r = pygame.Rect(50, 420, 1000, 155)
        verdict = self.evaluation_result.get("verdict", "INCONCLUSIVE")
        score = self.evaluation_result.get("total_score", 0)

        is_won = (verdict == "SUPPORTED")
        border_col = ACCENT_GREEN if is_won else ACCENT_ORANGE
        bg_col = (18, 38, 22) if is_won else (38, 28, 16)

        draw_chamfered_rect(self.screen, r, bg_col, border_col, cut=14, border_width=2, corner_brackets=True, inner_glow=True)

        v_font = get_font(22, bold=True)
        v_title = f"⚖ FINAL COURTROOM VERDICT: {verdict}"
        self.screen.blit(v_font.render(v_title, True, border_col), (r.x + 20, r.y + 14))

        score_font = get_font(32, bold=True)
        score_surf = score_font.render(f"{score} / 100 PTS", True, GOLD_LIGHT)
        self.screen.blit(score_surf, (r.right - score_surf.get_width() - 25, r.y + 10))

        bd = self.evaluation_result.get("breakdown", {})
        det_txt = (
            f"Logic Validity: {bd.get('logical_validity', 0)}/30  |  "
            f"Evidence Strength: {bd.get('evidence_strength', 0)}/40  |  "
            f"Fact Grounding: {bd.get('fact_grounding', 0)}/15  |  "
            f"Safeguards: {bd.get('safeguards', 0)}/15"
        )
        self.screen.blit(get_font(15, bold=True).render(det_txt, True, WHITE), (r.x + 20, r.y + 54))

        feedback = self.evaluation_result.get("feedback", "")
        self.screen.blit(get_font(14, italic=True).render(f'Magistrate Evaluation: "{feedback}"', True, GOLD_LIGHT), (r.x + 20, r.y + 88))



