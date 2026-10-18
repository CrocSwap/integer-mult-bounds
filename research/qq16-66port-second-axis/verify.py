#!/usr/bin/env python3
"""QQ16 66-port counterexample; exact sums of f_v(d)=bit_0(d v).

Empty sums prove identities; evaluation proves inequality. Independence of
the f_v is never assumed. No predecessor Python is imported. Apache-2.0.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
import argparse
from copy import deepcopy
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
PREVIOUS = "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
MEMBERS = {
    "t16/global/base/work/complex-nine-native/DATA-PHASES.json":
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz":
        "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518",
}
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = [p for p in range(112) if p not in A + T]
UNREAD = [44, 45, 48, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60,
          61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 77]
READ = [p for p in U if p not in UNREAD]
COEFFICIENTS = {44: -1, 49: -1, 58: -1, 70: 1}
IDENTITY = tuple(1 << i for i in range(73))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def equal_receipt(actual, expected):
    require(canonical(actual) == canonical(expected), "complete typed receipt mismatch")


def authenticate(raw, pin, label):
    require(sha256(raw).hexdigest() == pin, "source hash mismatch: " + label)
    return raw


def sources(root=ROOT):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    pins = {f["path"]: f["sha256"] for f in manifest["files"] if f["usage"] == "input"}
    require(set(pins) == {ARCHIVE, PACKET, PREVIOUS,
                         "research/joint-query/evidence/CONSERVED-QQ16.md",
                         "research/joint-query/evidence/JOINT-QUERY-TRANSFER.md",
                         "research/joint-query/evidence/QQ16-COVER-ACTION-ADDENDUM.md"},
            "complete declared source set")
    raw = {name: authenticate((root / name).read_bytes(), pin, name)
           for name, pin in pins.items()}
    decoded = []
    with tarfile.open(fileobj=BytesIO(raw[ARCHIVE]), mode="r:gz") as archive:
        for name, pin in MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            require(len(matches) == 1 and matches[0].isfile(), "unique regular archive member")
            data = authenticate(archive.extractfile(matches[0]).read(), pin, name)
            decoded.append(json.loads(gzip.decompress(data) if name.endswith(".gz") else data))
    return (json.loads(gzip.decompress(raw[PACKET])), *decoded,
            json.loads(raw[PREVIOUS]), pins)


def combination(terms):
    """Rational linear combination of dictionaries representing f_v functions."""
    out = {}
    for scale, function in terms:
        for v, coefficient in function.items():
            value = out.get(v, Q(0)) + scale * coefficient
            if value:
                out[v] = value
            else:
                out.pop(v, None)
    return out


def action(columns, vector):
    result = 0
    for i, column in enumerate(columns):
        if (vector >> i) & 1:
            result ^= column
    return result


def transport(function, columns):
    return combination((coefficient, {action(columns, v): Q(1)})
                       for v, coefficient in function.items())


def evaluate(function, owner=IDENTITY):
    return sum((c * (action(owner, v) & 1) for v, c in function.items()), Q(0))


def serialize(function):
    return {str(v): str(c) for v, c in sorted(function.items())}


def zero_bank():
    return [{} for _ in range(112)]


def derive_routes(packet, phases):
    require(phases["m"] == 73 and len(phases["recipes"]) == 112, "source dimensions")
    registered = {tuple(m["owner_right_matrix_columns"])
                  for m in packet["map_registry"].values()}
    bases, routes = [], {}
    for p, record in enumerate(phases["recipes"]):
        basis = record["idle_children"][0]["orthogonal_axes"][:8]
        local = [record["q"], *basis]
        require(record["port"] == p and len(local) == 9, "source port binding")
        require(all(0 < v < 512 for v in local), "local chart support")
        require(all(((v & w).bit_count() % 2) == int(i == j)
                    for i, v in enumerate(local) for j, w in enumerate(local)),
                "orthonormal local chart")
        bases.append(basis)
        for s in range(9):
            columns = list(IDENTITY)
            if s:
                for i, b in enumerate(basis):
                    delta = b ^ (1 << (9 + 8 * (s - 1) + i))
                    columns = [v ^ delta if (v & delta).bit_count() % 2 else v
                               for v in columns]
            columns = tuple(columns)
            require(columns in registered, "route missing from native map registry")
            require(all(action(columns, columns[i]) == IDENTITY[i] for i in range(73)),
                    "route inverse")
            require(action(columns, record["q"]) == record["q"], "route fixes port line")
            if s:
                require(all(action(columns, b) == 1 << (9 + 8 * (s - 1) + i)
                            for i, b in enumerate(basis)), "all-axis route identity")
            routes[s, p] = columns
    require([p for p in U if bases[p][0] == 2] == UNREAD,
            "PR2354 exact attaining unread set")
    return bases, routes


class Model:
    """Ordered logical maps from the retained conserved QQ16 contract."""
    def __init__(self, packet, routes):
        require((packet["A_ports"], packet["T_ports"], packet["U_ports"]) == (A, T, U),
                "QQ16 partition")
        self.R = [[Q(row.get(str(p), "0")) for p in range(112)] for row in packet["R_rows"]]
        require(len(self.R) == 8, "query width")
        self.routes = routes
        for ports, scale in ((A, 4), (T, 4), (U, 48)):
            require(all(sum(self.R[i][p] * self.R[j][p] for p in ports)
                        == (scale if i == j else 0) for i in range(8) for j in range(8)),
                    "actual selected and ordinary Grams")

    def query(self, fields, stage, ports=range(112)):
        return [combination((row[p], transport(fields[p], self.routes[stage, p]))
                            for p in ports) for row in self.R]

    def inject(self, query, stage, ports):
        fields = zero_bank()
        for p in ports:
            value = combination((self.R[k][p] / 4, query[k]) for k in range(8))
            fields[p] = transport(value, self.routes[stage, p])
        return fields

    def forward(self, x, y, stage):
        f = self.query(x, stage)
        k = self.inject(f, stage, U)
        old_t = self.inject(self.query(x, stage, T), stage, A)
        new_t = self.inject(f, stage, T)
        xx, yy = zero_bank(), zero_bank()
        for p in U:
            xx[p] = combination([(1, x[p]), (-1, k[p])])
            yy[p] = combination([(1, y[p]), (1, xx[p])])
        for p in A + T:
            xx[p] = old_t[p] if p in A else new_t[p]
            yy[p] = combination([(1, x[p]), (1, y[p]), (-1, xx[p])])
        return xx, yy, f

    def backward(self, x, y, stage, future):
        q = self.query(y, future, U + T)
        logger = self.inject(q, future, A)
        u = [combination([(1, yy), (1, ll)]) for yy, ll in zip(y, logger)]
        a = self.query(x, stage, T)
        b = self.query(u, stage)
        ku = self.inject(a, stage, U)
        correction = self.inject([combination([(1, bb), (11, aa)])
                                  for aa, bb in zip(a, b)], stage, T)
        target = self.inject([combination([(1, bb), (12, aa)])
                              for aa, bb in zip(a, b)], stage, T)
        xx, yy = zero_bank(), zero_bank()
        for p in U:
            xx[p] = combination([(1, x[p]), (-1, y[p])])
            yy[p] = combination([(1, y[p]), (1, ku[p])])
        for p in A:
            xx[p] = combination([(1, x[p]), (1, y[p]), (-1, u[p])])
            yy[p] = u[p]
        for p in T:
            xx[p] = target[p]
            yy[p] = combination([(1, u[p]), (-1, correction[p])])
        return xx, yy


def bind_schedule(recipe, calls):
    require(recipe[:2] == [{"kind": "local", "pair": 0, "reverse": False, "stage": 0},
                           {"kind": "local", "pair": 0, "reverse": True, "stage": 1}],
            "fixed F0/B1 first pair")
    scheduled = {(e["stage"], e["pair"], "backward" if e["reverse"] else "forward")
                 for e in recipe if e["kind"] == "local"}
    require(scheduled == {(c["stage"], c["pair"], c["orientation"]) for c in calls},
            "local stage/pair/orientation differs from hosted template")


def replay(model, template, h, reads=READ, initial_sign=-1):
    H = model.query(h, 0)
    require(any(evaluate(f) for f in H), "old-chart defect is not witnessed at identity")
    for stage in range(1, 9):
        require(not any(model.query(h, stage)), "later query does not vanish identically")
    selected = model.inject(H, 0, A)
    x, y = deepcopy(h), zero_bank()
    for p in A:
        x[p] = combination([(initial_sign, selected[p])])
        y[p] = combination([(-initial_sign, selected[p])])
    initial_A = [x[p] for p in A]
    require(any(evaluate(f) for f in initial_A), "nonzero original selected input")
    banks = [[x, y]] + [[zero_bank(), zero_bank()] for _ in range(3)]
    trace, histories = [], []
    bind_schedule(template["recipe"], template["calls"])
    for index, event in enumerate(template["recipe"]):
        kind = event["kind"]
        if kind == "local":
            pair, stage = event["pair"], event["stage"]
            x, y = banks[pair]
            if event["reverse"]:
                banks[pair] = list(model.backward(x, y, stage, stage + 1))
            else:
                xx, yy, f = model.forward(x, y, stage)
                require(not any(f), "forward history is nonzero")
                histories.append(stage)
                banks[pair] = [xx, yy]
        elif kind == "bridge":
            source, target, c = event["src"], event["dst"], event["coefficient"]
            for p in U:
                banks[target][0][p] = combination([(1, banks[target][0][p]),
                                                   (c, banks[source][0][p])])
                banks[source][1][p] = combination([(1, banks[source][1][p]),
                                                   (-c, banks[target][1][p])])
        else:
            require(kind == "terminal" and index == len(template["recipe"]) - 1,
                    "unique final terminal")
            banks = [[y, [combination([(-1, f)]) for f in x]] for x, y in banks]
        require(not any(fields[p] for pair in banks for fields in pair for p in A + T),
                "selected output survives")
        require(not any(fields[p] for pair in banks for fields in pair for p in reads),
                "ordinary read transcript is nonzero")
        if index >= 1:
            completed_side = 1 if kind == "terminal" else 0
            require(not any(pair[completed_side][p] for pair in banks for p in U),
                    "completed-X descendant is nonzero")
        multipliers = []
        for pair in banks:
            for fields in pair:
                candidates = [c for c in (-1, 0, 1)
                              if all(fields[p] == combination([(c, h[p])]) for p in U)]
                require(len(candidates) == 1, "ordinary trajectory not a unique h multiple")
                multipliers.append(candidates[0])
        trace.append({"event": event, "ordinary": multipliers})
    require(histories == [0, 2, 4, 6, 8], "all five forward histories")
    require(trace[-1]["ordinary"] == [1, 0, 0, 0, 0, 0, 0, 0], "former-Y endpoint")
    return initial_A, H, trace


def build_result():
    packet, phases, template, previous, pins = sources()
    bases, routes = derive_routes(packet, phases)
    model = Model(packet, routes)
    h = zero_bank()
    for p, c in COEFFICIENTS.items():
        h[p] = {bases[p][1]: Q(c)}
    require([bases[p][1] for p in COEFFICIENTS] == [25, 145, 4, 4], "second axes")
    coefficient_sum = [sum(row[p] * c for p, c in COEFFICIENTS.items()) for row in model.R]
    require(coefficient_sum == [0] * 8, "four-column rational relation")
    initial_A, H, trace = replay(model, template, h)
    require([entry["ordinary"] for entry in trace[2:]] ==
            [entry["ordinary"] for entry in previous["trajectory_after_B1"]],
            "retained ordinary-tail receipt")
    require([evaluate(f) for f in H] == [-1, 0, -1, 0, 0, -1, 0, -1],
            "explicit nonzero old-chart value")
    controls = []

    def rejects(name, check):
        try:
            check()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("mutation was not rejected: " + name)

    bad_h = deepcopy(h)
    bad_h[70] = {bases[70][1]: Q(-1)}
    rejects("flip coefficient on port 70", lambda: replay(model, template, bad_h))
    first_h = zero_bank()
    for p, c in COEFFICIENTS.items():
        first_h[p] = {bases[p][0]: Q(c)}
    rejects("reuse first axis with no original defect", lambda: replay(model, template, first_h))
    rejects("reverse initial A cancellation sign", lambda: replay(model, template, h, initial_sign=1))
    rejects("add a read of witness port 44", lambda: replay(model, template, h, reads=READ + [44]))
    wrong_routes = dict(routes)
    wrong_routes[1, 44] = IDENTITY
    rejects("omit owner action at one source", lambda: replay(Model(packet, wrong_routes), template, h))
    wrong = deepcopy(template)
    wrong["recipe"] = [e for e in wrong["recipe"] if e !=
                       {"kind": "bridge", "src": 1, "dst": 0, "coefficient": -1}]
    rejects("omit cancelling bridge", lambda: replay(model, wrong, h))
    wrong = deepcopy(template)
    next(e for e in wrong["recipe"] if e.get("stage") == 2)["pair"] = 1
    rejects("wrong F2 bank binding", lambda: replay(model, wrong, h))
    rejects("observe former-Y terminal output", lambda: require(not any(h), "extra final read sees h"))
    require(evaluate(h[44]) == -1, "additional port-44 read detects this witness")
    require(any(evaluate(f) for f in H), "dense old-chart positive detection control")
    return {
        "schema": "qq16-66port-second-axis-v1", "status": "PASS_QQ16_66PORT_SECOND_AXIS",
        "source_sha256": pins, "archive_members": MEMBERS,
        "read_ports": READ, "unread_ports": UNREAD, "observed_port_count": len(READ),
        "local_axis_zero_based": 1,
        "support": [{"port": p, "coefficient": c, "axis": bases[p][1],
                     "R_column": [str(row[p]) for row in model.R]} for p, c in COEFFICIENTS.items()],
        "coefficient_sum": [str(x) for x in coefficient_sum],
        "old_chart_query": [serialize(f) for f in H],
        "old_chart_at_identity": [str(evaluate(f)) for f in H],
        "initial_A": [serialize(f) for f in initial_A],
        "initial_A_at_identity": [str(evaluate(f)) for f in initial_A],
        "registered_port_stage_routes": len(routes), "common_axis_checks": 112 * 8 * 8,
        "zero_later_queries": list(range(1, 9)), "zero_forward_histories": [0, 2, 4, 6, 8],
        "trace": trace, "rejected_controls": controls,
        "positive_controls": ["extra port-44 read detects witness", "dense initial B0 query detects witness"],
        "scope": "specified read set only; no other 66-port-set or minimum-tap claim; no new kappa",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", type=Path, help="write a new receipt exclusively")
    args = parser.parse_args()
    result = build_result()
    if args.emit_result:
        with args.emit_result.open("x", encoding="utf-8") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        equal_receipt(result, json.loads((PACKAGE / "RESULT.json").read_text()))
    print("PASS_QQ16_66PORT_SECOND_AXIS support=4 observed_ports=66 stages=9 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
