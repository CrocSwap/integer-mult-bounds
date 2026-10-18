#!/usr/bin/env python3
"""Exact all-cut input and defect maps of the completed PR2139 P104 word."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
WORD_SHA256 = "8be1f3c659d887030fa70afdbdeca38fbfbaea1b2a57b1783d3669e92816545c"
MAX_BYTES = 4 * 1024 * 1024


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_word(path=HERE / "WORD.json.gz"):
    need(path.stat().st_size <= MAX_BYTES, "compressed stream capacity")
    with gzip.open(path, "rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    need(len(raw) <= MAX_BYTES, "decompressed stream capacity")
    need(hashlib.sha256(raw).hexdigest() == WORD_SHA256, "literal stream authentication")
    return json.loads(raw)


class Instruction(NamedTuple):
    op: str
    dst: int = -1
    src: int = -1
    coefficient: Q = Q(0)
    rank: int = 0


def coefficient(value):
    q = Q(value)
    need(q != 0 and abs(q) <= 65536, "nonzero bounded coefficient")
    need(q.denominator <= 65536 and q.denominator & (q.denominator - 1) == 0,
         "bounded dyadic coefficient")
    return q


def register(reference):
    need(isinstance(reference, list) and len(reference) == 2, "register reference")
    kind, index = reference
    need(kind in ("C", "L") and type(index) is int, "register kind/index")
    limit = 8 if kind == "C" else 844
    need(0 <= index < limit, "register index capacity")
    return index + (704 if kind == "C" else 0)


def span(basis):
    need(isinstance(basis, list) and len(basis) <= 9, "binary basis capacity")
    values = {0}
    for value in basis:
        need(type(value) is int and 0 <= value < 512, "nine-bit frame label")
        values.update(x ^ value for x in tuple(values))
    return frozenset(values)


def scalar_instruction(event, current):
    need(len(event) == 3 and isinstance(event[1], list), "scalar event shape")
    op, frame = event[1:]
    dst = register(op[1])
    need(current[dst] == frame, "scalar destination chart")
    code = op[0]
    if code == "clear":
        need(len(op) == 2 and 704 <= dst < 712 and frame == 0, "owned exact clear")
        return Instruction("reset", dst)
    if code == "scale":
        need(len(op) == 4, "scale shape")
        return Instruction(code, dst, coefficient=coefficient(Q(op[2], op[3])))
    need(code == "add" and len(op) == 5, "scalar opcode/shape")
    src = register(op[2])
    need(src != dst and current[src] == frame, "distinct common-chart operands")
    return Instruction(code, dst, src, coefficient(Q(op[3], op[4])))


def action_instruction(event, current, frames):
    need(isinstance(event, list) and 2 <= len(event) <= 6, "action shape")
    if event[0] == "scalar":
        return scalar_instruction(event, current)
    if event[0] == "owned_init":
        need(len(event) == 3 and 704 <= event[1] < 712, "owned private reset")
        dst, new = event[1:]
        need(0 <= new < len(frames), "private reset frame")
        current[dst] = new
        return Instruction("reset", dst)
    if event[0] == "climb":
        need(len(event) == 6, "transport shape")
        dst, old, new, rank = event[2:]
        need(type(dst) is int and 0 <= dst < 844, "transport register")
        need(0 <= old < len(frames) and 0 <= new < len(frames), "transport frame indices")
        need(current[dst] == old, "transport entry chart")
        a, b = frames[old], frames[new]
        need(a <= b or b <= a, "nested native transport")
        need(rank == abs(len(a).bit_length() - len(b).bit_length()) and rank > 0,
             "positive transport rank")
        current[dst] = new
        return Instruction("transport", dst, rank=rank)
    need(event[0] in ("phase", "adapter", "residual_adapter"), "action opcode")
    return Instruction("exact")


def normalize(word):
    need(word["schema_version"] == 1 and word["total_roles"] == 844, "word geometry")
    need(len(word["initial_frames"]) == len(word["final_frames"]) == 844,
         "boundary role inventory")
    need(len(word["frame_bases"]) == 1008, "frame inventory")
    frames = [span(basis) for basis in word["frame_bases"]]
    current = list(word["initial_frames"])
    need(all(type(f) is int and 0 <= f < len(frames) for f in current), "initial frames")
    live = word["live_ports"]
    need(len(live) == 104 and live == sorted(set(live)) and all(0 <= p < 112 for p in live),
         "live P104 ports")
    need(len(word["compensation"]) == 7686 and len(word["actions"]) == 26647,
         "complete instruction inventory")
    program = []
    for dst, src, raw in word["compensation"]:
        need(type(dst) is int and type(src) is int and 0 <= dst < 844 and 0 <= src < 844,
             "compensation indices")
        need(dst != src and current[dst] == current[src] == 0, "baseline common zero chart")
        program.append(Instruction("add", dst, src, coefficient(raw)))
    for event in word["actions"]:
        program.append(action_instruction(event, current, frames))
    need(current == word["final_frames"], "complete output charts")
    paid = Counter(e.rank for e in program if e.op == "transport")
    need(dict(paid) == {1: 2564, 2: 547, 3: 432, 4: 142, 5: 83, 6: 128, 7: 11},
         "complete predecessor paid profile")
    return program


class DyadicRow:
    """Integer coefficients at one row-local power-of-two denominator."""
    def __init__(self, weights, initial=None):
        self.weights = weights
        self.exponent = 0
        self.values = {} if initial is None else {initial: 1}
        self.absolute = 0 if initial is None else 1
        self.weighted = 0

    def add_scaled(self, other, q):
        denominator_bits = q.denominator.bit_length() - 1
        exponent = max(self.exponent, other.exponent + denominator_bits)
        if exponent != self.exponent:
            factor = 1 << (exponent - self.exponent)
            self.values = {j: v * factor for j, v in self.values.items()}
            self.absolute *= factor
            self.weighted *= factor
            self.exponent = exponent
        factor = q.numerator << (exponent - other.exponent - denominator_bits)
        for j, value in other.values.items():
            old = self.values.get(j, 0)
            new = old + value * factor
            change = abs(new) - abs(old)
            self.absolute += change
            self.weighted += change * self.weights[j]
            if new:
                self.values[j] = new
            else:
                self.values.pop(j, None)

    def scale(self, q):
        self.exponent += q.denominator.bit_length() - 1
        self.values = {j: v * q.numerator for j, v in self.values.items()}
        self.absolute *= abs(q.numerator)
        self.weighted *= abs(q.numerator)

    def inject(self, index):
        value = 1 << self.exponent
        self.values[index] = value
        self.absolute += value
        self.weighted += value * self.weights[index]

    def coefficients(self):
        return {j: Q(v, 1 << self.exponent) for j, v in self.values.items()}


def weights_for(program):
    result = []
    for event in program:
        if event.op == "add":
            result.append(1 + abs(event.coefficient))
        elif event.op == "scale":
            result.append(abs(event.coefficient))
        else:
            result.append(Q(int(event.op == "transport")))
    bits = max((q.denominator.bit_length() - 1 for q in result), default=0)
    return result, bits, tuple(int(q * (1 << bits)) for q in result)


def update(rows, event, weights):
    dst = event.dst
    if event.op == "reset":
        rows[dst] = DyadicRow(weights)
    elif event.op == "add":
        rows[dst].add_scaled(rows[event.src], event.coefficient)
    elif event.op == "scale":
        rows[dst].scale(event.coefficient)


def analyze(program, roles=844):
    need(1 <= roles <= 844 and 1 <= len(program) <= 34333, "replay domain capacity")
    weights, bits, integers = weights_for(program)
    zero_weights = (0,) * roles
    inputs = [DyadicRow(zero_weights, i) for i in range(roles)]
    errors = [DyadicRow(integers) for _ in range(roles)]
    peaks = [(Q(1), -1, 0, {0: Q(1)}), (Q(0), -1, 0, {}), (Q(0), -1, 0, {})]
    stream = hashlib.sha256()
    max_slots = slots = 0
    max_exponent = 0
    for index, event in enumerate(program):
        if event.op == "exact":
            continue
        dst = event.dst
        before = len(errors[dst].values)
        update(inputs, event, zero_weights)
        update(errors, event, integers)
        if weights[index]:
            errors[dst].inject(index)
        slots += len(errors[dst].values) - before
        max_slots = max(max_slots, slots)
        ir, er = inputs[dst], errors[dst]
        need(ir.absolute == sum(map(abs, ir.values.values())), "input row norm cache")
        need(er.absolute == sum(map(abs, er.values.values())), "defect row norm cache")
        need(er.weighted == sum(abs(v) * integers[j] for j, v in er.values.items()),
             "weighted defect row norm cache")
        values = (Q(ir.absolute, 1 << ir.exponent), Q(er.absolute, 1 << er.exponent),
                  Q(er.weighted, 1 << (er.exponent + bits)))
        for which, value in enumerate(values):
            if value > peaks[which][0]:
                row = ir if which == 0 else er
                peaks[which] = value, index, dst, row.coefficients()
        stream.update(canonical([index, dst, *map(str, values)]) + b"\n")
        max_exponent = max(max_exponent, ir.exponent, er.exponent)
    return {"inputs": inputs, "errors": errors, "weights": weights, "peaks": peaks,
            "norm_stream_sha256": stream.hexdigest(), "max_error_slots": max_slots,
            "max_row_denominator_bits": max_exponent}


def endpoint_check(result, live):
    for reg, row in enumerate(result["inputs"]):
        expected = {} if 704 <= reg < 712 else {reg: Q(1)}
        if 112 <= reg < 224 and reg - 112 in live:
            expected[reg - 112] = Q(1)
        need(row.coefficients() == expected, "arbitrary-input endpoint: " + str(reg))


def adjoint(program, stop, target, roles=844):
    """Separate Fraction recurrence for one cut, with no integer-row machinery."""
    need(1 <= roles <= 844 and 0 <= target < roles and -1 <= stop < len(program) <= 34333,
         "reverse cut capacity")
    row = [Q(int(i == target)) for i in range(roles)]
    defects = {}
    for index in range(stop, -1, -1):
        event = program[index]
        if event.op == "exact":
            continue
        dst = event.dst
        if event.op in ("add", "scale", "transport") and row[dst]:
            defects[index] = row[dst]
        if event.op == "reset":
            row[dst] = Q(0)
        elif event.op == "add":
            row[event.src] += event.coefficient * row[dst]
        elif event.op == "scale":
            row[dst] *= event.coefficient
    return {i: q for i, q in enumerate(row) if q}, defects


def injected(program, stop, target, inputs=None, defects=None, roles=844):
    need(1 <= roles <= 844 and 0 <= target < roles and -1 <= stop < len(program) <= 34333,
         "injected cut capacity")
    state = [Q(0)] * roles
    for i, q in (inputs or {}).items():
        state[i] = q
    for index in range(stop + 1):
        event = program[index]
        if event.op == "exact":
            continue
        dst = event.dst
        if event.op == "reset":
            state[dst] = Q(0)
        elif event.op == "add":
            state[dst] += event.coefficient * state[event.src]
        elif event.op == "scale":
            state[dst] *= event.coefficient
        if defects and index in defects:
            state[dst] += defects[index]
    return state[target]


def check_peaks(program, result):
    for which, (value, index, target, witness) in enumerate(result["peaks"]):
        inputs, defects = adjoint(program, index, target)
        need(witness == (inputs if which == 0 else defects), "reverse cut coefficient identity")
        signs = {j: Q(1 if q > 0 else -1) for j, q in witness.items()}
        if which == 0:
            actual = injected(program, index, target, inputs=signs)
        else:
            if which == 2:
                signs = {j: q * result["weights"][j] for j, q in signs.items()}
            actual = injected(program, index, target, defects=signs)
        need(actual == value, "constructive peak attainment")


def guard_bits(P, K):
    need(P >= 0 and K > 0, "nonnegative input and positive feedback coefficients")
    bits = 0
    for candidate in range(1025):
        if Q(1 << candidate) >= K * (P + 1):
            bits = candidate
            break
    else:
        raise ValueError("guard-bit capacity exceeded")
    need(K < 1 << bits, "strict feedback guard")
    return bits


def summarize(program, word, result):
    P, A, K = (peak[0] for peak in result["peaks"])
    guards = guard_bits(P, K)
    groups = {"source": word["live_ports"], "target": [112 + t for t in word["live_ports"]],
              "dirty_helper": [r for r in range(844) if r not in word["live_ports"]
                               and r not in [112 + t for t in word["live_ports"]]
                               and not 704 <= r < 712], "private": list(range(704, 712))}
    endpoint = {}
    for name, regs in groups.items():
        rows = [result["errors"][r].coefficients() for r in regs]
        endpoint[name] = {"roles": len(regs),
                          "absolute": str(max(sum(map(abs, row.values()), Q(0)) for row in rows)),
                          "relative": str(max(sum((abs(v) * result["weights"][j]
                                                   for j, v in row.items()), Q(0)) for row in rows))}
    need(P == 131072 and A == 1394705 and K == 2134050 and guards == 39,
         "complete all-cut constants")
    peaks = {name: {"value": str(value), "event": index, "register": reg,
                   "witness": [[j, str(q)] for j, q in sorted(row.items())]}
             for name, (value, index, reg, row) in zip(("input", "absolute", "relative"), result["peaks"])}
    return {"status": "PASS_P104_DELAYED_PRECISION", "word_sha256": WORD_SHA256,
            "events": len(program), "roles": 844,
            "defect_sites": sum(bool(w) for w in result["weights"]),
            "op_counts": dict(sorted(Counter(e.op for e in program).items())),
            "paid_mass": sum(e.rank for e in program), "all_cut_peaks": peaks,
            "endpoint_error_maxima": endpoint, "uniform_relative_guard_bits": guards,
            "all_cut_norms_sha256": result["norm_stream_sha256"],
            "maximum_live_error_coefficients": result["max_error_slots"],
            "maximum_row_denominator_bits": result["max_row_denominator_bits"],
            "evidence": ["full arbitrary-input endpoint and paid profile", "three reverse cut identities",
                         "three sign-aligned attaining executions"],
            "scope": "Finite completed forward word, conditional unitary-chart/completed-child defect contract. No rounded-child, global hosting, all-size, supplier or kappa claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create a new canonical receipt exclusively")
    args = parser.parse_args()
    word = load_word()
    program = normalize(word)
    result = analyze(program)
    endpoint_check(result, word["live_ports"])
    check_peaks(program, result)
    receipt = summarize(program, word, result)
    if args.write:
        with args.write.open("x") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        need(canonical(receipt) == canonical(json.loads((HERE / "RESULT.json").read_text())),
             "complete canonical precision receipt")
    print("PASS_P104_DELAYED_PRECISION input=131072 absolute=1394705 relative=2134050 "
          "guard_bits=39 endpoint_columns=844 reverse_cuts=3 no_new_kappa")


if __name__ == "__main__":
    main()
