"""Finite differential and independent ordered-RUP controls. Apache-2.0.

All original literals here satisfy the frozen encoder's valid-literal contract.
The raw check() API does not enforce parse()'s terminal-empty requirement; the
tests deliberately preserve that distinction, including empty proof behavior.
Substantial OpenAI Codex assistance; predecessor attribution is in README.md.
"""

import hashlib
from itertools import product
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))  # Support isolated Python and an unrelated cwd.
import candidate


def reference_checker():
    path = ROOT.parent / "p111-minrank-proof-reconciliation" / "lrat.py"
    expected = json.loads((ROOT / "SOURCES.json").read_text())["files_sha256"]["lrat.py"]
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("predecessor pin: lrat.py")
    module = types.ModuleType("frozen_rup_reference")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def verdict(checker, proof, original, variables, initial_clauses):
    try:
        return True, checker(proof, original, variables, initial_clauses)
    except ValueError as error:
        return False, str(error)


def set_oracle(proof, original, variables, initial_clauses):
    """Declarative residual-clause oracle; no variable-indexed assignments.

    Each epoch is represented by a fresh set of false *literals*. A premise is
    classified by its satisfied literals and the set of its residual literals.
    This intentionally does not reproduce the checker's order of error messages.
    """
    database = dict(original)
    previous = initial_clauses
    for position, (index, clause, hints) in enumerate(proof):
        if index <= previous or index in database:
            return False
        if not all(0 < abs(lit) <= variables for lit in clause):
            return False
        previous = index
        false_literals = set(clause)
        conflict = bool(false_literals & {-lit for lit in false_literals})
        if conflict:
            if hints:
                return False
        else:
            for step, hint in enumerate(hints):
                if hint not in database or hint >= index:
                    return False
                premise = database[hint]
                if any(-lit in false_literals for lit in premise):
                    return False
                residual = set(premise) - false_literals
                if len(residual) > 1:
                    return False
                if not residual:
                    conflict = True
                    if step != len(hints) - 1:
                        return False
                    break
                false_literals.add(-next(iter(residual)))
        if not conflict or (not clause and position != len(proof) - 1):
            return False
        database[index] = clause
    return True


def models(original, variables):
    return [values for values in product((False, True), repeat=variables)
            if all(any(values[abs(lit) - 1] == (lit > 0) for lit in clause)
                   for clause in original.values())]


def run():
    reference = reference_checker()
    counts = {"exhaustive_single_addition": 0, "exhaustive_two_additions": 0,
              "targeted_controls": 0, "accepted": 0, "rejected": 0,
              "truth_table_lemma_checks": 0}
    rejection_messages = set()

    def compare(proof, original, variables, initial_clauses, group, original_models=None):
        expected = verdict(reference.check, proof, original, variables, initial_clauses)
        actual = verdict(candidate.check, proof, original, variables, initial_clauses)
        if actual != expected:
            raise AssertionError(("differential mismatch", proof, original, expected, actual))
        if set_oracle(proof, original, variables, initial_clauses) != actual[0]:
            raise AssertionError(("independent residual-set mismatch", proof, original, actual))
        counts[group] += 1
        counts["accepted" if actual[0] else "rejected"] += 1
        if not actual[0]:
            rejection_messages.add(actual[1])
            return False
        if original_models is None:
            original_models = models(original, variables)
        for _, clause, _ in proof:
            if not all(any(values[abs(lit) - 1] == (lit > 0) for lit in clause)
                       for values in original_models):
                raise AssertionError(("admitted lemma is not entailed", proof, original))
            counts["truth_table_lemma_checks"] += 1
        return True

    # Every ordered clause over two variables of width 0, 1 or 2, including
    # repeated literals and both orders of tautologies: 1 + 4 + 16 = 21.
    literals = (-2, -1, 1, 2)
    clauses = [tuple(row) for width in range(3) for row in product(literals, repeat=width)]
    hints = [tuple(row) for width in range(3) for row in product((1, 2, 3, 4), repeat=width)]
    suffix_hints = [tuple(row) for width in range(3) for row in product((1, 2, 3), repeat=width)]
    for first_root, second_root in product(clauses, repeat=2):
        original = {1: first_root, 2: second_root}
        original_models = models(original, 2)
        for clause in clauses:
            admitted_prefixes = []
            for sequence in hints:
                proof = [(3, clause, sequence)]
                admitted = compare(proof, original, 2, 2, "exhaustive_single_addition", original_models)
                if admitted and clause:
                    admitted_prefixes.append(proof)
            # For every admitted nonempty prefix in this domain, exhaust all
            # two-hint empty-clause suffixes, including reuse of the new lemma.
            # This catches state leakage even when the first lemma is tautological.
            for admitted_prefix in admitted_prefixes:
                for sequence in suffix_hints:
                    compare(admitted_prefix + [(4, (), sequence)], original, 2, 2,
                            "exhaustive_two_additions", original_models)

    explicit = [
        # A complete three-hint implication chain and its order/suffix mutants.
        ([(4, (), (1, 2, 3))], {1: (1,), 2: (-1, 2), 3: (-2,)}, 2, 3),
        ([(4, (), (2, 1, 3))], {1: (1,), 2: (-1, 2), 3: (-2,)}, 2, 3),
        ([(4, (), (1, 2, 3, 1))], {1: (1,), 2: (-1, 2), 3: (-2,)}, 2, 3),
        # A satisfiable formula must not become refutable through stale -2.
        ([(3, (2,), (1, 2)), (4, (), (2, 1))], {1: (1,), 2: (-1, 2)}, 2, 2),
        # Two opposing epochs followed by a valid fresh-epoch refutation.
        ([(3, (2,), (1, 2)), (4, (-2,), (1, 2)), (5, (), (1, 2))],
         {1: (1,), 2: (-1,)}, 2, 2),
        # Consecutive tautologies must leave no assignments in a later epoch.
        ([(2, (1, -1), ()), (3, (-1, 1), ()), (4, (), (1,))], {1: (1,)}, 1, 1),
        # Repeated root literals form one unit; opposing signs do not.
        ([(3, (), (1, 2))], {1: (1, 1, 1), 2: (-1, -1)}, 1, 2),
        ([(2, (), (1,))], {1: (1, -1, 1)}, 1, 1),
        # Diagnostic priority follows literal order when both failures exist.
        ([(3, (), (1, 2))], {1: (1,), 2: (2, -2, 1)}, 2, 2),
        ([(3, (), (1, 2))], {1: (1,), 2: (1, 2, -2)}, 2, 2),
        # Boundary IDs, an existing future ID, sparse roots, invalid new literals.
        ([(2, (), (1,))], {1: ()}, 0, 2),
        ([(3, (), (7,))], {1: (), 7: ()}, 1, 2),
        ([(8, (), (1,))], {1: ()}, 1, 7),
        ([(2, (0,), (1,))], {1: ()}, 1, 1),
        ([(2, (2,), (1,))], {1: ()}, 1, 1),
        ([(2, (), (1,)), (3, (), (1,))], {1: ()}, 0, 1),
        # Document raw-API behavior; parse() supplies the terminal-empty guard.
        ([], {}, 0, 0),
        ([(1, (1, -1), ())], {}, 1, 0),
    ]
    for case in explicit:
        compare(*case, "targeted_controls")
    counts["rejection_messages"] = sorted(rejection_messages)
    counts["root_clause_universe"] = len(clauses)
    counts["independent_oracle"] = "false-literal sets plus truth-table entailment"
    return counts


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
