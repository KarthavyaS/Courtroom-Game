"""Natural Language Rule-Based Argument Parser for LOGIC COURTROOM.
Maps player-entered natural language sentences, premises, and lawyer statements
to formal logical propositions.
"""

import re
from typing import List, Dict, Tuple, Optional, Any

# Standard dictionary mapping keywords and regex patterns to normalized logical propositions
PROPOSITION_PATTERNS = [
    (r"(fingerprint|prints?).*(knife|weapon|blade)", "fingerprints_on_knife"),
    (r"(knife|wound|stab|blade).*(cause|death|killed|fatal)", "victim_cause_of_death_knife_wound"),
    (r"(knife|weapon).*(belong|owned|registered|purchased).*(suspect|victor|clara|arthur|julian)", "knife_owned_by_suspect"),
    (r"(knife|weapon).*(found|scene|room|floor)", "knife_found_at_scene"),
    (r"(suspect|victor|clara|arthur|julian).*(present|scene|mansion|room|midnight|12)", "suspect_present_at_scene_at_time"),
    (r"(suspect|victor|clara|arthur|julian).*(motive|money|inherit|debt|threat)", "suspect_has_motive"),
    (r"(alibi).*(fake|refuted|false|contradict|unverified|disproven)", "suspect_alibi_refuted"),
    (r"(alibi).*(confirmed|verified|true|valid|solid)", "suspect_alibi_verified"),
    (r"(cctv|camera).*(footage|shows|recorded).*(suspect|entering)", "cctv_shows_suspect_entry"),
    (r"(cctv|camera).*(tampered|deleted|wiped|offline)", "cctv_tampered_by_suspect"),
    (r"(blood|dna).*(stain|clothes|shoes|knife).*(suspect)", "suspect_dna_on_evidence"),
    (r"(broken|open).*(window|door|entry|forced)", "forced_entry_via_window"),
    (r"(phone|text|messages|email).*(threat|blackmail|money)", "incriminating_phone_messages"),
    (r"(witness|statement|heard|saw).*(argument|shouting|quarrel)", "witness_heard_argument"),
    (r"(access|key|code).*(safe|vault|room)", "suspect_had_safe_access"),
    (r"(transaction|transfer|ledger|embezzle).*(account|money)", "financial_fraud_detected"),
]


class ArgumentParser:
    """Rule-based parser translating human legal claims to propositional identifiers."""

    def __init__(self):
        self.patterns = PROPOSITION_PATTERNS

    def parse_sentence(self, sentence: str) -> Tuple[str, float, str]:
        """Parses a single natural sentence into a normalized proposition symbol.
        Returns:
            (proposition_id, confidence_score, explanation)
        """
        clean_text = sentence.strip().lower()
        if not clean_text:
            return "empty_premise", 0.0, "Empty premise provided."

        # If already an exact proposition format (snake_case)
        if "_" in clean_text and " " not in clean_text:
            return clean_text, 1.0, f"Direct formal proposition '{clean_text}'."

        for pattern, prop_id in self.patterns:
            if re.search(pattern, clean_text):
                return prop_id, 0.9, f"Mapped '{sentence}' to '{prop_id}' via keyword pattern."

        # Fallback slugification
        clean_slug = re.sub(r"[^\w\s]", "", clean_text)
        slug = "_".join(clean_slug.split()[:5])
        return slug, 0.4, f"Custom proposition created from phrase: '{slug}'."

    def parse_argument(self, raw_premises: List[str], raw_conclusion: str) -> Dict[str, Any]:
        """Parses a full argument structure."""
        parsed_premises = []
        premise_explanations = []

        for p in raw_premises:
            prop_id, conf, exp = self.parse_sentence(p)
            parsed_premises.append(prop_id)
            premise_explanations.append({"raw": p, "symbol": prop_id, "confidence": conf, "explanation": exp})

        concl_id, concl_conf, concl_exp = self.parse_sentence(raw_conclusion)

        return {
            "parsed_premises": parsed_premises,
            "parsed_conclusion": concl_id,
            "premise_details": premise_explanations,
            "conclusion_details": {"raw": raw_conclusion, "symbol": concl_id, "confidence": concl_conf, "explanation": concl_exp}
        }
