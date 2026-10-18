#!/usr/bin/env python3
"""Exact conditional P104 scalar surgery; no native schedule or gain claim.

Run from any directory with Python 3.12+ and the standard library:
    python3 -I -B research/p104-interleaved-search/scalar_surgery.py

The old 112-port scalar word is retained except for its centre cut. Eight X
ports and eight Y ports become arbitrary dirty helpers. The hypothetical new
cut supplies eight *pure initial-live-X* queries and adds their specified
linear combinations into live Y registers. This is an oracle contract, not a
claim that those queries occupy available registers or have legal frames.

The verifier constructs initial-zero-frame compensation and final-full-frame
restoration, then replays every generated scalar operation on all 704 initial
columns. It also reports the native survivor-mask violations of the proposed
cut. Query construction, query storage/restoration, legal interleaving, native
transports, and a complete hosted cost remain unproved.

Sources: retained PR1042 local word used by the selected PR1094 assembly, via
complex-block-rank-optimum; icekylinx's frame-sa504 Hamming coordinates; Josie
Elliston's PR1071 P104 fixture, retained through PR1940/1972 and the native
channel package. Their notices and attribution remain in those packages.
New verifier prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "word": (
        "research/complex-block-rank-optimum/inputs/selected.json.gz",
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    ),
    "coordinates": (
        "research/frame-sa504/inputs/hamming/PROTOTYPE.json",
        "327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f",
    ),
    "fixture": (
        "research/p104-native-channel/inputs/P104-FIXTURE.json",
        "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    ),
}
REMOVED = (3, 14, 21, 34, 39, 61, 76, 93)
DECODER_ROOT_PAIRS = ((1, 28), (2, 47), (3, 113), (4, 57),
                      (12, 7), (65, 0), (82, 6), (97, 5))
Q = Fraction
Row = dict[int, Fraction]
Rows = list[Row]


def require(condition: bool, message: str) -> None:
    """Keep all checks active under python -O as well."""
    if not condition:
        raise ValueError(message)


def load_inputs() -> dict:
    result = {}
    for name, (relative, expected) in INPUTS.items():
        data = (ROOT / relative).read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected, f"input hash: {relative}")
        result[name] = json.loads(gzip.decompress(data) if relative.endswith(".gz") else data)
    return result


def identity(n: int) -> Rows:
    return [{i: Q(1)} for i in range(n)]


def add_row(target: Row, source: Row, coefficient: Fraction) -> None:
    for column, value in list(source.items()):
        updated = target.get(column, Q(0)) + coefficient * value
        if updated:
            target[column] = updated
        else:
            target.pop(column, None)


def apply(event: list, rows: Rows) -> None:
    kind, target = event[:2]
    if kind == "scale":
        coefficient = Q(event[2], event[3])
        require(bool(coefficient), "zero scaling is not invertible")
        rows[target] = {j: coefficient * value for j, value in rows[target].items()}
    elif kind == "add":
        source = event[2]
        require(target != source, "self-add is outside the retained operation contract")
        add_row(rows[target], rows[source], Q(event[3], event[4]))
    else:
        raise ValueError(f"unknown scalar operation: {kind}")


def run(rows: Rows, *parts: list) -> Rows:
    for part in parts:
        for event in part:
            apply(event, rows)
    return rows


def endpoint_failures(rows: Rows, v: int, live: list[int]) -> list[int]:
    """All non-live-Y registers must be restored, including the sixteen roles."""
    live_set = set(live)
    bad = []
    for register, row in enumerate(rows):
        wanted = {register: Q(1)}
        if v <= register < 2 * v and register - v in live_set:
            wanted[register - v] = Q(1)
        if row != wanted:
            bad.append(register)
    return bad


def solve(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    """Exact square solve, rejecting a singular live-target transfer matrix."""
    n = len(left)
    augmented = [a.copy() + b.copy() for a, b in zip(left, right)]
    for column in range(n):
        pivot = next((r for r in range(column, n) if augmented[r][column]), None)
        require(pivot is not None, f"singular target transfer at column {column}")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        coefficient = augmented[column][column]
        augmented[column] = [x / coefficient for x in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            coefficient = augmented[row][column]
            if coefficient:
                augmented[row] = [x - coefficient * y for x, y in zip(augmented[row], augmented[column])]
    require(
        all(augmented[i][:n] == [Q(i == j) for j in range(n)] for i in range(n)),
        "target solve did not reduce to the identity",
    )
    answer = [row[n:] for row in augmented]
    require(
        all(sum(left[i][j] * answer[j][k] for j in range(n)) == right[i][k]
            for i in range(n) for k in range(len(right[0]))),
        "target solve residual",
    )
    return answer


def dot(a: list | tuple, b: list | tuple) -> int:
    return sum(x * y for x, y in zip(a, b))


def coordinate_data(word: dict, prototype: dict, fixture: dict) -> tuple:
    native = fixture["section4_explicit_P104"]

    def transform(label: int) -> int:
        return label ^ (43 if (label & 43).bit_count() % 2 else 0)

    def coordinates(vector: list) -> tuple[int, ...]:
        products = [dot(vector, basis_vector) for basis_vector in native["F0"]]
        require(all(value % 4 == 0 for value in products), "nonintegral fixture coordinates")
        return tuple(value // 4 for value in products)

    def canonical(vector: tuple) -> tuple:
        first = next(x for x in vector if x)
        return tuple(-x for x in vector) if first < 0 else vector

    roots = prototype["root_lines"]
    labels = prototype["binary_ports"]
    index = {tuple(root): i for i, root in enumerate(roots)}
    root_by_label = {transform(label): root for label, root in zip(labels, roots)}
    selected_roots = [root_by_label[label] for label in word["ports"]]
    removed_labels = {transform(labels[index[canonical(coordinates(c))]]) for c in native["C"]}
    derived_removed = tuple(i for i, label in enumerate(word["ports"]) if label in removed_labels)
    require(derived_removed == REMOVED, "fixture/selected puncture mismatch")
    terms = []
    # This orientation is shared with the retained two-query delivery fragment.
    # The pinned native fixture supplies the puncture, not its old orientation.
    for ai, bi in DECODER_ROOT_PAIRS:
        a, b = tuple(roots[ai]), tuple(roots[bi])
        ab_dot = dot(a, b)
        require(ab_dot != 0, "zero decoder denominator")
        terms.append((a, b, transform(labels[ai]), ab_dot))
    require(len(terms) == 8, "expected eight decoder terms")
    return selected_roots, terms


def verify() -> dict:
    inputs = load_inputs()
    word = inputs["word"]
    v, n = word["v"], 2 * word["v"] + word["R"]
    require((v, n, word["R"]) == (112, 704, 480), "unexpected retained word dimensions")
    live = [i for i in range(v) if i not in REMOVED]
    prefix = [word[key] for key in ("precondition", "compensation", "A")]
    suffix = [word[key] for key in ("B", "tail", "cleanup")]
    baseline = run(identity(n), *prefix, word["cut"], *suffix)
    require(not endpoint_failures(baseline, v, list(range(v))), "original full-column baseline failed")

    # Mutate one actual centre coefficient. The original full-column identity
    # must detect it, independently of any surgery-derived compensation.
    corrupted_cut = [event.copy() for event in word["cut"]]
    require(corrupted_cut[0][0] == "add", "control expects a centre addition")
    corrupted_cut[0][3] += corrupted_cut[0][4]
    corrupt_bad = endpoint_failures(run(identity(n), *prefix, corrupted_cut, *suffix), v, list(range(v)))
    require(bool(corrupt_bad), "corrupted baseline gate was accepted")

    # This invariant permits scalar restoration using restored X/helper values:
    # no scalar gate sends Y data back into those registers. Their frame access
    # is checked separately below, not inferred from scalar independence.
    require(
        all(not (event[0] == "add" and v <= event[2] < 2 * v and not v <= event[1] < 2 * v)
            for part in prefix + suffix + [word["cut"]] for event in part),
        "Y data flows into a source/helper register",
    )
    frames = word["frames"]
    require(frames[0] == [], "frame index zero is not the zero frame")
    require(all(word["start"][v + t] == 0 for t in range(v)), "targets do not all start at zero")
    require(all(len(frames[word["start"][t]]) == 1 for t in REMOVED), "removed X is not a line")
    require(all(len(frames[word["final"][v + t]]) == 8 for t in REMOVED), "removed Y is not rank eight")

    target_inputs = [{i - v: Q(1)} if v <= i < 2 * v else {} for i in range(n)]
    target_transfer = run(target_inputs, word["B"])
    matrix = [target_transfer[v + i] for i in range(v)]
    roots, terms = coordinate_data(word, inputs["coordinates"], inputs["fixture"])
    decoder = [[Q(dot(roots[t], a), 4 * denominator) for a, b, label, denominator in terms] for t in live]
    scatter = solve([[matrix[i].get(j, Q(0)) for j in live] for i in live], decoder)
    queries = [{s: Q(dot(roots[s], b)) for s in live if dot(roots[s], b)} for a, b, label, denominator in terms]
    require(
        all(sum(decoder[i][k] * queries[k].get(s, Q(0)) for k in range(8)) == Q(dot(roots[t], roots[s]), 4)
            for i, t in enumerate(live) for s in live),
        "decoder does not give the required live G/2 endpoint",
    )

    def hypothetical_cut(rows: Rows, query_rows: Rows) -> None:
        # Query dictionaries index *initial* source columns, not rows currently
        # stored in registers. No physical realization is hidden in this step.
        for i, target in enumerate(live):
            for k, query in enumerate(query_rows):
                if scatter[i][k]:
                    add_row(rows[v + target], query, scatter[i][k])

    def surgery(initial_compensation: list, query_rows: Rows | None = None) -> Rows:
        rows = run(identity(n), initial_compensation, *prefix)
        hypothetical_cut(rows, queries if query_rows is None else query_rows)
        return run(rows, *suffix)

    uncorrected = surgery([])
    new_compensation = []
    for target in live:
        row = uncorrected[v + target]
        require(all(row.get(s, Q(0)) == Q(s == target) for s in live), "wrong live source endpoint")
        require(row.get(v + target) == 1, "wrong initial target coefficient")
        for source, coefficient in sorted(row.items()):
            if source in (target, v + target):
                continue
            require(source in REMOVED or (source >= 2 * v and word["start"][source] == 0),
                    f"nuisance column {source} cannot be compensated at frame zero")
            q = -coefficient
            new_compensation.append(["add", v + target, source, q.numerator, q.denominator, 0])

    # Replay the new gates before the old precondition, rather than assuming
    # that deleting their predicted endpoint coefficients proves correctness.
    compensated = surgery(new_compensation)
    require(all(compensated[v + t] == {v + t: Q(1), t: Q(1)} for t in live),
            "actual initial compensation replay failed")
    require(all(compensated[r] == {r: Q(1)} for r in list(range(v)) + list(range(2 * v, n))),
            "source/helper restoration failed before final Y repair")
    full_frame = word["final"][0]
    restores = []
    for target in REMOVED:
        require(compensated[v + target].get(v + target) == 1, "removed Y lost its initial value")
        for source, coefficient in sorted(compensated[v + target].items()):
            if source == v + target:
                continue
            require(source < v or source >= 2 * v, "restoration needs a non-full live Y input")
            q = -coefficient
            restores.append(["add", v + target, source, q.numerator, q.denominator, full_frame])
    omitted_bad = endpoint_failures(compensated, v, live)
    require(bool(restores) and bool(omitted_bad), "omitted-restoration control was accepted")
    require(all(v + t in omitted_bad for t in REMOVED), "not every removed Y needs restoration")
    completed = run([row.copy() for row in compensated], restores)
    require(not endpoint_failures(completed, v, live), "conditional all-column endpoint failed")
    nonfull_restore_sources = sorted({event[2] for event in restores
                                      if len(frames[word["final"][event[2]]]) != 9})
    require(not nonfull_restore_sources, "final restoration needs a source outside the retained full endpoint")

    # Keep all derived repair coefficients fixed in both controls. A new solve
    # would conceal precisely the dirty-input and query errors being tested.
    without_compensation = run([row.copy() for row in uncorrected], restores)
    dirty_columns = set(REMOVED) | {r for r in range(2 * v, n) if word["start"][r] == 0}
    uncompensated_live_dirty_entries = sum(
        bool(without_compensation[v + t].get(source)) for t in live for source in dirty_columns
    )
    require(uncompensated_live_dirty_entries > 0, "omitted compensation did not expose live-Y dirty columns")
    uncompensated_bad = endpoint_failures(without_compensation, v, live)
    require(bool(uncompensated_bad), "omitted-compensation control was accepted")

    corrupted_queries = [row.copy() for row in queries]
    corrupt_query_source = min(corrupted_queries[0])
    corrupted_queries[0][corrupt_query_source] += 1
    corrupted_query_endpoint = run(surgery(new_compensation, corrupted_queries), restores)
    query_bad = endpoint_failures(corrupted_query_endpoint, v, live)
    require(bool(query_bad), "corrupted hypothetical query was accepted with fixed repairs")
    require(any(corrupted_query_endpoint[v + t].get(corrupt_query_source, Q(0)) != Q(t == corrupt_query_source)
                for t in live), "query corruption was not detected on a live source column")

    illegal_reads = [sum(bool(scatter[i][k]) and bool((word["ports"][t] & label).bit_count() % 2)
                         for i, t in enumerate(live)) for k, (a, b, label, denominator) in enumerate(terms)]
    require(illegal_reads == [0, 0, 0, 0, 26, 0, 26, 28], f"survivor-mask diagnostic changed: {illegal_reads}")
    return {
        "status": "PASS_CONDITIONAL_SCALAR_SURGERY",
        "scope": "Exact rational scalar identity under hypothetical pure-source query-cut access; no legal native schedule or kappa gain claimed.",
        "sources": [{"path": relative, "sha256": digest} for relative, digest in INPUTS.values()],
        "input_columns": n,
        "original_ports": v,
        "live_ports": len(live),
        "retained_old_helpers": word["R"],
        "converted_dirty_roles": 2 * len(REMOVED),
        "removed_selected_positions": list(REMOVED),
        "baseline_all_columns_pass": True,
        "live_target_transfer_rank": len(live),
        "hypothetical_query_count": len(queries),
        "decoder_hamming_root_pairs": [list(pair) for pair in DECODER_ROOT_PAIRS],
        "query_scale_for_delivery_output_dot_a": [str(Q(1, 4 * denominator)) for a, b, label, denominator in terms],
        "hypothetical_query_definition": "q_k = sum over live s of dot(root_s,b_k)*initial_X_s; endpoint coefficient is dot(root_t,a_k)/(4*dot(a_k,b_k)). A delivery source may absorb the constant 1/(4*dot(a_k,b_k)); no assembled schedule is asserted.",
        "hypothetical_scatter_additions": sum(bool(q) for row in scatter for q in row),
        "new_zero_frame_compensation_additions": len(new_compensation),
        "new_full_frame_restoration_additions": len(restores),
        "restoration_sources_without_retained_full_endpoint": nonfull_restore_sources,
        "repair_max_coefficient_denominator": max(event[4] for event in new_compensation + restores),
        "endpoint_role_changes": {"removed_X_start_rank": [1, 0], "removed_Y_final_rank": [8, 9]},
        "hypothetical_cut_illegal_survivor_reads_by_term": illegal_reads,
        "controls": {
            "corrupted_original_cut_coefficient_rejected": True,
            "corrupted_original_cut_bad_registers": corrupt_bad,
            "omitted_final_restoration_rejected": True,
            "omitted_final_restoration_bad_registers": omitted_bad,
            "omitted_new_compensation_rejected": True,
            "omitted_new_compensation_bad_registers": uncompensated_bad,
            "omitted_new_compensation_live_dirty_entries": uncompensated_live_dirty_entries,
            "corrupted_hypothetical_query_with_fixed_repairs_rejected": True,
            "corrupted_hypothetical_query_bad_registers": query_bad,
            "corrupted_hypothetical_query_term_and_source": [0, corrupt_query_source],
        },
        "unproved_obligations": [
            "Form and store the eight pure-source queries with restored dirty helpers.",
            "Replace the hypothetical cut by legal native common-frame operations.",
            "Check actual added transport, storage lifetimes, backward supplier, and whole-call hosting.",
            "Establish a complete paid recurrence and a kappa improvement.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
