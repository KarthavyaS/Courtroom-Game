"""Unit tests for ProgressService, SaveService, and session state persistence.
"""

import unittest
import shutil
from pathlib import Path
from services.progress_service import ProgressService
from services.save_service import SaveService
from services.tutorial_service import TutorialService
from services.game_state import GameState
from models.profile import PlayerProfile
from models.case import Case
from models.suspect import Suspect
from models.evidence import Evidence

class TestProgressAndSave(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path("tests/temp_data")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.save_service = SaveService(
            file_path=self.test_dir / "leaderboard.json",
            profile_path=self.test_dir / "profile.json",
            save_path=self.test_dir / "active_save.json"
        )

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_tutorial_service_progression(self):
        tut = TutorialService()
        self.assertEqual(tut.total_steps, 7)
        self.assertEqual(tut.current_step_index, 0)
        self.assertTrue(tut.next_step())
        self.assertEqual(tut.current_step_index, 1)
        tut.goto_step(6)
        self.assertEqual(tut.current_step_index, 6)
        self.assertFalse(tut.next_step())
        self.assertTrue(tut.prev_step())
        self.assertEqual(tut.current_step_index, 5)

    def test_progress_service_milestones(self):
        prog = ProgressService()
        self.assertEqual(prog.calculate_progress_percentage(), 0)

        prog.mark_briefing_read()
        self.assertTrue(prog.briefing_read)
        self.assertGreater(prog.calculate_progress_percentage(), 0)

        prog.record_evidence_inspected("EVD-001")
        self.assertTrue(prog.crime_scene_explored)

        prog.record_evidence_collected("EVD-001")
        self.assertTrue(prog.evidence_reviewed)

        prog.record_suspect_interview("SUS-001", "Q1", total_suspect_count=1)
        self.assertTrue(prog.suspects_reviewed)

        prog.record_case_board_opened()
        self.assertTrue(prog.case_board_reviewed)

        prog.record_argument_drafted(is_valid=True)
        self.assertTrue(prog.argument_prepared)

        prog.record_courtroom_finished()
        self.assertTrue(prog.courtroom_completed)
        self.assertEqual(prog.calculate_progress_percentage(), 100)

    def test_active_game_save_and_restore(self):
        profile = PlayerProfile(name="Sherlock Holmes")
        self.save_service.save_profile(profile)

        gs = GameState(profile=profile)
        case = Case(
            id="TEST_CASE",
            title="The Test Case",
            type="Murder",
            description="A test investigation.",
            difficulty="EASY",
            reward=100,
            suspects=[Suspect(id="SUS-1", name="Suspect One", occupation="Witness", relationship="Acquaintance", motive="", alibi="", statement="")],
            evidence_list=[Evidence(id="EVD-1", name="Test Clue", description="Clue", category="Physical", reliability=1.0, relevance=1.0, facts_unlocked=["fact_1"])]
        )
        gs.set_case(case)
        gs.collect_evidence("EVD-1")
        gs.progress.record_suspect_interview("SUS-1", "Q1", total_suspect_count=1)
        gs.progress.player_notes = "Important note about suspect."

        saved = self.save_service.save_active_game(gs)
        self.assertTrue(saved)
        self.assertTrue(self.save_service.has_active_save())

        summary = self.save_service.get_active_save_summary()
        self.assertIsNotNone(summary)
        self.assertEqual(summary["case_id"], "TEST_CASE")
        self.assertEqual(summary["collected_count"], 1)

        # Restore in a fresh game state
        gs2 = GameState()
        active_data = self.save_service.load_active_game()
        self.assertIsNotNone(active_data)
        gs2.restore_from_save(case, active_data)

        self.assertTrue(gs2.is_evidence_collected("EVD-1"))
        self.assertTrue("fact_1" in gs2.get_unlocked_facts())
        self.assertEqual(gs2.progress.player_notes, "Important note about suspect.")

        # Clear active save
        self.save_service.clear_active_save()
        self.assertFalse(self.save_service.has_active_save())

if __name__ == "__main__":
    unittest.main()
