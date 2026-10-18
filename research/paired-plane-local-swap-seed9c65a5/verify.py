#!/usr/bin/env python3
"""Reconstruct the best legal two-edge switch of the pinned plane matching."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ARCHIVE_PATH = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PAYLOAD_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
ARCHIVE_MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
SELECTED_SHA = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
CATALOG_SHA = "d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7"
SEED = "9c65a5d9c501b3f5185d52cd340a9579"
N = 9
PORTS = 112


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def check_source_pins() -> None:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    need(manifest["base_commit"] == BASE_COMMIT, "source manifest base commit")
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            need(path.is_file(), "missing pinned input: " + row["path"])
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                 "pinned input hash mismatch: " + row["path"])
    need(next(x for x in manifest["files"] if x["path"] == "certificates/selected-result.json")["sha256"] == SELECTED_SHA,
         "selected record pin")
    need(next(x for x in manifest["files"] if x["path"] == "docs/research/agent-task-catalog.json")["sha256"] == CATALOG_SHA,
         "task catalogue pin")


def load_labels() -> list[int]:
    archive = ARCHIVE_PATH.read_bytes()
    need(hashlib.sha256(archive).hexdigest() == ARCHIVE_SHA, "selected replay archive hash")
    with tarfile.open(ARCHIVE_PATH, "r:gz") as tf:
        member = tf.extractfile(ARCHIVE_MEMBER)
        need(member is not None, "selected DATA-PHASES entry missing")
        raw = member.read()
    need(hashlib.sha256(raw).hexdigest() == PAYLOAD_SHA, "selected DATA-PHASES payload hash")
    rows = json.loads(raw)["recipes"]
    rows = sorted(rows, key=lambda row: row["port"])
    need(len(rows) == PORTS and [r["port"] for r in rows] == list(range(PORTS)), "port order/count")
    labels = [r["q"] for r in rows]
    need(len(set(labels)) == PORTS and all(0 < q < (1 << N) for q in labels), "label support")
    need({q.bit_count() for q in labels} == {3, 7}, "selected label weights")
    return labels


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def legal_edge(q: list[int], i: int, j: int) -> bool:
    return i != j and dot(q[i], q[j]) == 0


def matrix_rank(m: int) -> int:
    a, b, c, d = ((m >> t) & 1 for t in range(4))
    return 0 if m == 0 else (2 if (a * d ^ b * c) else 1)


def solve_factorization(q: list[int], pairs: tuple[tuple[int, int], ...]) -> list[int] | None:
    """Solve sum_k A_k M_k A_k^T=I_9 over F2, with free variables zero."""
    columns = []
    for i, j in pairs:
        basis = (q[i], q[j])
        for a in range(2):
            for b in range(2):
                col = 0
                for r in range(N):
                    for c in range(N):
                        if ((basis[a] >> r) & 1) and ((basis[b] >> c) & 1):
                            col |= 1 << (r * N + c)
                columns.append(col)
    variables = len(columns)
    rhs_bit = 1 << variables
    variable_mask = rhs_bit - 1
    equations = []
    for output in range(N * N):
        row = 0
        for variable, column in enumerate(columns):
            if (column >> output) & 1:
                row |= 1 << variable
        if output // N == output % N:
            row |= rhs_bit
        equations.append(row)
    pivots: dict[int, int] = {}
    for original in equations:
        row = original
        while row & variable_mask:
            pivot = (row & variable_mask).bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
        if not row & variable_mask and row & rhs_bit:
            return None
    solution = 0
    for pivot in sorted(pivots):
        row = pivots[pivot]
        value = (row >> variables) & 1
        value ^= ((row & ((1 << pivot) - 1)) & solution).bit_count() & 1
        if value:
            solution |= 1 << pivot
    return [sum(((solution >> (4 * k + t)) & 1) << t for t in range(4))
            for k in range(len(pairs))]


def factor_rank_one(m: int) -> tuple[int, int]:
    for x in range(1, 4):
        for y in range(1, 4):
            packed = sum((((x >> a) & 1) * ((y >> b) & 1)) << (2 * a + b)
                         for a in range(2) for b in range(2))
            if packed == m:
                return x, y
    raise ValueError("rank-one 2x2 matrix has no outer-product factorization")


def port_support(q: list[int], vector: int) -> int:
    return sum(dot(label, vector) << t for t, label in enumerate(q))


def rank_f2(rows: list[int]) -> int:
    basis: dict[int, int] = {}
    for value in rows:
        row = value
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def rectangle_rank(q: list[int], left: int, right: int) -> int:
    cols = [j for j in range(len(q)) if (right >> j) & 1]
    rows = [i for i in range(len(q)) if (left >> i) & 1]
    packed = [sum(dot(q[i], q[j]) << c for c, j in enumerate(cols)) for i in rows]
    return rank_f2(packed)


def factor_costs(q: list[int], pairs: tuple[tuple[int, int], ...], matrices: list[int]):
    terms = []
    decoder_columns: list[tuple[int, int]] = []
    for index, ((i, j), m) in enumerate(zip(pairs, matrices)):
        rank = matrix_rank(m)
        if rank == 0:
            continue
        qi, qj = q[i], q[j]
        if rank == 1:
            x, y = factor_rank_one(m)
            left = (qi if x & 1 else 0) ^ (qj if x & 2 else 0)
            right = (qi if y & 1 else 0) ^ (qj if y & 2 else 0)
            support_left, support_right = port_support(q, left), port_support(q, right)
            decoder_columns.append((support_left, support_right))
        else:
            left0, left1 = port_support(q, qi), port_support(q, qj)
            row0 = ((m >> 0) & 1, (m >> 1) & 1)
            row1 = ((m >> 2) & 1, (m >> 3) & 1)
            right0 = (qi if row0[0] else 0) ^ (qj if row0[1] else 0)
            right1 = (qi if row1[0] else 0) ^ (qj if row1[1] else 0)
            support_left = left0 | left1
            support_right = port_support(q, right0) | port_support(q, right1)
            need(support_left == support_right, "invertible plane matrix changed support")
            decoder_columns.extend(((left0, port_support(q, right0)),
                                    (left1, port_support(q, right1))))
        charge = rectangle_rank(q, support_left, support_right)
        need(1 <= charge <= N, "unexpected exact support-pairing rank")
        terms.append({"pair_index": index, "ports": [i, j], "matrix_bits": m,
                      "matrix_rank": rank, "support_pairing_rank": charge})
    return terms, decoder_columns


def check_local_identity(q: list[int], pairs: tuple[tuple[int, int], ...], matrices: list[int]) -> None:
    total = [[0] * N for _ in range(N)]
    for (i, j), m in zip(pairs, matrices):
        basis = (q[i], q[j])
        for r in range(N):
            for c in range(N):
                value = 0
                for a in range(2):
                    for b in range(2):
                        value ^= (((m >> (2 * a + b)) & 1)
                                  & ((basis[a] >> r) & 1)
                                  & ((basis[b] >> c) & 1))
                total[r][c] ^= value
    need(total == [[int(r == c) for c in range(N)] for r in range(N)],
         "local tensor factorization is not I_9")


def check_full_factorization(q: list[int], columns: list[tuple[int, int]]) -> None:
    actual = [0] * len(q)
    for left, right in columns:
        for i in range(len(q)):
            if (left >> i) & 1:
                actual[i] ^= right
    expected = [sum(dot(q[i], q[j]) << j for j in range(len(q))) for i in range(len(q))]
    need(actual == expected, "full-port D T^T factorization differs from U U^T")


def apply_c_word(start: int, word: list[int]) -> tuple[dict[int, tuple[int, int]], int]:
    """Exact Gaussian-integer numerators for the pinned C_q operator word."""
    state: dict[int, tuple[int, int]] = {start: (1, 0)}
    for qv in word:
        following: dict[int, tuple[int, int]] = {}
        for address, (re, im) in state.items():
            old = following.get(address, (0, 0))
            following[address] = (old[0] + re - im, old[1] + re + im)
            moved = address ^ qv
            old = following.get(moved, (0, 0))
            following[moved] = (old[0] + re + im, old[1] + im - re)
        state = {address: pair for address, pair in following.items() if pair != (0, 0)}
    return state, 1 << len(word)


def check_plane_endpoint(q: list[int], pairs: tuple[tuple[int, int], ...]) -> int:
    checked = 0
    for i, j in pairs:
        qi, qj = q[i], q[j]
        need(dot(qi, qj) == 0 and qi != qj and (qi ^ qj) != 0,
             "paired plane is not an independent orthogonal basis")
        for start in range(1 << N):
            state, denominator = apply_c_word(start, [qi, qj, qi, qj])
            need(state == {start ^ qi ^ qj: (16, 0)} and denominator == 16,
                 f"dirty-state plane endpoint failed at pair {(i, j)}, start {start}")
            checked += 1
    return checked


def matrix_rank_histogram(matrices: list[int]) -> dict[str, int]:
    return {str(r): sum(matrix_rank(m) == r for m in matrices) for r in range(3)}


def enumerate_two_edge_switches(q, baseline):
    """Exhaust all 2*C(56,2) reconnections; retain only legal orthogonal edges."""
    possible = 2 * (len(baseline) * (len(baseline) - 1) // 2)
    seen: set[tuple[tuple[int, int], ...]] = set()
    cost_histogram: dict[int, int] = {}
    best_cost = None
    best_rows = []
    edge_rejected = 0
    inconsistent = 0
    for a in range(len(baseline)):
        i, j = baseline[a]
        for b in range(a + 1, len(baseline)):
            k, ell = baseline[b]
            for edge_a, edge_b in (((i, k), (j, ell)), ((i, ell), (j, k))):
                first, second = tuple(sorted(edge_a)), tuple(sorted(edge_b))
                if not (legal_edge(q, *first) and legal_edge(q, *second)):
                    edge_rejected += 1
                    continue
                candidate = list(baseline)
                candidate[a], candidate[b] = first, second
                candidate = tuple(candidate)
                need(candidate not in seen, "two switch descriptions produced duplicate matching")
                seen.add(candidate)
                matrices = solve_factorization(q, candidate)
                if matrices is None:
                    inconsistent += 1
                    continue
                check_local_identity(q, candidate, matrices)
                terms, _ = factor_costs(q, candidate, matrices)
                charge = sum(row["support_pairing_rank"] for row in terms)
                cost_histogram[charge] = cost_histogram.get(charge, 0) + 1
                if best_cost is None or charge < best_cost:
                    best_cost, best_rows = charge, [(candidate, matrices, terms)]
                elif charge == best_cost:
                    best_rows.append((candidate, matrices, terms))
    need(len(seen) + edge_rejected == possible, "two-switch domain accounting")
    return {"possible": possible, "edge_rejected": edge_rejected, "legal": len(seen),
            "inconsistent": inconsistent, "cost_histogram": dict(sorted(cost_histogram.items())),
            "best_cost": best_cost, "best_count": len(best_rows), "best_rows": best_rows}


def load_ceiling_module():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    need(spec is not None and spec.loader is not None, "cannot load pinned ceiling module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_screen(profile: dict[int, int]) -> dict:
    module = load_ceiling_module()
    selected = json.loads((ROOT / "research/complex-local-word-ceiling/RESULT.json").read_text())
    target = Q(selected["selected"]["complex_lower"])
    lo, hi = module.ceiling(profile, 73, 896, 9, centre=96,
                            grid=Q(1, 10**12), unpaid=2)
    need((lo, hi) == (Q(4864733253, 10**12), Q(2432366627, 500_000_000_000)),
         "candidate complex-side ceiling bracket")
    additions = {}
    for n in (67, 68):
        enlarged = dict(profile)
        enlarged[1] += n
        relax_lo, relax_hi = module.relax(enlarged, 73, 896, 9, 96 + n, target, unpaid=2)
        additions[str(n)] = {"relaxation_lo": str(relax_lo), "relaxation_hi": str(relax_hi),
                             "passes_selected_complex_lower": relax_hi < 1,
                             "fails_selected_complex_lower": relax_lo > 1}
    need(additions["67"]["passes_selected_complex_lower"], "67-unit planning positive control")
    need(additions["68"]["fails_selected_complex_lower"], "68-unit planning threshold control")
    kappa = hi / (1 + hi)
    return {"local_profile_per_call": {str(r): n for r, n in sorted(profile.items())},
            "unpaid_coordinates": 2, "centre_charge": 96, "a_lo": str(lo), "a_hi": str(hi),
            "kappa_planning_cap": str(kappa), "selected_complex_lower": str(target),
            "rank_one_plus_centre_budget": additions,
            "interpretation": "favorable selected-complex-side relaxation only; no supplier, scalar decoder, or assembly claim"}


def check_negative_controls(q, pairs, matrices, terms, columns) -> dict:
    nonedges = [(i, j) for i in range(len(q)) for j in range(i + 1, len(q))
                if not legal_edge(q, i, j)]
    need(bool(nonedges), "nonedge negative control unavailable")
    i, j = nonedges[0]
    need(not legal_edge(q, i, j), "wrong-pair nonedge unexpectedly legal")

    dropped = columns[:-matrix_rank(next(m for m in reversed(matrices) if m))]
    actual = [0] * len(q)
    for left, right in dropped:
        for t in range(len(q)):
            if (left >> t) & 1:
                actual[t] ^= right
    expected = [sum(dot(q[t], q[u]) << u for u in range(len(q))) for t in range(len(q))]
    need(actual != expected, "omitted active term did not break full factorization")

    changed = list(matrices)
    k = next(k for k, value in enumerate(changed) if value)
    changed[k] ^= 1
    try:
        check_local_identity(q, pairs, changed)
    except ValueError:
        pass
    else:
        raise ValueError("mutated matrix negative control passed")

    a, b = pairs[0]
    uncorrected, denominator = apply_c_word(0, [q[a], q[b], q[a], q[b]])
    need(uncorrected != {0: (denominator, 0)}, "omitted translation control passed")
    return {"illegal_edge_rejected": True, "omitted_active_term_breaks_factorization": True,
            "mutated_matrix_breaks_local_identity": True,
            "omitted_plane_translation_breaks_endpoint": True,
            "baseline_cost_exceeds_candidate": sum(t["support_pairing_rank"] for t in terms) < 126}


def build_certificate(q, search, baseline, base_matrices, pairs, matrices, terms,
                      endpoint_checks, controls, profile, screen):
    return {
        "schema_version": 1,
        "seed": SEED,
        "base_commit": BASE_COMMIT,
        "selected_record_sha256": SELECTED_SHA,
        "selected_archive_sha256": ARCHIVE_SHA,
        "selected_payload_sha256": PAYLOAD_SHA,
        "port_count": PORTS,
        "label_space_dimension": N,
        "edge_rule": "i != j and parity(q_i dot q_j)=0",
        "baseline_matching": [list(pair) for pair in baseline],
        "baseline_plane_matrix_rows": base_matrices,
        "baseline_copy_charge": 126,
        "search_domain": {k: search[k] for k in ("possible", "edge_rejected", "legal", "inconsistent")},
        "cost_histogram": {str(k): v for k, v in search["cost_histogram"].items()},
        "minimum_copy_charge": search["best_cost"],
        "minimum_count": search["best_count"],
        "matching": [list(pair) for pair in pairs],
        "plane_translation_labels": [q[i] ^ q[j] for i, j in pairs],
        "plane_matrix_rows": matrices,
        "plane_matrix_rank_histogram": matrix_rank_histogram(matrices),
        "active_terms": terms,
        "active_matrix_count": len(terms),
        "copy_rank_histogram": {str(r): sum(t["support_pairing_rank"] == r for t in terms)
                                for r in (7, 8, 9)},
        "copy_charge": sum(t["support_pairing_rank"] for t in terms),
        "exact_dirty_basis_states_checked": endpoint_checks,
        "negative_controls": controls,
        "complex_side_screen": screen,
        "local_profile_per_call": {str(r): n for r, n in sorted(profile.items())},
        "scope_limit": "one exact two-edge-switch neighborhood of the pinned deterministic matching"
    }


def build_result(certificate):
    return {
        "schema_version": 1,
        "status": "completed finite local construction optimization; scalar decoder and supplier integration remain open",
        "track": "recursive-interfaces",
        "task_id": "coverage-law-change",
        "priority_revision": 4,
        "seed": SEED,
        "catalog_sha256": CATALOG_SHA,
        "base_commit": BASE_COMMIT,
        "selected_record_sha256": SELECTED_SHA,
        "construction": {
            "mathematical_object": "B14 copy invoice of a paired-plane F2 factorization over the selected 112-port label family",
            "changed_expense": "replace two edges of the canonical zero-dot perfect matching and refactor sum A_k M_k A_k^T=I_9",
            "baseline_copy_charge": 126,
            "candidate_copy_charge": certificate["copy_charge"],
            "absolute_reduction": 126 - certificate["copy_charge"],
            "relative_reduction": "5/21",
            "minimum_count_in_searched_domain": certificate["minimum_count"],
            "candidate_active_terms": certificate["active_matrix_count"],
            "candidate_plane_matrix_rank_histogram": certificate["plane_matrix_rank_histogram"],
            "candidate_copy_rank_histogram": certificate["copy_rank_histogram"],
            "matching": certificate["matching"],
            "plane_matrix_rows": certificate["plane_matrix_rows"]
        },
        "search": certificate["search_domain"] | {"cost_histogram": certificate["cost_histogram"]},
        "local_profile_per_call": certificate["local_profile_per_call"],
        "complex_side_screen": certificate["complex_side_screen"],
        "interpretation": "The factorization is not a scalar masked-plane decoder. No new supplier or selected kappa is established.",
        "predecessor": "research/paired-plane-port-matching-seed6c563a",
        "attribution": "Substantial OpenAI Codex assistance; no independent human review or formal proof assistant is claimed."
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-artifacts", action="store_true",
                        help="write the deterministically reconstructed CERTIFICATE.json and RESULT.json")
    args = parser.parse_args()
    check_source_pins()
    q = load_labels()
    predecessor = json.loads((ROOT / "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json").read_text())
    baseline = tuple(tuple(pair) for pair in predecessor["matching"])
    need(len(baseline) == 56 and len({v for pair in baseline for v in pair}) == PORTS,
         "pinned predecessor matching shape")
    need(all(legal_edge(q, *pair) for pair in baseline), "pinned predecessor has illegal edge")
    base_matrices = solve_factorization(q, baseline)
    need(base_matrices == predecessor["plane_matrices_2bit_rows"], "predecessor matrix reconstruction")
    check_local_identity(q, baseline, base_matrices)
    base_terms, _ = factor_costs(q, baseline, base_matrices)
    base_charge = sum(t["support_pairing_rank"] for t in base_terms)
    need(base_charge == 126, "pinned predecessor baseline cost")

    search = enumerate_two_edge_switches(q, baseline)
    need(search["possible"] == 3080 and search["edge_rejected"] == 2414
         and search["legal"] == 666 and search["inconsistent"] == 0,
         "complete two-edge-switch search counts")
    need(search["best_cost"] == 96 and search["best_count"] == 1,
         "unique best copy charge in searched domain")
    pairs, matrices, terms = search["best_rows"][0]
    need(pairs[31:33] == ((87, 90), (42, 44)), "best switch edge receipt")
    need(matrices == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 8, 6, 6, 0, 0, 0, 0,
                      0, 0, 6, 8, 0, 0, 0, 0, 0, 8, 14, 0, 0, 0, 14, 0, 1,
                      15, 0, 15], "best 2x2 matrix receipt")
    need(matrix_rank_histogram(matrices) == {"0": 44, "1": 7, "2": 5}, "candidate plane ranks")
    need({str(r): sum(t["support_pairing_rank"] == r for t in terms) for r in (7, 8, 9)}
         == {"7": 5, "8": 2, "9": 5}, "candidate support-rank histogram")
    check_full_factorization(q, factor_costs(q, pairs, matrices)[1])
    endpoint_checks = check_plane_endpoint(q, pairs)
    need(endpoint_checks == 28_672, "candidate dirty endpoint coverage")

    predecessor_profile = json.loads((ROOT / "research/complex-local-word-ceiling/RESULT.json").read_text())
    old = {int(r): n for r, n in predecessor_profile["selected"]["local_profile_per_call"].items()}
    need(old == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "pinned selected local profile")
    profile = dict(old)
    del profile[8]
    for rank in (7, 8, 9):
        profile[rank] = sum(t["support_pairing_rank"] == rank for t in terms)
    need(profile == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 7: 5, 8: 2, 9: 5},
         "candidate local profile splice")
    screen = make_screen(profile)
    controls = check_negative_controls(q, pairs, matrices, terms, factor_costs(q, pairs, matrices)[1])
    certificate = build_certificate(q, search, baseline, base_matrices, pairs, matrices, terms,
                                    endpoint_checks, controls, profile, screen)
    result = build_result(certificate)
    cert_path, result_path = PACKAGE / "CERTIFICATE.json", PACKAGE / "RESULT.json"
    if args.write_artifacts:
        cert_path.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
        result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        need(cert_path.is_file() and json.loads(cert_path.read_text()) == certificate,
             "CERTIFICATE.json differs from exact reconstruction")
        need(result_path.is_file() and json.loads(result_path.read_text()) == result,
             "RESULT.json differs from exact reconstruction")
    print("PASS_PAIRED_PLANE_LOCAL_TWO_EDGE_SWITCH")
    print("possible=3080 edge_valid=666 inconsistent=0 unique_minimum=96 baseline=126")
    print("copy_rank_histogram={7:5,8:2,9:5} dirty_basis_states=28672 controls=5")
    print(f"complex_ceiling_a_hi={screen['a_hi']} planning_kappa_cap={screen['kappa_planning_cap']}")


if __name__ == "__main__":
    main()
