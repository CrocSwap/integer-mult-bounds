#!/usr/bin/env python3
"""Second full scalar interpreter, using Fraction coefficients throughout.

Michał Ciemięga (@zewelor), substantial OpenAI Codex assistance, Apache-2.0.
No imports from verify.py, controls.py, or their row-arithmetic implementation.
The source programs and the two lowerers are intentionally shared inputs.
This checks finite scalar traces, not physical frames or the full theorem.
"""
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/"
REFERENCE = "research/complex-dyadic-lowering/lower.py"
WORK = ("W", 0)
REGISTERS = [("L", i) for i in range(716)] + [WORK] + [("C", i) for i in range(8)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def load_lower(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lower


def basis():
    return {r: {i: Fraction(1)} for i, r in enumerate(REGISTERS)}


class FractionMachine:
    def __init__(self):
        self.state = basis()
        self.counts = Counter()
        self.reads = self.source_reads = self.depth = 0
        self.peak = Fraction(1)
        self.stream = hashlib.sha256()

    def execute(self, word, target, macro_source, event_index=0, frame=0):
        for instruction in word:
            tag, dst = instruction[:2]
            binary = tag in ("copy", "add", "subtract")
            require(len(instruction) == (3 if binary else 2), "arity")
            require(dst in self.state and dst in (target, WORK), "write outside macro")
            src = instruction[2] if binary else None
            if binary:
                require(src in self.state and src != dst, "source alias or missing register")
                require(src in (target, macro_source, WORK), "read outside macro")
            operands = ([] if tag == "clear" else [src] if tag == "copy"
                        else [dst, src] if binary else [dst])
            self.reads += len(operands)
            self.source_reads += operands.count(macro_source) if macro_source is not None else 0
            if tag == "clear":
                result = {}
            elif tag == "copy":
                result = self.state[src].copy()
            elif tag in ("add", "subtract"):
                result = self.state[dst].copy()
                for column, coefficient in self.state[src].items():
                    if tag == "add":
                        result[column] = result.get(column, Fraction(0)) + coefficient
                    else:
                        result[column] = result.get(column, Fraction(0)) - coefficient
            elif tag in ("double", "halve", "negate"):
                factor = {"double": Fraction(2), "halve": Fraction(1, 2), "negate": Fraction(-1)}[tag]
                result = {column: factor*coefficient for column, coefficient in self.state[dst].items()}
            else:
                raise ValueError("unknown primitive")
            self.state[dst] = {column: coefficient for column, coefficient in result.items() if coefficient}
            self.peak = max(self.peak, sum(map(abs, self.state[dst].values()), Fraction(0)))
            for coefficient in self.state[dst].values():
                denominator = coefficient.denominator
                require(denominator & (denominator-1) == 0, "nondyadic coefficient")
                self.depth = max(self.depth, denominator.bit_length()-1)
            self.counts[tag] += 1
            self.stream.update(encode([event_index, frame, instruction]) + b"\n")

    def receipt(self):
        return {"real_primitives": 2*sum(self.counts.values()),
                "primitive_counts": {key: 2*value for key, value in sorted(self.counts.items())},
                "real_macro_source_reads": 2*self.source_reads, "real_operand_reads": 2*self.reads,
                "maximum_denominator_depth": self.depth, "maximum_row_l1": str(self.peak),
                "stream_sha256": self.stream.hexdigest()}


def macro_endpoint(before, op):
    """Specify the entire macro map directly, without primitive execution."""
    tag, dst = op[0], tuple(op[1])
    after = before.copy()
    if tag == "clear":
        after[dst] = {}
    elif tag == "copy":
        after[dst] = before[tuple(op[2])].copy()
    elif tag == "scale":
        factor = Fraction(op[2], op[3])
        after[dst] = {i: x*factor for i, x in before[dst].items() if x*factor}
    elif tag == "add":
        src, q = tuple(op[2]), Fraction(op[3], op[4])
        after[dst] = {i: before[dst].get(i, 0) + q*before[src].get(i, 0)
                      for i in before[dst].keys() | before[src].keys()}
        after[dst] = {i: x for i, x in after[dst].items() if x}
        after[WORK] = {}
    else:
        raise ValueError("unknown macro")
    return after


def check_direction(direction, events, expected, baseline, candidate):
    machines = [FractionMachine(), FractionMachine()]
    changed, coefficients, phases, frames, paid = [], Counter(), Counter(), Counter(), Counter()
    nonscalar = hashlib.sha256()
    phase, macros = None, 0
    for index, event in enumerate(events):
        if event[0] != "scalar":
            require(event[0] in ("phase", "center", "climb", "adapter", "residual_adapter"), "unknown event")
            nonscalar.update(encode([index, event]) + b"\n")
            if event[0] == "phase":
                phase = event[1]
            if event[0] in ("center", "climb"):
                paid[str(event[4] if event[0] == "center" else event[5])] += 1
            continue
        _, op, frame = event
        dst = tuple(op[1])
        src = tuple(op[2]) if op[0] in ("add", "copy") else None
        words = [baseline(op), candidate(op, baseline)]
        qualifies = op[0] == "add" and abs(Fraction(op[3], op[4])) in (2, 3)
        require((words[0] != words[1]) == qualifies, "replacement domain")
        if qualifies:
            changed.append(index)
            coefficients[str(Fraction(op[3], op[4]))] += 1
            phases[str(phase)] += 1
            frames[str(frame)] += 1
        endpoint = macro_endpoint(machines[0].state, op)
        for machine, word in zip(machines, words):
            machine.execute(word, dst, src, index, frame)
            require(machine.state == endpoint, f"{direction}: full boundary at event {index}")
        macros += 1
    endpoint = basis()
    for i in range(112):
        if direction == "forward":
            endpoint[("L", i+112)][i] = Fraction(1)
        else:
            endpoint[("L", i)][i+112] = Fraction(-1)
    for register in REGISTERS[716:]:
        endpoint[register] = {}
    for machine in machines:
        require(machine.state == endpoint, "final shear, helper restoration or private clear")
    old, new = (machine.receipt() for machine in machines)
    actual = {"events": len(events), "macros": macros, "exact_input_columns": len(REGISTERS),
              "dirty_helpers_restored": 716-2*112, "private_registers_cleared": len(REGISTERS)-716,
              "changed_macros": len(changed), "changed_event_indices": changed,
              "coefficient_census": dict(coefficients), "phase_census": dict(phases),
              "frame_census": dict(frames), "paid_profile": dict(paid),
              "retained_nonscalar_sha256": nonscalar.hexdigest(), "baseline": old, "candidate": new,
              "saved_real_primitives": old["real_primitives"]-new["real_primitives"]}
    require(encode(actual) == encode(expected), f"{direction}: Fraction receipt mismatch")
    print(f"PASS_FRACTION_{direction.upper()} macros={macros} columns={len(REGISTERS)} "
          f"saved={actual['saved_real_primitives']}", flush=True)


def check_rejections(baseline, candidate):
    op = ["add", ["L", 0], ["L", 1], 3, 1]
    word = candidate(op, baseline)
    endpoint = macro_endpoint(basis(), op)
    mutants = [word[:-1], word[1:], [("subtract", ("L", 0), ("L", 1))]+word[1:],
               [("add", ("L", 0), WORK)]+word[1:]]
    for mutant in mutants:
        machine = FractionMachine()
        machine.execute(mutant, ("L", 0), ("L", 1))
        require(machine.state != endpoint, "accepted wrong endpoint or private dirt")
    # Endpoint-preserving perturbations must still change the checked receipt.
    good = FractionMachine()
    good.execute(word, ("L", 0), ("L", 1))
    for metric, prefix in (
        ("maximum_denominator_depth", [("halve", ("L", 0)), ("double", ("L", 0))]),
        ("maximum_row_l1", [("double", ("L", 0))]*3+[("halve", ("L", 0))]*3),
        ("real_primitives", [("clear", WORK)]),
    ):
        machine = FractionMachine()
        machine.execute(prefix+word, ("L", 0), ("L", 1))
        require(machine.state == endpoint, "invalid endpoint-preserving control")
        require(Fraction(machine.receipt()[metric]) > Fraction(good.receipt()[metric]),
                "missed changed prefix or cost: " + metric)
    print("PASS_FRACTION_CONTROLS endpoint_mutations=4 prefix_or_cost_mutations=3", flush=True)


def main():
    pins = read(HERE / "SOURCES.json")
    for name, pin in pins["files"].items():
        payload = (ROOT / name).read_bytes()
        if name.endswith(".gz"):
            payload = gzip.decompress(payload)
        require(hashlib.sha256(payload).hexdigest() == pin["sha256"], "source pin: " + name)
    baseline = load_lower(ROOT / REFERENCE, "fraction_pr696")
    candidate = load_lower(HERE / "lower.py", "fraction_candidate")
    expected = read(HERE / "EXPECTED.json")
    programs = read(ROOT / (PROVIDER + "LOCAL-PROGRAMS.json.gz"))
    require(set(programs) == {"forward", "backward"}, "orientation coverage")
    check_rejections(baseline, candidate)
    for direction in ("forward", "backward"):
        check_direction(direction, programs[direction], expected["programs"][direction], baseline, candidate)
    print("PASS_JP8_FRACTION_RECHECK all_program_receipt_fields=equal no_new_kappa")


if __name__ == "__main__":
    main()
