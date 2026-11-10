"""AI Judge Cross-Examination & Interactive Deliberation Engine for LOGIC COURTROOM.
Generates dynamic judicial reactions, cross-examination challenges, and questions
as the player submits arguments one by one during a live trial.
"""

from typing import List, Dict, Any, Optional, Set
from models.argument import Argument
from models.suspect import Suspect
from models.evidence import Evidence
from .knowledge_base import KnowledgeBase
from .forward_chaining import ForwardChainingEngine
from .rule_engine import RuleEngine

class JudgeDialogueEngine:
    """Simulates an interactive traditional AI Judge cross-examining counsel."""

    def __init__(self):
        self.forward_chainer = ForwardChainingEngine()
        self.rule_engine = RuleEngine()

    def evaluate_trial_step(
        self,
        new_argument: Argument,
        cumulative_kb: KnowledgeBase,
        all_collected_evidence: List[Evidence],
        suspect: Optional[Suspect]
    ) -> Dict[str, Any]:
        """Evaluates a single argument submitted during an interactive trial session.
        Returns the judge's reaction, question, deductive progress, and element status.
        """
        # 1. Update cumulative KB with new premises
        for p in new_argument.premises:
            cumulative_kb.tell(p)

        # Run forward deduction
        derived_facts, trace = self.forward_chainer.run(cumulative_kb)

        # Check key legal pillars
        pillars_established = []
        pillars_missing = []

        # 1. Cause of Death / Crime Act
        if any(f in derived_facts for f in ["victim_cause_of_death_stab_wound", "safe_opened_without_forced_entry", "financial_fraud_detected"]):
            pillars_established.append("Corpus Delicti / Actus Reus (Crime Act Proven)")
        else:
            pillars_missing.append("Cause of Death / Crime Method")

        # 2. Weapon / Instrument Link
        if any(f in derived_facts for f in ["suspect_had_contact_with_knife", "knife_is_murder_weapon", "suspect_unauthorized_vault_access", "suspect_executed_fraudulent_transfer"]):
            pillars_established.append("Physical Instrument / Means Linked to Suspect")
        else:
            pillars_missing.append("Physical Connection to Murder Weapon / Asset")

        # 3. Opportunity / Scene Presence
        if any(f in derived_facts for f in ["suspect_had_opportunity", "cctv_shows_suspect_entry", "marcus_logged_on_second_floor", "suspect_digital_signature_used"]):
            pillars_established.append("Opportunity & Presence at Time of Crime")
        else:
            pillars_missing.append("Opportunity / Timeline Presence")

        # 4. Alibi Falsification
        if "suspect_alibi_refuted" in derived_facts:
            pillars_established.append("Alibi Shattered by Objective Evidence")
        elif "suspect_alibi_verified" in derived_facts:
            pillars_established.append("WARNING: Suspect Holds Verified True Alibi")
        else:
            pillars_missing.append("Alibi Verification / Disproof")

        # 5. Proven Motive
        if any(f in derived_facts for f in ["suspect_has_proven_motive", "suspect_debt_or_inheritance", "offshore_account_linked_to_suspect"]):
            pillars_established.append("Criminal Motive & Intent Established")
        else:
            pillars_missing.append("Motive / Financial Gain")

        # Check for safeguard violations
        violations = self.rule_engine.check_safeguards(list(derived_facts), new_argument.conclusion, cumulative_kb)

        # Generate Contextual Judge Dialogue & Inquiry
        judge_speech = ""
        judge_question = ""
        mood = "neutral"
        sound_effect = "deliberate"

        if any(v["severity"] == "FATAL" for v in violations):
            mood = "stern"
            sound_effect = "gavel_slam"
            judge_speech = f"OBJECTION! The court notes that {suspect.name if suspect else 'the accused'} has a verified independent alibi on the official record! You cannot assert guilt while ignoring exculpatory evidence."
            judge_question = "How do you account for the confirmed alibi before proceeding with this indictment?"

        elif any(v["severity"] == "CRITICAL" for v in violations):
            mood = "stern"
            sound_effect = "gavel_slam"
            judge_speech = "Counsel, motive alone does NOT establish criminal guilt! A desire for money does not prove the accused wielded the fatal blade."
            judge_question = "Where is the forensic evidence placing the weapon in the suspect's hands?"

        elif "suspect_guilty_beyond_reasonable_doubt" in derived_facts or len(pillars_established) >= 4:
            mood = "satisfied"
            sound_effect = "gavel_slam"
            judge_speech = "The court is deeply impressed. Your deductive chain connects the weapon, opportunity, refuted alibi, and motive with mathematical precision."
            judge_question = "The prosecution has established a prima facie case. You may call for final verdict, or introduce further corroboration."

        elif "suspect_alibi_refuted" in derived_facts and "suspect_has_proven_motive" not in derived_facts:
            mood = "interested"
            judge_speech = "The CCTV footage unequivocally demolishes the claimed alibi! The suspect was indeed present at the scene at midnight."
            judge_question = "Counsel, what was the suspect's motive for this heinous attack? Do you have phone records or financial evidence?"

        elif "suspect_had_contact_with_knife" in derived_facts and "suspect_had_opportunity" not in derived_facts:
            mood = "interested"
            judge_speech = "The forensic fingerprint match is accepted into evidence. The suspect definitely handled the blade."
            judge_question = "However, how do you prove the suspect was in the mansion at midnight, given their claim of being downtown?"

        elif "victim_cause_of_death_stab_wound" in derived_facts and len(pillars_established) <= 1:
            mood = "interested"
            judge_speech = "The coroner's autopsy is entered into record. The cause of death is established as a lethal knife wound."
            judge_question = "Now, Counsel—what physical weapon was recovered, and how do you connect it to the accused?"

        else:
            mood = "neutral"
            judge_speech = f"The court has entered your argument into the trial record. ({len(new_argument.premises)} premise(s) presented)."
            if pillars_missing:
                judge_question = f"Counsel, you have yet to establish: {pillars_missing[0]}. How do you answer this gap?"
            else:
                judge_question = "Present your next piece of evidence or submit for final judgment."

        return {
            "judge_speech": judge_speech,
            "judge_question": judge_question,
            "judge_mood": mood,
            "sound_effect": sound_effect,
            "derived_facts": list(derived_facts),
            "pillars_established": pillars_established,
            "pillars_missing": pillars_missing,
            "rule_trace": [s.explanation for s in trace],
            "violations": violations
        }
