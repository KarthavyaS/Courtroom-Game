"""Scoring Engine for LOGIC COURTROOM.
Calculates objective legal score (0-100), evaluates validity, evidence strength,
safeguard violations, and generates structured judge verdict and feedback.
"""

from typing import Dict, Any, List, Optional
from models.argument import Argument
from models.evidence import Evidence
from models.suspect import Suspect
from .knowledge_base import KnowledgeBase
from .forward_chaining import ForwardChainingEngine
from .backward_chaining import BackwardChainingEngine
from .resolution import ResolutionEngine
from .evidence_analyzer import EvidenceAnalyzer
from .rule_engine import RuleEngine

class ScoringEngine:
    """Evaluates lawyer arguments using traditional artificial intelligence logic engines."""

    def __init__(self):
        self.forward_chainer = ForwardChainingEngine()
        self.backward_chainer = BackwardChainingEngine()
        self.resolution_engine = ResolutionEngine()
        self.evidence_analyzer = EvidenceAnalyzer()
        self.rule_engine = RuleEngine()

    def evaluate_argument(
        self,
        argument: Argument,
        kb: KnowledgeBase,
        collected_evidence: List[Evidence],
        suspect: Optional[Suspect] = None
    ) -> Dict[str, Any]:
        """Performs comprehensive traditional AI evaluation on the submitted argument."""

        # 1. Setup KB with collected facts and premises
        working_kb = kb.clone()
        for p in argument.premises:
            working_kb.tell(p)

        # 2. Check Logical Entailment via Backward Chaining & Forward Chaining
        is_proven_bw, bw_trace, proof_tree = self.backward_chainer.prove(argument.conclusion, working_kb)
        derived_facts, fw_trace = self.forward_chainer.run(working_kb)
        is_proven_fw = argument.conclusion.lower() in derived_facts

        # 3. Check Entailment via Resolution
        is_proven_res, res_trace, clauses = self.resolution_engine.prove_by_refutation(argument.conclusion, working_kb)

        logical_validity_proven = is_proven_bw or is_proven_fw or is_proven_res

        # 4. Score Component 1: Logical Validity (0 - 30 pts)
        if logical_validity_proven:
            validity_score = 30
            validity_msg = "Conclusion is logically and deductively sound via inference rules."
        else:
            # Partial score if at least some premises derive intermediate conclusions
            if len(fw_trace) > 0:
                validity_score = 15
                validity_msg = "Intermediate facts derived, but final conclusion is not fully entailed."
            else:
                validity_score = 5
                validity_msg = "Conclusion does not logically follow from the supplied premises."

        # 5. Score Component 2: Evidence Strength & Reliability (0 - 40 pts)
        selected_evidence = [
            e for e in collected_evidence if e.id in argument.selected_evidence_ids
        ]
        ev_eval = self.evidence_analyzer.evaluate_bundle(selected_evidence, suspect)

        rel_points = round(ev_eval["avg_reliability"] * 20)
        rev_points = round(ev_eval["avg_relevance"] * 20)
        evidence_score = rel_points + rev_points

        # 6. Score Component 3: Premise Grounding (0 - 15 pts)
        unlocked_facts = set()
        for e in collected_evidence:
            unlocked_facts.update(e.facts_unlocked)
        unlocked_facts.update(kb.get_facts())

        grounded_count = sum(1 for p in argument.premises if p.lower() in unlocked_facts)
        total_premises = max(1, len(argument.premises))
        grounding_ratio = grounded_count / total_premises
        grounding_score = round(grounding_ratio * 15)

        # 7. Score Component 4: Safeguard Violations & Contradictions (0 - 15 pts)
        safeguard_violations = self.rule_engine.check_safeguards(argument.premises, argument.conclusion, working_kb)

        contradiction_points = 15
        violation_notes = []
        for v in safeguard_violations:
            if v["severity"] == "FATAL":
                contradiction_points -= 15
            elif v["severity"] == "CRITICAL":
                contradiction_points -= 10
            elif v["severity"] == "HIGH":
                contradiction_points -= 5
            violation_notes.append(f"[{v['type']}] {v['message']}")

        contradiction_points = max(0, contradiction_points)

        # Total Score Calculation (0 - 100)
        total_score = max(0, min(100, validity_score + evidence_score + grounding_score + contradiction_points))

        # Determine Final Courtroom Verdict
        has_fatal_contradiction = any(v["severity"] == "FATAL" for v in safeguard_violations)
        if has_fatal_contradiction or (logical_validity_proven is False and total_score < 35):
            verdict = "CONTRADICTED" if has_fatal_contradiction else "NOT PROVEN"
        elif logical_validity_proven and total_score >= 70:
            verdict = "SUPPORTED"
        else:
            verdict = "NOT PROVEN"

        # Generate Judge Reasoning Narrative
        trace_summary = []
        trace_summary.append("=== AI JUDGE INFERENCE TRACE ===")
        trace_summary.append(f"Target Conclusion: '{argument.conclusion}'")
        trace_summary.append(f"Forward Chaining Inferences: {len(fw_trace)} rule(s) fired.")
        for step in fw_trace:
            trace_summary.append(f"  • {step.explanation}")

        trace_summary.append(f"Backward Chaining Goal Proof: {'SUCCESS' if is_proven_bw else 'FAILED'}")
        trace_summary.append(f"Resolution Refutation: {'ENTAILMENT CONFIRMED (Empty Clause)' if is_proven_res else 'INSUFFICIENT PROOF'}")

        if violation_notes:
            trace_summary.append("=== LEGAL SAFEGUARD WARNINGS ===")
            for v_note in violation_notes:
                trace_summary.append(f"  ⚠ {v_note}")

        feedback = (
            f"Verdict: {verdict}. Score: {total_score}/100. "
            f"Validity: {validity_score}/30. Evidence Strength: {evidence_score}/40. "
            f"Fact Grounding: {grounding_score}/15. Safeguards: {contradiction_points}/15."
        )

        return {
            "verdict": verdict,
            "total_score": total_score,
            "breakdown": {
                "logical_validity": validity_score,
                "evidence_strength": evidence_score,
                "fact_grounding": grounding_score,
                "safeguards": contradiction_points,
            },
            "is_proven": logical_validity_proven,
            "reasoning_trace": trace_summary,
            "backward_trace": bw_trace,
            "resolution_trace": res_trace,
            "violations": violation_notes,
            "evidence_eval": ev_eval,
            "feedback": feedback
        }
