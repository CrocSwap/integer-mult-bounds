"""Exact Laurent transport of the selected R76 pair, without a physical build."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from time import monotonic
import runpy

PAIR = (1580, 1659)
PRICE = "52e05b80069ce01cad3b8e5f3cf9123e930de36987bd398dd43f103953a4674a"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
GAUSS = "5bc0f4fd3fece7223551be76d7e4343631e7ee3156b73d3d01c81446a9e7e214"
ZERO = (0,) * 17
ENGINE_PATH = Path(__file__).with_name("gaussian_necessity.py")
G = runpy.run_path(str(ENGINE_PATH))["G"]


class Capped(Exception):
    pass


def pinned(path, sha):
    data = path.read_bytes()
    if sha256(data).hexdigest() != sha:
        raise ValueError("changed input " + path.name)
    return data


def mono(k=1, phase=0, powers=ZERO):
    return {(phase % 4, powers): k} if k else {}


def add(a, b, sign=1):
    out = a.copy()
    for m, c in b.items():
        x = out.get(m, 0) + sign * c
        if x:
            out[m] = x
        else:
            out.pop(m, None)
    return out


def mul(a, b):
    out = {}
    for (q, v), x in a.items():
        for (r, w), y in b.items():
            key = ((q + r) % 4, tuple(i + j for i, j in zip(v, w, strict=True)))
            z = out.get(key, 0) + x * y
            if z:
                out[key] = z
            else:
                out.pop(key, None)
    return out


def scalar(role, coeff=Q(1), phase=0, mask=()):
    powers = tuple(mask.count(i) for i in range(1, 18))
    return ("SCALE", role, role, mono(coeff, phase, powers),
            mono(1 / coeff, -phase, tuple(-x for x in powers)))


def emit(event, alpha, even):
    family, op, *args = event
    if family == "B":
        return []
    if family == "J":
        u, v, x, y = args[0]
        return [("ADD", v, u, mono(1, -1), None), ("ADD", x, y, mono(alpha, 1), None),
                *(scalar(r, mask=(op,)) for r in (u, v, x, y))]
    assert family == "A"
    d, *tail = args
    if op == "ADD":
        return [(op, d, tail[0], mono(Q(tail[1])), None)]
    if op == "SCALE":
        return [scalar(d, Q(tail[0]))]
    if op == "SWAP":
        return [(op, d, tail[0], None, None)]
    if op == "QUERY":
        return [("ADD", d, tail[0], mono(1, 0 if even else tail[1]), None)]
    if op == "LAMBDA":
        s = Q(tail[0], 2)
        a, b = G(Q(1, 2), s), G(Q(1, 2), -s)
        return [("SCALE", d, d, add(mono(a), mono(b, 2)), add(mono(b), mono(a, 2)))]
    if op in ("IDLE_ONE", "IDLE_ODD"):
        return [scalar(d, phase=tail[1] if op == "IDLE_ODD" else 0, mask=tuple(tail[0]))]
    raise ValueError("unknown Type A event")


def transport(ops, n, dest, source, deadline):
    u = [mono(Q(i == dest)) for i in range(n)]
    v = [mono(Q(i == source)) for i in range(n)]
    for kind, d, s, scale, inv in reversed(ops):
        if monotonic() >= deadline:
            raise Capped
        if kind == "ADD":
            u[d] = add(u[d], mul(scale, u[s]), -1)
            v[s] = add(v[s], mul(scale, v[d]))
        elif kind == "SCALE":
            u[d] = mul(inv, u[d])
            v[d] = mul(scale, v[d])
        else:
            assert kind == "SWAP"
            u[d], u[s] = u[s], u[d]
            v[d], v[s] = v[s], v[d]
    return u, v


def describe(poly):
    return [{"q": phase, "body": {j + 1: n for j, n in enumerate(powers) if n}, "coefficient": str(c)}
            for (phase, powers), c in sorted(poly.items())]


def proof(caller, deadline):
    first, second = PAIR
    events = caller["events"]
    ty = caller["types"]["A"]
    assert all(events[t] == ["A", "QUERY", 0, 1, -1] for t in PAIR)
    tape = [item for t in range(first, second)
            for item in emit(events[t], Q(ty["alpha2"]), t == first)]
    u, v = transport(tape, ty["roles"], 0, 1, deadline)
    dot = {}
    for x, y in zip(u, v, strict=True):
        dot = add(dot, mul(x, y))
    assert not dot, "transported shear lost own square-zero property"
    outer = {}
    for i, x in enumerate(u):
        if monotonic() >= deadline:
            raise Capped
        if x:
            for j, y in enumerate(v):
                if y and (p := mul(x, y)):
                    outer[i, j] = p
    bad_body = [(i, j, describe(p)) for (i, j), p in outer.items() if any(m[1] != ZERO for m in p)]
    odd = [(i, j) for (i, j), p in outer.items() if any(m[0] % 2 for m in p)]
    corrected = {}
    delta = add(mono(1, -1), mono(-1))
    for key, p in outer.items():
        if result := mul(delta, p):
            corrected[key] = result
    for i, x in enumerate(u):
        if x and (p := mul(mul(delta, delta), mul(x, v[0]))):
            key = (i, 1)
            corrected[key] = add(corrected.get(key, {}), p)
    corrected[0, 1] = add(corrected.get((0, 1), {}), delta)
    corrected = {k: p for k, p in corrected.items() if p}
    return {
        "status": "EXACT_SYMBOLIC_AXES" if not (u[1] or v[0] or bad_body or odd) else "FORMAL_SHAPE_OPEN",
        "pair": PAIR, "literal_between_event_count": len(range(first, second)),
        "elementary_operation_count": len(tape), "vector_support": [sum(map(bool, u)), sum(map(bool, v))],
        "vectors": {"u": {i: describe(p) for i, p in enumerate(u) if p},
                    "v": {i: describe(p) for i, p in enumerate(v) if p}},
        "cross_actions": {"u_source": describe(u[1]), "v_dest": describe(v[0]), "v_u": describe(dot)},
        "outer_body_dependency": bad_body, "outer_q_odd_entries": odd,
        "outer_axis": {f"{i},{j}": describe(p) for (i, j), p in outer.items()},
        "normalized_delta_entries": {f"{i},{j}": describe(p) for (i, j), p in corrected.items()},
        "condition_if_success": "G=I+(q^-1−1)(e0 e1^T+u v) over Q(i)[q,D_1^±1,...,D_17^±1]/(q^4−1). Formal axes only, with no physical provider or cost admission."
    }


def main(args):
    start = monotonic()
    controls = [
        mul(add(mono(G(Q(1, 2), Q(1, 2))), mono(G(Q(1, 2), Q(-1, 2)), 2)),
            add(mono(G(Q(1, 2), Q(-1, 2))), mono(G(Q(1, 2), Q(1, 2)), 2))) == mono(),
        mul(mono(3, -1, (1,) + ZERO[1:]), mono(Q(1, 3), 1, (-1,) + ZERO[1:])) == mono(),
    ]
    assert all(controls)
    price = loads(pinned(args.price, PRICE))
    gaussian = loads(pinned(args.gaussian, GAUSS))
    assert price["formal_case_cap"] == 1 and price["formal_runner_seconds"] == 90 and tuple(gaussian["pair"]) == PAIR
    caller = loads(pinned(args.caller, CALLER))
    try:
        result = proof(caller, start + 87)
    except Capped:
        result = {"status": "CAPPED", "pair": PAIR, "pending": "Finish exact Laurent rank-one transport/product"}
    result.update({"caller_sha256": CALLER, "price_sha256": PRICE, "gaussian_receipt_sha256": GAUSS,
                   "controls": ["LAMBDA inverse", "Laurent monomial inverse"], "unvisited_pair": [1516, 1721]})
    print(dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    p = ArgumentParser()
    for name in ("price", "caller", "gaussian"):
        p.add_argument("--" + name, type=Path, required=True)
    main(p.parse_args())
