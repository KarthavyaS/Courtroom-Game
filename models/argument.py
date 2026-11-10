from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Argument:
    """Represents a structured legal argument presented by the player to the AI Judge."""
    suspect_id: str
    premises: List[str] = field(default_factory=list)
    conclusion: str = ""
    selected_evidence_ids: List[str] = field(default_factory=list)
    rule_id: Optional[str] = None
    custom_text: str = ""
    verdict: str = "PENDING"  # 'SUPPORTED', 'NOT PROVEN', 'CONTRADICTED'
    score: int = 0
    score_breakdown: Dict[str, Any] = field(default_factory=dict)
    reasoning_trace: List[str] = field(default_factory=list)
    judge_feedback: str = ""
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.evidence_ids and not self.selected_evidence_ids:
            self.selected_evidence_ids = list(self.evidence_ids)
        elif self.selected_evidence_ids and not self.evidence_ids:
            self.evidence_ids = list(self.selected_evidence_ids)

    def to_dict(self) -> dict:
        return {
            "suspect_id": self.suspect_id,
            "premises": self.premises,
            "conclusion": self.conclusion,
            "selected_evidence_ids": self.selected_evidence_ids,
            "rule_id": self.rule_id,
            "custom_text": self.custom_text,
            "verdict": self.verdict,
            "score": self.score,
            "score_breakdown": self.score_breakdown,
            "reasoning_trace": self.reasoning_trace,
            "judge_feedback": self.judge_feedback
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Argument":
        return cls(
            suspect_id=data.get("suspect_id", ""),
            premises=data.get("premises", []),
            conclusion=data.get("conclusion", ""),
            selected_evidence_ids=data.get("selected_evidence_ids", []) or data.get("evidence_ids", []),
            rule_id=data.get("rule_id"),
            custom_text=data.get("custom_text", ""),
            verdict=data.get("verdict", "PENDING"),
            score=int(data.get("score", 0)),
            score_breakdown=data.get("score_breakdown", {}),
            reasoning_trace=data.get("reasoning_trace", []),
            judge_feedback=data.get("judge_feedback", "")
        )
