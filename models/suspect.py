from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Suspect:
    """Represents a person of interest in a criminal case."""
    id: str
    name: str
    occupation: str
    relationship: str
    motive: str
    alibi: str
    statement: str
    known_facts: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    avatar_type: str = "detective"
    is_guilty: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "occupation": self.occupation,
            "relationship": self.relationship,
            "motive": self.motive,
            "alibi": self.alibi,
            "statement": self.statement,
            "known_facts": self.known_facts,
            "contradictions": self.contradictions,
            "avatar_type": self.avatar_type,
            "is_guilty": self.is_guilty
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Suspect":
        return cls(
            id=data.get("id", "SUS-000"),
            name=data.get("name", "Unknown Suspect"),
            occupation=data.get("occupation", "Unknown"),
            relationship=data.get("relationship", "Acquaintance"),
            motive=data.get("motive", "None known"),
            alibi=data.get("alibi", "No alibi provided"),
            statement=data.get("statement", "..."),
            known_facts=data.get("known_facts", []),
            contradictions=data.get("contradictions", []),
            avatar_type=data.get("avatar_type", "default"),
            is_guilty=bool(data.get("is_guilty", False))
        )
