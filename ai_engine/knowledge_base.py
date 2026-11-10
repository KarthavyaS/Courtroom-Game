"""Knowledge Base for Traditional Artificial Intelligence Courtroom reasoning.
Stores established facts, forensic observations, propositions, and inference rules.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from .propositional_logic import parse_literal

@dataclass
class Rule:
    """Represents a propositional Horn clause rule: Antecedent_1 AND Antecedent_2 ... => Consequent."""
    id: str
    name: str
    antecedents: List[str]  # e.g. ["knife_wound_cause_of_death", "knife_has_suspect_fingerprints"]
    consequent: str         # e.g. "suspect_had_physical_contact_with_weapon"
    description: str = ""
    category: str = "forensic"  # forensic, legal, circumstantial, alibi
    weight: float = 1.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "antecedents": self.antecedents,
            "consequent": self.consequent,
            "description": self.description,
            "category": self.category,
            "weight": self.weight
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Rule":
        return cls(
            id=data.get("id", "RULE-000"),
            name=data.get("name", "Unnamed Rule"),
            antecedents=data.get("antecedents", []),
            consequent=data.get("consequent", ""),
            description=data.get("description", ""),
            category=data.get("category", "forensic"),
            weight=float(data.get("weight", 1.0))
        )


class KnowledgeBase:
    """Manages facts, rules, and logic assertions for courtroom investigation."""

    def __init__(self):
        self.facts: Set[str] = set()
        self.false_facts: Set[str] = set()
        self.rules: List[Rule] = []
        self.metadata: Dict[str, Any] = {}

    def tell(self, fact: str) -> None:
        """Asserts a fact is true."""
        name, is_neg = parse_literal(fact)
        if is_neg:
            self.false_facts.add(name)
            self.facts.discard(name)
        else:
            self.facts.add(name)
            self.false_facts.discard(name)

    def tell_all(self, facts: List[str]) -> None:
        for f in facts:
            self.tell(f)

    def retract(self, fact: str) -> None:
        """Removes a fact from the knowledge base."""
        name, is_neg = parse_literal(fact)
        self.facts.discard(name)
        self.false_facts.discard(name)

    def add_rule(self, rule: Rule) -> None:
        # Avoid duplicate rule IDs
        self.rules = [r for r in self.rules if r.id != rule.id]
        self.rules.append(rule)

    def is_true(self, proposition: str) -> bool:
        """Returns True if the proposition is explicitly known to be true."""
        name, is_neg = parse_literal(proposition)
        if is_neg:
            return name in self.false_facts
        return name in self.facts

    def is_false(self, proposition: str) -> bool:
        """Returns True if the proposition is explicitly known to be false."""
        name, is_neg = parse_literal(proposition)
        if is_neg:
            return name in self.facts
        return name in self.false_facts

    def get_facts(self) -> Set[str]:
        return set(self.facts)

    def get_rules(self) -> List[Rule]:
        return list(self.rules)

    def clone(self) -> "KnowledgeBase":
        new_kb = KnowledgeBase()
        new_kb.facts = set(self.facts)
        new_kb.false_facts = set(self.false_facts)
        new_kb.rules = list(self.rules)
        new_kb.metadata = dict(self.metadata)
        return new_kb

    def __repr__(self) -> str:
        return f"<KnowledgeBase facts={len(self.facts)}, rules={len(self.rules)}>"
