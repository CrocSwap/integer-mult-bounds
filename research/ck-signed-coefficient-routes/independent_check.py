"""Integer-only exhaustive route/cost/prefix crosscheck; imports no circuit code.

This implementation enumerates both exponents. The constructor instead solves
for the second exponent using rational arithmetic. Apache-2.0; see README.md.
Joseph / AmazedBot, with substantial OpenAI Codex assistance.
"""

from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ("W", 0)


def demand(ok, why):
    if not ok:
        raise ValueError(why)


def data(path):
    raw = path.read_bytes()
    return gzip.decompress(raw) if path.suffix == ".gz" else raw


def load(path):
    return json.loads(data(path))


def compact(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def dyadic(n, denominator=1):
    """Return normalized (integer numerator, power-of-two denominator exponent)."""
    if denominator < 0:
        n, denominator = -n, -denominator
    demand(denominator > 0 and denominator & (denominator - 1) == 0, "not dyadic")
    k = denominator.bit_length() - 1
    while k and n % 2 == 0:
        n //= 2
        k -= 1
    return n, k


def parse(s):
    bits = s.split("/")
    return dyadic(int(bits[0]), int(bits[1]) if len(bits) == 2 else 1)


def show(x):
    n, k = x
    return str(n) if k == 0 else f"{n}/{1 << k}"


def plus(a, b):
    k = max(a[1], b[1])
    return dyadic((a[0] << (k - a[1])) + (b[0] << (k - b[1])), 1 << k)


def scaled(a, e):
    n, k = a
    return dyadic(n << max(0, e - k), 1 << max(0, k - e))


def greater(a, b):
    return (a[0] << b[1]) > (b[0] << a[1])


def power_between(a, b):
    an, ak = a
    bn, bk = b
    au = (an & -an).bit_length() - 1
    bu = (bn & -bn).bit_length() - 1
    if an >> au != bn >> bu:
        return None
    return bu - bk - au + ak


def preparation_cost(b):
    n, k = b
    return n.bit_length() + n.bit_count() + k - 1


def brute(a, b):
    """All 2*33*33 one-read candidates, plus reset and power-only."""
    reset = (preparation_cost(b), "reset", 0, 0, 0)
    candidates = [reset]
    e = power_between(a, b)
    if e is not None:
        candidates.append((abs(e), "power", e, 0, 0))
    power = min(candidates)
    positive, signed = list(candidates), list(candidates)
    valid = 0
    for u in range(-16, 17):
        for v in range(-16, 17):
            # Clear all denominators before comparison. No Fraction arithmetic.
            ea, eb, es = u + v - a[1], -b[1], v
            floor = min(ea, eb, es, 0)
            lhs = a[0] << (ea - floor)
            rhs = b[0] << (eb - floor)
            unit = 1 << (es - floor)
            for sign in (-1, 1):
                if lhs + sign * unit == rhs:
                    valid += 1
                    choice = (abs(u) + abs(v) + 1, "read", u, v, sign)
                    signed.append(choice)
                    if sign == 1:
                        positive.append(choice)
    return {"power": list(power), "positive": list(min(positive)),
            "signed": list(min(signed))}, valid


def shift_ops(register, e):
    return [("double" if e > 0 else "halve", register) for _ in range(abs(e))]


def preparation(source, value, copy_initial=True):
    n, k = value
    word = [("clear", WORK)]
    for i in reversed(range(n.bit_length())):
        if i < n.bit_length() - 1:
            word.append(("double", WORK))
        if n & (1 << i):
            word.append(("add", WORK, source))
    word += [("halve", WORK) for _ in range(k)]
    return [("copy", WORK, source)] + word[2:] if copy_initial else word


def lower_original(op):
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        return [(tag, target)]
    if tag == "copy":
        return [(tag, target, tuple(op[2]))]
    if tag == "scale":
        n, k = dyadic(op[2], op[3])
        demand(abs(n) & (abs(n) - 1) == 0, "nonpower scale")
        return shift_ops(target, abs(n).bit_length() - 1 - k) + (
            [("negate", target)] if n < 0 else [])
    demand(tag == "add", "unknown macro")
    n, k = dyadic(op[3], op[4])
    return preparation(tuple(op[2]), (abs(n), k), copy_initial=False) + [
        ("add" if n > 0 else "subtract", target, WORK), ("clear", WORK)]


def lower_copy(op):
    if op[0] != "add":
        return lower_original(op)
    n, k = dyadic(op[3], op[4])
    source, target = tuple(op[2]), tuple(op[1])
    sign = "add" if n > 0 else "subtract"
    if abs(n) == 1 and k == 0:
        return [(sign, target, source), ("clear", WORK)]
    return preparation(source, (abs(n), k)) + [(sign, target, WORK), ("clear", WORK)]


def group_signature(e):
    if e[0] != "scalar" or e[1][0] != "add":
        return None
    n, k = dyadic(*e[1][3:5])
    if abs(n) == 1 and k == 0:
        return None
    return tuple(e[1][2]), e[2]


def expand_group(chunk, table, mode):
    source = tuple(chunk[0][1][2])
    last = None
    word = []
    for e in chunk:
        n, k = dyadic(*e[1][3:5])
        b = (abs(n), k)
        if last is None:
            word.extend(preparation(source, b))
        else:
            cost, kind, u, v, sign = table[show(last), show(b)][mode]
            if kind == "reset":
                route = preparation(source, b)
            else:
                route = shift_ops(WORK, u)
                if kind == "read":
                    route += [("add" if sign == 1 else "subtract", WORK, source)]
                    route += shift_ops(WORK, v)
            demand(len(route) == cost, "route count")
            # Independently execute each route from W=a*S, S=1.
            coefficient = last
            for op in route:
                if op[0] == "clear":
                    coefficient = (0, 0)
                elif op[0] == "copy":
                    coefficient = (1, 0)
                elif op[0] in ("double", "halve"):
                    coefficient = scaled(coefficient, 1 if op[0] == "double" else -1)
                else:
                    coefficient = plus(coefficient, (1 if op[0] == "add" else -1, 0))
            demand(coefficient == b, "route identity")
            word.extend(route)
        word.append(("add" if n > 0 else "subtract", tuple(e[1][1]), WORK))
        last = b
    return word + [("clear", WORK)]


def prefix_op(env, op):
    tag, t = op[:2]
    if tag == "clear":
        env[t] = (0, 0)
    elif tag == "copy":
        env[t] = env[op[2]]
    elif tag == "double":
        env[t] = scaled(env[t], 1)
    elif tag == "halve":
        env[t] = scaled(env[t], -1)
    elif tag in ("add", "subtract"):
        env[t] = plus(env[t], env[op[2]])
    elif tag != "negate":
        raise ValueError("unknown primitive")
    return env[t]


def audit():
    pins = load(HERE / "SOURCES.json")
    for name, pin in pins["files"].items():
        demand(hashlib.sha256(data(ROOT / name)).hexdigest() == pin["payload_sha256"], "source pin")
    paths = [p for p in pins["files"] if p.endswith("/ck/LOCAL-PROGRAMS.json.gz")]
    demand(len(paths) == 1, "program inventory")
    programs = load(ROOT / paths[0])
    certificate = load(HERE / "ROUTES.json")
    expected = load(HERE / "EXPECTED.json")
    table, legal = {}, 0
    for row in certificate:
        key = row["a"], row["b"]
        demand(key not in table, "duplicate coefficient pair")
        result, valid = brute(parse(key[0]), parse(key[1]))
        demand(result == {mode: row[mode] for mode in result}, "nonminimal or wrong route")
        table[key] = result
        legal += valid
    demand(hashlib.sha256(compact(certificate)).hexdigest() == expected["routes_sha256"], "route receipt")
    encountered = set()
    summaries = {}
    for orientation, events in programs.items():
        env = {("L", r): (1, 0) for r in range(716)}
        env.update({("C", r): (1, 0) for r in range(8)})
        env[WORK] = (1, 0)
        peak = (1, 0)
        counts = Counter()
        modes = Counter()
        h = hashlib.sha256()
        at = groups = additions = 0
        while at < len(events):
            event = events[at]
            end = at + 1
            key = group_signature(event)
            if key is not None:
                while end < len(events) and group_signature(events[end]) == key:
                    end += 1
            if event[0] != "scalar":
                at = end
                continue
            chunk = events[at:end]
            modes["original"] += 2 * sum(len(lower_original(e[1])) for e in chunk)
            modes["copy_baseline"] += 2 * sum(len(lower_copy(e[1])) for e in chunk)
            if len(chunk) > 1:
                groups += 1
                additions += len(chunk)
                magnitudes = [dyadic(abs(e[1][3]), abs(e[1][4])) for e in chunk]
                encountered.update((show(a), show(b)) for a, b in zip(magnitudes, magnitudes[1:]))
                for mode in ("power", "positive", "signed"):
                    word = expand_group(chunk, table, mode)
                    modes[mode] += 2 * len(word)
            else:
                word = lower_copy(event[1])
                for mode in ("power", "positive", "signed"):
                    modes[mode] += 2 * len(word)
            for op in word:
                h.update(compact([event[2], op]) + b"\n")
                counts[op[0]] += 2
                now = prefix_op(env, op)
                if greater(now, peak):
                    peak = now
            at = end
        receipt = expected["programs"][orientation]
        demand(dict(modes) == receipt["real_primitives"], "complete primitive counts")
        demand(dict(counts) == receipt["primitive_counts"], "primitive inventory")
        demand(h.hexdigest() == receipt["primitive_word_sha256"], "primitive word digest")
        demand(show(peak) == receipt["literal_positive_prefix"], "literal prefix")
        demand(groups == receipt["blocks"] and additions == receipt["run_additions"], "run coverage")
        summaries[orientation] = {"groups": groups, "prefix": show(peak), "real_primitives": dict(modes)}
    demand(encountered == set(table), "missing or extra pair coverage")
    demand(len(table) == expected["distinct_coefficient_pairs"], "pair count")
    # Arithmetic controls independent of the Fraction implementation.
    demand(scaled((3, 1), -1) == (3, 2), "half control")
    demand(plus((3, 2), (-1, 0)) == (-1, 2), "signed addition control")
    demand(scaled((3, 2), 1) != (3, 2), "omitted doubling control")
    demand(plus((3, 1), (-1, 0)) != plus((3, 1), (1, 0)), "wrong sign control")
    return {"pairs": len(table), "one_read_cases": len(table) * 2 * 33 * 33,
            "legal_one_read_cases": legal, "programs": summaries}


if __name__ == "__main__":
    result = audit()
    print(f"PASS_CK_SIGNED_ROUTES_INTEGER pairs={result['pairs']} "
          f"one_read_cases={result['one_read_cases']} programs=2")
