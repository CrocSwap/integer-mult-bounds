#!/usr/bin/env python3
"""Exact full-owner rank certificate for the credited QQ16 kernel family.

No predecessor Python is imported. All checks remain active under -O.
kyzer1023 with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
import gzip
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
PACKET = "research/joint-query/certificate.json.gz"
WITNESS = "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
PROOF = "research/joint-query/evidence/JOINT-QUERY-TRANSFER.md"
PINS = {
    ARCHIVE: "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
    PACKET: "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7",
    WITNESS: "e35e5868a1322e406191079c0675975b139692ba50b1e2e5fb8a40b6480519f4",
    PROOF: "9e13e73ebf3192a6548798c2f1d13bd4d83957e8db0dc34de12b1a5311a52a75",
}
MEMBERS = {
    "t16/global/base/work/complex-nine-native/DATA-PHASES.json":
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz":
        "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518",
}
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = [p for p in range(112) if p not in A + T]
IDENTITY = tuple(1 << j for j in range(73))
MINOR_DETERMINANT = 36317027395115679744


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate(raw, expected, label):
    require(sha256(raw).hexdigest() == expected, "source hash: " + label)
    return raw


def load_sources():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    require({r["path"]: r["sha256"] for r in sources["files"]
             if r["usage"] == "input"} == PINS, "declared input pins")
    raw = {name: authenticate((ROOT / name).read_bytes(), pin, name)
           for name, pin in PINS.items()}
    members = {}
    with tarfile.open(fileobj=BytesIO(raw[ARCHIVE]), mode="r:gz") as archive:
        for name, pin in MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            require(len(matches) == 1 and matches[0].isfile(), "unique archive member")
            data = authenticate(archive.extractfile(matches[0]).read(), pin, name)
            members[name.rsplit("/", 1)[-1]] = json.loads(
                gzip.decompress(data) if name.endswith(".gz") else data)
    return (json.loads(gzip.decompress(raw[PACKET])), members["DATA-PHASES.json"],
            members["GLOBAL-TEMPLATE.json.gz"], json.loads(raw[WITNESS]))


def rref(matrix):
    """Rational reduction; transposing selects independent original rows."""
    a = [list(map(Q, row)) for row in matrix]
    require(bool(a) and bool(a[0]) and all(len(row) == len(a[0]) for row in a),
            "nonempty rectangular matrix")
    pivots = []
    for col in range(len(a[0])):
        k = len(pivots)
        pivot = next((i for i in range(k, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[k], a[pivot] = a[pivot], a[k]
        scale = a[k][col]
        a[k] = [x / scale for x in a[k]]
        for i in range(len(a)):
            if i != k and a[i][col]:
                scale = a[i][col]
                a[i] = [x - scale * y for x, y in zip(a[i], a[k])]
        pivots.append(col)
        if len(pivots) == len(a):
            break
    return a, pivots


def rank(matrix):
    return len(rref(matrix)[1])


def determinant(matrix):
    """Integer Bareiss determinant, with every exact division checked."""
    a = [row[:] for row in matrix]
    n = len(a)
    require(n > 0 and all(len(row) == n for row in a), "square minor")
    require(all(type(x) is int for row in a for x in row), "integer minor")
    previous, sign = 1, 1
    for k in range(n - 1):
        pivot_row = next((i for i in range(k, n) if a[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                value, remainder = divmod(a[i][j] * pivot - a[i][k] * a[k][j], previous)
                require(remainder == 0, "Bareiss exact division")
                a[i][j] = value
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1]


def action(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def route(basis, stage):
    columns = []
    for vector in IDENTITY:
        for i, axis in enumerate(basis):
            difference = axis ^ (1 << (9 + 8 * (stage - 1) + i))
            if (vector & difference).bit_count() & 1:
                vector ^= difference
        columns.append(vector)
    return tuple(columns)


def check_route(columns, basis, stage, registered):
    require(columns in registered, "route absent from QQ16 packet")
    require(all(action(columns, v) == IDENTITY[i] for i, v in enumerate(columns)),
            "route involution")
    if stage:
        require(all(action(columns, b) == 1 << (9 + 8 * (stage - 1) + i)
                    for i, b in enumerate(basis)), "common-axis route")


def groups_certificate(R, bases):
    groups = {}
    for p in U:
        groups.setdefault(bases[p][0], []).append(p)
    records = []
    for axis, ports in sorted(groups.items()):
        _, pivots = rref([[R[k][p] for p in ports] for k in range(8)])
        records.append({"axis": axis, "ports": ports, "rank": len(pivots),
                        "basis_ports": [ports[j] for j in pivots]})
    return records


def tail_certificate(recipe, previous):
    """Symbolic h-multipliers, using B_s h=0 for every s=1,...,8."""
    require(recipe[:2] == [{"kind": "local", "pair": 0, "reverse": False, "stage": 0},
                           {"kind": "local", "pair": 0, "reverse": True, "stage": 1}],
            "fixed first pair")
    banks = [[0, 1], [0, 0], [0, 0], [0, 0]]
    records = []
    for event in recipe[2:]:
        kind = event["kind"]
        if kind == "bridge":
            s, t, c = event["src"], event["dst"], event["coefficient"]
            banks[t][0] += c * banks[s][0]
            banks[s][1] -= c * banks[t][1]
            record = dict(event)
        elif kind == "local":
            require(1 <= event["stage"] <= 8, "nonzero later chart")
            x, y = banks[event["pair"]]
            banks[event["pair"]] = [x - y, y] if event["reverse"] else [x, y + x]
            record = {"kind": "local", "stage": event["stage"]}
        else:
            require(kind == "terminal" and all(x == 0 for x, _ in banks),
                    "zero completed-X descendants")
            banks = [[y, -x] for x, y in banks]
            record = {"kind": "terminal"}
        record["ordinary"] = [x for pair in banks for x in pair]
        records.append(record)
    require(records == previous["trajectory_after_B1"], "pinned full tail trajectory")
    require(banks == [[1, 0], [0, 0], [0, 0], [0, 0]], "former-Y endpoint")
    return records


def reject(name, operation, controls):
    try:
        operation()
    except ValueError:
        controls.append(name)
    else:
        raise ValueError("control did not reject: " + name)


def check_call_bindings(recipe, calls):
    scheduled = {(e["stage"], e["pair"], "backward" if e["reverse"] else "forward")
                 for e in recipe if e["kind"] == "local"}
    require(scheduled == {(c["stage"], c["pair"], c["orientation"]) for c in calls},
            "recipe and hosted-call binding")


def build_result():
    packet, phases, template, previous = load_sources()
    require((packet["A_ports"], packet["T_ports"], packet["U_ports"]) == (A, T, U),
            "actual QQ16 partition")
    rational = [[Q(row.get(str(p), "0")) for p in range(112)] for row in packet["R_rows"]]
    require(len(rational) == 8 and all(x.denominator == 1 for row in rational for x in row),
            "integral source centre matrix")
    R = [[int(x) for x in row] for row in rational]
    RU = [[row[p] for p in U] for row in R]
    for ports, scale in ((U, 48), (A, 4)):
        require(all(sum(R[i][p] * R[j][p] for p in ports) == (scale if i == j else 0)
                    for i in range(8) for j in range(8)), "ordinary/selected Gram")
    require(phases["m"] == 73 and len(phases["recipes"]) == 112, "phase geometry")
    registered = {tuple(row["owner_right_matrix_columns"]) for row in packet["map_registry"].values()}
    bases, routes = [], []
    for p, record in enumerate(phases["recipes"]):
        basis = tuple(record["idle_children"][0]["orthogonal_axes"][:8])
        local = (record["q"],) + basis
        require(record["port"] == p and len(local) == 9 and all(0 < x < 512 for x in local),
                "local chart dimensions")
        require(all(((x & y).bit_count() & 1) == (i == j)
                    for i, x in enumerate(local) for j, y in enumerate(local)), "orthonormal chart")
        port_routes = [IDENTITY] + [route(basis, s) for s in range(1, 9)]
        for s, columns in enumerate(port_routes):
            check_route(columns, basis, s, registered)
        bases.append(basis)
        routes.append(port_routes)
    groups = groups_certificate(R, bases)
    upper = sum(g["rank"] for g in groups)
    require(upper == 74 and len(groups) == 47, "formal group rank bound")

    # Fixed actual owners suffice; no independence of formal bit functions assumed.
    owners = [("identity", IDENTITY)] + [(p, routes[p][1]) for p in range(16)]
    labels, evaluations = [], []
    for owner, columns in owners:
        for k in range(8):
            labels.append([owner, k])
            evaluations.append([R[k][p] * (action(columns, bases[p][0]) & 1) for p in U])
    require(all(any(action(columns, bases[p][0]) & 1 for _, columns in owners) for p in U),
            "every coordinate function has a nonzero owner evaluation")
    _, selected_rows = rref(list(map(list, zip(*evaluations))))
    selected = [evaluations[i] for i in selected_rows]
    _, selected_columns = rref(selected)
    require(len(selected_rows) == len(selected_columns) == upper, "matching lower and upper ranks")
    minor = [[row[j] for j in selected_columns] for row in selected]
    exact_det = determinant(minor)
    require(exact_det == MINOR_DETERMINANT, "exact separating determinant")
    require(rank(RU) == 8 and rank(evaluations + RU) == upper, "R factors through owner evaluations")
    large = next(g for g in groups if g["axis"] == 2)
    require(len(large["ports"]) == 30 and large["rank"] == 8, "attaining unread group")
    require(all(g["rank"] == len(g["ports"]) for g in groups if g["axis"] != 2),
            "no other within-axis coefficient redundancy")
    taps = [p for p in U if p not in large["ports"]]
    require(len(taps) == 66, "attaining set size")
    indices = [U.index(p) for p in large["ports"]]
    require(rank([[row[j] for j in indices] for row in evaluations]) == 8, "single-axis sufficiency")
    trajectory = tail_certificate(template["recipe"], previous)
    check_call_bindings(template["recipe"], template["calls"])

    controls = []
    broken = [row[:] for row in minor]
    broken[-1] = broken[0][:]
    reject("duplicated separating row", lambda: require(determinant(broken) != 0, "singular minor"), controls)
    reject("wrong determinant", lambda: require(exact_det == MINOR_DETERMINANT + 1, "determinant"), controls)
    reject("payload-only owner action", lambda: check_route(IDENTITY, bases[0], 1, registered), controls)
    reject("unregistered route", lambda: check_route(routes[0][1], bases[0], 1, {IDENTITY}), controls)
    reject("wrong common axis", lambda: check_route(routes[0][1], (bases[0][1],) + bases[0][1:], 1, registered), controls)
    reject("identity-owner rank substituted", lambda: require(rank(evaluations[:8]) == upper, "identity rank"), controls)
    reject("66 directions mislabeled per owner", lambda: require(rank(evaluations[:8]) >= 66, "per-owner outputs"), controls)
    wrong_recipe = [dict(e) for e in template["recipe"]]
    next(e for e in wrong_recipe if e["kind"] == "local" and e["stage"] == 2)["pair"] = 1
    reject("wrong F2 bank", lambda: check_call_bindings(wrong_recipe, template["calls"]), controls)
    missing = [e for e in template["recipe"] if e !=
               {"kind": "bridge", "src": 1, "dst": 0, "coefficient": -1}]
    reject("missing cancelling bridge", lambda: tail_certificate(missing, previous), controls)
    reject("source corruption", lambda: authenticate(b"changed", PINS[PACKET], PACKET), controls)
    reject("receipt number changed to boolean", lambda: require(canonical({"rank": 1}) ==
                                                               canonical({"rank": True}), "JSON scalar type"), controls)
    remaining = large["ports"] + [taps[0]]
    indices = [U.index(p) for p in remaining]
    survivor_rank = rank([[row[j] for j in indices] for row in evaluations])
    require(survivor_rank == 9 and rank([[R[k][p] for p in remaining] for k in range(8)]) == 8,
            "65-tap boundary retains exactly one defect")
    reject("65 taps claimed sufficient", lambda: require(survivor_rank == 8, "one defect survives"), controls)
    return {
        "schema": "qq16-owner-separation-v1", "status": "PASS_QQ16_OWNER_SEPARATION",
        "source_hashes": PINS, "archive_members": MEMBERS, "ordinary_ports": U,
        "ordinary_rank": 8, "common_kernel_dimension": 88, "groups": groups,
        "group_rank_upper_bound": upper, "owner_evaluation_rank": 74,
        "owner_evaluation_count": len(owners),
        "separating_minor": {"rows": [labels[i] for i in selected_rows],
                             "ports": [U[j] for j in selected_columns],
                             "determinant": str(exact_det), "matrix": minor},
        "coefficient_kernel_dimension": 22, "original_A_defect_dimension": 66,
        "sharp_family_coordinate_threshold": 66, "attaining_taps": taps,
        "attaining_unread_ports": large["ports"], "65_tap_remaining_defect": 1,
        "nonzero_chart_routes_checked": 896, "packet_route_bindings": 1008,
        "tail_trajectory": trajectory, "rejecting_controls": controls,
        "scope": "Coefficient-family result across the whole owner array, not per owner; fixed maps/schedule; no full controller, native tariff, supplier or kappa claim.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", type=Path, help="Create a receipt exclusively; never overwrite")
    args = parser.parse_args()
    result = build_result()
    if args.emit_result:
        with args.emit_result.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
        require(canonical(result) == canonical(expected), "complete canonical receipt equality")
    print(result["status"] + " rank=74 defect=66 sharp_family_taps=66 controls=" +
          str(len(result["rejecting_controls"])) + " no_new_kappa")


if __name__ == "__main__":
    main()
