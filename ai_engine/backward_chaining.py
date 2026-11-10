"""Backward Chaining Inference Engine for LOGIC COURTROOM.
Top-down goal-directed reasoning to verify whether a conclusion can be proven from premises and rules.
"""

from typing import List, Set, Dict, Tuple, Optional, Any
from .knowledge_base import KnowledgeBase, Rule
from .propositional_logic import parse_literal

class BackwardChainingEngine:
    """Implements recursive goal-directed backward chaining proof search with cycle detection."""

    def __init__(self, kb: Optional[KnowledgeBase] = None):
        self.kb = kb or KnowledgeBase()

    def prove(self, target: str, kb: Optional[KnowledgeBase] = None) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Attempts to prove target proposition from KnowledgeBase.
        Returns:
            (proven: bool, trace: List[str], proof_tree: dict)
        """
        active_kb = kb if kb is not None else self.kb
        trace: List[str] = []
        visited: Set[str] = set()

        def _search_goal(goal: str, depth: int) -> Tuple[bool, Dict[str, Any]]:
            indent = "  " * depth
            goal_name, is_neg = parse_literal(goal)
            norm_goal = f"~{goal_name}" if is_neg else goal_name

            node: Dict[str, Any] = {
                "goal": norm_goal,
                "proven": False,
                "source": "unproven",
                "subgoals": []
            }

            trace.append(f"{indent}Investigating Goal: '{norm_goal}'")

            # Check if already a known fact in KB
            if not is_neg and goal_name in active_kb.facts:
                trace.append(f"{indent}✓ '{norm_goal}' is an established fact in the Knowledge Base.")
                node["proven"] = True
                node["source"] = "base_fact"
                return True, node

            if is_neg and goal_name in active_kb.false_facts:
                trace.append(f"{indent}✓ '{norm_goal}' is confirmed FALSE in the Knowledge Base.")
                node["proven"] = True
                node["source"] = "base_fact_negated"
                return True, node

            # Cycle detection
            if norm_goal in visited:
                trace.append(f"{indent}✗ Cycle detected for '{norm_goal}', abandoning branch.")
                node["source"] = "cycle"
                return False, node

            visited.add(norm_goal)

            # Find matching rules where consequent matches goal
            matching_rules = [
                r for r in active_kb.get_rules()
                if parse_literal(r.consequent)[0] == goal_name and parse_literal(r.consequent)[1] == is_neg
            ]

            if not matching_rules:
                trace.append(f"{indent}✗ No inference rules found to establish '{norm_goal}'.")
                visited.remove(norm_goal)
                return False, node

            for rule in matching_rules:
                trace.append(f"{indent}Testing Rule '{rule.name}' for goal '{norm_goal}'...")
                rule_subgoals_proven = True
                subgoal_nodes = []

                for ant in rule.antecedents:
                    sub_proven, sub_node = _search_goal(ant, depth + 1)
                    subgoal_nodes.append(sub_node)
                    if not sub_proven:
                        rule_subgoals_proven = False
                        trace.append(f"{indent}  Subgoal '{ant}' could NOT be verified for rule '{rule.name}'.")
                        break

                if rule_subgoals_proven:
                    trace.append(f"{indent}✓ Rule '{rule.name}' fully satisfied! Proved: '{norm_goal}'.")
                    node["proven"] = True
                    node["source"] = f"rule_{rule.id}"
                    node["rule"] = rule.name
                    node["subgoals"] = subgoal_nodes
                    visited.remove(norm_goal)
                    return True, node
                else:
                    node["subgoals"].extend(subgoal_nodes)

            visited.remove(norm_goal)
            trace.append(f"{indent}✗ Could NOT prove '{norm_goal}' with available rules.")
            return False, node

        proven, tree = _search_goal(target, 0)
        return proven, trace, tree
