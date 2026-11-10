"""Evidence Analyzer for LOGIC COURTROOM.
Evaluates evidence based on Reliability, Relevance, Directness, Consistency, and Corroboration.
"""

from typing import List, Dict, Any, Optional
from models.evidence import Evidence
from models.suspect import Suspect

class EvidenceAnalyzer:
    """Analyzes evidence items according to forensic and legal standards."""

    CATEGORY_WEIGHTS = {
        "Direct": 1.0,
        "Physical": 0.9,
        "Digital": 0.85,
        "Testimonial": 0.7,
        "Circumstantial": 0.6
    }

    def evaluate_item(self, evidence: Evidence) -> Dict[str, Any]:
        """Evaluates a single piece of evidence."""
        cat_weight = self.CATEGORY_WEIGHTS.get(evidence.category, 0.5)
        combined_strength = (evidence.reliability * 0.5) + (evidence.relevance * 0.3) + (cat_weight * 0.2)

        # Generate legal insight
        insight = ""
        if evidence.category == "Physical":
            insight = "Physical forensic evidence provides high reliability regarding contact, presence, or mechanics, but requires intent context."
        elif evidence.category == "Digital":
            insight = "Digital evidence (logs, timestamps, messages) provides objective timelines unless tampering is suspected."
        elif evidence.category == "Testimonial":
            insight = "Witness or suspect testimony is subject to bias, perception errors, and credibility challenges."
        elif evidence.category == "Circumstantial":
            insight = "Circumstantial evidence supports an inference when combined with other facts, but does not standalone prove guilt."
        elif evidence.category == "Direct":
            insight = "Direct evidence immediately links an actor to the action without intermediate inferences."

        return {
            "id": evidence.id,
            "name": evidence.name,
            "category": evidence.category,
            "reliability": evidence.reliability,
            "relevance": evidence.relevance,
            "directness_score": cat_weight,
            "combined_strength": round(combined_strength, 2),
            "legal_insight": insight
        }

    def evaluate_bundle(self, evidence_list: List[Evidence], suspect: Optional[Suspect] = None) -> Dict[str, Any]:
        """Evaluates a collection of evidence submitted for an argument."""
        if not evidence_list:
            return {
                "total_items": 0,
                "avg_reliability": 0.0,
                "avg_relevance": 0.0,
                "corroboration_score": 0.0,
                "contradictions": [],
                "summary": "No evidence submitted."
            }

        total_rel = sum(e.reliability for e in evidence_list)
        total_rev = sum(e.relevance for e in evidence_list)
        avg_rel = total_rel / len(evidence_list)
        avg_rev = total_rev / len(evidence_list)

        # Corroboration: multiple evidence items supporting the same facts or category
        categories = set(e.category for e in evidence_list)
        corroboration = min(1.0, 0.4 + (0.2 * len(categories)) + (0.1 * min(len(evidence_list), 4)))

        # Check for contradictions between suspect alibi and collected evidence
        contradictions = []
        if suspect:
            for ev in evidence_list:
                for f in ev.facts_unlocked:
                    if "cctv_shows" in f and "cinema" in suspect.alibi.lower():
                        contradictions.append(f"CCTV footage directly refutes {suspect.name}'s cinema alibi.")
                    if "fingerprints_on_knife" in f and "never touched" in suspect.statement.lower():
                        contradictions.append(f"Fingerprint analysis on knife contradicts {suspect.name}'s claim of never touching the knife.")
                    if "phone_threat" in f and "good terms" in suspect.statement.lower():
                        contradictions.append(f"Threatening text messages contradict {suspect.name}'s claim of being on peaceful terms.")

        return {
            "total_items": len(evidence_list),
            "avg_reliability": round(avg_rel, 2),
            "avg_relevance": round(avg_rev, 2),
            "corroboration_score": round(corroboration, 2),
            "contradictions": contradictions,
            "summary": f"Bundle of {len(evidence_list)} evidence items with avg reliability {round(avg_rel*100)}% and relevance {round(avg_rev*100)}%."
        }
