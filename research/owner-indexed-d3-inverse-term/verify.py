#!/usr/bin/env python3
"""D-exponent (0,-1) corrections of the sharp owner index leave the x1 residual.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The predecessor replay and group algebra are imported unchanged.
The syllable-length-4 replay is a control. The proof is the identity in PROOF.md.
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
DELTA = (
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
    d3inv = algebra.inv(d3)
    blank = {}
    observed, _targets, rows = search.replay(algebra, algebra.one, algebra.mul(c1, q, q))
    need(len(observed) == 39, "saved-bank count moved")
    left = [row for label, row in observed if label.startswith("left:")]
    need(left == rows, "final rows are not the left endpoint banks")
    stored = tuple(tuple(tuple(sorted(entry.items())) for entry in row) for row in rows)

    const = algebra.add(algebra.term(QINV, (0, 0), -1), algebra.term(LONG, (0, 0)))
    one_plus_q = algebra.add(algebra.one, q)
    x = algebra.mul(algebra.mul(q, q), one_plus_q, c1, q)
    sharp_m0 = algebra.mul(const, c1)
    sharp_m2 = algebra.add(algebra.one, algebra.neg(algebra.mul(sharp_m0, x)))
    sharp_m1 = algebra.add(const, algebra.neg(algebra.mul(sharp_m0, c1)))
    need(sharp_m1 == blank, "sharp index reopened y0")
    need(support(sharp_m0) == {((-1, 2), (0, 0)): -1, ((-1, 2, 1), (0, 0)): 1},
         "sharp m0 support moved")
    need(sharp_m2 == algebra.term(SHARP_M2, (0, 0)), "sharp m2 is not one monomial")
    sharp = [algebra.add(algebra.mul(sharp_m0, rows[0][column]),
                         algebra.mul(sharp_m2, rows[2][column]))
             for column in range(4)]
    residual = algebra.term(RESIDUAL, (1, 1))
    anchor = algebra.term(QINV, (1, 0))
    need(sharp[0] == anchor and sharp[1] == blank and sharp[3] == blank,
         "sharp image did not keep x0 and clear y0 and y1")
    need(sharp[2] == residual, "sharp x1 is not the residual monomial")

    expected = [
        [
            algebra.add(algebra.term((-1, 2), (1, -1)), algebra.term((1, 1, 2), (1, -1))),
            algebra.term((-1,), (1, -1)),
            algebra.term((1, 1, 2), (1, -1), -1),
            blank,
        ],
        [
            blank,
            algebra.term((2, 1), (1, -1)),
            blank,
            blank,
        ],
        [
            algebra.term((-1,), (1, -1)),
            algebra.add(algebra.term((-1, 2, 1), (1, -1)),
                        algebra.term((-1, 2, 1, 1), (1, -1), -1)),
            algebra.add(algebra.term((-1,), (1, -1), -1),
                        algebra.term((-1, 2, 1, 2), (1, -1)),
                        algebra.term((3, -1), (1, 0))),
            blank,
        ],
        [
            algebra.term((1, 3, 1, 1, 2), (1, 0)),
            algebra.term((1, 3, -1), (1, 0)),
            algebra.add(algebra.term((), (1, 0), -1),
                        algebra.term((1, 3, -1, 2), (1, 0)),
                        algebra.term((1, 3, 1, 1, 2), (1, 0), -1)),
            algebra.term((1, 3), (1, 0)),
        ],
    ]
    transported = [[algebra.mul(d3inv, rows[bank][column]) for column in range(4)]
                   for bank in range(4)]
    need(transported == expected, "D3^{-1} column transports moved")
    for bank in range(4):
        need((1, 1) not in degrees(transported[bank][2]),
             "a D3^{-1} x1 transport met the residual degree")
    need(degrees(transported[0][0]) == {(1, -1)} and degrees(transported[0][1]) == {(1, -1)},
         "bank 0 gate degrees moved")
    need(degrees(transported[1][1]) == {(1, -1)} and transported[1][0] == blank,
         "bank 1 gate degrees moved")
    need(degrees(transported[2][0]) == {(1, -1)} and degrees(transported[2][1]) == {(1, -1)},
         "bank 2 gate degrees moved")
    need(degrees(transported[3][0]) == {(1, 0)} and degrees(transported[3][1]) == {(1, 0)},
         "bank 3 gate degrees moved")

    gates = (
        transported[0][1],
        transported[1][1],
        transported[2][0],
        transported[3][0],
        transported[3][1],
    )
    for gate in gates:
        inverse = algebra.inv(gate)
        need(algebra.mul(gate, inverse) == algebra.one and algebra.mul(inverse, gate) == algebra.one,
             "a gate column is not a monomial unit")

    # The degree-0 identities transport because x and C1 contain no C3.
    need(algebra.mul(d3inv, x) == algebra.mul(x, d3inv), "x failed to commute with D3^{-1}")
    need(algebra.mul(d3inv, c1) == algebra.mul(c1, d3inv), "C1 failed to commute with D3^{-1}")
    need(algebra.add(transported[0][0], algebra.neg(algebra.mul(x, transported[2][0]))) == blank,
         "x0 transport identity failed")
    y_identity = algebra.add(transported[0][1],
                             algebra.neg(algebra.mul(c1, transported[1][1])),
                             algebra.neg(algebra.mul(x, transported[2][1])))
    need(y_identity == blank, "y0 transport identity failed")
    delta = algebra.add(transported[0][2], algebra.neg(algebra.mul(x, transported[2][2])))
    need(delta == literal(algebra, DELTA), "homogeneous x1 defect moved")
    need((1, 1) not in degrees(delta) and delta != blank, "defect met the residual degree or vanished")

    samples = [
        blank,
        algebra.one,
        c1,
        c3,
        q,
        algebra.mul(qinv, c1),
        algebra.add(c3, algebra.mul(q, q), algebra.term((2, 3), (0, 0), -2)),
        algebra.term((2, 3, 1, 1, 2), (0, 0), 5),
    ]
    for coefficient in samples:
        need(degrees(coefficient) <= {(0, 0)}, "sample left the D-exponent-0 line")
        u1 = algebra.mul(algebra.neg(coefficient), c1)
        u2 = algebra.mul(algebra.neg(coefficient), x)
        solved_u2 = algebra.mul(algebra.neg(algebra.mul(coefficient, transported[0][0])),
                                algebra.inv(transported[2][0]))
        y_load = algebra.add(algebra.mul(coefficient, transported[0][1]),
                             algebra.mul(u2, transported[2][1]))
        solved_u1 = algebra.mul(algebra.neg(y_load), algebra.inv(transported[1][1]))
        need(solved_u1 == u1 and solved_u2 == u2, "boundary solution left the closed form")
        image = []
        for column in range(4):
            image.append(algebra.add(
                sharp[column],
                algebra.mul(coefficient, transported[0][column]),
                algebra.mul(u1, transported[1][column]),
                algebra.mul(u2, transported[2][column])))
        need(image[0] == anchor and image[1] == blank and image[3] == blank,
             "boundary family failed to keep x0 and clear y0 and y1")
        need(degree_part(image[2], (1, 1)) == residual, "boundary family changed the residual")
        need(image[2] == algebra.add(residual, algebra.mul(coefficient, delta)),
             "boundary x1 is not the residual plus u0 times the defect")
        # Arbitrary coefficients, not only the boundary family.
        stray = algebra.add(
            sharp[2],
            algebra.mul(coefficient, transported[0][2]),
            algebra.mul(c3, transported[1][2]),
            algebra.mul(q, transported[2][2]),
            algebra.mul(c1, transported[3][2]))
        need(degree_part(stray, (1, 1)) == residual,
             "a non-boundary (0,-1) correction changed the residual")

    # Witness u0 = I. Four new multiplier monomials, three extra x1 monomials.
    witness_u1 = algebra.neg(c1)
    witness_u2 = algebra.neg(x)
    need(support(witness_u2) == {((-1, 2, 1), (0, 0)): -1, ((1, 1, 2, 1), (0, 0)): -1},
         "witness u2 is not -Q^{-1} C1 Q - Q^2 C1 Q")
    witness = []
    for column in range(4):
        witness.append(algebra.add(
            sharp[column],
            transported[0][column],
            algebra.mul(witness_u1, transported[1][column]),
            algebra.mul(witness_u2, transported[2][column])))
    need(witness[0] == anchor and witness[1] == blank and witness[3] == blank,
         "witness did not keep the boundary")
    need(witness[2] == algebra.add(residual, delta) and len(witness[2]) == 4,
         "witness x1 is not the residual plus the three-term defect")
    need(degree_part(witness[2], (1, 1)) == residual, "witness cancelled or duplicated the residual")

    # One bank, any listed degree: the monomial gate forces the coefficient to vanish.
    single_degrees = ((0, 0), (0, -1), (0, 1), (1, 0), (-1, 1), (2, -3))
    gate_columns = (1, 1, 0, 0)
    for degree in single_degrees:
        shift = algebra.term((), degree)
        for bank, column in enumerate(gate_columns):
            gate = algebra.mul(shift, rows[bank][column])
            need(len(gate) == 1, "a single-bank gate stopped being one monomial")
            inverse = algebra.inv(gate)
            need(algebra.mul(gate, inverse) == algebra.one, "a single-bank gate is not a unit")
            image = [algebra.add(sharp[index], algebra.mul(shift, rows[bank][index]))
                     for index in range(4)]
            need(image[0] != anchor or image[1] != blank,
                 "a nonzero single-bank term kept x0 and y0")
            if degree == (0, -1):
                need(degree_part(image[2], (1, 1)) == residual,
                     "a single-bank (0,-1) term changed the residual")

    # Syllable control for the fold and the Q-exponent bijection. Not a census of u0.
    words = normal_words(algebra, 4)
    need(len(words) == syllable_count(4) == 192, "four-syllable normal forms are incomplete")
    syllables = ((1,), (1, 1), (-1,), (2,), (3,))
    for word in words:
        need(search.reduce_word(word) == word, "generated word was not normal")
        exponent, prefix = final_q_exponent(word)
        for syllable in syllables:
            extended = word + syllable
            need(search.reduce_word(search.reduce_word(word) + syllable) == search.reduce_word(extended),
                 "reducer fold failed on a four-syllable word")
            if abs(syllable[0]) == 1:
                power = { (1,): 1, (1, 1): 2, (-1,): 3 }[syllable]
                shifted = algebra.mul(algebra.term(word, (0, 0)), algebra.term(syllable, (0, 0)))
                (new, degree), value = next(iter(shifted.items()))
                new_exponent, new_prefix = final_q_exponent(new)
                need(degree == (0, 0) and value == 1, "Q power left the degree-0 group")
                need(new_prefix == prefix and new_exponent == (exponent + power) % 4,
                     "Q power did not act on the final exponent")
        for gate in gates:
            ((gate_word, gate_degree), gate_value), = gate.items()
            cancelled = algebra.mul(algebra.term(word, (0, 0)), gate, algebra.inv(gate))
            need(cancelled == algebra.term(word, (0, 0)),
                 "a gate failed to cancel on a four-syllable word")
            need(gate_value != 0 and gate_degree != (0, 0), "gate degree collapsed")
            need(gate_word == search.reduce_word(gate_word), "gate word was not normal")

    # Failure controls.
    for bank in range(4):
        only = [algebra.add(sharp[column], transported[bank][column]) for column in range(4)]
        need(only[0] != anchor or only[1] != blank, "one bank of D3^{-1} kept the boundary")
        need(degree_part(only[2], (1, 1)) == residual, "one bank of D3^{-1} changed the residual")
    positive = algebra.D(1)
    copied = []
    for column in range(4):
        copied.append(algebra.add(
            sharp[column],
            algebra.mul(positive, rows[0][column]),
            algebra.mul(witness_u1, positive, rows[1][column]),
            algebra.mul(witness_u2, positive, rows[2][column])))
    need(copied[0] == anchor and copied[1] == blank and copied[3] == blank,
         "the commuting coefficient shape stopped preserving the boundary at D3")
    need(copied[2] != blank and degree_part(copied[2], (1, 1)) != residual,
         "D3^{+1} reproduced the (0,-1) residual line")
    need(residual.items() <= degree_part(copied[2], (1, 1)).items(),
         "the unchecked D3^{+1} shape already deleted the residual key")
    need(tuple(stored) == tuple(tuple(tuple(sorted(entry.items())) for entry in row) for row in rows),
         "stored endpoint banks were overwritten")
    need(selected["kappa"] == "781451/250000000", "selected frontier value moved during the check")

    print("PASS_OWNER_INDEXED_D3_INVERSE_TERM")
    print("evidence_class", "proof")
    print("residual_coefficient", 1)
    print("boundary_family", "u1=-u0*C1, u2=-u0*x, u3=0")
    print("witness_new_multiplier_monomials", 4)
    print("witness_x1_terms", len(witness[2]))
    print("syllable_control", 4)
    print("new_kappa", None)


if __name__ == "__main__":
    main()
