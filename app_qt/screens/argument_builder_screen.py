"""Argument Workshop & Indictment Builder Screen for PySide6 LOGIC COURTROOM.
Modern 3-panel deductive workspace:
1. Target Accused & Legal Charge & Trial Readiness
2. Forensic Evidence & Proposition Pool (Categorized & Filtered)
3. Assembled Court Indictment with Clerk Watson Advisor & Trial Entry
"""

from typing import Optional, List, Set, Dict, Any
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QLineEdit, QProgressBar, QSizePolicy
)

from models.argument import Argument
from services.game_state import GameState
from services.save_service import SaveService
from ai_engine.argument_parser import ArgumentParser
from app_qt.config import (
    COLOR_BG_CARD, COLOR_BG_PANEL, COLOR_BORDER, COLOR_GOLD, COLOR_GOLD_LIGHT,
    COLOR_GOLD_DARK, COLOR_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_PARCHMENT,
    COLOR_ACCENT_GREEN, COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, get_qt_font
)
from app_qt.services.sound_service_qt import get_sound_service_qt


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


class ArgumentBuilderScreenQt(QWidget):
    """3-Panel Argument Builder and Trial Indictment screen."""

    navigate = Signal(str)
    notify = Signal(str, str)

    def __init__(self, game_state: GameState, save_service: Optional[SaveService] = None, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service_qt()
        self.argument_parser = ArgumentParser()

        self.selected_suspect_id: Optional[str] = None
        self.selected_evidence_ids: Set[str] = set()
        self.selected_premises: List[str] = []
        self.selected_conclusion: str = "suspect_guilty_beyond_reasonable_doubt"
        self.active_category_filter = "ALL"

        self.suspect_buttons: List[QPushButton] = []

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(12)

        # 1. Top Header
        header_layout = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_lbl = QLabel("ARGUMENT WORKSHOP & INDICTMENT BUILDER")
        title_lbl.setFont(get_qt_font(18, bold=True))
        title_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()}; letter-spacing: 1px;")

        sub_lbl = QLabel("Construct a rigorous legal deduction by equipping Method, Access, and Motive premises.")
        sub_lbl.setFont(get_qt_font(10))
        sub_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED.name()};")
        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)
        header_layout.addLayout(title_col)

        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # 2. Main 3-Panel Horizontal Layout
        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(12)

        # ==========================================
        # PANEL 1: TARGET ACCUSED & TRIAL READINESS
        # ==========================================
        panel1 = QFrame()
        panel1.setFixedWidth(270)
        panel1.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        p1_layout = QVBoxLayout(panel1)
        p1_layout.setContentsMargins(14, 14, 14, 14)
        p1_layout.setSpacing(10)

        p1_header = QLabel("1. SELECT ACCUSED")
        p1_header.setFont(get_qt_font(12, bold=True))
        p1_header.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        p1_layout.addWidget(p1_header)

        # Suspects buttons list
        self.suspects_box = QVBoxLayout()
        self.suspects_box.setSpacing(6)
        p1_layout.addLayout(self.suspects_box)

        # Legal Charge Box
        charge_box = QFrame()
        charge_box.setStyleSheet(f"background-color: #172817; border: 1px solid {COLOR_ACCENT_GREEN.name()}; border-radius: 6px; padding: 10px;")
        ch_layout = QVBoxLayout(charge_box)
        ch_layout.setSpacing(3)

        ch_badge = QLabel("LEGAL CHARGE:")
        ch_badge.setFont(get_qt_font(9, bold=True))
        ch_badge.setStyleSheet(f"color: {COLOR_ACCENT_GREEN.name()};")
        ch_layout.addWidget(ch_badge)

        ch_title = QLabel("Guilty Beyond Doubt")
        ch_title.setFont(get_qt_font(11, bold=True))
        ch_title.setStyleSheet("color: #ffffff;")
        ch_layout.addWidget(ch_title)

        ch_desc = QLabel("Requires Method + Access + Motive")
        ch_desc.setFont(get_qt_font(9))
        ch_desc.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        ch_layout.addWidget(ch_desc)

        p1_layout.addWidget(charge_box)

        # Trial Readiness Meter
        meter_box = QFrame()
        meter_box.setStyleSheet("background-color: #1a120c; border: 1px solid #3d2b1f; border-radius: 6px; padding: 10px;")
        m_layout = QVBoxLayout(meter_box)
        m_layout.setSpacing(6)

        m_title = QLabel("TRIAL READINESS:")
        m_title.setFont(get_qt_font(10, bold=True))
        m_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        m_layout.addWidget(m_title)

        self.lbl_readiness_pct = QLabel("0% READY")
        self.lbl_readiness_pct.setFont(get_qt_font(14, bold=True))
        self.lbl_readiness_pct.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        m_layout.addWidget(self.lbl_readiness_pct)

        self.progress_readiness = QProgressBar()
        self.progress_readiness.setRange(0, 100)
        self.progress_readiness.setValue(0)
        self.progress_readiness.setFixedHeight(10)
        self.progress_readiness.setTextVisible(False)
        self.progress_readiness.setStyleSheet(f"""
            QProgressBar {{
                background-color: #120d09;
                border: 1px solid #3d2b1f;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_ACCENT_GREEN.name()};
                border-radius: 3px;
            }}
        """)
        m_layout.addWidget(self.progress_readiness)

        self.lbl_pillars_status = QLabel("0/3 Pillars Equipped")
        self.lbl_pillars_status.setFont(get_qt_font(9))
        self.lbl_pillars_status.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        m_layout.addWidget(self.lbl_pillars_status)

        p1_layout.addWidget(meter_box)
        p1_layout.addStretch()

        # Left Action buttons
        btn_auto = QPushButton("⚡ AUTO-EQUIP CLUES [A]")
        btn_auto.setFont(get_qt_font(10, bold=True))
        btn_auto.setStyleSheet("padding: 8px; background-color: #6d4420; color: #fff; border: 1px solid #c9a050; border-radius: 4px;")
        btn_auto.clicked.connect(self._auto_fill_collected)
        p1_layout.addWidget(btn_auto)

        btn_clear = QPushButton("✕ CLEAR INDICTMENT [C]")
        btn_clear.setFont(get_qt_font(10, bold=True))
        btn_clear.setStyleSheet("padding: 7px; background-color: #4a2222; color: #ff8888; border: 1px solid #883333; border-radius: 4px;")
        btn_clear.clicked.connect(self._clear_premises)
        p1_layout.addWidget(btn_clear)

        panels_layout.addWidget(panel1)

        # ==========================================
        # PANEL 2: EVIDENCE & PROPOSITION POOL
        # ==========================================
        panel2 = QFrame()
        panel2.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        p2_layout = QVBoxLayout(panel2)
        p2_layout.setContentsMargins(14, 14, 14, 14)
        p2_layout.setSpacing(10)

        p2_header = QLabel("2. PROPOSITION & EVIDENCE POOL")
        p2_header.setFont(get_qt_font(12, bold=True))
        p2_header.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        p2_layout.addWidget(p2_header)

        # Filter buttons bar
        filt_bar = QHBoxLayout()
        filt_bar.setSpacing(6)

        self.btn_filt_all = QPushButton("ALL")
        self.btn_filt_all.setFont(get_qt_font(9, bold=True))
        self.btn_filt_all.clicked.connect(lambda: self._set_filter("ALL"))
        filt_bar.addWidget(self.btn_filt_all)

        self.btn_filt_means = QPushButton("🗡 METHOD")
        self.btn_filt_means.setFont(get_qt_font(9, bold=True))
        self.btn_filt_means.clicked.connect(lambda: self._set_filter("MEANS"))
        filt_bar.addWidget(self.btn_filt_means)

        self.btn_filt_opp = QPushButton("🚪 ACCESS")
        self.btn_filt_opp.setFont(get_qt_font(9, bold=True))
        self.btn_filt_opp.clicked.connect(lambda: self._set_filter("OPPORTUNITY"))
        filt_bar.addWidget(self.btn_filt_opp)

        self.btn_filt_mot = QPushButton("💰 MOTIVE")
        self.btn_filt_mot.setFont(get_qt_font(9, bold=True))
        self.btn_filt_mot.clicked.connect(lambda: self._set_filter("MOTIVE"))
        filt_bar.addWidget(self.btn_filt_mot)

        p2_layout.addLayout(filt_bar)
        self._update_filter_button_styles()

        # Proposition Scroll Area
        scroll_prop = QScrollArea()
        scroll_prop.setWidgetResizable(True)
        scroll_prop.setStyleSheet("background-color: transparent; border: none;")

        self.prop_container = QWidget()
        self.prop_layout = QVBoxLayout(self.prop_container)
        self.prop_layout.setSpacing(8)
        self.prop_layout.addStretch()

        scroll_prop.setWidget(self.prop_container)
        p2_layout.addWidget(scroll_prop, stretch=1)

        # Custom argument line input bar
        custom_bar = QHBoxLayout()
        custom_bar.setSpacing(6)

        self.txt_custom = QLineEdit()
        self.txt_custom.setFont(get_qt_font(10))
        self.txt_custom.setPlaceholderText("Type custom legal proposition statement...")
        self.txt_custom.setStyleSheet(f"""
            QLineEdit {{
                background-color: #17110e;
                color: #e6d3a3;
                border: 1px solid #3d2b1f;
                border-radius: 4px;
                padding: 6px 10px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_GOLD.name()};
            }}
        """)
        self.txt_custom.returnPressed.connect(self._add_custom_argument)
        custom_bar.addWidget(self.txt_custom, stretch=1)

        btn_add_custom = QPushButton("+ ADD")
        btn_add_custom.setFont(get_qt_font(10, bold=True))
        btn_add_custom.setStyleSheet("padding: 6px 14px; background-color: #1e3a5f; color: #fff; border: 1px solid #3a75b4; border-radius: 4px;")
        btn_add_custom.clicked.connect(self._add_custom_argument)
        custom_bar.addWidget(btn_add_custom)

        p2_layout.addLayout(custom_bar)
        panels_layout.addWidget(panel2, stretch=2)

        # ==========================================
        # PANEL 3: ASSEMBLED INDICTMENT & TRIAL
        # ==========================================
        panel3 = QFrame()
        panel3.setFixedWidth(280)
        panel3.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        p3_layout = QVBoxLayout(panel3)
        p3_layout.setContentsMargins(14, 14, 14, 14)
        p3_layout.setSpacing(10)

        p3_top = QHBoxLayout()
        p3_header = QLabel("3. COURT INDICTMENT")
        p3_header.setFont(get_qt_font(12, bold=True))
        p3_header.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        p3_top.addWidget(p3_header)

        self.lbl_premise_count = QLabel("0 Premises")
        self.lbl_premise_count.setFont(get_qt_font(9))
        self.lbl_premise_count.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        p3_top.addWidget(self.lbl_premise_count, alignment=Qt.AlignRight)
        p3_layout.addLayout(p3_top)

        # Equipped premises scroll list
        scroll_indict = QScrollArea()
        scroll_indict.setWidgetResizable(True)
        scroll_indict.setStyleSheet("background-color: transparent; border: none;")

        self.indict_container = QWidget()
        self.indict_layout = QVBoxLayout(self.indict_container)
        self.indict_layout.setSpacing(6)
        self.indict_layout.addStretch()

        scroll_indict.setWidget(self.indict_container)
        p3_layout.addWidget(scroll_indict, stretch=1)

        # Clerk Watson Legal Advisor Box
        self.watson_box = QFrame()
        self.watson_box.setStyleSheet("background-color: #1f1828; border: 1px solid #7848a0; border-radius: 6px; padding: 10px;")
        w_layout = QVBoxLayout(self.watson_box)
        w_layout.setSpacing(4)

        w_header = QLabel("💡 CLERK WATSON ADVISOR")
        w_header.setFont(get_qt_font(9, bold=True))
        w_header.setStyleSheet("color: #d8b8ff;")
        w_layout.addWidget(w_header)

        self.lbl_watson_advice = QLabel("Counsel! We need proof of Access (CCTV or entry logs) to disprove their alibi.")
        self.lbl_watson_advice.setFont(get_qt_font(9))
        self.lbl_watson_advice.setWordWrap(True)
        self.lbl_watson_advice.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        w_layout.addWidget(self.lbl_watson_advice)

        p3_layout.addWidget(self.watson_box)

        # Primary Enter Trial Button
        self.btn_submit = QPushButton("⚔️ ENTER TRIAL (COURT) ➔")
        self.btn_submit.setFont(get_qt_font(11, bold=True))
        self.btn_submit.setFixedHeight(44)
        self.btn_submit.setStyleSheet(f"background-color: {COLOR_ACCENT_GREEN.name()}; color: #ffffff; border: 1px solid #70c070; border-radius: 6px;")
        self.btn_submit.clicked.connect(self._submit)
        p3_layout.addWidget(self.btn_submit)

        panels_layout.addWidget(panel3)
        main_layout.addLayout(panels_layout, stretch=1)

    def _set_filter(self, mode: str):
        self.active_category_filter = mode
        self.sound_service.play("click")
        self._update_filter_button_styles()
        self._render_proposition_pool()

    def _update_filter_button_styles(self):
        for btn, mode, active_col in [
            (self.btn_filt_all, "ALL", "#5a381e"),
            (self.btn_filt_means, "MEANS", "#6b3322"),
            (self.btn_filt_opp, "OPPORTUNITY", "#224466"),
            (self.btn_filt_mot, "MOTIVE", "#555022")
        ]:
            if self.active_category_filter == mode:
                btn.setStyleSheet(f"padding: 5px 10px; background-color: {active_col}; color: #fff; border: 1px solid #c9a050; border-radius: 4px;")
            else:
                btn.setStyleSheet("padding: 5px 10px; background-color: #211713; color: #a08c70; border: 1px solid #3d2b1f; border-radius: 4px;")

    def _build_proposition_pool(self) -> List[Dict[str, Any]]:
        case = self.game_state.current_case
        if not case:
            return []

        pool = []
        seen_facts = set()

        for ev in case.evidence_list:
            unlocked = getattr(ev, "unlocked_facts", None) or getattr(ev, "facts_unlocked", [])
            for fact in unlocked:
                if fact not in seen_facts:
                    seen_facts.add(fact)
                    if fact in PROPOSITION_META:
                        title, cat, desc = PROPOSITION_META[fact]
                    else:
                        title = fact.replace("_", " ").title()
                        cat = "MEANS" if "knife" in fact or "weapon" in fact else "OPPORTUNITY"
                        desc = f"Forensic artifact unlocked from {ev.name}."
                    pool.append({"fact": fact, "title": title, "cat": cat, "desc": desc, "evidence_id": ev.id})

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

    def _render_suspects(self):
        case = self.game_state.current_case
        if not case:
            return

        # Clear existing
        while self.suspects_box.count() > 0:
            child = self.suspects_box.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.suspect_buttons.clear()

        for s in case.suspects:
            is_sel = (s.id == self.selected_suspect_id)
            btn = QPushButton(f"👤 {s.name}\n({s.occupation})")
            btn.setFont(get_qt_font(10, bold=is_sel))
            btn.setCheckable(True)
            btn.setChecked(is_sel)
            btn.clicked.connect(lambda checked=False, s_id=s.id: self._select_suspect(s_id))
            self._style_suspect_button(btn, is_sel)
            self.suspect_buttons.append(btn)
            self.suspects_box.addWidget(btn)

    def _style_suspect_button(self, btn: QPushButton, is_sel: bool):
        if is_sel:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6b4420;
                    border: 2px solid #d4af37;
                    border-radius: 6px;
                    color: #ffffff;
                    text-align: left;
                    padding: 8px;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e1510;
                    border: 1px solid #3d2b1f;
                    border-radius: 6px;
                    color: #c0b090;
                    text-align: left;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #2b1f14;
                    border-color: #704222;
                }
            """)

    def _select_suspect(self, suspect_id: str):
        self.selected_suspect_id = suspect_id
        self.game_state.selected_suspect_id = suspect_id
        self.sound_service.play("click")
        self._render_suspects()
        self._render_proposition_pool()

    def _render_proposition_pool(self):
        while self.prop_layout.count() > 1:
            child = self.prop_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        pool = self._build_proposition_pool()
        filtered = [item for item in pool if self.active_category_filter == "ALL" or item["cat"] == self.active_category_filter]

        for item in filtered:
            fact = item["fact"]
            is_equipped = fact in self.selected_premises

            card = QFrame()
            bg_col = "#1b2a1b" if is_equipped else "#1c140f"
            bdr_col = COLOR_ACCENT_GREEN.name() if is_equipped else "#3d2b1f"
            card.setStyleSheet(f"background-color: {bg_col}; border: 1px solid {bdr_col}; border-radius: 6px; padding: 8px;")

            c_layout = QVBoxLayout(card)
            c_layout.setSpacing(3)

            top_row = QHBoxLayout()
            cat = item["cat"]
            cat_col = "#ff8c64" if cat == "MEANS" else ("#64c8ff" if cat == "OPPORTUNITY" else "#ffd764")
            cat_lbl = QLabel(f"[{cat}]")
            cat_lbl.setFont(get_qt_font(9, bold=True))
            cat_lbl.setStyleSheet(f"color: {cat_col};")
            top_row.addWidget(cat_lbl)

            btn_toggle = QPushButton("✓ EQUIPPED" if is_equipped else "+ EQUIP")
            btn_toggle.setFont(get_qt_font(9, bold=True))
            btn_toggle.setFixedWidth(90)
            if is_equipped:
                btn_toggle.setStyleSheet("background-color: #1e4a1e; color: #fff; border: 1px solid #3d8c3d; border-radius: 4px; padding: 3px;")
            else:
                btn_toggle.setStyleSheet("background-color: #3d2b1f; color: #c9a050; border: 1px solid #6b4420; border-radius: 4px; padding: 3px;")
            btn_toggle.clicked.connect(lambda checked=False, it=item: self._toggle_proposition(it))
            top_row.addWidget(btn_toggle, alignment=Qt.AlignRight)
            c_layout.addLayout(top_row)

            title_lbl = QLabel(item["title"])
            title_lbl.setFont(get_qt_font(11, bold=True))
            title_lbl.setStyleSheet(f"color: {COLOR_WHITE.name()};")
            c_layout.addWidget(title_lbl)

            desc_lbl = QLabel(item["desc"])
            desc_lbl.setFont(get_qt_font(9))
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
            c_layout.addWidget(desc_lbl)

            self.prop_layout.insertWidget(self.prop_layout.count() - 1, card)

    def _render_indictment(self):
        while self.indict_layout.count() > 1:
            child = self.indict_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.lbl_premise_count.setText(f"{len(self.selected_premises)} Premises")

        if not self.selected_premises:
            empty_lbl = QLabel("Indictment is empty.\nClick + EQUIP or AUTO-EQUIP [A].")
            empty_lbl.setFont(get_qt_font(10, italic=True))
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED.name()}; padding: 20px 0;")
            self.indict_layout.insertWidget(0, empty_lbl)
        else:
            for fact in self.selected_premises:
                row = QFrame()
                row.setStyleSheet(f"background-color: #172417; border: 1px solid {COLOR_ACCENT_GREEN.name()}; border-radius: 4px; padding: 4px;")
                r_layout = QHBoxLayout(row)
                r_layout.setContentsMargins(6, 4, 6, 4)

                title = PROPOSITION_META.get(fact, (fact.replace("_", " ").title(), "", ""))[0]
                lbl = QLabel(f"• {title}")
                lbl.setFont(get_qt_font(10, bold=True))
                lbl.setStyleSheet("color: #ffffff;")
                r_layout.addWidget(lbl, stretch=1)

                btn_del = QPushButton("✕")
                btn_del.setFont(get_qt_font(9, bold=True))
                btn_del.setFixedSize(20, 20)
                btn_del.setStyleSheet("background-color: #4a2222; color: #ff8888; border: 1px solid #883333; border-radius: 3px;")
                btn_del.clicked.connect(lambda checked=False, f=fact: self._remove_premise(f))
                r_layout.addWidget(btn_del)

                self.indict_layout.insertWidget(self.indict_layout.count() - 1, row)

        self._update_readiness_and_watson()

    def _update_readiness_and_watson(self):
        count = len(self.selected_premises)
        pct = min(100, int((count / 3.0) * 100)) if count > 0 else 0
        self.progress_readiness.setValue(pct)
        self.lbl_readiness_pct.setText(f"{pct}% READY")
        self.lbl_pillars_status.setText(f"{min(3, count)}/3 Pillars Equipped")

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
            advice = "Splendid! Method, Access, and Motive are fully equipped! Demand a verdict in court."

        self.lbl_watson_advice.setText(advice)

    def _toggle_proposition(self, item: Dict[str, Any]):
        fact = item["fact"]
        ev_id = item.get("evidence_id")

        if fact in self.selected_premises:
            self.selected_premises.remove(fact)
            if ev_id and ev_id in self.selected_evidence_ids:
                pool = self._build_proposition_pool()
                other_uses = any(
                    other["fact"] in self.selected_premises and other.get("evidence_id") == ev_id
                    for other in pool
                )
                if not other_uses:
                    self.selected_evidence_ids.discard(ev_id)
            self.sound_service.play("click")
        else:
            self.selected_premises.append(fact)
            if ev_id:
                self.selected_evidence_ids.add(ev_id)
            self.sound_service.play("evidence")

        self._render_proposition_pool()
        self._render_indictment()

    def _remove_premise(self, fact: str):
        if fact in self.selected_premises:
            self.selected_premises.remove(fact)
            self.sound_service.play("click")
            self._render_proposition_pool()
            self._render_indictment()

    def _auto_fill_collected(self):
        self.selected_premises.clear()
        self.selected_evidence_ids.clear()

        pool = self._build_proposition_pool()
        for item in pool:
            self.selected_premises.append(item["fact"])
            if item.get("evidence_id"):
                self.selected_evidence_ids.add(item["evidence_id"])

        self.game_state.progress.record_argument_drafted(is_valid=True)
        self.sound_service.play("evidence")
        self._render_proposition_pool()
        self._render_indictment()
        self.notify.emit("SUCCESS", "All forensic clues equipped into indictment!")

    def _clear_premises(self):
        self.selected_premises.clear()
        self.selected_evidence_ids.clear()
        self.sound_service.play("click")
        self._render_proposition_pool()
        self._render_indictment()

    def _add_custom_argument(self):
        txt = self.txt_custom.text().strip()
        if not txt:
            self.notify.emit("WARNING", "Please type a custom argument statement!")
            return
        parsed_id, conf, exp = self.argument_parser.parse_sentence(txt)
        if parsed_id not in self.selected_premises:
            self.selected_premises.append(parsed_id)
            self.sound_service.play("evidence")
            self.notify.emit("SUCCESS", f"Custom premise registered: {parsed_id}")
            self._render_proposition_pool()
            self._render_indictment()
        self.txt_custom.clear()

    def _submit(self):
        if not self.selected_suspect_id:
            if self.game_state.current_case and self.game_state.current_case.suspects:
                self.selected_suspect_id = self.game_state.current_case.suspects[0].id
                self.game_state.selected_suspect_id = self.selected_suspect_id
            else:
                self.selected_suspect_id = "SUS-001"

        premises_list = list(self.selected_premises)
        if not premises_list:
            self._auto_fill_collected()
            premises_list = list(self.selected_premises)

        conclusion = self.selected_conclusion
        if not conclusion and self.game_state.current_case:
            conclusion = self.game_state.current_case.solution_conclusion
        if not conclusion:
            conclusion = "suspect_guilty_beyond_reasonable_doubt"

        arg = Argument(
            suspect_id=self.selected_suspect_id,
            premises=premises_list,
            conclusion=conclusion,
            selected_evidence_ids=list(self.selected_evidence_ids),
            custom_text=""
        )

        self.game_state.current_argument = arg
        self.game_state.progress.record_argument_drafted(is_valid=True)
        self.save_service.save_active_game(self.game_state)
        self.sound_service.play("gavel")
        self.navigate.emit("courtroom")

    def on_enter_screen(self):
        """Called when this screen becomes active."""
        if self.game_state.current_case:
            if not self.selected_suspect_id and self.game_state.current_case.suspects:
                self.selected_suspect_id = self.game_state.selected_suspect_id or self.game_state.current_case.suspects[0].id
            self.selected_conclusion = self.game_state.current_case.solution_conclusion

        self._render_suspects()
        if not self.selected_premises:
            self._auto_fill_collected()
        else:
            self._render_proposition_pool()
            self._render_indictment()

