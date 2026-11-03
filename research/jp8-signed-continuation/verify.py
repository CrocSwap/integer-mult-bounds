"""Check one new JP8 splice. Produced by Nick Petalas. Apache-2.0."""

import gzip
import hashlib
import itertools
import json
import platform
import runpy
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REGISTERS = (81, 227, 230, 231, 232, 724)
SOURCE, WORK = 81, 724
CONSTRUCTOR = "research/jp8-additive-coefficient-routes/construct.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    raw = path.read_bytes()
    require(len(raw) <= 2_000_000, "JSON input too large")
    return json.loads(raw)


def load_fragment():
    pins = read_json(HERE / "SOURCES.json")
    for row in pins["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            require(digest(raw) == row["sha256"], "source hash mismatch")
    witness = read_json(HERE / "WITNESS.json")
    require((witness["start"], witness["stop"]) == (19709, 19713),
            "fragment boundary mismatch")
    raw = gzip.decompress((ROOT / witness["program_path"]).read_bytes())
    require(len(raw) < 16_000_000, "program payload too large")
    events = json.loads(raw)["forward"]
    require(len(events) < 100_000, "program event limit")
    selected = events[19709:19713]
    require(selected == witness["events"], "literal source fragment mismatch")
    phases = [event[1] for event in events[:19710] if event[0] == "phase"]
    require(phases[-1] == "full_frame_cleanup", "wrong source phase")
    expected = ((227, 3, 2), (230, -3, 2), (231, -1, 2), (232, 5, 2))
    for event, (target, numerator, denominator) in zip(selected, expected):
        require(event == ["scalar", ["add", ["L", target], ["L", SOURCE],
                                    numerator, denominator], 1],
                "source operands, frame or coefficients changed")
    parent = runpy.run_path(str(ROOT / CONSTRUCTOR))
    blocks = witness["parent_blocks"]
    require(blocks == [{"start": 19709, "stop": 19711,
                        "routes": [["shift", 0]]},
                       {"start": 19711, "stop": 19713,
                        "routes": [["read", -1, 1]]}], "parent blocks changed")
    first = parent["lower_block"](events, blocks[0])
    second = parent["lower_block"](events, blocks[1])
    baseline = first + second
    replacement = witness["replacement"]
    require(replacement == first[:-1] + [["sub", WORK, SOURCE]] + second[3:],
            "replacement is not the declared single signed continuation")
    require((len(baseline), len(replacement)) == (17, 14), "wrong local bill")
    return selected, baseline, replacement


def execute_matrix(word):
    require(0 < len(word) <= 32, "word length limit")
    n = len(REGISTERS)
    rows = {r: [Fraction(int(j == i)) for j in range(n)]
            for i, r in enumerate(REGISTERS)}
    peaks = []
    for operation in word:
        tag, target = operation[:2]
        require(target in rows, "unknown target")
        if tag == "clear":
            require(len(operation) == 2, "clear arity")
            rows[target] = [Fraction(0)] * n
        elif tag in ("halve", "double"):
            require(len(operation) == 2, "scale arity")
            factor = Fraction(1, 2) if tag == "halve" else 2
            rows[target] = [factor * x for x in rows[target]]
        else:
            require(tag in ("add", "sub") and len(operation) == 3,
                    "unsupported primitive")
            source = operation[2]
            require(source in rows and source != target, "invalid source")
            sign = 1 if tag == "add" else -1
            rows[target] = [a + sign * b for a, b in zip(rows[target], rows[source])]
        peaks.append(sum(abs(x) for x in rows[WORK]))
    return rows, peaks


def target_matrix():
    n = len(REGISTERS)
    rows = {r: [Fraction(int(j == i)) for j in range(n)]
            for i, r in enumerate(REGISTERS)}
    for target, coefficient in ((227, Fraction(3, 2)), (230, Fraction(-3, 2)),
                                (231, Fraction(-1, 2)), (232, Fraction(5, 2))):
        rows[target][0] = coefficient
    rows[WORK] = [Fraction(0)] * n
    return rows


def check_word(word):
    rows, peaks = execute_matrix(word)
    require(rows == target_matrix(), "arbitrary-input endpoint mismatch")
    require(max(peaks) == 3, "exact work magnitude coefficient changed")
    return rows, peaks


def integer_grid(word):
    """Separate literal scalar engine on fourfold integer input values."""
    require(len(word) <= 32, "grid word length limit")
    cases = 0
    for values in itertools.product(range(-2, 3), repeat=6):
        state = dict(zip(REGISTERS, (4 * value for value in values)))
        for operation in word:
            tag, target = operation[:2]
            if tag == "clear":
                state[target] = 0
            elif tag == "double":
                state[target] *= 2
            elif tag == "halve":
                require(state[target] % 2 == 0, "integer grid division not exact")
                state[target] //= 2
            elif tag == "add":
                state[target] += state[operation[2]]
            elif tag == "sub":
                state[target] -= state[operation[2]]
            else:
                raise ValueError("unknown grid instruction")
        source, a, b, c, d, _ = values
        expected = (4 * source, 4 * a + 6 * source, 4 * b - 6 * source,
                    4 * c - 2 * source, 4 * d + 10 * source, 0)
        require(tuple(state[r] for r in REGISTERS) == expected,
                "literal grid endpoint mismatch")
        cases += 1
    return cases


def controls(word):
    mutants = {"missing_initial_clear": word[1:],
               "missing_final_clear": word[:-1],
               "missing_subtraction": word[:7] + word[8:],
               "addition_instead": [*word[:7], ["add", WORK, SOURCE], *word[8:]],
               "wrong_source": [*word[:7], ["sub", WORK, 227], *word[8:]],
               "wrong_target_sign": [*word[:6], ["add", 230, WORK], *word[7:]],
               "extra_work_excursion": word[:1] + [["add", WORK, SOURCE],
                   ["double", WORK], ["double", WORK], ["sub", WORK, SOURCE],
                   ["sub", WORK, SOURCE], ["sub", WORK, SOURCE],
                   ["sub", WORK, SOURCE]] + word[1:]}
    rejected = []
    for name, mutant in mutants.items():
        try:
            check_word(mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted mutation: " + name)
    return rejected


def main():
    events, baseline, replacement = load_fragment()
    reference, old_peaks = check_word(baseline)
    result, new_peaks = check_word(replacement)
    require(result == reference, "splice changes its complete matrix")
    old_cases = integer_grid(baseline)
    new_cases = integer_grid(replacement)
    rejected = controls(replacement)
    source_hashes = {p.name: digest(p.read_bytes()) for p in sorted(HERE.iterdir())
                     if p.is_file()}
    receipt = {"status": "PASS_JP8_SIGNED_CONTINUATION", "claim_type":
               "finite circuit certificate with a scoped substitution proof",
               "python": platform.python_version(), "events": len(events),
               "independent_inputs": len(REGISTERS), "before": len(baseline),
               "after": len(replacement), "real_component_saving":
               2 * (len(baseline) - len(replacement)),
               "baseline_grid_cases": old_cases, "replacement_grid_cases": new_cases,
               "old_work_peaks": list(map(str, old_peaks)),
               "new_work_peaks": list(map(str, new_peaks)),
               "rejected_controls": rejected, "package_sha256": source_hashes}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
