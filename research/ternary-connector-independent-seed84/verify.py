#!/usr/bin/env python3
"""Exact F3 connector census; Python 3.10+, standard library, no source imports."""
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 84
M = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
OPS = tuple((k, i) for k in ("A", "B") for i in range(3))
MOVES = tuple((j, s) for j in range(3) for s in (-1, 1))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def rows_mod(matrix):
    return tuple(tuple(x % 3 for x in row) for row in matrix)


def prefixes(word):
    q = [0, 0, 0]
    points = [tuple(q)]
    for j, s in word:
        q[j] = (q[j] + s) % 3
        points.append(tuple(q))
    require(q == [0, 0, 0], "source path does not restore")
    return points


def differences(points):
    result = {}
    for a, b in it.product(range(len(points)), repeat=2):
        row = tuple((x - y) % 3 for x, y in zip(points[a], points[b]))
        result.setdefault(row, ((a, 1), (b, -1)))
    return result


def triples(points):
    result = {}
    for indices in it.combinations_with_replacement(range(len(points)), 3):
        for sign in (-1, 1):
            row = tuple(sign * sum(points[t][j] for t in indices) % 3 for j in range(3))
            result.setdefault(row, tuple((t, sign) for t in indices))
    return result


def assemble(source, readers):
    word = []
    for t in range(len(source) + 1):
        for i, reads in enumerate(readers):
            word.extend(("A", i, s) for at, s in reads if at == t)
        if t < len(source):
            j, s = source[t]
            word.append(("B", j, s))
    return tuple(word)


def seven_paths(j):
    other = tuple(move for move in MOVES if move[0] != j)
    for sign in (-1, 1):
        for positions in it.combinations(range(7), 3):
            for remaining in it.permutations(other):
                rest = iter(remaining)
                yield tuple((j, sign) if t in positions else next(rest) for t in range(7))


def matrix_replay(word, modulus):
    # Scalar identity maps are faithful to the coefficient equations in this alphabet.
    state = [[int(i == j) for j in range(7)] for i in range(7)]
    for kind, i, sign in word:
        source, target = (i, 6) if kind == "B" else (6, 3 + i)
        state[target] = [a + sign * b for a, b in zip(state[target], state[source])]
        if modulus:
            state[target] = [x % modulus for x in state[target]]
    return state


def wanted(matrix, modulus):
    result = [[int(i == j) for j in range(7)] for i in range(7)]
    for i, row in enumerate(matrix):
        result[3 + i][:3] = [x % modulus if modulus else x for x in row]
    return result


def inverse(word):
    return tuple((k, i, -s) for k, i, s in reversed(word))


def transforms(words):
    family = {}
    for rp, cp in it.product(it.permutations(range(3)), repeat=2):
        for rs, cs in it.product(it.product((-1, 1), repeat=3), repeat=2):
            matrix = tuple(tuple(rs[i] * cs[j] * M[rp[i]][cp[j]] for j in range(3)) for i in range(3))
            if matrix in family:
                continue
            transformed = {}
            for (kind, old), word in words.items():
                perm, signs = (rp, rs) if kind == "A" else (cp, cs)
                key = (kind, perm.index(old))
                transformed[key] = tuple((k, (rp if k == "A" else cp).index(i),
                    s * (rs if k == "A" else cs)[(rp if k == "A" else cp).index(i)])
                    for k, i, s in word)
            family[matrix] = transformed
    return family


def factors(kind, i):
    length = (5 + i) if kind == "A" else (2 + i)
    return tuple(f"{kind}{i}.{j}" for j in range(length))


def lower(product, source, target, depth=0):
    if len(product) == 1:
        return ((product[0], source, target, 1),)
    cut = len(product) // 2
    scratch = 7 + depth
    right = lower(product[:cut], source, scratch, depth + 1)
    left = lower(product[cut:], scratch, target, depth + 1)
    undo = lambda word: tuple((f, x, y, -s) for f, x, y, s in reversed(word))
    return right + left + undo(right) + undo(left)


def expand(word):
    leaves = []
    for kind, i, sign in word:
        source, target = (i, 6) if kind == "B" else (6, 3 + i)
        block = lower(factors(kind, i), source, target)
        if sign < 0:
            block = tuple((f, x, y, -s) for f, x, y, s in reversed(block))
        leaves.extend(block)
    return leaves


def module_replay(leaves):
    state = [{(i, ()): 1} for i in range(10)]
    for f, source, target, sign in leaves:
        require(source != target and 0 <= source < 10 and 0 <= target < 10, "invalid leaf ports")
        for (origin, operators), coefficient in list(state[source].items()):
            key = (origin, (f,) + operators)
            value = (state[target].get(key, 0) + sign * coefficient) % 3
            if value:
                state[target][key] = value
            else:
                state[target].pop(key, None)
    return state


def wanted_module(matrix):
    state = [{(i, ()): 1} for i in range(10)]
    for i, row in enumerate(matrix):
        for j, coefficient in enumerate(row):
            if coefficient:
                chain = tuple(reversed(factors("B", j) + factors("A", i)))
                state[3 + i][(j, chain)] = coefficient % 3
    return state


def compute():
    target = rows_mod(M)
    reached = set()
    witnesses = {}
    hits = {op: 0 for op in OPS}
    trace12, trace13 = [], []
    for source in it.permutations(MOVES):
        points = prefixes(source)
        pairs = differences(points)
        codes = sorted(sum(x * 3 ** j for j, x in enumerate(row)) for row in pairs)
        reached.update(a + 27 * b + 729 * c for a, b, c in it.product(codes, repeat=3))
        triple = triples(points)
        flags = []
        for i in range(3):
            ok = target[i] in triple and all(target[k] in pairs for k in range(3) if k != i)
            flags.append(ok)
            if ok:
                hits[("A", i)] += 1
                readers = [triple[row] if k == i else pairs[row] for k, row in enumerate(target)]
                witnesses.setdefault(("A", i), assemble(source, readers))
        trace12.append((source, codes, flags))
    for j in range(3):
        count = 0
        for source in seven_paths(j):
            count += 1
            pairs = differences(prefixes(source))
            ok = all(row in pairs for row in target)
            if ok:
                hits[("B", j)] += 1
                witnesses.setdefault(("B", j), assemble(source, [pairs[row] for row in target]))
            trace13.append((source, ok))
        require(count == 1680, "seven-step domain incomplete")
    require(len(trace12) == 720 and len(trace13) == 5040, "path coverage")
    missing = set(range(27 ** 3)) - reached
    family = transforms(witnesses)
    encode = lambda matrix: sum((x % 3) * 3 ** (3 * i + j) for i, row in enumerate(matrix) for j, x in enumerate(row))
    require(len(reached) == 19395 and len(missing) == 288, "twelve-query classification")
    require(set(map(encode, family)) == missing, "obstruction orbit differs from exclusion")
    predecessor = json.loads((ROOT / "research/signed-connector-obstruction/CERTIFICATE.json").read_text())
    require({encode(m) for m in predecessor["obstructed_patterns"]} == missing, "predecessor obstruction mismatch")
    require(len(witnesses) == 6 and len(family) == 288, "six repairs for whole orbit missing")
    replays = 0
    for matrix, words in family.items():
        for extra, word in words.items():
            require(len(word) == 13, "word length")
            require([sum((k, i) == op for k, i, _ in word) for op in OPS] ==
                    [2 + int(op == extra) for op in OPS], "operator invoice")
            require(matrix_replay(word, 3) == wanted(matrix, 3), "F3 word failure")
            require(matrix_replay(word + inverse(word), 3) == wanted(((0, 0, 0),) * 3, 3), "inverse failure")
            replays += 1
    fixture = sorted(family)[SEED]
    leaf_counts = {}
    leaf_replays = 0
    for matrix, words in ((M, witnesses), (fixture, family[fixture])):
        for extra, word in words.items():
            leaves = expand(word)
            require(module_replay(leaves) == wanted_module(matrix), "noncommutative leaf identity")
            leaf_replays += 1
            if matrix == M:
                leaf_counts["".join(map(str, extra))] = len(leaves)
    controls = {}
    for extra, word in witnesses.items():
        name = "".join(map(str, extra))
        controls["integer_" + name] = matrix_replay(word, 0) != wanted(M, 0)
        controls["F5_" + name] = matrix_replay(word, 5) != wanted(M, 5)
        for t in range(13):
            controls[f"omit_{name}_{t}"] = matrix_replay(word[:t] + word[t + 1:], 3) != wanted(M, 3)
            changed = word[:t] + ((word[t][0], word[t][1], -word[t][2]),) + word[t + 1:]
            controls[f"flip_{name}_{t}"] = matrix_replay(changed, 3) != wanted(M, 3)
    chosen = witnesses[("B", 0)]
    leaves = expand(chosen)
    controls["omit_leaf"] = module_replay(leaves[:-1]) != wanted_module(M)
    wrong = wanted_module(M)
    key = next(k for k in wrong[3] if k[1])
    coefficient = wrong[3].pop(key)
    wrong[3][(key[0], tuple(reversed(key[1])))] = coefficient
    controls["commute_factors"] = module_replay(leaves) != wrong
    require(all(controls.values()), "negative control did not fail")
    return {
        "status": "PASS_TERNARY_CONNECTOR_INDEPENDENT", "seed": SEED,
        "base": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f", "field": 3,
        "matrices": 19683, "support_bound_attained": len(reached),
        "obstructed_minimum_13": len(missing), "source_paths_6": len(trace12),
        "source_paths_7": len(trace13), "canonical_feasible_source_paths":
            {"".join(map(str, op)): hits[op] for op in OPS},
        "trace12_sha256": digest(trace12), "trace13_sha256": digest(trace13),
        "missing_sha256": digest(sorted(missing)), "orbit_word_replays": replays,
        "literal_leaf_replays": leaf_replays, "canonical_leaf_counts": leaf_counts,
        "canonical_words": {"".join(map(str, op)): witnesses[op] for op in OPS},
        "seed_fixture": {"index": SEED, "matrix": fixture, "B0_word": family[fixture][("B", 0)]},
        "negative_controls": len(controls), "controls_sha256": digest(controls),
        "scope": "Exact F3 query-alphabet optimum; no physical supplier or new kappa."
    }


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path, expected in pins["files"].items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, "source pin: " + path)
    receipt = compute()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        require(not sys.argv[1:], "only --emit is supported")
        expected = json.loads((HERE / "CERTIFICATE.json").read_text())
        require(json.loads(json.dumps(receipt)) == expected, "certificate drift")
        print(receipt["status"], "matrices=19683 obstructed_minimum=13 orbit_replays=1728",
              "source_paths=5760 leaf_replays=12 controls=" + str(receipt["negative_controls"]))


if __name__ == "__main__":
    main()
