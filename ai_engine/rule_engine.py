"""Rule Engine and Legal Safeguards for LOGIC COURTROOM.
Defines formal propositional rules for forensic investigations and safeguards against logical fallacies.
"""

from typing import List, Dict, Any, Optional
from .knowledge_base import Rule, KnowledgeBase

# Predefined standard courtroom inference rules
STANDARD_RULES = [
    Rule(
        id="RULE_001",
        name="Physical Contact with Weapon",
        antecedents=["knife_found_at_scene", "suspect_fingerprints_on_knife"],
        consequent="suspect_had_contact_with_knife",
        description="Fingerprints on the murder weapon establish physical handling by the suspect.",
        category="forensic"
    ),
    Rule(
        id="RULE_002",
        name="Lethal Weapon Identification",
        antecedents=["victim_cause_of_death_stab_wound", "knife_found_at_scene", "blood_on_knife_matches_victim"],
        consequent="knife_is_murder_weapon",
        description="Stab wound cause of death combined with victim's blood on knife establishes it as the murder weapon.",
        category="forensic"
    ),
    Rule(
        id="RULE_003",
        name="Opportunity and Scene Presence",
        antecedents=["cctv_shows_suspect_entry", "suspect_present_at_mansion_at_midnight"],
        consequent="suspect_had_opportunity",
        description="Presence at the scene during time of death establishes opportunity.",
        category="legal"
    ),
    Rule(
        id="RULE_004",
        name="Alibi Falsification",
        antecedents=["cctv_shows_suspect_entry", "suspect_claimed_cinema_alibi"],
        consequent="suspect_alibi_refuted",
        description="Direct CCTV footage of suspect at the crime scene directly refutes an external alibi.",
        category="alibi"
    ),
    Rule(
        id="RULE_005",
        name="Motive and Intent",
        antecedents=["incriminating_phone_messages", "suspect_debt_or_inheritance"],
        consequent="suspect_has_proven_motive",
        description="Threatening messages combined with financial inheritance/debt establish strong motive.",
        category="legal"
    ),
    Rule(
        id="RULE_006",
        name="Proof of Guilt Beyond Reasonable Doubt",
        antecedents=[
            "knife_is_murder_weapon",
            "suspect_had_contact_with_knife",
            "suspect_had_opportunity",
            "suspect_alibi_refuted",
            "suspect_has_proven_motive"
        ],
        consequent="suspect_guilty_beyond_reasonable_doubt",
        description="Full chain of evidence: Murder weapon identified + physical contact + opportunity + refuted alibi + proven motive proves guilt beyond reasonable doubt.",
        category="legal"
    ),
    # Theft Case Rules
    Rule(
        id="RULE_101",
        name="Safe Unauthorized Access",
        antecedents=["suspect_had_safe_key", "safe_opened_without_forced_entry"],
        consequent="suspect_unauthorized_vault_access",
        description="Possession of safe key and unforced entry indicates insider access.",
        category="forensic"
    ),
    Rule(
        id="RULE_102",
        name="Possession of Stolen Property",
        antecedents=["necklace_found_in_suspect_bag", "necklace_identified_as_stolen"],
        consequent="suspect_guilty_of_theft",
        description="Possession of stolen necklace with vault access confirms grand larceny.",
        category="legal"
    ),
    # Corporate Fraud Rules
    Rule(
        id="RULE_201",
        name="Unauthorized Fund Transfer",
        antecedents=["financial_fraud_detected", "suspect_digital_signature_used"],
        consequent="suspect_executed_fraudulent_transfer",
        description="Digital credentials matching suspect used for fraudulent transaction.",
        category="forensic"
    ),
    Rule(
        id="RULE_202",
        name="Corporate Embezzlement Conviction",
        antecedents=["suspect_executed_fraudulent_transfer", "offshore_account_linked_to_suspect"],
        consequent="suspect_guilty_of_embezzlement",
        description="Fraudulent transfer directly linked to suspect's offshore account confirms embezzlement.",
        category="legal"
    )
]


class RuleEngine:
    """Manages rules and verifies safeguards against common courtroom fallacies."""

    def __init__(self):
        self.rules = {r.id: r for r in STANDARD_RULES}

    def get_all_rules(self) -> List[Rule]:
        return list(self.rules.values())

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        return self.rules.get(rule_id)

    def load_custom_rules(self, rules_data: List[Dict[str, Any]]) -> None:
        for r_dict in rules_data:
            rule = Rule.from_dict(r_dict)
            self.rules[rule.id] = rule

    def check_safeguards(
        self, premises: List[str], conclusion: str, kb: KnowledgeBase
    ) -> List[Dict[str, str]]:
        """Verifies if the submitted argument commits common logical/legal fallacies.
        Returns a list of warnings or violations.
        """
        violations = []
        prem_set = set(p.lower() for p in premises)
        concl = conclusion.lower()

        # Safeguard 1: Motive alone does not prove guilt
        if "suspect_has_proven_motive" in prem_set or "suspect_has_motive" in prem_set:
            if "guilty" in concl:
                if not any(k in prem_set for k in ["knife_is_murder_weapon", "suspect_had_opportunity", "suspect_had_contact_with_knife", "suspect_unauthorized_vault_access", "suspect_executed_fraudulent_transfer"]):
                    violations.append({
                        "type": "Motive Is Not Guilt",
                        "severity": "CRITICAL",
                        "message": "Motive alone is circumstantial. Without physical evidence or opportunity linking the suspect to the act, guilt cannot be established."
                    })

        # Safeguard 2: Fingerprints alone do not prove murder
        if "suspect_fingerprints_on_knife" in prem_set or "fingerprints_on_knife" in prem_set or "suspect_had_contact_with_knife" in prem_set:
            if "guilty" in concl:
                if "knife_is_murder_weapon" not in prem_set and "victim_cause_of_death_stab_wound" not in prem_set:
                    violations.append({
                        "type": "Contact Is Not Homicide",
                        "severity": "HIGH",
                        "message": "Fingerprints establish that the suspect handled the knife, but do not prove it was the murder weapon or used in the homicide without cause of death link."
                    })

        # Safeguard 3: Presence alone does not prove guilt
        if "suspect_had_opportunity" in prem_set or "suspect_present_at_scene_at_time" in prem_set:
            if "guilty" in concl and len(prem_set) <= 2:
                violations.append({
                    "type": "Presence Is Not Guilt",
                    "severity": "HIGH",
                    "message": "Being present at the crime scene demonstrates opportunity, but does not independently establish criminal act."
                })

        # Safeguard 4: Contradicted alibi vs verified alibi
        if "suspect_alibi_verified" in kb.facts and "guilty" in concl:
            violations.append({
                "type": "Direct Contradiction",
                "severity": "FATAL",
                "message": "The suspect has a verified alibi on record. Asserting guilt without refuting the alibi constitutes an irreconcilable contradiction."
            })

        return violations
