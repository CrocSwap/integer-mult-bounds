#!/usr/bin/env python3
"""Independent verifier: imports neither the generator nor predecessor code."""
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def freeze(matrix):
    return tuple(tuple(row) for row in matrix)


def inputs(n):
    return [{(i, ()): 1} for i in range(n)]


def shear(state, operator, source, target, sign):
    require(type(source) is int and type(target) is int and source != target
            and type(sign) is int and sign in (-1, 1), "invalid primitive ports/sign")
    for (origin, monomial), coefficient in list(state[source].items()):
        key = (origin, (operator,) + monomial)
        value = state[target].get(key, 0) + sign * coefficient
        if value:
            state[target][key] = value
        else:
            state[target].pop(key, None)


def query_replay(word, state=None):
    state = inputs(7) if state is None else [dict(row) for row in state]
    for kind, j, sign in word:
        require(kind in ("A", "B") and type(j) is int and 0 <= j < 3,
                "invalid query")
        source, target = (j, 6) if kind == "B" else (6, j + 3)
        shear(state, kind + str(j), source, target, sign)
    return state


def reversed_word(word):
    return [tuple(op[:-1]) + (-op[-1],) for op in reversed(word)]


def wanted(rows, factors=None):
    state = inputs(7 if factors is None else 10)
    for i, row in enumerate(rows):
        for j, coefficient in enumerate(row):
            if coefficient:
                operators = ("A" + str(i), "B" + str(j)) if factors is None else (
                    tuple(reversed(factors[i + 3])) + tuple(reversed(factors[j])))
                state[i + 3][(j, operators)] = coefficient
    return state


def check_word(rows, word, optimum=None):
    actual = query_replay(word)
    require(actual == wanted(rows), "wrong complete free-operator map")
    require(query_replay(reversed_word(word), actual) == inputs(7),
            "wrong inverse")
    if optimum is not None:
        require(len(word) == optimum, "nonminimum query count")


def bound(rows):
    return 2 * (sum(any(row) for row in rows)
                + sum(any(rows[i][j] for i in range(3)) for j in range(3)))


def enumerate_paths():
    # Independent signed-move DFS, not multiset permutations or the generator.
    completed = []

    def visit(counts, first, q, states, moves):
        if sum(counts) == 6:
            require(q == (0, 0, 0), "source path did not close")
            differences = {}
            for a in range(7):
                for b in range(7):
                    delta = tuple(states[b][j] - states[a][j] for j in range(3))
                    differences.setdefault(delta, (a, b))
            completed.append((tuple(moves), differences))
            return
        for j in range(3):
            if counts[j] == 2:
                continue
            signs = (-1, 1) if counts[j] == 0 else (-first[j],)
            for sign in signs:
                c, f = list(counts), list(first)
                if c[j] == 0:
                    f[j] = sign
                c[j] += 1
                r = tuple(q[k] + (sign if k == j else 0) for k in range(3))
                visit(c, f, r, states + [r], moves + [(j, sign)])

    visit([0]*3, [0]*3, (0, 0, 0), [(0, 0, 0)], [])
    require(len(completed) == len({p[0] for p in completed}) == 720,
            "incomplete source paths")
    return completed


def path_word(rows, moves, pairs):
    reads = [[] for _ in range(7)]
    for i, row in enumerate(rows):
        if any(row):
            start, end = pairs[row]
            reads[start].append(("A", i, -1))
            reads[end].append(("A", i, 1))
    active = {j for j in range(3) if any(rows[i][j] for i in range(3))}
    result = []
    for k in range(7):
        result.extend(reads[k])
        if k < 6 and moves[k][0] in active:
            j, sign = moves[k]
            result.append(("B", j, sign))
    return result


def transformed_family(rows, word):
    result = {}
    for rp in itertools.permutations(range(3)):
        for cp in itertools.permutations(range(3)):
            for signs in itertools.product((-1, 1), repeat=6):
                matrix = tuple(tuple(rows[rp[i]][cp[j]] * signs[i] * signs[3+j]
                                     for j in range(3)) for i in range(3))
                if matrix not in result:
                    out = []
                    for kind, j, sign in word:
                        perm, offset = (rp, 0) if kind == "A" else (cp, 3)
                        new = perm.index(j)
                        out.append((kind, new, sign * signs[offset+new]))
                    result[matrix] = out
    return result


def expand_queries(word, factors):
    # Explicit work stack with sign-dependent inverse order, not generated code.
    result = []
    for kind, j, sign in word:
        source, target = (j, 6) if kind == "B" else (6, j+3)
        tasks = [(tuple(factors[j if kind == "B" else j+3]), source, target,
                  (7, 8, 9), sign)]
        while tasks:
            fs, source, target, pool, direction = tasks.pop()
            if len(fs) == 1:
                result.append((fs[0], source, target, direction))
                continue
            require(bool(pool), "unpaid recursive connector")
            w, rest = pool[0], pool[1:]
            m = len(fs)//2
            a = (fs[:m], source, w, rest)
            b = (fs[m:], w, target, rest)
            calls = [a+(1,), b+(1,), a+(-1,), b+(-1,)]
            if direction == -1:
                calls = [c[:-1]+(-c[-1],) for c in reversed(calls)]
            tasks.extend(reversed(calls))
    return result


def leaf_replay(word, factors):
    state = inputs(10)
    for factor, source, target, sign in word:
        require(type(factor) is int and 0 <= factor < 27, "unknown factor")
        require(0 <= source < 10 and 0 <= target < 10, "unpriced role")
        shear(state, factor, source, target, sign)
    require(state == wanted(((1, 1, 1), (1, 1, -1), (1, -1, 0)), factors),
            "wrong lowered product/restoration")
    for factor, source, target, sign in reversed_word(word):
        shear(state, factor, source, target, sign)
    require(state == inputs(10), "wrong lowered inverse")


def dense_checks(rows, word):
    rng = random.Random(53)
    cases = 0
    for size in (1, 2, 3):
        for modulus in (None, 3, 5):
            matrices = [[[rng.randrange(-2, 3) for _ in range(size)]
                         for _ in range(size)] for _ in range(6)]
            def matvec(m, v):
                return [sum(a*b for a, b in zip(row, v)) for row in m]
            def norm(v):
                return [x if modulus is None else x % modulus for x in v]
            def execute(program, data):
                data = [list(v) for v in data]
                for kind, j, sign in program:
                    s, t, f = (j, 6, j) if kind == "B" else (6, j+3, j+3)
                    value = matvec(matrices[f], data[s])
                    data[t] = norm([a + sign*b for a, b in zip(data[t], value)])
                return data
            fixtures = []
            for column in range(7*size):
                data = [[0]*size for _ in range(7)]
                data[column//size][column % size] = 1
                fixtures.append(data)
            for _ in range(4):
                fixtures.append([[rng.randrange(-5, 6) for _ in range(size)]
                                 for _ in range(7)])
            if modulus is None:
                fixtures.append([[Fraction(rng.randrange(-5, 6), 3)
                                  for _ in range(size)] for _ in range(7)])
            for initial in fixtures:
                initial = [norm(v) for v in initial]
                target = [list(v) for v in initial]
                for i, row in enumerate(rows):
                    for j, coefficient in enumerate(row):
                        v = matvec(matrices[3+i], matvec(matrices[j], initial[j]))
                        target[3+i] = [a+coefficient*b for a, b in zip(target[3+i], v)]
                target = [norm(v) for v in target]
                actual = execute(word, initial)
                require(actual == target, "dense target mismatch")
                require(execute(reversed_word(word), actual) == initial,
                        "dense inverse mismatch")
                cases += 1
    return cases


def rejects(action):
    try:
        action()
    except (ValueError, KeyError, IndexError):
        return
    raise ValueError("negative control was accepted")


def source_checks():
    sources = json.loads((ROOT / "SOURCES.json").read_text())
    for entry in sources["retained_files"]:
        content = (ROOT / entry["local"]).read_bytes()
        require(hashlib.sha256(content).hexdigest() == entry["sha256"],
                "retained source SHA256 mismatch")
        git_blob = b"blob " + str(len(content)).encode() + b"\0" + content
        require(hashlib.sha1(git_blob).hexdigest() == entry["git_blob"],
                "retained Git blob mismatch")
    return len(sources["retained_files"])


def dense_invoice(program, size):
    travel = formula = 0
    for factor, source, target, _ in program:
        head = 0
        previous = 0
        offset = 10*size + factor*size*size
        for i in range(size):
            first = offset + i*size
            formula += (first-previous + (2*size-1)*(first-source*size)
                        + size-1 + abs(source*size+size-1-(target*size+i)))
            for j in range(size):
                for cell in (offset+i*size+j, source*size+j):
                    travel += abs(cell-head)
                    head = cell
            cell = target*size+i
            travel += abs(cell-head)
            head = cell
            previous = cell
        travel += head
        formula += target*size+size-1
    require(travel == formula, "dense tape trace/formula disagree")
    calls = len(program)
    return {
        "leaf_calls": calls, "row_length": size,
        "coefficient_reads": calls*size*size, "source_reads": calls*size*size,
        "target_reads": calls*size, "target_writes": calls*size,
        "scalar_multiplications": calls*size*size,
        "scalar_additions": calls*size*(size+1),
        "scalar_negations": sum(op[-1] == -1 for op in program)*size,
        "accumulator_resets": calls*size, "head_word_moves": travel,
        "mutable_words": 10*size, "coefficient_words": 27*size*size,
        "initial_value_validation_reads": 10*size+27*size*size,
        "instruction_records": calls, "instruction_payload_bits": 14*calls,
    }


def verify():
    c = json.loads((ROOT / "CERTIFICATE.json").read_text())
    require(c["format"] == "signed-connector-obstruction-v1" and c["seed"] == 53,
            "certificate identity mismatch")
    require(c["shape"] == [3, 3] and c["coefficient_domain"] == [-1, 0, 1],
            "changed finite domain")
    require(c["base"] == "91a2094f2e022930069e8cfdc810a3ea1b81cd09", "base drift")
    canonical = c["canonical"]
    rep = freeze(canonical["matrix"])
    require(rep == ((1, 1, 1), (1, 1, -1), (1, -1, 0)), "wrong representative")
    require(canonical["support_lower_bound"] == 12 and canonical["minimum_queries"] == 14,
            "wrong minimum")
    check_word(rep, canonical["word"], 14)
    paths = enumerate_paths()
    directions = set()
    for v in itertools.product((-1, 0, 1), repeat=3):
        if any(v):
            directions.add(tuple(x * next(y for y in v if y) for x in v))
    directions = sorted(directions)
    require(c["directions"] == [list(v) for v in directions], "direction table drift")
    masks = set()
    records = []
    for moves, pairs in paths:
        mask = sum(1 << k for k, v in enumerate(directions) if v in pairs)
        masks.add(mask)
        first = [next(s for j, s in moves if j == k) for k in range(3)]
        records.append({"order": [j for j, _ in moves], "first_signs": first, "mask": mask})
    records.sort(key=lambda r: (r["order"], r["first_signs"]))
    payload = json.dumps(records, separators=(",", ":"), sort_keys=True).encode()
    require(hashlib.sha256(payload).hexdigest() == c["path_sha256"], "path digest drift")
    require(c["closed_source_paths"] == len(paths) and c["distinct_path_masks"] == sorted(masks),
            "coverage masks differ")
    family = transformed_family(rep, canonical["word"])
    missing, attained, unsigned, classifications = [], 0, 0, []
    # Cache equal requested direction sets, but replay every complete matrix word.
    choices = {}
    for flat in itertools.product((-1, 0, 1), repeat=9):
        rows = tuple(tuple(flat[3*i:3*i+3]) for i in range(3))
        wanted_rows = frozenset(rows) - {(0, 0, 0)}
        if wanted_rows not in choices:
            choices[wanted_rows] = next((p for p in paths if wanted_rows <= p[1].keys()), None)
        choice = choices[wanted_rows]
        if choice is None:
            missing.append(rows)
            require(rows in family and bound(rows) == 12, "unclassified obstruction")
            word, minimum = family[rows], 14
        else:
            word = path_word(rows, *choice)
            minimum = bound(rows)
            attained += 1
            unsigned += all(x >= 0 for x in flat)
        check_word(rows, word, minimum)
        classifications.append(minimum)
    require(len(missing) == len(family) == 288 and set(missing) == set(family),
            "orbit is not exactly the missing domain")
    require(missing == [freeze(m) for m in c["obstructed_patterns"]], "missing-pattern drift")
    require(attained == c["support_bound_attained"] == 19395, "attainment count drift")
    require(unsigned == c["unsigned_patterns_attained"] == 512, "unsigned coverage drift")
    fixture = c["seed_fixture"]
    require(fixture["index"] == 53 and freeze(fixture["matrix"]) == missing[53], "seed fixture drift")
    check_word(missing[53], fixture["word"], 14)
    recursive = c["recursive"]
    factors = recursive["factors"]
    require(recursive["factor_lengths"] == list(range(2, 8)), "changed factors")
    require([len(fs) for fs in factors] == list(range(2, 8))
            and sum(factors, []) == list(range(27)), "bad factor partition")
    require(recursive["live_roles"] == 10 and recursive["dirty_arrays"] == 4,
            "unpaid data/workspace")
    require([list(op) for op in expand_queries(canonical["word"], factors)] == recursive["word"],
            "lowered instruction mismatch")
    require(len(recursive["word"]) == recursive["leaf_calls"] == 308, "unpaid leaf")
    leaf_replay(recursive["word"], factors)
    lowered_programs = {"signed_walk": recursive["word"]}
    for name, expected in (("row", 388), ("column", 676)):
        program = recursive[name+"_star_word"]
        check_word(rep, program, 22)
        leaves = expand_queries(program, factors)
        require(len(leaves) == recursive[name+"_star_leaves"] == expected, "star price mismatch")
        leaf_replay(leaves, factors)
        lowered_programs[name+"_stars"] = leaves
    prices = [len(expand_queries([("B" if i < 3 else "A", i % 3, 1)], factors))
              for i in range(6)]
    require(prices == [4, 10, 16, 28, 40, 52] and 2*sum(prices)+2*min(prices) == 308,
            "weighted support/parity bound mismatch")
    dense = dense_checks(rep, canonical["word"]) + dense_checks(missing[53], fixture["word"])
    controls = 0
    word = [list(op) for op in canonical["word"]]
    for index in range(len(word)):
        rejects(lambda index=index: check_word(rep, word[:index]+word[index+1:]))
        controls += 1
    altered = [op[:] for op in word]; altered[0][-1] *= -1
    rejects(lambda: check_word(rep, altered)); controls += 1
    rejects(lambda: check_word(rep, word, 12)); controls += 1
    rejects(lambda: check_word(rep, word + [("B", 0, 1), ("B", 0, -1)], 14)); controls += 1
    require(query_replay(word + [("B", 0, 1), ("B", 0, -1)]) == wanted(rep),
            "valid nonoptimal control is not valid")
    # An unsigned version is not a signed integer identity; XOR would hide this.
    rejects(lambda: check_word(rep, [(k, j, 1) for k, j, _ in word])); controls += 1
    wrong = [list(op) for op in recursive["word"]]; wrong[0][0] = 26
    rejects(lambda: leaf_replay(wrong, factors)); controls += 1
    rejects(lambda: shear(inputs(2), "F", 0, 0, 1)); controls += 1
    # Nonlinear readouts restore the connector but can depend on its initial dirt.
    def nonlinear(dirt):
        values = [1, 2, 3, 0, 0, 0, dirt]
        for kind, j, sign in word:
            if kind == "B":
                values[6] += sign * values[j]
            else:
                values[3+j] += sign * values[6]**2
        require(values[:3] == [1, 2, 3] and values[6] == dirt, "nonlinear restore failed")
        return values[3:6]
    require(nonlinear(5) != nonlinear(6), "nonlinear boundary control failed"); controls += 1
    # Changing an immutable source between matching calls corrupts restoration.
    changed = inputs(7)
    for index, (kind, j, sign) in enumerate(word):
        if index == 2:
            changed[0][(0, ())] += 1
        source, target = (j, 6) if kind == "B" else (6, 3+j)
        shear(changed, kind+str(j), source, target, sign)
    require(changed[6] != inputs(7)[6], "source mutation control failed"); controls += 1
    invoices = {name: dense_invoice(program, 3) for name, program in lowered_programs.items()}
    for program in lowered_programs.values():
        for size in (1, 2, 4, 5):
            dense_invoice(program, size)
    return {
        "status": "PASS_SIGNED_CONNECTOR_OBSTRUCTION", "source_paths": 720,
        "matrices": len(classifications), "support_attained": attained,
        "obstructed_minimum_14": len(missing), "unsigned_attained": unsigned,
        "dense_cases": dense, "mathematical_controls": controls,
        "classification_sha256": hashlib.sha256(bytes(classifications)).hexdigest(),
        "leaf_comparison": {"row_stars": 388, "column_stars": 676, "signed_walk": 308},
        "dirty_arrays": 4, "source_files": source_checks(),
        "dense_tape_invoices": invoices, "tape_formula_comparisons": 15,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-summary", action="store_true")
    args = parser.parse_args()
    summary = verify()
    expected = ROOT / "EXPECTED.json"
    if args.write_summary:
        expected.write_text(json.dumps(summary, indent=2) + "\n")
    else:
        require(summary == json.loads(expected.read_text()), "expected receipt differs")
    print(json.dumps(summary, sort_keys=True))
