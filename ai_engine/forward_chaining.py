"""Forward Chaining Inference Engine for LOGIC COURTROOM.
Derives new logical facts step-by-step from known facts and propositional Horn rules.
"""

from typing import List, Set, Dict, Tuple, Optional
from dataclasses import dataclass
from .knowledge_base import KnowledgeBase, Rule
from .propositional_logic import parse_literal

@dataclass
class DerivationStep:
    rule_id: str
    rule_name: str
    antecedents_satisfied: List[str]
    derived_fact: str
    explanation: str


class ForwardChainingEngine:
    """Implements bottom-up forward chaining deduction on propositional Horn rules."""

    def __init__(self, kb: Optional[KnowledgeBase] = None):
        self.kb = kb or KnowledgeBase()

    def run(self, kb: Optional[KnowledgeBase] = None) -> Tuple[Set[str], List[DerivationStep]]:
        """Executes forward chaining until a fixed point is reached.
        Returns the set of all derived facts and a chronological list of derivation steps.
        """
        active_kb = kb if kb is not None else self.kb
        inferred_facts = set(active_kb.get_facts())
        trace: List[DerivationStep] = []

        rules = active_kb.get_rules()
        # Count unsatisfied premises for each rule
        premise_count: Dict[str, int] = {}
        for rule in rules:
            # Normalize antecedents
            unmet = 0
            for ant in rule.antecedents:
                name, is_neg = parse_literal(ant)
                if not is_neg:
                    if name not in inferred_facts:
                        unmet += 1
                else:
                    if name in inferred_facts:
                        unmet += 1
            premise_count[rule.id] = unmet

        # Queue of facts newly added
        queue = list(inferred_facts)
        fired_rules: Set[str] = set()

        changed = True
        while changed:
            changed = False
            for rule in rules:
                if rule.id in fired_rules:
                    continue

                # Check if all antecedents are currently satisfied
                all_satisfied = True
                satisfied_ants = []
                for ant in rule.antecedents:
                    name, is_neg = parse_literal(ant)
                    if not is_neg:
                        if name in inferred_facts:
                            satisfied_ants.append(name)
                        else:
                            all_satisfied = False
                            break
                    else:
                        if name not in inferred_facts:
                            satisfied_ants.append(f"~{name}")
                        else:
                            all_satisfied = False
                            break

                if all_satisfied:
                    fired_rules.add(rule.id)
                    consequent_name, is_consequent_neg = parse_literal(rule.consequent)
                    target_fact = consequent_name if not is_consequent_neg else f"~{consequent_name}"

                    if consequent_name not in inferred_facts:
                        inferred_facts.add(consequent_name)
                        changed = True

                        step = DerivationStep(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            antecedents_satisfied=satisfied_ants,
                            derived_fact=target_fact,
                            explanation=f"Applied Rule '{rule.name}' [{', '.join(satisfied_ants)}] => {target_fact}"
                        )
                        trace.append(step)

        return inferred_facts, trace

    def is_entailed(self, target: str, kb: Optional[KnowledgeBase] = None) -> Tuple[bool, List[DerivationStep]]:
        """Checks if a specific target proposition is entailed via forward chaining."""
        derived, trace = self.run(kb)
        name, is_neg = parse_literal(target)
        if not is_neg:
            return (name in derived), trace
        else:
            return (name not in derived), trace
