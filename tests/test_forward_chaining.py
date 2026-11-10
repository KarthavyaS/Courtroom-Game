import unittest
from ai_engine.knowledge_base import KnowledgeBase, Rule
from ai_engine.forward_chaining import ForwardChainingEngine

class TestForwardChaining(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()
        self.engine = ForwardChainingEngine(self.kb)

    def test_single_rule_derivation(self):
        """A valid rule derives a new fact through forward chaining."""
        self.kb.tell("knife_found_at_scene")
        self.kb.tell("suspect_fingerprints_on_knife")
        self.kb.add_rule(Rule(
            id="R1",
            name="Contact with Weapon",
            antecedents=["knife_found_at_scene", "suspect_fingerprints_on_knife"],
            consequent="suspect_had_contact_with_knife"
        ))

        derived, trace = self.engine.run(self.kb)
        self.assertIn("suspect_had_contact_with_knife", derived)
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace[0].rule_id, "R1")

    def test_multi_step_chaining(self):
        """Chained rules A -> B and B -> C derive C."""
        self.kb.tell("a")
        self.kb.add_rule(Rule(id="R1", name="A to B", antecedents=["a"], consequent="b"))
        self.kb.add_rule(Rule(id="R2", name="B to C", antecedents=["b"], consequent="c"))

        derived, trace = self.engine.run(self.kb)
        self.assertIn("b", derived)
        self.assertIn("c", derived)
        self.assertEqual(len(trace), 2)

    def test_unmet_antecedents_do_not_fire(self):
        """Rule does not fire if one antecedent is missing."""
        self.kb.tell("knife_found_at_scene")
        # Missing fingerprints
        self.kb.add_rule(Rule(
            id="R1",
            name="Contact with Weapon",
            antecedents=["knife_found_at_scene", "suspect_fingerprints_on_knife"],
            consequent="suspect_had_contact_with_knife"
        ))

        derived, trace = self.engine.run(self.kb)
        self.assertNotIn("suspect_had_contact_with_knife", derived)
        self.assertEqual(len(trace), 0)

    def test_fingerprints_alone_do_not_derive_murder(self):
        """Safeguard: Fingerprints alone do not establish murder."""
        self.kb.tell("suspect_fingerprints_on_knife")
        self.kb.add_rule(Rule(
            id="R_LETHAL",
            name="Murder Conviction",
            antecedents=["knife_is_murder_weapon", "suspect_had_contact_with_knife", "suspect_had_opportunity"],
            consequent="suspect_guilty_of_murder"
        ))

        derived, _ = self.engine.run(self.kb)
        self.assertNotIn("suspect_guilty_of_murder", derived)

if __name__ == "__main__":
    unittest.main()
