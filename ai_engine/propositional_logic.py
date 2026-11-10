"""Propositional Logic AST and CNF Resolution Utilities for LOGIC COURTROOM.
Implements representations for Propositional Logic expressions, evaluation,
truth assignment satisfaction, and CNF (Conjunctive Normal Form) transformation.
"""

from typing import Set, Dict, List, Tuple, Union, Optional, Any

class Expr:
    """Base class for all Propositional Logic Expressions."""
    def evaluate(self, model: Dict[str, bool]) -> bool:
        raise NotImplementedError

    def symbols(self) -> Set[str]:
        raise NotImplementedError

    def to_cnf(self) -> "Expr":
        """Convert expression to Conjunctive Normal Form (CNF)."""
        # Step 1: Eliminate implications and equivalences
        elim = self.eliminate_implications()
        # Step 2: Push negations inward (De Morgan's laws)
        nnf = elim.push_not_inward()
        # Step 3: Distribute OR over AND
        cnf = nnf.distribute_or_over_and()
        return cnf

    def eliminate_implications(self) -> "Expr":
        return self

    def push_not_inward(self) -> "Expr":
        return self

    def distribute_or_over_and(self) -> "Expr":
        return self

    def get_clauses(self) -> List[Set[str]]:
        """Extract a list of clauses (sets of literals like {'P', '~Q'})."""
        cnf = self.to_cnf()
        return cnf._extract_clauses()

    def _extract_clauses(self) -> List[Set[str]]:
        raise NotImplementedError

    def __repr__(self) -> str:
        return str(self)


class Literal(Expr):
    """Represents a propositional variable or its negation."""
    def __init__(self, name: str, is_negated: bool = False):
        self.name = name.strip().lower()
        self.is_negated = is_negated

    def evaluate(self, model: Dict[str, bool]) -> bool:
        val = model.get(self.name, False)
        return not val if self.is_negated else val

    def symbols(self) -> Set[str]:
        return {self.name}

    def eliminate_implications(self) -> "Expr":
        return self

    def push_not_inward(self) -> "Expr":
        return self

    def distribute_or_over_and(self) -> "Expr":
        return self

    def _extract_clauses(self) -> List[Set[str]]:
        literal_str = f"~{self.name}" if self.is_negated else self.name
        return [{literal_str}]

    def __str__(self) -> str:
        return f"~{self.name}" if self.is_negated else self.name

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Literal) and self.name == other.name and self.is_negated == other.is_negated

    def __hash__(self) -> int:
        return hash((self.name, self.is_negated))


class Not(Expr):
    """Negation of an expression (~A)."""
    def __init__(self, operand: Expr):
        self.operand = operand

    def evaluate(self, model: Dict[str, bool]) -> bool:
        return not self.operand.evaluate(model)

    def symbols(self) -> Set[str]:
        return self.operand.symbols()

    def eliminate_implications(self) -> "Expr":
        return Not(self.operand.eliminate_implications())

    def push_not_inward(self) -> "Expr":
        if isinstance(self.operand, Literal):
            return Literal(self.operand.name, not self.operand.is_negated)
        elif isinstance(self.operand, Not):
            return self.operand.operand.push_not_inward()
        elif isinstance(self.operand, And):
            # ~(A & B) <=> (~A | ~B)
            return Or([Not(arg).push_not_inward() for arg in self.operand.args]).push_not_inward()
        elif isinstance(self.operand, Or):
            # ~(A | B) <=> (~A & ~B)
            return And([Not(arg).push_not_inward() for arg in self.operand.args]).push_not_inward()
        return self

    def distribute_or_over_and(self) -> "Expr":
        return self

    def _extract_clauses(self) -> List[Set[str]]:
        if isinstance(self.operand, Literal):
            lit_str = self.operand.name if self.operand.is_negated else f"~{self.operand.name}"
            return [{lit_str}]
        raise ValueError("Cannot extract clauses from unsimplified NOT")

    def __str__(self) -> str:
        return f"~({self.operand})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self) -> int:
        return hash(("not", self.operand))


class And(Expr):
    """Conjunction of expressions (A & B & ...)."""
    def __init__(self, args: List[Expr]):
        self.args = args

    def evaluate(self, model: Dict[str, bool]) -> bool:
        return all(arg.evaluate(model) for arg in self.args)

    def symbols(self) -> Set[str]:
        res = set()
        for a in self.args:
            res.update(a.symbols())
        return res

    def eliminate_implications(self) -> "Expr":
        return And([arg.eliminate_implications() for arg in self.args])

    def push_not_inward(self) -> "Expr":
        return And([arg.push_not_inward() for arg in self.args])

    def distribute_or_over_and(self) -> "Expr":
        return And([arg.distribute_or_over_and() for arg in self.args])

    def _extract_clauses(self) -> List[Set[str]]:
        clauses = []
        for arg in self.args:
            clauses.extend(arg._extract_clauses())
        return clauses

    def __str__(self) -> str:
        return f"({' & '.join(str(a) for a in self.args)})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, And) and self.args == other.args

    def __hash__(self) -> int:
        return hash(("and", tuple(self.args)))


class Or(Expr):
    """Disjunction of expressions (A | B | ...)."""
    def __init__(self, args: List[Expr]):
        self.args = args

    def evaluate(self, model: Dict[str, bool]) -> bool:
        return any(arg.evaluate(model) for arg in self.args)

    def symbols(self) -> Set[str]:
        res = set()
        for a in self.args:
            res.update(a.symbols())
        return res

    def eliminate_implications(self) -> "Expr":
        return Or([arg.eliminate_implications() for arg in self.args])

    def push_not_inward(self) -> "Expr":
        return Or([arg.push_not_inward() for arg in self.args])

    def distribute_or_over_and(self) -> "Expr":
        # Recursively distribute children
        new_args = [arg.distribute_or_over_and() for arg in self.args]
        if not new_args:
            return Or([])
        if len(new_args) == 1:
            return new_args[0]

        # Combine two at a time: (A | B)
        result = new_args[0]
        for next_expr in new_args[1:]:
            result = self._distribute_pair(result, next_expr)
        return result

    def _distribute_pair(self, expr1: Expr, expr2: Expr) -> Expr:
        if isinstance(expr1, And):
            return And([self._distribute_pair(c, expr2) for c in expr1.args])
        if isinstance(expr2, And):
            return And([self._distribute_pair(expr1, c) for c in expr2.args])
        return Or([expr1, expr2])

    def _extract_clauses(self) -> List[Set[str]]:
        single_clause = set()
        for arg in self.args:
            if isinstance(arg, Literal):
                lit_str = f"~{arg.name}" if arg.is_negated else arg.name
                single_clause.add(lit_str)
            elif isinstance(arg, Or):
                for sub in arg.args:
                    if isinstance(sub, Literal):
                        lit_str = f"~{sub.name}" if sub.is_negated else sub.name
                        single_clause.add(lit_str)
            elif isinstance(arg, Not) and isinstance(arg.operand, Literal):
                lit_str = arg.operand.name if arg.operand.is_negated else f"~{arg.operand.name}"
                single_clause.add(lit_str)
            else:
                for sub_clause in arg._extract_clauses():
                    single_clause.update(sub_clause)
        return [single_clause]

    def __str__(self) -> str:
        return f"({' | '.join(str(a) for a in self.args)})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Or) and self.args == other.args

    def __hash__(self) -> int:
        return hash(("or", tuple(self.args)))


class Implies(Expr):
    """Implication expression (Premise => Consequent)."""
    def __init__(self, premise: Expr, consequent: Expr):
        self.premise = premise
        self.consequent = consequent

    def evaluate(self, model: Dict[str, bool]) -> bool:
        return not self.premise.evaluate(model) or self.consequent.evaluate(model)

    def symbols(self) -> Set[str]:
        return self.premise.symbols().union(self.consequent.symbols())

    def eliminate_implications(self) -> "Expr":
        # A => B <=> ~A | B
        return Or([Not(self.premise.eliminate_implications()), self.consequent.eliminate_implications()])

    def __str__(self) -> str:
        return f"({self.premise} => {self.consequent})"


def parse_literal(lit: str) -> Tuple[str, bool]:
    """Parses a string literal such as '~knife_found' or 'knife_found' into (name, is_negated)."""
    lit = lit.strip()
    if lit.startswith("~") or lit.startswith("!") or lit.startswith("not "):
        name = lit.lstrip("~!").removeprefix("not ").strip().lower()
        return name, True
    return lit.lower(), False


def make_expr(symbol_or_expr: Union[str, Expr]) -> Expr:
    """Convenience factory creating a Literal from a string or returning existing Expr."""
    if isinstance(symbol_or_expr, Expr):
        return symbol_or_expr
    name, is_neg = parse_literal(symbol_or_expr)
    return Literal(name, is_neg)
