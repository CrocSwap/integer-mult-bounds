#!/usr/bin/env python3
"""The declared active-feedback decoder preserves one y0 coupling monomial.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The predecessor replay and group algebra are imported unchanged.
"""
from hashlib import sha256
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ALPHA = ((-1,), (1, 0))
BETA = ((-1, 2, 1), (1, 0))
SUPPORT = {
    (),
    (-1,),
    (-1, 2),
    (2, 1),
    (-1, 2, 1),
    (1, 1, 2),
    (-1, 2, 1, 1),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_search():
    path = ROOT / "research/coded-active-feedback/search.py"
    spec = importlib.util.spec_from_file_location("active_feedback_search_pinned", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def declared_controls(search, limit):
    """Alternating code words of C-length at most `limit`, with and without right Q^2."""
    family = []
    for word in search.words(limit):
        family.append(word)
        family.append(search.reduce_word(tuple(word) + (1, 1)))
    return list(dict.fromkeys(family))


def c_length(word):
    return sum(abs(letter) in (2, 3) for letter in word)


def preimage_key(algebra, control, key):
    image = algebra.mul(algebra.inv(algebra.term(control, (0, 0))), algebra.term(*key))
    need(len(image) == 1, "control preimage is not a monomial")
    ((word, degree), coefficient), = image.items()
    need(coefficient == 1 and degree == (1, 0), "preimage left the D1 line")
    return word


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
    q, c1 = algebra.gen(1), algebra.gen(2)
    q_inverse, d1 = algebra.inv(q), algebra.D(0)
    restored = algebra.mul(d1, q_inverse)
    coupling = algebra.mul(q_inverse, c1, q, algebra.add(algebra.one, algebra.neg(q)), d1)
    lock = algebra.mul(q_inverse, c1, q, q, algebra.add(algebra.one, algebra.neg(q)))
    need(algebra.mul(lock, restored) == coupling, "published y0 coefficient is not the left multiple K A")
    need(len(restored) == 1 and len(coupling) == 2 and len(lock) == 2, "unexpected term counts")
    need(coupling.get(BETA) == 1, "beta is not a coupling term")

    observed, targets, rows = search.replay(algebra, algebra.one, algebra.mul(c1, q, q))
    by_label = dict(observed)
    published = by_label["query4:3"]
    need(published[0] == restored and published[1] == coupling, "published row moved")
    need(rows[2][0] == restored and rows[2][1] == coupling, "final image of the restored bank moved")
    need(published[1].get(BETA) == 1 and published[0].get(ALPHA) == 1, "witness coefficients are not 1")

    support = set()
    for _label, row in observed:
        for column in (0, 1):
            for (word, degree), value in row[column].items():
                if value and degree == (1, 0):
                    support.add(word)
    need(support == SUPPORT, "D1-line word support changed")

    equal_banks = []
    for label, row in observed:
        alpha = row[0].get(ALPHA, 0)
        beta = row[1].get(BETA, 0)
        need(alpha == beta, "identity control already separates " + label)
        if alpha:
            equal_banks.append(label)
    need(equal_banks == ["response4", "query4:3", "left:2"], "unexpected banks carry the witness")

    # Nonempty short words are enumerated. A pure code word of C-length n has
    # alpha-preimage length n+1. Its right-Q^2 extension has length n+3. Both
    # exceed the support once n >= 4 and n >= 2 respectively.
    short = declared_controls(search, 4)
    identity_hits = 0
    for control in short:
        alpha_word = preimage_key(algebra, control, ALPHA)
        beta_word = preimage_key(algebra, control, BETA)
        if control == ():
            need(alpha_word == ALPHA[0] and beta_word == BETA[0], "identity preimage moved")
            identity_hits += 1
            continue
        need(alpha_word not in SUPPORT and beta_word not in SUPPORT,
             "short control hits the witness support: " + str(control))
        if c_length(control) == 0:
            need(alpha_word == (1,) and beta_word == (1, 2, 1), "bare Q^2 preimage changed")
    need(identity_hits == 1, "the family lost its identity")
    for phase_start in (2, 3):
        for n, pure_length, shifted_length in ((4, 5, 7), (5, 6, 8)):
            word = tuple(2 + ((j + phase_start) % 2) for j in range(n))
            pure = preimage_key(algebra, word, ALPHA)
            shifted = preimage_key(algebra, search.reduce_word(word + (1, 1)), ALPHA)
            need(len(pure) == pure_length and len(shifted) == shifted_length,
                 "length formula failed")
            need(pure not in SUPPORT and shifted not in SUPPORT, "long preimage fell into the support")

    # Every declared control, of any C-length, therefore has equal pulled-back
    # coefficients: the identity by the bank table, and every other control because
    # both preimages miss the finite support. Check the published bound and one
    # longer slice directly.
    for limit in (7, 12):
        for control in declared_controls(search, limit):
            alpha_word = preimage_key(algebra, control, ALPHA)
            beta_word = preimage_key(algebra, control, BETA)
            for _label, row in observed:
                need(row[0].get((alpha_word, (1, 0)), 0) == row[1].get((beta_word, (1, 0)), 0),
                     "decoder image separated the witness")
    need(restored.get(ALPHA) == 1, "target lost alpha")
    # The autonomous x0 target has no y0 block, so its beta coefficient is 0.
    need(restored.get(ALPHA, 0) - 0 == 1, "target witness difference is not 1")

    # Outside the grammar, one left image of final bank 1 clears y0 and keeps A.
    # This control is not a declared code word, so it does not contradict the theorem.
    companion = rows[1][1]
    need(len(companion) == 1 and rows[1][0] == {} and rows[1][2] == {} and rows[1][3] == {},
         "companion bank is not a pure y0 monomial")
    correction = algebra.mul(coupling, algebra.inv(companion))
    cleaned = [algebra.add(rows[2][j], algebra.neg(algebra.mul(correction, rows[1][j]))) for j in range(4)]
    need(cleaned[0] == restored and cleaned[1] == {}, "odd-Q companion correction failed")
    family = set(declared_controls(search, 7))
    for (word, degree), value in correction.items():
        need(value and degree == (0, 0) and word not in family,
             "companion correction fell inside the declared family")

    # Wrong second edge must not be described as the same restored coefficient.
    _unused, _targets, wrong_rows = search.replay(algebra, algebra.one, {})
    need(wrong_rows[2][0] != restored, "omitted second edge still restored A")
    need(targets[0][0] == restored and targets[0][1] == {}, "autonomous target changed")
    print("PASS_ACTIVE_FEEDBACK_COUPLING_LOCK")
    print("witness_banks", ",".join(equal_banks))
    print("declared_family", "alternating C1/C3 words, optionally times right Q^2")
    print("new_kappa", None)


if __name__ == "__main__":
    main()
