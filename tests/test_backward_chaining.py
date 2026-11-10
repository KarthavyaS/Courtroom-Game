import unittest
from ai_engine.knowledge_base import KnowledgeBase, Rule
from ai_engine.backward_chaining import BackwardChainingEngine

class TestBackwardChaining(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()
        self.engine = BackwardChainingEngine(self.kb)

    def test_verify_supported_target(self):
        """Backward chaining successfully verifies a supported target."""
        self.kb.tell("knife_found_at_scene")
        self.kb.tell("suspect_fingerprints_on_knife")
        self.kb.add_rule(Rule(
            id="R1",
            name="Contact with Weapon",
            antecedents=["knife_found_at_scene", "suspect_fingerprints_on_knife"],
            consequent="suspect_had_contact_with_knife"
        ))

        proven, trace, tree = self.engine.prove("suspect_had_contact_with_knife", self.kb)
        self.assertTrue(proven)
        self.assertEqual(tree["proven"], True)

    def test_reject_unsupported_target(self):
        """Backward chaining rejects an unsupported target."""
        self.kb.tell("knife_found_at_scene")
        # Missing suspect fingerprints
        self.kb.add_rule(Rule(
            id="R1",
            name="Contact with Weapon",
            antecedents=["knife_found_at_scene", "suspect_fingerprints_on_knife"],
            consequent="suspect_had_contact_with_knife"
        ))

        proven, trace, tree = self.engine.prove("suspect_had_contact_with_knife", self.kb)
        self.assertFalse(proven)
        self.assertEqual(tree["proven"], False)

    def test_direct_fact_in_kb(self):
        """Direct fact in KB is proven immediately."""
        self.kb.tell("suspect_present_at_scene")
        proven, trace, tree = self.engine.prove("suspect_present_at_scene", self.kb)
        self.assertTrue(proven)
        self.assertEqual(tree["source"], "base_fact")

    def test_cycle_handling(self):
        """Cyclic rules (A->B, B->A) do not cause infinite recursion."""
        self.kb.add_rule(Rule(id="R1", name="A to B", antecedents=["a"], consequent="b"))
        self.kb.add_rule(Rule(id="R2", name="B to A", antecedents=["b"], consequent="a"))

        proven, trace, tree = self.engine.prove("b", self.kb)
        self.assertFalse(proven)

if __name__ == "__main__":
    unittest.main()
