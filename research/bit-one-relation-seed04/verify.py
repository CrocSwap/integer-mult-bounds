#!/usr/bin/env python3
"""Finite checks supporting the written arbitrary-register one-relation proof.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
The universal argument is in README.md; this finite replay is not that proof.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return sum(1 << (i * n + i) for i in range(n))


def mm(a, b, n):
    """Packed binary matrices, ordinary matrix multiplication over F2."""
    result = 0
    mask = (1 << n) - 1
    for i in range(n):
        row = 0
        for j in range(n):
            if (a >> (i * n + j)) & 1:
                row ^= (b >> (j * n)) & mask
        result |= row << (i * n)
    return result


def outer(x, y, n):
    return sum(y << (i * n) for i in range(n) if (x >> i) & 1)


def projectors(n):
    return sorted(outer(x, y, n)
                  for x in range(1, 1 << n)
                  for y in range(1, 1 << n)
                  if (x & y).bit_count() % 2)


def topological(pattern, n):
    pending = set(range(n))
    order = []
    while pending:
        roots = [j for j in sorted(pending)
                 if not any((pattern >> (i * n + j)) & 1 for i in pending)]
        if not roots:
            return None
        j = roots[0]
        order.append(j)
        pending.remove(j)
    return order


def cycle_vertices(pattern, n):
    reach = [[bool((pattern >> (i * n + j)) & 1) for j in range(n)]
             for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] |= reach[i][k] and reach[k][j]
    return sum(1 << (i * n + i) for i in range(n) if reach[i][i])


def pmul(left, right, n):
    """Laurent polynomials with packed F2 matrix coefficients."""
    out = {}
    for a, x in left.items():
        for b, y in right.items():
            key = tuple(u + v for u, v in zip(a, b))
            out[key] = out.get(key, 0) ^ mm(x, y, n)
    return {k: v for k, v in out.items() if v}


def factor(frame, p, n):
    zero = (Q(0),) * len(frame)
    out = {zero: eye(n) ^ p}
    out[frame] = out.get(frame, 0) ^ p
    return {k: v for k, v in out.items() if v}


def product(operations, n, dimension):
    out = {(Q(0),) * dimension: eye(n)}
    for frame, p in operations:
        out = pmul(out, factor(frame, p, n), n)
    return out


def rank(rows):
    rows = [list(map(Q, row)) for row in rows]
    if not rows:
        return 0
    r = 0
    for j in range(len(rows[0])):
        pivot = next((i for i in range(r, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        scale = rows[r][j]
        rows[r] = [x / scale for x in rows[r]]
        for i in range(r + 1, len(rows)):
            scale = rows[i][j]
            rows[i] = [a - scale * b for a, b in zip(rows[i], rows[r])]
        r += 1
        if r == len(rows):
            break
    return r


def address_rank(a, m):
    return rank([a[i * m:(i + 1) * m] for i in range(m)])


def endpoint_targets(poly, n):
    if any(p & ~eye(n) for p in poly.values()):
        return None
    targets = []
    for i in range(n):
        terms = [a for a, p in poly.items() if (p >> (i * n + i)) & 1]
        if len(terms) != 1:
            return None
        targets.append(terms[0])
    return targets


def structural_census(n):
    ps = projectors(n)
    groups = defaultdict(list)
    for p in ps:
        require(mm(p, p, n) == p, "projector construction")
        groups[p & ~eye(n)].append(p)
    cyclic = 0
    for pattern, group in groups.items():
        order = topological(pattern, n)
        if order is None:
            cyclic += 1
            require(len(group) == 1, "cyclic pattern does not determine projector")
            require(group[0] & eye(n) == cycle_vertices(pattern, n),
                    "cyclic diagonal recovery")
        else:
            for p in group:
                require(sum((p >> (i * n + i)) & 1 for i in range(n)) == 1,
                        "acyclic rank-one projector needs one diagonal one")
                require(all(not ((p >> (order[i] * n + order[j])) & 1)
                            for i in range(n) for j in range(i)),
                        "common triangular order")
    active = 0
    for p in ps:
        for k in range(n):
            e = 1 << (k * n + k)
            q = pmul(pmul(factor((Q(1),), p, n), {(Q(0),): e}, n),
                     factor((Q(-1),), p, n), n)
            commute = mm(p, e, n) == mm(e, p, n)
            off = any(c & ~eye(n) for c in q.values())
            require(off != commute, "conjugation/commutation equivalence")
            if not commute:
                active += 1
                cells = [{a[0] for a, c in q.items() if (c >> (i * n + j)) & 1}
                         for i in range(n) for j in range(n) if i != j]
                require({Q(0), Q(1)} in cells or {Q(0), Q(-1)} in cells,
                        "missing explicit z+1 or z^-1+1 witness")
            else:
                require(q == {(Q(0),): e}, "commuting conjugation is unchanged")
    return {
        "registers": n, "projectors": len(ps), "off_diagonal_patterns": len(groups),
        "cyclic_patterns": cyclic, "acyclic_patterns": len(groups) - cyclic,
        "pattern_multiplicities": dict(sorted(Counter(map(len, groups.values())).items())),
        "conjugations": n * len(ps), "noncommuting_conjugations": active,
        "projectors_sha256": hashlib.sha256(json.dumps(ps).encode()).hexdigest(),
    }


def unit(i, j, m=4):
    return tuple(Q(int((a, b) == (i, j))) for a in range(m) for b in range(m))


def plus(*vectors):
    return tuple(sum(x) for x in zip(*vectors))


def scale(c, a):
    return tuple(c * x for x in a)


def fixtures():
    """Explicit rational addresses; coefficient arithmetic alone is binary."""
    n = m = 4
    a, b, c = unit(0, 0), unit(0, 1), unit(2, 2)
    j3 = outer(7, 7, n)
    e0, e3 = 1, 1 << 15
    loop = [(a, j3), (b, j3), (scale(-1, plus(a, b)), j3)]
    outgoing = outer(15, 7, n)
    incoming = outer(7, 15, n)
    outgoing_loop = [(frame, outgoing) for frame, _ in loop]
    incoming_loop = [(frame, incoming) for frame, _ in loop]
    p, q = outer(1, 3, n), outer(3, 2, n)
    # PR468 controls.py's noncommuting eight-call, rank-two-target fixture,
    # embedded into four scalar registers and four address coordinates.
    old_frames = [unit(2, 2), a, unit(1, 1), plus(a, unit(1, 0)),
                  plus(unit(1, 1), scale(-1, unit(1, 0))),
                  plus(a, b), plus(unit(1, 1), scale(-1, b)), scale(-1, unit(2, 2))]
    old_ps = [p, e0, e0, 1 << 5, 1 << 5, 1 << 10, 1 << 10, p]
    sharp = [(unit(i, (i + w) % m), 1 << (w * n + w))
             for w in range(n) for i in range(m)]
    return {
        "four_full_rank_targets_16_calls": (n, m, sharp, True, True),
        "acyclic_equal_pattern_half":
            (n, m, [(scale(Q(1, 2), a), p), (scale(Q(1, 2), a), q)], True, True),
        "acyclic_opposite_frames_rejected":
            (n, m, [(scale(Q(1, 2), a), p), (scale(Q(-1, 2), a), q)], False, True),
        "non_cube_relation_coordinate_word":
            (n, m, [(scale(2, a), e0), (a, 1 << 5)], True, True),
        "non_cube_relation_mixing_rejected":
            (n, m, [(scale(2, a), j3), (a, j3)], False, True),
        "cyclic_three_frame_loop": (n, m, loop, True, True),
        "cyclic_active_exterior": (n, m, loop + [(c, e0)], True, True),
        "cyclic_disjoint_interior":
            (n, m, [loop[0], (c, e3), *loop[1:]], True, True),
        "cyclic_active_interior_rejected":
            (n, m, [loop[0], (c, e0), *loop[1:]], False, True),
        "fourth_role_outgoing_only_rejected":
            (n, m, [outgoing_loop[0], (c, e3), *outgoing_loop[1:]], False, True),
        "fourth_role_incoming_only_rejected":
            (n, m, [incoming_loop[0], (c, e3), *incoming_loop[1:]], False, True),
        "wrong_common_pattern_rejected":
            (n, m, [(a, j3), (scale(-1, a), p)], False, True),
        "pr468_eight_call_outside_nullity_scope":
            (n, m, list(zip(old_frames, old_ps)), True, False),
    }


def canonical_product(poly):
    return [[list(map(str, a)), p] for a, p in sorted(poly.items())]


def replay_fixture(name, fixture):
    n, m, ops, diagonal, scope = fixture
    allowed = set(projectors(n))
    require(all(p in allowed for _, p in ops), name + ": rank-one scalar idempotents")
    require(all(address_rank(a, m) == 1 for a, _ in ops), name + ": rank-one rational frames")
    nullity = len(ops) - rank([a for a, _ in ops])
    require((nullity <= 1) == scope, name + ": relation scope")
    poly = product(ops, n, m * m)
    targets = endpoint_targets(poly, n)
    require((targets is not None) == diagonal, name + ": endpoint expectation")
    target_ranks = None if targets is None else [address_rank(t, m) for t in targets]
    if diagonal and scope:
        require(sum(target_ranks) <= len(ops), name + ": rank bill")
    return {
        "calls": len(ops), "frame_span": len(ops) - nullity, "relation_nullity": nullity,
        "diagonal_endpoint": diagonal, "within_relation_scope": scope,
        "target_ranks": target_ranks,
        "formal_product_sha256": hashlib.sha256(
            json.dumps(canonical_product(poly), separators=(",", ":")).encode()).hexdigest(),
    }, poly


def input_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    count = 0
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue
        data = (ROOT / item["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item["sha256"], "source SHA256: " + item["path"])
        git_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(git_blob == item["git_blob"], "source Git blob: " + item["path"])
        count += 1
    return count


def independent_module():
    spec = importlib.util.spec_from_file_location("one_relation_independent", HERE / "independent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    inputs = input_pins()
    independent = independent_module()
    census = [structural_census(n) for n in range(1, 5)]
    for row in census:
        independent.check_structure(row)
    results = {}
    for name, fixture in fixtures().items():
        results[name], poly = replay_fixture(name, fixture)
        independent.check_word(name, fixture, poly, results[name])
    controls = {}
    # One rank-two projector produces two rank-one diagonal targets for one call.
    a = unit(0, 0)
    rank_two = 1 | (1 << 5)
    require(rank_two not in projectors(4), "rank-two projector was admitted")
    targets = endpoint_targets(product([(a, rank_two)], 4, 16), 4)
    require(sum(address_rank(t, 4) for t in targets) == 2, "rank-two hypothesis control")
    controls["rank_two_projector_would_violate_bill"] = True
    # [A] and [3A] have identical parity but distinct formal addresses.
    p1 = product([(a, 1)], 4, 16)
    p3 = product([(scale(3, a), 1)], 4, 16)
    require(p1 != p3, "rational address alias was accepted")
    require(tuple(x % 2 for x in a) == tuple(x % 2 for x in scale(3, a)), "alias fixture")
    independent.check_controls()
    controls["mod_two_address_alias_rejected"] = True
    controls["acyclic_relation_sign_error_rejected"] = True
    controls["non_cube_relation_mixing_rejected"] = True
    controls["active_interior_rejected"] = True
    controls["zero_diagonal_outgoing_role_not_inactive"] = True
    controls["zero_diagonal_incoming_role_not_inactive"] = True
    controls["unequal_cyclic_pattern_rejected"] = True
    controls["extra_relations_not_admitted"] = True
    return {
        "schema_version": 1, "assignment_seed": 4,
        "statement": "Finite supporting identities only; the universal theorem is the written proof.",
        "source_inputs_checked": inputs, "census": census, "fixtures": results,
        "negative_controls": controls,
        "independence": "Packed coefficient matrices versus per-entry exponent sets; separate scalar catalogue and rational rank algorithms.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    result = run()
    data = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        path.write_text(data)
    else:
        require(path.read_text() == data, "certificate differs from exact replay")
    print("PASS_BIT_ONE_RELATION registers=1..4 projectors=155 conjugations=577 fixtures=13 controls=9 no_new_kappa")


if __name__ == "__main__":
    main()
