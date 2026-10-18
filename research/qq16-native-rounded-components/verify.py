#!/usr/bin/env python3
"""Finite native F0 rounding audit. Sricharan Vagvala, with OpenAI Codex assistance.

Apache-2.0. Exact Clifford vector primitives are reused from Tekalign/PR3017.
The rounded interpreter and binary64 interpreter below are new.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from functools import lru_cache
from pathlib import Path
import tarfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = types.ModuleType("credited_native_vectors")
NATIVE_SHA = "999eb1230798b25821de7771ecfa86381e137124059b30ccef167169d176ee8e"
raw_native = (HERE / "vendor/native.py").read_bytes()
if hashlib.sha256(raw_native).hexdigest() != NATIVE_SHA:
    raise ValueError("Pinned PR3017 native evaluator changed")
exec(compile(raw_native, str(HERE / "vendor/native.py"), "exec"), N.__dict__)
need = N.need
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/CLIFFORD-RECIPES.json": "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731",
    "slots/local/RESIDUAL-ADAPTERS.json": "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c",
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


@lru_cache(2048)
def vector_digest(value):
    return digest(value)


def load():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for pin in sources["files"]:
        if pin["usage"] == "input":
            need(hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest()
                 == pin["sha256"], "Scientific source hash: " + pin["path"])
    objects = []
    with tarfile.open(ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz") as archive:
        for name, expected in MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), "Unique regular member")
            raw = archive.extractfile(matches[0]).read()
            need(hashlib.sha256(raw).hexdigest() == expected, "Native member hash")
            objects.append(json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw))
    packet = json.loads(gzip.decompress((ROOT / "research/joint-query/certificate.json.gz").read_bytes()))
    need(packet["programs"]["F_0"][0][:3] == ["retained_core", "forward", 0], "F0 binding")
    events = list(packet["core_words"]["forward"])
    for sweep in packet["programs"]["F_0"][1:]:
        need(sweep[0] in ("cover_sweep", "private_sweep"), "Wrapper kind")
        events.extend(sweep[2])
    need(Counter(e[0] for e in events) == {
        "scalar": 21025, "climb": 3486, "adapter": 1090,
        "residual_adapter": 480, "phase": 10, "native_line": 8}, "Literal inventory")
    return events, packet, *objects


def reg(token):
    kind, at = token
    need(kind in ("L", "C") and type(at) is int, "Register type")
    need(0 <= at < (704 if kind == "L" else 8), "Register range")
    return at + 704 * (kind == "C")


def nearest_integer(n, bits):
    """RN-even of n * 2^-e; integer n suffices for every shared dyadic e."""
    if bits is None or not n or abs(n).bit_length() <= bits:
        return n
    sign = -1 if n < 0 else 1
    shift = abs(n).bit_length() - bits
    q, rem = divmod(abs(n), 1 << shift)
    half = 1 << (shift - 1)
    if rem > half or (rem == half and q & 1):
        q += 1
    return sign * (q << shift)


class Dyadic:
    zero = N.ZERO

    def __init__(self, bits):
        self.bits = bits
        self.event = None
        self.faults = Counter()
        self.max_error = {}
        self.low_exponent = 65
        self.high_exponent = 65

    def observe(self, values, exponent):
        for n in values:
            if n:
                binary_exponent = abs(n).bit_length()-1-exponent
                self.low_exponent = min(self.low_exponent, binary_exponent)
                self.high_exponent = max(self.high_exponent, binary_exponent)

    def round(self, values, exponent, stage):
        self.observe(values, exponent)
        out = []
        for x in values:
            y = nearest_integer(x, self.bits)
            if y != x:
                self.faults[self.event, stage] += 1
                key = self.event, stage
                err = Fraction(abs(y-x), 1 << exponent)
                self.max_error[key] = max(self.max_error.get(key, 0), err)
            out.append(y)
        self.observe(out, exponent)
        return out

    def constant(self, value):
        return N.scaled(N.ONE, Fraction(value))

    def mono(self, value, key, adjoint=False):
        return N.mono(value, key, adjoint)

    def canonical(self, value):
        return value

    def scalar(self, value, numerator, denominator, stage):
        re, im, e = N.scaled(value, Fraction(numerator, denominator))
        return N.vector(self.round(re, e, stage), self.round(im, e, stage), e)

    def add(self, left, right):
        a, b, e = left
        c, d, f = right
        power = max(e, f)
        re = [(x << (power-e)) + (y << (power-f)) for x, y in zip(a, c)]
        im = [(x << (power-e)) + (y << (power-f)) for x, y in zip(b, d)]
        return N.vector(self.round(re, power, "scalar-add"),
                        self.round(im, power, "scalar-add"), power)

    def line(self, value, axis):
        """Pair sums/differences, then crossed sums/differences, then /2."""
        re, im, e = value
        rr, ii = [0] * N.DIM, [0] * N.DIM
        for x in range(N.DIM):
            y = x ^ axis
            if x > y:
                continue
            a, b, c, d = re[x], im[x], re[y], im[y]
            rp, ip, rd, idiff = self.round([a+c, b+d, a-c, b-d], e, "native-pair")
            r0, i0, r1, i1 = self.round([rp-idiff, ip+rd, rp+idiff, ip-rd], e, "native-cross")
            rr[x], ii[x], rr[y], ii[y] = r0, i0, r1, i1
        self.observe(rr + ii, e+1)
        return N.vector(rr, ii, e+1)

    def recipe(self, value, record, axes=9):
        if record["rank"]:
            value = self.mono(value, N.monomial_key(record["right"], axes))
            for j in range(record["rank"]):
                value = self.line(value, 1 << j)
        else:
            need(record["right"] is None, "Rank-zero right monomial")
        return self.mono(value, N.monomial_key(record["left"], axes))

    def report(self):
        return [{"event": i, "stage": stage, "rounded_components": count,
                 "max_component_error": str(self.max_error[i, stage])}
                for (i, stage), count in sorted(self.faults.items())]


class Binary64(Dyadic):
    """Separate float primitives; shared event order and monomial index table."""
    zero = ((0.0,) * N.DIM, (0.0,) * N.DIM)

    def __init__(self):
        self.event = None

    def constant(self, value):
        return (float(value),) * N.DIM, (0.0,) * N.DIM

    def mono(self, value, key, adjoint=False):
        re, im = value
        rr, ii = [0.0] * N.DIM, [0.0] * N.DIM
        # Direct complex phase rotation, separate from the integer evaluator.
        phases = (1+0j, 1j, -1+0j, -1j)
        for x, (dest, angle) in enumerate(N.table(key)):
            if adjoint:
                z = complex(re[dest], im[dest]) * phases[-angle % 4]
                rr[x], ii[x] = z.real, z.imag
            else:
                z = complex(re[x], im[x]) * phases[angle]
                rr[dest], ii[dest] = z.real, z.imag
        return tuple(rr), tuple(ii)

    def scalar(self, value, numerator, denominator, stage):
        coefficient = numerator / denominator
        return tuple(x * coefficient for x in value[0]), tuple(x * coefficient for x in value[1])

    def add(self, left, right):
        return (tuple(a+b for a, b in zip(left[0], right[0])),
                tuple(a+b for a, b in zip(left[1], right[1])))

    def line(self, value, axis):
        re, im = value
        rr, ii = [0.0] * N.DIM, [0.0] * N.DIM
        for x in range(N.DIM):
            y = x ^ axis
            if x > y:
                continue
            sr, si = re[x] + re[y], im[x] + im[y]
            dr, di = re[x] - re[y], im[x] - im[y]
            rr[x], ii[x] = (sr-di) * 0.5, (si+dr) * 0.5
            rr[y], ii[y] = (sr+di) * 0.5, (si-dr) * 0.5
        return tuple(rr), tuple(ii)

    def canonical(self, value):
        ratios = [x.as_integer_ratio() for row in value for x in row]
        exponent = max(d.bit_length()-1 for _, d in ratios)
        ints = [n << (exponent - (d.bit_length()-1)) for n, d in ratios]
        return N.vector(ints[:N.DIM], ints[N.DIM:], exponent)

    def report(self):
        return []  # Rounding locations are counted by the exact interpreter.


def run(data, bits=53, dirty=True, signal=1, engine=None, trace=None):
    events, packet, word, recipes, residuals = data
    engine = engine or Dyadic(bits)
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    adapters = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
    state = [engine.zero] * 712
    state[112] = engine.constant(signal)
    state[224] = engine.constant(signal * 2**65) if dirty else engine.zero
    cuts = {}
    for index, event in enumerate(events):
        engine.event = index
        kind = event[0]
        if index in (3887, 4060):
            cuts[index] = [engine.canonical(state[reg(event[1][1])]),
                           engine.canonical(state[reg(event[1][2])])]
        if kind == "scalar":
            gate = event[1]
            dst = reg(gate[1])
            if gate[0] == "clear":
                need(dst >= 704, "Owned private CLEAR")
                state[dst] = engine.zero
            elif gate[0] == "scale":
                state[dst] = engine.scalar(state[dst], gate[2], gate[3], "scalar-scale")
            else:
                need(gate[0] == "add", "Scalar operation")
                term = engine.scalar(state[reg(gate[2])], gate[3], gate[4], "scalar-multiply")
                state[dst] = engine.add(state[dst], term)
        elif kind == "climb":
            _, _, dst, old, new, _ = event
            if state[dst] != engine.zero:
                state[dst] = engine.recipe(state[dst], children[old, new])
        elif kind == "adapter":
            _, direction, dst, _ = event
            if direction == "old_to_new" and dst < 112:
                state[dst] = engine.mono(state[dst], N.monomial_key(adapters["source", dst]["left"]))
            elif direction == "new_to_old" and 112 <= dst < 224:
                state[dst] = engine.mono(state[dst], N.monomial_key(adapters["target", dst-112]["left"]), True)
        elif kind == "residual_adapter":
            direction, dst, a = event[1:4]
            b = event[4] if len(event) == 5 else 1
            key = str(a) if b == 1 else f"{a}:{b}"
            part = "right" if direction == "pre" else "left"
            state[dst] = engine.mono(state[dst], N.monomial_key(residuals["recipes"][key][part]), True)
        elif kind == "native_line":
            dst = reg(event[1])
            state[dst] = engine.recipe(state[dst], packet["native_line_recipes"][event[2]]["recipe"])
        else:
            need(kind == "phase", "Unknown physical event")
        if trace is not None and kind != "phase":
            changed = (reg(event[1][1]) if kind == "scalar" else reg(event[1])
                       if kind == "native_line" else event[2])
            trace.append((index, changed, vector_digest(engine.canonical(state[changed]))))
    return [engine.canonical(value) for value in state], engine.report(), cuts


def summary(state):
    values = []
    for i, (re, im, e) in enumerate(state):
        if any(re) or any(im):
            values.append({"register": i, "real_values": sorted(set(re)),
                           "imag_values": sorted(set(im)), "denominator_power": e})
    return {"endpoint_sha256": digest(state), "nonzero_fields": values}


def expected(dirty=True, rounded=False, signal=1):
    state = [N.ZERO] * 712
    state[112] = N.scaled(N.ONE, Fraction(signal))
    state[224] = N.scaled(N.ONE, Fraction(signal * 2**65)) if dirty else N.ZERO
    if rounded:
        state[112] = N.ZERO
        for at in (114, 137, 190, 211):
            state[at] = N.scaled(N.ONE, Fraction(-signal, 2))
    return state


def audit():
    data = load()
    need(data[2]["start"][224] == 0 and data[2]["final"][224] == 1,
         "Ordinary dirty-helper endpoints")
    trace = []
    numeric = Dyadic(53)
    state, faults, cuts = run(data, engine=numeric, trace=trace)
    need(-1022 <= numeric.low_exponent <= numeric.high_exponent < 1023,
         "Normal finite binary64 primitive range")
    for event in data[0]:
        if event[0] == "scalar" and event[1][0] != "clear":
            gate = event[1]
            coefficient = Fraction(*gate[-2:])
            n, d = coefficient.numerator, coefficient.denominator
            need(0 < d and d & (d-1) == 0 and abs(n).bit_length() <= 53,
                 "Exactly representable scalar coefficient")
    need(state == expected(rounded=True), "Native rounded endpoint")
    need(faults == [{"event": i, "stage": "scalar-add", "rounded_components": 512,
                     "max_component_error": "1/2"} for i in (3887, 4060)],
         "Exactly two genuine native rounding sites")
    for i in (3887, 4060):
        need(cuts[i] == [N.scaled(N.ONE, Fraction(1, 2)),
                         N.scaled(N.ONE, Fraction(2**65))], "Physical fault operands")
    binary_trace = []
    binary, _, binary_cuts = run(data, engine=Binary64(), trace=binary_trace)
    need(binary == state and binary_cuts == cuts and binary_trace == trace,
         "Every changed-field native cut agrees with actual binary64")
    controls = {}
    for name, bits, dirty in (("exact", None, True), ("wider65", 65, True),
                              ("clean", 53, False)):
        out, info, _ = run(data, bits=bits, dirty=dirty)
        need(out == expected(dirty=dirty) and not info, "Escape control: " + name)
        controls[name] = digest(out)
    return {"schema_version": 1, "status": "PASS_QQ16_NATIVE_ROUNDED_COMPONENTS",
            "scope": "Finite 512-complex-coordinate native F0, specified pair-first binary arithmetic",
            "expanded_events": len(data[0]), "event_sha256": digest(data[0]),
            "changed_field_cuts": len(trace), "changed_field_trace_sha256": digest(trace),
            "endpoint": summary(state), "rounding": faults,
            "physical_cut_sha256": {str(k): digest(v) for k, v in cuts.items()},
            "controls": controls, "binary64_every_changed_cut_agrees": True,
            "all_480_helpers_restore_as_values": True, "all_8_private_fields_zero": True,
            "native_internal_rounded_components": 0,
            "nonzero_primitive_binary_exponents": [numeric.low_exponent, numeric.high_exponent],
            "native_implementation_cost_admitted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="Create an absent receipt")
    args = parser.parse_args()
    result = audit()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(json.loads((HERE / "RESULT.json").read_text()) == result, "Result receipt mismatch")
    print(result["status"])
    print("26099 events; 26089 changed-field cuts agree with binary64; 480 helpers restore.")


if __name__ == "__main__":
    main()
