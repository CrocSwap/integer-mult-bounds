#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Second check: source reconstruction, explicit binary spans, modular minors.

Does not import verify.py, PR2308 code, or any numerical package. A nonzero
integer minor modulo 101 certifies its nonvanishing in characteristic zero;
no finite-field equality is substituted for a rational identity.
"""
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def moddet(matrix, p=101):
    a = [[x % p for x in row] for row in matrix]
    answer = 1
    for c in range(len(a)):
        row = next((i for i in range(c, len(a)) if a[i][c]), None)
        if row is None:
            return 0
        if row != c:
            a[c], a[row] = a[row], a[c]
            answer = -answer
        answer = answer * a[c][c] % p
        inverse = pow(a[c][c], -1, p)
        for i in range(c + 1, len(a)):
            factor = a[i][c] * inverse % p
            a[i] = [(x - factor * y) % p for x, y in zip(a[i], a[c])]
    return answer % p


def span_rank(rows):
    space = {0}
    for v in rows:
        space |= {x ^ v for x in tuple(space)}
    need(len(space) & (len(space) - 1) == 0, "binary span size")
    return len(space).bit_length() - 1


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for pin in pins["files"] + pins["external_files"]:
        if pin.get("usage") == "provenance":
            continue
        need(sha256((ROOT / pin["path"]).read_bytes()).hexdigest() == pin["sha256"], "source drift")
    cert = json.loads((HERE / "PR2308-CERTIFICATE.json").read_text())
    result = json.loads((HERE / "RESULT.json").read_text())
    roots = []
    for a, b in combinations(range(8), 2):
        for sign in (1, -1):
            v = [0] * 8
            v[a], v[b] = 2, 2 * sign
            roots.append(v)
    roots += [[1, *v] for v in product((1, -1), repeat=7) if sum(x < 0 for x in v) % 2 == 0]
    gram = [[sum(x*y for x,y in zip(a,b)) // 4 for b in roots] for a in roots]
    labels = {x["line"]: x["q"] for x in cert["q_to_line"]}
    frames = cert["witness"]["frames"]
    union = sorted(set(frames[0]) | set(frames[1]))
    r = 234
    need(result["physical_shared_direction"] == r and r.bit_count() % 2 == 1, "shared r")
    need(all((labels[a] & r).bit_count() % 2 == 0 for a in union), "upgrade orthogonality")
    complement = [a for a in sorted(labels) if (labels[a] & r).bit_count() % 2]
    need(union == result["union"] and len(union) == 12 and complement == result["complement_ports"], "port sets")
    cols = union + complement
    twice_rectangle = [[2 * int(a == b) - gram[a][b] for b in cols] for a in union]
    receipt = result["forced_rectangle"]
    need(receipt["rank"] == receipt["any_additive_scalar_correction_COPY_floor"] == 12,
         "rank-to-cost claim")
    need(twice_rectangle == receipt["twice_entries"], "forced rectangle source binding")
    positions = receipt["minor_column_positions"]
    need(len(set(positions)) == 12 and all(0 <= p < len(cols) for p in positions), "minor columns")
    minor = [[row[p] for p in positions] for row in twice_rectangle]
    residue = moddet(minor)
    need(residue != 0 and residue == receipt["minor_determinant"] % 101 == 2048 % 101, "rank12 minor")
    rt = result["complement_rank_witness"]
    need(len(rt["line_ids"]) == 8 and set(rt["line_ids"]) <= set(complement), "rank8 domain")
    need(moddet([roots[a] for a in rt["line_ids"]]) == 1024 % 101 != 0, "rank8 root minor")

    charges = []
    for k, s in enumerate(frames[0]):
        rows = [a for a in union if gram[a][s]]
        columns = [b for b in complement if gram[s][b]]
        left = [v for a in rows for v in [labels[a], r]]
        right = [labels[b] for b in columns]
        masks = [sum(((a & b).bit_count() & 1) << j for j, b in enumerate(right)) for a in left]
        charge = span_rank(masks)
        recorded = result["correction_terms"][k]
        need(recorded == {"column": k, "row_support": rows, "column_support": columns,
                          "pairing_rank_per_direction": charge}, "literal support charge")
        charges.append(charge)
    need(charges == [1,1,4,4,1,1,4,4] and 2 * sum(charges) == 40, "rank invoice")
    missing = [[a, b, str(gram[a][b]) + "/2"] for a in union for b in union if a != b and gram[a][b]]
    need(missing == result["forbidden_nonzero_entries"] and len(missing) == 32, "missing plane coefficients")
    need(gram[16][20] == 1 and labels[16] == 38 and labels[20] == 70, "counterexample binding")
    # Changed hypotheses are real: omitting the shared r removes this constraint.
    need((38 & 70).bit_count() % 2 == 0 and r.bit_count() % 2 == 1, "line/plane boundary control")
    bad_minor = [row[:] for row in minor]
    bad_minor[-1] = bad_minor[0][:]
    need(moddet(bad_minor) == 0, "dependent-minor control")
    print("PASS_P112_SHARED_CORRECTION_SECOND_CHECK rank12_minor_mod101=" + str(residue)
          + " support_COPY=40 forbidden_entries=32 no_new_kappa")


if __name__ == "__main__":
    main()
