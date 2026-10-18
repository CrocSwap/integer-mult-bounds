"""Small ordered RUP checker for the positive-hint subset of LRAT.

No SAT solver, native checker or encoding implementation is imported.
Deletion-free RUP proofs are sufficient for both committed certificates.
New files Apache-2.0; substantial OpenAI Codex assistance; see NOTICE.md.
"""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parse(text):
    proof = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            fields = list(map(int, line.split()))
        except ValueError as error:
            raise ValueError("only deletion-free integer LRAT records are accepted") from error
        need(len(fields) >= 3 and fields[-1] == 0, "LRAT terminator")
        cut = fields.index(0)
        need(cut >= 1 and 0 not in fields[cut+1:-1], "LRAT field layout")
        index, clause, hints = fields[0], tuple(fields[1:cut]), tuple(fields[cut+1:-1])
        need(index > 0 and all(h > 0 for h in hints), "RAT or nonpositive hint unsupported")
        need(len(set(clause)) == len(clause), "duplicate clause literal")
        proof.append((index, clause, hints))
    need(proof and proof[-1][1] == (), "proof must end with the empty clause")
    return proof


def root_references(proof, initial_clauses):
    return {hint for _, _, hints in proof for hint in hints if hint <= initial_clauses}


def check(proof, original, variables, initial_clauses):
    database = dict(original)
    previous = initial_clauses
    used_hints = 0
    maximum_width = 0
    for position, (index, clause, hints) in enumerate(proof):
        need(index > previous and index not in database, "nonmonotone or reused clause ID")
        need(all(0 < abs(lit) <= variables for lit in clause), "proof literal outside formula")
        previous = index
        assignment = {}
        conflict = False
        for lit in clause:
            var, value = abs(lit), lit < 0  # Falsify the proposed clause.
            if var in assignment and assignment[var] != value:
                conflict = True
            assignment[var] = value
        if conflict:
            need(not hints, "tautological addition must not hide unused hints")
        else:
            for step, hint in enumerate(hints):
                need(hint in database and hint < index, "missing or forward proof hint")
                unit = None
                for lit in database[hint]:
                    var = abs(lit)
                    if var in assignment:
                        need(assignment[var] != (lit > 0), "hint already satisfied")
                    else:
                        need(unit is None or unit == lit, "hint is not unit or conflicting")
                        unit = lit
                used_hints += 1
                if unit is None:
                    conflict = True
                    need(step == len(hints)-1, "unused hints after conflict")
                    break
                assignment[abs(unit)] = unit > 0
        need(conflict, "RUP deduction does not reach conflict")
        need(clause or position == len(proof)-1, "empty clause before end")
        database[index] = clause
        maximum_width = max(maximum_width, len(clause))
    return {"additions": len(proof), "hints_checked": used_hints,
            "root_clauses_used": len(original), "maximum_lemma_width": maximum_width,
            "final_clause": previous, "empty_clause_derived": True}
