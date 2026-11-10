import unittest
from ai_engine.scoring import ScoringEngine
from ai_engine.knowledge_base import KnowledgeBase
from ai_engine.rule_engine import STANDARD_RULES
from models.argument import Argument
from models.evidence import Evidence
from models.suspect import Suspect

class TestScoring(unittest.TestCase):

    def setUp(self):
        self.engine = ScoringEngine()
        self.kb = KnowledgeBase()
        for r in STANDARD_RULES:
            self.kb.add_rule(r)

        self.knife_ev = Evidence(
            id="EVD-002",
            name="Bloody Knife",
            description="Forensic examination shows victim blood and Victor's fingerprints.",
            category="Physical",
            reliability=0.95,
            relevance=0.9,
            collected=True,
            facts_unlocked=[
                "knife_found_at_scene",
                "suspect_fingerprints_on_knife",
                "blood_on_knife_matches_victim"
            ]
        )

        self.cctv_ev = Evidence(
            id="EVD-006",
            name="CCTV Hard Drive",
            description="CCTV footage shows suspect entering at 11:50 PM.",
            category="Digital",
            reliability=0.9,
            relevance=0.85,
            collected=True,
            facts_unlocked=[
                "cctv_shows_suspect_entry",
                "suspect_present_at_mansion_at_midnight"
            ]
        )

        self.phone_ev = Evidence(
            id="EVD-005",
            name="Encrypted Mobile Phone",
            description="Threatening text messages regarding immediate inheritance.",
            category="Digital",
            reliability=0.85,
            relevance=0.8,
            collected=True,
            facts_unlocked=[
                "incriminating_phone_messages",
                "suspect_debt_or_inheritance"
            ]
        )

        self.autopsy_ev = Evidence(
            id="EVD-001",
            name="Autopsy Report",
            description="Cause of death is stab wound.",
            category="Direct",
            reliability=1.0,
            relevance=1.0,
            collected=True,
            facts_unlocked=["victim_cause_of_death_stab_wound"]
        )

        self.suspect = Suspect(
            id="SUS-001",
            name="Victor Vance",
            occupation="Heir",
            relationship="Brother",
            motive="Stood to inherit the estate upon brother's death",
            alibi="Claims he was at the cinema from 10 PM to 1 AM",
            statement="I never touched any knife and was at the cinema!",
            is_guilty=True
        )

    def test_complete_sound_argument_supported(self):
        """A complete, grounded, logically sound argument receives SUPPORTED verdict."""
        self.kb.tell("suspect_claimed_cinema_alibi")

        arg = Argument(
            suspect_id="SUS-001",
            premises=[
                "victim_cause_of_death_stab_wound",
                "knife_found_at_scene",
                "blood_on_knife_matches_victim",
                "suspect_fingerprints_on_knife",
                "cctv_shows_suspect_entry",
                "suspect_present_at_mansion_at_midnight",
                "suspect_claimed_cinema_alibi",
                "incriminating_phone_messages",
                "suspect_debt_or_inheritance"
            ],
            conclusion="suspect_guilty_beyond_reasonable_doubt",
            selected_evidence_ids=["EVD-001", "EVD-002", "EVD-005", "EVD-006"]
        )

        result = self.engine.evaluate_argument(
            arg, self.kb, [self.autopsy_ev, self.knife_ev, self.cctv_ev, self.phone_ev], self.suspect
        )

        self.assertEqual(result["verdict"], "SUPPORTED")
        self.assertGreaterEqual(result["total_score"], 70)
        self.assertTrue(result["is_proven"])

    def test_motive_alone_safeguard(self):
        """Motive alone does NOT establish guilt beyond reasonable doubt."""
        arg = Argument(
            suspect_id="SUS-001",
            premises=["suspect_has_proven_motive"],
            conclusion="suspect_guilty_beyond_reasonable_doubt",
            selected_evidence_ids=["EVD-005"]
        )

        result = self.engine.evaluate_argument(
            arg, self.kb, [self.phone_ev], self.suspect
        )

        self.assertNotEqual(result["verdict"], "SUPPORTED")
        self.assertLess(result["total_score"], 50)
        self.assertTrue(any("Motive Is Not Guilt" in v for v in result["violations"]))

    def test_fingerprints_alone_safeguard(self):
        """Fingerprints on weapon do NOT independently establish murder guilt."""
        arg = Argument(
            suspect_id="SUS-001",
            premises=["suspect_fingerprints_on_knife", "knife_found_at_scene"],
            conclusion="suspect_guilty_beyond_reasonable_doubt",
            selected_evidence_ids=["EVD-002"]
        )

        result = self.engine.evaluate_argument(
            arg, self.kb, [self.knife_ev], self.suspect
        )

        self.assertNotEqual(result["verdict"], "SUPPORTED")
        self.assertTrue(any("Contact Is Not Homicide" in v for v in result["violations"]))

    def test_unsupported_argument_low_score(self):
        """Unsupported claims receive a low logical score."""
        arg = Argument(
            suspect_id="SUS-001",
            premises=["unrelated_rumor"],
            conclusion="suspect_guilty_beyond_reasonable_doubt",
            selected_evidence_ids=[]
        )

        result = self.engine.evaluate_argument(
            arg, self.kb, [], self.suspect
        )

        self.assertFalse(result["is_proven"])
        self.assertEqual(result["verdict"], "NOT PROVEN")
        self.assertLess(result["total_score"], 30)

if __name__ == "__main__":
    unittest.main()
