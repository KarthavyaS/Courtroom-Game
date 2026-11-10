"""Courtroom Trial Session State & Discipline Manager for LOGIC COURTROOM.
Tracks live adversarial dialogue, submitted arguments, logical evaluations,
unwanted argument penalties (warnings 1-3, termination on 4th), and cumulative trial score.
"""

from typing import List, Dict, Any, Optional
from models.argument import Argument
from models.suspect import Suspect
from models.evidence import Evidence
from ai_engine.knowledge_base import KnowledgeBase
from ai_engine.argument_classifier import ArgumentClassifier, ArgumentEvaluation
from services.sound_service import get_sound_service

class CourtMessage:
    """A single dialogue exchange message in the trial transcript."""
    def __init__(self, speaker: str, text: str, expression: str = "neutral", is_warning: bool = False):
        self.speaker = speaker
        self.text = text
        self.expression = expression
        self.is_warning = is_warning


class CourtroomSession:
    """Manages an active trial proceeding, dialogue history, and unwanted argument discipline."""

    def __init__(self, case_data: Any, selected_suspect: Optional[Suspect]):
        self.case_data = case_data
        self.selected_suspect = selected_suspect
        self.classifier = ArgumentClassifier()
        self.kb = KnowledgeBase()
        
        # Load initial case facts into KB
        initial_facts = getattr(case_data, 'initial_facts', getattr(case_data, 'facts', [])) if case_data else []
        for f in initial_facts:
            self.kb.tell(f)

        # Trial State
        self.unwanted_argument_count: int = 0
        self.max_unwanted_allowed: int = 3
        self.is_hearing_terminated: bool = False
        self.termination_reason: str = ""
        self.cumulative_score: int = 0
        self.arguments_submitted: List[Dict[str, Any]] = []
        self.messages: List[CourtMessage] = []

        # Start initial greeting
        suspect_name = selected_suspect.name if selected_suspect else "The Accused"
        self.messages.append(
            CourtMessage(
                speaker="Judge",
                text=f"The court is now in session regarding the indictment of {suspect_name}. Counsel for the Prosecution, present your initial argument and supporting facts.",
                expression="neutral"
            )
        )

    def restart_hearing(self):
        """Resets the hearing state and discipline counters for a fresh trial session."""
        self.unwanted_argument_count = 0
        self.is_hearing_terminated = False
        self.termination_reason = ""
        self.cumulative_score = 0
        self.arguments_submitted.clear()
        self.messages.clear()

        # Re-initialize KB
        self.kb = KnowledgeBase()
        initial_facts = getattr(self.case_data, 'initial_facts', getattr(self.case_data, 'facts', [])) if self.case_data else []
        for f in initial_facts:
            self.kb.tell(f)

        suspect_name = self.selected_suspect.name if self.selected_suspect else "The Accused"
        self.messages.append(
            CourtMessage(
                speaker="Judge",
                text=f"A new hearing has commenced for {suspect_name}. Counsel, present your substantiated arguments.",
                expression="neutral"
            )
        )

    def submit_argument(self, argument_text: str) -> ArgumentEvaluation:
        """Processes a player argument through the AI classifier and handles discipline penalties."""
        sound_service = get_sound_service()

        # If already terminated, reject
        if self.is_hearing_terminated:
            return ArgumentEvaluation(
                category="HEARING_TERMINATED",
                logical_validity=False,
                evidence_relevance=0.0,
                supporting_facts=[],
                contradicting_facts=[],
                unsupported_claims=[],
                reasoning_trace=["Hearing is currently terminated."],
                score=0,
                judge_response_category="TERMINATED",
                judge_dialogue="This hearing has been terminated by the court. You must restart the proceeding to submit further arguments.",
                judge_expression="angry",
                suspect_expression="neutral",
                is_unwanted=False
            )

        # 1. Record Player Dialogue
        self.messages.append(
            CourtMessage(
                speaker="Player Counsel",
                text=argument_text,
                expression="speaking"
            )
        )

        # 2. AI Classifier Evaluation
        ev_list = getattr(self.case_data, 'evidence_list', getattr(self.case_data, 'evidence', [])) if self.case_data else []
        eval_result = self.classifier.classify_submission(
            argument_text=argument_text,
            kb=self.kb,
            all_case_evidence=ev_list,
            selected_suspect=self.selected_suspect
        )

        # 3. Process Discipline / Unwanted Argument System
        if eval_result.is_unwanted:
            self.unwanted_argument_count += 1
            sound_service.play("warning")

            if self.unwanted_argument_count == 1:
                # 1st Warning
                judge_text = (
                    "FIRST WARNING: Counsel, that submission is entirely off-topic and unsupported by the case file. "
                    "This court requires factual relevance. Please present evidence directly tied to the charge."
                )
                eval_result.judge_dialogue = judge_text
                eval_result.judge_expression = "angry"
                self.messages.append(CourtMessage("Judge", judge_text, expression="angry", is_warning=True))

            elif self.unwanted_argument_count == 2:
                # 2nd Warning: Penalty -5 pts
                self.cumulative_score = max(0, self.cumulative_score - 5)
                judge_text = (
                    "SECOND WARNING: Counsel, repeated irrelevant submissions are an unacceptable waste of judicial time! "
                    "A discipline deduction has been applied. Focus your line of questioning on the evidence."
                )
                eval_result.judge_dialogue = judge_text
                eval_result.judge_expression = "angry"
                self.messages.append(CourtMessage("Judge", judge_text, expression="angry", is_warning=True))

            elif self.unwanted_argument_count == 3:
                # 3rd Warning: Penalty -10 pts
                self.cumulative_score = max(0, self.cumulative_score - 10)
                judge_text = (
                    "FINAL WARNING: Counsel, you are on the verge of contempt! One more frivolous or ungrounded statement "
                    "will result in immediate termination of this hearing!"
                )
                eval_result.judge_dialogue = judge_text
                eval_result.judge_expression = "angry"
                self.messages.append(CourtMessage("Judge", judge_text, expression="angry", is_warning=True))

            else:
                # 4th Unwanted Argument: Terminate Hearing!
                self.is_hearing_terminated = True
                self.termination_reason = "Repeated submission of irrelevant and frivolous arguments violating courtroom procedure."
                sound_service.play("gavel")

                termination_speech = (
                    "Counsel, this court has repeatedly asked you to present relevant facts and logically supported arguments. "
                    "Instead, you have continued to submit unrelated claims. This hearing is hereby terminated. "
                    "The case has been disclosed due to repeated misuse of courtroom proceedings. "
                    "Review your evidence and return with a proper argument."
                )
                eval_result.judge_dialogue = termination_speech
                eval_result.judge_expression = "angry"
                self.messages.append(CourtMessage("Judge", termination_speech, expression="angry", is_warning=True))
                self.messages.append(
                    CourtMessage(
                        "Bailiff",
                        "HEARING TERMINATED BY ORDER OF THE COURT. [Case Disclosed due to Procedural Contempt]",
                        expression="neutral",
                        is_warning=True
                    )
                )
        else:
            # Valid or constructive evaluation
            self.cumulative_score += max(0, eval_result.score)
            self.messages.append(
                CourtMessage(
                    speaker="Judge",
                    text=eval_result.judge_dialogue,
                    expression=eval_result.judge_expression
                )
            )

        # 4. Save history record
        self.arguments_submitted.append({
            "text": argument_text,
            "category": eval_result.category,
            "score": eval_result.score,
            "judge_dialogue": eval_result.judge_dialogue,
            "is_unwanted": eval_result.is_unwanted
        })

        return eval_result
