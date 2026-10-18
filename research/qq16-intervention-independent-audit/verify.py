#!/usr/bin/env python3
"""Independent QQ16 difference-module audit. Apache-2.0; Codex assisted."""
from copy import deepcopy
from fractions import Fraction as Q
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKET = "research/joint-query/certificate.json.gz"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
PHASES = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
TEMPLATE = "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz"
MEMBER_PINS = {
    PHASES: "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    TEMPLATE: "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518",
}
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
SUPPORT = {2: -1, 8: 1, 85: 1}


def require(value, message):
    if not value:
        raise ValueError(message)


def load():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            raw = (ROOT / entry["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == entry["sha256"], "source digest: " + entry["path"])
    members = {}
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        for name, digest in MEMBER_PINS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            require(len(matches) == 1 and matches[0].isfile(), "archive member")
            raw = archive.extractfile(matches[0]).read()
            require(hashlib.sha256(raw).hexdigest() == digest, "member digest")
            members[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    return json.loads(gzip.decompress((ROOT / PACKET).read_bytes())), members


def witness(packet, phases, coefficients=None):
    # All-owner cancellation follows from the separately bound common route
    # image, not from sampling owner values or importing Walsh-polynomial code.
    coefficients = SUPPORT if coefficients is None else coefficients
    R = [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet["R_rows"]]
    require((packet["A_ports"], packet["T_ports"]) == (A, T), "selected minors")
    require(len(R) == 8, "R dimension")
    require(all(sum(R[i][p] * R[j][p] for p in A) == 4 * (i == j)
                for i in range(8) for j in range(8)), "A inverse")
    axes = {p: phases["recipes"][p]["idle_children"][0]["orthogonal_axes"][0] for p in coefficients}
    require(axes == {2: 37, 8: 38, 85: 506}, "witness axes")
    require(all(sum(c * R[i][p] for p, c in coefficients.items()) == 0 for i in range(8)),
            "common routed column cancellation")
    b0 = [sum(c * (-1 if axes[p] & 1 else 1) * R[i][p]
              for p, c in coefficients.items()) for i in range(8)]
    original_A = [-sum(R[i][p] * b0[i] for i in range(8)) / 4 for p in A]
    require(b0 == [2, 2, 0, 0, 0, 0, 2, -2], "B0 at identity")
    require(original_A == [-1, 0, -1, -1, 0, 1, 0, 0], "lost original A")
    require([sum(R[i][p] * original_A[j] for j, p in enumerate(A)) + b0[i]
             for i in range(8)] == [0] * 8, "F0 query cancellation")
    return {"B0_h_at_identity": list(map(str, b0)), "original_A_at_identity": list(map(str, original_A))}


def recipe_key(event):
    if event["kind"] == "local":
        return ["B" if event["reverse"] else "F", event["stage"], event["pair"]]
    if event["kind"] == "bridge":
        return ["bridge", event["src"], event["dst"], event["coefficient"]]
    return [event["kind"], event.get("pairs")]


EXPECTED_RECIPE = [
    ["F", 0, 0], ["B", 1, 0], ["bridge", 1, 0, 1], ["F", 2, 0],
    ["bridge", 1, 0, -1], ["B", 3, 1], ["bridge", 2, 1, 1], ["F", 4, 1],
    ["bridge", 2, 1, -1], ["B", 5, 2], ["bridge", 3, 2, 1], ["F", 6, 2],
    ["bridge", 3, 2, -1], ["B", 7, 3], ["F", 8, 3],
    ["bridge", 2, 3, 1], ["bridge", 1, 2, 1], ["bridge", 0, 1, 1], ["terminal", 4],
]


def trajectory(recipe, terminal_sign=-1):
    require([recipe_key(e) for e in recipe] == EXPECTED_RECIPE, "stage/pair/bridge schedule")
    # Rows are coefficients of h in (x0,y0,x1,y1,x2,y2,x3,y3) after F0.
    matrix = [[int(i == j) for j in range(8)] for i in range(8)]
    state = [1, 1, 0, 0, 0, 0, 0, 0]
    receipt = [{"event": 0, "ordinary_h_coefficients": state}]
    before_terminal = None
    for index, event in enumerate(recipe[1:], 1):
        kind = event["kind"]
        if kind == "local":
            x = 2 * event["pair"]
            if event["reverse"]:
                matrix[x] = [a - b for a, b in zip(matrix[x], matrix[x + 1])]
            else:
                matrix[x + 1] = [a + b for a, b in zip(matrix[x], matrix[x + 1])]
        elif kind == "bridge":
            s, d, c = 2 * event["src"], 2 * event["dst"], event["coefficient"]
            matrix[d] = [a + c * b for a, b in zip(matrix[d], matrix[s])]
            matrix[s + 1] = [a - c * b for a, b in zip(matrix[s + 1], matrix[d + 1])]
        else:
            before_terminal = deepcopy(matrix)
            matrix = [row for p in range(4) for row in
                      (matrix[2 * p + 1], [terminal_sign * a for a in matrix[2 * p]])]
        receipt.append({"event": index, "ordinary_h_coefficients":
                        [sum(a * b for a, b in zip(row, state)) for row in matrix]})
    expected = [[int(i == j) for j in range(8)] for i in range(8)]
    expected[1][0] = -1
    require(matrix == expected, "complete eight-variable tail transfer")
    require(receipt[-1]["ordinary_h_coefficients"] == [1, 0, 0, 0, 0, 0, 0, 0], "former-Y endpoint")
    require(all(sum(a * b for a, b in zip(before_terminal[i], state)) == 0
                for i in (0, 2, 4, 6)), "completed-X observations")
    return {"tail_matrix_after_F0": matrix, "events": receipt,
            "completed_X_projection_before_terminal": before_terminal[::2]}


def rejected(fn):
    try:
        fn()
    except ValueError:
        return True
    raise ValueError("negative control unexpectedly accepted")


def build_result():
    packet, members = load()
    phases, recipe = members[PHASES], members[TEMPLATE]["recipe"]
    w, tr = witness(packet, phases), trajectory(recipe)
    wrong_pair = deepcopy(recipe)
    wrong_pair[3]["pair"] = 1
    controls = {
        "column_dependency_sign": rejected(lambda: witness(packet, phases, {2: 1, 8: 1, 85: 1})),
        "wrong_F2_pair": rejected(lambda: trajectory(wrong_pair)),
        "missing_negative_bridge": rejected(lambda: trajectory(recipe[:4] + recipe[5:])),
        "wrong_terminal_sign": rejected(lambda: trajectory(recipe, terminal_sign=1)),
    }
    require(any(Q(v) for v in w["B0_h_at_identity"]), "B0 read must detect")
    require(tr["events"][-1]["ordinary_h_coefficients"][0] == 1, "former-Y read must detect")
    spec = importlib.util.spec_from_file_location("route_binding", HERE / "route_binding.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    route_result = module.check_bindings(packet, phases)
    route_result.update(module.run_controls(packet, phases))
    return {"status": "PASS_QQ16_INDEPENDENT_INTERVENTION_AUDIT", "witness": w,
            "reduced_trajectory": tr, "route_binding": route_result,
            "rejected_controls": controls, "detecting_observations": ["B0_h", "final_former_Y_X0U"],
            "scope": "Independent audit of PR2306; nonlinear induction is written proof, not sampling; no supplier or kappa claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    result = build_result()
    if args.write_result:
        with args.write_result.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(json.loads((HERE / "RESULT.json").read_text()) == result, "complete receipt")
    print(result["status"])
    print("19 events; exact eight-variable tail transfer; nonzero original A; no new kappa")


if __name__ == "__main__":
    main()
