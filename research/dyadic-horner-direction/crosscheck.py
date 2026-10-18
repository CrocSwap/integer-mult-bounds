"""Independent integer-scaled three-column and cost-formula crosscheck.

No import of the rational replay, its interpreter, or its digit routines.
The emitted words are the object under test. Gareth Davidson (@bitplane),
substantial OpenAI Codex assistance; Apache-2.0. Not independent authorship.
"""

import importlib.util
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def normal(nums, exponent):
    nums = tuple(nums)
    while exponent and all(x % 2 == 0 for x in nums):
        nums = tuple(x // 2 for x in nums)
        exponent -= 1
    return nums, exponent


def add(a, b, sign=1):
    av, ae = a
    bv, be = b
    e = max(ae, be)
    return normal([x * 2**(e-ae) + sign * y * 2**(e-be) for x, y in zip(av, bv)], e)


def scale(a, double):
    nums, e = a
    return normal([2*x for x in nums], e) if double else normal(nums, e+1)


def greater(a, b):
    return a[0][0] * 2**b[1] > b[0][0] * 2**a[1]


def scalar_text(value):
    n, e = value[0][0], value[1]
    return str(n) if e == 0 else str(n) + "/" + str(2**e)


def execute(word, numerator, denominator):
    """Three dense integer columns, each with a shared binary denominator."""
    t, s, w = ("T", 0), ("S", 0), ("W", 0)
    state = {t: ((1, 0, 0), 0), s: ((0, 1, 0), 0), w: ((0, 0, 1), 0)}
    majorant = dict.fromkeys(state, ((1,), 0))
    peak = ((1,), 0)
    for step in word:
        tag, dest = step[:2]
        require(dest in (t, w), "foreign/source write")
        if tag == "clear":
            state[dest], majorant[dest] = ((0, 0, 0), 0), ((0,), 0)
        elif tag == "copy":
            state[dest], majorant[dest] = state[step[2]], majorant[step[2]]
        elif tag in ("add", "subtract"):
            src = step[2]
            state[dest] = add(state[dest], state[src], 1 if tag == "add" else -1)
            majorant[dest] = add(majorant[dest], majorant[src])
        elif tag in ("double", "halve"):
            state[dest] = scale(state[dest], tag == "double")
            majorant[dest] = scale(majorant[dest], tag == "double")
        else:
            raise ValueError("unexpected primitive")
        if greater(majorant[dest], peak):
            peak = majorant[dest]
    expected = normal((denominator, numerator, 0), denominator.bit_length()-1)
    require(state[t] == expected, "dense target endpoint mismatch")
    require(state[s] == ((0, 1, 0), 0), "dense source modified")
    require(state[w] == ((0, 0, 0), 0), "dense dirty work survives")
    return scalar_text(peak)


def statistics(n, signed):
    if not signed:
        return n.bit_length()-1, n.bit_count()
    # NAF digits from the difference of shifted bits of 3n and n.
    # This uses neither the lowerer's modular recurrence nor its digit list.
    ds = [((3*n >> i) & 1) - ((n >> i) & 1) for i in range(1, (3*n).bit_length())]
    require(sum(d * 2**i for i, d in enumerate(ds)) == n, "independent NAF identity")
    return len(ds)-1, sum(d != 0 for d in ds)


def formula(n, denominator):
    n = abs(n)
    if n == denominator:
        return {"binary-forward": 2}
    k = denominator.bit_length()-1
    h, weight = statistics(n, False)
    hn, wn = statistics(n, True)
    out = {"binary-forward": 2+h+weight+k, "naf-forward": 2+hn+wn+k}
    trailing = (n & -n).bit_length()-1
    odd = n >> trailing
    for signed, name in ((False, "binary-reverse"), (True, "naf-reverse")):
        height, weight = statistics(odd, signed)
        out[name] = 2 + height + weight + abs(height+trailing-k)
    return out


def check(lowering, n, d):
    common = gcd(abs(n), d)
    n, d = n//common, d//common
    op = ["add", ["T", 0], ["S", 0], n, d]
    words = lowering.candidates(op)
    expected = formula(n, d)
    costs = {name: len(word) for name, word in words.items()}
    require(costs == expected, "closed-form cost mismatch")
    peaks = {name: execute(word, n, d) for name, word in words.items()}
    chosen = min(expected, key=expected.get)
    require(lowering.choose(op)[0] == chosen, "tie/choice mismatch")
    return costs, peaks, chosen


def main():
    spec = importlib.util.spec_from_file_location("tested_lowering", HERE / "lower.py")
    lowering = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lowering)
    receipt = json.loads((HERE / "EXPECTED.json").read_bytes())
    records = receipt["coefficient_certificates"]
    for record in records:
        pieces = record["coefficient"].split("/")
        n, d = int(pieces[0]), int(pieces[1]) if len(pieces) == 2 else 1
        costs, peaks, chosen = check(lowering, n, d)
        require(costs == record["costs"] and peaks == record["positive_prefixes"] and
                chosen == record["chosen"], "rational/integer receipt disagreement")
    # A fixed domain includes both signs, reducible inputs, integral powers,
    # fractions above/below one and negative leading reverse NAF digits.
    cases = 0
    for n in range(1, 512):
        for k in range(13):
            for sign in (-1, 1):
                check(lowering, sign*n, 2**k)
                cases += 1
    print("PASS_INTEGER_HORNER_CROSSCHECK coefficients=" + str(len(records)) +
          " grid_cases=" + str(cases) + " input_columns=3 costs_and_prefixes=exact")


if __name__ == "__main__":
    main()
