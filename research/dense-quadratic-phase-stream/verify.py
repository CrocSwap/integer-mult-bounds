"""Finite exact checks, with a direct-polynomial oracle and generated hashes."""

import hashlib
import itertools
import json
from pathlib import Path

from stream import MAX_BITS, Meter, phase_stream


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def polynomial(code: int, linear: tuple[int, ...],
               cross: tuple[tuple[int, ...], ...], constant: int) -> int:
    bits = tuple((code >> i) & 1 for i in range(len(linear)))
    result = constant + sum(a * x for a, x in zip(linear, bits))
    for j, row in enumerate(cross):
        result += sum(a * bits[i] * bits[j] for i, a in enumerate(row))
    return result % 4


def unpack(n: int, coefficients: tuple[int, ...]) -> tuple:
    constant = coefficients[0]
    linear = coefficients[1:n + 1]
    cross = []
    position = n + 1
    for j in range(n):
        cross.append(coefficients[position:position + j])
        position += j
    check(position == len(coefficients), "coefficient cursor")
    return linear, tuple(cross), constant


def one_case(linear: tuple, cross: tuple, constant: int, digest) -> tuple[int, int]:
    meter = Meter()
    original = (linear, cross, constant)
    count = 0
    for code, phase in enumerate(phase_stream(linear, cross, constant, meter)):
        check(phase == polynomial(code, linear, cross, constant), "direct polynomial")
        digest.update(bytes((phase,)))
        count += 1
    check(meter.restored and original == (linear, cross, constant), "return contract")
    check(meter.events == 4 * count - 3, "event census")
    return count, meter.updates


def exhaustive(digest) -> dict:
    cases = outputs = updates = 0
    for n in range(4):
        size = 1 + n + n * (n - 1) // 2
        for coefficients in itertools.product(range(4), repeat=size):
            count, work = one_case(*unpack(n, coefficients), digest)
            cases += 1
            outputs += count
            updates += work
    return {"cases": cases, "outputs": outputs, "updates": updates}


def dense_cases(digest) -> dict:
    cases = outputs = updates = 0
    for n in range(4, 13):
        size = 1 + n + n * (n - 1) // 2
        for seed in range(8):
            coefficients = tuple((i * i + seed * i + seed + i // 3) % 4
                                 for i in range(size))
            count, work = one_case(*unpack(n, coefficients), digest)
            cases += 1
            outputs += count
            updates += work
    return {"cases": cases, "outputs": outputs, "updates": updates}


def reject(args: tuple, label: str) -> None:
    try:
        list(phase_stream(*args))
    except ValueError:
        return
    raise RuntimeError("accepted invalid " + label)


def domain_controls() -> int:
    used_meter = Meter()
    used_meter.outputs = 1
    invalid = [
        ((1,), (), 0, Meter()),
        ((1,), ((0,),), 0, Meter()),
        ((True,), ((),), 0, Meter()),
        ((1,), ((),), 4, Meter()),
        ((1,), ((),), True, Meter()),
        ([1], ((),), 0, Meter()),
        ((0,) * (MAX_BITS + 1), ((),) * (MAX_BITS + 1), 0, Meter()),
        ((1,), ((),), 0, used_meter),
        ((1, 2), ((), (4,)), 0, Meter()),
    ]
    for index, args in enumerate(invalid):
        reject(args, str(index))
    return len(invalid)


def semantic_controls() -> int:
    linear, cross, constant = (1, 2, 3), ((), (1,), (3, 2)), 3
    correct = tuple(polynomial(x, linear, cross, constant) for x in range(8))
    alternatives = [
        tuple(polynomial(x, linear, cross, 0) for x in range(8)),
        tuple(polynomial(x, (0, 0, 0), cross, constant) for x in range(8)),
        tuple(polynomial(x, linear, ((), (0,), (0, 0)), constant) for x in range(8)),
        tuple(polynomial(x, linear, cross, constant) % 2 for x in range(8)),
        tuple(polynomial(7 - x, linear, cross, constant) for x in range(8)),
    ]
    for candidate in alternatives:
        check(candidate != correct, "semantic control did not discriminate")
    meter = Meter()
    partial = phase_stream(linear, cross, constant, meter)
    for _ in range(8):
        next(partial)
    check(not meter.restored, "last yield is not completed exhaustion")
    check(next(partial, None) is None and meter.restored, "final cleanup")
    partial.close()
    return len(alternatives) + 1


def capacity_case() -> dict:
    linear = (0,) * MAX_BITS
    cross = tuple((0,) * j for j in range(MAX_BITS))
    meter = Meter()
    count = 0
    for phase in phase_stream(linear, cross, 0, meter):
        check(phase == 0, "capacity zero polynomial")
        count += 1
    check(count == 1 << MAX_BITS and meter.restored, "capacity return")
    return {"bits": MAX_BITS, "outputs": count, "updates": meter.updates,
            "events": meter.events, "max_stack": meter.max_stack}


def source_bindings(package: Path) -> int:
    manifest = package / "SOURCES.json"
    check(manifest.stat().st_size <= 1024 * 1024, "manifest size")
    rows = json.loads(manifest.read_text())["files"]
    check(len(rows) <= 16, "source count")
    count = 0
    root = package.parents[1]
    for row in rows:
        if row["usage"] != "input":
            continue
        source = root / row["path"]
        check(source.stat().st_size <= 1024 * 1024, "source size")
        check(hashlib.sha256(source.read_bytes()).hexdigest() == row["sha256"],
              "source binding " + row["path"])
        count += 1
    return count


def main() -> None:
    package = Path(__file__).resolve().parent
    digest = hashlib.sha256()
    report = {"exhaustive": exhaustive(digest), "dense": dense_cases(digest),
              "domain_controls": domain_controls(),
              "semantic_controls": semantic_controls(), "capacity": capacity_case(),
              "source_bindings": source_bindings(package)}
    report["phase_sha256"] = digest.hexdigest()
    names = ("README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json",
             "stream.py", "verify.py")
    report["files"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                       for name in names}
    print("PASS_DENSE_QUADRATIC_PHASE_STREAM " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
