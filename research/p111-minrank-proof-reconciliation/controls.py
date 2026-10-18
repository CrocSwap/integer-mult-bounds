"""Independent small-domain semantics and adversarial RUP checks. Apache-2.0."""
from itertools import combinations, product
import hashlib
import json

import encoding
import lrat


def rank2(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length()-1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def matrix_rows(bits, n):
    return [(bits >> (i*n)) & ((1 << n)-1) for i in range(n)]


def packed(matrix):
    return sum(int(value) << (i*len(matrix)+j)
               for i, row in enumerate(matrix) for j, value in enumerate(row))


def rejection(function, label):
    try:
        function()
    except (ValueError, KeyError):
        return label
    raise ValueError("negative control accepted: "+label)


def gates():
    cases = 0
    for name in ("AND", "XOR"):
        clauses = []
        f = encoding.CNF(lambda i, row: clauses.append(row))
        a, b = f.new(), f.new()
        output = getattr(f, name)(a, b)
        for x, y, z in product((False, True), repeat=3):
            assignment = {a:x, b:y, output:z}
            accepted = all(any(assignment[abs(lit)] == (lit > 0) for lit in row) for row in clauses)
            expected = z == (x and y if name == "AND" else x != y)
            encoding.need(accepted == expected, "Tseitin gate truth table")
            cases += 1
    return cases


def small_semantics():
    n = 3
    order = [2, 0, 1]  # Seed 95 modulo three rotates the labels by two.
    edges = list(combinations(order, 2))
    receipts = []
    factors_checked = 0
    candidate_matrices = 0
    for mask in range(8):
        pattern = set()
        for bit, (i, j) in enumerate(edges):
            if (mask >> bit) & 1:
                pattern |= {(i, j), (j, i)}
        free = [(i, j) for i in range(n) for j in range(n)
                if i != j and (i, j) not in pattern]
        diagonal = sum(1 << (i*n+i) for i in range(n))
        fitting = []
        for values in range(1 << len(free)):
            fitting.append(diagonal | sum(((values >> k) & 1) << (i*n+j)
                                          for k, (i, j) in enumerate(free)))
        for c in (1, 2):
            admissible = {m for m in fitting if rank2(matrix_rows(m, n)) <= c}
            candidate_matrices += len(fitting)
            baseline_bits = min(admissible) if admissible else diagonal
            baseline = [[(baseline_bits >> (i*n+j)) & 1 for j in range(n)] for i in range(n)]
            clique = next(cl for size in range(c, 0, -1)
                          if (cl := encoding.first_clique(n, pattern, size)) is not None)
            free_ports = [i for i in range(n) if i not in clique]
            models = {"none":set(), "neB0":set()}
            for values in product(range(1 << c), repeat=2*len(free_ports)):
                source, sink = [0]*n, [0]*n
                for i, port in enumerate(clique):
                    source[port] = sink[port] = 1 << i
                for i, port in enumerate(free_ports):
                    source[port], sink[port] = values[i], values[i+len(free_ports)]
                matrix = [[(sink[i] & source[j]).bit_count() % 2 for j in range(n)] for i in range(n)]
                matrix_bits = packed(matrix)
                for mode in models:
                    f = encoding.build(n, pattern, baseline, c, clique, mode,
                                       inputs=(source, sink))
                    if not f.unsatisfied:
                        models[mode].add(matrix_bits)
                    factors_checked += 1
            encoding.need(models["none"] == admissible, "small fitting/gauge equivalence")
            encoding.need(models["neB0"] == admissible-{baseline_bits}, "small disequality equivalence")
            receipts.append({"edge_mask":mask, "dimension":c, "anchor":clique,
                             "fitting_matrices":len(admissible),
                             "unequal_matrices":len(admissible-{baseline_bits}),
                             "model_set_sha256":hashlib.sha256(json.dumps(sorted(admissible)).encode()).hexdigest()})
    return {"vertices":3, "seed_order":order, "cases":receipts,
            "factor_assignments_and_modes":factors_checked,
            "direct_matrix_candidates":candidate_matrices,
            "gate_truth_cases":gates()}


def proof_controls(proof, original, variables, initial_clauses):
    labels = []
    first, rest = proof[0], proof[1:]
    index, clause, hints = first
    encoding.need(len(clause) == 1 and hints, "small proof control anchor")
    mutant = [(index, (-clause[0],), hints)]+rest
    labels.append(rejection(lambda:lrat.check(mutant,original,variables,initial_clauses), "negated learned unit"))
    mutant = [(index, clause, hints[1:])]+rest
    labels.append(rejection(lambda:lrat.check(mutant,original,variables,initial_clauses), "omitted necessary hint"))
    mutant = [(index, clause, tuple(reversed(hints)))]+rest
    labels.append(rejection(lambda:lrat.check(mutant,original,variables,initial_clauses), "reversed unit propagation"))
    mutant = [(index, clause, (index,)+hints)]+rest
    labels.append(rejection(lambda:lrat.check(mutant,original,variables,initial_clauses), "self-referential hint"))
    mutant = [(initial_clauses, clause, hints)]+rest
    labels.append(rejection(lambda:lrat.check(mutant,original,variables,initial_clauses), "reused clause identifier"))
    mutant = [(index, (variables+1,), hints)]+rest
    labels.append(rejection(lambda:lrat.check(mutant,original,variables,initial_clauses), "out-of-range proof variable"))
    omitted = dict(original)
    del omitted[hints[0]]
    labels.append(rejection(lambda:lrat.check(proof,omitted,variables,initial_clauses), "missing original premise"))
    labels.append(rejection(lambda:lrat.parse("3 0 -1 0\n"), "RAT hint outside supported subset"))
    labels.append(rejection(lambda:lrat.parse("3 1 0 1 0\n"), "missing terminal empty clause"))
    labels.append(rejection(lambda:lrat.parse("3 d 1 0\n"), "deletion record outside supported subset"))
    labels.append(rejection(lambda:lrat.check([(2,(),(1,))], {1:(1,)}, 1, 1), "false refutation of satisfiable unit"))
    labels.append(rejection(lambda:lrat.check([(2,(),(1,))], {1:(1,2)}, 2, 1), "nonunit hint"))
    labels.append(rejection(lambda:lrat.check([(2,(-1,),(1,)),(3,(),(2,))], {1:(1,)}, 1, 1), "satisfied hint"))
    labels.append(rejection(lambda:encoding.build(2,set(),[[1,0],[0,1]],2,[0,1],"none"), "nonclique gauge"))
    valid = lrat.check([(3,(),(1,2))], {1:(1,),2:(-1,)}, 1, 2)
    encoding.need(valid["empty_clause_derived"], "independent tiny positive proof")
    return {"rejected":labels, "tiny_positive_proof":valid}
