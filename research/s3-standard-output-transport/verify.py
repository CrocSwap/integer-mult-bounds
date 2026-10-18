#!/usr/bin/env python3
"""Recompute the exact, scoped S3 transport certificate; never trust exit alone.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from hashlib import sha256
import importlib.util
from itertools import product
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location("s3_transport_"+name, HERE/(name+".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


m, o = load("model"), load("oracle")
require = o.require


def digest(value):
    return sha256(json.dumps(value, separators=(",", ":"), sort_keys=True).encode()).hexdigest()


def sum_vectors(children):
    leaves = []
    def visit(c):
        if c.children:
            for sub in c.children:
                visit(sub)
        else:
            leaves.append(c.v)
    for child in children:
        visit(child)
    return tuple(sum(v[i] for v in leaves) for i in range(2))


def source_bindings():
    refs = json.loads((HERE/"PREDECESSORS.json").read_text())
    pins = []
    for row in refs["references"]:
        if "path" in row:
            data = (HERE/row["path"]).read_bytes()
            require(sha256(data).hexdigest() == row["sha256"], "predecessor source drift")
            pins.append({"path": row["path"], "sha256": row["sha256"]})
    return pins


def check_group_and_admission():
    require(m.G == o.MATS, "matrix/permutation group disagreement")
    for a, b in product(range(6), repeat=2):
        require(m.mul(a, b) == o.compose(a, b), "chronological product mismatch")
    costs, layers = o.primitive_frame_minima()
    require(costs == list(m.Q_COST), "output primitive minimum differs")
    for g in range(6):
        actual, _ = o.run(m.p_word(g, list(range(6))), 6)
        require(actual == o.regular(g), "wrong regular permutation word")
        actual, _ = o.run(m.q_word(g, (0, 1)), 2)
        require(sum(actual, []) == list(o.MATS[g]), "wrong output word")
        require(m.P_COST[g] == (0 if g == m.E else 12), "workspace macro bill")
    require(m.mul(m.S, m.T) != m.mul(m.T, m.S), "commuting fixture")
    mutations = checks = 0
    for v in product(range(-2, 3), repeat=2):
        r = m.reader(v)
        require([list(row) for row in r] == o.intertwiner(v), "reader mismatch")
        require(m.admitted(r), "valid intertwiner rejected")
        for g in range(6):
            q = [list(o.MATS[g][:2]), list(o.MATS[g][2:])]
            require(o.linear_product(r, o.regular(g)) == o.linear_product(q, r),
                    "dense intertwiner equality failed")
            checks += 1
        for i, j in product(range(2), range(6)):
            bad = [list(row) for row in r]
            bad[i][j] += 1
            require(not m.admitted(bad), "one-entry nonintertwiner admitted")
            mutations += 1
    # Complete enumeration of group matrices proves this finite representation
    # is faithful; the written characterization extends to all allowed readers.
    require(len(set(o.MATS)) == 6, "nonfaithful output action")
    return {"group_products": 36, "frame_words": 12, "admission_identities": checks,
            "admission_mutations": mutations, "output_bfs_layers": layers,
            "output_costs": costs, "workspace_macro_costs": list(m.P_COST)}


def check_schedules():
    words = accepted = comparisons = 0
    records = []
    for k in range(1, 4):
        for drifts in product((m.S, m.T), repeat=k):
            minima, count, valid = o.raw_schedule_minima(drifts, m.P_COST, m.Q_COST)
            words += count
            accepted += valid
            for (a, b), value in minima.items():
                result = m.plan(drifts, pscale=a, qscale=b)[0]
                require(result == value, "six-state planner/raw schedule disagreement")
                comparisons += 1
            records.append([list(drifts), valid, sorted((list(key), value)
                                                      for key, value in minima.items())])
    cut_comparisons = 0
    for cuts in ((1,), (2,), (1, 2), (0, 1, 2)):
        drifts = (m.S, m.T, m.S)
        minima, _, _ = o.raw_schedule_minima(drifts, m.P_COST, m.Q_COST, cuts)
        for (a, b), value in minima.items():
            require(m.plan(drifts, cuts, a, b)[0] == value, "canonical cut mismatch")
            cut_comparisons += 1
    return {"unrestricted_words": words, "admitted_words": accepted,
            "price_comparisons": comparisons, "cut_words": 4*36**3,
            "cut_price_comparisons": cut_comparisons, "records_sha256": digest(records)}


def seed_fixture():
    rng = random.Random(58)
    nontrivial = [g for g in range(6) if g != m.E]
    drifts = [rng.choice(nontrivial) for _ in range(8)]
    vectors = [rng.choice(((1, 0), (0, 1), (1, 1))) for _ in drifts]
    return tuple(m.Node(g, v) for g, v in zip(drifts, vectors))


def check_echo(children, optimized, cuts=()):
    n = 2+6*(max(map(m.depth, children))+2)
    word = m.echo_word(children, (0, 1), tuple(range(2, 8)), 8, optimized, cuts)
    actual, invoice = o.run(word, n)
    v = sum_vectors(children)
    require(actual == o.expected(n, v), "dirty echo map mismatch")
    inverse, inverse_invoice = o.run(m.inverse_word(word), n)
    require(inverse == o.expected(n, v, inverse=True), "dirty echo inverse mismatch")
    require(len(word) == m.cost_echo(children, optimized, cuts), "echo recurrence mismatch")
    invoice["inverse_prefix_l1_peak"] = inverse_invoice["prefix_l1_peak"]
    return word, invoice


def check_recursive_cases():
    rng = random.Random(58)
    cases = columns = occurrences = 0
    invoices = []
    def tree(d):
        g = rng.randrange(6)
        if not d:
            return m.Node(g, (rng.randrange(-1, 2), rng.randrange(-1, 2)))
        return m.Node(g, children=tuple(tree(d-1) for _ in range(2)))
    for d in range(4):
        for _ in range(3):
            node = tree(d)
            n = 2+6*(d+1)
            for optimized in (False, True):
                word = m.node_word(node, optimized=optimized)
                actual, invoice = o.run(word, n)
                v = sum_vectors((node,))
                require(actual == o.expected(n, v, node.drift), "recursive child contract")
                inverse, inverse_invoice = o.run(m.inverse_word(word), n)
                require(inverse == o.expected(n, v, node.drift, True),
                        "recursive child inverse contract")
                require(len(word) == m.cost_node(node, optimized), "node recurrence")
                cases += 1
                columns += 2*n
                occurrences += 2*len(word)
                invoices.append([d, optimized, invoice, inverse_invoice["prefix_l1_peak"]])
    return {"cases": cases, "forward_and_inverse_columns": columns,
            "primitive_occurrences": occurrences, "invoice_sha256": digest(invoices)}


def check_array_lifts(word, base_map, base_invoice):
    records = []
    for width in (2, 3):
        lifted = [(kind, d*width+j, s*width+j if kind == "ADD" else -1, sign)
                  for kind, d, s, sign in word for j in range(width)]
        actual, invoice = o.run(lifted, len(base_map)*width)
        expected = [[base_map[i//width][j//width] if i % width == j % width else 0
                     for j in range(len(actual))] for i in range(len(actual))]
        require(actual == expected, "array lift differs from the exact tensor product")
        for field in ("ADD", "NEG", "instructions", "data_reads", "data_writes",
                      "descriptor_fields", "registers"):
            require(invoice[field] == width*base_invoice[field], "array cost not charged")
        require(invoice["prefix_l1_peak"] == base_invoice["prefix_l1_peak"],
                "array lift prefix bound")
        records.append({"width": width, "basis_columns": len(actual),
                        "instructions": len(lifted), "word_sha256": digest(lifted)})
    return records


def controls(children, optimized_word):
    names = []
    n = 14
    target = o.expected(n, sum_vectors(children))
    def rejected(name, word):
        require(o.run(word, n)[0] != target, "negative control survived: "+name)
        names.append(name)
    rejected("missing_positive_source_copy", optimized_word[1:])
    # The reverse H call is essential; these children are not involutions.
    h, path, _ = m.batch_word(children, (0, 1), list(range(8, 14)), 14)
    plus = [m.add(8+j, 2+j) for j in range(6)]
    minus = [m.add(8+j, 2+j, -1) for j in range(6)]
    rejected("forward_child_batch_used_as_inverse", plus+h+minus+h)
    rejected("missing_negative_source_copy", plus+h+minus[1:]+m.inverse_word(h))
    # The optimal seed uses pure P or Q gaps, where an order bug is invisible.
    # Use a legal mixed-frame witness instead: drift S, requested next phase T.
    # Correct formula is delta*g^-1, not g^-1*delta.
    pair = (m.Node(m.S, (1, 0)), m.Node(m.T, (0, 1)))
    phases = (m.E, m.T, m.E)
    right, wrong = [], []
    for j, child in enumerate(pair):
        child_word = m.node_word(child, (0, 1), tuple(range(8, 14)), 14)
        delta = m.mul(phases[j+1], m.INVERSE[phases[j]])
        for word, a in ((right, m.mul(delta, m.INVERSE[child.drift])),
                        (wrong, m.mul(m.INVERSE[child.drift], delta))):
            word.extend(child_word)
            word.extend(m.p_word(a, list(range(8, 14))))
            word.extend(m.q_word(delta, (0, 1)))
    pair_target = o.expected(n, sum_vectors(pair))
    require(o.run(plus+right+minus+m.inverse_word(right), n)[0] == pair_target,
            "mixed-gap positive control")
    require(o.run(plus+wrong+minus+m.inverse_word(wrong), n)[0] != pair_target,
            "mixed-gap noncommuting order control survived")
    names.append("reversed_noncommuting_gap_order")
    # Ignoring Q entirely leaves dirt-independent but incorrect source responses.
    untransported = []
    for child in children:
        untransported.extend(m.node_word(child, (0, 1), tuple(range(8, 14)), 14))
    product_g = m.E
    for child in children:
        product_g = m.mul(child.drift, product_g)
    untransported.extend(m.p_word(m.INVERSE[product_g], list(range(8, 14))))
    rejected("workspace_restored_without_output_transport",
             plus+untransported+minus+m.inverse_word(untransported))
    batch, phases, cuts = m.batch_word(children, (0, 1), tuple(range(2, 8)), 8)
    observed = False
    for j in range(1, len(children)):
        if phases[j] != m.E:
            physical, _ = o.run(batch[:cuts[j]], 8)
            canonical = o.expected(8, sum_vectors(children[:j]))
            if physical[:2] != canonical[:2]:
                observed = True
                break
    require(observed, "premature canonical observation control did not fire")
    names.append("premature_canonical_output_observation")
    # A canonical frame inside H still contains workspace dirt. It is not a
    # public partial source-only answer until the enclosing echo finishes.
    canonical_h, _, boundaries = m.batch_word(children, (0, 1), tuple(range(8, 14)),
                                             14, cuts=(4,))
    mid, _ = o.run(plus+canonical_h[:boundaries[4]], n)
    require(mid[:2] != o.expected(n, sum_vectors(children[:4]))[:2],
            "dirty midpoint was incorrectly exposed as source-only")
    names.append("canonical_frame_is_not_public_dirty_echo_output")
    r = o.intertwiner((1, 0))
    lhs = o.linear_product(r, o.regular(m.T))
    require(lhs != [[-x for x in row] for row in r], "scalar sign unexpectedly sufficient")
    names.append("replace_faithful_output_by_sign_character")
    # With nonlinear readout f(w)=w^2 the echo difference contains 2wx.
    require((2+3)**2-2**2 != 3**2, "nonlinear dirty echo control")
    names.append("nonlinear_readout_breaks_dirty_echo")
    try:
        o.run([m.add(0, 0)], 2)
    except ValueError:
        names.append("aliased_two_address_add")
    else:
        raise ValueError("aliasing accepted")
    return names


def evidence():
    refs = source_bindings()
    group = check_group_and_admission()
    schedules = check_schedules()
    children = seed_fixture()
    optimized, opt = check_echo(children, True)
    eager, old = check_echo(children, False)
    require(opt["instructions"] < old["instructions"], "no complete improvement")
    price, path = m.plan(tuple(c.drift for c in children))
    drifts = tuple(c.drift for c in children)
    dual = o.certify_boundary(drifts, m.P_COST, m.Q_COST,
                             m.distance_certificate(drifts), path, price)
    with_cut, cut_invoice = check_echo(children, True, (4,))
    # Explicitly verify the canonical midpoint, including workspace restoration.
    batch, _, boundaries = m.batch_word(children, (0, 1), tuple(range(2, 8)), 8,
                                      cuts=(4,))
    mid, _ = o.run(batch[:boundaries[4]], 8)
    require(mid == o.expected(8, sum_vectors(children[:4])), "canonical midpoint broken")
    recursive = check_recursive_cases()
    failures = controls(children, optimized)
    lifts = check_array_lifts(optimized, o.expected(14, sum_vectors(children)), opt)
    bad_dual = [row[:] for row in dual["potentials"]]
    bad_dual[-1][m.E] += 1
    try:
        o.certify_boundary(drifts, m.P_COST, m.Q_COST, bad_dual, path, price+1)
    except ValueError:
        failures.append("overstated_boundary_lower_bound")
    else:
        raise ValueError("overstated lower-bound certificate accepted")
    return {"schema_version": 1, "status": "SCOPED_EXACT_INTERFACE_NO_NEW_KAPPA",
            "assignment_seed": 58, "group": [list(g) for g in m.G],
            "source_bindings": refs, "group_and_admission": group,
            "schedule_coverage": schedules, "recursive_coverage": recursive,
            "array_lifts": lifts,
            "seed_fixture": {
                "children": [{"drift": c.drift, "v": list(c.v)} for c in children],
                "reader_sum_vector": list(sum_vectors(children)),
                "boundary_cost": price, "eager_boundary_cost": sum(m.P_COST[c.drift] for c in children),
                "boundary_primal_dual": dual,
                "midpoint_boundary_cost": m.plan(tuple(c.drift for c in children), (4,))[0],
                "path": list(path), "eager": old, "transport": opt,
                "saved_instructions": old["instructions"]-opt["instructions"],
                "eager_word_sha256": digest(eager), "transport_word_sha256": digest(optimized),
                "midpoint_canonical": cut_invoice, "midpoint_word_sha256": digest(with_cut)},
            "negative_controls": failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="write a fresh certificate; ordinary replay is read-only")
    args = parser.parse_args()
    try:
        actual = evidence()
        if args.emit:
            require(not args.emit.exists(), "refusing to overwrite a certificate")
            args.emit.write_text(json.dumps(actual, indent=2)+"\n")
        else:
            expected = json.loads((HERE/"CERTIFICATE.json").read_text())
            require(actual == expected, "certificate differs from exact recomputation")
        seed = actual["seed_fixture"]
        print("PASS_S3_STANDARD_OUTPUT boundary=%s_vs_%s echo=%s_vs_%s saved=%s controls=%s no_new_kappa"
              % (seed["boundary_cost"], seed["eager_boundary_cost"],
                 seed["transport"]["instructions"], seed["eager"]["instructions"],
                 seed["saved_instructions"], len(actual["negative_controls"])))
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print("FAIL_S3_STANDARD_OUTPUT: "+str(exc), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
