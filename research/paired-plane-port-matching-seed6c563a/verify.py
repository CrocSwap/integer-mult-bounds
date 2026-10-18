#!/usr/bin/env python3
"""Exact bounded certificate for the paired-plane E8 port factorization."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
LOCAL_RESULT = ROOT / "research/complex-local-word-ceiling/RESULT.json"
ARCHIVE_ENTRY = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PAYLOAD_SHA256 = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
N = 9
PORTS = 112


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_input_pins() -> None:
    source_manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    need(source_manifest["base_commit"] == "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
         "source-manifest base commit")
    for row in source_manifest["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                 "live input hash mismatch: " + row["path"])


def load_ports() -> list[int]:
    archive = ARCHIVE.read_bytes()
    need(hashlib.sha256(archive).hexdigest() == ARCHIVE_SHA256, "selected replay archive hash")
    with tarfile.open(ARCHIVE, "r:gz") as tf:
        member = tf.extractfile(ARCHIVE_ENTRY)
        need(member is not None, "selected DATA-PHASES entry missing")
        payload = member.read()
    need(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA256, "selected DATA-PHASES payload hash")
    data = json.loads(payload)
    recipes = sorted(data["recipes"], key=lambda row: row["port"])
    need(data["ports"] == PORTS and len(recipes) == PORTS, "selected port count")
    need([row["port"] for row in recipes] == list(range(PORTS)), "selected port ordering")
    q = [row["q"] for row in recipes]
    need(len(set(q)) == PORTS, "port labels are not distinct")
    need(all(0 < v < (1 << N) for v in q), "label is not a nonzero 9-bit vector")
    need({v.bit_count() for v in q} == {3, 7}, "unexpected selected label weights")
    return q


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def edge(a: int, b: int) -> bool:
    return a != b and dot(a, b) == 0


def deterministic_matching(q: list[int]) -> tuple[tuple[int, int], ...]:
    """MRV backtracking, vertex-index and neighbor-index tie breaks."""
    adjacency = [[j for j, other in enumerate(q) if edge(value, other)]
                 for i, value in enumerate(q)]
    need({len(neighbors) for neighbors in adjacency} == {52}, "unexpected selected graph degree")
    dead: set[int] = set()

    def visit(mask: int):
        if not mask:
            return ()
        if mask in dead:
            return None
        remaining = [i for i in range(len(q)) if (mask >> i) & 1]
        i = min(remaining, key=lambda v: (sum((mask >> j) & 1 for j in adjacency[v]), v))
        for j in adjacency[i]:
            if (mask >> j) & 1:
                suffix = visit(mask ^ (1 << i) ^ (1 << j))
                if suffix is not None:
                    return ((i, j),) + suffix
        dead.add(mask)
        return None

    answer = visit((1 << len(q)) - 1)
    need(answer is not None and len(answer) * 2 == len(q), "no perfect matching found")
    need(all(edge(q[i], q[j]) for i, j in answer), "matching contains a non-edge")
    need(sorted(v for pair in answer for v in pair) == list(range(len(q))), "matching does not cover ports")
    return answer


def solve_plane_matrices(q: list[int], pairs: tuple[tuple[int, int], ...]) -> list[int]:
    """Solve sum A_k M_k A_k^T=I over F2; free variables are zero.

    Equations are bit-packed. Each row pivots on its highest variable index;
    back-substitution is in increasing pivot order. This fixes one reproducible
    certificate without making an optimality claim about the chosen solution.
    """
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
    nvars = len(columns)
    rhs_bit = 1 << nvars
    equations = []
    for out in range(N * N):
        row = 0
        for var, column in enumerate(columns):
            if (column >> out) & 1:
                row |= 1 << var
        if out // N == out % N:
            row |= rhs_bit
        equations.append(row)

    variable_mask = rhs_bit - 1
    basis_rows: dict[int, int] = {}
    for original in equations:
        row = original
        while row & variable_mask:
            pivot = (row & variable_mask).bit_length() - 1
            if pivot in basis_rows:
                row ^= basis_rows[pivot]
            else:
                basis_rows[pivot] = row
                break
        if not row & variable_mask:
            need(not (row & rhs_bit), "plane factorization system is inconsistent")

    solution = 0
    for pivot in sorted(basis_rows):
        row = basis_rows[pivot]
        value = (row >> nvars) & 1
        lower = row & ((1 << pivot) - 1)
        value ^= (lower & solution).bit_count() & 1
        if value:
            solution |= 1 << pivot
    matrices = []
    for k in range(len(pairs)):
        m = sum(((solution >> (4 * k + t)) & 1) << t for t in range(4))
        matrices.append(m)
    need(sum(m != 0 for m in matrices) == 16, "active plane count")
    need(sum(rank2(m) == 1 for m in matrices) == 9, "rank-one plane count")
    need(sum(rank2(m) == 2 for m in matrices) == 7, "rank-two plane count")
    need(sum(rank2(m) == 0 for m in matrices) == 40, "zero plane count")
    return matrices


def rank2(m: int) -> int:
    a, b, c, d = ((m >> t) & 1 for t in range(4))
    return 0 if m == 0 else (2 if (a * d ^ b * c) else 1)


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


def port_vector(q: list[int], v: int) -> int:
    return sum(dot(label, v) << t for t, label in enumerate(q))


def rank_b0_rectangle(q: list[int], rows: int, columns: int) -> int:
    row_indices = [i for i in range(len(q)) if (rows >> i) & 1]
    col_indices = [j for j in range(len(q)) if (columns >> j) & 1]
    packed = []
    for i in row_indices:
        packed.append(sum(dot(q[i], q[j]) << col for col, j in enumerate(col_indices)))
    return rank_f2(packed)


def factor_rank_one(m: int) -> tuple[int, int]:
    for x in range(1, 4):
        for y in range(1, 4):
            candidate = sum((((x >> a) & 1) * ((y >> b) & 1)) << (2 * a + b)
                            for a in range(2) for b in range(2))
            if candidate == m:
                return x, y
    raise ValueError("rank-one matrix did not factor")


def term_data(q: list[int], pairs: tuple[tuple[int, int], ...], matrices: list[int]):
    terms = []
    decoder_columns: list[tuple[int, int]] = []
    for index, ((i, j), m) in enumerate(zip(pairs, matrices)):
        rank = rank2(m)
        if not rank:
            continue
        qi, qj = q[i], q[j]
        if rank == 1:
            x, y = factor_rank_one(m)
            left = (qi if x & 1 else 0) ^ (qj if x & 2 else 0)
            right = (qi if y & 1 else 0) ^ (qj if y & 2 else 0)
            support_l, support_r = port_vector(q, left), port_vector(q, right)
            decoder_columns.append((support_l, support_r))
        else:
            left0, left1 = port_vector(q, qi), port_vector(q, qj)
            mrow0 = ((m >> 0) & 1, (m >> 1) & 1)
            mrow1 = ((m >> 2) & 1, (m >> 3) & 1)
            right0 = (qi if mrow0[0] else 0) ^ (qj if mrow0[1] else 0)
            right1 = (qi if mrow1[0] else 0) ^ (qj if mrow1[1] else 0)
            support_l = left0 | left1
            support_r = port_vector(q, right0) | port_vector(q, right1)
            need(support_l == support_r, "invertible M changed plane support")
            decoder_columns.extend(((left0, port_vector(q, right0)),
                                    (left1, port_vector(q, right1))))
        copy_rank = rank_b0_rectangle(q, support_l, support_r)
        need(copy_rank == (7 if rank == 1 else 9), "unexpected support pairing rank")
        terms.append({"pair_index": index, "ports": [i, j], "M_bits": m,
                      "matrix_rank": rank, "support_pairing_rank": copy_rank})
    return terms, decoder_columns


def identity_factorization(q: list[int], pairs: tuple[tuple[int, int], ...], matrices: list[int]) -> None:
    local = [[0] * N for _ in range(N)]
    for (i, j), m in zip(pairs, matrices):
        basis = (q[i], q[j])
        for r in range(N):
            for c in range(N):
                value = 0
                for a in range(2):
                    for b in range(2):
                        value ^= ((m >> (2 * a + b)) & 1) & ((basis[a] >> r) & 1) & ((basis[b] >> c) & 1)
                local[r][c] ^= value
    need(local == [[int(r == c) for c in range(N)] for r in range(N)], "sum A M A^T != I_9")


def full_decoder_identity(q: list[int], decoder_columns: list[tuple[int, int]]) -> None:
    actual = [0] * len(q)
    for left, right in decoder_columns:
        for t in range(len(q)):
            if (left >> t) & 1:
                actual[t] ^= right
    expected = [sum(dot(q[t], q[u]) << u for u in range(len(q))) for t in range(len(q))]
    need(actual == expected, "full 112 by 112 D T^T != U U^T")


def apply_c_sequence(start: int, sequence: list[int]) -> tuple[dict[int, tuple[int, int]], int]:
    """Exact Gaussian-integer numerator vector for a sequence of C_q operators."""
    state: dict[int, tuple[int, int]] = {start: (1, 0)}
    for qv in sequence:
        nxt: dict[int, tuple[int, int]] = {}
        for address, (re, im) in state.items():
            a = nxt.get(address, (0, 0))
            nxt[address] = (a[0] + re - im, a[1] + re + im)
            moved = address ^ qv
            b = nxt.get(moved, (0, 0))
            nxt[moved] = (b[0] + re + im, b[1] + im - re)
        state = {address: value for address, value in nxt.items() if value != (0, 0)}
    return state, 1 << len(sequence)


def exact_plane_endpoint(q: list[int], pairs: tuple[tuple[int, int], ...]) -> int:
    checked = 0
    for i, j in pairs:
        qi, qj = q[i], q[j]
        need(dot(qi, qj) == 0, "plane basis is not orthogonal")
        need(qi != qj and (qi ^ qj) != 0, "plane basis is dependent")
        for start in range(1 << N):
            state, denominator = apply_c_sequence(start, [qi, qj, qi, qj])
            target = start ^ qi ^ qj
            need(denominator == 16 and state == {target: (16, 0)},
                 f"exact dirty-state plane correction failed at pair {(i, j)}, state {start}")
            checked += 1
    return checked


def negative_controls(q, pairs, matrices, decoder_columns):
    # A changed partner must fail the perfect-matching edge predicate.
    i, j = pairs[0]
    alternatives = [k for k in range(len(q)) if k not in (i, j) and not edge(q[i], q[k])]
    need(bool(alternatives), "no non-edge negative control available")
    need(not edge(q[i], q[alternatives[0]]), "wrong-pair control unexpectedly legal")

    # Dropping the final complete active plane query must break the identity.
    need(bool(decoder_columns), "no decoder term for omission control")
    final_active_rank = rank2(next(m for m in reversed(matrices) if m))
    dropped = decoder_columns[:-final_active_rank]
    rows = [0] * len(q)
    for left, right in dropped:
        for t in range(len(q)):
            if (left >> t) & 1:
                rows[t] ^= right
    target_rows = [sum(dot(q[t], q[u]) << u for u in range(len(q))) for t in range(len(q))]
    need(rows != target_rows, "omitted-term control did not break decoder")

    # Flipping any active M coefficient must break the local tensor identity.
    changed = list(matrices)
    k = next(k for k, m in enumerate(changed) if m)
    changed[k] ^= 1
    try:
        identity_factorization(q, pairs, changed)
    except ValueError:
        pass
    else:
        raise ValueError("mutated-M negative control unexpectedly passed")

    # Without the required address translation, C_E^2 is not the identity endpoint.
    uncorrected, denominator = apply_c_sequence(0, [q[i], q[j], q[i], q[j]])
    need(uncorrected != {0: (denominator, 0)}, "omitted plane-translation correction control passed")
    return 4


def ceiling_screen(profile: dict[int, int]) -> dict:
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    grid = Fraction(1, 10**12)
    lo, hi = module.ceiling(profile, 73, 896, 9, centre=126, unpaid=2, grid=grid)
    need((lo, hi) == (Fraction(3447203500, 10**12), Fraction(3447203501, 10**12)),
         "changed-law ceiling bracket")
    kappa = hi / (1 + hi)
    return {"a_lo": str(lo), "a_hi": str(hi), "kappa_planning_cap_exact": str(kappa),
            "kappa_planning_cap_decimal_12": f"{float(kappa):.12f}",
            "model": {"m": 73, "families": 896, "stages": 9, "unpaid": 2, "centre": 126,
                      "idle_rank_cap": module.max_idle_rank(73)}}


def changed_local_profile(terms):
    result = json.loads(LOCAL_RESULT.read_text(encoding="utf-8"))
    selected = result["selected"]["local_profile_per_call"]
    old = {int(rank): count for rank, count in selected.items()}
    need(old == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
         "pinned selected local profile changed")
    profile = dict(old)
    del profile[8]
    profile[7] = sum(t["support_pairing_rank"] == 7 for t in terms)
    profile[9] = sum(t["support_pairing_rank"] == 9 for t in terms)
    need(profile == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 7: 9, 9: 7},
         "paired-plane replacement profile")
    return profile


def build_certificate(q, pairs, matrices, terms, endpoint_states, controls, screen):
    return {
        "schema_version": 1,
        "selected_archive_sha256": ARCHIVE_SHA256,
        "selected_payload_sha256": PAYLOAD_SHA256,
        "port_count": len(q),
        "label_space_dimension": N,
        "edge_rule": "i != j and parity(q_i dot q_j)=0",
        "matching": [list(pair) for pair in pairs],
        "plane_translation_labels": [q[i] ^ q[j] for i, j in pairs],
        "matching_degree": 52,
        "plane_matrices_2bit_rows": matrices,
        "plane_matrix_rank_histogram": {"0": matrices.count(0),
                                         "1": sum(rank2(m) == 1 for m in matrices),
                                         "2": sum(rank2(m) == 2 for m in matrices)},
        "active_query_terms": terms,
        "copy_charge": sum(t["support_pairing_rank"] for t in terms),
        "copy_rank_histogram": {"7": sum(t["support_pairing_rank"] == 7 for t in terms),
                                "9": sum(t["support_pairing_rank"] == 9 for t in terms)},
        "exact_dirty_basis_states_checked": endpoint_states,
        "negative_controls_rejected": controls,
        "ceiling_screen": screen
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-certificate", action="store_true",
                        help="write the deterministic computed certificate to CERTIFICATE.json")
    args = parser.parse_args()
    check_input_pins()
    q = load_ports()
    pairs = deterministic_matching(q)
    matrices = solve_plane_matrices(q, pairs)
    identity_factorization(q, pairs, matrices)
    terms, decoder_columns = term_data(q, pairs, matrices)
    full_decoder_identity(q, decoder_columns)
    need(sum(row["support_pairing_rank"] for row in terms) == 126, "copy charge must be 126")
    endpoint_states = exact_plane_endpoint(q, pairs)
    controls = negative_controls(q, pairs, matrices, decoder_columns)
    profile = changed_local_profile(terms)
    screen = ceiling_screen(profile)
    calculated = build_certificate(q, pairs, matrices, terms, endpoint_states, controls, screen)
    cert_path = PACKAGE / "CERTIFICATE.json"
    if args.emit_certificate:
        cert_path.write_text(json.dumps(calculated, indent=2) + "\n", encoding="utf-8")
    else:
        need(cert_path.is_file(), "CERTIFICATE.json missing; use --emit-certificate once")
        stored = json.loads(cert_path.read_text(encoding="utf-8"))
        # Search-state counts are deliberately not part of the stable certificate.
        need(stored == calculated, "stored certificate differs from exact reconstruction")
    print("PASS_PAIRED_PLANE_PORT_MATCHING")
    print(f"matching_edges={len(pairs)} active_queries={len(terms)} copy_charge={sum(t['support_pairing_rank'] for t in terms)}")
    print(f"query_ranks={{7:{sum(t['support_pairing_rank'] == 7 for t in terms)},9:{sum(t['support_pairing_rank'] == 9 for t in terms)}}}")
    print(f"dirty_basis_states={endpoint_states} negative_controls={controls}")
    print(f"complex_relaxation_a_hi={screen['a_hi']} kappa_planning_cap={screen['kappa_planning_cap_decimal_12']}")


if __name__ == "__main__":
    main()
