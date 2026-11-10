"""Courtroom Dialogue Manager for LOGIC COURTROOM.
Orchestrates turn-based exchanges between the Player Lawyer, AI Judge, and Accused Suspect.
"""

from typing import List, Dict, Any, Optional
from models.suspect import Suspect
from ai_engine.argument_classifier import ArgumentEvaluation
from services.courtroom_session import CourtroomSession, CourtMessage

class DialogueManager:
    """Manages conversational state and dialogue formatting for the Courtroom screen."""

    def __init__(self, session: CourtroomSession):
        self.session = session

    def submit_pleading(self, text: str) -> ArgumentEvaluation:
        """Submits player pleading to the session and returns the AI evaluation."""
        return self.session.submit_argument(text)

    def get_latest_messages(self, limit: int = 20) -> List[CourtMessage]:
        """Returns recent trial transcript messages."""
        return self.session.messages[-limit:]

    def is_terminated(self) -> bool:
        """Checks if the active hearing has been terminated due to discipline violations."""
        return self.session.is_hearing_terminated

    def get_warning_level(self) -> int:
        """Returns the current number of unwanted argument strikes."""
        return self.session.unwanted_argument_count
