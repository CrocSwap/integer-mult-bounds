"""Independent exact forward support gate for the two fixed Type A hosts."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/PR7404-RESULT.json": "eba0ebfac85759cc9c884b3a12237975ff487c76b17f6095949e80d2fbca60fc",
    "inputs/retiming.py": "3f22de2c9f9e53e194b9244df4d3562f0c3f1199b63b91f76e8d3732bb818e99",
    "inputs/R174-PRICE.json": "eb5ba68fe579cfea3ae1c79782850f173bc6e06fb853ce152bf58d7d6ed507b1",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PEER = "aadd1de3e520cfd1e5b062729bd76f543dc879f4"
HOSTS = {1423: (8, (8, 0, 18, 26)), 3058: (9, (9, 0, 18, 27))}
DEMOTED, RETIRED = (1580, 1659), (0, 18)
N, SECONDS = 36, 20


def unique(items):
    out = dict(items)
    assert len(items) == len(out)
    return out


def read(path, decode=True):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return loads(raw, object_pairs_hook=unique) if decode else raw


def stop(*_):
    raise TimeoutError("20-second runner cap")


def add(a, b, c):
    out = a.copy()
    for i, x in b.items():
        v = out.get(i, 0) + c*x
        if v:
            out[i] = v
        else:
            out.pop(i, None)
    return out


def transpose(rows, width):
    out = [{} for _ in range(width)]
    for i, row in enumerate(rows):
        for j, v in row.items():
            out[j][i] = v
    return out


def columns(events, roles, q, demote):
    rows = [{} for _ in range(N)]
    for i, r in enumerate(roles):
        rows[r] = {i: Q(1)}
    for t, (ty, *args) in events:
        if ty == "B":
            continue
        if ty == "J":
            _, (u, v, x, y), _ = args
            rows[v] = add(rows[v], rows[u], q)
            rows[x] = add(rows[x], rows[y], -q)
            continue
        assert ty == "A"
        op, r, *extra = args
        if op in ("ADD", "QUERY"):
            s, z = extra
            if op == "ADD":
                coeff = Q(z)
            else:
                assert z == -1
                coeff = Q(1 if demote and t in DEMOTED else q)
            rows[r] = add(rows[r], rows[s], coeff)
        elif op == "SCALE":
            coeff = Q(extra[0])
            assert coeff
            rows[r] = {i: coeff*v for i, v in rows[r].items()}
        elif op == "SWAP":
            s, = extra
            rows[r], rows[s] = rows[s], rows[r]
        else:
            assert op in ("LAMBDA", "IDLE_ONE")
    return transpose(rows, len(roles))


def reduce(v, basis):
    residual = v.copy()
    for i, b in sorted(basis.items()):
        if i in residual:
            residual = add(residual, b, -residual[i])
    return residual


def echelon(generators):
    basis = {}
    for col in generators:
        residual = reduce(col, basis)
        if residual:
            i = min(residual)
            basis[i] = {j: v/residual[i] for j, v in residual.items()}
    return basis


def dot(a, b):
    return sum((v*b.get(i, 0) for i, v in a.items()), Q(0))


def separator(generators, target, basis):
    residual = reduce(target, basis)
    if not residual:
        return None
    f = {min(residual): Q(1)}
    for i, b in sorted(basis.items(), reverse=True):
        val = -dot(b, f)
        if val:
            f[i] = val
    assert all(not dot(f, a) for a in generators) and dot(f, target)
    return f


def compare(generators, targets):
    basis = echelon(generators)
    assert separator(generators, generators[0], basis) is None
    bad = {}
    for j, want in enumerate(targets):
        f = separator(generators, want, basis)
        if f is not None:
            bad[j] = {"annihilator": f, "target_value": dot(f, want),
                      "generator_values": [dot(f, col) for col in generators]}
    return {"span_rank": len(basis), "residual_rank": len(echelon(targets)),
            "violations": bad, "outside_count": len(bad)}


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(SECONDS)
    c = read("inputs/CALLER.json")
    peer = read("inputs/PR7404-RESULT.json")
    price = read("inputs/R174-PRICE.json")
    read("inputs/retiming.py", False)
    assert (price["native_head"], price["caller_head"], price["peer_head"]) == (HEAD, CALLER, PEER)
    assert price["demote_queries"] == list(DEMOTED) and price["price"]["roots"] == list(RETIRED)
    assert len(c["events"]) == 4783
    assert all(row[:2] == [-1, 0] for row in c["types"]["A"]["diagonal"])
    original, before, after = run_path(str(ROOT / "inputs/retiming.py"))["retiming"](c["events"], peer)
    timeline = before + [original[1423]] + after
    for clock, (stage, roles) in HOSTS.items():
        assert c["events"][clock][:3] == ["J", stage, list(roles)]
    old = [{i: Q(-1)} for i in range(N)]
    assert columns(original, range(N), -1, False) == old
    assert columns(timeline, range(N), -1, False) == old
    assert columns(timeline, range(N), 1, True) == [{i: Q(1)} for i in range(N)]
    baseline = columns(timeline, range(N), -1, True)
    desired = [{i: Q(1 if i in RETIRED else -1)} for i in range(N)]
    delta = [add(w, got, -1) for w, got in zip(desired, baseline, strict=True)]
    assert any(delta)
    suffix, prefix = {}, {}
    for clock, (_, roles) in HOSTS.items():
        where = next(i for i, (t, _) in enumerate(timeline) if t == clock)
        suffix[clock] = columns(timeline[where+1:], roles, -1, True)
        prefix_rows = transpose(columns(timeline[:where], range(N), -1, True), N)
        prefix[clock] = [prefix_rows[r] for r in roles]
    outputs = [v for group in suffix.values() for v in group]
    inputs = [v for group in prefix.values() for v in group]
    assert len(outputs) == len(inputs) == 8
    out_test = compare(outputs, delta)
    in_test = compare(inputs, transpose(delta, N))
    control = compare([{0: Q(1)}, {1: Q(1)}], [{0: Q(1), 2: Q(2)}])
    assert control["outside_count"] == 1 and control["violations"][0]["target_value"] == 2
    alarm(0)
    print(dumps({"head": HEAD, "caller": CALLER, "peer": PEER, "pins": PINS, "hosts": HOSTS,
                 "phase": -1, "unit_bodies": True, "basis_columns": N, "cap_seconds": SECONDS,
                 "demoted": DEMOTED, "retired": RETIRED, "retimed_event_count": len(timeline),
                 "suffix_columns": suffix, "prefix_rows": prefix, "residual_columns": delta,
                 "output_test": out_test, "input_test": in_test,
                 "inherited_zero_paid_price": price["price"],
                 "status": "support excludes" if out_test["outside_count"] or in_test["outside_count"] else
                           "both necessary supports survive",
                 "controls": ["old and retimed q=-1 endpoints", "q=+1 demotion neutral",
                              "known generator survives", "known exterior target rejected"]},
                indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
