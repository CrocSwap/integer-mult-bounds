#!/usr/bin/env python3
"""Exact, producer-independent QQ16 expanded-observation counterexample.

Sparse functions represent finite sums of f_v(d) = bit_0(d v).  A zero
formal sum is zero at every owner; nonzeroness is witnessed at d = I.
No predecessor Python code is imported or executed.  Apache-2.0.
Prepared for Adam Gall with substantial OpenAI Codex assistance.
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
CERTIFICATE = "research/joint-query/certificate.json.gz"
EVIDENCE = "research/joint-query/evidence/"
INPUTS = {
    ARCHIVE: "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
    CERTIFICATE: "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7",
    EVIDENCE + "JOINT-QUERY-TRANSFER.md": "9e13e73ebf3192a6548798c2f1d13bd4d83957e8db0dc34de12b1a5311a52a75",
    EVIDENCE + "QQ16-RATIONAL-OBSERVATION-REVIEW.md": "9a06ff40830ef80d3566fce77c78639cb64d519d487a0a7f57d543c3146e2c49",
    EVIDENCE + "QQ16-SELECTED-WITNESS.md": "52f2ee565320f05282c637aa79eee100606c24240b1b5866f0c8d62e7913c9fc",
    EVIDENCE + "QQ16-SELECTED-WITNESS.json": "e35e5868a1322e406191079c0675975b139692ba50b1e2e5fb8a40b6480519f4",
    EVIDENCE + "BRIDGE-REVIEW.md": "d01b5f4959f7c91f835496d050dfae3eeab9dee2f581571c316a42571eaa1cd3",
}
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "t16/global/base/work/complex-nine-native/DATA-PHASES.json": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz": "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518",
}
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
COEFFICIENTS = {2: -1, 8: 1, 85: 1}
AXES = tuple(1 << j for j in range(73))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, expected, name):
    require(sha256(raw).hexdigest() == expected, "source hash: " + name)
    return raw


def load_sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    require({row["path"]: row["sha256"] for row in manifest["files"]
             if row["usage"] == "input"} == INPUTS, "manifest input pins")
    raw = {name: authenticate((ROOT / name).read_bytes(), pin, name)
           for name, pin in INPUTS.items()}
    members = {}
    with tarfile.open(fileobj=BytesIO(raw[ARCHIVE]), mode="r:gz") as archive:
        for name, pin in MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            require(len(matches) == 1 and matches[0].isfile(), "unique member: " + name)
            payload = authenticate(archive.extractfile(matches[0]).read(), pin, name)
            if name.endswith(".gz"):
                payload = gzip.decompress(payload)
            members[name.rsplit("/", 1)[-1]] = json.loads(payload)
    certificate = json.loads(gzip.decompress(raw[CERTIFICATE]))
    previous = json.loads(raw[EVIDENCE + "QQ16-SELECTED-WITNESS.json"])
    return members, certificate, previous


def linear(*terms):
    """Exact sum of (scalar, sparse row/function) terms, with zero removal."""
    result = {}
    for coefficient, row in terms:
        for key, value in row.items():
            result[key] = result.get(key, Q(0)) + coefficient * value
    return {key: value for key, value in result.items() if value}


def reconstruct_R(word, programs):
    require((word["v"], word["R"], word["h"]) == (112, 480, 9), "selected geometry")
    # Project the original scalar operations to the 112 source input columns.
    rows = [{p: Q(1)} if p < 112 else {} for p in range(712)]
    reached = False
    for event in programs["forward"]:
        if event == ["phase", "centers"]:
            reached = True
            break
        if event[0] != "scalar":
            continue
        op = event[1]
        target = op[1][1] + (704 if op[1][0] == "C" else 0)
        if op[0] == "clear":
            rows[target] = {}
        elif op[0] == "scale":
            rows[target] = linear((Q(op[2], op[3]), rows[target]))
        else:
            require(op[0] in ("add", "copy"), "original scalar alphabet")
            source = op[2][1] + (704 if op[2][0] == "C" else 0)
            rows[target] = (rows[source].copy() if op[0] == "copy" else
                            linear((1, rows[target]), (Q(op[3], op[4]), rows[source])))
    require(reached, "source centre cut")
    return [[rows[c].get(p, Q(0)) for p in range(112)] for c in word["centers"]]


def inverse(matrix):
    n = len(matrix)
    rows = [list(row) + [Q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        require(pivot is not None, "selected minor invertibility")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [x / divisor for x in rows[col]]
        for i in range(n):
            if i != col:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[col])]
    return [row[n:] for row in rows]


def binary_action(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def route_axis(basis, stage, vector):
    if stage == 0:
        return vector
    for i, axis in enumerate(basis):
        swap = axis ^ AXES[9 + 8 * (stage - 1) + i]
        if (vector & swap).bit_count() % 2:
            vector ^= swap
    return vector


class Model:
    def __init__(self, R, phases, ignore_owner=False):
        self.R = R
        self.bases = [tuple(row["idle_children"][0]["orthogonal_axes"][:8])
                      for row in phases["recipes"]]
        self.inverses = {ports: inverse([[R[k][p] for p in ports] for k in range(8)])
                         for ports in (A, T)}
        self.routes = []
        require(phases["m"] == 73 and len(self.bases) == 112, "actual phase geometry")
        for p, (basis, record) in enumerate(zip(self.bases, phases["recipes"])):
            local = (record["q"],) + basis
            require(record["port"] == p and all(0 < v < (1 << 9) for v in local),
                    "actual first-block chart")
            require(all((local[i] & local[j]).bit_count() % 2 == (i == j)
                        for i in range(9) for j in range(9)), "orthonormal chart")
            routes = []
            for stage in range(9):
                columns = tuple(route_axis(basis, stage, v) for v in AXES)
                require(all(binary_action(columns, column) == AXES[i]
                            for i, column in enumerate(columns)), "route involution")
                if stage:
                    require(all(binary_action(columns, basis[i]) == AXES[9 + 8 * (stage - 1) + i]
                                for i in range(8)), "actual common-axis image")
                routes.append(AXES if ignore_owner else columns)
            self.routes.append(routes)

    def move(self, stage, port, function):
        return linear(*((value, {binary_action(self.routes[port][stage], axis): Q(1)})
                        for axis, value in function.items()))

    def query(self, stage, fields, ports=tuple(range(112))):
        return [linear(*((self.R[k][p], self.move(stage, p, fields[p])) for p in ports))
                for k in range(8)]

    def inject(self, stage, ports, query):
        result = [{} for _ in range(112)]
        for i, p in enumerate(ports):
            result[p] = self.move(stage, p, linear(*((self.inverses[ports][i][k], query[k])
                                                    for k in range(8))))
        return result

    def ordinary_response(self, stage, query):
        result = [{} for _ in range(112)]
        for p in U:
            result[p] = self.move(stage, p, linear(*((self.R[k][p] / 4, query[k])
                                                    for k in range(8))))
        return result

    def forward(self, stage, x, y):
        f = self.query(stage, x)
        selected = self.query(stage, x, T)
        response = self.ordinary_response(stage, f)
        xa, xt = self.inject(stage, A, selected), self.inject(stage, T, f)
        out_x, out_y = [{} for _ in range(112)], [{} for _ in range(112)]
        for p in U:
            out_x[p] = linear((1, x[p]), (-1, response[p]))
            out_y[p] = linear((1, y[p]), (1, out_x[p]))
        for p in A + T:
            out_x[p] = xa[p] if p in A else xt[p]
            out_y[p] = linear((1, x[p]), (1, y[p]), (-1, out_x[p]))
        return out_x, out_y, f

    def backward(self, stage, future, x, y):
        ua = self.inject(future, A, self.query(future, y))
        u = [ua[p] if p in A else y[p].copy() for p in range(112)]
        a, b = self.query(stage, x, T), self.query(stage, u)
        response = self.ordinary_response(stage, a)
        xt = self.inject(stage, T, [linear((1, b[k]), (12, a[k])) for k in range(8)])
        subtract = self.inject(stage, T, [linear((1, b[k]), (11, a[k])) for k in range(8)])
        out_x, out_y = [{} for _ in range(112)], [{} for _ in range(112)]
        for p in U:
            out_x[p] = linear((1, x[p]), (-1, y[p]))
            out_y[p] = linear((1, y[p]), (1, response[p]))
        for p in A:
            out_x[p] = linear((1, x[p]), (1, y[p]), (-1, u[p]))
            out_y[p] = u[p]
        for p in T:
            out_x[p], out_y[p] = xt[p], linear((1, u[p]), (-1, subtract[p]))
        return out_x, out_y


def at_identity(function):
    return sum(coefficient * (axis & 1) for axis, coefficient in function.items())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def experiment(model, template, previous, coefficients=None, axis_mutation=False,
               omit_initial_correction=False, omit_minus=False, wrong_endpoint=False,
               extra_stage=2):
    coefficients = COEFFICIENTS if coefficients is None else coefficients
    h = [{} for _ in range(112)]
    for p, c in coefficients.items():
        axis_index = 1 if axis_mutation and p == 2 else 0
        h[p] = {model.bases[p][axis_index]: Q(c)}
    b0 = model.query(0, h)
    require(any(at_identity(row) for row in b0), "nonzero B0 at identity")
    require(not any(model.query(1, h)), "B1 kernel")
    require(not any(model.query(extra_stage, h)), "extra observation kernel")
    initial_a = model.inject(0, A, b0)
    x, y = h.copy(), [{} for _ in range(112)]
    for p in A:
        x[p] = {} if omit_initial_correction else linear((-1, initial_a[p]))
        y[p] = linear((-1, x[p]))
    required_input = [str(at_identity(x[p])) for p in A]
    require(any(at_identity(x[p]) for p in A), "nonzero required original A")
    x, y, f0 = model.forward(0, x, y)
    require(not any(f0), "zero f0")
    require(all(not x[p] and not y[p] for p in A + T), "selected zero after F0")
    x, y = model.backward(1, 2, x, y)
    require(not any(x) and y == h, "exact first-pair output")
    banks = [[x, y]] + [[[{ } for _ in range(112)], [{ } for _ in range(112)]] for _ in range(3)]
    histories = {0: f0}
    trajectory = []
    recipe = template["recipe"]
    require(recipe[:2] == [{"kind": "local", "pair": 0, "reverse": False, "stage": 0},
                           {"kind": "local", "pair": 0, "reverse": True, "stage": 1}],
            "fixed first pair")
    for event in recipe[2:]:
        if omit_minus and event == {"kind": "bridge", "src": 1, "dst": 0, "coefficient": -1}:
            continue
        kind = event["kind"]
        if kind == "bridge":
            src, dst, c = event["src"], event["dst"], event["coefficient"]
            for p in U:
                banks[dst][0][p] = linear((1, banks[dst][0][p]), (c, banks[src][0][p]))
                banks[src][1][p] = linear((1, banks[src][1][p]), (-c, banks[dst][1][p]))
            record = dict(event)
        elif kind == "local":
            stage, pair = event["stage"], event["pair"]
            bx, by = banks[pair]
            if event["reverse"]:
                banks[pair] = list(model.backward(stage, stage + 1, bx, by))
            else:
                bx, by, f = model.forward(stage, bx, by)
                banks[pair] = [bx, by]
                histories[stage] = f
            record = {"kind": "local", "stage": stage}
        else:
            require(kind == "terminal", "retained schedule alphabet")
            # The completed-X descendants are the pre-exchange X fields.
            require(not any(row for bx, _ in banks for row in bx), "completed-X descendants")
            banks = [[by, [linear((-1, row)) for row in bx]] for bx, by in banks]
            record = {"kind": "terminal"}
        require(not any(fields[p] for pair in banks for fields in pair for p in A + T),
                "selected outputs stay zero")
        # Each ordinary bank is an exact scalar multiple of the entire h field.
        ordinary = []
        for pair in banks:
            for fields in pair:
                multiplier = next((c for c in (0, 1, -1) if all(
                    fields[p] == linear((c, h[p])) for p in U)), None)
                require(multiplier is not None, "ordinary trajectory closure")
                ordinary.append(multiplier)
        record["ordinary"] = ordinary
        trajectory.append(record)
    require(trajectory == previous["trajectory_after_B1"], "retained full tail trajectory")
    require(sorted(histories) == [0, 2, 4, 6, 8] and not any(
        row for query in histories.values() for row in query), "all five forward histories")
    require(banks[0][0] == h and not any(row for pair in banks[1:] for fields in pair for row in fields),
            "only old-Y-typed final X0 survives")
    require(not any(row for _, by in banks for row in by), "zero final completed-X descendants")
    if wrong_endpoint:
        require(not any(row for bx, _ in banks for row in bx), "wrong old-Y endpoint observation")
    return {
        "B0_h_at_identity": [str(at_identity(row)) for row in b0],
        "required_initial_X_A_at_identity": required_input,
        "zero_observations": ["all selected endpoints", "all completed-X descendants",
                              "f0", "f2", "f4", "f6", "f8", "pre-F0 B2 X_U"],
        "tail_trajectory": trajectory,
        "surviving_unobserved_endpoint": "final X0_U=h, with old-Y native type",
    }


def rejecting(name, action, controls):
    try:
        action()
    except ValueError:
        controls.append(name)
    else:
        raise ValueError("negative control accepted: " + name)


def build_result():
    members, certificate, previous = load_sources()
    word = members["CANONICAL-WORD.json.gz"]
    R = reconstruct_R(word, members["LOCAL-PROGRAMS.json.gz"])
    require(R == [[Q(row.get(str(p), "0")) for p in range(112)]
                  for row in certificate["R_rows"]], "operation-derived R equals QQ16 input")
    require((certificate["A_ports"], certificate["T_ports"], certificate["U_ports"])
            == (list(A), list(T), list(U)), "actual selected and ordinary ports")
    require(all(sum(R[i][p] * R[j][p] for p in U) == (48 if i == j else 0)
                for i in range(8) for j in range(8)), "ordinary Gram")
    require(all(sum(R[k][p] * c for p, c in COEFFICIENTS.items()) == 0 for k in range(8)),
            "three-column exact dependency")
    phases = members["DATA-PHASES.json"]
    model = Model(R, phases)
    template = members["GLOBAL-TEMPLATE.json.gz"]
    require(all(phases["recipes"][p]["q"] == word["ports"][p] for p in range(112)),
            "phase/root binding")
    recipe_calls = {(e["stage"], e["pair"], "backward" if e["reverse"] else "forward")
                    for e in template["recipe"] if e["kind"] == "local"}
    require(recipe_calls == {(c["stage"], c["pair"], c["orientation"]) for c in template["calls"]},
            "recipe/hosted-call binding")
    result = experiment(model, template, previous)
    # Stronger than required: this h has zero query in all eight nonzero charts.
    h = [{model.bases[p][0]: Q(COEFFICIENTS[p])} if p in COEFFICIENTS else {} for p in range(112)]
    require(all(not any(model.query(s, h)) for s in range(1, 9)), "all nonzero-stage kernels")
    controls = []
    cases = [
        ("changed dependency coefficient", {"coefficients": {2: -1, 8: 1, 85: -1}}),
        ("changed chart axis", {"axis_mutation": True}),
        ("missing initial A cancellation", {"omit_initial_correction": True}),
        ("missing first negative bridge", {"omit_minus": True}),
        ("old-Y endpoint mislabeled as completed-X", {"wrong_endpoint": True}),
        ("B0 observation detects this witness", {"extra_stage": 0}),
    ]
    for name, options in cases:
        rejecting(name, lambda options=options: experiment(model, template, previous, **options), controls)
    rejecting("owner action replaced by payload-only action",
              lambda: experiment(Model(R, phases, ignore_owner=True), template, previous), controls)
    rejecting("source-byte mutation", lambda: authenticate(b"changed", INPUTS[CERTIFICATE], CERTIFICATE), controls)
    return {
        "schema": "qq16-b2-observation-kernel-v1",
        "status": "PASS_QQ16_B2_OBSERVATION_KERNEL",
        "proof_inputs": INPUTS,
        "archive_members": MEMBERS,
        "source_R_sha256": sha256(canonical([[str(x) for x in row] for row in R]).encode()).hexdigest(),
        "witness": {"definition": "h_p(d)=c_p bit_0(d b_(p,0)), constant in every payload coordinate",
                    "coefficients": {str(p): c for p, c in COEFFICIENTS.items()},
                    "axes": {str(p): model.bases[p][0] for p in COEFFICIENTS},
                    "vanishing_stages": list(range(1, 9))},
        "observation_audit": result,
        "rejecting_controls": controls,
        "scope": "Fixed first pair and ordinary schedule; exact B2 pre-read added. No changed feedback, native read, supplier, new kappa, or formal-kernel claim.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", type=Path, help="Create a new receipt exclusively; never overwrite")
    args = parser.parse_args()
    result = build_result()
    if args.emit_result is not None:
        with args.emit_result.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        recorded = json.loads((PACKAGE / "RESULT.json").read_text())
        require(canonical(recorded) == canonical(result), "complete canonical result equality")
    print(result["status"])
    print("3 ordinary ports; B1h=B2h=0; original A nonzero; 8 zero observations; 8 rejecting controls")


if __name__ == "__main__":
    main()
