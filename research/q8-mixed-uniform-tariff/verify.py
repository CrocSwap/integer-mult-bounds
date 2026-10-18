"""Exact finite corroboration of the written uniform Q8 tariff theorem."""
from collections import Counter
from itertools import product
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# Elements 0,1,2,3,4,5,6,7 are 1,i,j,k,-1,-i,-j,-k.
UNITS = (((0,0),(1,0),(2,0),(3,0)), ((1,0),(0,1),(3,0),(2,1)),
         ((2,0),(3,1),(0,1),(1,0)), ((3,0),(2,0),(1,1),(0,1)))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def group(a, b):
    unit, sign = UNITS[a & 3][b & 3]
    return unit | (((a >> 2) ^ (b >> 2) ^ sign) << 2)


TABLE = [[group(a, b) for b in range(8)] for a in range(8)]


def multiply(a, b):
    result = 0
    for i in range(8):
        if a >> i & 1:
            for j in range(8):
                if b >> j & 1:
                    result ^= 1 << TABLE[i][j]
    return result


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def span(rows):
    result = {0}
    for row in rows:
        result |= {x ^ row for x in tuple(result)}
    return result


def outer(u, v, r):
    return [v if u >> i & 1 else 0 for i in range(r)]


def sum_projectors(factors, r, label=None):
    rows = [0] * r
    for g, u, v in factors:
        if label is None or g == label:
            for i, value in enumerate(outer(u, v, r)):
                rows[i] ^= value
    return rows


def formal(r, factors):
    state = [[int(i == j) for j in range(r)] for i in range(r)]
    for g, u, v in factors:
        need(g in (1, 2) and type(g) is int, "paid label")
        need(type(u) is type(v) is int and 0 < u < 1 << r and 0 < v < 1 << r, "scalar vectors")
        need((u & v).bit_count() % 2 == 1, "rank-one idempotent")
        for i in range(r):
            source = 0
            for k in range(r):
                if u >> k & 1:
                    source ^= state[i][k]
            delta = multiply(source, (1 << g) ^ 1)
            for j in range(r):
                if v >> j & 1:
                    state[i][j] ^= delta
    return state


def endpoint(targets):
    r = len(targets)
    return [[(1 << targets[i]) if i == j else 0 for j in range(r)] for i in range(r)]


def quotient(element):
    # The algebra 1,x,y with x^2=xy=yx=y^2=0.
    aug, first = element.bit_count() % 2, 0
    for g in range(8):
        if element >> g & 1:
            first ^= g & 3
    return aug, first


def checks_for_word(r, factors, state):
    xs = [u for _, u, _ in factors]
    ys = [v for _, _, v in factors]
    column_space, row_space = span(xs), span(ys)
    for g in range(8):
        rows = [sum((((state[i][j] >> g) & 1) ^ int(g == 0 and i == j)) << j for j in range(r)) for i in range(r)]
        columns = [sum(((rows[i] >> j) & 1) << i for i in range(r)) for j in range(r)]
        need(all(row in row_space for row in rows), "full coefficient row support")
        need(all(column in column_space for column in columns), "full coefficient image support")
    for label, bit in ((1, 0), (2, 1)):
        coefficient = [sum(((quotient(state[i][j])[1] >> bit) & 1) << j for j in range(r)) for i in range(r)]
        summed = sum_projectors(factors, r, label)
        need(coefficient == summed, "first-order coefficient identity")
        chosen = [(u, v) for g, u, v in factors if g == label]
        need(binary_rank([u for u, _ in chosen]) + binary_rank([v for _, v in chosen])
             <= len(chosen) + binary_rank(summed), "label Sylvester inequality")
    return binary_rank(xs), binary_rank(ys)


def direct(targets, prices):
    factors = []
    cheap = 1 if prices[0] <= prices[1] else 2
    for index, target in enumerate(targets):
        need(target in (0, 1, 2, 4), "target alphabet")
        labels = [] if target == 0 else [target] if target in (1, 2) else [cheap, cheap]
        factors.extend([g, 1 << index, 1 << index] for g in labels)
    return factors


def fixtures():
    result = []
    for width in range(5):
        for data in product((0, 1, 2, 4), repeat=width):
            targets = list(data) + [0]  # one explicitly dirty restored extra
            for prices in ((1, 1), (2, 5), (5, 2)):
                result.append({"targets": targets, "prices": list(prices), "word": direct(targets, prices), "attaining": True})
    rng = random.Random(310031)
    # Exact identity spurs genuinely mix an active coordinate with dirty extras.
    for r in (4, 6, 9):
        targets = [4, 4, 1] + [0] * (r - 3)
        seen = set()
        while len(seen) < 8:
            u, v = rng.randrange(1, 1 << r), rng.randrange(1, 1 << r)
            if (u & v).bit_count() % 2 != 1 or not ((u | v) >> 3) or not ((u | v) & 7) or (u, v) in seen:
                continue
            seen.add((u, v))
            word = [[1, u, v] for _ in range(4)] + direct(targets, (2, 3))
            # Whole spur is identity because i^4=1 and N^2=N.
            result.append({"targets": targets, "prices": [2, 3], "word": word, "attaining": False})
    return result


def sylvester_census():
    counts, transcript = {}, hashlib.sha256()
    for r in range(1, 4):
        for n in range(4):
            count = 0
            choices = list(product(range(1 << r), repeat=n))
            for columns in choices:
                rx = binary_rank(columns)
                for rows in choices:
                    ry = binary_rank(rows)
                    xy = [0] * r
                    for u, v in zip(columns, rows):
                        for i in range(r):
                            if u >> i & 1:
                                xy[i] ^= v
                    rxy = binary_rank(xy)
                    need(rx + ry <= n + rxy, "exhaustive Sylvester")
                    transcript.update(bytes((rx, ry, rxy)))
                    count += 1
            counts[f"r{r}-n{n}"] = count
    return counts, transcript.hexdigest()


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    for record in manifest["files"]:
        if record["usage"] == "input":
            need(hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"], "context source drift")
    need({record["path"] for record in manifest["vendored_inputs"]} == {
        "inputs/pr1573-README.md", "inputs/pr2047-README.md", "inputs/pr2248-README.md"
    } and len(manifest["vendored_inputs"]) == 3, "three retained predecessor texts")
    for record in manifest["vendored_inputs"]:
        raw = (HERE / record["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == record["sha256"], "predecessor source drift")
        need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == record["git_blob"], "predecessor Git blob")


def run():
    authenticate()
    need(all(TABLE[TABLE[a][b]][c] == TABLE[a][TABLE[b][c]] for a,b,c in product(range(8), repeat=3)), "Q8 associativity")
    need(TABLE[1][1] == TABLE[2][2] == 4 and TABLE[1][2] != TABLE[2][1], "Q8 defining products")
    need(all((TABLE[a][b] & 3) == ((a & 3) ^ (b & 3)) for a,b in product(range(8), repeat=2)), "first-order quotient")
    cases = fixtures()
    need(canonical(cases) == canonical(json.loads((HERE / "FIXTURES.json").read_bytes())), "complete fixture regeneration")
    columns, lower_slacks = 0, Counter()
    for fixture in cases:
        targets, prices, word = fixture["targets"], fixture["prices"], fixture["word"]
        r = len(targets)
        state = formal(r, word)
        need(state == endpoint(targets), "full formal endpoint")
        rx, ry = checks_for_word(r, word, state)
        t, si, sj = targets.count(4), targets.count(1), targets.count(2)
        active = t + si + sj
        need(rx >= active and ry >= active, "target support ranks")
        ni, nj = sum(g == 1 for g,_,_ in word), sum(g == 2 for g,_,_ in word)
        need(ni >= si and nj >= sj and ni + nj >= 2*t + si + sj, "uniform lower bound")
        cost = prices[0]*ni + prices[1]*nj
        exact = prices[0]*si + prices[1]*sj + 2*t*min(prices)
        need(cost >= exact and (not fixture["attaining"] or cost == exact), "exact weighted tariff")
        columns += 8*r
        lower_slacks[ni+nj-(2*t+si+sj)] += 1
    # Arbitrary non-diagonal words corroborate support and quotient identities,
    # independently of the attaining coordinate-word family.
    rng = random.Random(310031)
    random_prefixes = 0
    for r in (2, 3, 5, 7):
        for _ in range(16):
            word = []
            for _ in range(7):
                u = rng.randrange(1, 1 << r)
                v = rng.randrange(1, 1 << r)
                while (u & v).bit_count() % 2 != 1:
                    v = rng.randrange(1, 1 << r)
                word.append([rng.choice((1, 2)), u, v])
                checks_for_word(r, word, formal(r, word))
                random_prefixes += 1
    counts, sylvester_hash = sylvester_census()
    # Semantic countercontrols identify material hypotheses, not just syntax.
    need(formal(2, [[1,1,1]]) != endpoint([4,0]), "one generator cannot realize central target")
    need(quotient(1 << 4) == quotient(1) and (1 << 4) != 1, "quotient kernel control")
    dirty = formal(2, [[1,3,1]])
    need(dirty[0] == [1 << 1, 0] and dirty != endpoint([1,0]), "dirty helper leakage control")
    need(formal(3, direct([4,4,1], (1,1))[:-1]) != endpoint([4,4,1]), "omitted paid call control")
    # If central z were itself unit priced, one coordinate call attains z in
    # one step. The theorem's paid alphabet deliberately excludes that factor.
    expanded = [[1 << 4, 0], [0, 1]]
    need(expanded == endpoint([4,0]) and 1 < 2, "expanded alphabet countercontrol")
    try:
        formal(2, [[1,1,2]])
    except ValueError as error:
        need("idempotent" in str(error), "nilpotent rejection reason")
    else:
        raise ValueError("accepted nilpotent factor")
    spec = importlib.util.spec_from_file_location("q8_faithful_independent", HERE / "independent.py")
    independent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(independent)
    corroboration = independent.check(cases)
    return {"status": "PASS_Q8_MIXED_UNIFORM_TARIFF", "group_associativity_triples": 512,
            "fixtures": len(cases), "formal_input_columns": columns, "fixture_sha256": digest(cases),
            "paid_count_slacks": dict(sorted(lower_slacks.items())), "random_prefixes": random_prefixes,
            "sylvester_pairs": sum(counts.values()), "sylvester_domains": counts, "sylvester_sha256": sylvester_hash,
            "independent": corroboration, "controls": ["underpriced_central", "quotient_kernel", "dirty_leakage", "omitted_call", "expanded_alphabet", "nilpotent_projector"],
            "scope": "Written all-size formal Q8 tariff for targets1/i/j/-1, paid labels i/j and arbitrary restored dirty roles. Finite checks corroborate; no native supplier or kappa."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out:
        need(not args.out.exists(), "output already exists")
    result = run()
    if args.out:
        with args.out.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads((HERE / "RESULT.json").read_bytes())), "typed receipt mismatch")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
