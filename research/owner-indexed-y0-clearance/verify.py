#!/usr/bin/env python3
"""Owner-indexed reading that clears active-feedback y0 and keeps x0.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The predecessor replay and group algebra are imported unchanged.
"""
from hashlib import sha256
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
QINV = (-1,)
LONG = (-1, 2, 1, 2)
# Inherited field units from research/coded-active-feedback/PROOF.md.
# One F-transpose recoding, one bank addition, one capture, one Q^2 pass.
C1_ADDS = 896
C1_MONOMIALS = 224
C1_CLEARS = 16
BANK_ADDS = 112
BANK_COPYS = 112
MONOMIAL_PASS = 112


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_search():
    path = ROOT / "research/coded-active-feedback/search.py"
    spec = importlib.util.spec_from_file_location("active_feedback_search_pinned", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def even_word(word):
    """Normal-form words whose every Q run has even exponent."""
    run = 0
    for letter in word:
        if abs(letter) == 1:
            run += letter
        else:
            if run % 2:
                return False
            run = 0
    return run % 2 == 0


def in_even(element):
    return all(even_word(word) for (word, _degree), value in element.items() if value)


def snapshot(rows):
    return tuple(tuple(sorted(entry.items()) for entry in row) for row in rows)


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
    qinv, d1, d3 = algebra.inv(q), algebra.D(0), algebra.D(1)
    observed, targets, rows = search.replay(algebra, algebra.one, algebra.mul(c1, q, q))
    need(len(observed) == 39, "saved-bank count moved")
    left = [row for label, row in observed if label.startswith("left:")]
    need(left == rows, "final rows are not the left endpoint banks")
    stored = snapshot(rows)

    blank = {}
    need(rows[1] == [blank, rows[1][1], blank, blank], "bank 1 is not pure y0")
    need(len(rows[1][1]) == 1 and len(rows[2][0]) == 1, "units A and G moved")
    a_coef = rows[2][0]
    b_coef = rows[2][1]
    g_coef = rows[1][1]
    x3, y3 = rows[3][0], rows[3][1]
    need(len(x3) == 1 and len(y3) == 1, "bank 3 lost its monomial columns")
    inv_a = algebra.inv(a_coef)
    x = algebra.mul(rows[0][0], inv_a)
    g = algebra.mul(g_coef, inv_a)
    b = algebra.mul(b_coef, inv_a)
    need(g == algebra.term((2, 1, 1), (0, 0)), "g is not C1 Q^2")
    need(algebra.mul(c1, g) == algebra.mul(q, q), "C1 g is not Q^2")
    one_minus_q2 = algebra.add(algebra.one, algebra.neg(algebra.mul(q, q)))
    need(algebra.mul(x, b) == one_minus_q2, "x b is not 1 - Q^2")
    need(algebra.mul(algebra.add(algebra.mul(x, b), algebra.neg(algebra.one)), algebra.inv(g))
         == algebra.neg(c1),
         "defect slope is not -C1")
    const = algebra.mul(algebra.neg(b), algebra.inv(g))
    expected = {
        (QINV, (0, 0)): -1,
        (LONG, (0, 0)): 1,
    }
    need({key: int(value) for key, value in const.items()} == expected,
         "const support moved")
    factored = algebra.mul(qinv, algebra.add(algebra.mul(c1, q, c1), algebra.neg(algebra.one)))
    need(factored == const, "factored circuit is not the defect")
    need(not in_even(const), "defect collapsed into the even subalgebra")

    # Every D-exponent-0 m0 obeys m1 + m0 C1 = const once the finite products above hold.
    # Spot-check the rearrangement, including a relocation of the pure Q^{-1} term into m0.
    samples = [
        {},
        algebra.term((2, 3, 1, 1), (0, 0), 1),
        algebra.add(algebra.term((3,), (0, 0), 2), algebra.term((1, 2, -1), (0, 0), -3)),
        algebra.mul(algebra.neg(qinv), c1),
    ]
    for m0 in samples:
        m2 = algebra.add(algebra.one, algebra.neg(algebra.mul(m0, x)))
        m1 = algebra.add(const, algebra.neg(algebra.mul(m0, c1)))
        image_x = algebra.add(algebra.mul(m0, rows[0][0]), algebra.mul(m2, a_coef))
        image_y = algebra.add(algebra.mul(m0, rows[0][1]), algebra.mul(m1, g_coef),
                              algebra.mul(m2, b_coef))
        need(image_x == a_coef and image_y == {}, "sample owner index missed the defect")
        need(algebra.add(m1, algebra.mul(m0, c1)) == const, "sample defect was not const")
    relocated_m0 = samples[-1]
    relocated_m1 = algebra.add(const, algebra.neg(algebra.mul(relocated_m0, c1)))
    need(algebra.mul(relocated_m0, c1).get((QINV, (0, 0))) == -1,
         "relocation lost Q^{-1}")
    need((QINV, (0, 0)) not in relocated_m1, "relocation failed to move Q^{-1} out of m1")
    need(any(not even_word(word) for (word, _degree), value in relocated_m0.items() if value),
         "relocated m0 became even")

    # Nonzero bank-3 coefficient cannot hide on the D1 line.
    stray = algebra.mul(c1, y3)
    need(stray and all(degree[1] == 1 for (_word, degree) in stray),
         "bank 3 no longer occupies the D3 line")
    need(all(degree[1] == 0 for (_word, degree) in b_coef), "coupling left the D1 line")

    # Constant owner index. Fresh image only; the four stored banks are not written.
    m1 = const
    fresh = [algebra.add(rows[2][j], algebra.mul(m1, rows[1][j])) for j in range(4)]
    need(fresh[0] == a_coef and fresh[1] == {} and fresh[3] == {},
         "fresh image did not keep x0 and clear y0")
    need(fresh[2] == rows[2][2] and fresh[2] != {}, "x1 block did not stay the published remainder")
    published_x1 = algebra.add(
        algebra.mul(algebra.add(algebra.mul(qinv, c1, q, c1), algebra.neg(qinv)), d1),
        algebra.mul(qinv, c3, d1, d3))
    need(fresh[2] == published_x1, "x1 remainder is not the published three-term coefficient")
    need(snapshot(rows) == stored, "stored endpoint banks were overwritten")
    for dropped in (QINV, LONG):
        partial = {key: value for key, value in m1.items() if key[0] != dropped}
        residue = algebra.add(b_coef, algebra.mul(partial, g_coef))
        need(residue, "dropping a defect monomial still cleared y0")

    declared = []
    for word in search.words(4):
        declared.append(word)
        declared.append(search.reduce_word(tuple(word) + (1, 1)))
    declared = set(declared)
    for word in (QINV, LONG):
        need(word not in declared, "defect monomial fell in the short declared family")

    # Letter count of the factored word Q^{-1}(C1 Q C1 - I), plus the copies and adds
    # that keep both source banks stored.
    c1_uses = 2
    uniform_monomials = 2
    bank_adds = 2
    bank_copies = 2
    ledger = {
        "scalar_adds": c1_uses * C1_ADDS + bank_adds * BANK_ADDS,
        "monomial_passes": c1_uses * C1_MONOMIALS + uniform_monomials * MONOMIAL_PASS,
        "mode_clears": c1_uses * C1_CLEARS,
        "copies": bank_copies * BANK_COPYS,
        "extra_fields": 3 * BANK_COPYS,
        "mode_fields": 8,
        "gaussian_children": 0,
    }
    need(ledger == {
        "scalar_adds": 2016,
        "monomial_passes": 672,
        "mode_clears": 32,
        "copies": 224,
        "extra_fields": 336,
        "mode_fields": 8,
        "gaussian_children": 0,
    }, "ledger arithmetic moved")
    need(len(const) == 2, "a defect monomial was omitted from the support")
    print("PASS_OWNER_INDEXED_Y0_CLEARANCE")
    print("defect", "-Q^{-1}+Q^{-1} C1 Q C1")
    print("ledger", ledger)
    print("x1_terms", len(fresh[2]))
    print("new_kappa", None)


if __name__ == "__main__":
    main()
