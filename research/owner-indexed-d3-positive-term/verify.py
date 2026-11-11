#!/usr/bin/env python3
"""No D-exponent (0,1) correction clears the sharp x1 column.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The predecessor replay and group algebra are imported unchanged.
The syllable-length-4 replay is a control. The proof is the identity in PROOF.md.
"""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
QINV = (-1,)
LONG = (-1, 2, 1, 2)
SHARP_M2 = (-1, 2, 1, 1, 2, 1)
RESIDUAL = (-1, 2, 1, 1, 2, 3)
STAR = (-1, 2, 1, 1, 2, 3, 2)
U2_WORDS = (
    (-1, 2, 1, 1, 2, 3, 2, -1, 2, 1),
    (-1, 2, 1, 1, 2, 3, 2, 1, 1, 2, 1),
)
LEFTOVER = (
    (-1, 2, 1, 1, 2, 3, 2, -1, 2, -1, 3, 1),
    (-1, 2, 1, 1, 2, 3, 2, 1, 1, 2, -1, 3, 1),
)
DELTA_PLUS = (
    ((2,), (1, 1), -1),
    ((-1, 2, -1, 3, 1), (1, 2), -1),
    ((1, 1, 2, -1, 3, 1), (1, 2), -1),
)
DELTA_MINUS = (
    ((2,), (1, -1), -1),
    ((-1, 2, 1, 3, -1), (1, 0), -1),
    ((1, 1, 2, 1, 3, -1), (1, 0), -1),
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_search():
    path = ROOT / "research/coded-active-feedback/search.py"
    spec = importlib.util.spec_from_file_location("active_feedback_search_pinned", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def support(element):
    return {(word, degree): int(value) if value.denominator == 1 else value
            for (word, degree), value in element.items()}


def degree_part(element, degree):
    return {key: value for key, value in element.items() if key[1] == degree}


def degrees(element):
    return {degree for (_word, degree) in element}


def literal(algebra, rows):
    total = {}
    for word, degree, coefficient in rows:
        total = algebra.add(total, algebra.term(word, degree, coefficient))
    return total


def syllable_count(max_syllables):
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


def syllable_length(word):
    count = 0
    previous = None
    for letter in word:
        factor = "Q" if abs(letter) == 1 else letter
        if factor != previous:
            count += 1
            previous = factor
    return count


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


def final_q_exponent(word):
    index = len(word)
    while index and abs(word[index - 1]) == 1:
        index -= 1
    tail = word[index:]
    if tail == ():
        return 0, word
    if tail == (1,):
        return 1, word[:index]
    if tail == (1, 1):
        return 2, word[:index]
    if tail == (-1,):
        return 3, word[:index]
    raise ValueError("normal word has a noncanonical Q tail")


def d_power(algebra, k):
    if k == 0:
        return algebra.one
    step = algebra.D(1) if k > 0 else algebra.inv(algebra.D(1))
    out = algebra.one
    for _ in range(abs(k)):
        out = algebra.mul(out, step)
    return out


def main():
    pinned = {
        "research/coded-active-feedback/search.py":
            "1383010827af29a1b0e595e2c1aa2ffad461b266ffc9f936efce1603ff9f5eb6",
        "research/coded-native-caller/gauge.py":
            "390391d291353741c89daea999d483660ca185987ed96a15b82576280c487cad",
        "certificates/selected-result.json":
            "154c3d30455d778fd3343b6b4851f0fa4665f0f7625b0adb3675e2bafbbf6bf1",
    }
    for name, digest in pinned.items():
        need(sha256((ROOT / name).read_bytes()).hexdigest() == digest, "changed pin " + name)
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    need(selected["kappa"] == "363005817/100000000000", "selected frontier value moved")

    search = load_search()
    algebra = search.algebra()
    q, c1, c3 = algebra.gen(1), algebra.gen(2), algebra.gen(3)
    qinv, d1, d3 = algebra.inv(q), algebra.D(0), algebra.D(1)
    q2, q3 = algebra.mul(q, q), algebra.mul(q, q, q)
    blank = {}
    one_plus_q = algebra.add(algebra.one, q)
    sigma = algebra.add(algebra.one, algebra.neg(q), q2, algebra.neg(q3))
    observed, _targets, rows = search.replay(algebra, algebra.one, algebra.mul(c1, q, q))
    need(len(observed) == 39, "saved-bank count moved")
    left = [row for label, row in observed if label.startswith("left:")]
    need(left == rows, "final rows are not the left endpoint banks")
    stored = tuple(tuple(tuple(sorted(entry.items())) for entry in row) for row in rows)

    raw = [
        [
            algebra.add(algebra.term((-1, 2), (1, 0)), algebra.term((1, 1, 2), (1, 0))),
            algebra.term((-1,), (1, 0)),
            algebra.term((1, 1, 2), (1, 0), -1),
            blank,
        ],
        [
            blank,
            algebra.term((2, 1), (1, 0)),
            blank,
            blank,
        ],
        [
            algebra.term((-1,), (1, 0)),
            algebra.add(algebra.term((-1, 2, 1), (1, 0)),
                        algebra.term((-1, 2, 1, 1), (1, 0), -1)),
            algebra.add(algebra.term((-1,), (1, 0), -1),
                        algebra.term((-1, 2, 1, 2), (1, 0)),
                        algebra.term((-1, 3), (1, 1))),
            blank,
        ],
        [
            algebra.term((3, -1, 2), (1, 1)),
            algebra.term((3,), (1, 1)),
            algebra.add(algebra.term((), (1, 1), -1),
                        algebra.term((3, -1, 2), (1, 1), -1),
                        algebra.term((3, 2), (1, 1))),
            algebra.term((3, 1), (1, 1)),
        ],
    ]
    need(rows == raw, "replayed final banks moved")
    for bank in (0, 1, 2):
        need(rows[bank][3] == blank, "a C3-free bank gained a y1 column")
    need(rows[1][0] == blank and rows[1][2] == blank, "bank 1 gained an x column")

    const = algebra.add(algebra.term(QINV, (0, 0), -1), algebra.term(LONG, (0, 0)))
    x = algebra.mul(q2, one_plus_q, c1, q)
    sharp_m0 = algebra.mul(const, c1)
    sharp_m2 = algebra.term(SHARP_M2, (0, 0))
    need(sharp_m2 == algebra.add(algebra.one, algebra.neg(algebra.mul(sharp_m0, x))),
         "sharp m2 is not the closed monomial")
    need(support(sharp_m0) == {((-1, 2), (0, 0)): -1, ((-1, 2, 1), (0, 0)): 1},
         "sharp m0 support moved")
    sharp_m1 = algebra.add(const, algebra.neg(algebra.mul(sharp_m0, c1)))
    need(sharp_m1 == blank, "sharp index reopened y0")
    sharp = [algebra.add(algebra.mul(sharp_m0, rows[0][column]),
                         algebra.mul(sharp_m2, rows[2][column]))
             for column in range(4)]
    residual = algebra.term(RESIDUAL, (1, 1))
    anchor = algebra.mul(d1, qinv)
    need(anchor == algebra.term(QINV, (1, 0)), "D1 does not commute with Q^{-1}")
    need(sharp[0] == anchor and sharp[1] == blank and sharp[3] == blank,
         "sharp image did not keep x0 and clear y0 and y1")
    need(sharp[2] == residual, "sharp x1 is not the residual monomial")
    rho = algebra.term(RESIDUAL, (0, 0))
    star = algebra.term(STAR, (0, 0))
    need(algebra.mul(rho, c1) == star and algebra.mul(star, c1) == rho,
         "the residual monomial is not a right C1 translate")
    q_sum = algebra.add(qinv, q2)
    need(q_sum == algebra.mul(q2, one_plus_q), "Q^{-1}+Q^2 left Q^2(I+Q)")
    need(x == algebra.mul(q_sum, c1, q), "x left the factored form")
    need(algebra.mul(sigma, one_plus_q) == blank and len(sigma) == 4,
         "the length-4 anti-invariant moved")
    need(algebra.mul(sigma, x) == blank, "the right kernel of x missed sigma")

    def transported(k):
        power = d_power(algebra, k)
        return [[algebra.mul(power, rows[bank][column]) for column in range(4)]
                for bank in range(4)]

    positive = transported(1)
    for bank in range(4):
        for column in range(4):
            shifted = {}
            for (word, degree), value in rows[bank][column].items():
                # C3-free columns keep their words. The full transport is checked below.
                if 3 not in word and -3 not in word:
                    shifted[(word, (degree[0], degree[1] + 1))] = value
            if all(3 not in word and -3 not in word for (word, _degree) in rows[bank][column]):
                need(positive[bank][column] == shifted, "a C3-free column changed its word at D3")
    need(positive[0][2] == algebra.term((1, 1, 2), (1, 1), -1), "bank 0 x1 transport moved")
    need(positive[1][2] == blank, "bank 1 x1 transport became nonempty")
    need(positive[2][2] == algebra.add(
        algebra.term((-1,), (1, 1), -1),
        algebra.term((-1, 2, 1, 2), (1, 1)),
        algebra.term((1, 1, 3, 1), (1, 2))), "bank 2 x1 transport moved")
    need(len(positive[3][0]) == 1 and degrees(positive[3][0]) == {(1, 2)},
         "bank 3 x0 gate left degree (1,2)")
    need(len(positive[3][1]) == 1 and degrees(positive[3][1]) == {(1, 2)},
         "bank 3 y0 gate left degree (1,2)")
    for gate in (positive[2][0], positive[1][1], positive[3][0], positive[3][1]):
        inverse = algebra.inv(gate)
        need(algebra.mul(gate, inverse) == algebra.one and algebra.mul(inverse, gate) == algebra.one,
             "a boundary gate is not a monomial unit")
    need(algebra.mul(d3, x) == algebra.mul(x, d3), "x failed to commute with D3")
    need(algebra.mul(d3, c1) == algebra.mul(c1, d3), "C1 failed to commute with D3")
    need(algebra.add(positive[0][0], algebra.neg(algebra.mul(x, positive[2][0]))) == blank,
         "x0 transport identity failed")
    y_identity = algebra.add(positive[0][1],
                             algebra.neg(algebra.mul(c1, positive[1][1])),
                             algebra.neg(algebra.mul(x, positive[2][1])))
    need(y_identity == blank, "y0 transport identity failed")
    delta = algebra.add(positive[0][2], algebra.neg(algebra.mul(x, positive[2][2])))
    need(delta == literal(algebra, DELTA_PLUS), "exponent-(0,1) defect moved")
    unit = algebra.mul(qinv, c3, q)
    factored = algebra.mul(algebra.neg(q_sum), c1, unit)
    need(degree_part(delta, (1, 2)) == algebra.mul(factored, algebra.term((), (1, 2))),
         "degree-(1,2) defect left the factored form")
    need(degree_part(delta, (1, 1)) == algebra.term((2,), (1, 1), -1),
         "degree-(1,1) defect is not -C1")
    need(algebra.mul(unit, algebra.inv(unit)) == algebra.one, "the degree-(1,2) right factor is not a unit")

    def boundary_image(coefficient, tables):
        u1 = algebra.mul(algebra.neg(coefficient), c1)
        u2 = algebra.mul(algebra.neg(coefficient), x)
        image = []
        for column in range(4):
            image.append(algebra.add(
                sharp[column],
                algebra.mul(coefficient, tables[0][column]),
                algebra.mul(u1, tables[1][column]),
                algebra.mul(u2, tables[2][column])))
        return image, u1, u2

    samples = [
        blank,
        algebra.one,
        c1,
        c3,
        q,
        sigma,
        star,
        algebra.mul(qinv, c1),
        algebra.add(c3, q2, algebra.term((2, 3), (0, 0), -2)),
        algebra.add(star, sigma),
        algebra.term((2, 3, 1, 1, 2), (0, 0), 5),
    ]
    for coefficient in samples:
        need(degrees(coefficient) <= {(0, 0)}, "sample left the D-exponent-0 line")
        image, u1, u2 = boundary_image(coefficient, positive)
        need(image[0] == anchor and image[1] == blank and image[3] == blank,
             "boundary family failed to keep x0 and clear y0 and y1")
        need(image[2] == algebra.add(residual, algebra.mul(coefficient, delta)),
             "boundary x1 is not the residual plus u0 times the defect")
        line = degree_part(image[2], (1, 1))
        expected_line = algebra.add(residual, algebra.mul(coefficient, algebra.term((2,), (1, 1), -1)))
        need(line == expected_line, "degree-(1,1) line is not rho minus u0 C1")
        need(image[2] != blank, "a sample coefficient cleared x1")
        need((line == blank) == (coefficient == star),
             "degree (1,1) vanished for a coefficient other than the near-miss")
        high = degree_part(image[2], (1, 2))
        kills_high = algebra.mul(coefficient, one_plus_q) == blank
        need((high == blank) == kills_high, "degree (1,2) vanished outside the kernel of I+Q")

    image_star, u1_star, u2_star = boundary_image(star, positive)
    need(support(u1_star) == {(RESIDUAL, (0, 0)): -1}, "near-miss u1 is not -rho")
    need(support(u2_star) == {(word, (0, 0)): -1 for word in U2_WORDS},
         "near-miss u2 is not the two stated monomials")
    need(len(u2_star) == 2 and u1_star != blank and star != blank, "near-miss lost a bank")
    need(image_star[2] == literal(algebra, tuple((word, (1, 2), -1) for word in LEFTOVER)),
         "near-miss x1 is not the two degree-(1,2) monomials")
    need(degree_part(image_star[2], (1, 1)) == blank and len(image_star[2]) == 2,
         "near-miss did not clear exactly the residual degree")
    need(algebra.mul(star, one_plus_q) != blank, "the near-miss was treated as anti-invariant")

    image_sigma, u1_sigma, u2_sigma = boundary_image(sigma, positive)
    need(u2_sigma == blank and len(sigma) == 4 and len(u1_sigma) == 4,
         "sigma is not a two-bank correction with eight multiplier monomials")
    need(degree_part(image_sigma[2], (1, 2)) == blank, "sigma failed to kill degree (1,2)")
    need(len(image_sigma[2]) == 5 and degree_part(image_sigma[2], (1, 1)) == image_sigma[2],
         "sigma image is not five monomials at degree (1,1)")
    need(image_sigma[2].get((RESIDUAL, (1, 1))) == 1, "sigma cancelled the residual monomial")

    # One nonzero bank cannot keep the boundary. This is the exponent-(0,1) case of the #7052 gate.
    for bank in range(4):
        only = [algebra.add(sharp[column], positive[bank][column]) for column in range(4)]
        need(only[0] != anchor or only[1] != blank, "one bank of D3 kept the boundary")

    # Every other nonzero single power misses degree (1,1), for arbitrary coefficients.
    stray = (c3, q, c1, algebra.add(c1, q))
    for k in (-4, -3, -2, -1, 0, 1, 2, 3, 4, 5):
        tables = positive if k == 1 else transported(k)
        x1_degrees = set()
        for bank in range(4):
            x1_degrees |= degrees(tables[bank][2])
        if k in (0, 1):
            need((1, 1) in x1_degrees, "power " + str(k) + " lost the residual degree")
        else:
            need((1, 1) not in x1_degrees, "power " + str(k) + " met the residual degree")
        arbitrary = []
        for column in range(4):
            arbitrary.append(algebra.add(
                sharp[column],
                *(algebra.mul(stray[bank], tables[bank][column]) for bank in range(4))))
        if k not in (0, 1):
            need(degree_part(arbitrary[2], (1, 1)) == residual,
                 "an arbitrary coefficient changed the residual degree")
        if k != 0:
            need(degrees(tables[0][0]) == {(1, k)} and degrees(tables[2][0]) == {(1, k)},
                 "C3-free x0 degree moved")
            need(degrees(tables[3][0]) == {(1, 1 + k)} and len(tables[3][0]) == 1,
                 "bank 3 x0 stopped being one monomial")
            need(algebra.add(tables[0][0], algebra.neg(algebra.mul(x, tables[2][0]))) == blank,
                 "the x0 identity failed at another power")
            y_again = algebra.add(tables[0][1],
                                  algebra.neg(algebra.mul(c1, tables[1][1])),
                                  algebra.neg(algebra.mul(x, tables[2][1])))
            need(y_again == blank, "the y0 identity failed at another power")
            other = algebra.add(tables[0][2], algebra.neg(algebra.mul(x, tables[2][2])))
            need(degree_part(other, (1, k)) == algebra.term((2,), (1, k), -1),
                 "the C3-free defect is not -C1")
            if k != 1:
                need((1, 1) not in degrees(other), "a non-unit power put -C1 on the residual degree")

    # Exponent (0,-1) remains the published three-term defect with no degree-(1,1) term.
    inverse_tables = transported(-1)
    inverse_delta = algebra.add(inverse_tables[0][2], algebra.neg(algebra.mul(x, inverse_tables[2][2])))
    need(inverse_delta == literal(algebra, DELTA_MINUS), "the published (0,-1) defect moved")
    need((1, 1) not in degrees(inverse_delta), "the (0,-1) defect met the residual degree")

    # Exponent (0,2) cannot repair the near-miss inside the boundary family.
    second = transported(2)
    delta2 = algebra.add(second[0][2], algebra.neg(algebra.mul(x, second[2][2])))
    unit2 = algebra.mul(q2, c3, q2)
    factored2 = algebra.mul(algebra.neg(q_sum), c1, unit2)
    need(algebra.mul(unit2, algebra.inv(unit2)) == algebra.one, "the degree-(1,3) factor is not a unit")
    need(degree_part(delta2, (1, 2)) == algebra.term((2,), (1, 2), -1),
         "the exponent-2 defect lost -C1 at degree (1,2)")
    need(degree_part(delta2, (1, 3)) == algebra.mul(factored2, algebra.term((), (1, 3))),
         "the exponent-2 defect left the factored form")
    leftover = image_star[2]
    need(len(leftover) == 2 and degrees(leftover) == {(1, 2)}, "leftover support moved")
    for coefficient in samples:
        repair = algebra.mul(coefficient, delta2)
        total = algebra.add(leftover, repair)
        need(total != blank, "a boundary-preserving exponent-2 coefficient repaired the near-miss")
        if algebra.mul(coefficient, one_plus_q) == blank and coefficient:
            need(len(coefficient) % 4 == 0, "a nonzero anti-invariant had support outside 4Z")
            need(degree_part(repair, (1, 3)) == blank, "an anti-invariant left degree (1,3)")
            need(len(degree_part(repair, (1, 2))) == len(coefficient),
                 "right multiplication by C1 changed support size")

    # Syllable control for the free Q action. Not a census of u0.
    words = normal_words(algebra, 4)
    need(len(words) == syllable_count(4) == 192, "four-syllable normal forms are incomplete")
    syllables = ((1,), (1, 1), (-1,), (2,), (3,))
    for word in words:
        need(search.reduce_word(word) == word, "generated word was not normal")
        exponent, prefix = final_q_exponent(word)
        orbit = []
        for step in range(4):
            powered = algebra.mul(algebra.term(word, (0, 0)), algebra.term((1,) * step, (0, 0))
                                  if step else algebra.one)
            ((new, degree), value), = powered.items()
            need(degree == (0, 0) and value == 1, "a Q power left the degree-0 group")
            orbit.append(new)
        need(len(set(orbit)) == 4, "a right Q orbit collapsed")
        orbit_element = algebra.mul(algebra.term(word, (0, 0)), sigma)
        need(len(orbit_element) == 4 and algebra.mul(orbit_element, one_plus_q) == blank
             and algebra.mul(orbit_element, q_sum) == blank,
             "an orbit element left the kernel of I+Q")
        for syllable in syllables:
            need(search.reduce_word(search.reduce_word(word) + syllable)
                 == search.reduce_word(word + syllable),
                 "reducer fold failed on a four-syllable word")
            if abs(syllable[0]) == 1:
                power = {(1,): 1, (1, 1): 2, (-1,): 3}[syllable]
                shifted = algebra.mul(algebra.term(word, (0, 0)), algebra.term(syllable, (0, 0)))
                ((new, degree), value), = shifted.items()
                new_exponent, new_prefix = final_q_exponent(new)
                need(degree == (0, 0) and value == 1 and new_prefix == prefix
                     and new_exponent == (exponent + power) % 4,
                     "Q power did not act on the final exponent")
        twice = algebra.mul(algebra.term(word, (0, 0)), c1, c1)
        need(twice == algebra.term(word, (0, 0)), "C1 failed to be an involution")

    need(tuple(stored) == tuple(tuple(tuple(sorted(entry.items())) for entry in row) for row in rows),
         "stored endpoint banks were overwritten")
    need(selected["kappa"] == "363005817/100000000000", "selected frontier value moved during the check")

    print("PASS_OWNER_INDEXED_D3_POSITIVE_TERM")
    print("evidence_class", "proof")
    print("boundary_family", "u1=-u0*C1, u2=-u0*x, u3=0")
    print("two_bank_witness_multiplier_monomials", 8)
    print("two_bank_witness_x1_terms", len(image_sigma[2]))
    print("near_miss_multiplier_monomials", 4)
    print("near_miss_x1_terms", len(image_star[2]))
    print("solution_count", 0)
    print("syllable_control", 4)
    print("new_kappa", None)


if __name__ == "__main__":
    main()
