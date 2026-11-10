"""Game State Management for LOGIC COURTROOM.
Preserves active case, collected evidence inventory, selected suspects,
player profile, arguments, investigation progress, and courtroom verdict results.
"""

from typing import Optional, Set, List, Dict, Any
from models.case import Case
from models.evidence import Evidence
from models.suspect import Suspect
from models.argument import Argument
from models.profile import PlayerProfile
from ai_engine.knowledge_base import KnowledgeBase, Rule
from ai_engine.rule_engine import STANDARD_RULES
from services.progress_service import ProgressService

class GameState:
    """Central singleton/manager for active gameplay session state and progress."""

    def __init__(self, profile: Optional[PlayerProfile] = None):
        self.profile: PlayerProfile = profile or PlayerProfile()
        self.player_name: str = self.profile.name
        self.current_case: Optional[Case] = None
        self.collected_evidence_ids: Set[str] = set()
        self.selected_suspect_id: Optional[str] = None
        self.current_argument: Optional[Argument] = None
        self.submitted_arguments: List[Argument] = []
        self.trial_transcript: List[Dict[str, Any]] = []
        self.last_verdict_result: Optional[Dict[str, Any]] = None
        self.warning_count: int = 0
        self.knowledge_base: KnowledgeBase = KnowledgeBase()
        self.progress: ProgressService = ProgressService()
        self.notification_message: Optional[str] = None
        self.notification_category: str = "INFO"
        self.notification_timer: int = 0

    def set_case(self, case: Case) -> None:
        """Sets the active case and initializes evidence collection, progress, and KnowledgeBase."""
        self.current_case = case
        self.collected_evidence_ids.clear()
        self.selected_suspect_id = case.suspects[0].id if case.suspects else None
        self.current_argument = None
        self.submitted_arguments.clear()
        self.trial_transcript.clear()
        self.last_verdict_result = None
        self.warning_count = 0
        self.progress.reset_for_new_case()

        # Re-initialize KnowledgeBase with case rules and initial facts
        self.knowledge_base = KnowledgeBase()
        for r in STANDARD_RULES:
            self.knowledge_base.add_rule(r)

        for custom_rule_dict in case.rules:
            self.knowledge_base.add_rule(Rule.from_dict(custom_rule_dict))

        for fact in case.initial_facts:
            self.knowledge_base.tell(fact)

    def restore_from_save(self, case: Case, save_data: Dict[str, Any]) -> None:
        """Restores in-progress case state from save data dictionary."""
        self.set_case(case)
        collected = save_data.get("collected_evidence_ids", [])
        for ev_id in collected:
            self.collect_evidence(ev_id)

        self.selected_suspect_id = save_data.get("selected_suspect_id", self.selected_suspect_id)
        self.warning_count = int(save_data.get("warning_count", 0))
        self.trial_transcript = save_data.get("trial_transcript", [])

        if "progress" in save_data:
            self.progress = ProgressService.from_dict(save_data["progress"])

    def collect_evidence(self, evidence_id: str) -> bool:
        """Marks evidence as collected and asserts unlocked facts into the KnowledgeBase."""
        if not self.current_case:
            return False

        ev = self.current_case.get_evidence(evidence_id)
        if not ev:
            return False

        if evidence_id not in self.collected_evidence_ids:
            self.collected_evidence_ids.add(evidence_id)
            ev.collected = True
            for fact in ev.facts_unlocked:
                self.knowledge_base.tell(fact)
            self.progress.record_evidence_collected(evidence_id)
            return True
        return False

    def is_evidence_collected(self, evidence_id: str) -> bool:
        return evidence_id in self.collected_evidence_ids

    def get_collected_evidence_objects(self) -> List[Evidence]:
        if not self.current_case:
            return []
        return [
            e for e in self.current_case.evidence_list
            if e.id in self.collected_evidence_ids
        ]

    def get_selected_suspect(self) -> Optional[Suspect]:
        if not self.current_case or not self.selected_suspect_id:
            return None
        return self.current_case.get_suspect(self.selected_suspect_id)

    def get_unlocked_facts(self) -> Set[str]:
        facts = set(self.knowledge_base.get_facts())
        return facts

    def set_notification(self, message: str, category: str = "INFO", duration_frames: int = 150) -> None:
        self.notification_message = message
        self.notification_category = category
        self.notification_timer = duration_frames

    def update(self) -> None:
        if self.notification_timer > 0:
            self.notification_timer -= 1
            if self.notification_timer <= 0:
                self.notification_message = None
