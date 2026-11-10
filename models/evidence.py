from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Any

@dataclass
class Evidence:
    """Represents an item or piece of evidence in a case."""
    id: str
    name: str
    description: str
    category: str  # 'Physical', 'Direct', 'Circumstantial', 'Testimonial', 'Digital'
    reliability: float  # 0.0 to 1.0 (how trustworthy the source is)
    relevance: float    # 0.0 to 1.0 (how related it is to establishing the core crime facts)
    associated_suspect: Optional[str] = None
    collected: bool = False
    scene_pos: Tuple[int, int, int, int] = (100, 100, 60, 60)  # (x, y, width, height) in crime scene view
    icon_type: str = "generic"
    facts_unlocked: List[str] = field(default_factory=list)
    details: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "reliability": self.reliability,
            "relevance": self.relevance,
            "associated_suspect": self.associated_suspect,
            "collected": self.collected,
            "scene_pos": list(self.scene_pos),
            "icon_type": self.icon_type,
            "facts_unlocked": self.facts_unlocked,
            "details": self.details
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Evidence":
        return cls(
            id=data.get("id", "EVD-000"),
            name=data.get("name", "Unknown Evidence"),
            description=data.get("description", ""),
            category=data.get("category", "Circumstantial"),
            reliability=float(data.get("reliability", 0.5)),
            relevance=float(data.get("relevance", 0.5)),
            associated_suspect=data.get("associated_suspect"),
            collected=bool(data.get("collected", False)),
            scene_pos=tuple(data.get("scene_pos", [100, 100, 60, 60])),  # type: ignore
            icon_type=data.get("icon_type", "generic"),
            facts_unlocked=data.get("facts_unlocked", []),
            details=data.get("details", "")
        )
