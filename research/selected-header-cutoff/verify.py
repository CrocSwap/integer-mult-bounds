"""Bounded exact checks; host integers belong to the oracle, not the machine."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import cutoff_prefix as C


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unary(tape, origin):
    at = origin
    while tape.cells.get(at, C.BLANK) == C.ONE:
        at += 1
    return at - origin


def root_cutoff(d, e, q):
    # Small-denominator oracle uses Python's exact exponentiation directly.
    # The selected-denominator fixtures satisfy d<2^Q, so their root is 1 or 2.
    if q == C.SELECTED_Q:
        need(d.bit_length() <= q, "selected sanity range")
        return min(1 if d == 1 else 2, e + 1)
    return next(t for t in range(1, e + 2) if t == e + 1 or t ** q >= d)


def events(n, sites, e, cutoff):
    if e < max(n, cutoff):
        return [("L", e), ("X", e)], e, 1, 0
    remainder = e % n
    out = [("E", e), ("B" + str(remainder), e)]
    mass, nodes, depth = e, 1, 0
    for i in range(sites):
        child = e // n
        ev, cm, cn, cd = events(n, sites, child, cutoff)
        out += [("D" + str(i), child)] + ev + [("U" + str(i), e)]
        mass += cm
        nodes += cn
        depth = max(depth, cd + 1)
    return out + [("A" + str(remainder), e), ("X", e)], mass, nodes, depth


def inspect_run(code, tapes, origins, cutoff, expected, bound):
    saved = [(t.cells.copy(), t.head) for t in tapes]
    machine = C.Machine(code, tapes)
    observed = []
    ready = False
    while not machine.halted:
        need(machine.steps < bound, "complete transition budget")
        ins = code[machine.pc]
        if ins[0] == "emit":
            name = ins[1]
            if name == "READY":
                need(not ready, "unique prefix handoff")
                ready = True
                need(unary(tapes[C.CUTOFF], origins[C.CUTOFF]) == cutoff, "generated cutoff")
                for j, t in enumerate(tapes):
                    if j != C.CUTOFF:
                        need((t.cells, t.head) == saved[j], "prefix input/scratch restoration")
                need(tapes[C.CUTOFF].head == origins[C.CUTOFF], "cutoff handoff head")
            elif name == "RETIRED":
                need(ready, "retirement after ready")
                need(all((t.cells, t.head) == s for t, s in zip(tapes, saved)), "cutoff retirement")
            else:
                need(ready, "selected control before prefix")
                need(unary(tapes[C.CUTOFF], origins[C.CUTOFF]) == cutoff, "retained cutoff")
                need(tapes[C.CUTOFF].head == origins[C.CUTOFF], "retained cutoff head")
                observed.append((name, unary(tapes[C.WIDTH], origins[C.WIDTH])))
        machine.step()
    need(observed == expected, "exact composed event/width contour")
    need(machine.events[0] == "READY" and machine.events[-1] == "RETIRED", "handoff edges")
    need(all((t.cells, t.head) == s for t, s in zip(tapes, saved)), "complete endpoint")
    for j, tape in enumerate(tapes):
        floor = origins[j] if j == C.HEADER else origins[j] - 1
        need(tape.low >= floor, "ancestor visit")
    return machine


def one(n, sites, q, p, d, e, origins=None, supplied_code=None):
    origins = (0,) * 11 if origins is None else tuple(origins)
    code, alphabet, meta = C.compile_joined(n, sites, q)
    need(meta["prefix"] == 273 + 84 * meta["power_stages"], "prefix instruction census")
    need(meta["cleanup"] == 14, "retirement instruction census")
    need(len(code) == 329 + 84 * meta["power_stages"] + 30 * n + sites * (69 + 3 * n),
         "joined instruction census")
    if supplied_code is not None:
        code = supplied_code
    cutoff = root_cutoff(d, e, q)
    expected, mass, nodes, depth = events(n, sites, e, cutoff)
    h = len(C.gamma(p) + C.gamma(d))
    prep_bill = 1000 * (meta["power_stages"] + 1) * (h + d * cutoff + 1)
    bill = prep_bill + 200 * (sites + 1) * mass
    ts = C.initial(p, d, e, origins)
    machine = inspect_run(code, ts, origins, cutoff, expected, bill)
    span = sum(t.high - t.low + 1 for t in ts)
    backing_bill = (5 + Fraction(n, n - 1)) * e + 5 * d + 4 * h + 40
    need(span <= backing_bill, "historical backing bill")
    need(ts[C.HEADER].high <= origins[C.HEADER] + h, "header prefix access")
    need(len(alphabet) == sites + 4, "fixed alphabet")
    return machine.steps, nodes, cutoff, span, expected


def dense(code, original, limit):
    """Separately implemented dense interpreter; no Machine/Tape methods."""
    low = min(t.head for t in original) - 40
    high = max(t.head for t in original) + 10000
    arrays = [[C.BLANK] * (high - low + 1) for _ in original]
    heads = [t.head for t in original]
    for j, t in enumerate(original):
        for at, symbol in t.cells.items():
            arrays[j][at - low] = symbol
    pc = steps = 0
    emitted = []
    while steps < limit:
        ins = code[pc]
        op = ins[0]
        steps += 1
        if op == "halt":
            return steps, emitted, heads, arrays, low
        if op == "goto":
            pc = ins[1]
            continue
        if op == "read":
            pc = ins[2][arrays[ins[1]][heads[ins[1]] - low]]
            continue
        if op == "write":
            arrays[ins[1]][heads[ins[1]] - low] = ins[2]
        elif op == "move":
            heads[ins[1]] += ins[2]
        elif op == "emit":
            emitted.append(ins[1])
        else:
            raise ValueError("unknown dense opcode")
        pc += 1
    raise ValueError("dense transition limit")


def rejects(mutated, q, p, d, e, factor=3):
    n, sites = 2, 1
    baseline = one(n, sites, q, p, d, e)[0]
    cutoff = root_cutoff(d, e, q)
    expected = events(n, sites, e, cutoff)[0]
    try:
        inspect_run(mutated, C.initial(p, d, e), (0,) * 11, cutoff,
                    expected, factor * baseline + 100)
    except (ValueError, KeyError):
        return
    raise ValueError("mutated program escaped detection")


def main():
    cases = steps = nodes = 0
    for q in (2, 3, 5):
        for d in range(1, 33):
            for e in sorted({1, d, max(1, d // 2), min(d, 3)}):
                st, no, _, _, _ = one(3, 2, q, 2 * d + 1, d, e)
                cases += 1
                steps += st
                nodes += no
    boundaries = 0
    for q in (2, 3, 5):
        for t in range(2, 5):
            for delta in (-1, 0, 1):
                d = t ** q + delta
                e = min(d, t + 1)
                st, no, _, _, _ = one(2, 1, q, 2 * d + 1, d, e)
                boundaries += 1
                steps += st
                nodes += no
    selected_cases = 0
    for d, e in ((1, 1), (2, 1), (2, 2), (7, 7), (31, 2), (257, 2), (4097, 1)):
        st, no, _, _, _ = one(3, 2, C.SELECTED_Q, 2 * d + 1, d, e)
        selected_cases += 1
        steps += st
        nodes += no

    # Saturated multiplication is checked directly against min(a*b,d).
    a = C.Builder()
    C.saturated_multiply(a)
    a.op("halt")
    mul_code, _ = a.finish((C.BLANK, "0", C.ONE, C.MARK))
    products = 0
    for d in range(1, 9):
        for x in range(1, d + 1):
            for y in range(1, d + 1):
                ts = C.initial(1, d, 1)
                for j in (C.D, C.ACC, C.FACTOR, C.PRODUCT):
                    ts[j].cells[-1] = C.MARK
                for j, size in ((C.D, d), (C.ACC, x), (C.FACTOR, y)):
                    ts[j].cells.update({k: C.ONE for k in range(size)})
                before = [(t.cells.copy(), t.head) for t in ts]
                z = C.Machine(mul_code, ts).run(40 * min(x * y, d) + 40)
                need(unary(ts[C.PRODUCT], 0) == min(x * y, d), "literal saturated product")
                for j, tape in enumerate(ts):
                    if j != C.PRODUCT:
                        need((tape.cells, tape.head) == before[j], "multiplication inputs")
                need(ts[C.PRODUCT].head == 0, "product head return")
                products += 1

    dense_cases = 0
    shifted = tuple(23 - 7 * j for j in range(11))
    for q, p, d, e in ((2, 31, 16, 5), (3, 37, 28, 4), (C.SELECTED_Q, 17, 7, 2)):
        for origin in ((0,) * 11, shifted):
            code, _, _ = C.compile_joined(3, 2, q)
            st, _, _, _, _ = one(3, 2, q, p, d, e, origin)
            original = C.initial(p, d, e, origin)
            ds, de, dh, da, lo = dense(code, C.initial(p, d, e, origin), st + 1)
            oracle_events = ["READY"] + [x[0] for x in events(3, 2, e, root_cutoff(d, e, q))[0]] + ["RETIRED"]
            need((ds, de, dh) == (st, oracle_events, list(origin)), "independent dense CPU")
            for j, tape in enumerate(original):
                need({k + lo: v for k, v in enumerate(da[j]) if v != C.BLANK} == tape.cells,
                     "dense complete restoration")
            dense_cases += 1

    controls = []
    for q in (0, 1, True):
        try:
            C.compile_prefix(q)
        except ValueError:
            controls.append("invalid-fixed-exponent")
        else:
            raise ValueError("invalid exponent accepted")
    code, _, meta = C.compile_joined(2, 1, 2)
    bad = list(code)
    j = next(i for i, ins in enumerate(bad) if ins == ("move", C.HEADER, -1))
    bad[j] = ("move", C.HEADER, 0)
    rejects(tuple(bad), 2, 17, 4, 4)
    controls.append("borrowed-header-return")
    bad = list(code)
    j = next(i for i, ins in enumerate(bad[:meta["prefix"] - 1])
             if ins[0] == "read" and ins[1] == C.CUTOFF and
             bad[i + 1][0:2] == ("read", C.WIDTH))
    targets = dict(bad[j][2])
    targets[C.BLANK] = bad[j + 1][2][C.BLANK]
    bad[j] = ("read", C.CUTOFF, targets)
    rejects(tuple(bad), 2, 17, 9, 2)
    controls.append("sentinel-equality")
    bad = list(code)
    j = next(i for i, ins in enumerate(bad[:meta["prefix"] - 1])
             if ins[0:2] == ("read", C.D) and bad[i + 1][0:2] == ("read", C.ACC))
    targets = dict(bad[j][2])
    targets[C.BLANK] = bad[j + 1][2][C.BLANK]
    bad[j] = ("read", C.D, targets)
    rejects(tuple(bad), 2, 17, 4, 4)
    controls.append("perfect-power-strictness")
    bad = list(code)
    j = next(i for i, ins in enumerate(bad) if ins == ("write", C.PRODUCT, C.ONE))
    bad[j] = ("write", C.PRODUCT, C.BLANK)
    rejects(tuple(bad), 2, 17, 4, 4)
    controls.append("Gamma-d-doubling")
    bad = list(code)
    bad[meta["cleanup_at"]] = ("goto", len(bad) - 2)
    rejects(tuple(bad), 2, 17, 4, 4)
    controls.append("cutoff-retirement")
    # Skipping one final multiplication saturation permits a too-long result.
    bad = list(code)
    mul_limits = [i for i, ins in enumerate(bad[:meta["prefix"] - 1])
                  if ins[0:2] == ("read", C.D) and bad[i + 1][0:2] == ("read", C.FACTOR)]
    j = mul_limits[-1]
    targets = dict(bad[j][2])
    targets[C.BLANK] = targets[C.ONE]
    bad[j] = ("read", C.D, targets)
    rejects(tuple(bad), 2, 17, 3, 3)
    controls.append("product-saturation")
    wrong, _, _ = C.compile_joined(2, 1, 3)
    rejects(wrong, 2, 17, 8, 4)
    controls.append("wrong-cutoff-exponent")
    baseline = one(2, 1, 2, 17, 4, 4)[0]
    try:
        C.Machine(code, C.initial(17, 4, 4)).run(baseline - 1)
    except ValueError:
        controls.append("undercharged-total-time")
    else:
        raise ValueError("undercharged execution passed")
    _, _, _, span, _ = one(2, 1, 2, 4099, 2049, 1)
    need(span > 100, "unary-d historical backing control")
    controls.append("false-root-width-only-space")
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp)
        (target / "inputs").mkdir()
        (target / "cutoff_prefix.py").write_bytes(Path(C.__file__).read_bytes())
        for name in C.PINS:
            data = (C.INPUTS / name).read_bytes()
            if name == "selected_control.py":
                data += b"\n# changed source\n"
            (target / "inputs" / name).write_bytes(data)
        process = subprocess.run([sys.executable, "-B", "-c", "import cutoff_prefix"],
                                 cwd=target, capture_output=True, text=True, timeout=20)
        need(process.returncode != 0 and "frozen controller dependency hash" in process.stderr,
             "source corruption rejection")
    controls.append("frozen-source-corruption")

    selected_code, selected_abc, selected_meta = C.compile_joined(3, 2)
    source = Path(C.__file__).read_bytes()
    print(json.dumps({
        "status": "PASS_SELECTED_HEADER_CUTOFF_PREFIX",
        "finite_cases": cases,
        "exact_power_boundary_cases": boundaries,
        "selected_Q_cases": selected_cases,
        "counted_transitions": steps,
        "counted_selected_nodes": nodes,
        "direct_saturated_products": products,
        "independent_dense_cases": dense_cases,
        "negative_controls": len(controls),
        "control_names": controls,
        "selected_Q": C.SELECTED_Q,
        "selected_Q_power_stages": selected_meta["power_stages"],
        "n3_sites2_instruction_count": len(selected_code),
        "tapes": 11,
        "alphabet_size_n3_sites2": len(selected_abc),
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "scope": "literal header/cutoff/control composition; payload and Q0 producer retained",
        "kappa": "unchanged",
        "formal_kernel": "not_run",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
