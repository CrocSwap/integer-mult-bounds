"""Signed-epoch implementation of PR1097's ordered RUP checker.

Apache-2.0. Adapted from Gareth Davidson / bitplane's lrat.check in PR1097
with substantial OpenAI Codex assistance. See NOTICE.md.

The parser and authenticated formula generator retain responsibility for the
input contract: a nonempty, terminal-empty proof, and valid original literals.
This is an opt-in storage optimization, not a broader LRAT implementation.
"""


def check(proof, original, variables, initial_clauses):
    database = dict(original)
    previous = initial_clauses
    used_hints = 0
    maximum_width = 0
    # A variable has a value in this lemma only when its stamp is +/-epoch.
    # Python integers do not wrap; a new lemma cannot see a stale assignment.
    assignment = [0] * (variables + 1)
    for position, (index, clause, hints) in enumerate(proof):
        if not (index > previous and index not in database):
            raise ValueError("nonmonotone or reused clause ID")
        if not all(0 < abs(lit) <= variables for lit in clause):
            raise ValueError("proof literal outside formula")
        previous = index
        epoch = position + 1
        negative_epoch = -epoch
        conflict = False
        for lit in clause:
            var = abs(lit)
            value = epoch if lit < 0 else negative_epoch
            if assignment[var] == -value:
                conflict = True
            assignment[var] = value
        if conflict:
            if hints:
                raise ValueError("tautological addition must not hide unused hints")
        else:
            for step, hint in enumerate(hints):
                if not (hint in database and hint < index):
                    raise ValueError("missing or forward proof hint")
                unit = None
                for lit in database[hint]:
                    var = abs(lit)
                    true_stamp = epoch if lit > 0 else negative_epoch
                    stamp = assignment[var]
                    if stamp == true_stamp:
                        raise ValueError("hint already satisfied")
                    if stamp != -true_stamp:
                        if unit is not None and unit != lit:
                            raise ValueError("hint is not unit or conflicting")
                        unit = lit
                used_hints += 1
                if unit is None:
                    conflict = True
                    if step != len(hints) - 1:
                        raise ValueError("unused hints after conflict")
                    break
                assignment[abs(unit)] = epoch if unit > 0 else negative_epoch
        if not conflict:
            raise ValueError("RUP deduction does not reach conflict")
        if not clause and position != len(proof) - 1:
            raise ValueError("empty clause before end")
        database[index] = clause
        maximum_width = max(maximum_width, len(clause))
    return {"additions": len(proof), "hints_checked": used_hints,
            "root_clauses_used": len(original), "maximum_lemma_width": maximum_width,
            "final_clause": previous, "empty_clause_derived": True}
