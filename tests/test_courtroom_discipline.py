"""Unit Tests for Courtroom Discipline, Argument Classifier, and Trial Sessions."""

import unittest
from models.suspect import Suspect
from models.evidence import Evidence
from models.case import Case
from ai_engine.argument_classifier import ArgumentClassifier
from services.courtroom_session import CourtroomSession

class TestCourtroomDiscipline(unittest.TestCase):

    def setUp(self):
        self.suspect = Suspect(
            id="SUS-001",
            name="Victor Vance",
            occupation="Heir",
            relationship="Brother",
            motive="Personal debt",
            alibi="Cinema screening",
            statement="I was at the cinema downtown all evening.",
            known_facts=["suspect_claimed_cinema_alibi"],
            contradictions=[],
            avatar_type="heir",
            is_guilty=True
        )
        self.evidence = [
            Evidence(
                id="EVD-001",
                name="Autopsy Report",
                description="Victim died from knife stab wound.",
                category="Direct",
                reliability=1.0,
                relevance=1.0,
                collected=True,
                scene_pos=[100, 100, 50, 50],
                icon_type="body",
                facts_unlocked=["victim_cause_of_death_stab_wound"],
                details="Stab wound confirmed."
            ),
            Evidence(
                id="EVD-002",
                name="Bloody Knife",
                description="Chef knife with fingerprints.",
                category="Physical",
                reliability=0.95,
                relevance=0.95,
                collected=True,
                scene_pos=[200, 200, 50, 50],
                icon_type="knife",
                facts_unlocked=["knife_found_at_scene", "suspect_fingerprints_on_knife"],
                details="Fingerprints match Victor Vance."
            )
        ]
        self.case = Case(
            id="CASE001",
            title="The Midnight Murder",
            type="Murder",
            description="Arthur Vance was stabbed to death.",
            difficulty="HARD",
            reward=500,
            scene_name="Study",
            scene_type="mansion",
            solution_suspect_id="SUS-001",
            solution_conclusion="suspect_guilty_beyond_reasonable_doubt",
            solution_summary="Victor Vance committed the crime.",
            suspects=[self.suspect],
            evidence_list=self.evidence,
            initial_facts=["victim_cause_of_death_stab_wound", "knife_found_at_scene"],
            rules=[]
        )
        self.session = CourtroomSession(self.case, self.suspect)
        self.classifier = ArgumentClassifier()

    def test_relevant_supported_argument(self):
        """Supported argument with matching forensic facts should receive positive classification."""
        arg_text = "The CCTV footage and forensic fingerprints on the knife connect Victor Vance to the murder weapon."
        eval_res = self.session.submit_argument(arg_text)
        self.assertEqual(eval_res.category, "RELEVANT_SUPPORTED")
        self.assertFalse(eval_res.is_unwanted)
        self.assertEqual(self.session.unwanted_argument_count, 0)
        self.assertGreater(self.session.cumulative_score, 0)

    def test_relevant_insufficient_argument(self):
        """Relevant but incomplete argument should give constructive guidance and NOT penalize."""
        arg_text = "The fingerprints were on the knife."
        eval_res = self.session.submit_argument(arg_text)
        self.assertEqual(eval_res.category, "RELEVANT_INSUFFICIENT")
        self.assertFalse(eval_res.is_unwanted)
        # Must not increment unwanted counter
        self.assertEqual(self.session.unwanted_argument_count, 0)

    def test_unwanted_discipline_progression_to_termination(self):
        """Unwanted arguments should trigger warnings 1, 2, 3 and terminate on 4th."""
        # 1st Strike: Warning 1
        res1 = self.session.submit_argument("The suspect likes expensive sports cars and pizza.")
        self.assertTrue(res1.is_unwanted)
        self.assertEqual(self.session.unwanted_argument_count, 1)
        self.assertFalse(self.session.is_hearing_terminated)
        self.assertIn("FIRST WARNING", res1.judge_dialogue)

        # 2nd Strike: Warning 2 (-5 pts)
        res2 = self.session.submit_argument("The moon was shining bright in the sky.")
        self.assertTrue(res2.is_unwanted)
        self.assertEqual(self.session.unwanted_argument_count, 2)
        self.assertFalse(self.session.is_hearing_terminated)
        self.assertIn("SECOND WARNING", res2.judge_dialogue)

        # 3rd Strike: Final Warning (-10 pts)
        res3 = self.session.submit_argument("I think the weather downtown is very rainy.")
        self.assertTrue(res3.is_unwanted)
        self.assertEqual(self.session.unwanted_argument_count, 3)
        self.assertFalse(self.session.is_hearing_terminated)
        self.assertIn("FINAL WARNING", res3.judge_dialogue)

        # 4th Strike: HEARING TERMINATED
        res4 = self.session.submit_argument("Arbitrary irrelevant text.")
        self.assertTrue(res4.is_unwanted)
        self.assertEqual(self.session.unwanted_argument_count, 4)
        self.assertTrue(self.session.is_hearing_terminated)
        self.assertIn("hearing is hereby terminated", res4.judge_dialogue.lower())

        # Further submissions while terminated must be rejected
        res5 = self.session.submit_argument("Another argument")
        self.assertEqual(res5.category, "HEARING_TERMINATED")

    def test_restart_hearing_resets_penalties(self):
        """Restarting hearing resets strike counter and unblocks submissions."""
        # Accumulate strikes
        self.session.submit_argument("Random nonsense 1")
        self.session.submit_argument("Random nonsense 2")
        self.assertEqual(self.session.unwanted_argument_count, 2)

        # Restart
        self.session.restart_hearing()
        self.assertEqual(self.session.unwanted_argument_count, 0)
        self.assertFalse(self.session.is_hearing_terminated)

        # New valid submission works cleanly
        res = self.session.submit_argument("The fingerprints on the knife match Victor Vance.")
        self.assertFalse(res.is_unwanted)
        self.assertEqual(self.session.unwanted_argument_count, 0)

if __name__ == "__main__":
    unittest.main()
