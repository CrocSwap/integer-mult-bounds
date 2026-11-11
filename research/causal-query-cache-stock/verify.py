"""Finite corroboration and literal instruction replay for the cache theorem."""

from copy import deepcopy
import hashlib
from itertools import product
import json
from pathlib import Path
import runpy

PACKAGE = Path(__file__).resolve().parent
ENGINE = runpy.run_path(str(PACKAGE / "compile.py"))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def row_add(left, right, factor, prime):
    return [(a + factor * b) % prime for a, b in zip(left, right)]


def operate(bank, operation, prime, capacity):
    need(type(operation) is list and operation, "instruction shape")
    kind, *args = operation
    sizes = {"clear": 1, "scale": 2, "swap": 2, "add": 3}
    need(kind in sizes and len(args) == sizes[kind], "instruction arity")
    indices = args[:2] if kind in ("swap", "add") else args[:1]
    need(all(type(i) is int and 0 <= i < capacity for i in indices), "slot index")
    target = args[0]
    if kind == "clear":
        bank[target] = [0] * len(bank[target])
    elif kind == "swap":
        bank[target], bank[args[1]] = bank[args[1]], bank[target]
    elif kind == "scale":
        need(type(args[1]) is int and 0 < args[1] < prime, "scale unit")
        bank[target] = [x * args[1] % prime for x in bank[target]]
    else:
        need(target != args[1], "ADD alias")
        need(type(args[2]) is int and 0 <= args[2] < prime, "ADD coefficient")
        bank[target] = row_add(bank[target], bank[args[1]], args[2], prime)


def replay(plan):
    prime, dimension, rows = ENGINE["validate"](plan["problem"])
    width = plan["cache_width"]
    need(type(width) is int and 0 <= width <= dimension, "cache width")
    capacity, columns = width + 1, dimension + width + 3
    bank = [[int(j == dimension + i) for j in range(columns)]
            for i in range(capacity + 2)]
    spectators = deepcopy(bank[capacity:])
    need(plan["bank_fields"] == capacity, "bank capacity")
    need(plan["initial_clear"] == list(range(capacity)), "entry scrub")
    for slot in plan["initial_clear"]:
        operate(bank, ["clear", slot], prime, capacity)
    need(len(plan["stages"]) == len(rows), "stage count")
    need(len(plan["cuts"]) == len(rows) + 1, "cut count")
    acquisitions, instructions = 0, capacity
    for index, (row, stage) in enumerate(zip(rows, plan["stages"])):
        need(type(stage["acquire"]) is bool, "acquisition flag")
        if stage["acquire"]:
            need(not any(bank[width]), "query port was not cleared")
            bank[width] = row[:] + [0] * (columns - dimension)
            acquisitions += 1
        for instruction in stage["prepare"] + stage["transition"]:
            operate(bank, instruction, prime, capacity)
            instructions += 1
        need(bank[width] == row + [0] * (columns - dimension), "wrong delivered answer")
        expected = plan["cuts"][index + 1]["basis"]
        need(len(expected) <= width, "cut overflows cache")
        desired = [v + [0] * (columns - dimension) for v in expected]
        desired += [[0] * columns for _ in range(width - len(expected))]
        need(bank[:width] == desired, "wrong retained cache")
        operate(bank, ["clear", width], prime, capacity)
        instructions += 1
    need(acquisitions == plan["queries"], "wrong acquisition total")
    need(all(not any(v) for v in bank[:capacity]), "exit cache not zero")
    need(bank[capacity:] == spectators, "dirty spectator changed")
    return instructions


def digits(code, prime, dimension):
    return [(code // prime ** j) % prime for j in range(dimension)]


def finite_spaces(prime, dimension):
    """Independent oracle: enumerate every subset and test additive closure."""
    order = prime ** dimension
    vectors = [digits(i, prime, dimension) for i in range(order)]
    addition = [[sum(((a[k] + b[k]) % prime) * prime ** k
                     for k in range(dimension)) for b in vectors] for a in vectors]
    spaces = []
    for mask in range(1, 1 << order, 2):
        elements = [i for i in range(order) if mask >> i & 1]
        if all(mask >> addition[a][b] & 1 for a in elements for b in elements):
            dimension_here = next(d for d in range(dimension + 1)
                                  if prime ** d == len(elements))
            spaces.append((mask, dimension_here))
    spans, options = {}, {}
    for mask, _ in spaces:
        for code in range(order):
            multiple, span = 0, 0
            for _ in range(prime):
                for a in range(order):
                    if mask >> a & 1:
                        span |= 1 << addition[a][multiple]
                multiple = addition[multiple][code]
            spans[mask, code] = span
        for limit in range(dimension + 1):
            options[mask, limit] = [sub for sub, d in spaces
                                    if d <= limit and sub & mask == sub]
    return spaces, spans, options


def oracle_width(codes, rank, dimension, spans, options):
    """Enumerate every linear cache state; minimize queries for each capacity."""
    for limit in range(dimension + 1):
        states = {1: 0}
        for code in codes:
            following = {}
            for mask, queries in states.items():
                cost = queries + int(not (mask >> code & 1))
                available = spans[mask, code]
                for subspace in options[available, limit]:
                    following[subspace] = min(following.get(subspace, len(codes) + 1), cost)
            states = following
        if min(states.values()) == rank:
            return limit
    raise ValueError("finite state oracle found no rank-minimal schedule")


def exhaustive_streams(prime, dimension, maximum, digest):
    spaces, spans, options = finite_spaces(prime, dimension)
    cases, instructions = 0, 0
    for length in range(maximum + 1):
        for codes in product(range(prime ** dimension), repeat=length):
            full = 1
            for code in codes:
                full = spans[full, code]
            rank = next(d for mask, d in spaces if mask == full)
            rows = [digits(code, prime, dimension) for code in codes]
            problem = {"prime": prime, "dimension": dimension, "rows": rows}
            plan = ENGINE["compile_stream"](problem)
            need(plan["queries"] == rank, "independent span rank disagrees")
            optimum = oracle_width(codes, rank, dimension, spans, options)
            need(plan["cache_width"] == optimum, "independent stock optimum disagrees")
            instructions += replay(plan)
            digest.update(json.dumps([prime, dimension, codes, rank, optimum],
                                     separators=(",", ":")).encode())
            cases += 1
    return {"prime": prime, "dimension": dimension, "maximum_length": maximum,
            "all_subspaces": len(spaces), "streams": cases, "instructions": instructions}


def matrix_checks():
    cases, instructions = 0, 0
    for prime, size in ((2, 2), (3, 2), (5, 2), (2, 3)):
        for flat in product(range(prime), repeat=size * size):
            target = [list(flat[i * size:(i + 1) * size]) for i in range(size)]
            bank = [[int(i == j) for j in range(size)] for i in range(size)]
            program = ENGINE["matrix_program"](target, prime)
            for operation in program:
                operate(bank, operation, prime, size)
            need(bank == target, "matrix instruction endpoint disagrees")
            cases += 1
            instructions += len(program)
    return {"matrices": cases, "instructions": instructions}


def family_checks():
    cases, instructions = 0, 0
    for prime in ENGINE["PRIMES"]:
        for dimension in range(1, 9):
            unit = [[int(i == j) for j in range(dimension)] for i in range(dimension)]
            rows = unit + [[1] * dimension]
            problem = {"prime": prime, "dimension": dimension, "rows": rows}
            saved = deepcopy(problem)
            plan = ENGINE["compile_stream"](problem)
            need(plan["queries"] == dimension and plan["cache_width"] == 1,
                 "running-sum family does not attain one cache field")
            need(problem == saved, "compiler changed input")
            instructions += replay(plan)
            cases += 1
    boundary_cases = 0
    for prime in ENGINE["PRIMES"]:
        unit = [[int(i == j) for j in range(8)] for i in range(8)]
        plan = ENGINE["compile_stream"]({"prime": prime, "dimension": 8, "rows": unit * 3})
        need(plan["queries"] == 8 and plan["cache_width"] == 8, "maximum bank boundary")
        instructions += replay(plan)
        boundary_cases += 1
    plan = ENGINE["compile_stream"]({"prime": 11, "dimension": 8, "rows": [[0] * 8] * 24})
    need(plan["queries"] == plan["cache_width"] == 0, "zero-request rank boundary")
    instructions += replay(plan)
    return {"sum_family_cases": cases, "boundary_cases": boundary_cases + 1,
            "instructions": instructions}


def reject(call, message):
    try:
        call()
    except (ValueError, KeyError, IndexError, TypeError):
        return 1
    raise ValueError("accepted control: " + message)


def controls():
    compile_stream = ENGINE["compile_stream"]
    valid = {"prime": 3, "dimension": 2, "rows": [[1, 0], [0, 1], [1, 1]]}
    bad_inputs = [None, {}, dict(valid, prime=True), dict(valid, prime=4),
                  dict(valid, dimension=0), dict(valid, dimension=9),
                  dict(valid, rows=[[1]]), dict(valid, rows=[[True, 0]]),
                  dict(valid, rows=[[3, 0]]), dict(valid, rows=[[1, 0]] * 25),
                  dict(valid, extra=0)]
    count = sum(reject(lambda item=item: compile_stream(item), "input boundary")
                for item in bad_inputs)
    plan = compile_stream(valid)
    replay(plan)
    mutants = []
    changed = deepcopy(plan)
    changed["stages"][0]["acquire"] = False
    mutants.append(changed)
    changed = deepcopy(plan)
    changed["initial_clear"] = []
    mutants.append(changed)
    changed = deepcopy(plan)
    changed["queries"] -= 1
    mutants.append(changed)
    changed = deepcopy(plan)
    changed["stages"][0]["transition"].append(["clear", changed["cache_width"]])
    mutants.append(changed)
    changed = deepcopy(plan)
    changed["stages"][0]["transition"].append(["clear", changed["bank_fields"]])
    mutants.append(changed)
    changed = deepcopy(plan)
    changed["cuts"][1]["basis"][0][0] = 0
    mutants.append(changed)
    count += sum(reject(lambda item=item: replay(item), "changed schedule") for item in mutants)
    bank = [[1, 0], [0, 1]]
    for instruction in (["add", 0, 0, 1], ["scale", 0, 0], ["clear", True], ["jump", 0]):
        count += reject(lambda op=instruction: operate(bank, op, 3, 2), "instruction boundary")
    return count


def main():
    digest = hashlib.sha256()
    domains = [exhaustive_streams(p, n, length, digest)
               for p, n, length in ((2, 2, 6), (2, 3, 4), (3, 2, 4))]
    result = {"status": "PASS_CAUSAL_QUERY_CACHE_STOCK", "domains": domains,
              "matrix_compiler": matrix_checks(), "family": family_checks(),
              "rejection_controls": controls(), "stream_digest": digest.hexdigest()}
    result["files"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in sorted(PACKAGE.iterdir()) if path.is_file()}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
