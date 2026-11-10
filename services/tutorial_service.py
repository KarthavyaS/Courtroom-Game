"""Interactive Tutorial Service for LOGIC COURTROOM.
Defines 7 guided interactive tutorial steps with clear descriptions,
visual highlights, and practice prompts for beginners.
"""

from typing import Dict, Any, List

class TutorialService:
    """Manages the 7-step interactive tutorial content and progression."""

    STEPS = [
        {
            "step": 1,
            "title": "STEP 1: UNDERSTAND THE CASE",
            "subtitle": "Case Briefing & Investigation Objective",
            "icon": "dossier",
            "description": (
                "Every case begins with an official dossier. Read what happened, where the incident occurred, "
                "and who was present. Pay close attention to the Investigation Objective, which states "
                "the precise logical claim you must prove to the AI Judge in court."
            ),
            "key_takeaway": "Key Tip: Note initial known facts and victim details before stepping into the crime scene."
        },
        {
            "step": 2,
            "title": "STEP 2: INVESTIGATE THE CRIME SCENE",
            "subtitle": "Click Hotspots & Inspect Forensic Clues",
            "icon": "magnifier",
            "description": (
                "Explore the 2D crime scene room. Interactive objects illuminate when you hover over them. "
                "Click on any object to inspect its forensic details, category, and reliability. "
                "Choose 'Inspect' to examine or 'Collect Evidence' to add it to your legal inventory."
            ),
            "key_takeaway": "Key Tip: Collecting evidence unlocks crucial logical facts needed to build your court argument."
        },
        {
            "step": 3,
            "title": "STEP 3: REVIEW SUSPECTS & STATEMENTS",
            "subtitle": "Interrogations, Motives, & Contradictions",
            "icon": "suspect",
            "description": (
                "Each suspect has a profile containing their motive, stated alibi, and recorded testimony. "
                "Ask suspects predefined questions to uncover their whereabouts and test their alibis. "
                "Look for contradictions where physical evidence directly disproves what a suspect claimed."
            ),
            "key_takeaway": "Key Tip: A nervous expression alone is NOT proof of guilt—always back claims with physical evidence."
        },
        {
            "step": 4,
            "title": "STEP 4: COLLECT & ANALYZE EVIDENCE",
            "subtitle": "Forensic Reliability & Logical Facts",
            "icon": "evidence",
            "description": (
                "Open your Evidence Dashboard to review all collected forensic items. "
                "Each piece of evidence provides a Reliability score (0.0 - 1.0) and reveals underlying "
                "atomic propositions (facts) such as fingerprints, timestamps, or weapon identification."
            ),
            "key_takeaway": "Key Tip: Digital and Physical evidence with high reliability form the strongest arguments."
        },
        {
            "step": 5,
            "title": "STEP 5: BUILD A LOGICAL ARGUMENT",
            "subtitle": "Premises, Inference, & Conclusions",
            "icon": "logic",
            "description": (
                "Before going to court, use the Argument Workspace. Select your target suspect, "
                "choose your claim, and select supporting premises and evidence items. "
                "Logical rules connect your premises together: If A and B are true, then C follows."
            ),
            "key_takeaway": "Key Tip: Beware overreaching! Your conclusion must be strictly supported by your supplied premises."
        },
        {
            "step": 6,
            "title": "STEP 6: ENTER THE LIVE COURTROOM",
            "subtitle": "Presenting to the AI Judge",
            "icon": "court",
            "description": (
                "Deliver your argument before the AI Judge. The Judge will evaluate your submission "
                "using traditional Artificial Intelligence (Forward Chaining and Resolution). "
                "Engage in conversation, respond to the Judge's inquiries, and submit supporting facts."
            ),
            "key_takeaway": "Key Tip: Off-topic or nonsensical submissions will trigger Court Discipline warnings."
        },
        {
            "step": 7,
            "title": "STEP 7: UNDERSTAND THE VERDICT",
            "subtitle": "Supported vs. Not Proven vs. Contradicted",
            "icon": "gavel",
            "description": (
                "After closing statements, the AI Judge delivers a detailed ruling:\n"
                "• SUPPORTED: Your premises logically entail the conclusion beyond doubt.\n"
                "• NOT PROVEN: Your evidence is plausible but insufficient to prove the claim.\n"
                "• CONTRADICTED: The evidence or rules directly disprove your claim."
            ),
            "key_takeaway": "Key Tip: Review the AI inference trace on the Results screen to improve your future arguments!"
        }
    ]

    def __init__(self):
        self.current_step_index = 0

    @property
    def total_steps(self) -> int:
        return len(self.STEPS)

    @property
    def current_step_data(self) -> Dict[str, Any]:
        return self.STEPS[self.current_step_index]

    def next_step(self) -> bool:
        if self.current_step_index < self.total_steps - 1:
            self.current_step_index += 1
            return True
        return False

    def prev_step(self) -> bool:
        if self.current_step_index > 0:
            self.current_step_index -= 1
            return True
        return False

    def goto_step(self, step_index: int) -> None:
        self.current_step_index = max(0, min(self.total_steps - 1, step_index))

    def reset(self) -> None:
        self.current_step_index = 0
