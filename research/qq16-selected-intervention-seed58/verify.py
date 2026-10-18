#!/usr/bin/env python3
"""Exact QQ16 selected-only intervention checks; proof and scope in README.md.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Witness: Adam Gall, PR2093. QQ16 maps/routes: Ali Romman, PR1969.
No predecessor executable is imported. Universal claims rest on the proof.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
from io import BytesIO
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKET = "research/joint-query/certificate.json.gz"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
TAIL = "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
PHASES = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
TEMPLATE = "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz"
MEMBER_PINS = {
    PHASES: "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    TEMPLATE: "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518",
}
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
S = A + T
U = tuple(p for p in range(112) if p not in S)
MARKER = "PASS_QQ16_SELECTED_INTERVENTION_OBSTRUCTION"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def constant(value):
        raise ValueError("nonfinite JSON constant: " + value)

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def authenticate(raw, expected):
    require(hashlib.sha256(raw).hexdigest() == expected, "source digest mismatch")
    return raw


def load_sources(root):
    manifest = read_json((HERE / "SOURCES.json").read_bytes())
    raw = {e["path"]: authenticate((root / e["path"]).read_bytes(), e["sha256"])
           for e in manifest["files"] if e["usage"] == "input"}
    members = {}
    with tarfile.open(fileobj=BytesIO(raw[ARCHIVE]), mode="r:gz") as archive:
        for name, pin in MEMBER_PINS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            require(len(matches) == 1 and matches[0].isfile(), "unique regular member: " + name)
            data = authenticate(archive.extractfile(matches[0]).read(), pin)
            members[name] = read_json(gzip.decompress(data) if name.endswith(".gz") else data)
    return read_json(gzip.decompress(raw[PACKET])), members, read_json(raw[TAIL])


# Exact Walsh sums: chi_v(d)=(-1)^bit_0(d*v), chi_u*chi_v=chi_(u XOR v).
# Mask zero is constant one. Formal cancellation implies all-owner equality;
# independence of the functions on the restricted owner group is not assumed.
def linear(*terms):
    result = {}
    for scale, field in terms:
        for mask, value in field.items():
            result[mask] = result.get(mask, Q(0)) + scale * value
    return {mask: value for mask, value in result.items() if value}


def multiply(left, right):
    return linear(*((a * b, {u ^ v: Q(1)}) for u, a in left.items() for v, b in right.items()))


def at_identity(field):
    return sum(value * (-1 if mask & 1 else 1) for mask, value in field.items())


def zero_ports():
    return [{} for _ in range(112)]


def zero_banks():
    return [[zero_ports(), zero_ports()] for _ in range(4)]


def difference(left, right):
    return [[[linear((1, a), (-1, b)) for a, b in zip(lf, rf)]
             for lf, rf in zip(lp, rp)] for lp, rp in zip(left, right)]


class Model:
    def __init__(self, packet, phases):
        require((packet["A_ports"], packet["T_ports"], packet["U_ports"])
                == (list(A), list(T), list(U)), "port partition")
        self.r = [[Q(row.get(str(p), "0")) for p in range(112)] for row in packet["R_rows"]]
        require(len(self.r) == 8, "query dimension")
        for ports, gram in ((A, 4), (T, 4), (U, 48)):
            require(all(sum(self.r[i][p] * self.r[j][p] for p in ports)
                        == gram * (i == j) for i in range(8) for j in range(8)), "Gram/section identity")
        require(phases["m"] == 73 and len(phases["recipes"]) == 112, "route dimension")
        self.bases = [r["idle_children"][0]["orthogonal_axes"][:8] for r in phases["recipes"]]
        registry = {tuple(r["owner_right_matrix_columns"]) for r in packet["map_registry"].values()}
        self.routes = []
        for p, basis in enumerate(self.bases):
            local = [phases["recipes"][p]["q"]] + basis
            require(all(0 < x < 512 for x in local), "first local block")
            require(all((a & b).bit_count() % 2 == (i == j)
                        for i, a in enumerate(local) for j, b in enumerate(local)), "orthonormal local axes")
            stages = []
            for s in range(9):
                swaps = [] if s == 0 else [b ^ (1 << (9 + 8 * (s - 1) + i)) for i, b in enumerate(basis)]
                columns = tuple(self.transvections(1 << i, swaps) for i in range(73))
                require(columns in registry, "actual route absent from packet registry")
                require(all(self.action(columns, c) == 1 << i for i, c in enumerate(columns)), "route inverse")
                if s:
                    require(all(self.action(columns, b) == 1 << (9 + 8 * (s - 1) + i)
                                for i, b in enumerate(basis)), "common stage axes")
                stages.append(columns)
            self.routes.append(stages)

    @staticmethod
    def transvections(vector, swaps):
        result = vector
        for swap in swaps:
            if (vector & swap).bit_count() % 2:
                result ^= swap
        return result

    @staticmethod
    def action(columns, vector):
        result = 0
        for i, column in enumerate(columns):
            if (vector >> i) & 1:
                result ^= column
        return result

    def route(self, stage, port, field):
        return linear(*((value, {self.action(self.routes[port][stage], mask): Q(1)})
                        for mask, value in field.items()))

    def query(self, stage, fields, ports=tuple(range(112))):
        routed = {p: self.route(stage, p, fields[p]) for p in ports if fields[p]}
        return [linear(*((self.r[k][p], field) for p, field in routed.items())) for k in range(8)]

    def inject(self, stage, ports, query):
        result = zero_ports()
        for p in ports:
            result[p] = self.route(stage, p, linear(*((self.r[k][p] / 4, query[k]) for k in range(8))))
        return result

    def forward(self, stage, x, y):
        f, c = self.query(stage, x), self.query(stage, x, T)
        ku = self.inject(stage, U, f)
        pa, pt = self.inject(stage, A, c), self.inject(stage, T, f)
        xx = [pa[p] if p in A else pt[p] if p in T else linear((1, x[p]), (-1, ku[p])) for p in range(112)]
        yy = [linear((1, x[p]), (1, y[p]), (-1, xx[p])) if p in S
              else linear((1, y[p]), (1, xx[p])) for p in range(112)]
        return [xx, yy], f

    def backward(self, stage, future, x, y):
        # Ordered E / exchange / H factorization followed by conservation;
        # separate from the direct row formulas in CONSERVED-QQ16 equation (1).
        encoded_a = self.inject(future, A, self.query(future, y))
        u = [encoded_a[p] if p in A else y[p] for p in range(112)]
        a, b = self.query(stage, x, T), self.query(stage, u)
        exchange = self.inject(stage, T, [linear((1, a[k]), (-1, b[k])) for k in range(8)])
        v = [linear((1, u[p]), (1, exchange[p])) for p in range(112)]
        rv = self.query(stage, v)
        require(rv == a, "ordered full-query exchange")
        ordinary, selected = self.inject(stage, U, rv), self.inject(stage, T, rv)
        yy = [linear((1, v[p]), (1, ordinary[p]), (-12, selected[p])) for p in range(112)]
        xx = [linear((1, x[p]), (1, y[p]), (-1, yy[p])) if p in S
              else linear((1, x[p]), (-1, y[p])) for p in range(112)]
        return [xx, yy]


def witness(model, bad_sign=False, bad_axis=False, omit_correction=False):
    h = zero_ports()
    for p, c in ((2, -1), (8, 1), (85, -1 if bad_sign else 1)):
        h[p] = {model.bases[p][1 if bad_axis and p == 2 else 0]: Q(c)}
    require([model.bases[p][0] for p in (2, 8, 85)] == [37, 38, 506], "credited witness axes")
    require(all(not any(model.query(s, h)) for s in range(1, 9)), "nonzero-chart common kernel")
    b0 = model.query(0, h)
    require(any(at_identity(x) for x in b0), "old-chart witness is nonzero")
    banks = zero_banks()
    banks[0][0] = deepcopy(h)
    correction = model.inject(0, A, b0)
    for p in A:
        banks[0][0][p] = {} if omit_correction else linear((-1, correction[p]))
        banks[0][1][p] = linear((-1, banks[0][0][p]))
    after, f = model.forward(0, *banks[0])
    require(not any(f) and all(not field[p] for field in after for p in S), "selected state equal after F0")
    require(after == [h, h], "ordinary state after F0")
    return banks, h


def intervention(banks, helper, mode, index):
    # Reversible selected-only shears, with a common dirty helper retained.
    # Nonlinear modes are deliberately stronger than the native linear model.
    if mode == "none" or (mode == "pr2216" and index != 0):
        return
    for j, (a, t) in enumerate(zip(A, T)):
        x, y = banks[0]
        amount = x[a]
        if mode == "affine":
            amount = linear((1, amount), (index + j + 1, helper))
        elif mode == "nonlinear":
            amount = linear((1, multiply(amount, amount)), (index + j + 1, helper))
        elif mode == "ordinary_read":
            amount = linear((1, amount), (1, banks[0][0][2]))
        x[t], y[t] = linear((1, x[t]), (1, amount)), linear((1, y[t]), (-1, amount))


def replay(model, recipe, initial, mode="none", dirty=False, omit_minus=False):
    base = zero_banks()
    if dirty:
        for b, pair in enumerate(base):
            for side, fields in enumerate(pair):
                for p in range(112):
                    n = (58 + 3 * b + 5 * side + p) % 7 - 3
                    fields[p] = {0: Q(n)} if n else {}
    other = [[[linear((1, x), (1, delta)) for x, delta in zip(fields, change)]
              for fields, change in zip(pair, dif)] for pair, dif in zip(base, initial)]
    helper = {0: Q(3)}
    trace, histories = [], []
    for index, event in enumerate(recipe):
        if omit_minus and event == {"kind": "bridge", "src": 1, "dst": 0, "coefficient": -1}:
            continue
        for banks in (base, other):
            if event["kind"] == "local":
                s, b = event["stage"], event["pair"]
                if event["reverse"]:
                    banks[b] = model.backward(s, s + 1, *banks[b])
                else:
                    banks[b], f = model.forward(s, *banks[b])
                    if banks is base:
                        base_f = f
                    else:
                        require(f == base_f, "forward histories differ")
                        histories.append(s)
            elif event["kind"] == "bridge":
                src, dst, c = event["src"], event["dst"], event["coefficient"]
                for p in U:
                    banks[dst][0][p] = linear((1, banks[dst][0][p]), (c, banks[src][0][p]))
                    banks[src][1][p] = linear((1, banks[src][1][p]), (-c, banks[dst][1][p]))
            else:
                require(event["kind"] == "terminal", "schedule event")
                banks[:] = [[y, [linear((-1, f)) for f in x]] for x, y in banks]
        require(all(base[b][side][p] == other[b][side][p]
                    for b in range(4) for side in range(2) for p in S), "selected observation differs before intervention")
        for banks in (base, other):
            intervention(banks, helper, mode, index)
        require(all(base[b][side][p] == other[b][side][p]
                    for b in range(4) for side in range(2) for p in S), "selected observation differs after intervention")
        trace.append(difference(other, base))
    require(histories == [0, 2, 4, 6, 8], "five actual forward histories")
    require(all(not field for pair in trace[-1] for field in pair[1]), "completed-X endpoint differs")
    return trace, trace[-1]


def rejecting(label, action):
    try:
        action()
    except ValueError:
        return label
    raise ValueError("negative control accepted: " + label)


def bind_schedule(template):
    recipe = template["recipe"]
    require(len(recipe) == 19 and [e["pair"] for e in recipe if e["kind"] == "local"]
            == [0, 0, 0, 1, 1, 2, 2, 3, 3], "complete schedule/pair binding")
    require({(e["stage"], e["pair"], "backward" if e["reverse"] else "forward")
             for e in recipe if e["kind"] == "local"}
            == {(e["stage"], e["pair"], e["orientation"]) for e in template["calls"]}, "hosted-call binding")
    return recipe


def build_result(root):
    packet, members, previous = load_sources(root)
    model = Model(packet, members[PHASES])
    template = members[TEMPLATE]
    recipe = bind_schedule(template)
    initial, h = witness(model)
    baseline_trace, delta = replay(model, recipe, initial)
    expected_final = zero_banks()
    expected_final[0][0] = h
    require(delta == expected_final, "only former-Y final X0 differs")
    tail = []
    for event, dif in zip(recipe[2:], baseline_trace[2:]):
        ordinary = []
        for pair in dif:
            for fields in pair:
                matches = [c for c in (0, 1, -1) if all(fields[p] == linear((c, h[p])) for p in U)]
                require(len(matches) == 1, "unique formal tail multiplier")
                ordinary.append(matches[0])
        row = ({"kind": "local", "stage": event["stage"]} if event["kind"] == "local"
               else {"kind": "terminal"} if event["kind"] == "terminal" else dict(event))
        row["ordinary"] = ordinary
        tail.append(row)
    require(tail == previous["trajectory_after_B1"], "all retained tail states")
    fixtures = []
    for mode, dirty in (("pr2216", False), ("pr2216", True), ("affine", True), ("nonlinear", True)):
        trace, endpoint = replay(model, recipe, initial, mode, dirty)
        require(trace == baseline_trace and endpoint == expected_final, "two-run difference invariant")
        fixtures.append({"intervention": mode, "dirty_background": dirty,
                         "boundary_states_checked": len(trace), "histories_equal": 5,
                         "selected_fields_equal_at_each_boundary": 128})
    wrong_template = deepcopy(template)
    wrong_template["recipe"][3]["pair"] = 1
    controls = [rejecting(name, action) for name, action in (
        ("dependency sign", lambda: witness(model, bad_sign=True)),
        ("local axis", lambda: witness(model, bad_axis=True)),
        ("missing initial A correction", lambda: witness(model, omit_correction=True)),
        ("missing cancelling bridge", lambda: replay(model, recipe, initial, omit_minus=True)),
        ("wrong F2 pair source binding", lambda: bind_schedule(wrong_template)),
        ("ordinary-reading intervention detects witness", lambda: replay(model, recipe, initial, "ordinary_read")),
        ("old-Y endpoint mislabelled completed-X", lambda: require(not any(delta[0][0]), "old-Y is not an observation")),
        ("B0 query detects witness", lambda: require(not any(model.query(0, h)), "old chart separates inputs")),
        ("changed source bytes", lambda: authenticate(b"mutated", MEMBER_PINS[PHASES])),
    )]
    return {
        "schema": "qq16-selected-intervention-v1", "status": MARKER,
        "scope": "Fixed local QQ16 maps and ordinary schedule; selected-only interventions after F0; no new kappa",
        "route_bindings": 1008, "query_gram": 48,
        "witness": {"predecessor": "PR2093", "representation": "Walsh-character variant of the credited three-port witness",
                    "ordinary_ports": [2, 8, 85], "axes": [37, 38, 506], "coefficients": [-1, 1, 1],
                    "query_columns": {str(p): [str(model.r[k][p]) for k in range(8)] for p in (2, 8, 85)},
                    "zero_query_stages": list(range(1, 9)),
                    "initial_X_A_at_identity": [str(at_identity(initial[0][0][p])) for p in A],
                    "B0_h_at_identity": [str(at_identity(x)) for x in model.query(0, h)]},
        "schedule_events": len(recipe), "tail_trajectory": tail,
        "two_execution_fixtures": fixtures, "negative_controls_rejected": controls,
        "favorable_cost_screen": "Infeasible with all added operations free; no valid restoration recurrence",
        "archive_members": MEMBER_PINS,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true", help="explicitly regenerate RESULT.json")
    args = parser.parse_args()
    result = build_result(args.root)
    target = HERE / "RESULT.json"
    if args.write:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(read_json(target.read_bytes()) == result, "complete result mismatch")
    print(MARKER)
    print("3-port witness; 1008 routes; 19 events; 4 two-run fixtures; 9 rejecting controls; no new kappa")


if __name__ == "__main__":
    main()
