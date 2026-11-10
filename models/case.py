from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .suspect import Suspect
from .evidence import Evidence

@dataclass
class Case:
    """Represents a playable criminal investigation case."""
    id: str
    title: str
    type: str
    description: str
    difficulty: str
    reward: int
    scene_name: str = "Crime Scene"
    scene_type: str = "mansion"  # 'mansion', 'vault', 'office', 'generic'
    suspects: List[Suspect] = field(default_factory=list)
    evidence_list: List[Evidence] = field(default_factory=list)
    initial_facts: List[str] = field(default_factory=list)
    rules: List[Dict[str, Any]] = field(default_factory=list)
    solution_suspect_id: Optional[str] = None
    solution_conclusion: str = "suspect_guilty_beyond_reasonable_doubt"
    solution_summary: str = ""

    def get_suspect(self, suspect_id: str) -> Optional[Suspect]:
        for s in self.suspects:
            if s.id == suspect_id:
                return s
        return None

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        for e in self.evidence_list:
            if e.id == evidence_id:
                return e
        return None

    def get_collected_evidence(self) -> List[Evidence]:
        return [e for e in self.evidence_list if e.collected]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "description": self.description,
            "difficulty": self.difficulty,
            "reward": self.reward,
            "scene_name": self.scene_name,
            "scene_type": self.scene_type,
            "suspects": [s.to_dict() for s in self.suspects],
            "evidence": [e.to_dict() for e in self.evidence_list],
            "initial_facts": self.initial_facts,
            "rules": self.rules,
            "solution_suspect_id": self.solution_suspect_id,
            "solution_conclusion": self.solution_conclusion,
            "solution_summary": self.solution_summary
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Case":
        suspects_data = data.get("suspects", [])
        if isinstance(suspects_data, list):
            suspects = [Suspect.from_dict(s) if isinstance(s, dict) else s for s in suspects_data]
        else:
            suspects = []

        evidence_data = data.get("evidence", []) or data.get("evidence_list", [])
        if isinstance(evidence_data, list):
            evidence_list = [Evidence.from_dict(e) if isinstance(e, dict) else e for e in evidence_data]
        else:
            evidence_list = []

        return cls(
            id=data.get("id", "CASE000"),
            title=data.get("title", "Untitled Case"),
            type=data.get("type", "Investigation"),
            description=data.get("description", ""),
            difficulty=data.get("difficulty", "MEDIUM"),
            reward=int(data.get("reward", 100)),
            scene_name=data.get("scene_name", "Crime Scene"),
            scene_type=data.get("scene_type", "mansion"),
            suspects=suspects,
            evidence_list=evidence_list,
            initial_facts=data.get("initial_facts", []),
            rules=data.get("rules", []),
            solution_suspect_id=data.get("solution_suspect_id"),
            solution_conclusion=data.get("solution_conclusion", "guilty"),
            solution_summary=data.get("solution_summary", "")
        )
