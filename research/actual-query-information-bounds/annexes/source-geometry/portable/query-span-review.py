"""Check the source rows and the exact line and plane query certificates."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path


import argparse

ANNEX = Path(__file__).resolve().parents[1]
PARENT = ANNEX.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", required=True)
OUT = Path(parser.parse_args().out).resolve()
OUT.mkdir(parents=True, exist_ok=True)
HERE = ANNEX / "frozen" / 'lanes/source-domain/query-span-review'
LANES = HERE.parents[1]
ROOT = LANES.parents[2]
PACKET = LANES / "schur-selection/plane-repair"
PINS = {
    "QUERY-SPAN.md": "785e27fdc6f2bcd83318afee14103f3e021065d32be2265b8afdec3fea3e1081",
    "check_query_span.py": "bcc8bb5482c76578014512d51dd5d650d4bf13d6546b29e355ae01bec8a07811",
    "QUERY-SPAN.json": "a06939cba2c937f452027ee4a1f20b31121a70b7fc7393d9ccad091817ee448e",
    "PLANE-INVOLUTION.json": "f55bd0e7b81a15b6526ca3056ef3bf1bbf57b13137699e71a374f4cf8f55f794",
}
ARCHIVE = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBERS = {
    "word": ("candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz",
             "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"),
    "program": ("candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz",
                "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"),
    "phases": ("candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json",
               "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def dot(a, b):
    return (a & b).bit_count() % 2


def add(target, source, coefficient):
    for key, value in source.items():
        new = target.get(key, 0) + coefficient * value
        if new:
            target[key] = new
        else:
            target.pop(key, None)


def main():
    for name, pin in PINS.items():
        need(sha256((PACKET / name).read_bytes()).hexdigest() == pin, "Frozen packet: " + name)
    certificate = json.loads((PACKET / "QUERY-SPAN.json").read_bytes())
    planes = json.loads((PACKET / "PLANE-INVOLUTION.json").read_bytes())["planes"]
    archive_record = json.loads((ANNEX / "ARCHIVE-CHECK.json").read_bytes())
    need(archive_record["archive_sha256"] == ARCHIVE, "Historical archive binding")
    source = {}
    for key, (name, pin) in MEMBERS.items():
        raw = (PARENT / "payload/upstream" / Path(name).name).read_bytes()
        need(sha256(raw).hexdigest() == pin, "Selected member: " + key)
        source[key] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    word, program, phases = [source[key] for key in MEMBERS]
    rows = [{i: Fraction(1)} if i < 112 else {} for i in range(712)]
    count = 0
    for event in program["forward"]:
        if event == ["phase", "centers"]:
            break
        if event[0] != "scalar":
            continue
        gate = event[1]
        t = gate[1][1] + (704 if gate[1][0] == "C" else 0)
        if gate[0] == "clear":
            rows[t] = {}
        elif gate[0] == "scale":
            coefficient = Fraction(gate[2], gate[3])
            rows[t] = {i: value * coefficient for i, value in rows[t].items() if value * coefficient}
        else:
            s = gate[2][1] + (704 if gate[2][0] == "C" else 0)
            if gate[0] == "copy":
                rows[t] = rows[s].copy()
            else:
                add(rows[t], rows[s], Fraction(gate[3], gate[4]))
        count += 1
    else:
        raise ValueError("The original centre boundary is absent")
    matrix = [[rows[centre].get(p, 0) for p in range(112)] for centre in word["centers"]]
    interface_raw = (PARENT / "payload/lanes/circuit-interface/INTERFACE.json").read_bytes()
    need(sha256(interface_raw).hexdigest() == certificate["interface_sha256"], "Accepted interface pin")
    interface = json.loads(interface_raw)
    expected = [[Fraction(row.get(str(p), "0")) for p in range(112)] for row in interface["R"]]
    need(matrix == expected and len(matrix) == 8, "Independent source reconstruction of R")
    gram = [[sum(a * b for a, b in zip(row, other)) for other in matrix] for row in matrix]
    need(gram == [[56 * int(i == j) for j in range(8)] for i in range(8)], "Actual row Gram")
    labels = [record["q"] for record in phases["recipes"]]
    need(labels == word["ports"] == interface["ports"] and len(set(labels)) == 112
         and all(q and q.bit_count() % 2 for q in labels), "Exact distinct odd line labels")
    need(all(sum(matrix[i][p] != 0 for i in range(8)) == 4 for p in range(112)),
         "Four nonzero source entries in every column")
    for p, row in enumerate(certificate["line_pivot_functionals"]):
        need(row["port"] == p and row["q"] == labels[p]
             and matrix[row["centre_row"]][p] == row["pivot"]
             and abs(row["pivot"]) == 1, "Every line diagonal pivot")
    need(len(planes) == 56 and sorted(p for plane in planes for p in plane["ports"]) == list(range(112)),
         "The 56 planes partition the actual ports")
    directions = Counter(plane["q"] ^ plane["r"] for plane in planes)
    need(len(directions) == 41, "Repeated plane directions are retained")
    # Build each exact Fourier column from C_q C_r^-1 P_(q+r).
    columns = []
    trace_counts = []
    for plane in planes:
        p, s = plane["ports"]
        q, r = plane["q"], plane["r"]
        need([q, r] == [labels[p], labels[s]] and dot(q, r) == 0, "Actual ordered orthogonal pair")
        w = q ^ r
        operator = []
        for y in range(512):
            image = y ^ (w if dot(w, y) else 0)
            power = (dot(q, image) - dot(r, image)) % 4
            operator.append((image, power))
        need(all(operator[image][0] == y and (power + operator[image][1]) % 4 == 0
                 for y, (image, power) in enumerate(operator)), "Exact plane involution")
        need(operator[0] == (0, 0), "Constant character is fixed")
        trace = sum(1 for y, (image, power) in enumerate(operator) if image == y and power == 0)
        need(trace == 256 and all(power == 0 for y, (image, power) in enumerate(operator) if image == y),
             "Exact normalized plane trace")
        trace_counts.append(trace)
        columns.append(operator)
    unit = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    functional_checks = 0
    for k, plane in enumerate(planes):
        q, w = plane["q"], plane["q"] ^ plane["r"]
        support = [y for y in range(512) if dot(w, y)]
        for j, operator in enumerate(columns):
            real = imag = 0
            for y in support:
                image, power = operator[y]
                if image == y ^ w:
                    a, b = unit[(power - 1 + 2 * dot(q, y)) % 4]
                    real += a
                    imag += b
                functional_checks += 1
            need((real, imag) == (256 * int(j == k), 0), "Full plane-separating functional matrix")
    determinant = 1
    for k, (plane, pivot) in enumerate(zip(planes, certificate["plane_pivot_functionals"])):
        p, s = plane["ports"]
        a, b = [matrix[i][p] for i in range(8)], [matrix[i][s] for i in range(8)]
        det_gram = sum(x*x for x in a) * sum(y*y for y in b) - sum(x*y for x, y in zip(a, b))**2
        need(det_gram == 12 and pivot["plane"] == k and pivot["ports"] == [p, s], "Actual pair Gram and order")
        i, j = pivot["centre_rows"]
        det = a[i] * b[j] - b[i] * a[j]
        need(det == pivot["determinant"] and det != 0, "Exact certified two-column pivot")
        determinant *= det
    need(determinant == certificate["plane_minor_determinant_in_matching_order"] == 8,
         "Exact 112-column block determinant")
    need(certificate["line_scalar_input_rank"] == certificate["plane_scalar_input_rank"] == 112,
         "Stated source ranks")
    # A reversed plane orientation changes the moved-character sign.
    q, r = planes[0]["q"], planes[0]["r"]
    w = q ^ r
    y = next(y for y in range(512) if dot(w, y))
    image = y ^ w
    need((dot(q, image) - dot(r, image)) % 4 != (dot(r, image) - dot(q, image)) % 4,
         "Wrong plane orientation control")
    result = dict(status="PASS_INDEPENDENT_QUERY_SPAN_SOURCE_AND_CERTIFICATE",
                  frozen_packet_sha256=PINS, archive_sha256=ARCHIVE,
                  source_member_sha256={k: pin for k, (_, pin) in MEMBERS.items()},
                  source_scalar_events_replayed=count, source_rows=8, nonzero_line_columns=112,
                  line_source_rank=112, plane_source_rank=112,
                  planes=56, distinct_plane_directions=len(directions),
                  repeated_direction_group_sizes=sorted(directions.values()),
                  exact_Fourier_columns=56*512, separating_functional_column_checks=functional_checks,
                  pair_Gram_determinants=[12]*56, exact_block_minor_determinant=int(determinant),
                  source_reconstruction="Independent data-only scalar propagation to the original centre boundary; no producer import or execution.",
                  all_depth="Proof: compress all but one tensor factor to the fixed constant character.",
                  grammar="Every non-scalar payload map is counted, including rank-zero address maps; scalar initial and final contracts are required.",
                  controls=["Exact reversed-orientation moved-character sign differs."],
                  not_certified=["Native-child lower bound", "Native-cost bound", "Changed source interface", "Supplier or kappa improvement"])
    (OUT / "REVIEW.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(json.dumps({key: result[key] for key in ("source_scalar_events_replayed", "exact_Fourier_columns",
                                                 "separating_functional_column_checks", "exact_block_minor_determinant")}))


if __name__ == "__main__":
    main()
