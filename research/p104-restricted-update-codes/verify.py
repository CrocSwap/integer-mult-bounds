"""Exact restricted-coordinate P104 defect code census. Apache-2.0.

Ross Richardson, with substantial OpenAI Codex assistance.
The pinned floor word and translation lattice remain predecessor work.
"""

from collections import Counter
from fractions import Fraction
import hashlib
import types
import json
from math import gcd
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def authenticate():
    metadata = json.loads((ROOT / "PREDECESSOR.json").read_text())
    need(metadata["head"] == "0b8b44c6cc367725a8737f8b3cd997f42d3bd0d9", "predecessor head")
    for row in metadata["files"]:
        path = ROOT / row["local"]
        need(path.resolve().is_relative_to(ROOT) and not path.is_symlink(), "source path")
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "predecessor bytes")
        need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
             == row["git_blob"], "predecessor blob")
    path = ROOT / "source/model.py"
    source = types.ModuleType("pinned_p104_word")
    source.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), source.__dict__)
    return source


def inverse(matrix):
    size = len(matrix)
    a = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(size)]
         for i, row in enumerate(matrix)]
    for j in range(size):
        pivot = next(i for i in range(j, size) if a[i][j])
        a[j], a[pivot] = a[pivot], a[j]
        factor = a[j][j]
        a[j] = [x / factor for x in a[j]]
        for i in range(size):
            if i != j:
                factor = a[i][j]
                a[i] = [x - factor * y for x, y in zip(a[i], a[j], strict=True)]
    return [row[size:] for row in a]


def labels(values):
    registry = {}
    return [registry.setdefault(value, len(registry)) for value in values]


def quotient(source, rank):
    basis, generators, stage_bits = source.transversal(rank)
    dimension = source.shape(rank)
    period = 1 << (rank // 2 + 1)
    inv = inverse(basis)
    scaled = [[period * x for x in row] for row in inv]
    need(all(x.denominator == 1 for row in scaled for x in row), "scalar period containment")
    scaled = [[int(x) for x in row] for row in scaled]
    for i in range(dimension):
        for j in range(dimension):
            need(sum(scaled[i][k] * basis[k][j] for k in range(dimension))
                 == period * (i == j), "exact lattice inverse")
    def key(x):
        return tuple(sum(a * b for a, b in zip(row, x, strict=True)) % period
                     for row in scaled)
    representatives = list(source.representatives(generators, dimension))
    keys = [key(x) for x in representatives]
    index = {x: i for i, x in enumerate(keys)}
    need(len(index) == 1 << sum(stage_bits), "complete distinct transversal")
    transition = []
    for j in range(dimension):
        delta = tuple(row[j] % period for row in scaled)
        permutation = [index[tuple((a + b) % period for a, b in zip(k, delta, strict=True))]
                       for k in keys]
        need(len(set(permutation)) == len(keys), "coordinate action is permutation")
        transition.append(permutation)
    defects = [source.defect(x, rank) for x in representatives]
    return representatives, defects, transition, period, stage_bits


def restricted(base, permutation, period, step):
    size = len(base)
    order = period // gcd(period, step)
    update = list(range(size))
    for _ in range(step % period):
        update = [permutation[i] for i in update]
    signatures = [[] for _ in base]
    current = list(range(size))
    for _ in range(order):
        for i in range(size):
            signatures[i].append(base[current[i]])
        current = [update[i] for i in current]
    need(current == list(range(size)), "declared cyclic period")
    code = labels(tuple(x) for x in signatures)
    code_update = {}
    for i, nxt in enumerate(update):
        old, new = code[i], code[nxt]
        need(old not in code_update or code_update[old] == new, "code update well-defined")
        code_update[old] = new
    need(len(set(code_update.values())) == len(code_update), "code update reversible")
    fibers = Counter(code)
    return {"states": len(fibers), "fixed_bits": (len(fibers) - 1).bit_length(),
            "fiber_histogram": {str(k): v for k, v in sorted(Counter(fibers.values()).items())},
            "signature_sha256": hashlib.sha256(canonical(signatures)).hexdigest(),
            "code_update_sha256": hashlib.sha256(canonical(sorted(code_update.items()))).hexdigest()}, code


def full_refinement(base, transitions):
    code = list(base)
    rounds = 0
    while True:
        new = labels((code[i], *(code[p[i]] for p in transitions)) for i in range(len(code)))
        rounds += 1
        if len(set(new)) == len(set(code)):
            return len(set(new)), rounds
        code = new
        need(rounds <= 20, "bounded full refinement")


def result():
    source = authenticate()
    rows = []
    for rank in (1, 2, 3):
        reps, defects, transitions, period, stage_bits = quotient(source, rank)
        base = labels(defects)
        coordinates = []
        for j, transition in enumerate(transitions):
            steps = []
            for step in (1, 2, 4):
                row, code = restricted(base, transition, period, step)
                row["step"] = step
                # Direct floor evaluation checks the quotient action, not just its group law.
                for i, x in enumerate(reps):
                    if step == 1 or (i % 257 == 0):
                        y = list(x)
                        y[j] += step
                        index = i
                        for _ in range(step % period):
                            index = transition[index]
                        need(source.defect(y, rank) == defects[index], "translated literal word")
                steps.append(row)
            coordinates.append({"coordinate": j, "steps": steps})
        all_states, rounds = full_refinement(base, transitions)
        need(all_states == len(reps), "all-translation control separates every coset")
        rows.append({"rank": rank, "dimension": source.shape(rank), "scalar_period": period,
                     "stage_index_bits": stage_bits, "cosets": len(reps),
                     "immutable_states": len(set(base)), "immutable_fixed_bits": (len(set(base))-1).bit_length(),
                     "all_coordinate_states": all_states, "full_refinement_rounds": rounds,
                     "coordinates": coordinates})
    return {"status": "PASS_P104_RESTRICTED_UPDATE_CODES_NO_NEW_KAPPA", "censuses": rows,
            "scope": "Complete rank1..3 period transversals, every real coordinate, integer update steps1,2,4; general minimal-code theorem is written, not formal-kernel checked. No rank7 census or paid supplier."}


def typed_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(typed_equal(x,y) for x,y in zip(a,b,strict=True))
    return a == b


def main():
    actual = result()
    if sys.argv[1:] == ["--write"]:
        with (ROOT / "RESULT.json").open("x") as output:
            json.dump(actual, output, indent=2)
            output.write("\n")
    else:
        need(not sys.argv[1:], "unexpected arguments")
        need(typed_equal(actual, json.loads((ROOT / "RESULT.json").read_text())), "typed receipt mismatch")
    for row in actual["censuses"]:
        print("rank",row["rank"],"states by coordinate0",[z["states"] for z in row["coordinates"][0]["steps"]])
    print(actual["status"])


if __name__ == "__main__":
    main()
