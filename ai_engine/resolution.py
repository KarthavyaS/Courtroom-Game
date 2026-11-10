"""Propositional Resolution Engine for LOGIC COURTROOM.
Implements refutation resolution, CNF clause management, and contradiction detection.
"""

from typing import List, Set, Tuple, Optional, FrozenSet, Dict
from .propositional_logic import parse_literal, Expr, Literal, Or, And, Not, Implies
from .knowledge_base import KnowledgeBase, Rule

def complement(literal: str) -> str:
    """Returns the complementary literal (e.g. 'p' -> '~p', '~p' -> 'p')."""
    name, is_neg = parse_literal(literal)
    return name if is_neg else f"~{name}"


class ResolutionEngine:
    """Implements propositional refutation resolution."""

    def __init__(self):
        pass

    def rule_to_clause(self, rule: Rule) -> FrozenSet[str]:
        """Converts a Horn rule (A1 & A2 => C) to a CNF clause: {~A1, ~A2, C}."""
        literals = set()
        for ant in rule.antecedents:
            name, is_neg = parse_literal(ant)
            # Negate antecedent
            literals.add(name if is_neg else f"~{name}")
        c_name, c_neg = parse_literal(rule.consequent)
        literals.add(f"~{c_name}" if c_neg else c_name)
        return frozenset(literals)

    def kb_to_clauses(self, kb: KnowledgeBase) -> Set[FrozenSet[str]]:
        """Extracts initial CNF clauses from KB facts and rules."""
        clauses: Set[FrozenSet[str]] = set()

        for f in kb.facts:
            clauses.add(frozenset([f.lower()]))
        for ff in kb.false_facts:
            clauses.add(frozenset([f"~{ff.lower()}"]))

        for rule in kb.get_rules():
            clause = self.rule_to_clause(rule)
            clauses.add(clause)

        return clauses

    def resolve(self, ci: FrozenSet[str], cj: FrozenSet[str]) -> List[FrozenSet[str]]:
        """Resolves two CNF clauses. Returns all valid resolvents."""
        resolvents = []
        for lit in ci:
            comp = complement(lit)
            if comp in cj:
                # Remove lit from ci and comp from cj, and combine
                resolvent = (set(ci) - {lit}) | (set(cj) - {comp})
                # Check for tautology (e.g. {P, ~P})
                has_tautology = any(complement(l) in resolvent for l in resolvent)
                if not has_tautology:
                    resolvents.append(frozenset(resolvent))
        return resolvents

    def prove_by_refutation(
        self, query: str, kb: KnowledgeBase, max_iterations: int = 500
    ) -> Tuple[bool, List[str], List[FrozenSet[str]]]:
        """Applies refutation resolution to test if KB entails query (KB |= query).
        Returns:
            (entailed: bool, trace: List[str], generated_clauses: List[FrozenSet])
        """
        clauses = set(self.kb_to_clauses(kb))
        trace: List[str] = []

        q_name, q_neg = parse_literal(query)
        # Negate the query to test refutation
        neg_query_lit = q_name if q_neg else f"~{q_name}"
        neg_clause = frozenset([neg_query_lit])
        clauses.add(neg_clause)

        trace.append(f"Goal to prove: '{query}'")
        trace.append(f"Adding negated goal to clause set: {{{neg_query_lit}}}")
        trace.append(f"Initial Clause count: {len(clauses)}")

        new_clauses: Set[FrozenSet[str]] = set()
        iterations = 0

        seen_pairs: Set[Tuple[FrozenSet[str], FrozenSet[str]]] = set()
        clause_list = list(clauses)

        while iterations < max_iterations:
            iterations += 1
            new_generated = []
            found_new = False
            n = len(clause_list)

            for i in range(n):
                for j in range(i + 1, n):
                    ci, cj = clause_list[i], clause_list[j]
                    pair_key = (ci, cj) if hash(ci) < hash(cj) else (cj, ci)
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)

                    resolvents = self.resolve(ci, cj)
                    for res in resolvents:
                        if len(res) == 0:
                            trace.append(f"Resolved {{{', '.join(ci)}}} and {{{', '.join(cj)}}} => EMPTY CLAUSE (Box).")
                            trace.append("Contradiction reached! The query is mathematically entailed by the premises.")
                            return True, trace, list(clauses)

                        if res not in clauses and res not in new_clauses:
                            new_clauses.add(res)
                            new_generated.append(res)
                            found_new = True
                            trace.append(f"Resolved {{{', '.join(ci)}}} and {{{', '.join(cj)}}} => {{{', '.join(res)}}}")

            if not found_new or len(clause_list) > 150:
                break
            clause_list.extend(new_generated)
            clauses.update(new_clauses)

        trace.append("No further resolvents can be produced without deriving empty clause.")
        trace.append("Conclusion is NOT entailed by the Knowledge Base.")
        return False, trace, list(clauses)

    def detect_contradictions(self, clauses: Set[FrozenSet[str]]) -> Tuple[bool, List[str]]:
        """Checks if a set of clauses contains internal contradictions."""
        trace = []
        clause_list = list(clauses)
        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                ci, cj = clause_list[i], clause_list[j]
                if len(ci) == 1 and len(cj) == 1:
                    lit_i = next(iter(ci))
                    lit_j = next(iter(cj))
                    if complement(lit_i) == lit_j:
                        trace.append(f"Direct contradiction detected: '{lit_i}' conflicts with '{lit_j}'")
                        return True, trace
        return False, trace
