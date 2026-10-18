#!/usr/bin/env python3
"""Exact paired-call root-code criterion and eight-source exclusion.

Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported. All failures survive python -O.
"""
import argparse
from collections import Counter
from itertools import combinations, permutations
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(basis):
    values = [0]
    for row in basis:
        values += [value ^ row for value in values]
    return tuple(sorted(values))


def quotient_spaces(n, dimension):
    """Independent of the native RREF engine: extend and deduplicate full spans."""
    spaces = {(0,)}
    for _ in range(dimension):
        spaces = {
            tuple(sorted(space + tuple(value ^ vector for value in space)))
            for space in spaces for vector in range(1, 1 << n) if vector not in space
        }
    return sorted(spaces)


def root_codes(n, r):
    full = (1 << n) - 1
    # H intersect {h: h[0]=0} has dimension r-1, with unique complement <full>.
    return sorted(tuple(sorted([value << 1 for value in space] +
                               [(value << 1) ^ full for value in space]))
                  for space in quotient_spaces(n - 1, r - 1))


def prefix_points(word):
    points = [0]
    for label in word:
        points.append(points[-1] ^ (1 << label))
    return points


def differences(word):
    points = prefix_points(word)
    return {a ^ b for a in points for b in points}


def mandatory(code, n):
    """A mask absent from every proper reader support must itself be a difference."""
    full = (1 << n) - 1
    return {m for m in range(1, full + 1)
            if not any(h != full and h & m == m for h in code)}


def available(word, code):
    return {d & h for d in differences(word) for h in code}


def census(n, r):
    codes = root_codes(n, r)
    masks = [mandatory(code, n) for code in codes]
    required = [sum(1 << m for m in values) for values in masks]
    difference_hist = Counter()
    survivors = 0
    for order in permutations(range(n)):
        d = differences(tuple(range(n)) + order)
        difference_hist[len(d)] += 1
        bits = sum(1 << m for m in d)
        survivors += sum(1 for mask in required if bits & mask == mask)
    words = sum(difference_hist.values())
    summary = {
        "n": n, "roots": r, "source_orders": words, "codes": len(codes),
        "cases": words * len(codes), "mandatory_survivors": survivors,
        "max_difference_size": max(difference_hist),
        "difference_histogram": dict(sorted(difference_hist.items())),
        "mandatory_size_histogram": dict(sorted(Counter(map(len, masks)).items())),
    }
    # JSON object keys are strings in both the native and committed receipts.
    return json.loads(json.dumps(summary)), codes


def pair_words(n):
    """Small control only: enumerate position matchings, then label the pairs."""
    def walk(left, pairs):
        if not left:
            word = [0] * (2 * n)
            for label, (a, b) in enumerate(pairs):
                word[a] = word[b] = label
            yield tuple(word)
            return
        a = left[0]
        for b in left[1:]:
            yield from walk(tuple(x for x in left[1:] if x != b), pairs + ((a, b),))
    yield from walk(tuple(range(2 * n)), ())


def rotate_to_permutation(word, n):
    for cut in range(2 * n):
        rotated = word[cut:] + word[:cut]
        if len(set(rotated[:n])) != n:
            continue
        rename = {label: i for i, label in enumerate(rotated[:n])}
        return tuple(rename[label] for label in rotated), rename
    return None


def normalization_controls():
    checked = admitted = 0
    for n in range(1, 6):
        for word in pair_words(n):
            checked += 1
            old = differences(word)
            normalized = rotate_to_permutation(word, n)
            need((normalized is not None) == ((1 << n) - 1 in old), "all-ones cut reduction")
            if normalized is not None:
                admitted += 1
                new, rename = normalized
                need(new[:n] == tuple(range(n)) and sorted(new[n:]) == list(range(n)),
                     "not a double permutation")
                relabelled = {sum(((m >> j) & 1) << rename[j] for j in range(n)) for m in old}
                need(differences(new) == relabelled, "rotation changed the difference set")
    # A nonuniversal path cannot be admitted just because it restores sources.
    need(rotate_to_permutation((0, 0, 1, 1, 2, 2), 3) is None, "bad cut control")
    return {"paired_words_checked": checked, "all_ones_words_admitted": admitted}


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return len(pivots)


def inverse(rows):
    n = len(rows)
    left, right = list(rows), [1 << i for i in range(n)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if left[i] >> col & 1)
        left[col], left[pivot] = left[pivot], left[col]
        right[col], right[pivot] = right[pivot], right[col]
        for i in range(n):
            if i != col and left[i] >> col & 1:
                left[i] ^= left[col]
                right[i] ^= right[col]
    need(left == [1 << i for i in range(n)], "singular frame")
    return tuple(right)


def multiply(a, b):
    return tuple(_xor(b[j] for j in range(len(b)) if row >> j & 1) for row in a)


def _xor(values):
    out = 0
    for value in values:
        out ^= value
    return out


def completion(first, n):
    rows = [first]
    for unit in (1 << i for i in range(n)):
        if rank(rows + [unit]) > len(rows):
            rows.append(unit)
    need(len(rows) == n, "cannot complete a zero vector")
    return tuple(rows)


def frame_moves(current, target):
    """Literal row-XOR realization; swaps are three paid XORs."""
    n = len(current)
    work = list(multiply(target, inverse(current)))
    reduction = []
    def add(a, b):
        work[a] ^= work[b]
        reduction.append(("X", a, b))
    for col in range(n):
        if not (work[col] >> col & 1):
            pivot = next(i for i in range(col + 1, n) if work[i] >> col & 1)
            add(col, pivot)
            add(pivot, col)
            add(col, pivot)
        for i in range(n):
            if i != col and work[i] >> col & 1:
                add(i, col)
    need(work == [1 << i for i in range(n)], "frame elimination")
    return reduction[::-1]


def compile_code(word, basis, n):
    """Constructive sufficiency: all child ports are physical zero, frames paid."""
    r = len(basis)
    need(rank(basis) == r and (1 << n) - 1 in span(basis), "invalid root code")
    points = prefix_points(word)
    need(points[-1] == 0 and all(word.count(j) == 2 for j in range(n)), "invalid paired word")
    readers = [[] for _ in points]
    for mask in range(1, 1 << n):
        found = None
        for coefficient in range(1, 1 << r):
            h = _xor(basis[i] for i in range(r) if coefficient >> i & 1)
            for a in range(len(points)):
                for b in range(a + 1, len(points)):
                    if (points[a] ^ points[b]) & h == mask:
                        found = (coefficient, a, b)
                        break
                if found is not None:
                    break
            if found is not None:
                break
        need(found is not None, "root code cannot realize every mask")
        coefficient, a, b = found
        readers[a].append((mask, coefficient))
        readers[b].append((mask, coefficient))
    program = []
    current = tuple(1 << i for i in range(r))
    def change(target):
        nonlocal current
        program.extend(frame_moves(current, target))
        current = target
    for cut in range(len(points)):
        for mask, reader in readers[cut]:
            change(completion(reader, r))
            program.append(("A", mask, 0))
        if cut < len(word):
            j = word[cut]
            axis = sum(((basis[i] >> j) & 1) << i for i in range(r))
            columns = completion(axis, r)
            matrix = tuple(sum(((columns[j] >> i) & 1) << j for j in range(r)) for i in range(r))
            change(inverse(matrix))
            program.append(("B", j, 0))
    change(tuple(1 << i for i in range(r)))
    return program


def star(n):
    """PR2182's credited construction, independently transcribed from its proof."""
    s, program = n - 4, []
    gray = [i ^ (i >> 1) for i in range(1 << s)]
    for phase in range(2):
        cycle = (0, 1, 0, 1) if phase == 0 else (2, 3, 2, 3)
        bulk = 0
        for tour in range(4):
            path = gray if tour % 2 == 0 else gray[::-1]
            for k, u in enumerate(path):
                if k:
                    edge = path[k - 1] ^ u
                    program.append(("X", 0, edge.bit_length()))
                for other in range(4):
                    mask = ((bulk | (other << 2)) if phase == 0 else (other | (bulk << 2))) | (u << 4)
                    if mask:
                        program.append(("A", mask, 0))
            program.append(("B", cycle[tour], 0))
            bulk ^= 1 << (cycle[tour] - 2 * phase)
        for j in range(4, n):
            program.append(("B", j, j - 3))
    return program


def replay(program, n, r, omit=None, reverse=False, roots=None, outputs=None):
    roots = list(roots) if roots is not None else [1 << i for i in range(r)]
    outputs = list(outputs) if outputs is not None else [0] * (1 << n)
    indexed = list(enumerate(program))
    for i, (kind, a, b) in (indexed[::-1] if reverse else indexed):
        if i == omit:
            continue
        if kind == "X":
            roots[a] ^= roots[b]
        elif kind == "B":
            roots[b] ^= 1 << (r + a)
        elif kind == "A":
            outputs[a] ^= roots[b]
        else:
            raise ValueError("unknown operation")
    return roots, outputs


def correct(program, n, r, omit=None):
    roots, outputs = replay(program, n, r, omit=omit)
    return roots == [1 << i for i in range(r)] and outputs == [m << r for m in range(1 << n)]


def program_controls():
    fixtures = []
    for n in range(4, 9):
        r, program = n - 3, star(n)
        need(correct(program, n, r), "credited star fails dirty-state semantics")
        roots, outputs = replay(program, n, r)
        back = replay(program, n, r, reverse=True, roots=roots, outputs=outputs)
        need(back == ([1 << i for i in range(r)], [0] * (1 << n)), "literal inverse")
        counts = Counter(op[0] for op in program)
        need(counts == {"B": 2*n, "A": 2*((1 << n)-1), **({"X": 8*((1 << (n-4))-1)} if n > 4 else {})},
             "star invoice")
        fixtures.append({"n": n, "roots": r, **dict(sorted(counts.items()))})
    program = star(8)
    rejected = sum(not correct(program, 8, 5, omit=i) for i in range(len(program)))
    need(rejected == len(program) == 646, "an omitted paid operation escaped")
    # A known five-source / two-root code, derived directly from the star axes.
    word = tuple(op[1] for op in star(5) if op[0] == "B")
    basis = (15, 16)
    need(available(word, span(basis)) == set(range(32)), "known two-root code")
    compiled = compile_code(word, basis, 5)
    need(correct(compiled, 5, 2), "constructive criterion failed")
    compiled_rejected = sum(not correct(compiled, 5, 2, omit=i) for i in range(len(compiled)))
    need(compiled_rejected == len(compiled), "compiled paid operation omission")
    # Insufficient dirt channels: same word, one all-ones reader only.
    try:
        compile_code(word, (31,), 5)
    except ValueError:
        pass
    else:
        raise ValueError("invalid one-root certificate accepted")
    dirty = list(program)
    first = next(i for i, op in enumerate(dirty) if op[0] == "A")
    dirty[first] = ("A", dirty[first][1], 1)
    need(not correct(dirty, 8, 5), "wrong physical reader port accepted")
    wrong = list(program)
    first = next(i for i, op in enumerate(wrong) if op[0] == "X")
    _, a, b = wrong[first]
    wrong[first] = ("X", b, a)
    need(not correct(wrong, 8, 5), "wrong transfer direction accepted")
    return {"star_fixtures": fixtures, "star_omissions_rejected": rejected,
            "compiled_five_source_calls": dict(sorted(Counter(op[0] for op in compiled).items())),
            "compiled_omissions_rejected": compiled_rejected, "additional_failures_rejected": 3}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def check_receipt(actual, expected):
    need(canonical(actual) == canonical(expected), "receipt mismatch")


def run():
    normalized = normalization_controls()
    controls = program_controls()
    old, _ = census(7, 3)
    need(old["source_orders"] == 5040 and old["codes"] == 651 and old["mandatory_survivors"] == 0,
         "seven-source calibration")
    result, codes = census(8, 4)
    need(result["source_orders"] == 40320 and result["codes"] == 11811 and
         result["mandatory_survivors"] == 0, "eight-source exclusion")
    receipt = {"schema_version": 1, "status": "EXACT_PAIRED_CALL_ROOT_EXCLUSION",
               "census": result, "seven_source_calibration": old,
               "code_inventory_sha256": hashlib.sha256(canonical(codes).encode()).hexdigest(),
               "normalization": normalized, "program_controls": controls}
    altered = json.loads(json.dumps(receipt))
    altered["census"]["mandatory_survivors"] = False
    try:
        check_receipt(receipt, altered)
    except ValueError:
        pass
    else:
        raise ValueError("typed receipt corruption accepted")
    return receipt, codes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit freshly recomputed evidence")
    parser.add_argument("--native-result", type=Path)
    parser.add_argument("--expected", type=Path, default=PACKAGE / "RESULT.json")
    args = parser.parse_args()
    receipt, codes = run()
    if args.native_result:
        native = json.loads(args.native_result.read_text())
        check_receipt(receipt["census"], native["summary"])
        check_receipt(codes, native["code_inventory"])
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        check_receipt(receipt, json.loads(args.expected.read_text()))
        print("PASS_EIGHT_SOURCE_ROOT_CODE words=40320 codes=11811 cases=476219520 survivors=0 roots=5 "
              "star_B=16 star_A=510 star_X=120" + (" native=agree" if args.native_result else ""))


if __name__ == "__main__":
    main()
