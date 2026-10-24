"""Check the signed clique code without producer imports or native replay."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
LANE = HERE.parents[1]
LANES = LANE.parent
ROOT = LANES.parents[2]
PRODUCER = LANE / "rational-code-admission-20261020"
SOURCES = {
    "flags": (
        LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json",
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    ),
    "response": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json",
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
    ),
    "native": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
        "7160a8764f0b12131e30dd1ca90a28b781b9dd99e8eb2f1935b8592aaf48037b",
    ),
    "literal": (
        PRODUCER / "verified-final-normal/CLIQUE-CODES.json",
        "0b30ecf807c99c0e3239136bca4d2db129765879dbfd09a25b4447fb7ef3ca3f",
    ),
    "scan_proof": (
        LANES / "independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md",
        "e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01",
    ),
}


def need(value, label):
    if not value:
        raise ValueError(label)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col) if x and y)
             for col in bt] for row in a]


def rank_mod(a, p):
    m = [[int(x.numerator * pow(x.denominator, -1, p)) % p
          for x in row] for row in a]
    r = 0
    for j in range(len(m[0])):
        hit = next((i for i in range(r, len(m)) if m[i][j]), None)
        if hit is None:
            continue
        m[r], m[hit] = m[hit], m[r]
        inv = pow(m[r][j], -1, p)
        m[r] = [x * inv % p for x in m[r]]
        for i in range(r + 1, len(m)):
            q = m[i][j]
            m[i] = [(x - q * y) % p for x, y in zip(m[i], m[r])]
        r += 1
        if r == len(m):
            break
    return r


def height(x, p):
    d, k = x.denominator, 0
    while d % p == 0:
        d //= p
        k += 1
    return k


def sparse_json(rows):
    return [[F(row.get(str(j), 0)) for j in range(len(rows))]
            for row in rows]


def factor(gate):
    if gate[0] == "NEG":
        return F(-1)
    if gate[0] == "SCALE2":
        return F(2) ** gate[2]
    if gate[0] == "MULTIPLY_ODD":
        return F(gate[2])
    need(gate[0] == "DIVIDE_ODD", "Known scalar gate")
    return F(1, gate[2])


def reverse_rows(word):
    """Accumulate output covectors from the last event to the first."""
    out = []
    for i in range(114):
        row = [F(i == j) for j in range(114)]
        for gate in reversed(word):
            t = gate[1]
            need(0 <= t < 112, "Only data targets")
            if gate[0] == "ADD":
                s, q = gate[2:]
                need(0 <= s < 112 and s != t and q in (-1, 1),
                     "Only distinct data sources")
                row[s] += q * row[t]
            else:
                row[t] *= factor(gate)
        out.append(row)
    return out


def prefix_replay(word, start, integral=False):
    rows = [row[:] for row in start]
    maxima = {p: 0 for p in (2, 5, 7)}
    norm = max(sum(abs(x) for x in row) for row in rows)
    add_operand_bound = F(0)
    divisions = 0
    for gate in word:
        t = gate[1]
        if gate[0] == "ADD":
            s, q = gate[2:]
            add_operand_bound = max(
                add_operand_bound,
                sum(abs(x) for x in rows[t]) + sum(abs(x) for x in rows[s]))
            rows[t] = [a + q * b for a, b in zip(rows[t], rows[s])]
        else:
            if integral and gate[0] == "DIVIDE_ODD":
                need(all(x.denominator == 1 and x.numerator % gate[2] == 0
                         for x in rows[t]), "Every odd division is exact")
                divisions += 1
            q = factor(gate)
            rows[t] = [q * x for x in rows[t]]
        if integral:
            need(all(x.denominator == 1 for x in rows[t]), "Integral prefix")
        norm = max(norm, sum(abs(x) for x in rows[t]))
        for p in maxima:
            maxima[p] = max(maxima[p], max(height(x, p) for x in rows[t]))
    return rows, {
        "stored_row_l1": str(norm),
        "unit_add_operand_l1": str(add_operand_bound),
        "height": maxima,
        "checked_odd_divisions": divisions,
    }


def scan_word(n, w, d, divide):
    """Use an independent two's-complement recurrence."""
    c, result = 0, 0
    for j in range(w):
        bit = (n >> j) & 1
        if divide:
            a = (bit ^ c) & 1
            c = (c + d * a - bit) // 2
        else:
            total = d * bit + c
            a, c = total & 1, total >> 1
        need(0 <= c < d, "Bounded finite carry")
        result |= a << j
    sign_in = int(n < 0)
    sign_out = result >> (w - 1)
    condition = d * sign_out - sign_in if divide else d * sign_in - sign_out
    return c == condition, result - (sign_out << w)


def typed_check():
    c, ci = eye(4), eye(4)
    c[0][:2], c[1][:2] = [F(1, 5), F(1, 35)], [F(0), F(1, 7)]
    ci[0][:2], ci[1][:2] = [F(5), F(-1)], [F(0), F(7)]
    need(mm(c, ci) == mm(ci, c) == eye(4), "Independent typed fixture inverse")
    frame, frame_inverse = eye(4), eye(4)
    frame[1][0], frame_inverse[1][0] = F(1, 2), F(-1, 2)
    codes = [eye(4), c, mm(frame, c)]
    inverse_codes = [eye(4), ci, mm(ci, frame_inverse)]
    need(mm(codes[1], codes[2]) != mm(codes[2], codes[1]),
         "Noncommuting rational boundary codes")
    state, semantic, old_type = eye(4), eye(4), 0
    peaks = {5: 0, 7: 0}
    for j in range(24):
        next_type = (j + 1) % 3
        a = eye(4)
        a[j % 2][(j + 1) % 2] = F(1 if j % 3 else -1, 2)
        a[j % 2][2 + j % 2] = F(1, 4)
        m = mm(codes[next_type], mm(a, inverse_codes[old_type]))
        state, semantic = mm(m, state), mm(a, semantic)
        need(state == mm(codes[next_type], semantic), "Typed endpoint on all columns")
        need(state[2:] == eye(4)[2:], "Arbitrary helpers have identity endpoint")
        for p in peaks:
            peaks[p] = max(peaks[p], max(height(x, p) for row in state for x in row))
            need(peaks[p] <= 1, "Typed height does not count completed siblings")
        old_type = next_type
    need(any(state[i][j] for i in range(2) for j in range(2, 4)),
         "The fixture reads arbitrary helper columns")
    bad = eye(4)
    for _ in range(8):
        bad = mm(c, bad)
    need(max(height(x, 5) for row in bad for x in row) == 8 and
         max(height(x, 7) for row in bad for x in row) == 8,
         "Unmatched physical repetition increases odd height")
    return {"completed_calls": 24, "maximum_typed_heights": peaks,
            "arbitrary_helpers_read": 2, "mismatched_height": 8}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    need(shutil.disk_usage(HERE).free >= 3 * 2**30, "Three GiB free")
    sources, pins = {}, {}
    for name, (path, expected) in SOURCES.items():
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == expected, "Pinned source " + name)
        pins[name] = {"path": str(path), "sha256": expected}
        if name == "native":
            raw = gzip.decompress(raw)
            digest = sha256(raw).hexdigest()
            need(digest == "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
                 "Native raw payload pin")
            pins[name]["payload_sha256"] = digest
        if name != "scan_proof":
            sources[name] = json.loads(raw)
    f, r, n, literal = [sources[k] for k in ("flags", "response", "native", "literal")]
    model = n["model"]
    a = eye(112)
    affected = []
    for pair in f["pair_codes"]:
        ports, block = pair["ports"], pair["matrix"]
        need(mm([[F(x) for x in row] for row in block],
                [[F(x) for x in col] for col in zip(*block)]) ==
             [[2 * x for x in row] for row in eye(2)], "Pair orthogonality")
        for port, row in zip(ports, block):
            a[port] = [F(0)] * 112
            for source, value in zip(ports, row):
                a[port][source] = F(value)
        affected += ports
    need(len(affected) == len(set(affected)) == 48, "Disjoint pair ports")
    need(sorted(affected) == f["affected_ports"], "Actual affected ports")
    signs = {}
    for item in r["vertex_assignments"]:
        group = f["cyclic_carriers"][item["vertex"]]
        need(set(group) == set(item["ordered_carriers_a_b_c"]), "Actual carrier group")
        signs.update(zip(item["ordered_carriers_a_b_c"], item["signs"]))
    need(len(signs) == 48 and sum(x == -1 for x in signs.values()) == 4,
         "Exactly four negative mode signs")
    groups = f["cyclic_carriers"] + model["small_cliques"]
    need([len(g) for g in groups] == [6] * 8 + [8] * 8, "Block sizes")
    need(sorted(x for group in groups for x in group) == list(range(112)),
         "Full port partition")
    need(model["vertex_assignments"] == r["vertex_assignments"],
         "Native signs match actual response")
    need(all(g in r["maximal_small_cliques"] for g in groups[8:]),
         "Small clique certificate")
    need(literal["pair_codes"] == f["pair_codes"] and
         literal["six_mode_blocks"] == groups[:8] and
         literal["eight_cliques"] == groups[8:] and
         {int(k): v for k, v in literal["mode_signs"].items()} == signs,
         "Literal metadata binds all source signs and groups")
    weights = [[sum(signs.get(p, 1) * a[p][j] for p in group)
                for j in range(112)] for group in groups]
    for g, wg in enumerate(weights):
        for h, wh in enumerate(weights):
            expected = (2 if g < 8 else 1) * len(groups[g]) if g == h else 0
            need(sum(x * y for x, y in zip(wg, wh)) == expected,
                 "Orthogonal signed source covectors")
    endpoints, old_response_differences = {}, {}
    for direction in ("forward", "inverse"):
        e = eye(112)
        for g, w in enumerate(weights):
            denominator = (2 if g < 8 else 1)
            if direction == "inverse":
                denominator *= len(groups[g]) - 1
            for i in range(112):
                if w[i]:
                    for j in range(112):
                        e[i][j] -= w[i] * w[j] / denominator
        key = "response" if direction == "forward" else "response_inverse"
        need(e == sparse_json(model[key]),
             "The frozen native matrix matches the outer-product construction")
        previous = sparse_json(r[key])
        old_response_differences[direction] = sum(
            e[i][j] != previous[i][j] for i in range(112) for j in range(112))
        endpoints[direction] = e
    need(mm(endpoints["forward"], endpoints["inverse"]) == eye(112) and
         mm(endpoints["inverse"], endpoints["forward"]) == eye(112),
         "Both source inverse orders")
    reports = {}
    for direction, word in literal["words"].items():
        target = eye(114)
        target[:112] = [row + [F(0), F(0)] for row in endpoints[direction]]
        need(reverse_rows(word) == target, "Reverse covector replay")
        actual, prefix = prefix_replay(word, eye(114))
        need(actual == target, "Forward prefix replay matches reverse replay")
        grid = 70
        initial = [[grid * x for x in row] for row in eye(114)]
        exact, integer = prefix_replay(word, initial, True)
        need(exact == [[grid * x for x in row] for row in target], "Generic exact grid")
        counts = Counter(g[0] for g in word)
        scalar = 8 * counts["ADD"] + 2 * (counts["NEG"] + counts["SCALE2"])
        need(counts["ADD"] == 384 and counts["NEG"] == 126 and
             counts["SCALE2"] == 48 and scalar == 3420, "Exact scalar invoice")
        need(sum(g[0] in ("MULTIPLY_ODD", "DIVIDE_ODD") for g in word) == 16,
             "Thirty-two real odd scans")
        need(prefix["height"][2] == 1 and prefix["stored_row_l1"] ==
             ("20" if direction == "forward" else "18"), "Exact prefix bounds")
        need(F(prefix["unit_add_operand_l1"]) <= 64, "Unit-ADD temporary bound")
        reports[direction] = {"event_count": len(word), "counts": dict(counts),
                              "old_real_scalar_units": scalar, "real_odd_scans": 32,
                              "prefix": prefix, "generic_grid": integer}
    valid = eye(114)
    valid[:112] = [row + [F(0), F(0)] for row in endpoints["forward"]]
    valid = [[4 * x for x in row] for row in valid]
    decoded, valid_bounds = prefix_replay(literal["words"]["inverse"], valid, True)
    need(decoded == [[4 * x for x in row] for row in eye(114)],
         "Valid-code inverse without an odd root scale")
    syndromes = {}
    for p, rows in ((5, weights[:8]), (7, weights[8:])):
        need(rank_mod(rows, p) == 8, "Surjective real syndrome rows")
        need(rank_mod(endpoints["forward"], p) == 104, "Exact reduced code image")
        image = mm(rows, endpoints["forward"])
        need(all(x.numerator % p == 0 for row in image for x in row),
             "Zero code image syndrome")
        syndromes[p] = {"syndrome_rank": 8, "image_rank": 104}
    scan_cases = 0
    for d in (5, 7, 35, 2145):
        for w in range(1, 13):
            lo, hi = -(1 << (w - 1)), (1 << (w - 1)) - 1
            for x in range(lo, hi + 1):
                ok, y = scan_word(x, w, d, True)
                need(ok == (x % d == 0), "Exact signed division accepts only multiples")
                if ok:
                    need(d * y == x, "Exact signed quotient")
                ok, y = scan_word(x, w, d, False)
                need(ok == (lo <= d * x <= hi), "Exact signed overflow decision")
                if ok:
                    need(y == d * x, "Exact signed product")
                scan_cases += 2
    principal = {}
    for name in ("ordinary_inverse", "selected_inverse", "selected_inverse_block"):
        if name in model:
            denominators = sorted({F(x).denominator for row in model[name] for x in row.values()})
            principal[name] = denominators
    receipt = {
        "status": "PASS_INDEPENDENT_SIGNED_CLIQUE_CODE_REVIEW",
        "sources": pins,
        "signed_pair_blocks": 24,
        "group_sizes": [len(g) for g in groups],
        "negative_mode_signs": 4,
        "all_data_columns": 112,
        "arbitrary_spectator_columns": 2,
        "response_rank_minus_identity": 16,
        "source_eigenvalues_and_multiplicities": {"1": 96, "-5": 8, "-7": 8},
        "determinant": str(35**8),
        "older_response_entry_differences": old_response_differences,
        "literal_word_checks": reports,
        "valid_code_binary_grid": 4,
        "valid_code_prefix": valid_bounds,
        "syndromes": syndromes,
        "signed_scan_cases": scan_cases,
        "independent_typed_fixture": typed_check(),
        "principal_inverse_denominators": principal,
        "scope": "Common-frame scalar code and source equality. No native, phase, controller, or recursive caller replay.",
    }
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps({"scans": scan_cases, "words": reports, "principal": principal}, sort_keys=True))


if __name__ == "__main__":
    main()
