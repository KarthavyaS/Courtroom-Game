"""Progress Service for LOGIC COURTROOM.
Tracks player progress through the multi-stage case investigation journey:
1. Briefing -> 2. Crime Scene -> 3. Suspects -> 4. Evidence -> 5. Case Board -> 6. Arguments -> 7. Courtroom -> 8. Results
"""

from typing import Dict, Any, List, Set, Optional

class ProgressService:
    """Manages investigation milestones, completion percentages, and contextual guidance."""

    STAGES = [
        ("briefing", "Case Briefing"),
        ("crime_scene", "Crime Scene Exploration"),
        ("suspects", "Suspect Interrogations"),
        ("evidence", "Evidence Analysis"),
        ("case_board", "Case Board Connections"),
        ("arguments", "Argument Preparation"),
        ("courtroom", "Courtroom Hearing"),
        ("results", "Verdict & Case Results")
    ]

    def __init__(self):
        self.briefing_read: bool = False
        self.crime_scene_explored: bool = False
        self.suspects_reviewed: bool = False
        self.evidence_reviewed: bool = False
        self.case_board_reviewed: bool = False
        self.argument_prepared: bool = False
        self.courtroom_completed: bool = False
        self.current_stage: str = "briefing"

        # Detailed tracking sets
        self.inspected_evidence_ids: Set[str] = set()
        self.interviewed_suspect_ids: Set[str] = set()
        self.suspect_qa_history: Dict[str, List[str]] = {}
        self.player_notes: str = ""

    def reset_for_new_case(self) -> None:
        self.briefing_read = False
        self.crime_scene_explored = False
        self.suspects_reviewed = False
        self.evidence_reviewed = False
        self.case_board_reviewed = False
        self.argument_prepared = False
        self.courtroom_completed = False
        self.current_stage = "briefing"
        self.inspected_evidence_ids.clear()
        self.interviewed_suspect_ids.clear()
        self.suspect_qa_history.clear()
        self.player_notes = ""

    def mark_briefing_read(self) -> None:
        self.briefing_read = True
        if self.current_stage == "briefing":
            self.current_stage = "crime_scene"

    def record_evidence_inspected(self, evidence_id: str, total_evidence_count: int = 1) -> None:
        self.inspected_evidence_ids.add(evidence_id)
        if len(self.inspected_evidence_ids) >= 1:
            self.crime_scene_explored = True

    def record_evidence_collected(self, evidence_id: str) -> None:
        self.inspected_evidence_ids.add(evidence_id)
        self.crime_scene_explored = True
        self.evidence_reviewed = True

    def record_suspect_interview(self, suspect_id: str, question_id: str, total_suspect_count: int = 1) -> None:
        self.interviewed_suspect_ids.add(suspect_id)
        if suspect_id not in self.suspect_qa_history:
            self.suspect_qa_history[suspect_id] = []
        if question_id not in self.suspect_qa_history[suspect_id]:
            self.suspect_qa_history[suspect_id].append(question_id)

        if total_suspect_count > 0 and len(self.interviewed_suspect_ids) >= total_suspect_count:
            self.suspects_reviewed = True

    def record_case_board_opened(self) -> None:
        self.case_board_reviewed = True

    def record_argument_drafted(self, is_valid: bool = True) -> None:
        if is_valid:
            self.argument_prepared = True

    def record_courtroom_finished(self) -> None:
        self.courtroom_completed = True
        self.current_stage = "results"

    def calculate_progress_percentage(self) -> int:
        """Returns integer 0-100 indicating investigation completion."""
        weights = [
            (self.briefing_read, 10),
            (self.crime_scene_explored, 20),
            (self.suspects_reviewed, 20),
            (self.evidence_reviewed, 15),
            (self.case_board_reviewed, 10),
            (self.argument_prepared, 15),
            (self.courtroom_completed, 10)
        ]
        score = sum(w for done, w in weights if done)
        return min(100, score)

    def get_checklist_items(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "briefing",
                "label": "Read Case Briefing",
                "done": self.briefing_read,
                "hint": "Understand the incident details and investigation objective."
            },
            {
                "id": "crime_scene",
                "label": "Explore Crime Scene",
                "done": self.crime_scene_explored,
                "hint": "Inspect scene hotspots and collect physical clues."
            },
            {
                "id": "suspects",
                "label": "Interrogate Suspects",
                "done": self.suspects_reviewed,
                "hint": "Question suspects to find inconsistencies in their alibis."
            },
            {
                "id": "evidence",
                "label": "Analyze Collected Evidence",
                "done": self.evidence_reviewed,
                "hint": "Review forensic laboratory findings and unlocked facts."
            },
            {
                "id": "case_board",
                "label": "Examine Case Board",
                "done": self.case_board_reviewed,
                "hint": "Review visual connections between suspects, evidence, and contradictions."
            },
            {
                "id": "arguments",
                "label": "Construct Legal Argument",
                "done": self.argument_prepared,
                "hint": "Assemble premises connecting evidence to your logical claim."
            },
            {
                "id": "courtroom",
                "label": "Present Case in Court",
                "done": self.courtroom_completed,
                "hint": "Deliver your structured argument before the AI Judge."
            }
        ]

    def to_dict(self) -> dict:
        return {
            "briefing_read": self.briefing_read,
            "crime_scene_explored": self.crime_scene_explored,
            "suspects_reviewed": self.suspects_reviewed,
            "evidence_reviewed": self.evidence_reviewed,
            "case_board_reviewed": self.case_board_reviewed,
            "argument_prepared": self.argument_prepared,
            "courtroom_completed": self.courtroom_completed,
            "current_stage": self.current_stage,
            "inspected_evidence_ids": list(self.inspected_evidence_ids),
            "interviewed_suspect_ids": list(self.interviewed_suspect_ids),
            "suspect_qa_history": self.suspect_qa_history,
            "player_notes": self.player_notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProgressService":
        srv = cls()
        srv.briefing_read = bool(data.get("briefing_read", False))
        srv.crime_scene_explored = bool(data.get("crime_scene_explored", False))
        srv.suspects_reviewed = bool(data.get("suspects_reviewed", False))
        srv.evidence_reviewed = bool(data.get("evidence_reviewed", False))
        srv.case_board_reviewed = bool(data.get("case_board_reviewed", False))
        srv.argument_prepared = bool(data.get("argument_prepared", False))
        srv.courtroom_completed = bool(data.get("courtroom_completed", False))
        srv.current_stage = str(data.get("current_stage", "briefing"))
        srv.inspected_evidence_ids = set(data.get("inspected_evidence_ids", []))
        srv.interviewed_suspect_ids = set(data.get("interviewed_suspect_ids", []))
        srv.suspect_qa_history = data.get("suspect_qa_history", {})
        srv.player_notes = str(data.get("player_notes", ""))
        return srv
