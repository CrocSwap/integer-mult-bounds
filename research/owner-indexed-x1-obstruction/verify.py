#!/usr/bin/env python3
"""D-exponent-0 owner indexes cannot clear the active-feedback x1 block.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The predecessor replay and group algebra are imported unchanged.
The syllable product loop is a control. The proof is the identity in PROOF.md.
"""
from hashlib import sha256
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
QINV = (-1,)
LONG = (-1, 2, 1, 2)
SHARP_M2 = (-1, 2, 1, 1, 2, 1)
RESIDUAL = (-1, 2, 1, 1, 2, 3)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_search():
    path = ROOT / "research/coded-active-feedback/search.py"
    spec = importlib.util.spec_from_file_location("active_feedback_search_pinned", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def q_letter_count(word):
    return sum(1 for letter in word if abs(letter) == 1)


def phi(element):
    total = Fraction(0)
    for (word, degree), value in element.items():
        need(degree == (0, 0), "character left the D-exponent-0 line")
        sign = -1 if q_letter_count(word) % 2 else 1
        total += value * sign
    return total


def degree_part(element, degree):
    return {key: value for key, value in element.items() if key[1] == degree}


def syllable_count(max_syllables):
    """Independent count of alternating free-product words, Q then C1 or C3."""
    factors = ("Q", "C1", "C3")
    sizes = {"Q": 3, "C1": 1, "C3": 1}
    previous = {factor: sizes[factor] for factor in factors}
    total = 1 + sum(previous.values())
    for _length in range(2, max_syllables + 1):
        current = {}
        for factor in factors:
            current[factor] = sizes[factor] * sum(
                previous[other] for other in factors if other != factor)
            total += current[factor]
        previous = current
    return total


def normal_words(algebra, max_syllables):
    syllables = {
        "Q": ((1,), (1, 1), (-1,)),
        "C1": ((2,),),
        "C3": ((3,),),
    }
    found = {(): None}
    frontier = [()]
    while frontier:
        current = frontier
        frontier = []
        for word in current:
            if syllable_length(word) >= max_syllables:
                continue
            previous = found[word]
            for factor, choices in syllables.items():
                if factor == previous:
                    continue
                for syllable in choices:
                    produced = algebra.mul(algebra.term(word, (0, 0)),
                                           algebra.term(syllable, (0, 0)))
                    need(len(produced) == 1, "syllable product left the group")
                    (new, degree), value = next(iter(produced.items()))
                    need(degree == (0, 0) and value == 1, "syllable product was not a unit")
                    if new not in found:
                        found[new] = factor
                        frontier.append(new)
    return found


def syllable_length(word):
    count = 0
    previous = None
    for letter in word:
        factor = "Q" if abs(letter) == 1 else letter
        if factor != previous:
            count += 1
            previous = factor
    return count


def support(element):
    return {(word, degree): int(value) if value.denominator == 1 else value
            for (word, degree), value in element.items()}


def main():
    pinned = {
        "research/coded-active-feedback/search.py":
            "1383010827af29a1b0e595e2c1aa2ffad461b266ffc9f936efce1603ff9f5eb6",
        "research/coded-native-caller/gauge.py":
            "390391d291353741c89daea999d483660ca185987ed96a15b82576280c487cad",
        "certificates/selected-result.json":
            "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa",
    }
    for name, digest in pinned.items():
        need(sha256((ROOT / name).read_bytes()).hexdigest() == digest, "changed pin " + name)
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    need(selected["kappa"] == "781451/250000000", "selected frontier value moved")

    search = load_search()
    algebra = search.algebra()
    q, c1, c3 = algebra.gen(1), algebra.gen(2), algebra.gen(3)
    qinv, d1, d3 = algebra.inv(q), algebra.D(0), algebra.D(1)
    observed, _targets, rows = search.replay(algebra, algebra.one, algebra.mul(c1, q, q))
    need(len(observed) == 39, "saved-bank count moved")
    left = [row for label, row in observed if label.startswith("left:")]
    need(left == rows, "final rows are not the left endpoint banks")
    stored = tuple(tuple(tuple(sorted(entry.items())) for entry in row) for row in rows)

    blank = {}
    bank0 = [
        algebra.add(algebra.term((-1, 2), (1, 0)), algebra.term((1, 1, 2), (1, 0))),
        algebra.term((-1,), (1, 0)),
        algebra.term((1, 1, 2), (1, 0), -1),
        blank,
    ]
    bank1 = [blank, algebra.term((2, 1), (1, 0)), blank, blank]
    const = algebra.add(algebra.term(QINV, (0, 0), -1), algebra.term(LONG, (0, 0)))
    mono = algebra.term((-1, 3), (1, 1))
    bank2 = [
        algebra.term(QINV, (1, 0)),
        algebra.add(algebra.term((-1, 2, 1), (1, 0)),
                    algebra.term((-1, 2, 1, 1), (1, 0), -1)),
        algebra.add(algebra.mul(const, d1), mono),
        blank,
    ]
    bank3 = [
        algebra.term((3, -1, 2), (1, 1)),
        algebra.term((3,), (1, 1)),
        algebra.add(algebra.term((), (1, 1), -1),
                    algebra.term((3, -1, 2), (1, 1), -1),
                    algebra.term((3, 2), (1, 1))),
        algebra.term((3, 1), (1, 1)),
    ]
    need(rows == [bank0, bank1, bank2, bank3], "final banks moved")
    need(len(bank2[2]) == 3, "published x1 block lost a monomial")
    need(bank2[2] != blank, "published x1 block was already zero")

    one_plus_q = algebra.add(algebra.one, q)
    x = algebra.mul(algebra.mul(q, q), one_plus_q, c1, q)
    need(algebra.mul(rows[0][0], algebra.inv(rows[2][0])) == x, "x is not Q^2(I+Q)C1 Q")
    need(algebra.add(qinv, algebra.mul(q, q)) == algebra.mul(algebra.mul(q, q), one_plus_q),
         "Q^{-1}+Q^2 did not factor")
    need(rows[0][0] == algebra.mul(x, rows[2][0]), "bank0 x0 is not x A")
    factored_const = algebra.mul(qinv, algebra.add(algebra.mul(c1, q, c1), algebra.neg(algebra.one)))
    need(factored_const == const, "const factorisation moved")
    g = algebra.mul(qinv, c3)
    ginv = algebra.mul(c3, q)
    need(g == algebra.term((-1, 3), (0, 0)), "Q^{-1} C3 normal form moved")
    need(algebra.mul(g, ginv) == algebra.one and algebra.mul(ginv, g) == algebra.one,
         "Q^{-1} C3 is not a unit")
    need(algebra.mul(c1, c1) == algebra.one, "C1 is not an involution")
    bank3_inverse = algebra.inv(rows[3][0])
    need(algebra.mul(bank3_inverse, rows[3][0]) == algebra.one
         and algebra.mul(rows[3][0], bank3_inverse) == algebra.one,
         "bank3 x0 monomial is not a unit")
    a_inverse = algebra.inv(rows[2][0])
    need(algebra.mul(a_inverse, rows[2][0]) == algebra.one
         and algebra.mul(rows[2][0], a_inverse) == algebra.one,
         "A is not a unit")

    linear = algebra.add(rows[0][2], algebra.neg(algebra.mul(x, rows[2][2])))
    need(linear == algebra.add(algebra.mul(algebra.neg(c1), d1), algebra.neg(algebra.mul(x, mono))),
         "x1 linear coefficient moved")
    y0_constant = algebra.add(rows[2][1], algebra.mul(const, rows[1][1]))
    y0_linear = algebra.add(rows[0][1], algebra.neg(algebra.mul(c1, rows[1][1])),
                            algebra.neg(algebra.mul(x, rows[2][1])))
    need(y0_constant == blank and y0_linear == blank, "y0 identity does not cover every m0")

    # Character. Reducer steps used by the homomorphism argument.
    need(search.reduce_word((1, 1, 1, 1)) == (), "Q^4 did not reduce to I")
    need(search.reduce_word((2, 2)) == () and search.reduce_word((3, 3)) == (),
         "a code square did not reduce to I")
    cascade = (1, 1, 3, 3, -1)
    need(search.reduce_word(cascade) == (1,), "exposed Q run did not collapse")
    need(q_letter_count(cascade) % 2 == q_letter_count(search.reduce_word(cascade)) % 2,
         "Q-run collapse changed character parity")
    for exponent in range(8):
        raw = (1,) * exponent
        reduced = search.reduce_word(raw)
        need(q_letter_count(raw) % 2 == q_letter_count(reduced) % 2,
             "Q normal form changed character parity")
    need(phi(one_plus_q) == 0, "I+Q was not in the character kernel")
    need(phi(algebra.mul(qinv, c1)) == -1, "Q^{-1} C1 lost its character")
    need(algebra.mul(qinv, c1) == algebra.term((-1, 2), (0, 0)), "Q^{-1} C1 normal form moved")

    # Finite control: every normal word of at most three syllables, counted
    # independently of the reducer. This does not enumerate the theorem.
    words = normal_words(algebra, 3)
    need(len(words) == syllable_count(3) == 64, "three-syllable normal forms are incomplete")
    for left in words:
        for right in words:
            product = algebra.mul(algebra.term(left, (0, 0)), algebra.term(right, (0, 0)))
            need(phi(product) == phi(algebra.term(left, (0, 0))) * phi(algebra.term(right, (0, 0))),
                 "character failed on a three-syllable product")
            need(phi(algebra.mul(algebra.term(left, (0, 0)), one_plus_q)) == 0,
                 "a three-syllable word met the forbidden right-hand side")

    samples = [
        {},
        algebra.one,
        algebra.term((2, 3, 1, 1), (0, 0), 1),
        algebra.add(algebra.term((3,), (0, 0), 2), algebra.term((1, 2, -1), (0, 0), -3)),
        algebra.mul(algebra.neg(qinv), c1),
        algebra.term((2, 1, 3, 1, 1, 2, -1, 3), (0, 0), 5),
    ]
    for m0 in samples:
        m2 = algebra.add(algebra.one, algebra.neg(algebra.mul(m0, x)))
        m1 = algebra.add(const, algebra.neg(algebra.mul(m0, c1)))
        image = [algebra.add(algebra.mul(m0, rows[0][column]),
                             algebra.mul(m1, rows[1][column]),
                             algebra.mul(m2, rows[2][column]))
                 for column in range(4)]
        need(image[0] == rows[2][0] and image[1] == blank and image[3] == blank,
             "sample index failed to keep x0 and clear y0 and y1")
        d1_line = algebra.mul(algebra.add(const, algebra.neg(algebra.mul(m0, c1))), d1)
        d3_line = algebra.mul(m2, mono)
        need(image[2] == algebra.add(d1_line, d3_line), "sample x1 left the proved shape")
        need(d3_line, "sample D1 D3 summand vanished")
        need(phi(algebra.mul(m0, algebra.mul(algebra.mul(q, q), one_plus_q))) == 0,
             "sample met the forbidden equation in the character")

    # Unique index that clears the D1 line. It still keeps y0 zero.
    sharp_m0 = algebra.mul(const, c1)
    need(support(sharp_m0) == {((-1, 2), (0, 0)): -1, ((-1, 2, 1), (0, 0)): 1},
         "sharp m0 support moved")
    left = algebra.mul(algebra.neg(qinv), c1)
    right_a = algebra.mul(qinv, c1, q)
    right_b = algebra.mul(q, q, c1, q)
    term1 = algebra.mul(left, right_a)
    term2 = algebra.mul(left, right_b)
    term3 = algebra.mul(right_a, right_a)
    term4 = algebra.mul(right_a, right_b)
    need(term3 == algebra.one, "third sharp product is not I")
    need(algebra.add(term1, term4) == blank, "first and fourth sharp products did not cancel")
    sharp_m2 = algebra.add(algebra.one, algebra.neg(algebra.add(term1, term2, term3, term4)))
    need(sharp_m2 == algebra.add(algebra.one, algebra.neg(algebra.mul(sharp_m0, x))),
         "four-term expansion is not m0 x")
    need(sharp_m2 == algebra.term(SHARP_M2, (0, 0)), "sharp m2 is not one monomial")
    sharp_m1 = algebra.add(const, algebra.neg(algebra.mul(sharp_m0, c1)))
    need(sharp_m1 == blank, "clearing the D1 line reopened the y0 multiplier")
    fresh = [algebra.add(algebra.mul(sharp_m0, rows[0][column]),
                         algebra.mul(sharp_m2, rows[2][column]))
             for column in range(4)]
    residual = algebra.term(RESIDUAL, (1, 1))
    need(fresh[0] == rows[2][0] and fresh[1] == blank and fresh[3] == blank,
         "sharp image did not keep x0 and clear y0 and y1")
    need(fresh[2] == residual and fresh[2] != blank, "sharp x1 is not the forced monomial")
    need(fresh[2] != rows[2][2], "sharp index failed to change the three-term block")
    need(degree_part(fresh[2], (1, 0)) == blank, "sharp index left a D1 term")
    need(len(fresh[2]) == 1, "sharp residual is not a single monomial")

    # Failure controls. Reopening a hypothesis, or dropping a monomial, is not a solution.
    constant = [algebra.add(rows[2][column], algebra.mul(const, rows[1][column])) for column in range(4)]
    need(constant[0] == rows[2][0] and constant[1] == blank and constant[2] == rows[2][2],
         "constant index no longer reproduces the unpaid three-term block")
    spoiled = [algebra.add(rows[2][column], rows[3][column]) for column in range(4)]
    need(spoiled[0] != rows[2][0], "a nonzero bank-3 coefficient kept x0")
    partial = {key: value for key, value in sharp_m0.items() if key[0] != (-1, 2)}
    partial_image = algebra.add(algebra.mul(partial, rows[0][2]), algebra.mul(sharp_m2, rows[2][2]))
    need(degree_part(partial_image, (1, 0)), "dropping one sharp monomial still cleared the D1 line")
    need(tuple(stored) == tuple(tuple(tuple(sorted(entry.items())) for entry in row) for row in rows),
         "stored endpoint banks were overwritten")

    print("PASS_OWNER_INDEXED_X1_OBSTRUCTION")
    print("evidence_class", "proof")
    print("residual", "Q^{-1} C1 Q^2 C1 C3 D1 D3")
    print("x1_terms_at_sharp_index", len(fresh[2]))
    print("new_kappa", None)


if __name__ == "__main__":
    main()
