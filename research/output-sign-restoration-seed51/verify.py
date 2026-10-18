"""Independent affine replay, finite sign enumeration and package checks.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
Run with -I -O -B: checks deliberately do not rely on Python assert.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
from fractions import Fraction

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("sign_word", HERE / "word.py")
word = importlib.util.module_from_spec(spec)
spec.loader.exec_module(word)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def replay(program, state):
    state = list(state)
    for op in program:
        if op[0] == "add":
            _, dst, src, sign = op
            require(dst != src and sign in (-1, 1), "invalid ADD")
            state[dst] += sign * state[src]
        elif op[0] == "neg":
            state[op[1]] = -state[op[1]]
        else:
            raise ValueError("unknown instruction")
    return state


def matrix(tree, n, d):
    if "matrix" in tree:
        return tree["matrix"]
    result = [[0] * n for _ in range(d)]
    for child in tree["children"]:
        child_matrix = matrix(child, n, d)
        for i in range(d):
            for j in range(n):
                result[i][j] += child_matrix[i][j]
    return result


def expected(state, transform, n, d, reader=False, direction=1):
    result = list(state)
    for i in range(d):
        result[i] += (1 if reader else direction) * sum(transform[i][j] * state[d + j] for j in range(n))
    if reader:
        result[d:d+n] = [-x for x in state[d:d+n]]
    return result


def bill(program):
    adds = sum(op[0] == "add" for op in program)
    negs = len(program) - adds
    return {"ADD": adds, "NEG": negs, "instructions": len(program),
            "data_reads": 2 * adds + negs, "data_writes": adds + negs,
            "descriptor_fields": 4 * adds + 2 * negs}


def recurrence(tree, n, d, eager, reader):
    if "matrix" in tree:
        return sum(c != 0 for row in tree["matrix"] for c in row), n
    child_bills = [recurrence(child, n, d, eager, True) for child in tree["children"]]
    k = len(child_bills)
    boundary = k * n if eager else (k % 2) * n + 2 * (k // 2) * min(n, d)
    return 2 * sum(a for a, g in child_bills) + 2 * n, 2 * sum(g for a, g in child_bills) + 2 * boundary + (n if reader else 0)


def check_map(tree, n, d, eager=False, reader=False):
    program, registers = word.compile_word(tree, n, d, eager=eager, reader=reader)
    transform = matrix(tree, n, d)
    actual_bill = bill(program)
    require((actual_bill["ADD"], actual_bill["NEG"]) == recurrence(tree, n, d, eager, reader), "recursive bill mismatch")
    reverse = word.inverse(program)
    require(bill(reverse) == actual_bill, "inverse price mismatch")
    for j in range(registers):
        state = [int(i == j) for i in range(registers)]
        forward = replay(program, state)
        require(forward == expected(state, transform, n, d, reader), "basis map mismatch")
        require(replay(reverse, state) == expected(state, transform, n, d, reader, -1), "inverse basis mismatch")
        require(replay(reverse, forward) == state, "literal inverse failed")
    probe = [Fraction((-1)**i * (i+2), 2*i+1) for i in range(registers)]
    require(replay(program, probe) == expected(probe, transform, n, d, reader), "rational dirty probe failed")
    return program, registers, actual_bill


def enumerate_boundaries():
    # This replay knows no frame invariant or closed-form optimal schedule.
    schedules = 0
    prices = 0
    admitted = 0
    for k in range(1, 7):
        valid = []
        for gaps in itertools.product(range(4), repeat=k+1):
            schedules += 1
            wsign, out, a, b = 1, [1] + [0]*k, 0, 0
            for i, gate in enumerate(gaps):
                if gate & 1:
                    wsign = -wsign
                    a += 1
                if gate & 2:
                    out = [-v for v in out]
                    b += 1
                if i < k:
                    out[i+1] += wsign
                    wsign = -wsign
            if wsign == 1 and out == [1]*(k+1):
                valid.append((a, b))
        admitted += len(valid)
        for n in range(1, 9):
            for d in range(1, 9):
                prices += 1
                require(min(a*n + b*d for a, b in valid) == (k%2)*n + 2*(k//2)*min(n, d), "boundary minimum mismatch")
    return {"schedules": schedules, "admitted": admitted, "price_cases": prices}


def make_tree(rng, n, d, depth, k, dense=False):
    if depth == 0:
        alphabet = (-1, 1) if dense else (-1, 0, 1)
        return {"matrix": [[rng.choice(alphabet) for _ in range(n)] for _ in range(d)]}
    return {"children": [make_tree(rng, n, d, depth-1, k, dense) for _ in range(k)]}


def controls(tree, n, d, program, registers):
    transform = matrix(tree, n, d)
    def differs(bad):
        for j in range(registers):
            state = [int(i == j) for i in range(registers)]
            if replay(bad, state) != expected(state, transform, n, d):
                return True
        return False
    target_neg = next(i for i, op in enumerate(program) if op[0] == "neg" and op[1] < d)
    require(differs(program[:target_neg] + program[target_neg+1:]), "missing output sign accepted")
    source_copy = next(i for i, op in enumerate(program) if op[0] == "add" and op[1] >= d+n and d <= op[2] < d+n and op[3] == -1)
    require(differs(program[:source_copy] + program[source_copy+1:]), "missing source uncopy accepted")
    batch_end = source_copy - n
    require(all(op[0] == "neg" and op[1] >= d+n for op in program[batch_end:source_copy]), "workspace boundary not found")
    require(differs(program[:batch_end] + program[source_copy:]), "missing workspace restore accepted")
    require(differs(program[:source_copy+n]), "missing second pass accepted")
    # Unframed fixed readers alternate instead of adding, on a concrete input.
    w, out = 3, 7
    for _ in range(5):
        out += w
        w = -w
    w = -w
    require((out, w) != (22, 3), "unframed deferral control failed")
    # Oddness is enough for the batch, but the transparent echo needs additivity.
    require((3+2)**3 - 3**3 != 2**3, "nonlinear dirt control failed")
    # Between the second child and its output sign repair, D is noncanonical.
    w, out = 3, 7
    out += w; w = -w
    out = -out
    out += w; w = -w
    require(out != 7 + 2*3 and -out == 7 + 2*3, "prefix observer control failed")
    bad_inputs = [({}, n, d), ({"children": []}, n, d), ({"matrix": [[True]*n]}, n, d),
                  ({"matrix": [[2]*n]}, n, d), ({"matrix": [[1]*(n-1)]}, n, d),
                  (tree, True, d), (tree, n, 0)]
    for bad_tree, bad_n, bad_d in bad_inputs:
        try:
            word.compile_word(bad_tree, bad_n, bad_d, reader=True)
        except ValueError:
            continue
        raise ValueError("invalid input accepted")
    return {"mathematical": 7, "invalid_inputs": len(bad_inputs)}


def calculate():
    census = enumerate_boundaries()
    rng = random.Random(51)
    cases = columns = 0
    for n, d, k, depth in itertools.product(range(1, 5), range(1, 4), range(1, 5), range(1, 3)):
        tree = make_tree(rng, n, d, depth, k)
        for eager, reader in itertools.product((False, True), repeat=2):
            _, registers, _ = check_map(tree, n, d, eager, reader)
            cases += 1
            columns += registers
    tree = make_tree(random.Random(51), 8, 1, 1, 5, dense=True)
    program, registers, framed = check_map(tree, 8, 1)
    _, _, eager = check_map(tree, 8, 1, eager=True)
    deeper = []
    for depth in (2, 3):
        node = make_tree(random.Random(51+depth), 8, 1, depth, 5, dense=True)
        for old in (False, True):
            _, regs, count = check_map(node, 8, 1, eager=old, reader=True)
            deeper.append({"depth": depth, "eager": old, "registers": regs, **count})
    require(framed["ADD"] == 96 and framed["NEG"] == 104 and eager["NEG"] == 160, "selected invoice changed")
    return {"schema": 1, "seed": 51, "status": "finite recursive interface; no new kappa",
            "boundary_enumeration": census, "recursive_cases": cases, "basis_columns": columns,
            "selected": {"children": 5, "workspace_width": 8, "output_width": 1,
                         "registers": registers, "tree": tree, "matrix": matrix(tree, 8, 1),
                         "framed": framed, "eager": eager, "NEG_saved": 56,
                         "word_sha256": hashlib.sha256(json.dumps(program, separators=(",", ":")).encode()).hexdigest()},
            "deeper_readers": deeper, "controls": controls(tree, 8, 1, program, registers)}


def verify_pins():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
    required = {f"sources/PR{pr}-README.md" for pr in (1155, 1203, 1205)}
    require(len(pins["retained_sources"]) == 3 and
            {pin["local_path"] for pin in pins["retained_sources"]} == required,
            "source pin set mismatch")
    for pin in pins["retained_sources"]:
        data = (HERE / pin["local_path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin["sha256"], "source SHA256 mismatch: " + pin["local_path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == pin["git_blob"], "source Git blob mismatch")
    return len(pins["retained_sources"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true", help="print the recomputed certificate")
    args = parser.parse_args()
    pins = verify_pins()
    result = calculate()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(result == json.loads((HERE / "CERTIFICATE.json").read_text()), "certificate mismatch")
        print(f"PASS_OUTPUT_SIGN_RESTORATION schedules={result['boundary_enumeration']['schedules']} recursive_cases={result['recursive_cases']} saved_NEG=56 source_pins={pins} kappa=unchanged")


if __name__ == "__main__":
    main()
