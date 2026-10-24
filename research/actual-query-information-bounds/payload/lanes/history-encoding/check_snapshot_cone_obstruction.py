"""Check exact support and query minors for the backward snapshot cones."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
SNAPSHOT_PIN = "3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c"
INTERFACE_PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
NORMALS = [42, 7, 25, 52, 82, 127, 97, 76]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(row, other, scale):
    for j, a in other.items():
        value = row.get(j, Q(0)) + scale * a
        if value:
            row[j] = value
        else:
            row.pop(j, None)


def dot(a, b):
    return (a & b).bit_count() & 1


def determinant(matrix):
    a = [[Q(x) for x in row] for row in matrix]
    result = Q(1)
    for j in range(len(a)):
        pivot = next((i for i in range(j, len(a)) if a[i][j]), None)
        if pivot is None:
            return Q(0)
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            result = -result
        value = a[j][j]
        result *= value
        for i in range(j + 1, len(a)):
            scale = a[i][j] / value
            for k in range(j + 1, len(a)):
                a[i][k] -= scale * a[j][k]
    return result


def independent_columns(R, candidates):
    pivots = {}
    selected = []
    for p in candidates:
        row = {k: r[p] for k, r in enumerate(R) if r.get(p)}
        for k, basis in sorted(pivots.items()):
            if row.get(k):
                add(row, basis, -row[k])
        if row:
            k = min(row)
            a = row[k]
            pivots[k] = {j: b / a for j, b in row.items()}
            selected.append(p)
            if len(selected) == 8:
                return selected
    return selected


def main():
    raw = gzip.decompress((HERE / "BACKWARD-SNAPSHOT-INTERVALS.json.gz").read_bytes())
    require(sha256(raw).hexdigest() == SNAPSHOT_PIN, "snapshot source pin")
    data = json.loads(raw)
    raw_interface = (HERE.parent / "circuit-interface/INTERFACE.json").read_bytes()
    require(sha256(raw_interface).hexdigest() == INTERFACE_PIN, "interface source pin")
    interface = json.loads(raw_interface)
    ports = interface["ports"]
    require(data["R"] == interface["R"], "query source agreement")
    R = [{int(j): Q(a) for j, a in row.items()} for row in data["R"]]
    J = [{j: Q(1)} for j in range(112)]
    for j in range(112):
        for r in R:
            add(J[j], r, -r.get(j, Q(0)) / 4)

    def restrict(row):
        out = {j - 112: Q(a) for key, a in row.items()
               if 112 <= (j := int(key)) < 224}
        for key, a in row.items():
            j = int(key)
            if j < 112:
                add(out, J[j], Q(a))
        return out

    reduced = [restrict(row) for row in data["rows"]]
    pairs = sorted({(f, r) for lo, hi, j, f, r in data["intervals"]})
    coefficients = 0
    first_nonzero = None
    for f, r in pairs:
        U = data["frames"][f]
        for p, a in reduced[r].items():
            require(not any(dot(ports[p], u) for u in U), "snapshot support law")
            coefficients += 1
            if U and first_nonzero is None:
                first_nonzero = (f, r, p)
    final = [restrict(row) for row in data["final_rows"]]
    require(all(not final[j] for j in list(range(112)) + list(range(224, 712))),
            "completed X and all helper/private baselines vanish")

    minors = []
    for f, U in enumerate(data["frames"]):
        if not 0 < len(U) < 9:
            continue
        excluded = [p for p, q in enumerate(ports) if any(dot(q, u) for u in U)]
        chosen = independent_columns(R, excluded)
        require(len(chosen) == 8, "excluded query rank")
        matrix = [[r.get(p, Q(0)) for p in chosen] for r in R]
        det = determinant(matrix)
        require(det != 0, "exact query minor")
        minors.append({"frame": f, "basis": U, "excluded_count": len(excluded),
                       "minor_ports": chosen, "determinant": str(det)})

    lines = {U[0] for U in data["frames"] if len(U) == 1}
    require(lines.isdisjoint(NORMALS), "normal lines absent from actual frame list")
    for k, n in enumerate(NORMALS):
        require({p for p, q in enumerate(ports) if not dot(q, n)} == set(R[k]),
                "normal query support")
    f, r, p = first_nonzero
    require(dot(ports[p], ports[p]) == 1, "wrong-frame control is nonzero")
    bad_matrix = [[row.get(j, Q(0)) for j in minors[0]["minor_ports"]] for row in R]
    for row in bad_matrix:
        row[-1] = row[0]
    require(determinant(bad_matrix) == 0, "duplicate-minor-column control")
    report = {
        "status": "PASS_EXACT_SNAPSHOT_CONE_OBSTRUCTION",
        "snapshot_payload_sha256": SNAPSHOT_PIN,
        "interface_sha256": INTERFACE_PIN,
        "source_pins": data["pins"],
        "test_input": "X=JY; all 480 helpers and all 8 private inputs are zero",
        "support_law": "At frame U, every nonzero reduced Y coefficient has q_p perpendicular to U.",
        "distinct_frame_row_pairs": len(pairs),
        "exact_nonzero_support_coefficients": coefficients,
        "interval_count": len(data["intervals"]),
        "actual_positive_proper_frames": len(minors),
        "frames_by_rank": dict(sorted(Counter(len(m["basis"]) for m in minors).items())),
        "excluded_query_minors": minors,
        "normal_lines": NORMALS,
        "normal_lines_are_absent": True,
        "wrong_frame_control": {"row": r, "original_frame": f, "source_port": p,
                                "wrong_line": ports[p], "rejected": True},
        "duplicate_minor_column_rejected": True,
        "scope": "Single positive-birth cone, with all cone snapshots and all completed X/helper baselines. Merged incomparable cones and other protocols remain open.",
    }
    path = HERE / "SNAPSHOT-CONE-OBSTRUCTION.json"
    path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "distinct_frame_row_pairs",
                     "exact_nonzero_support_coefficients", "actual_positive_proper_frames")}, sort_keys=True))


if __name__ == "__main__":
    main()
