"""Case Service for LOGIC COURTROOM.
Handles loading, saving, and validating cases from JSON data storage.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from config import DATA_DIR
from models.case import Case

CASES_FILE = DATA_DIR / "cases.json"


class CaseService:
    """Manages reading and writing cases to persistent storage."""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or CASES_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def get_all_cases(self) -> List[Case]:
        """Loads and returns all case objects."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Case.from_dict(item) for item in data]
        except Exception as e:
            print(f"[CaseService] Error loading cases: {e}")
            return []

    def get_case_by_id(self, case_id: str) -> Optional[Case]:
        for c in self.get_all_cases():
            if c.id == case_id:
                return c
        return None

    def validate_case_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates that a custom case dictionary contains required fields."""
        if not data.get("title") or not data.get("title").strip():
            return False, "Case title cannot be empty."
        if not data.get("description") or not data.get("description").strip():
            return False, "Case description cannot be empty."
        suspects = data.get("suspects", [])
        if len(suspects) < 2:
            return False, "A valid case must contain at least 2 suspects."
        evidence = data.get("evidence", [])
        if len(evidence) < 2:
            return False, "A valid case must contain at least 2 evidence items."
        return True, "Valid case data."

    def save_custom_case(self, case: Case) -> bool:
        """Appends a new custom case to the cases repository."""
        try:
            cases = self.get_all_cases()
            # Replace if ID exists, otherwise append
            cases = [c for c in cases if c.id != case.id]
            cases.append(case)

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([c.to_dict() for c in cases], f, indent=2)
            return True
        except Exception as e:
            print(f"[CaseService] Error saving case: {e}")
            return False
