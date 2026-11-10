#!/usr/bin/env python3
"""Ordinary bill of the two-edge witness F1=Q, F2=C1 Q.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The predecessor schedule and group algebra are imported unchanged. No call
is added. The field ledger uses the predecessor's uniform monomial unit.
"""
from fractions import Fraction
from hashlib import sha256
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
COEFFICIENTS = ("-2", "-1", "-1/2", "1/2", "1", "2")
# Inherited field units from research/coded-active-feedback/PROOF.md.
BANK = 112
C1_ADDS = 896
C1_MONOMIALS = 224
C1_CLEARS = 16
MODES = 8


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_search():
    path = ROOT / "research/coded-active-feedback/search.py"
    spec = importlib.util.spec_from_file_location("active_feedback_search_pinned", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def family_operators(algebra, search, second_edge):
    operators = [{}]
    for word in search.words(7):
        for coefficient in COEFFICIENTS:
            body = tuple(word) + ((1, 1) if second_edge else ())
            operators.append(algebra.term(body, (0, 0), coefficient))
    need(len(operators) == len({tuple(sorted(item.items())) for item in operators}) == 91,
         "policy edge did not produce 91 operators")
    return operators


def key_of(monomial):
    need(len(monomial) == 1, "expected one monomial")
    ((word, degree), value), = monomial.items()
    need(value == 1, "expected a unit monomial")
    return (word, degree)


def occurrences(rows, key):
    found = []
    for bank, row in enumerate(rows):
        for column, entry in enumerate(row):
            if entry.get(key, 0):
                found.append((bank, column, entry[key]))
    return found


def scalar_suffix(algebra, rows):
    """The four scalar steps search.replay runs after query 4."""
    out = [list(row) for row in rows]

    def plus(dst, src, sign):
        op = algebra.term((), (0, 0), sign)
        out[dst] = [algebra.add(x, algebra.mul(op, y))
                    for x, y in zip(out[dst], out[src])]

    plus(2, 0, 1)
    plus(1, 3, -1)
    out[0], out[1] = out[1], [algebra.neg(entry) for entry in out[0]]
    out[2], out[3] = out[3], [algebra.neg(entry) for entry in out[2]]
    plus(0, 2, 1)
    plus(3, 1, -1)
    return out


def signed_permutation(algebra, rows):
    return [
        list(rows[1]),
        [algebra.neg(entry) for entry in rows[0]],
        list(rows[3]),
        [algebra.neg(entry) for entry in rows[2]],
    ]


def main():
    pinned = {
        "research/coded-active-feedback/search.py":
            "1383010827af29a1b0e595e2c1aa2ffad461b266ffc9f936efce1603ff9f5eb6",
        "research/coded-native-caller/gauge.py":
            "390391d291353741c89daea999d483660ca185987ed96a15b82576280c487cad",
    }
    for name, digest in pinned.items():
        need(sha256((ROOT / name).read_bytes()).hexdigest() == digest, "changed pin " + name)
    search = load_search()
    algebra = search.algebra()
    q, c1, c3 = algebra.gen(1), algebra.gen(2), algebra.gen(3)
    qi, d1, d3 = algebra.inv(q), algebra.D(0), algebra.D(1)
    two = algebra.term((), (0, 0), 2)
    published_f1, published_f2 = algebra.one, algebra.mul(c1, q, q)
    witness_f1, witness_f2 = q, algebra.mul(c1, q)
    need(witness_f1 == algebra.term((1,), (0, 0)), "F1 is not Q")
    need(witness_f2 == algebra.term((2, 1), (0, 0)), "F2 is not C1 Q")
    need(published_f2 == algebra.term((2, 1, 1), (0, 0)), "published F2 is not C1 Q^2")
    first_family = family_operators(algebra, search, False)
    second_family = family_operators(algebra, search, True)
    need(published_f1 in first_family and published_f2 in second_family,
         "published edges fell outside the 8,281-policy family")
    need(witness_f1 not in first_family and witness_f2 not in second_family,
         "the two-edge witness is inside the 8,281-policy family")

    # Conjugations used to move D through the saved banks.
    need(algebra.mul(d1, q, c1) == algebra.mul(c1, q, d1), "FULL1 X conjugation changed")
    need(algebra.mul(d1, c1, qi) == algebra.mul(qi, c1, d1), "saved h conjugation changed")
    need(algebra.mul(d3, q, c3, d1) == algebra.mul(c3, q, d1, d3),
         "FULL3 y conjugation changed")
    need(algebra.mul(d3, q, c3, qi, c1, d1) == algebra.mul(c3, c1, d1, d3),
         "FULL3 x0 conjugation changed")
    need(algebra.mul(d1, d3) == algebra.mul(d3, d1), "D1 and D3 no longer commute")

    h = [algebra.mul(qi, c1, d1), d1, algebra.neg(algebra.mul(qi, c1, d1)), {}]
    qh = [algebra.mul(c1, d1), algebra.mul(q, d1), algebra.neg(algebra.mul(c1, d1)), {}]
    x_at = [{}, algebra.neg(algebra.mul(c1, q, d1)), d1, {}]
    need([algebra.mul(q, entry) for entry in h] == qh, "Q h moved")
    need(qh != h, "Q and I agree on the saved FULL1 Y bank")
    need([qh[j] != h[j] for j in range(4)] == [True, True, True, False],
         "Q h should differ on x0, y0 and x1 only")
    witness_argument = [algebra.add(algebra.mul(c1, x), algebra.mul(q, y))
                        for x, y in zip(x_at, h)]
    published_argument = [algebra.add(algebra.mul(c1, x), y) for x, y in zip(x_at, h)]
    need(witness_argument == [algebra.mul(c1, d1), {}, {}, {}],
         "Q on h did not cancel the query-2 argument down to C1 D1")
    need(published_argument != witness_argument, "I on h produced the witness argument")
    need(published_argument[1] != {} and published_argument[2] != {},
         "the published argument lost a column")
    witness_response = [algebra.mul(qi, entry) for entry in witness_argument]
    need(witness_response == [algebra.mul(qi, c1, d1), {}, {}, {}],
         "witness response2 is not the single monomial Q^{-1} C1 D1")
    need(algebra.mul(witness_f2, witness_response[0]) == d1, "C1 Q did not return D1")
    need([algebra.mul(witness_f2, entry) for entry in witness_response] == [d1, {}, {}, {}],
         "C1 Q on the witness response is not pure D1")
    other = algebra.mul(published_f2, witness_response[0])
    need(other == algebra.mul(c1, q, c1, d1) and other != d1,
         "C1 Q^2 on the same witness response should stay off D1")

    published_observed, targets, published_final = search.replay(
        algebra, published_f1, published_f2)
    witness_observed, witness_targets, witness_final = search.replay(
        algebra, witness_f1, witness_f2)
    need(witness_targets == targets, "uncoded targets moved between replays")
    published_by = dict(published_observed)
    witness_by = dict(witness_observed)
    need(witness_by["FULL1:1"] == published_by["FULL1:1"] == h,
         "saved h is not the common FULL1 Y bank")
    need(witness_by["bridge_query2:0"] == x_at, "query-2 X bank moved")
    need(witness_by["response2"] == witness_response, "replayed witness response moved")
    published_response = [
        algebra.mul(q, q, c1, d1),
        algebra.add(algebra.neg(d1), algebra.mul(qi, d1)),
        algebra.add(algebra.mul(qi, c1, d1), algebra.neg(algebra.mul(q, q, c1, d1))),
        {},
    ]
    need(published_by["response2"] == published_response, "published response2 moved")
    published_images = (
        [algebra.mul(published_f2, entry) for entry in published_response],
        [algebra.mul(witness_f2, entry) for entry in published_response],
    )
    need(published_images[0] != published_images[1],
         "C1 Q^2 and C1 Q agree on the published response")
    need([published_images[0][j] != published_images[1][j] for j in range(3)],
         "the two second-edge operators should differ on three published columns")
    need(witness_by["response2"] != published_response,
         "changing F1 left the owned response unchanged")

    autonomous = [algebra.mul(d1, qi), {}, algebra.mul(qi, c3, d1, d3), {}]
    need(witness_by["query4:3"] == autonomous, "witness query-4 row is not autonomous")
    need(witness_by["query4:0"] == [{}, algebra.neg(algebra.mul(c1, q, d1)), {}, {}],
         "query-4 bank 0 is not the pure negative y0 monomial")
    bank0 = [
        algebra.mul(two, qi, c1, d1),
        d1,
        algebra.neg(algebra.mul(qi, c1, d1)),
        {},
    ]
    bank3 = [
        algebra.mul(c3, c1, d1, d3),
        algebra.mul(c3, q, d1, d3),
        algebra.neg(algebra.mul(d1, d3)),
        algebra.mul(c3, q, d1, d3),
    ]
    bank1 = [{}, algebra.mul(c1, q, d1), {}, {}]
    need(list(bank0[0].values()) == [Fraction(2)], "bank 0 x0 coefficient is not 2")
    need(witness_final[0] == bank0, "final bank 0 moved")
    need(witness_final[3] == bank3, "final bank 3 moved")
    need(witness_final[1] == published_final[1] == bank1,
         "final bank 1 is no longer the published pure y0 monomial")
    need(witness_final[2] == autonomous, "final bank 2 is not the autonomous row")
    need(bank3[1] == bank3[3], "final bank 3 should keep equal y0 and y1 monomials")
    need(all(witness_final[i] != targets[i] for i in range(4)),
         "a witness final bank matched its uncoded target")
    need(witness_final[0] != published_final[0] and witness_final[3] != published_final[3],
         "banks 0 and 3 accidentally matched the published feed")

    # The suffix is a signed permutation for every content. It clears a final
    # bank only by relocating a preimage that is already the signed target.
    query4 = [witness_by["query4:" + str(i)] for i in range(4)]
    need(signed_permutation(algebra, query4) == witness_final, "witness suffix moved")
    need(scalar_suffix(algebra, query4) == witness_final, "suffix steps disagree")
    for label, feedback1, feedback2 in (
            ("published", published_f1, published_f2),
            ("empty", {}, {}),
            ("first-only", witness_f1, {}),
    ):
        observed, _, final = search.replay(algebra, feedback1, feedback2)
        by_label = dict(observed)
        preimage = [by_label["query4:" + str(i)] for i in range(4)]
        need(scalar_suffix(algebra, preimage) == signed_permutation(algebra, preimage) == final,
             "suffix identity failed for " + label)
    separating = []
    power = 0
    base = algebra.D(0)
    degree = algebra.one
    for _bank in range(4):
        row = []
        for _column in range(4):
            power += 1
            degree = algebra.mul(degree, base)
            row.append(degree)
        separating.append(row)
    permuted = signed_permutation(algebra, separating)
    need(scalar_suffix(algebra, separating) == permuted, "separating suffix fixture moved")
    need(permuted != separating, "separating fixture was already a fixed point")
    signed_targets = [
        targets[1],
        [algebra.neg(entry) for entry in targets[0]],
        targets[3],
        [algebra.neg(entry) for entry in targets[2]],
    ]
    need(all(query4[i] != signed_targets[i] for i in range(4)),
         "a query-4 preimage was already the signed target its final bank needs")

    # Word-free rational combinations of these four banks. Each target monomial
    # is absent, or it occurs in exactly one column together with a second
    # monomial that no other column carries.
    pure_q_inverse = key_of(algebra.mul(d1, qi))
    dragged = key_of(algebra.mul(qi, c3, d1, d3))
    pure_q = key_of(algebra.mul(d1, q))
    degree_11_q_inverse = key_of(algebra.mul(d3, d1, qi))
    degree_11_q = key_of(algebra.mul(d3, d1, q))
    need(occurrences(witness_final, pure_q_inverse) == [(2, 0, Fraction(1))],
         "target-0 monomial is not isolated on bank 2")
    need(occurrences(witness_final, dragged) == [(2, 2, Fraction(1))],
         "the autonomous x1 monomial is not isolated on bank 2")
    for key, name in (
            (pure_q, "target 1"),
            (degree_11_q_inverse, "target 2"),
            (degree_11_q, "target 3"),
    ):
        need(occurrences(witness_final, key) == [], name + " monomial appeared")
    half = algebra.term((), (0, 0), Fraction(1, 2))
    need([algebra.mul(half, entry) for entry in bank0] != targets[0],
         "halving bank 0 produced target 0")
    need([algebra.mul(c3, entry) for entry in bank3] != targets[3],
         "one C3 on bank 3 produced target 3")

    # Same owned-bank lifetime as the published component. Q overwrites the
    # saved copy of h; that copy is not read again. No zero column is discounted.
    witness_monomials = C1_MONOMIALS + BANK + BANK
    published_monomials = C1_MONOMIALS + BANK
    witness_adds = 2 * BANK + C1_ADDS
    need(witness_monomials == 448 and published_monomials == 336, "monomial totals moved")
    need(witness_monomials - published_monomials == BANK, "the bill delta is not one Q on h")
    need(witness_adds == 1120, "scalar ADD total moved")
    need(2 * BANK == 224 and 3 * BANK == 336, "copy and reset totals moved")
    need(C1_CLEARS == 16 and MODES == 8 and BANK == 112, "inherited units moved")
    print("PASS_TWO_EDGE_WITNESS_BILL")
    print("owned_bank_delta", "one extra Q on saved h; response monomial Q^2 replaced by Q")
    print("monomial_passes", witness_monomials)
    print("published_monomial_passes", published_monomials)
    print("scalar_adds", witness_adds)
    print("mode_clears", C1_CLEARS)
    print("copies", 2 * BANK)
    print("resets", 3 * BANK)
    print("gaussian_children_under_monomial_unit", 0)
    print("final_banks_cleared_by_scalar_suffix", "none")
    print("word_free_target_hits", 0)
    print("new_kappa", None)


if __name__ == "__main__":
    main()
