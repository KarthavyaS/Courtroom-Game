"""Streamlined Argument Workshop & Indictment Builder for LOGIC COURTROOM.
Modern, clean 3-panel deductive workspace:
1. Target Accused & Legal Charge
2. Forensic Evidence & Proposition Pool (Categorized & Paginated)
3. Assembled Court Indictment with Integrated Watson Advisor & Trial Submission.
"""
#pyright: ignore
import pygame
from typing import Callable, Optional, List, Set, Dict, Any
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
from ai_engine.argument_parser import ArgumentParser
from components.animated_button import AnimatedButton
from components.navigation_bar import NavigationBar
from components.text_box import TextBox
from components.animation import ParticleSystem

# Meta-dictionary mapping formal logical propositions to concise labels and categories
PROPOSITION_META: Dict[str, tuple] = {
    # Means & Method
    "suspect_fingerprints_on_knife": ("Fingerprints on Weapon", "MEANS", "Latent prints match suspect with 99.8% certainty."),
    "blood_on_knife_matches_victim": ("Victim Blood on Blade", "MEANS", "Blade stains match victim blood profile."),
    "knife_found_at_scene": ("Murder Weapon at Scene", "MEANS", "Chef knife located beneath the study desk."),
    "victim_cause_of_death_stab_wound": ("Fatal Blade Wound", "MEANS", "Autopsy confirms acute blood loss from stab wound."),
    "suspect_had_safe_key": ("Duplicate Vault Key", "MEANS", "Brass key found in suspect appraisal case."),
    "necklace_found_in_suspect_bag": ("Stolen Necklace in Case", "MEANS", "Stolen diamond necklace hidden in velvet case."),
    "necklace_identified_as_stolen": ("Verified Stolen Gem", "MEANS", "Gemology stamps match stolen necklace."),
    "safe_opened_without_forced_entry": ("Unforced Safe Entry", "MEANS", "Safe lock opened without physical damage."),
    "silk_thread_matches_appraiser_gloves": ("Silk Glove Thread", "MEANS", "Thread on safe dial matches suspect gloves."),
    "suspect_digital_signature_used": ("2FA Security Signature", "MEANS", "Hardware token used for wire authorization."),
    "forged_invoice_at_scene": ("Forged Vendor Invoice", "MEANS", "Fake invoice bearing executive approval stamps."),
    "encrypted_keys_on_usb": ("Offshore Bank Keys", "MEANS", "Private encryption keys found in executive desk."),
    "suspect_master_key_used_at_scene": ("Master Gear Key", "MEANS", "Engraved brass key with initials found at scene."),
    "suspect_fingerprints_on_clockwork": ("Prints on Mechanism", "MEANS", "Fingerprints identified on clockwork frame."),
    "platinum_shavings_match_stolen_gear": ("Platinum Filings on Apron", "MEANS", "Shavings match 950-platinum gear alloy."),
    "escapement_gear_stolen_from_clock": ("Stolen Escapement Gear", "MEANS", "Gear removed with specialized horology tools."),
    "victim_poisoned_with_digitalis": ("Digitalis Poison in Tea", "MEANS", "Teapot infused with lethal digitalis glycoside."),
    "suspect_dispensed_lethal_digitalis": ("Biometric Dispenser Log", "MEANS", "Digitalis vault unlocked with suspect badge."),
    "digitalis_residue_on_suspect_gloves": ("Poison on Latex Gloves", "MEANS", "Digitalis powder and DNA found in archive bin."),
    "diamond_replaced_with_glass_replica": ("Cubic Zirconia Replica", "MEANS", "Artificial fake substituted on velvet stand."),
    "suspect_biometric_override_used": ("Thumbprint Override Log", "MEANS", "Thumbprint logged on vault security panel."),
    "sovereign_diamond_dust_in_briefcase": ("Diamond Dust in Briefcase", "MEANS", "Microscopic diamond facet dust in briefcase."),
    "laser_grid_bypassed_via_director_code": ("Laser Grid Override", "MEANS", "Bypass card found in director office safe."),

    # Opportunity & Access
    "cctv_shows_suspect_entry": ("CCTV Entry at Midnight", "OPPORTUNITY", "Security camera records suspect entering at 11:50 PM."),
    "suspect_present_at_mansion_at_midnight": ("Present in Mansion", "OPPORTUNITY", "Timeline verifies presence during crime window."),
    "broken_window_opened_from_inside": ("Window Opened From Inside", "OPPORTUNITY", "Balcony latch unlatched from within."),
    "muddy_bootprints_match_garden": ("Muddy Garden Bootprints", "OPPORTUNITY", "Tread marks match suspect wardrobe footwear."),
    "suspect_entered_tower_at_midnight": ("CCTV Staircase Log", "OPPORTUNITY", "Suspect recorded climbing tower stairs at 11:55 PM."),
    "suspect_present_in_archive_wing": ("Archive Access Log", "OPPORTUNITY", "Badge scan at archive corridor at 11:40 PM."),
    "suspect_entered_vault_at_midnight": ("Vault Midnight Entry", "OPPORTUNITY", "Biometric entry confirms access at 11:42 PM."),
    "suspect_claimed_cinema_alibi": ("Claimed Cinema Alibi", "OPPORTUNITY", "Suspect claimed to be at downtown cinema."),

    # Motive & Intent
    "suspect_debt_or_inheritance": ("£10M Inheritance & Debt", "MOTIVE", "Heavy personal debt; stands to inherit estate."),
    "incriminating_phone_messages": ("Threatening Phone Texts", "MOTIVE", "Urgent texts demanding immediate financial payout."),
    "financial_fraud_detected": ("£2.5M Fraud Detected", "MOTIVE", "Audit flags irregular wire to Cayman account."),
    "offshore_account_linked_to_suspect": ("Cayman Account Link", "MOTIVE", "Apex Horizons registration lists suspect as owner."),
    "suspect_facing_bankruptcy_motive": ("Urgent £50,000 Debt", "MOTIVE", "Blackmail telegram demanding immediate payment."),
    "victim_threatened_to_expose_plagiarism": ("Threatened with Exposure", "MOTIVE", "Draft letter demanding resignation for fraud."),
    "suspect_contracted_smuggling_vessel": ("Chartered Smuggling Cutter", "MOTIVE", "Manifest for steam cutter departing for Tangier.")
}


class ArgumentBuilder:
    """Streamlined deductive argument workshop with clean 3-panel architecture."""

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
        on_nav_notebook: Callable[[], None],
        on_submit_to_court: Callable[[Argument], None],
        on_nav_courtroom: Optional[Callable[[], None]] = None,
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
        self.on_nav_notebook = on_nav_notebook
        self.on_submit_to_court = on_submit_to_court
        self.on_nav_courtroom = on_nav_courtroom or (lambda: self._submit())
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service()

        self.argument_parser = ArgumentParser()
        self.particles = ParticleSystem(max_particles=30)

        self.selected_suspect_id: Optional[str] = None
        self.selected_evidence_ids: Set[str] = set()
        self.selected_premises: List[str] = []
        self.selected_conclusion: str = "suspect_guilty_beyond_reasonable_doubt"

        # Filter mode for Proposition Pool: 'ALL', 'MEANS', 'OPPORTUNITY', 'MOTIVE'
        self.active_category_filter = "ALL"
        self.page_index = 0
        self.items_per_page = 5

        # Navigation Bar
        self.nav_bar = NavigationBar(
            current_stage="arguments",
            game_state=self.game_state,
            on_nav_dashboard=self.on_nav_dashboard,
            on_nav_briefing=self.on_nav_briefing,
            on_nav_scene=self.on_nav_scene,
            on_nav_suspects=self.on_nav_suspects,
            on_nav_evidence=self.on_nav_evidence,
            on_nav_board=self.on_nav_board,
            on_nav_notebook=self.on_nav_notebook,
            on_nav_arguments=None,
            on_nav_courtroom=self.on_nav_courtroom
        )

        self.anim_tick = 0

        # Filter Buttons (Center Panel)
        btn_y = 66
        self.btn_filt_all = AnimatedButton(305, btn_y, 65, 28, "ALL", font_size=10, bg_color=(100, 75, 40), on_click=lambda: self._set_filter("ALL"))
        self.btn_filt_means = AnimatedButton(376, btn_y, 88, 28, "🗡 METHOD", font_size=10, bg_color=(90, 50, 40), on_click=lambda: self._set_filter("MEANS"))
        self.btn_filt_opp = AnimatedButton(470, btn_y, 88, 28, "🚪 ACCESS", font_size=10, bg_color=(40, 70, 95), on_click=lambda: self._set_filter("OPPORTUNITY"))
        self.btn_filt_mot = AnimatedButton(564, btn_y, 88, 28, "💰 MOTIVE", font_size=10, bg_color=(80, 75, 35), on_click=lambda: self._set_filter("MOTIVE"))

        # Center Pagination Buttons
        self.btn_prev_page = AnimatedButton(305, 526, 110, 30, "◀ PREV", font_size=11, bg_color=(50, 40, 35), on_click=self._prev_page)
        self.btn_next_page = AnimatedButton(675, 526, 110, 30, "NEXT ▶", font_size=11, bg_color=(50, 40, 35), on_click=self._next_page)

        # Custom Manual Argument Entry (Center Bottom)
        self.text_box = TextBox(
            x=305, y=566, width=380, height=36,
            placeholder="Type custom legal statement...",
            font_size=12, is_multiline=False
        )
        self.btn_add_custom = AnimatedButton(
            x=695, y=566, width=90, height=36,
            text="+ ADD", font_size=11, bg_color=ACCENT_BLUE,
            tooltip="Parse custom argument claim",
            on_click=self._add_custom_argument
        )

        # Left Quick Action Buttons
        self.btn_auto_populate = AnimatedButton(
            x=35, y=526, width=250, height=36,
            text="⚡ AUTO-EQUIP CLUES [A]", font_size=11, bg_color=(115, 80, 40),
            tooltip="Equip all verified evidence facts into indictment",
            on_click=self._auto_fill_collected
        )
        self.btn_clear = AnimatedButton(
            x=35, y=568, width=250, height=34,
            text="✕ CLEAR INDICTMENT [C]", font_size=11, bg_color=(75, 40, 35),
            tooltip="Clear all equipped premises",
            on_click=self._clear_premises
        )

        # Right Primary Submit Button
        self.btn_submit = AnimatedButton(
            x=805, y=555, width=265, height=48,
            text="⚔️ ENTER TRIAL (COURT) ➔", font_size=13, bg_color=ACCENT_GREEN,
            tooltip="Enter Courtroom to demand judgment (Space / Enter)",
            on_click=self._submit
        )

        self._init_suspect_and_conclusions()
        self._auto_fill_collected()

    def _init_suspect_and_conclusions(self) -> None:
        if self.game_state.current_case:
            if not self.selected_suspect_id and self.game_state.current_case.suspects:
                self.selected_suspect_id = self.game_state.selected_suspect_id or self.game_state.current_case.suspects[0].id
            self.selected_conclusion = self.game_state.current_case.solution_conclusion

    def _set_filter(self, mode: str) -> None:
        self.active_category_filter = mode
        self.page_index = 0
        self.sound_service.play("click")

    def _prev_page(self) -> None:
        if self.page_index > 0:
            self.page_index -= 1
            self.sound_service.play("click")

    def _next_page(self) -> None:
        pool = self._build_proposition_pool()
        filtered = [item for item in pool if self.active_category_filter == "ALL" or item["cat"] == self.active_category_filter]
        if (self.page_index + 1) * self.items_per_page < len(filtered):
            self.page_index += 1
            self.sound_service.play("click")

    def _build_proposition_pool(self) -> List[Dict[str, Any]]:
        """Constructs clean, non-bloated proposition pool for the active case."""
        case = self.game_state.current_case
        if not case:
            return []

        pool = []
        seen_facts = set()

        # 1. First add all evidence propositions unlocked or present in this case
        for ev in case.evidence_list:
            for fact in ev.facts_unlocked:
                if fact not in seen_facts:
                    seen_facts.add(fact)
                    if fact in PROPOSITION_META:
                        title, cat, desc = PROPOSITION_META[fact]
                    else:
                        title = fact.replace("_", " ").title()
                        cat = "MEANS" if "knife" in fact or "weapon" in fact else "OPPORTUNITY"
                        desc = f"Forensic artifact unlocked from {ev.name}."
                    pool.append({"fact": fact, "title": title, "cat": cat, "desc": desc, "evidence_id": ev.id})

        # 2. Add initial case facts
        for fact in case.initial_facts:
            if fact not in seen_facts:
                seen_facts.add(fact)
                if fact in PROPOSITION_META:
                    title, cat, desc = PROPOSITION_META[fact]
                else:
                    title = fact.replace("_", " ").title()
                    cat = "OPPORTUNITY"
                    desc = "Initial verified scene condition."
                pool.append({"fact": fact, "title": title, "cat": cat, "desc": desc, "evidence_id": None})

        # 3. Add suspect-specific known facts
        suspect = self.game_state.get_selected_suspect()
        if suspect:
            for fact in suspect.known_facts:
                if fact not in seen_facts:
                    seen_facts.add(fact)
                    if fact in PROPOSITION_META:
                        title, cat, desc = PROPOSITION_META[fact]
                    else:
                        title = fact.replace("_", " ").title()
                        cat = "MOTIVE" if "motive" in fact or "debt" in fact else "OPPORTUNITY"
                        desc = f"Deposition fact regarding {suspect.name}."
                    pool.append({"fact": fact, "title": title, "cat": cat, "desc": desc, "evidence_id": None})

        return pool

    def _toggle_proposition(self, item: Dict[str, Any]) -> None:
        fact = item["fact"]
        ev_id = item.get("evidence_id")

        if fact in self.selected_premises:
            self.selected_premises.remove(fact)
            if ev_id and ev_id in self.selected_evidence_ids:
                # Only remove evidence ID if no other premise uses it
                other_uses = any(
                    other["fact"] in self.selected_premises and other.get("evidence_id") == ev_id
                    for other in self._build_proposition_pool()
                )
                if not other_uses:
                    self.selected_evidence_ids.discard(ev_id)
            self.sound_service.play("click")
        else:
            self.selected_premises.append(fact)
            if ev_id:
                self.selected_evidence_ids.add(ev_id)
            self.sound_service.play("evidence")
            self.particles.emit(550, 300, count=10, color=(255, 215, 100), speed_mult=2.0)

    def _auto_fill_collected(self) -> None:
        self.selected_premises.clear()
        self.selected_evidence_ids.clear()

        pool = self._build_proposition_pool()
        for item in pool:
            # Equip all verified evidence facts and initial facts
            self.selected_premises.append(item["fact"])
            if item.get("evidence_id"):
                self.selected_evidence_ids.add(item["evidence_id"])

        self.game_state.progress.record_argument_drafted(is_valid=True)
        self.sound_service.play("evidence")
        self.particles.emit(550, 200, count=15, color=(100, 255, 180), speed_mult=2.5)

    def _clear_premises(self) -> None:
        self.selected_premises.clear()
        self.selected_evidence_ids.clear()
        self.sound_service.play("click")

    def _add_custom_argument(self) -> None:
        txt = self.text_box.get_text().strip()
        if not txt:
            self.game_state.set_notification("Please type a custom argument statement!", category="WARNING")
            return
        parsed_id, conf, exp = self.argument_parser.parse_sentence(txt)
        if parsed_id not in self.selected_premises:
            self.selected_premises.append(parsed_id)
            self.sound_service.play("evidence")
            self.game_state.set_notification(f"Custom premise registered: {parsed_id}", category="SUCCESS")
        self.text_box.set_text("")

    def _submit(self) -> None:
        if not self.selected_suspect_id:
            self.game_state.set_notification("Please select an accused suspect.", category="WARNING")
            return

        premises_list = list(self.selected_premises)
        if not premises_list:
            # Fallback to auto-fill so the player is never blocked
            self._auto_fill_collected()
            premises_list = list(self.selected_premises)

        arg = Argument(
            suspect_id=self.selected_suspect_id,
            premises=premises_list,
            conclusion=self.selected_conclusion,
            selected_evidence_ids=list(self.selected_evidence_ids),
            custom_text=""
        )

        self.game_state.current_argument = arg
        self.game_state.progress.record_argument_drafted(is_valid=True)
        self.save_service.save_active_game(self.game_state)
        self.sound_service.play("gavel")
        self.on_submit_to_court(arg)

    def handle_events(self, events) -> None:
        self.nav_bar.handle_events(events)
        for event in events:
            # Filter & Pagination
            self.btn_filt_all.handle_event(event)
            self.btn_filt_means.handle_event(event)
            self.btn_filt_opp.handle_event(event)
            self.btn_filt_mot.handle_event(event)
            self.btn_prev_page.handle_event(event)
            self.btn_next_page.handle_event(event)

            # Text input
            self.text_box.handle_event(event)
            self.btn_add_custom.handle_event(event)

            # Action buttons
            self.btn_auto_populate.handle_event(event)
            self.btn_clear.handle_event(event)
            self.btn_submit.handle_event(event)

            # Keyboard Shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self._auto_fill_collected()
                elif event.key == pygame.K_c and not self.text_box.is_focused:
                    self._clear_premises()
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if self.text_box.is_focused and self.text_box.get_text().strip():
                        self._add_custom_argument()
                    elif not self.text_box.is_focused:
                        self._submit()

            # Mouse wheel page scroll in center
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self._prev_page()
                elif event.y < 0:
                    self._next_page()

            # Click handling
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 1. Suspect selection in Left Panel (x=35)
                if self.game_state.current_case:
                    for i, s in enumerate(self.game_state.current_case.suspects):
                        s_rect = pygame.Rect(35, 100 + i * 46, 250, 40)
                        if s_rect.collidepoint(event.pos):
                            self.selected_suspect_id = s.id
                            self.game_state.selected_suspect_id = s.id
                            self.sound_service.play("click")
                            break

                # 2. Proposition toggling in Center Panel (x=305)
                pool = self._build_proposition_pool()
                filtered = [item for item in pool if self.active_category_filter == "ALL" or item["cat"] == self.active_category_filter]
                start_idx = self.page_index * self.items_per_page
                current_page_items = filtered[start_idx : start_idx + self.items_per_page]

                for j, item in enumerate(current_page_items):
                    c_rect = pygame.Rect(305, 102 + j * 78, 480, 70)
                    if c_rect.collidepoint(event.pos):
                        self._toggle_proposition(item)
                        break

                # 3. Remove equipped premise in Right Panel (x=805)
                for k, fact in enumerate(self.selected_premises[:5]):
                    rem_btn = pygame.Rect(1035, 140 + k * 46, 24, 24)
                    if rem_btn.collidepoint(event.pos):
                        self.selected_premises.remove(fact)
                        self.sound_service.play("click")
                        break

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.nav_bar.update(dt)
        self.btn_filt_all.update(dt)
        self.btn_filt_means.update(dt)
        self.btn_filt_opp.update(dt)
        self.btn_filt_mot.update(dt)
        self.btn_prev_page.update(dt)
        self.btn_next_page.update(dt)
        self.text_box.update(dt)
        self.btn_add_custom.update(dt)
        self.btn_auto_populate.update(dt)
        self.btn_clear.update(dt)
        self.btn_submit.update(dt)
        self.particles.update(dt)

    def draw(self) -> None:
        from components.ui_shapes import draw_chamfered_rect
        self.screen.fill(BACKGROUND)
        self.nav_bar.draw(self.screen)

        case = self.game_state.current_case
        if not case:
            return

        # =====================================================================
        # PANEL 1: TARGET ACCUSED & LEGAL CHARGE (Left: x=25, w=268, h=555)
        # =====================================================================
        p1 = pygame.Rect(25, 58, 268, 555)
        draw_chamfered_rect(self.screen, p1, CARD_BG, GOLD_LIGHT, cut=8, border_width=1)

        self.screen.blit(get_font(13, bold=True).render("1. SELECT ACCUSED", True, GOLD), (p1.x + 12, p1.y + 12))

        # Suspect Cards
        for i, s in enumerate(case.suspects):
            is_sel = (s.id == self.selected_suspect_id)
            s_rect = pygame.Rect(p1.x + 10, p1.y + 36 + i * 46, p1.width - 20, 40)
            bg = (140, 95, 45) if is_sel else (38, 28, 24)
            bdr = GOLD if is_sel else (75, 60, 50)
            draw_chamfered_rect(self.screen, s_rect, bg, bdr, cut=6, border_width=2 if is_sel else 1)

            self.screen.blit(get_font(12, bold=True).render(f"👤 {s.name}", True, WHITE), (s_rect.x + 10, s_rect.y + 6))
            self.screen.blit(get_font(10).render(f"{s.occupation}", True, LIGHT_PARCHMENT), (s_rect.x + 10, s_rect.y + 22))

            if is_sel:
                tag_rect = pygame.Rect(s_rect.right - 80, s_rect.y + 9, 72, 22)
                pygame.draw.rect(self.screen, (30, 95, 45), tag_rect, border_radius=4)
                self.screen.blit(get_font(10, bold=True).render("ACCUSED ⚔", True, WHITE), (tag_rect.x + 6, tag_rect.y + 4))

        # Target Legal Charge Box
        charge_y = p1.y + 235
        self.screen.blit(get_font(12, bold=True).render("LEGAL CHARGE:", True, GOLD), (p1.x + 12, charge_y))
        c_box = pygame.Rect(p1.x + 10, charge_y + 20, p1.width - 20, 70)
        draw_chamfered_rect(self.screen, c_box, (30, 42, 30), ACCENT_GREEN, cut=6, border_width=1)
        self.screen.blit(get_font(12, bold=True).render("Guilty Beyond Doubt", True, WHITE), (c_box.x + 10, c_box.y + 10))
        self.screen.blit(get_font(10).render("Requires Method + Access + Motive", True, LIGHT_PARCHMENT), (c_box.x + 10, c_box.y + 32))
        self.screen.blit(get_font(10).render(f"Case Objective: #{case.id}", True, (160, 210, 160)), (c_box.x + 10, c_box.y + 48))

        # Trial Readiness Meter
        meter_y = charge_y + 105
        m_box = pygame.Rect(p1.x + 10, meter_y, p1.width - 20, 110)
        draw_chamfered_rect(self.screen, m_box, (30, 24, 22), (75, 60, 50), cut=6, border_width=1)

        premise_count = len(self.selected_premises)
        readiness_pct = min(100, int((premise_count / 3.0) * 100)) if premise_count > 0 else 0
        status_txt = "READY FOR TRIAL!" if readiness_pct >= 100 else f"{premise_count}/3 Pillars Equipped"

        self.screen.blit(get_font(11, bold=True).render("TRIAL READINESS:", True, GOLD), (m_box.x + 10, m_box.y + 10))
        self.screen.blit(get_font(16, bold=True).render(f"{readiness_pct}% READY", True, ACCENT_GREEN if readiness_pct >= 100 else GOLD), (m_box.x + 10, m_box.y + 28))

        # Progress bar
        bar_bg = pygame.Rect(m_box.x + 10, m_box.y + 56, m_box.width - 20, 12)
        pygame.draw.rect(self.screen, (20, 15, 12), bar_bg, border_radius=3)
        fill_w = int((m_box.width - 20) * (min(100, readiness_pct) / 100.0))
        if fill_w > 0:
            pygame.draw.rect(self.screen, ACCENT_GREEN if readiness_pct >= 100 else (220, 160, 40), (bar_bg.x, bar_bg.y, fill_w, 12), border_radius=3)

        self.screen.blit(get_font(10).render(status_txt, True, LIGHT_PARCHMENT), (m_box.x + 10, m_box.y + 78))

        # Action Buttons
        self.btn_auto_populate.draw(self.screen)
        self.btn_clear.draw(self.screen)

        # =====================================================================
        # PANEL 2: EVIDENCE & PROPOSITION POOL (Center: x=300, w=490, h=555)
        # =====================================================================
        p2 = pygame.Rect(300, 58, 490, 555)
        draw_chamfered_rect(self.screen, p2, CARD_BG, GOLD_LIGHT, cut=8, border_width=1)

        self.screen.blit(get_font(13, bold=True).render("2. PROPOSITION & EVIDENCE POOL", True, GOLD), (p2.x + 12, p2.y + 12))

        # Filter buttons
        self.btn_filt_all.draw(self.screen)
        self.btn_filt_means.draw(self.screen)
        self.btn_filt_opp.draw(self.screen)
        self.btn_filt_mot.draw(self.screen)

        # Proposition Cards
        pool = self._build_proposition_pool()
        filtered = [item for item in pool if self.active_category_filter == "ALL" or item["cat"] == self.active_category_filter]
        total_pages = max(1, (len(filtered) + self.items_per_page - 1) // self.items_per_page)
        self.page_index = min(self.page_index, total_pages - 1)

        start_idx = self.page_index * self.items_per_page
        page_items = filtered[start_idx : start_idx + self.items_per_page]

        for j, item in enumerate(page_items):
            fact = item["fact"]
            is_equipped = fact in self.selected_premises
            c_rect = pygame.Rect(p2.x + 10, 102 + j * 78, p2.width - 20, 70)

            bg = (38, 55, 38) if is_equipped else (34, 26, 22)
            bdr = ACCENT_GREEN if is_equipped else (70, 55, 45)
            draw_chamfered_rect(self.screen, c_rect, bg, bdr, cut=6, border_width=2 if is_equipped else 1)

            # Category badge
            cat = item["cat"]
            cat_col = (255, 140, 100) if cat == "MEANS" else ((100, 200, 255) if cat == "OPPORTUNITY" else (255, 215, 100))
            self.screen.blit(get_font(10, bold=True).render(f"[{cat}]", True, cat_col), (c_rect.x + 10, c_rect.y + 8))

            # Status pill
            status_str = "✓ EQUIPPED" if is_equipped else "+ CLICK TO ADD"
            status_col = ACCENT_GREEN if is_equipped else GOLD
            self.screen.blit(get_font(10, bold=True).render(status_str, True, status_col), (c_rect.right - 105, c_rect.y + 8))

            # Title
            self.screen.blit(get_font(12, bold=True).render(item["title"], True, WHITE), (c_rect.x + 10, c_rect.y + 26))

            # 1-line description
            self.screen.blit(get_font(10).render(item["desc"], True, LIGHT_PARCHMENT), (c_rect.x + 10, c_rect.y + 48))

        # Pagination Bar
        self.btn_prev_page.draw(self.screen)
        page_lbl = get_font(11, bold=True).render(f"Page {self.page_index + 1} of {total_pages}", True, GOLD)
        self.screen.blit(page_lbl, (p2.centerx - page_lbl.get_width() // 2, 532))
        self.btn_next_page.draw(self.screen)

        # Custom Manual Entry Bar
        self.text_box.draw(self.screen)
        self.btn_add_custom.draw(self.screen)

        # =====================================================================
        # PANEL 3: ASSEMBLED INDICTMENT & TRIAL (Right: x=798, w=278, h=555)
        # =====================================================================
        p3 = pygame.Rect(798, 58, 278, 555)
        draw_chamfered_rect(self.screen, p3, CARD_BG, GOLD_LIGHT, cut=8, border_width=1)

        self.screen.blit(get_font(13, bold=True).render("3. COURT INDICTMENT", True, GOLD), (p3.x + 12, p3.y + 12))

        # Subtitle counter
        prem_cnt_lbl = get_font(10).render(f"Active Premises: {len(self.selected_premises)}", True, LIGHT_PARCHMENT)
        self.screen.blit(prem_cnt_lbl, (p3.right - prem_cnt_lbl.get_width() - 14, p3.y + 14))

        # Display equipped premises
        if not self.selected_premises:
            empty_box = pygame.Rect(p3.x + 10, p3.y + 40, p3.width - 20, 140)
            pygame.draw.rect(self.screen, (28, 22, 18), empty_box, border_radius=6)
            self.screen.blit(get_font(11, bold=True).render("INDICTMENT IS EMPTY", True, MUTED_TEXT), (empty_box.x + 14, empty_box.y + 35))
            self.screen.blit(get_font(10).render("Select clues from center", True, LIGHT_PARCHMENT), (empty_box.x + 14, empty_box.y + 60))
            self.screen.blit(get_font(10).render("or click AUTO-EQUIP [A].", True, LIGHT_PARCHMENT), (empty_box.x + 14, empty_box.y + 78))
        else:
            for k, fact in enumerate(self.selected_premises[:6]):
                item_y = p3.y + 40 + k * 44
                i_rect = pygame.Rect(p3.x + 10, item_y, p3.width - 20, 38)
                draw_chamfered_rect(self.screen, i_rect, (35, 48, 35), ACCENT_GREEN, cut=4, border_width=1)

                # Find title
                title = PROPOSITION_META.get(fact, (fact.replace("_", " ").title(), "", ""))[0]
                if len(title) > 22:
                    title = title[:20] + "..."

                self.screen.blit(get_font(11, bold=True).render(f"• {title}", True, WHITE), (i_rect.x + 8, i_rect.y + 10))

                # Remove button (✕)
                rem_btn = pygame.Rect(i_rect.right - 28, i_rect.y + 7, 22, 22)
                pygame.draw.rect(self.screen, (60, 30, 25), rem_btn, border_radius=3)
                self.screen.blit(get_font(11, bold=True).render("✕", True, (240, 120, 100)), (rem_btn.x + 5, rem_btn.y + 2))

        # Integrated Watson Legal Advisor Box (Bottom Right)
        w_box = pygame.Rect(p3.x + 10, p3.bottom - 185, p3.width - 20, 115)
        draw_chamfered_rect(self.screen, w_box, (28, 22, 35), (150, 110, 200), cut=6, border_width=1)

        self.screen.blit(get_font(11, bold=True).render("💡 CLERK WATSON ADVISOR", True, (215, 185, 255)), (w_box.x + 10, w_box.y + 8))

        # Dynamic advice based on active premises
        has_means = any(f in self.selected_premises for f in PROPOSITION_META if PROPOSITION_META[f][1] == "MEANS")
        has_opp = any(f in self.selected_premises for f in PROPOSITION_META if PROPOSITION_META[f][1] == "OPPORTUNITY")
        has_mot = any(f in self.selected_premises for f in PROPOSITION_META if PROPOSITION_META[f][1] == "MOTIVE")

        if not has_opp:
            advice = "Counsel! We need proof of Access (CCTV or entry logs) to disprove their alibi."
        elif not has_means:
            advice = "Sir! Equip physical proof of Method (fingerprints or weapon traces)."
        elif not has_mot:
            advice = "Advise connecting financial debts or threat messages to establish intent."
        else:
            advice = "Splendid! Method, Access, and Motive are fully equipped! Enter trial now."

        # Wrap advice text
        words = advice.split(" ")
        lines, cur = [], []
        f_adv = get_font(10)
        for w in words:
            if f_adv.size(" ".join(cur + [w]))[0] > (w_box.width - 20):
                lines.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(" ".join(cur))

        ay = w_box.y + 28
        for line in lines[:3]:
            self.screen.blit(f_adv.render(line, True, LIGHT_PARCHMENT), (w_box.x + 10, ay))
            ay += 18

        # Primary Enter Trial Button
        self.btn_submit.draw(self.screen)

        # Ambient Particles
        self.particles.draw(self.screen)
