"""Source-bound finite checks of the new literal-program refinement; writes stdout only."""
import hashlib
import json
from pathlib import Path
import sys
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from refine import MAX_PROGRAM, P, TEMP, VALUE, macro, refine, require


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            require(path.stat().st_size < 1_000_000, "input file capacity")
            require(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                    "source bytes: " + row["path"])


def load_producer():
    authenticate()
    sys.path.insert(0, str(ROOT / "research/wordram-ntt-kernel"))
    import ram_multiplier
    from ram.wordram_kernel import MASK, SCRATCH, run
    return ram_multiplier, MASK, SCRATCH, run


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def template_checks(producer):
    rows = []
    for digits in (1, 2, 4, 8, 16, 32, 64, 128, 256):
        plan = producer.build_multiplier(digits, digits)
        result = refine(plan.program)
        count = len(result.replacements)
        require(count == 3 * (plan.n - 1), "unit-twiddle count")
        require(len(plan.program) <= MAX_PROGRAM, "producer capacity")
        rows.append({"digits": digits, "n": plan.n, "replacements": count,
                     "static_before": len(plan.program),
                     "static_after": len(result.program),
                     "dynamic_saving": 31 * count,
                     "new_program_sha256": digest(result.program)})
    require(rows[-1]["static_after"] == 435650, "512-point static count")
    return rows


def local_checks(producer, mask, run):
    from ram.wordram_kernel import Builder
    builder = Builder()
    builder.setup()
    builder.literal(100, 1)
    start = len(builder.code)
    builder._mul(101, 100, VALUE)
    stop = len(builder.code)
    builder.accept()
    old = builder.program()
    replacement = macro(old, start)
    old_block = old[:stop] + [("accept",)]
    new_block = old[:start] + list(replacement) + [("accept",)]
    counts = 0
    for value in range(P):
        dirty = {101: value, 100: mask - value, VALUE: mask, TEMP: value ^ 123,
                 -77: value + 4, 777777: mask - 9}
        before = run(old_block, dirty)
        after = run(new_block, dirty)
        require(before is not None and after is not None, "local halt")
        require(before.accepted and after.accepted, "local accept")
        require(before.memory == after.memory, "full local memory")
        require(before.steps - after.steps == 31, "local dynamic saving")
        require(after.memory[VALUE] == value, "unit result")
        require(after.memory[TEMP] == (value - P) & mask, "scratch result")
        counts += 1
    return counts


def whole_checks(producer, mask, scratch, run):
    rows = []
    for digits in (1, 2, 4, 8, 16, 32, 64, 128, 256):
        plan = producer.build_multiplier(digits, digits)
        result = refine(plan.program)
        fixtures = ([0] * digits, [15] * digits,
                    [int(i == 0) for i in range(digits)],
                    [(7 * i + 3) % 16 for i in range(digits)])
        pairs = ((fixtures[0], fixtures[1]), (fixtures[1], fixtures[1]),
                 (fixtures[2], fixtures[3]), (fixtures[3], fixtures[3][::-1]))
        for index, (left, right) in enumerate(pairs):
            memory = {cell: (mask - cell) & mask for cell in
                      plan.temporaries | scratch | set(plan.output)}
            memory.update(zip(plan.left, left))
            memory.update(zip(plan.right, right))
            memory.update({-77: mask, 777777: 123456})
            before = run(plan.program, memory)
            after = run(result.program, memory)
            require(before is not None and after is not None, "whole halt")
            require(before.accepted and after.accepted, "whole accept")
            require(before.memory == after.memory, "full whole memory")
            require(before.steps - after.steps == 31 * len(result.replacements),
                    "whole dynamic saving")
            output = sum(after.memory[c] * 16 ** i for i, c in enumerate(plan.output))
            expected = (sum(v * 16 ** i for i, v in enumerate(left))
                        * sum(v * 16 ** i for i, v in enumerate(right)))
            require(output == expected, "new multiplier output")
            require(all(after.memory[c] == 0 for c in plan.temporaries | scratch),
                    "new dirty cleanup")
            rows.append((digits, index, before.steps, after.steps))
    return rows


def rejection_checks(producer):
    plan = producer.build_multiplier(2, 2)
    result = refine(plan.program)
    pos = result.replacements[0]
    faults = []
    altered = plan.program.copy()
    altered[pos + 1] = ("sub", TEMP, VALUE, 21)
    faults.append(altered)
    altered = plan.program.copy()
    altered[pos + 2] = ("bltz", TEMP, pos + 5)
    faults.append(altered)
    altered = plan.program.copy()
    altered[0] = ("bltz", 1000, pos + 1)
    faults.append(altered)
    altered = plan.program.copy()
    altered[pos] = ("mul", VALUE, TEMP, altered[pos][3])
    faults.append(altered)
    altered = plan.program.copy()
    altered[-1] = ("bltz", TEMP, 0)
    faults.append(altered)
    caught = 0
    for program in faults:
        try:
            refine(program)
        except ValueError:
            caught += 1
    require(caught == len(faults), "structural fault rejection")
    return caught


def main():
    started = time.monotonic()
    producer, mask, scratch, run = load_producer()
    templates = template_checks(producer)
    local_count = local_checks(producer, mask, run)
    whole = whole_checks(producer, mask, scratch, run)
    rejected = rejection_checks(producer)
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    print(json.dumps({"status": "PASS_WORDRAM_UNIT_TWIDDLES",
                      "templates": templates, "local_values": local_count,
                      "whole_cases": len(whole), "whole_transcript_sha256": digest(whole),
                      "structural_rejections": rejected, "package_sha256": files,
                      "elapsed_seconds": round(time.monotonic() - started, 3)}, sort_keys=True))


if __name__ == "__main__":
    main()
