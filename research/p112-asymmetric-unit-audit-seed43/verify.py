"""Exact standard-library replay of the fixed P112 d0=77 asymmetric unit."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
KAPPA = "836330098538459/500000000000000000"
SEED = 43


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def bits9(value):
    return [(value >> (8 - j)) & 1 for j in range(9)]


def f2_rank(matrix):
    basis = {}
    for row in matrix:
        value = sum((int(bit) & 1) << j for j, bit in enumerate(row))
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def matrix_sha(matrix):
    return sha(canonical(matrix))


def make_B(source_labels, lines, sink_words):
    sinks = [source_labels[line] for line in lines]
    relaxed = {}
    for line, word in zip((74, 77), sink_words):
        relaxed[line] = bits9(word)
    rows = []
    for line, sink in zip(lines, sinks):
        w = relaxed.get(line, sink)
        rows.append([dot(w, source_labels[s]) & 1 for s in lines])
    return rows


def make_N(L, G, lines, d, e, mus, q_sources):
    alpha = {s: -dot(L[s], d) for s in q_sources}
    result = [[Fraction(G[t][s], 2) for s in lines] for t in lines]
    for line in (74, 77):
        mu = mus[line]
        vec = [Fraction(d[i]) + mu * e[i] for i in range(8)]
        result[lines.index(line)] = [
            sum(Fraction(L[s][i]) * vec[i] for i in range(8)) + alpha.get(s, 0)
            for s in lines
        ]
    return result


def exact_endpoint(B, N):
    n = len(B)
    return all(B[t][t] == 1 and N[t][t] != 0
               and all(t == s or B[t][s] == 0 or N[t][s] == 0 for s in range(n))
               for t in range(n))


def copy_costs(B, L, lines, relaxed, q_sources):
    relaxed_local = {lines.index(x) for x in relaxed}
    beta_alpha = f2_rank([[B[t][lines.index(s)] for s in q_sources] for t in sorted(relaxed_local)])
    beta_coord = []
    for a in range(8):
        readers = [t for t, line in enumerate(lines) if L[line][a] != 0 or t in relaxed_local]
        sources = [s for s, line in enumerate(lines) if L[line][a] != 0]
        beta_coord.append(f2_rank([[B[t][s] for s in sources] for t in readers]))
    return beta_coord, beta_alpha


def compute():
    deps = json.loads((HERE / "DEPENDENCIES.json").read_bytes())
    need(deps["schema_version"] == 1 and deps["base_commit"] == BASE, "dependency base")
    need(deps["assignment_seed"] == SEED and deps["d0_line"] == 77, "assignment pins")
    for path, expected in deps["base_files"].items():
        raw = (ROOT / path).read_bytes()
        need(sha(raw) == expected["sha256"], "base source SHA " + path)
        need(git_blob(raw) == expected["git_blob"], "base source Git blob " + path)
    input_raw = (HERE / "INPUTS.json").read_bytes()
    need(sha(input_raw) == deps["inputs_sha256"] and git_blob(input_raw) == deps["inputs_git_blob"],
         "pinned E8 input data")
    data = json.loads(input_raw)
    L, U = data["L"], data["U9"]
    lines = data["witness"]["P112_lines"]
    need(len(L) == len(U) == 120 and all(len(row) == 8 for row in L)
         and all(len(row) == 9 for row in U), "120 E8 lines and labels")
    need(lines == list(range(8, 120)), "P112 uses exactly the 112 Hamming-code lines")
    G = []
    for i in range(120):
        row = []
        for j in range(120):
            raw = dot(L[i], L[j])
            need(raw % 2 == 0, "E8 Gram entries are even")
            row.append(raw // 2)
        G.append(row)
    need(all(G[i][i] == 2 for i in range(120)), "E8 line norm")
    need(all((dot(U[i], U[j]) - (1 + G[i][j])) % 2 == 0
             for i in range(120) for j in range(120)), "U9 labels realize (J+G) mod 2")

    e_line, d0 = data["witness"]["e_line"], data["witness"]["d0_line"]
    relaxed, sink_words = data["witness"]["relaxed_lines"], data["witness"]["sink_words"]
    need((e_line, d0, relaxed, sink_words) == (0, 77, [74, 77], [378, 389]),
         "fixed source witness parameters")
    e, d = L[e_line], L[d0]
    pe = {s: dot(L[s], e) for s in lines}
    pd = {s: dot(L[s], d) for s in lines}
    B = make_B(U, lines, sink_words)
    mus, extras = {}, {}
    for line in relaxed:
        t = lines.index(line)
        Z = [s for s in range(len(lines)) if B[t][s] == 1 and s != t]
        ratios = {Fraction(-pd[lines[s]], pe[lines[s]]) for s in Z if pe[lines[s]] != 0}
        need(len(ratios) == 1, "one exact decoder coefficient ratio at relaxed target " + str(line))
        mus[line] = next(iter(ratios))
        extras[line] = {lines[s] for s in Z if pe[lines[s]] == 0 and pd[lines[s]] != 0}
        need(line not in extras[line], "relaxed target not an extra source")
    qa, qb = extras[74], extras[77]
    need(qa.issubset({lines[s] for s in range(112) if B[lines.index(77)][s]})
         and qb.issubset({lines[s] for s in range(112) if B[lines.index(74)][s]})
         and 74 not in qb and 77 not in qa,
         "shared extra sources satisfy the other sink's pairing")
    q_sources = sorted(qa | qb)
    need(len(q_sources) == 24 and qa == qb, "shared extra total has exactly 24 sources")
    need(mus == {74: Fraction(-1), 77: Fraction(0)}, "exact relaxed-row coefficients")

    N = make_N(L, G, lines, d, e, mus, q_sources)
    need(exact_endpoint(B, N), "all 112 by 112 rational support entries")
    rankB = f2_rank(B)
    beta_coord, beta_alpha = copy_costs(B, L, lines, relaxed, q_sources)
    corrections = {line: sum(1 for s, source in enumerate(lines)
                             if source != line and N[lines.index(line)][s] != 0) for line in relaxed}
    baseline_corrections = {line: sum(1 for source in lines if source != line and G[line][source] != 0)
                            for line in relaxed}
    B0 = [[(1 + G[t][s]) & 1 for s in lines] for t in lines]
    differs = sum(B[t][s] != B0[t][s] for t in range(112) for s in range(112))
    asymmetric_pairs = sum(B[t][s] != B[s][t] for t in range(112) for s in range(t + 1, 112))
    need(rankB == 9 and beta_coord == [8] * 8 and beta_alpha == 1, "window and exact COPY ranks")
    need(sum(beta_coord) + beta_alpha == 65, "complete copy cost 65")
    need(corrections == {74: 28, 77: 28} and baseline_corrections == {74: 52, 77: 52},
         "both exact correction reductions")
    need(differs > 0 and asymmetric_pairs > 0, "pairing is asymmetric and differs from symmetric baseline")

    bad_sinks = [379, 389]
    B_bad_sink = make_B(U, lines, bad_sinks)
    bad_sink_rejected = not exact_endpoint(B_bad_sink, N)
    need(bad_sink_rejected, "changed-sink negative control")
    missing_q = q_sources[0]
    N_bad_q = make_N(L, G, lines, d, e, mus, q_sources[1:])
    missing_source_rejected = not exact_endpoint(B, N_bad_q)
    need(missing_source_rejected, "omitted-shared-source negative control")

    selected = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    need(selected["kappa"] == KAPPA, "selected result remains the pinned kappa")
    return {
        "status": "PASS_P112_ASYMMETRIC_UNIT_AUDIT_SEED43",
        "base_commit": BASE,
        "selected_kappa": KAPPA,
        "assignment_seed": SEED,
        "predecessor": {"pr1342_d0": 76, "format_limits_generator": "research/format-limits/scripts/e8units.py"},
        "witness": {"port_count": 112, "e_line": e_line, "d0_line": d0,
                    "relaxed_lines": relaxed, "sink_words": sink_words,
                    "mu": {str(k): str(v) for k, v in mus.items()},
                    "q_sources": q_sources, "q_size": len(q_sources)},
        "coverage": {"rational_support_entries": 112 * 112,
                     "pairing_sha256": matrix_sha(B),
                     "decoder_sha256": matrix_sha([[str(x) for x in row] for row in N])},
        "copy": {"window_rank_f2": rankB, "coordinate_ranks": beta_coord,
                 "shared_total_rank": beta_alpha, "total": sum(beta_coord) + beta_alpha},
        "corrections": {"asymmetric_unit": corrections, "symmetric_e8_unit": baseline_corrections},
        "structure": {"pairing_entries_different_from_B0": differs,
                      "asymmetric_unordered_pairs": asymmetric_pairs},
        "negative_controls": {"changed_sink_rejected": bad_sink_rejected,
                              "omitted_shared_source_rejected": missing_source_rejected,
                              "omitted_source": missing_q},
        "scope": "Finite exact replay of one d0=77 P112 witness only; no general decoder theorem or new kappa.",
    }


def main():
    result = compute()
    cert = HERE / "CERTIFICATE.json"
    encoded = canonical(result) + b"\n"
    if "--write" in sys.argv:
        need(not cert.exists(), "refuse to overwrite frozen certificate")
        cert.write_bytes(encoded)
    else:
        need(canonical(json.loads(cert.read_bytes())) == canonical(result), "frozen exact witness certificate")
    print(result["status"])
    print("ports=112 entries=12544 window_rank=9 copy=65 corrections=28+28 baseline=52+52")
    print("controls changed_sink=rejected omitted_shared_source=rejected")

if __name__ == "__main__":
    main()
