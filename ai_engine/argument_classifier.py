"""Traditional AI Argument Classifier & Conversational Reasoner for LOGIC COURTROOM.
Categorizes submitted arguments and conversational pleadings into:
1. RELEVANT_AND_SUPPORTED
2. RELEVANT_BUT_INSUFFICIENT
3. CONVERSATIONAL_INQUIRY
4. CONTRADICTED
5. UNSUPPORTED_ACCUSATION
6. IRRELEVANT_UNWANTED (Strictly for completely off-topic gibberish)
"""

from typing import List, Dict, Any, Optional, Set
from models.argument import Argument
from models.suspect import Suspect
from models.evidence import Evidence
from .knowledge_base import KnowledgeBase
from .forward_chaining import ForwardChainingEngine
from .rule_engine import RuleEngine

class ArgumentEvaluation:
    """Structured evaluation returned by the AI reasoning engine."""
    def __init__(
        self,
        category: str,
        logical_validity: bool,
        evidence_relevance: float,
        supporting_facts: List[str],
        contradicting_facts: List[str],
        unsupported_claims: List[str],
        reasoning_trace: List[str],
        score: int,
        judge_response_category: str,
        judge_dialogue: str,
        judge_expression: str,
        suspect_expression: str,
        is_unwanted: bool
    ):
        self.category = category
        self.logical_validity = logical_validity
        self.evidence_relevance = evidence_relevance
        self.supporting_facts = supporting_facts
        self.contradicting_facts = contradicting_facts
        self.unsupported_claims = unsupported_claims
        self.reasoning_trace = reasoning_trace
        self.score = score
        self.judge_response_category = judge_response_category
        self.judge_dialogue = judge_dialogue
        self.judge_expression = judge_expression
        self.suspect_expression = suspect_expression
        self.is_unwanted = is_unwanted


class ArgumentClassifier:
    """Classifies arguments and conversational dialogues submitted to the court."""

    def __init__(self):
        self.forward_chainer = ForwardChainingEngine()
        self.rule_engine = RuleEngine()

    def classify_submission(
        self,
        argument_text: str,
        kb: KnowledgeBase,
        all_case_evidence: List[Evidence],
        selected_suspect: Optional[Suspect],
        known_case_facts: Optional[Set[str]] = None
    ) -> ArgumentEvaluation:
        text_lower = argument_text.lower().strip()

        # 1. Greetings / Formal Courtroom Conversation Openers
        greeting_cues = ["hello", "hi", "good morning", "good afternoon", "your honor", "greetings", "judge", "counsel", "start", "begin", "court"]
        if any(g in text_lower for g in greeting_cues) and len(text_lower.split()) <= 6:
            return ArgumentEvaluation(
                category="CONVERSATIONAL_INQUIRY",
                logical_validity=True,
                evidence_relevance=0.4,
                supporting_facts=["Courtroom decorum acknowledged"],
                contradicting_facts=[],
                unsupported_claims=[],
                reasoning_trace=["Player opened with formal address or greeting."],
                score=2,
                judge_response_category="GREETING",
                judge_dialogue="Greetings, Counsel. The court is ready to hear your findings. What evidence or timeline connects to the accused?",
                judge_expression="neutral",
                suspect_expression="neutral",
                is_unwanted=False
            )

        # 2. Comprehensive Lexicon of Case, Investigation, and Forensic terms
        case_lexicon = [
            # Suspects & Persons
            "victor", "vance", "clara", "sterling", "finch", "arthur", "julian", "hayes",
            "butler", "doctor", "heir", "brother", "partner", "suspect", "accused", "witness", "physician",
            # Crime Elements & Means
            "knife", "blade", "stab", "wound", "blood", "murder", "kill", "killed", "dying", "died",
            "death", "autopsy", "coroner", "weapon", "fingerprint", "prints", "glass", "glove",
            "vault", "safe", "lock", "key", "keycard", "signature", "wine", "goblet", "poison",
            # Timeline & Opportunity
            "cctv", "camera", "footage", "timeline", "midnight", "11:45", "11:50", "10:30", "time",
            "mansion", "study", "manor", "scene", "room", "door", "window", "balcony", "cellar",
            "inside", "outside", "entry", "exit", "presence", "present", "alibi", "cinema", "movies",
            # Motive & Intent
            "debt", "will", "inheritance", "money", "audit", "fraud", "transfer", "threat", "phone",
            "message", "motive", "intent", "estate", "pounds", "dollars",
            # Legal & Conversational Inquiry
            "evidence", "proof", "prove", "fact", "facts", "record", "statement", "testimony",
            "question", "inquiry", "why", "how", "what", "where", "who", "when", "show", "tell",
            "think", "believe", "look", "found", "present", "innocent", "guilty", "lie", "lied", "truth",
            "exhibit", "argument", "claim", "theory", "reason", "account"
        ]

        # Broad off-topic blacklist (things completely outside detective/courtroom law)
        blatant_offtopic = [
            "pizza", "burger", "football", "cricket", "videogame", "minecraft", "fortnite",
            "superhero", "weather downtown is very rainy", "sports car", "banana", "chocolate",
            "movie review", "asdf", "qwerty", "blah blah", "xyz"
        ]

        is_strictly_offtopic = any(ot in text_lower for ot in blatant_offtopic)

        # Count matched terms
        matches = [kw for kw in case_lexicon if kw in text_lower]
        has_case_relevance = len(matches) > 0

        # Verified facts from evidence and KB
        verified_facts = set(kb.get_facts())
        for ev in all_case_evidence:
            if ev.collected:
                for f in getattr(ev, 'facts_unlocked', []):
                    verified_facts.add(f.lower())

        # Contradiction checks
        contradicting = []
        if "outside" in text_lower and ("cctv_shows_suspect_entry" in verified_facts or "suspect_present_at_mansion_at_midnight" in verified_facts):
            contradicting.append("Forensic CCTV timeline places suspect inside the mansion at midnight")
        if "never touched" in text_lower and "suspect_fingerprints_on_knife" in verified_facts:
            contradicting.append("Latent fingerprint forensics confirm suspect contact with the murder weapon")

        if contradicting:
            return ArgumentEvaluation(
                category="CONTRADICTED",
                logical_validity=False,
                evidence_relevance=0.4,
                supporting_facts=[f"Keyword '{m}'" for m in matches[:3]],
                contradicting_facts=contradicting,
                unsupported_claims=[],
                reasoning_trace=["Statement conflicts with forensic facts verified on the official record."],
                score=0,
                judge_response_category="CONTRADICTED",
                judge_dialogue="That assertion conflicts with the verified forensic timeline on record. Please review the evidence carefully, Counsel.",
                judge_expression="thinking",
                suspect_expression="surprised",
                is_unwanted=False
            )

        # Pure unsupported accusation ("He did it", "She is guilty")
        is_bare_accusation = any(p in text_lower for p in ["is guilty", "definitely the murderer", "killed him", "committed the crime"]) and len(matches) <= 2
        if is_bare_accusation:
            return ArgumentEvaluation(
                category="UNSUPPORTED_ACCUSATION",
                logical_validity=False,
                evidence_relevance=0.3,
                supporting_facts=[f"Accusation directed at {selected_suspect.name if selected_suspect else 'accused'}"],
                contradicting_facts=[],
                unsupported_claims=[argument_text],
                reasoning_trace=["Accusation made without intermediate evidentiary proof."],
                score=3,
                judge_response_category="UNSUPPORTED_ACCUSATION",
                judge_dialogue="Counsel, an assertion of guilt requires corroboration. Which specific forensic exhibits substantiate this claim?",
                judge_expression="thinking",
                suspect_expression="angry",
                is_unwanted=False
            )

        # Forensic Pillars
        pillars = set()
        if any(w in text_lower for w in ["knife", "fingerprint", "prints", "vault", "safe", "lock", "signature", "keycard", "weapon", "glass", "wine", "glove"]):
            pillars.add("MEANS")
        if any(w in text_lower for w in ["cctv", "camera", "footage", "timeline", "11:45", "11:50", "midnight", "entry", "exit", "balcony", "study", "manor", "mansion", "alibi", "cinema"]):
            pillars.add("OPPORTUNITY")
        if any(w in text_lower for w in ["debt", "will", "inheritance", "transfer", "money", "threat", "phone", "motive", "fraud", "audit"]):
            pillars.add("MOTIVE")
        if any(w in text_lower for w in ["autopsy", "stab", "wound", "death", "cause", "poison", "coroner", "killed"]):
            pillars.add("CORPUS_DELICTI")

        # Classification
        if len(pillars) >= 2 or (len(pillars) == 1 and "OPPORTUNITY" in pillars and len(argument_text.split()) > 6):
            return ArgumentEvaluation(
                category="RELEVANT_SUPPORTED",
                logical_validity=True,
                evidence_relevance=0.9,
                supporting_facts=[f"Pillar: {p}" for p in pillars],
                contradicting_facts=[],
                unsupported_claims=[],
                reasoning_trace=["Valid deductive argument linking evidence across verified legal pillars."],
                score=15,
                judge_response_category="SUPPORTED",
                judge_dialogue="That is relevant and supported by the forensic record. Let us examine how this connects with the chain of causation.",
                judge_expression="satisfied",
                suspect_expression="nervous",
                is_unwanted=False
            )

        elif len(pillars) == 1:
            # Single pillar established
            p_name = next(iter(pillars))
            return ArgumentEvaluation(
                category="RELEVANT_INSUFFICIENT",
                logical_validity=True,
                evidence_relevance=0.6,
                supporting_facts=[f"Pillar: {p_name}"],
                contradicting_facts=[],
                unsupported_claims=["Requires complementary corroboration across additional pillars"],
                reasoning_trace=[f"Evidence establishes {p_name}, but needs opportunity or motive link."],
                score=6,
                judge_response_category="INSUFFICIENT",
                judge_dialogue="That evidence establishes a relevant element. However, on its own it does not prove the complete charge. What further evidence connects this?",
                judge_expression="thinking",
                suspect_expression="nervous",
                is_unwanted=False
            )

        elif has_case_relevance and not is_strictly_offtopic:
            # Friendly conversational inquiry
            return ArgumentEvaluation(
                category="CONVERSATIONAL_INQUIRY",
                logical_validity=True,
                evidence_relevance=0.5,
                supporting_facts=[f"Referenced: {', '.join(matches[:4])}"],
                contradicting_facts=[],
                unsupported_claims=[],
                reasoning_trace=["Conversational inquiry or investigative proposition."],
                score=4,
                judge_response_category="INQUIRY",
                judge_dialogue="The court notes this investigative point, Counsel. Please proceed by presenting the forensic exhibit supporting this.",
                judge_expression="neutral",
                suspect_expression="neutral",
                is_unwanted=False
            )

        else:
            # Only truly off-topic / gibberish nonsense gets warned
            return ArgumentEvaluation(
                category="IRRELEVANT_UNWANTED",
                logical_validity=False,
                evidence_relevance=0.0,
                supporting_facts=[],
                contradicting_facts=[],
                unsupported_claims=[argument_text],
                reasoning_trace=["Text is completely unrelated to the crime, evidence, or courtroom proceedings."],
                score=-5,
                judge_response_category="IRRELEVANT",
                judge_dialogue="Counsel, how is that relevant to this court? Please present evidence related to the case. This courtroom is not a place for unrelated statements.",
                judge_expression="angry",
                suspect_expression="neutral",
                is_unwanted=True
            )
