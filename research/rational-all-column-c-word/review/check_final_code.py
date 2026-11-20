"""Final candidate-code checks against the earlier independent C oracle."""
from fractions import Fraction
from hashlib import sha256
from importlib.util import spec_from_file_location, module_from_spec
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
sys.path.insert(0, str(CANDIDATE))
from word import Word, encode, parse
from execute import execute

spec = spec_from_file_location("earlier_independent", HERE / "check_rational_grid.py")
earlier = module_from_spec(spec)
spec.loader.exec_module(earlier)


def need(ok, message):
    if not ok:
        raise ArithmeticError(message)


def oracle(data, axes):
    result = []
    for row in data:
        current = [(Fraction(a), Fraction(b)) for a, b in row]
        for axis in reversed(axes):
            current = earlier.reference_c(current, axis)
        current = [(a * (1 << len(axes)), b * (1 << len(axes))) for a, b in current]
        need(all(a.denominator == b.denominator == 1 for a, b in current),
             "reference integer numerator")
        result.append([(int(a), int(b)) for a, b in current])
    return result


def sample(count, ambient, constant=False):
    if constant:
        return [[(1, 0)] * (1 << ambient) for _ in range(count)]
    return [[(((19 * address + 11 * row) % 37) - 18,
              ((7 * address - 13 * row) % 41) - 20)
             for address in range(1 << ambient)] for row in range(count)]


def paid(n, w):
    return tuple(("paid", r, a) for r in range(w) for a in range(n))


def mixing(reg, source, scratch, a, b, q, subtract=False):
    return (("add", scratch, source), ("scale", scratch, a, b, q),
            ("sub" if subtract else "add", reg, scratch), ("clear", scratch))


def fixtures():
    deep = Word(2, 2, 0, (("scale", 0, 1, 0, 3),) * 5
                + paid(2, 2) + (("scale", 0, 3, 0, 1),) * 5)
    stash = (("add", 3, 0), ("scale", 0, 0, 0, 13), ("add", 0, 3), ("clear", 3))
    mix = mixing(1, 0, 3, 2, -1, 15) + mixing(2, 1, 4, -3, 2, 14)
    unmix = mixing(2, 1, 4, -3, 2, 14, True) + mixing(1, 0, 3, 2, -1, 15, True)
    native = (("x", 0, 2),) * 2 + (("s", 1, 0),) * 4
    native += (("cx", 2, 2, 0),) * 2 + (("cz", 1, 0, 2),) * 2
    native += (("unit", 0),) * 4
    private = (("add", 4, 2), ("scale", 4, -4, 1, 33),
               ("paid", 4, 1), ("clear", 4))
    three = Word(3, 3, 2, stash + mix + native + paid(3, 3) + unmix + private)
    large_binary = Word(2, 2, 0, (("scale", 0, 1, 0, 1 << 1024),)
                        + paid(2, 2) + (("scale", 0, 1 << 1024, 0, 1),))
    alias = Word(2, 2, 1, (("add", 2, 0), ("scale", 0, 0, 0, 5),
                          ("add", 0, 2), ("sub", 2, 2),
                          ("add", 1, 1), ("half", 1)) + paid(2, 2))
    return deep, three, large_binary, alias


def reject(action, fragment):
    try:
        action()
    except ArithmeticError as exc:
        need(fragment in str(exc), "wrong rejection reason: " + str(exc))
        return str(exc)
    raise ArithmeticError("negative control accepted")


def main():
    deep, three, large_binary, alias = fixtures()
    all_words = {"depth_debt": deep, "three_row": three,
                 "large_binary": large_binary, "self_alias": alias}
    for name, word in all_words.items():
        need(word.valid_syntax() and word.all_columns(), name + " rejected semantic identity")
        need(not word.funded(), "no tested word supplies a funding claim")
    records = []
    domains = [
        ("depth_debt", 9, 9, (8, 1, 6, 0, 3, 7, 2, 5)),
        ("three_row", 4, 5, (4, 0, 2)),
        ("three_row", 4, 8, (7, 1, 5, 0, 3, 6)),
        ("three_row", 5, 8, (7, 1, 5, 0, 3, 6, 2)),
        ("large_binary", 3, 3, (2, 0)),
        ("self_alias", 5, 5, (4, 0, 3, 1)),
    ]
    for name, count, ambient, axes in domains:
        data = sample(count, ambient)
        frozen = json.dumps(data)
        answer, stats = execute(all_words[name], data, axes)
        need(answer == oracle(data, axes), "independent normalized-C oracle: " + name)
        need(json.dumps(data) == frozen, "source mutation")
        need(stats["max_bits"] + 1 <= stats["capacity_bits"], "capacity receipt")
        records.append({"word": name, "axes": axes, "ambient": ambient, **stats,
                        "output_sha256": sha256(json.dumps(answer).encode()).hexdigest()})
    # At depth three, five scalar divisions per unfinished context demand
    # fifteen powers of 3 on the first paid-child spine, exceeding J=14.
    depth_error = reject(lambda: execute(deep, sample(8, 8, True), tuple(range(8)),
                                        odd_exponent=len(deep.ops)), "nonexact division")
    j, n, h = len(large_binary.ops), large_binary.dimension, 2
    old_guard = 8 * (j + n + 1) * (h + 1)
    binary_error = reject(lambda: execute(large_binary, sample(2, 2, True), (0, 1),
                                          guard_override=old_guard), "nonexact division")
    phase = Word(2, 2, 0, (("unit", 0), ("scale", 0, 0, -1, 1)) + paid(2, 2))
    need(not phase.all_columns(), "absolute matrix phase absorbed into scalar")
    phase_cases = []
    for rank in (2, 4):
        count = 2 ** (rank.bit_length() - 1)
        data = sample(count, rank)
        answer, _ = execute(phase, data, tuple(range(rank)), require_identity=False)
        agrees = answer == oracle(data, tuple(range(rank)))
        need(agrees == (rank == 2), "one-column/two-column phase control")
        phase_cases.append({"rank": rank, "agrees": agrees})
    scalar = Word(2, 2, 0, (("scale", 0, 1, 0, 3),) + paid(2, 2)
                  + (("scale", 0, 3, 0, 1),))
    data = sample(2, 2)
    wrong, receipt = execute(scalar, data, (0, 1), retire_odd=False)
    expected = oracle(data, (0, 1))
    factor = receipt["D"] ** (receipt["J"] * receipt["depth"])
    need(wrong == [[(factor*a, factor*b) for a, b in row] for row in expected],
         "root scale must be completely retired")
    codec = 0
    for a, b, q in product(range(-8, 9), range(-5, 6), range(1, 10)):
        word = Word(3, 3, 2, (("scale", 4, a, b, q),))
        need(parse(encode(word)) == word, "signed unary round trip")
        codec += 1
    # Every short binary string is either rejected or canonically round trips.
    short_codes = accepted = 0
    for length in range(1, 16):
        for bits in product("01", repeat=length):
            code = "".join(bits)
            word = parse(code)
            if word is not None:
                need(encode(word) == code and word.valid_syntax(), "noncanonical accepted code")
                accepted += 1
            short_codes += 1
    result = {
        "status": "PASS_FINAL_RATIONAL_CODE_REVIEW_CHECKS",
        "source_hashes": {name: sha256((CANDIDATE / name).read_bytes()).hexdigest()
                          for name in ("PROOF.md", "word.py", "execute.py", "verify.py")},
        "records": records,
        "fixed_words": {name: {"N": word.dimension, "W": word.productive,
                              "Z": word.owned, "J": len(word.ops),
                              "D": word.constants()[0], "m": word.constants()[1]}
                        for name, word in all_words.items()},
        "signed_codec_cases": codec,
        "short_code_domain": {"lengths": [1, 15], "strings": short_codes, "accepted": accepted},
        "controls": {"omitted_depth_factor": depth_error,
                     "old_scalar_height_blind_guard": binary_error,
                     "scalar_column_phase": phase_cases,
                     "unretired_odd_scale_exact_factor": factor},
        "scope": "Logical code review, conditional scalar/tape services, no funded word or kappa claim.",
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

