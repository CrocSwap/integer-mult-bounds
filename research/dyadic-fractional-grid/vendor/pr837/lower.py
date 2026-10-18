"""Both Horner directions for a single nonzero dyadic scalar macro.

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Apache-2.0. Binary copy/unit lowering is Sagar Thakrar's verbatim PR696
module. Forward NAF follows PR723 and our PR787; see README.md for pins.
"""

import importlib.util
from fractions import Fraction as Q
from pathlib import Path


def load_reference():
    spec = importlib.util.spec_from_file_location(
        "pr696", Path(__file__).resolve().parent / "vendor/pr696_lower.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reference = load_reference()


def digits(n, signed):
    """Least-significant-first binary or non-adjacent digits."""
    if type(n) is not int or n <= 0:
        raise ValueError("positive integer required")
    result = []
    while n:
        d = (2 - n % 4 if signed else 1) if n % 2 else 0
        result.append(d)
        n = (n - d) // 2
    return result


def candidates(op, work=("W", 0)):
    """Emit four circuits in stable tie order; each clears work on exit.

    Non-addition macros are inherited unchanged. No circuit writes source,
    borrows a logical register, or crosses the original macro boundary.
    """
    binary = reference.lower(op, work)  # Also validates dyadics and aliases.
    result = {"binary-forward": binary}
    if op[0] != "add" or abs(Q(op[3], op[4])) == 1:
        return result
    target, source = tuple(op[1]), tuple(op[2])
    q = Q(op[3], op[4])
    a, k = abs(q.numerator), q.denominator.bit_length() - 1
    sign = 1 if q > 0 else -1

    forward = [("copy", work, source)]
    for d in reversed(digits(a, True)[:-1]):
        forward.append(("double", work))
        if d:
            forward.append(("add" if d > 0 else "subtract", work, source))
    forward.extend([("halve", work)] * k)
    forward.extend([("add" if sign > 0 else "subtract", target, work), ("clear", work)])
    result["naf-forward"] = forward

    # Remove numerator trailing zeros so the initial reverse digit is +/-1.
    odd, exponent = a, -k
    while odd % 2 == 0:
        odd //= 2
        exponent += 1
    for signed in (False, True):
        ds = digits(odd, signed)
        initial_sign = ds[0]
        reverse = [("copy", work, source)]
        for d in ds[1:]:
            reverse.append(("halve", work))
            if d:
                reverse.append(("add" if d * initial_sign > 0 else "subtract", work, source))
        shift = len(ds) - 1 + exponent
        reverse.extend([("double" if shift > 0 else "halve", work)] * abs(shift))
        reverse.extend([
            ("add" if sign * initial_sign > 0 else "subtract", target, work),
            ("clear", work),
        ])
        result["naf-reverse" if signed else "binary-reverse"] = reverse
    return result


def choose(op, work=("W", 0), reverse=True):
    words = candidates(op, work)
    if not reverse:
        words = {k: v for k, v in words.items() if k.endswith("forward")}
    name = min(words, key=lambda key: len(words[key]))
    return name, words[name]


def lower(op, work=("W", 0)):
    return choose(op, work)[1]
