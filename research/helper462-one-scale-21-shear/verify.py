#!/usr/bin/env python3
"""A 21-shear one-scale zero-swap word for the pinned helper-462 matcher.

The certificate is the exact rational product of the frozen words. Twenty-one
is an upper bound from a heuristic search, not a minimum. No new kappa.
"""
from fractions import Fraction
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
RESULT = ROOT / "research/bit-completed-backend-api/science/RESULT.json"
N = 8
SCALE = Fraction(-16)
PRIMARY_SHEARS = 21
ROW_SHEARS = (21, 21, 24, 21, 21, 21, 21, 23)
TOKEN = "PASS_HELPER462_ONE_SCALE_21_SHEAR"


def need(condition, message):
    """Fail closed. A plain assert would vanish under python -O."""
    if not condition:
        raise SystemExit("FAIL: " + message)


def identity():
    return [[Fraction(int(i == j)) for j in range(N)] for i in range(N)]


def matmul(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(N)) for j in range(N)]
            for i in range(N)]


def determinant(matrix):
    work = [row[:] for row in matrix]
    value = Fraction(1)
    for column in range(N):
        pivot = next((row for row in range(column, N) if work[row][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            value = -value
        value *= work[column][column]
        for row in range(column + 1, N):
            factor = work[row][column] / work[column][column]
            for index in range(column, N):
                work[row][index] -= factor * work[column][index]
    return value


def parse_letter(raw):
    """Return ("add", target, source, coefficient) or ("scale", target, coefficient)."""
    need(isinstance(raw, dict), "a letter must be an object")
    kind = raw.get("op")
    target = raw.get("target")
    need(isinstance(target, int) and not isinstance(target, bool) and 0 <= target < N,
         "a letter target must be a row index")
    need(isinstance(raw.get("coefficient"), str), "a coefficient must be a string")
    coefficient = Fraction(raw["coefficient"])
    if kind == "add":
        source = raw.get("source")
        need(isinstance(source, int) and not isinstance(source, bool) and 0 <= source < N,
             "a shear source must be a row index")
        need(source != target, "a shear must be off-diagonal")
        need(coefficient != 0, "a shear coefficient must be nonzero")
        need(set(raw) == {"op", "target", "source", "coefficient"}, "unexpected shear key")
        return ("add", target, source, coefficient)
    need(kind == "scale", "the alphabet here is shears and scales; swaps are excluded")
    need(coefficient not in (0, 1), "a scale must be a non-identity coefficient")
    need(set(raw) == {"op", "target", "coefficient"}, "unexpected scale key")
    return ("scale", target, coefficient)


def apply_rows(letters):
    """Apply the letters first to last as row operations on the identity."""
    matrix = identity()
    for letter in letters:
        if letter[0] == "add":
            _, target, source, coefficient = letter
            matrix[target] = [matrix[target][c] + coefficient * matrix[source][c]
                              for c in range(N)]
        else:
            _, target, coefficient = letter
            matrix[target] = [coefficient * entry for entry in matrix[target]]
    return matrix


def elementary(letter):
    matrix = identity()
    if letter[0] == "add":
        matrix[letter[1]][letter[2]] = letter[3]
    else:
        matrix[letter[1]][letter[1]] = letter[2]
    return matrix


def multiply_out(letters):
    """Independent route: the product E_last ... E_first of elementary matrices."""
    matrix = identity()
    for letter in letters:
        matrix = matmul(elementary(letter), matrix)
    return matrix


def check_word(raw_letters, matcher, scale_row, shear_count):
    """One-scale zero-swap word: shear_count shears, then the scale -16 on scale_row."""
    letters = [parse_letter(raw) for raw in raw_letters]
    need(len(letters) == shear_count + 1, "wrong letter count for scale row %d" % scale_row)
    shears, scale = letters[:-1], letters[-1]
    need(all(letter[0] == "add" for letter in shears), "the scale must be the last letter")
    need(scale == ("scale", scale_row, SCALE), "the unique scale must be -16 on its row")
    need(apply_rows(letters) == matcher, "row operations miss the matcher")
    need(multiply_out(letters) == matcher, "elementary-matrix product misses the matcher")
    need(determinant(apply_rows(shears)) == 1, "the shear part must have determinant 1")
    for first, second in zip(shears, shears[1:]):
        need(first[1:3] != second[1:3], "adjacent shears on one position would merge")
    return letters


def failure_controls(letters, matcher):
    """Every single-letter deletion and every mutated coefficient must miss."""
    count = 0
    for index, letter in enumerate(letters):
        dropped = letters[:index] + letters[index + 1:]
        need(apply_rows(dropped) != matcher, "dropping letter %d still matches" % index)
        mutated = letters[:]
        mutated[index] = letter[:-1] + (letter[-1] + 1,)
        need(apply_rows(mutated) != matcher, "mutating letter %d still matches" % index)
        count += 2
    return count


def main():
    matcher_raw = json.loads(RESULT.read_text())["matcher"]
    need(len(matcher_raw) == N and all(len(row) == N for row in matcher_raw),
         "the pinned matcher must be 8 by 8")
    matcher = [[Fraction(entry) for entry in row] for row in matcher_raw]
    need(determinant(matcher) == SCALE, "the matcher determinant must be -16")

    word = json.loads((PACKAGE / "WORD.json").read_text())
    need(word["letter_counts"] == {"swap": 0, "scale": 1, "add": PRIMARY_SHEARS},
         "WORD.json letter counts")
    need(word["scale_row"] == 0 and Fraction(word["scale_coefficient"]) == SCALE,
         "WORD.json scale header")
    primary = check_word(word["letters"], matcher, 0, PRIMARY_SHEARS)
    controls = failure_controls(primary, matcher)
    denominators = sorted({letter[3].denominator for letter in primary[:-1]})
    need(denominators == [1, 2, 4, 8, 16], "primary shear denominators")
    need(PRIMARY_SHEARS < 26, "the word must be shorter than the 26 shears of PR #7054")

    rows = json.loads((PACKAGE / "ROW_WORDS.json").read_text())
    need(tuple(rows["shear_counts"]) == ROW_SHEARS, "ROW_WORDS.json shear counts")
    need(len(rows["words"]) == N, "ROW_WORDS.json must hold one word per scale row")
    for scale_row, entry in enumerate(rows["words"]):
        need(entry["scale_row"] == scale_row, "ROW_WORDS.json row order")
        letters = check_word(entry["letters"], matcher, scale_row, ROW_SHEARS[scale_row])
        controls += failure_controls(letters, matcher)
    need(rows["words"][0]["letters"] == word["letters"], "row 0 must equal WORD.json")

    print(TOKEN)
    print(json.dumps({
        "matcher_determinant": str(SCALE),
        "primary_word": {"swaps": 0, "scales": 1, "shears": PRIMARY_SHEARS,
                         "scale_row": 0, "shear_denominators": denominators},
        "shears_by_scale_row": list(ROW_SHEARS),
        "failure_controls": controls,
        "minimum_claimed": False,
        "new_kappa": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
