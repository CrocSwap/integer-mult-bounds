#!/usr/bin/env python3
"""Replay the finite census, independent oracles, source audit and controls.

Default is read-only. --write explicitly publishes a deterministic receipt.
No predecessor search or solver is run; only its two canonicalizers are loaded.
"""
import argparse
import ast
import hashlib
import itertools
import json
from pathlib import Path
import random

import census as c

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def record(pairs, z):
    return {"pairs": pairs, "Z": [e for i, e in enumerate(c.ARCS) if z & (1 << i)]}


def encode(pairs, edges):
    return tuple(map(tuple, pairs)), sum(1 << c.ARC_INDEX[tuple(e)] for e in edges)


def source_check():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for source in sources["archived_sources"]:
        raw = (HERE / source["vendored_path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == source["sha256"],
                "predecessor bytes changed: " + source["vendored_path"])
    return len(sources["archived_sources"])


def legacy_functions():
    path = HERE / "predecessor/box_search_kj.py"
    tree = ast.parse(path.read_text())
    # Avoid importing the historical script and its transitive predecessor tree.
    names = {"canon_total", "canon_config"}
    definitions = [node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name in names]
    require({node.name for node in definitions} == names, "legacy definitions missing")
    env = {"itertools": itertools}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), env)
    return env["canon_total"], env["canon_config"]


def controls(configurations, old_total, old_config):
    # Identical per-line canonical types can have different joint parities.
    equal = ((3, 3), (3, 3), (3, 3))
    rotated = ((3, 3), (3, 3), (5, 5))
    require(tuple(old_total(*p) for p in equal) ==
            tuple(old_total(*p) for p in rotated), "per-line mutant not reproduced")
    require(c.allowed_arcs(equal) != c.allowed_arcs(rotated), "lost joint parity")
    require(c.direct_canonical(equal, 0) != c.direct_canonical(rotated, 0),
            "global quotient merged distinct joint data")

    # A three-cycle exposes the pushforward/pullback mismatch in canon_config.
    pairs = ((1, 3), (3, 1), (1, 1))
    z = 1 << c.ARC_INDEX[(1, 0)]
    pp, edges = old_config(pairs, frozenset({(1, 0)}))
    legacy = encode(pp, edges)
    require(not (z & ~c.allowed_arcs(pairs)), "input must satisfy scope parity")
    require(legacy == (((1, 1), (1, 3), (3, 1)), 2), "legacy control drift")
    require(legacy[1] & ~c.allowed_arcs(legacy[0]), "invalid legacy output accepted")
    correct = c.direct_canonical(pairs, z)
    require(correct == (((1, 1), (1, 3), (3, 1)), 32), "correct arc pullback")

    # Definition-level action versus optimized canonicalization, including all
    # 36 transforms of deterministic samples and all 64 arc-mask transforms.
    rng = random.Random(20261017)
    for lp_index, lp in enumerate(c.PERMS):
        for mask in range(64):
            require(c.relabel(equal, mask, lp, (0, 1, 2))[1] ==
                    c.LINE_MAPS[lp_index][mask], "arc action table mismatch")
    samples = rng.sample(configurations, 80)
    for key in samples:
        require(c.direct_canonical(*key) == key, "not a direct canonical representative")
        for lp in c.PERMS:
            for tp in c.PERMS:
                pp, zz = c.relabel(*key, lp, tp)
                require(c.canonical_from_plan(c.pair_plan(pp), zz) == key,
                        "canonicalizer not invariant under a legal group action")
                require(not (zz & ~c.allowed_arcs(pp)), "legal action broke scope")

    diagonal = ((1, 1), (2, 2), (4, 4))
    witness = c.brute_witness(diagonal, 63)
    require(c.witness_valid(diagonal, 63, witness), "diagonal positive control")
    a, b, order = witness
    require(not c.witness_valid(diagonal, 63, ((0,) + a[1:], b, order)),
            "broken diagonal witness accepted")
    full = ((7, 7),) * 3
    bad_order = ((1, 1, 1), (1, 1, 1), (0, 1, 2))
    require(not c.witness_valid(full, 1, bad_order), "odd forward zero arc accepted")
    require(c.witness_valid(full, 1, (bad_order[0], bad_order[1], (1, 0, 2))),
            "reverse order control must pass")
    return {"per_line_loss": {"first": equal, "second": rotated,
                              "allowed_Z_masks": [c.allowed_arcs(equal),
                                                  c.allowed_arcs(rotated)]},
            "line_action_failure": {"input": record(pairs, z),
                                    "legacy": record(*legacy),
                                    "correct": record(*correct)},
            "action_samples": len(samples), "witness_rejections": 2}


def legacy_audit(old_total, old_config, complete):
    line_types = sorted({old_total(*p) for p in c.TYPES})
    old_states, represented = set(), set()
    for pairs in itertools.product(line_types, repeat=3):
        plan = c.pair_plan(pairs)
        for z in c.subsets(c.allowed_arcs(pairs)):
            edges = frozenset(e for i, e in enumerate(c.ARCS) if z & (1 << i))
            pp, zz = old_config(pairs, edges)
            old_states.add(encode(pp, zz))
            represented.add(c.canonical_from_plan(plan, z))
    require(len(old_states) == 3023, "source census fixture not reproduced")
    invalid = {key for key in old_states if key[1] & ~c.allowed_arcs(key[0])}
    legacy_gaps = {key for key in old_states if c.brute_witness(*key) is None}
    require(len(legacy_gaps) == 27, "source candidate fixture not reproduced")
    receipt = json.loads((HERE / "predecessor/realize-kj-receipt.json").read_text())
    source_records = receipt["records"]
    require({encode(zip(r["candidate"]["a0"], r["candidate"]["b0"]),
                    r["candidate"]["Z"]) for r in source_records} == legacy_gaps,
            "receipt candidate set differs from reproduced legacy gap set")
    rejected = []
    for index, item in enumerate(source_records):
        p = tuple(zip(item["candidate"]["a0"], item["candidate"]["b0"]))
        bad = [tuple(e) for e in item["candidate"]["Z"]
               if c.dot(p[e[0]][0], p[e[1]][1])]
        if bad:
            require(item["status"] == "not-found-in-cap", "unexpected invalid record")
            rejected.append({"source_record_index": index,
                             **record(p, encode(p, item["candidate"]["Z"])[1]),
                             "odd_anchor_zero_arcs": bad})
    require(len(rejected) == 20, "expected twenty scope-inconsistent candidates")
    return {"line_types": len(line_types), "states": len(old_states),
            "scope_inconsistent_states": len(invalid),
            "represented_valid_orbits": len(represented),
            "omitted_valid_orbits": len(set(complete) - represented),
            "legacy_candidates": len(legacy_gaps),
            "scope_inconsistent_candidates": rejected}, represented


def v2(value):
    require(value != 0, "valuation of zero")
    return (abs(value) & -abs(value)).bit_length() - 1


def realization_check(gaps):
    """Check the three credited integer witnesses from their defining P,Q.
    Rank/anchor-attainment rules dispose of the four other combinatorial shapes.
    """
    source = json.loads((HERE / "predecessor/realize-kj-receipt.json").read_text())
    realized = {}
    for item in source["counterexamples"]:
        P, Q = item["P"], item["Q"]
        M = [[sum(P[t][j] * Q[s][j] for j in range(3)) for s in range(3)]
             for t in range(3)]
        require(all(M[t][t] for t in range(3)), "zero decoder diagonal")
        require(all(M[t][s] == 0 for t, s in c.ARCS), "decoder not diagonal")
        m = [min(v2(P[t][j]) for t in range(3) if P[t][j]) for j in range(3)]
        n = [min(v2(Q[t][j]) for t in range(3) if Q[t][j]) for j in range(3)]
        gamma = min(m[j] + n[j] for j in range(3))
        aa = [sum(1 << j for j in range(3) if P[t][j] and v2(P[t][j]) == m[j])
              for t in range(3)]
        bb = [sum(1 << j for j in range(3) if Q[t][j] and
                  v2(Q[t][j]) == gamma - m[j]) for t in range(3)]
        pairs = tuple(zip(aa, bb))
        key = c.direct_canonical(pairs, 63)
        require(key in gaps and key not in realized, "duplicate/unknown realized shape")
        pi = tuple(sum(1 << j for j in range(3) if P[t][j]) for t in range(3))
        sg = tuple(sum(1 << j for j in range(3) if Q[t][j]) for t in range(3))
        support_pairs = tuple(zip(pi, sg))
        witness = c.brute_witness(support_pairs, 63)
        require(c.witness_valid(support_pairs, 63, witness), "cert=3 witness invalid")
        require(c.brute_witness(pairs, 63) is None, "box gap lost")
        realized[key] = {"P": P, "Q": Q, "M": M, "gamma": gamma,
                         "cert_witness": witness}
    shapes = []
    for pairs, z in gaps:
        require(z == 63 and all(a & 3 == 3 and b & 3 == 3 for a, b in pairs),
                "gap classification shape changed")
        # (a,b)=(1,1),(2,2) on lines 0,1 witnesses box>=2 in either order.
        union_a = pairs[0][0] | pairs[1][0] | pairs[2][0]
        if union_a != 7:
            status = "unrealizable: diagonal rank three requires three nondegenerate totals; each P-column minimum must be attained"
        else:
            require((pairs, z) in realized, "unresolved rank-three shape")
            status = "realized: predecessor integer P,Q replayed; box=2, cert=3"
        shapes.append({**record(pairs, z), "box": 2, "status": status,
                       "witness": realized.get((pairs, z))})
    require(len(realized) == 3 and len(shapes) == 7, "realization classification drift")
    return shapes


def replay():
    pins = source_check()
    configurations, raw, multisets = c.enumerate_orbits()
    burnside, fixed = c.burnside_count()
    require(burnside == len(configurations), "independent Burnside count mismatch")
    require(fixed[0] == raw, "ordered domain count mismatch")
    old_total, old_config = legacy_functions()
    control_receipt = controls(configurations, old_total, old_config)
    gaps, fallback = [], 0
    for pairs, z in configurations:
        require(not (z & ~c.allowed_arcs(pairs)), "inadmissible census state")
        fast = c.singleton_witness(pairs, z)
        if fast is None:
            fallback += 1
            fast = c.exact_witness(pairs, z)
        brute = c.brute_witness(pairs, z)
        require((fast is None) == (brute is None), "independent box decision mismatch")
        if fast is None:
            gaps.append((pairs, z))
        else:
            require(c.witness_valid(pairs, z, fast) and c.witness_valid(pairs, z, brute),
                    "positive census witness rejected")
    legacy, represented = legacy_audit(old_total, old_config, configurations)
    require(set(gaps) <= represented, "legacy reduced domain missed a gap shape")
    return {"schema_version": 1, "domain": {"totals": 3, "lines": 3, "tau_min": 1},
            "raw_ordered_states": raw, "raw_line_type_multisets": multisets,
            "global_orbits": len(configurations), "burnside_fixed_counts": fixed,
            "box3_orbits": len(configurations) - len(gaps), "box2_orbits": len(gaps),
            "chronological_fallbacks": fallback, "brute_oracle_checks": len(configurations),
            "legacy": legacy, "gap_shapes": realization_check(gaps),
            "controls": control_receipt, "source_pins": pins}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write RESULTS.json explicitly")
    args = parser.parse_args()
    result = replay()
    data = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = HERE / "RESULTS.json"
    if args.write:
        path.write_text(data, encoding="utf-8", newline="\n")
    else:
        require(path.read_text(encoding="utf-8") == data, "receipt differs; inspect before --write")
    digest = hashlib.sha256(data.encode()).hexdigest()
    print("PASS_JOINT_CENSUS ordered=%d orbits=%d box3=%d box2=%d brute=%d" %
          (result["raw_ordered_states"], result["global_orbits"], result["box3_orbits"],
           result["box2_orbits"], result["brute_oracle_checks"]))
    print("PASS_LEGACY_AUDIT states=3023 invalid=1370 candidates=27 invalid_candidates=20")
    print("PASS_REALIZATION_CLASSIFICATION shapes=7 realized=3 impossible=4")
    print("PASS_JOINT_CONTROLS pins=%d digest=%s" % (result["source_pins"], digest))


if __name__ == "__main__":
    main()
