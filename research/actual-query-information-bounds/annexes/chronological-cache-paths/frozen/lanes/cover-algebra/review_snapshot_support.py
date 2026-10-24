"""Check the snapshot support law with exact integer arithmetic."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import lcm
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
SNAPSHOT_PIN = "3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c"
INTERFACE_PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
PRIME = 65521


def require(value, message):
    if not value:
        raise ValueError(message)


def determinant(matrix):
    """Use exact elimination on the selected eight-column minor."""
    rows = [[Fraction(x) for x in row] for row in matrix]
    result = Fraction(1)
    for col in range(len(rows)):
        pivot = next((j for j in range(col, len(rows)) if rows[j][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            result = -result
        value = rows[col][col]
        result *= value
        for j in range(col + 1, len(rows)):
            scale = rows[j][col] / value
            for k in range(col + 1, len(rows)):
                rows[j][k] -= scale * rows[col][k]
    return result


def select_minor(matrix, columns):
    """Select columns over a finite field, then check their exact minor."""
    size = len(matrix)
    pivots = {}
    selected = []
    for column in columns:
        row = [matrix[k][column] % PRIME for k in range(size)]
        for k, pivot in sorted(pivots.items()):
            factor = row[k]
            row = [(a - factor*b) % PRIME for a, b in zip(row, pivot)]
        leading = next((k for k, value in enumerate(row) if value), None)
        if leading is not None:
            scale = pow(row[leading], -1, PRIME)
            pivots[leading] = [value*scale % PRIME for value in row]
            selected.append(column)
            if len(selected) == size:
                break
    require(len(selected) == size, "An excluded-column block has deficient rank")
    value = determinant([[row[p] for p in selected] for row in matrix])
    require(value != 0, "The selected rational minor is zero")
    return selected, str(value)


def main():
    snapshot_path = HERE.parent / "history-encoding/BACKWARD-SNAPSHOT-INTERVALS.json.gz"
    raw = gzip.decompress(snapshot_path.read_bytes())
    require(sha256(raw).hexdigest() == SNAPSHOT_PIN, "The snapshot pin differs")
    data = json.loads(raw)
    interface_path = HERE.parent / "circuit-interface/INTERFACE.json"
    interface_raw = interface_path.read_bytes()
    require(sha256(interface_raw).hexdigest() == INTERFACE_PIN, "The interface pin differs")
    interface = json.loads(interface_raw)
    labels = interface["ports"]
    R = [[int(Fraction(row.get(str(j), "0"))) for j in range(112)]
         for row in data["R"]]
    require(R == [[int(Fraction(row.get(str(j), "0"))) for j in range(112)]
                  for row in interface["R"]], "The root matrices differ")
    require(all(Fraction(v).denominator == 1 for row in data["R"] for v in row.values()),
            "A root coefficient is not an integer")
    require([[sum(a*b for a, b in zip(R[i], R[j])) for j in range(8)]
             for i in range(8)] == [[56*int(i == j) for j in range(8)] for i in range(8)],
            "The root Gram differs")
    J4 = [{q: 4*int(p == q)-sum(row[p]*row[q] for row in R)
           for q in range(112)} for p in range(112)]
    J4 = [{q: value for q, value in row.items() if value} for row in J4]
    reduced = []
    for item in data["rows"]:
        row = {int(k): Fraction(value) for k, value in item.items() if int(k) < 224}
        denominator = lcm(*(value.denominator for value in row.values()))
        output = {}
        for k, value in row.items():
            coefficient = int(value*denominator)
            source = J4[k] if k < 112 else {k-112: 4}
            for q, entry in source.items():
                output[q] = output.get(q, 0) + coefficient*entry
        reduced.append({q: value for q, value in output.items() if value})
    failures = []
    full_nonzero = []
    support_checks = 0
    for first, last, wire, frame, row in data["intervals"]:
        basis = data["frames"][frame]
        for port in reduced[row]:
            support_checks += 1
            if any((labels[port] & vector).bit_count() % 2 for vector in basis):
                failures.append([first, last, wire, frame, row, port])
        if frame == 1 and reduced[row]:
            full_nonzero.append(row)
    require(not failures, "A snapshot violates the exact support law")
    require(not full_nonzero, "A FULL snapshot remains nonzero on the test input")
    minors = []
    for frame, basis in enumerate(data["frames"]):
        if not 0 < len(basis) < 9:
            continue
        excluded = [p for p, q in enumerate(labels)
                    if any((q & v).bit_count() % 2 for v in basis)]
        columns, value = select_minor(R, excluded)
        minors.append({"frame": frame, "columns": columns, "determinant": value})
    normals = [42, 7, 25, 52, 82, 127, 97, 76]
    require(all([n] not in data["frames"] for n in normals), "A normal line is an actual frame")
    require(all({p for p, value in enumerate(R[k]) if value}
                == {p for p, q in enumerate(labels) if (q & n).bit_count() % 2 == 0}
                for k, n in enumerate(normals)), "The normal support relation differs")
    line_minors = []
    for vector in range(1, 512):
        excluded = [p for p, q in enumerate(labels) if (q & vector).bit_count() % 2]
        omit = normals.index(vector) if vector in normals else None
        selected_rows = [k for k in range(8) if k != omit]
        columns, value = select_minor([R[k] for k in selected_rows], excluded)
        if omit is not None:
            require(all(R[omit][p] == 0 for p in excluded), "A normal line has the wrong kernel")
        line_minors.append({"line": vector, "rank": len(selected_rows),
                            "rows": selected_rows, "columns": columns,
                            "determinant": value})
    source_proof = HERE.parent / "history-encoding/SNAPSHOT-CONE-OBSTRUCTION.md"
    source_receipt = HERE.parent / "history-encoding/SNAPSHOT-CONE-OBSTRUCTION.json"
    result = {
        "status": "PASS_EXACT_SNAPSHOT_SUPPORT_AND_SINGLE_CONE_EXCLUSION",
        "inputs": {"snapshot_decompressed_sha256": SNAPSHOT_PIN,
                   "interface_sha256": INTERFACE_PIN,
                   "reviewed_source_proof_sha256": sha256(source_proof.read_bytes()).hexdigest(),
                   "reviewed_source_receipt_sha256": sha256(source_receipt.read_bytes()).hexdigest()},
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "rows": len(reduced), "intervals": len(data["intervals"]),
        "nonzero_port_incidence_checks": support_checks,
        "proper_frame_minor_count": len(minors),
        "minor_determinants": dict(Counter(item["determinant"] for item in minors)),
        "excluded_column_minors": minors,
        "all_511_line_minors": line_minors,
        "line_rank_counts": dict(Counter(item["rank"] for item in line_minors)),
        "normal_lines_absent": normals,
        "test_input": "X=JY; all 480 helper and eight private inputs are zero",
        "scope": "One nonzero birth frame and all later containing frames. This does not exclude a merged network with incomparable capture frames.",
        "phase_scope": "Scalar rows are read in the canonical view. Non-FULL views after event 17605 require the supplied endpoint monomial adapter.",
        "not_checked": ["The full snapshot producer replay", "A new native cache word", "Chronological branching synthesis", "A complete supplier invoice"],
    }
    output = HERE / "SNAPSHOT-SUPPORT-REVIEW.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items()
                      if k not in {"excluded_column_minors", "all_511_line_minors"}}, sort_keys=True))


if __name__ == "__main__":
    main()
