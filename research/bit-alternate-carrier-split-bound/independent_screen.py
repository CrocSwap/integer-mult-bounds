#!/usr/bin/env python3
"""Independent rank-block audit of selected BIT alternate-carrier cuts.

Uses the pinned canonical word, an exact rational frame-containment check, a
forward row replay and a separate reverse column replay.  Candidate existence
is tested by rank identities, without enumerating kernel witness pairs.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

INPUT = Path(__file__).with_name("inputs") / "BIT-NATIVE-WORD.json.gz"
PIN = "e54523517d0f03e58352e647c403a5af3e525a57"
SOURCE = "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"
SOURCE_SHA = "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def read_source() -> tuple[dict, bytes]:
    raw = INPUT.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA, "pinned native source bytes")
    return json.loads(gzip.decompress(raw)), raw


def rref_rank(rows: list[list[F]]) -> int:
    """Exact rational row rank on the source's eight-coordinate chart basis."""
    if not rows:
        return 0
    a = [list(map(F, row)) for row in rows]
    width = len(a[0])
    rank = 0
    for col in range(width):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = a[rank][col]
        a[rank] = [x / scale for x in a[rank]]
        for i in range(len(a)):
            if i != rank and a[i][col]:
                factor = a[i][col]
                a[i] = [x - factor * y for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank


def contained(frame_rows: list[list[F]], larger_rows: list[list[F]]) -> bool:
    return rref_rank(larger_rows + frame_rows) == rref_rank(larger_rows)


def gf2_rank(rows: list[int]) -> int:
    """Row rank using low-bit pivots; works on packed matrix rows."""
    pivots: dict[int, int] = {}
    for row in rows:
        x = row
        while x:
            p = (x & -x).bit_length() - 1
            old = pivots.get(p)
            if old is None:
                pivots[p] = x
                break
            x ^= old
    return len(pivots)


def row_product(rows: list[int], coeffs: int) -> int:
    out = 0
    while coeffs:
        bit = coeffs & -coeffs
        i = bit.bit_length() - 1
        out ^= rows[i]
        coeffs ^= bit
    return out


def parity(x: int) -> int:
    return x.bit_count() & 1


def one_context(prefix_rows: list[int], suffix_cols: list[int], group_mask: int, n: int):
    """Return two quotient-image dimensions from direct rank identities.

    A = P[B, outside G], C = S[outside G, B], K = P[B,G] S[G,B].
    ``delta0`` measures the image of ker(A^T) modulo row(C); ``deltaK``
    measures the image of ker(A^T)K modulo row(C).
    """
    s = len(prefix_rows)
    all_inputs = (1 << n) - 1
    outside = all_inputs ^ group_mask
    a_rows = [r & outside for r in prefix_rows]
    out_indices = [i for i in range(n) if (outside >> i) & 1]
    c_rows = []
    for out in out_indices:
        c_rows.append(sum(((col >> out) & 1) << j for j, col in enumerate(suffix_cols)))

    # K[j,l] = <prefix row j on G, suffix column l on G>.
    in_g = [r & group_mask for r in prefix_rows]
    out_g = [col & group_mask for col in suffix_cols]
    k_rows = []
    for x in in_g:
        bits = 0
        for j, y in enumerate(out_g):
            bits |= parity(x & y) << j
        k_rows.append(bits)

    ra, rc = gf2_rank(a_rows), gf2_rank(c_rows)
    ca_rows = [row_product(a_rows, c) for c in c_rows]
    rca = gf2_rank(ca_rows)
    delta0 = s - ra - rc + rca

    # Rank of M=[[A,K],[0,C]], with unknown row (a,z) and equations
    # (aA, aK+zC).  Its rank yields dim(ker(A^T)K mod row(C)).
    # Keep a fixed outside-coordinate block width so rank comparisons agree
    # across zero columns and differing chart contexts.
    outside_width = n
    top = [a | (k << outside_width) for a, k in zip(a_rows, k_rows)]
    bottom = [c << outside_width for c in c_rows]
    rm = gf2_rank(top + bottom)
    delta_k = rm - ra - rc
    need(delta0 >= 0 and delta_k >= 0, "quotient dimensions are nonnegative")
    return {
        "bank_size": s,
        "outside_rank_A": ra,
        "outside_rank_C": rc,
        "rank_CA": rca,
        "rank_block_M": rm,
        "delta_ab": delta0,
        "delta_helper": delta_k,
    }


def run() -> dict:
    w, raw = read_source()
    n = int(w["public"])
    total_fields = n + int(w["owned_fields"])
    frames = {int(k): v for k, v in w["frames"].items()}
    groups_by_boundary: dict[tuple[int, int], list[int]] = defaultdict(list)
    for role in range(222, n):
        groups_by_boundary[(int(w["start"][role]), int(w["final"][role]))].append(role)
    boundaries = sorted(groups_by_boundary)
    groups = [groups_by_boundary[p] for p in boundaries]

    # Exact rational frame containment is computed from row spaces, rather
    # than complement-pair orthogonality.  These are the only legal A<C<D
    # triples in the screen.
    eligible_by_chart: dict[int, list[int]] = defaultdict(list)
    for c, fc in frames.items():
        for g, (a, d) in enumerate(boundaries):
            fa, fd = frames[a], frames[d]
            if int(fa["dim"]) < int(fc["dim"]) < int(fd["dim"]):
                if contained(fa["B"], fc["B"]) and contained(fc["B"], fd["B"]):
                    eligible_by_chart[c].append(g)

    groups_as_sets = [set(xs) for xs in groups]
    group_masks = [sum(1 << i for i in xs) for xs in groups]

    # Direct chronological state: each register row is its exact F2 form on
    # the 659 original public inputs. Owned registers start at zero.
    where: list[int | None] = list(map(int, w["start"])) + [None] * (total_fields - n)
    prefix: list[int] = [1 << i for i in range(n)] + [0] * (total_fields - n)
    banks: dict[int, set[int]] = defaultdict(set)
    for role, chart in enumerate(where):
        if chart is not None:
            banks[chart].add(role)
    snapshots: dict[int, list[tuple[int, list[int], list[int], list[int]]]] = defaultdict(list)
    seen: set[tuple[int, int, tuple[int, ...]]] = set()
    counts = Counter()

    def capture(event: int, charts: set[int]) -> None:
        for c in sorted(charts):
            eligible = eligible_by_chart.get(c, [])
            if not eligible:
                continue
            bank = sorted(banks[c])
            if not bank:
                continue
            candidates = [g for g in eligible if not (set(bank) & groups_as_sets[g])]
            if not candidates:
                continue
            key = (event, c, tuple(bank))
            if key in seen:
                continue
            seen.add(key)
            snapshots[event].append((c, bank, [prefix[i] for i in bank], candidates))
            counts["changed_banks"] += 1
            counts["bank_group_contexts"] += len(candidates)

    # Entry cut.
    capture(-1, set(banks))
    for event, instruction in enumerate(w["program"]):
        op, a = instruction[:2]
        touched: set[int] = set()
        old = where[a]
        if old is not None:
            touched.add(old)
        if op == "ADD":
            b = int(instruction[2])
            need(where[a] == where[b] == int(instruction[3]), "source cochart ADD")
            prefix[a] ^= prefix[b]
        elif op == "MOVE":
            src, dst = int(instruction[2]), int(instruction[3])
            need(where[a] == src, "source MOVE chart")
            banks[src].remove(a)
            banks[dst].add(a)
            where[a] = dst
            touched.add(dst)
        elif op == "SWAP":
            b = int(instruction[2])
            touched.add(int(where[b]))
            banks[int(where[a])].remove(a)
            banks[int(where[b])].remove(b)
            where[a], where[b] = where[b], where[a]
            prefix[a], prefix[b] = prefix[b], prefix[a]
            banks[int(where[a])].add(a)
            banks[int(where[b])].add(b)
        elif op == "INIT":
            chart = int(instruction[2])
            prefix[a] = 0
            where[a] = chart
            banks[chart].add(a)
            touched.add(chart)
        elif op == "CLEAR":
            need(where[a] is not None, "CLEAR active owner")
            banks[int(where[a])].remove(a)
            where[a] = None
            prefix[a] = 0
        else:
            raise AssertionError(f"unexpected opcode {op}")
        capture(event, touched)

    need(where == list(map(int, w["final"])) + [None] * (total_fields - n), "public endpoints")
    for role, row in enumerate(prefix[:n]):
        expected = (1 << role) ^ ((1 << (role - 111)) if 111 <= role < 222 else 0)
        need(row == expected, "all 659-input endpoint rows")

    # Reverse map columns are packed output vectors.  At each reverse cut we
    # pair these with the independently stored forward bank rows.
    suffix: list[int] = [1 << i for i in range(n)] + [0] * (total_fields - n)
    rank_hist = Counter()
    examples = {"local_only": None, "helper_only": None}
    positive = []
    seen_contexts = 0
    for event in range(len(w["program"]) - 1, -2, -1):
        for c, bank, p_rows, group_ids in snapshots.get(event, []):
            s_cols = [suffix[i] for i in bank]
            for g in group_ids:
                ranks = one_context(p_rows, s_cols, group_masks[g], n)
                key = (ranks["delta_ab"] > 0, ranks["delta_helper"] > 0)
                rank_hist[str(key)] += 1
                seen_contexts += 1
                record = {
                    "event": event,
                    "chart": c,
                    "boundary": list(boundaries[g]),
                    "group_size": len(groups[g]),
                    **ranks,
                }
                if examples["local_only"] is None and key == (True, False):
                    examples["local_only"] = record
                if examples["helper_only"] is None and key == (False, True):
                    examples["helper_only"] = record
                if key == (True, True):
                    positive.append(record)
        if event >= 0:
            instruction = w["program"][event]
            op, a = instruction[:2]
            if op in ("INIT", "CLEAR"):
                suffix[a] = 0
            elif op == "ADD":
                suffix[int(instruction[2])] ^= suffix[a]
            elif op == "SWAP":
                b = int(instruction[2])
                suffix[a], suffix[b] = suffix[b], suffix[a]
            elif op == "MOVE":
                pass

    need(seen_contexts == 4521, "expected all eligible alternate-carrier contexts")
    need(counts["changed_banks"] == 3908, "expected changed-bank census")
    need(rank_hist.get("(False, True)", 0) == 0
         and rank_hist.get("(True, True)", 0) == 0,
         "every context has zero clean endpoint-pairing form")
    need(not positive, "no source context has both nonzero quotient images")
    need(examples["local_only"] is not None, "positive local-pairing negative control exists")

    # Tiny positive control for the criterion and exact dirty-entry algebra.
    # It is a scalar toy, not a selected-source witness.
    toy = one_context([1], [1], 1, 1)
    need(toy["delta_ab"] == toy["delta_helper"] == 1,
         "the criterion accepts a genuinely paired scalar channel")
    toy_rows = []
    dirty_clear_before_suffix_fails = False
    for x in (0, 1):
        for dirty in (0, 1):
            z, t = x, dirty
            t ^= z
            z ^= t
            t ^= z
            need((z, t) == (dirty, x), "three ADD layers are the exact dirty-state swap")
            delivered = z
            z = 0  # legal only after the suffix has delivered ``delivered`` elsewhere
            need((delivered, t) == (dirty, x) and z == 0,
                 "post-delivery scratch retirement preserves both outputs")
            if dirty:
                premature = 0  # CLEAR before suffix has delivered the carrier
                dirty_clear_before_suffix_fails |= premature != dirty
            toy_rows.append({"x": x, "dirty_carrier": dirty,
                             "split_output": [delivered, t]})
    need(dirty_clear_before_suffix_fails,
         "dirty nonzero control rejects premature CLEAR")

    result = {
        "status": "PASS_INDEPENDENT_RANK_BLOCK_SCREEN_NO_ALTERNATE_SPLIT",
        "canonical_head": PIN,
        "source_path": SOURCE,
        "source_sha256": SOURCE_SHA,
        "public_inputs_outputs": n,
        "owned_fields": int(w["owned_fields"]),
        "native_events": len(w["program"]),
        "groups": [
            {"boundary": list(boundaries[i]), "count": len(groups[i])}
            for i in range(len(groups))
        ],
        "eligible_charts": len(eligible_by_chart),
        "changed_bank_contexts": dict(counts),
        "pair_dimension_histogram": dict(rank_hist),
        "clean_endpoint_pairing_zero_in_all_contexts": True,
        "positive_multiplicity_extension": "For any finite V over F2, an admissible block row has each matrix coefficient in ker(A^T), and an admissible block column has each coefficient in ker(C). Since every scalar pairing a K b is zero, the lifted block pairing is a sum of zero coefficients times ordered products X_i Y_j; it is zero for arbitrary, possibly noncommuting, V×V coefficients.",
        "positive_candidates": positive,
        "negative_controls": {
            "local_pairing_alone_is_insufficient": examples["local_only"],
            "candidate_conditions_are_conjunctive": "A local a·b witness exists here (delta_ab>0), but delta_helper=0, so no a,b can satisfy both."
        },
        "algebra_controls": {
            "one_channel_positive_dimensions": toy,
            "dirty_truth_table": toy_rows,
            "premature_clear_rejected_for_dirty_one": dirty_clear_before_suffix_fails,
            "meaning": "The 3-ADD map is reversible on (bank, dirty carrier): (x,d)->(d,x). The carrier value d must reach its suffix output before CLEAR; an old completed output must remain in a distinct slot."
        },
        "proof_scope": "For every unchanged-word cut with C strictly nested between a helper group's common entrance A and exit D and with no original helper from that group in the C-bank, all F2 linear combinations of bank fields are covered. This excludes the stated alternate-carrier rank-one split at these cuts; it does not exclude changed source words or paid multi-frame boundaries.",
    }
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
