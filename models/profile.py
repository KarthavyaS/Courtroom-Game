"""Player Profile Model and Career Progression for LOGIC COURTROOM.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class PlayerProfile:
    """Represents the player's barrister persona, stats, settings, and achievements."""
    name: str = "Arthur Pendelton"
    title: str = "Junior Barrister"
    avatar_id: str = "counsel_1"
    total_score: int = 0
    cases_completed: int = 0
    verdicts_won: int = 0
    arguments_submitted: int = 0
    highest_score: int = 0
    achievements: List[str] = field(default_factory=lambda: ["Bar Exam Passed"])
    tutorial_completed: bool = False
    onboarded: bool = False
    sound_enabled: bool = True
    music_enabled: bool = True
    volume: float = 0.8
    text_scale: float = 1.0

    @property
    def cases_won(self) -> int:
        return self.verdicts_won

    @cases_won.setter
    def cases_won(self, val: int):
        self.verdicts_won = val

    @property
    def cases_lost(self) -> int:
        return max(0, self.cases_completed - self.verdicts_won)

    @cases_lost.setter
    def cases_lost(self, val: int):
        pass

    def get_rank(self) -> str:
        if self.total_score >= 1200:
            return "Lord Chief Justice"
        elif self.total_score >= 800:
            return "King's Counsel (KC)"
        elif self.total_score >= 500:
            return "Senior Advocate"
        elif self.total_score >= 200:
            return "Barrister-at-Law"
        else:
            return "Junior Barrister"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "title": self.get_rank(),
            "avatar_id": self.avatar_id,
            "total_score": self.total_score,
            "cases_completed": self.cases_completed,
            "verdicts_won": self.verdicts_won,
            "arguments_submitted": self.arguments_submitted,
            "highest_score": self.highest_score,
            "achievements": self.achievements,
            "tutorial_completed": self.tutorial_completed,
            "onboarded": self.onboarded,
            "sound_enabled": self.sound_enabled,
            "music_enabled": self.music_enabled,
            "volume": self.volume,
            "text_scale": self.text_scale
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerProfile":
        return cls(
            name=data.get("name", "Arthur Pendelton"),
            title=data.get("title", "Junior Barrister"),
            avatar_id=data.get("avatar_id", "counsel_1"),
            total_score=int(data.get("total_score", 0)),
            cases_completed=int(data.get("cases_completed", 0)),
            verdicts_won=int(data.get("verdicts_won", 0)),
            arguments_submitted=int(data.get("arguments_submitted", 0)),
            highest_score=int(data.get("highest_score", 0)),
            achievements=data.get("achievements", ["Bar Exam Passed"]),
            tutorial_completed=bool(data.get("tutorial_completed", False)),
            onboarded=bool(data.get("onboarded", False)),
            sound_enabled=bool(data.get("sound_enabled", True)),
            music_enabled=bool(data.get("music_enabled", True)),
            volume=float(data.get("volume", 0.8)),
            text_scale=float(data.get("text_scale", 1.0))
        )
