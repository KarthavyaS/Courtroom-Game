"""Save Service for LOGIC COURTROOM.
Manages persistent user score entries, leaderboard storage, player profile,
and active game investigation save/resume sessions in JSON.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import DATA_DIR
from models.profile import PlayerProfile

LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"
PROFILE_FILE = DATA_DIR / "profile.json"
ACTIVE_SAVE_FILE = DATA_DIR / "active_save.json"


class SaveService:
    """Handles persistent scoring, profile management, leaderboard, and active session saves."""

    def __init__(
        self,
        file_path: Optional[Path] = None,
        profile_path: Optional[Path] = None,
        save_path: Optional[Path] = None
    ):
        self.file_path = file_path or LEADERBOARD_FILE
        self.profile_path = profile_path or PROFILE_FILE
        self.save_path = save_path or ACTIVE_SAVE_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
        if not self.profile_path.exists():
            default_profile = PlayerProfile()
            with open(self.profile_path, "w", encoding="utf-8") as f:
                json.dump(default_profile.to_dict(), f, indent=2)

    def load_profile(self) -> PlayerProfile:
        """Loads the player profile from persistent JSON storage."""
        try:
            with open(self.profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return PlayerProfile.from_dict(data)
        except Exception as e:
            print(f"[SaveService] Error loading profile: {e}")
            return PlayerProfile()

    def save_profile(self, profile: PlayerProfile) -> bool:
        """Saves the player profile to JSON storage."""
        try:
            with open(self.profile_path, "w", encoding="utf-8") as f:
                json.dump(profile.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"[SaveService] Error saving profile: {e}")
            return False

    def has_active_save(self) -> bool:
        """Checks if a valid in-progress investigation save exists."""
        if not self.save_path.exists():
            return False
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return bool(data.get("case_id")) and not data.get("completed", False)
        except Exception:
            return False

    def get_active_save_summary(self) -> Optional[Dict[str, Any]]:
        """Returns brief summary metadata for the dashboard continue card."""
        if not self.has_active_save():
            return None
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {
                "case_id": data.get("case_id"),
                "case_title": data.get("case_title", "Unknown Case"),
                "stage": data.get("stage", "briefing"),
                "progress_pct": data.get("progress_pct", 0),
                "timestamp": data.get("timestamp", "Recent"),
                "collected_count": len(data.get("collected_evidence_ids", [])),
                "total_evidence": data.get("total_evidence", 0)
            }
        except Exception as e:
            print(f"[SaveService] Error reading active save summary: {e}")
            return None

    def save_active_game(self, game_state: Any) -> bool:
        """Saves current case investigation state into active_save.json."""
        if not game_state.current_case:
            return False
        try:
            save_data = {
                "case_id": game_state.current_case.id,
                "case_title": game_state.current_case.title,
                "stage": game_state.progress.current_stage,
                "progress_pct": game_state.progress.calculate_progress_percentage(),
                "progress": game_state.progress.to_dict(),
                "collected_evidence_ids": list(game_state.collected_evidence_ids),
                "selected_suspect_id": game_state.selected_suspect_id,
                "warning_count": getattr(game_state, "warning_count", 0),
                "trial_transcript": game_state.trial_transcript,
                "player_notes": game_state.progress.player_notes,
                "total_evidence": len(game_state.current_case.evidence_list),
                "completed": game_state.progress.courtroom_completed,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            print(f"[SaveService] Error saving active game: {e}")
            return False

    def load_active_game(self) -> Optional[Dict[str, Any]]:
        """Loads and returns active game session dictionary."""
        if not self.has_active_save():
            return None
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[SaveService] Error loading active game: {e}")
            return None

    def clear_active_save(self) -> None:
        """Deletes active save file when investigation finishes or is reset."""
        try:
            if self.save_path.exists():
                self.save_path.unlink()
        except Exception as e:
            print(f"[SaveService] Error clearing active save: {e}")

    def reset_all_progress(self) -> None:
        """Resets profile, leaderboard, and active saves to factory defaults."""
        self.clear_active_save()
        default_profile = PlayerProfile()
        self.save_profile(default_profile)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Returns sorted leaderboard list by score descending."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return []
            data.sort(key=lambda x: x.get("score", 0), reverse=True)
            return data
        except Exception as e:
            print(f"[SaveService] Error reading leaderboard: {e}")
            return []

    def record_score(
        self,
        player_name: str,
        case_id: str,
        case_title: str,
        score: int,
        verdict: str
    ) -> bool:
        """Appends a new score entry, updates profile stats, and saves."""
        try:
            records = self.get_leaderboard()
            entry = {
                "player_name": player_name.strip() or "Anonymous Counsel",
                "case_id": case_id,
                "case_title": case_title,
                "score": score,
                "verdict": verdict,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            records.append(entry)
            records.sort(key=lambda x: x.get("score", 0), reverse=True)

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(records[:100], f, indent=2)

            # Update Profile stats
            prof = self.load_profile()
            prof.total_score += score
            prof.cases_completed += 1
            if verdict == "SUPPORTED":
                prof.verdicts_won += 1
            if score > prof.highest_score:
                prof.highest_score = score
            self.save_profile(prof)

            return True
        except Exception as e:
            print(f"[SaveService] Error saving leaderboard record: {e}")
            return False
