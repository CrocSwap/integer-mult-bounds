#!/usr/bin/env python3
"""Ordered QQ16 two-query recovery; exact standard-library checks.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. F/B maps and schedule: Ali Romman, PR1969. No predecessor
executable is imported. PROOF.md states the quantified claim.
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
TAIL = "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
RECIPE = "research/community-reconciliation-third100-audit/regenerated/pr377-outputs/work/odd-stages/RECIPE-9.json.gz"
TEMPLATE_MEMBER = "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz"
TEMPLATE_SHA256 = "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518"
MARKER = "PASS_QQ16_TWO_QUERY_KERNEL"
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = [p for p in range(112) if p not in A + T]


class Failure(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Failure(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def constant(value):
        raise Failure("nonfinite JSON: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def load_sources(root):
    manifest = read_json((HERE / "SOURCES.json").read_bytes())
    raw = {}
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            data = (root / entry["path"]).read_bytes()
            need(digest(data) == entry["sha256"], "source digest: " + entry["path"])
            raw[entry["path"]] = data
    need({PACKET, TAIL, ARCHIVE, RECIPE} <= raw.keys(), "source inventory")
    return raw


def eye(n, scale=1):
    return [[Q(scale * (i == j)) for j in range(n)] for i in range(n)]


def tr(a):
    return [list(c) for c in zip(*a)]


def mv(a, v):
    need(all(len(row) == len(v) for row in a), "matrix/vector shape")
    return [sum(x*y for x, y in zip(row, v)) for row in a]


def mm(a, b):
    return tr([mv(a, c) for c in tr(b)])


def add(*vectors):
    need(vectors and len({len(v) for v in vectors}) == 1, "vector shape")
    return [sum(c) for c in zip(*vectors)]


def scale(c, v):
    return [c*x for x in v]


def sub(a, b):
    return add(a, scale(-1, b))


def rref(a):
    a = [list(map(Q, row)) for row in a]
    need(a and len({len(row) for row in a}) == 1, "rectangular matrix")
    pivots = []
    for j in range(len(a[0])):
        k = next((i for i in range(len(pivots), len(a)) if a[i][j]), None)
        if k is None:
            continue
        i = len(pivots)
        a[i], a[k] = a[k], a[i]
        c = a[i][j]
        a[i] = [x/c for x in a[i]]
        for k in range(len(a)):
            if k != i and a[k][j]:
                c = a[k][j]
                a[k] = [x-c*y for x, y in zip(a[k], a[i])]
        pivots.append(j)
        if len(pivots) == len(a):
            break
    return a, pivots


def inverse(a):
    n = len(a)
    out, pivots = rref([row+unit for row, unit in zip(a, eye(n))])
    need(pivots == list(range(n)), "selected inverse")
    return [row[n:] for row in out]


# Linear forms over a free NONCOMMUTATIVE operator algebra. A key is
# (ordered operator word, input symbol); these checks do not sample matrices.
def var(name):
    return {((), name): 1}


def lin(*terms):
    out = {}
    for coefficient, expression in terms:
        for key, value in expression.items():
            out[key] = out.get(key, 0) + coefficient*value
    return {key: value for key, value in out.items() if value}


def op(name, expression):
    return {((name,)+word, variable): value
            for (word, variable), value in expression.items()}


def expression_json(expression):
    return [[list(word), name, coefficient]
            for (word, name), coefficient in sorted(expression.items())]


def symbolic_decoder():
    z, w, a, c, pa, pt, f2 = map(var, ("z", "w", "a", "c", "pA", "pT", "f2"))
    q0, q2 = op("B0", z), op("B2", z)
    f = lin((1, q0), (1, a), (1, c))
    source_after_f = lin((1, w), (1, z), (-1, op("K0", f)))
    # D = ell_0,A P_2,A, E = ell_2,T P_0,T. Factors never commute.
    inside = lin((1, op("B2", source_after_f)), (1, op("E", lin((1, pt), (-1, f)))))
    d = lin((1, pa), (-1, c), (1, op("D", inside)))
    completed = lin((1, w), (1, op("K2", f2)))
    rw = lin((1, completed), (-1, op("K2", f2)))
    inner = lin((1, op("B2", rw)), (1, q2), (-1, op("B2", op("K0", f))),
                (1, op("E", lin((1, pt), (-1, f)))))
    rc = lin((1, pa), (-1, d), (1, op("D", inner)))
    ra = lin((1, f), (-1, q0), (-1, rc))
    residuals = [lin((1, rw), (-1, w)), lin((1, rc), (-1, c)), lin((1, ra), (-1, a))]
    need(all(not r for r in residuals), "free ordered recovery identity")
    base = lin((1, op("B2", rw)), (1, q2), (-1, op("B2", op("K0", f))))
    wrong = lin((1, pa), (-1, d), (1, op("D", base)),
                (1, op("E", op("D", lin((1, pt), (-1, f))))))
    need(wrong != c, "noncommutative-order control")
    need(lin((1, rc), (-1, op("D", q2))) != c, "missing second read control")
    return {"residual_term_counts": [len(r) for r in residuals],
            "backward_A_normal_form": expression_json(d),
            "completed_X_normal_form": expression_json(completed),
            "commuted_D_E_residual_terms": len(lin((1, wrong), (-1, c)))}


def bind_schedule(raw):
    # The old zero-witness receipt omits local pair assignments. Bind them to
    # the complete selected template, rather than guessing from stage parity.
    recipe = read_json(gzip.decompress(raw[RECIPE]))
    with tarfile.open(fileobj=BytesIO(raw[ARCHIVE]), mode="r:gz") as archive:
        matches = [m for m in archive.getmembers() if m.name == TEMPLATE_MEMBER]
        need(len(matches) == 1 and matches[0].isfile(), "one regular template member")
        member = archive.extractfile(matches[0]).read()
    need(digest(member) == TEMPLATE_SHA256, "selected template member")
    template = read_json(gzip.decompress(member))
    need(template["recipe"] == recipe, "selected and retained recipe agreement")
    need(recipe[:2] == [{"kind": "local", "pair": 0, "reverse": False, "stage": 0},
                        {"kind": "local", "pair": 0, "reverse": True, "stage": 1}], "first pair")
    need(len(recipe) == 19 and recipe[-1] == {"kind": "terminal", "pairs": 4}, "recipe boundary")
    witness = read_json(raw[TAIL])["trajectory_after_B1"]
    events = recipe[2:]
    need(len(events) == len(witness), "witness event coverage")
    for actual, old in zip(events, witness):
        keys = {"kind", "stage", "src", "dst", "coefficient"} & actual.keys()
        need(all(actual[k] == old[k] for k in keys), "witness event binding")
    return events


def tail_symbols(events):
    x = [var("x"+str(i)) for i in range(4)]
    y = [var("y"+str(i)) for i in range(4)]
    stages, history = [], []
    for event in events:
        kind = event["kind"]
        if kind == "bridge":
            i, j, k = event["src"], event["dst"], event["coefficient"]
            need(i in range(4) and j in range(4) and i != j and k in (-1, 1), "bridge domain")
            x[j] = lin((1, x[j]), (k, x[i]))
            y[i] = lin((1, y[i]), (-k, y[j]))
        elif kind == "local":
            s = event["stage"]
            stages.append(s)
            i = event["pair"]
            need(i in range(4) and event["reverse"] == bool(s % 2), "local pair/orientation")
            if not event["reverse"]:
                x[i] = lin((1, x[i]), (-1, op("K"+str(s), var("f"+str(s)))))
                y[i] = lin((1, y[i]), (1, x[i]))
            else:
                old_y = y[i]
                x[i] = lin((1, x[i]), (-1, old_y))
                y[i] = lin((1, old_y), (1, op("K"+str(s), var("a"+str(s)))))
        else:
            need(kind == "terminal", "tail event kind")
            x, y = y, [lin((-1, v)) for v in x]
        history.append(digest(canonical([expression_json(v) for v in x+y]).encode()))
    need(stages == list(range(2, 9)), "complete ordered tail stages")
    expected = lin((-1, var("x0")), (1, op("K2", var("f2"))))
    need(y[0] == expected, "completed-X tail identity")
    return {"events": len(events), "stages": stages,
            "local_pairs": [e["pair"] for e in events if e["kind"] == "local"],
            "Y_final_0": expression_json(y[0]), "state_hashes": history}


def packet_check(packet):
    need((packet["A_ports"], packet["T_ports"], packet["U_ports"]) == (A, T, U), "port partition")
    R = [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet["R_rows"]]
    need(len(R) == 8, "query dimension")
    blocks = [[[row[p] for p in ports] for row in R] for ports in (U, A, T)]
    need(mm(blocks[0], tr(blocks[0])) == eye(8, 48), "ordinary Gram")
    for block in blocks[1:]:
        need(mm(block, tr(block)) == eye(8, 4), "selected unit minor")
        inv = inverse(block)
        need(mm(inv, block) == mm(block, inv) == eye(8), "two-sided selected unit")
    need(all("F_"+str(s) in packet["programs"] for s in range(9)), "forward programs")
    need("B_1_2" in packet["programs"], "first backward program")
    return R, {"ports": [len(U), len(A), len(T)], "ordinary_gram": 48,
               "selected_grams": [4, 4], "R_sha256": digest(canonical([[str(x) for x in row] for row in R]).encode())}


def chart(B, LA, LT, K):
    need(mm(B, K) == eye(len(B), 12), "centre response")
    return {"B": B, "LA": LA, "LT": LT, "PA": inverse(LA), "PT": inverse(LT), "K": K}


def shear(q, step):
    a = eye(q)
    i, j = step % q, (step+1) % q
    a[i][j] = Q(1 + step % 3)
    return a


def fixture(q):
    charts = []
    for s in range(9):
        D, E = shear(q, s), shear(q, s+1)
        B = [a+b for a, b in zip(D, E)]
        K = [[12*x for x in row] for row in inverse(D)] + [[Q(0)]*q for _ in range(q)]
        charts.append(chart(B, shear(q, s+2), shear(q, s+3), K))
    return charts


def query(ch, data):
    u, a, t = data
    return add(mv(ch["B"], u), mv(ch["LA"], a), mv(ch["LT"], t))


def forward_scalar(ch, pair):
    # Literal three-step source word, independent of the reconstruction.
    x, y = deepcopy(pair)
    z, a, c = x[0], mv(ch["LA"], x[1]), mv(ch["LT"], x[2])
    c = add(c, mv(ch["B"], z), a)
    f = c[:]
    z = sub(z, mv(ch["K"], c))
    a = sub(scale(-1, a), add(mv(ch["B"], z), scale(11, c)))
    nx = [z, mv(ch["PA"], a), mv(ch["PT"], c)]
    ny = [add(y[0], z), sub(add(x[1], y[1]), nx[1]), sub(add(x[2], y[2]), nx[2])]
    return [nx, ny], f


def backward_exchange(ch, future, pair):
    # E, full-query exchange, H and conserved sums; a separate implementation
    # from the row formula used in the proof. All intermediate inputs are dirty.
    x, y = deepcopy(pair)
    u = deepcopy(y)
    u[1] = add(u[1], mv(future["PA"], add(mv(future["B"], y[0]), mv(future["LT"], y[2]))))
    a, b = mv(ch["LT"], x[2]), query(ch, u)
    v = deepcopy(u)
    v[2] = add(v[2], mv(ch["PT"], sub(a, b)))
    rv = query(ch, v)
    ny = [add(v[0], mv(ch["K"], rv)), v[1], sub(v[2], mv(ch["PT"], scale(12, rv)))]
    nx = [sub(x[0], y[0]), sub(add(x[1], y[1]), ny[1]), sub(add(x[2], y[2]), ny[2])]
    return [nx, ny]


def run(charts, events, values):
    q, u = len(charts[0]["LA"]), len(charts[0]["K"])
    n = u+2*q
    banks = []
    for i in range(4):
        pair = []
        for j in range(2):
            v = list(values[(2*i+j)*n:(2*i+j+1)*n])
            pair.append([v[:u], v[u:u+q], v[u+q:]])
        banks.append(pair)
    original = deepcopy(banks[0])
    q0, q2 = mv(charts[0]["B"], original[0][0]), mv(charts[2]["B"], original[0][0])
    banks[0], f0 = forward_scalar(charts[0], banks[0])
    banks[0] = backward_exchange(charts[1], charts[2], banks[0])
    first = deepcopy(banks[0])
    need(first[0][0] == scale(-1, original[1][0]), "first pair ordinary cancellation")
    queries = {0: f0}
    for event in events:
        kind = event["kind"]
        if kind == "bridge":
            i, j, k = event["src"], event["dst"], event["coefficient"]
            banks[j][0][0] = add(banks[j][0][0], scale(k, banks[i][0][0]))
            banks[i][1][0] = sub(banks[i][1][0], scale(k, banks[j][1][0]))
        elif kind == "local":
            s = event["stage"]
            i = event["pair"]
            if not event["reverse"]:
                banks[i], queries[s] = forward_scalar(charts[s], banks[i])
            else:
                banks[i] = backward_exchange(charts[s], charts[s+1], banks[i])
        else:
            need(kind == "terminal", "terminal event")
            for pair in banks:
                pair[0][0], pair[1][0] = pair[1][0], scale(-1, pair[0][0])
    obs = {"q0": q0, "q2": q2, "f0": f0, "f2": queries[2],
           "pA": add(first[0][1], first[1][1]), "pT": add(first[0][2], first[1][2]),
           "dA": first[1][1], "completed": banks[0][1][0]}
    return obs, original


def decode(charts, o, mutation=None):
    ch0, ch2 = charts[0], charts[2]
    f = o["f0"]
    w = sub(o["completed"], mv(ch2["K"], o["f2"]))
    if mutation == "discard_initial_Y":
        w = [Q(0)]*len(w)
    elif mutation == "omit_F2":
        w = add(w, mv(ch2["K"], o["f2"]))
    elif mutation == "F2_sign":
        w = add(w, scale(2, mv(ch2["K"], o["f2"])))
    elif mutation == "terminal_sign":
        w = sub(w, scale(2, o["completed"]))
    source = add(mv(ch2["B"], w), o["q2"], scale(-1, mv(ch2["B"], mv(ch0["K"], f))))
    if mutation == "omit_baseline_shift":
        source = add(source, mv(ch2["B"], mv(ch0["K"], f)))
    elif mutation == "omit_second_read":
        source = sub(source, o["q2"])
    target = mv(ch2["LT"], sub(o["pT"], mv(ch0["PT"], f)))
    if mutation == "omit_T_baseline":
        target = [Q(0)]*len(target)
    temp = add(o["pA"], scale(-1, o["dA"]), mv(ch2["PA"], add(source, target)))
    # Reconstruct the transient F0 A value; it is NOT an observation.
    if mutation == "commute_selected_units":
        xt = mv(ch0["PA"], mv(ch0["LT"], temp))
    else:
        xt = mv(ch0["PT"], mv(ch0["LA"], temp))
    xa = mv(ch0["PA"], sub(sub(f, o["q0"]), mv(ch0["LT"], xt)))
    if mutation == "omit_first_read":
        xa = add(xa, mv(ch0["PA"], o["q0"]))
    return [xa, xt, sub(o["pA"], xa), sub(o["pT"], xt)], w


MUTANTS = ["discard_initial_Y", "omit_F2", "F2_sign", "terminal_sign", "omit_baseline_shift",
           "omit_second_read", "omit_T_baseline", "commute_selected_units", "omit_first_read"]


def finite_check(charts, events, label):
    q, u = len(charts[0]["LA"]), len(charts[0]["K"])
    dimension = 8*(u+2*q)
    observation_columns, target_columns, rejected = [], [], {}
    for i in range(dimension):
        values = [Q(int(i == j)) for j in range(dimension)]
        obs, original = run(charts, events, values)
        result, w = decode(charts, obs)
        expected = original[0][1:] + original[1][1:]
        need(result == expected and w == original[1][0], "arbitrary-input recovery: " + label)
        observation_columns.append([x for key in sorted(obs) for x in obs[key]])
        target_columns.append([x for block in expected for x in block])
        for mutation in MUTANTS:
            if mutation not in rejected and decode(charts, obs, mutation)[0] != expected:
                rejected[mutation] = i
    observation, target = tr(observation_columns), tr(target_columns)
    observation_rank = len(rref(observation)[1])
    stacked_rank = len(rref(observation+target)[1])
    need(stacked_rank == observation_rank, "complete observation-kernel projection")
    return {"label": label, "centre_dimension": q, "ordinary_dimension": u,
            "basis_inputs": dimension, "observation_rank": observation_rank,
            "observation_plus_selected_rank": stacked_rank,
            "selected_target_rank": len(rref(target)[1]), "mutants_rejected_at_basis": rejected,
            "observation_matrix_sha256": digest(canonical([[str(x) for x in row] for row in observation]).encode())}


def reject(call, fragment):
    try:
        call()
    except Failure as exc:
        need(fragment in str(exc), "unexpected rejection: " + str(exc))
    else:
        raise Failure("accepted mutation: " + fragment)


def report(root):
    raw = load_sources(root)
    packet = read_json(gzip.decompress(raw[PACKET]))
    events = bind_schedule(raw)
    _, source = packet_check(packet)
    symbolic, tail_result = symbolic_decoder(), tail_symbols(events)
    fixtures = [finite_check(fixture(q), events, "noncommuting-q"+str(q)) for q in (2, 3)]
    need(all(set(r["mutants_rejected_at_basis"]) == set(MUTANTS) for r in fixtures), "complete decoder controls")
    bad = deepcopy(packet)
    bad["R_rows"][0][str(U[0])] = str(Q(bad["R_rows"][0].get(str(U[0]), 0))+1)
    reject(lambda: packet_check(bad), "ordinary Gram")
    bad_events = deepcopy(events)
    next(e for e in bad_events if e.get("coefficient") == -1)["coefficient"] = 1
    reject(lambda: tail_symbols(bad_events), "completed-X tail identity")
    bad_pairs = deepcopy(events)
    for event in bad_pairs:
        if event["kind"] == "local":
            event["pair"] = event["stage"]//2 % 4
    reject(lambda: tail_symbols(bad_pairs), "completed-X tail identity")
    return {"status": MARKER, "source": source, "ordered_identity": symbolic, "tail": tail_result,
            "finite_fixtures": fixtures, "decoder_controls": MUTANTS,
            "source_and_schedule_controls": ["query coefficient", "first negative bridge", "guessed stage pair"],
            "scope": "pair0 arbitrary selected inputs; recorded post-B1 selected cut; logical information only; no supplier or kappa"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--receipt", type=Path, default=HERE / "RESULT.json")
    ap.add_argument("--write", action="store_true", help="explicitly regenerate the package receipt")
    args = ap.parse_args()
    try:
        result = report(args.root)
        if args.write:
            args.receipt.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
        else:
            need(canonical(read_json(args.receipt.read_bytes())) == canonical(result), "receipt mismatch")
    except (Failure, OSError, KeyError, ValueError) as exc:
        raise SystemExit("FAIL_QQ16_TWO_QUERY_KERNEL: " + str(exc))
    print(MARKER + " pair0_selected_recovered symbolic=3 tail=17 basis=160 controls=12 no_new_kappa")


if __name__ == "__main__":
    main()
