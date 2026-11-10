import unittest
from ai_engine.knowledge_base import KnowledgeBase, Rule
from ai_engine.resolution import ResolutionEngine
from ai_engine.propositional_logic import Literal, And, Or, Not, Implies

class TestResolution(unittest.TestCase):

    def setUp(self):
        self.engine = ResolutionEngine()
        self.kb = KnowledgeBase()

    def test_resolution_proves_entailment(self):
        """Resolution refutation proves entailment (derives empty clause)."""
        # KB: P, P => Q  (equivalent to clause {~P, Q})
        self.kb.tell("p")
        self.kb.add_rule(Rule(id="R1", name="P implies Q", antecedents=["p"], consequent="q"))

        # Prove Q
        entailed, trace, clauses = self.engine.prove_by_refutation("q", self.kb)
        self.assertTrue(entailed)
        self.assertTrue(any("EMPTY CLAUSE" in line for line in trace))

    def test_resolution_rejects_unentailed_query(self):
        """Resolution rejects query not entailed by KB."""
        self.kb.tell("p")
        self.kb.add_rule(Rule(id="R1", name="R implies Q", antecedents=["r"], consequent="q"))

        entailed, trace, clauses = self.engine.prove_by_refutation("q", self.kb)
        self.assertFalse(entailed)

    def test_direct_contradiction_detection(self):
        """Resolution detects direct contradictory clauses {p} and {~p}."""
        clauses = {frozenset(["alibi_verified"]), frozenset(["~alibi_verified"])}
        has_contra, trace = self.engine.detect_contradictions(clauses)
        self.assertTrue(has_contra)
        self.assertTrue(any("Direct contradiction detected" in t for t in trace))

    def test_cnf_transformation(self):
        """Converts (A & B) and (A => B) to CNF expressions."""
        imp = Implies(Literal("p"), Literal("q"))
        cnf = imp.to_cnf()
        clauses = cnf.get_clauses()
        # Should contain one clause with ~p and q
        self.assertEqual(len(clauses), 1)
        self.assertEqual(clauses[0], {"~p", "q"})

if __name__ == "__main__":
    unittest.main()
