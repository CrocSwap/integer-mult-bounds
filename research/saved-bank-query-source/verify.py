#!/usr/bin/env python3
"""One saved bank other than response2, with the second operator held at C1 Q^2.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The predecessor schedule and group algebra are imported unchanged. No call
is added. The positive identity is one algebra element on one named bank.
The census is the finite list of recorded banks, not a search over operators.
"""
from hashlib import sha256
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
# Inherited field units from research/coded-active-feedback/PROOF.md.
C1_ADDS = 896
C1_MONOMIALS = 224
C1_CLEARS = 16
BANK_ADDS = 112
BANK_COPYS = 112
MONOMIAL_PASS = 112

PRE_QUERY = (
    "right:0", "right:1", "right:2", "right:3",
    "response0",
    "query0:0", "query0:1", "query0:2", "query0:3",
    "FULL1:0", "FULL1:1", "FULL1:2", "FULL1:3",
    "IDLE:0", "IDLE:1", "IDLE:2", "IDLE:3",
    "response2",
    "bridge_query2:0", "bridge_query2:1", "bridge_query2:2", "bridge_query2:3",
    "bridge_minus:0", "bridge_minus:1", "bridge_minus:2", "bridge_minus:3",
    "FULL3:0", "FULL3:1", "FULL3:2", "FULL3:3",
)
POST_QUERY = (
    "response4",
    "query4:0", "query4:1", "query4:2", "query4:3",
    "left:0", "left:1", "left:2", "left:3",
)
ZERO_COLUMN = (
    "right:0", "right:1", "right:2", "right:3",
    "response0", "query0:0", "query0:2", "query0:3",
    "FULL1:0", "FULL1:2", "FULL1:3",
    "IDLE:0", "IDLE:2", "IDLE:3",
    "bridge_query2:2", "bridge_query2:3",
    "bridge_minus:0", "bridge_minus:2",
    "FULL3:0",
)
UNIT_KILLS = (
    "query0:1", "FULL1:1", "IDLE:1",
    "bridge_minus:3", "FULL3:2", "FULL3:3",
)
UNIQUE_FAILS = ("bridge_query2:1", "bridge_minus:1", "FULL3:1")
POST_ZERO = ("query4:0", "left:1")
POST_UNIT = ("response4", "query4:2", "query4:3", "left:2", "left:3")
POST_UNIQUE_FAILS = ("query4:1", "left:0")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_search():
    path = ROOT / "research/coded-active-feedback/search.py"
    spec = importlib.util.spec_from_file_location("saved_bank_search_pinned", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def schedule(algebra, feedback1, feedback2, insert=None):
    """search.replay, plus one optional left operator on the saved pair-0 X bank."""
    q, qi = algebra.gen(1), algebra.inv(algebra.gen(1))
    c1, c3 = algebra.gen(2), algebra.gen(3)
    d1, d3 = algebra.D(0), algebra.D(1)
    rows = [[algebra.one if i == j else {} for j in range(4)] for i in range(4)]
    observed = []

    def snap(label):
        observed.extend((label + ":" + str(i), [dict(entry) for entry in row])
                        for i, row in enumerate(rows))

    def plus(dst, src, op):
        rows[dst] = [algebra.add(x, algebra.mul(op, y))
                     for x, y in zip(rows[dst], rows[src])]

    def left(index, op):
        rows[index] = [algebra.mul(op, entry) for entry in rows[index]]

    def query(pair, argument, label, after=None):
        response = [algebra.mul(qi, entry) for entry in argument]
        observed.append((label, [dict(entry) for entry in response]))
        rows[2 * pair + 1] = [algebra.add(x, algebra.mul(after or algebra.one, y))
                              for x, y in zip(rows[2 * pair + 1], response)]
        return response

    def full(pair, code, stage):
        plus(2 * pair, 2 * pair + 1, algebra.neg(algebra.mul(q, code)))
        left(2 * pair, stage)
        left(2 * pair + 1, stage)

    def bridge(dst, src, sign):
        plus(2 * dst, 2 * src, algebra.term((), (0, 0), sign))
        plus(2 * src + 1, 2 * dst + 1, algebra.term((), (0, 0), -sign))

    rows[0][2], rows[3][1] = algebra.neg(algebra.one), algebra.one
    snap("right")
    query(0, rows[0], "response0", c1)
    snap("query0")
    full(0, c1, d1)
    snap("FULL1")
    late_y = [dict(entry) for entry in rows[1]]
    left(2, d1)
    left(3, d1)
    snap("IDLE")
    bridge(0, 1, 1)
    before_query2 = [dict(entry) for entry in rows[0]]
    argument = [algebra.add(algebra.mul(c1, x), algebra.mul(feedback1, y))
                for x, y in zip(rows[0], late_y)]
    response2 = query(0, argument, "response2")
    snap("bridge_query2")
    saved = [dict(entry) for entry in rows[0]]
    bridge(0, 1, -1)
    snap("bridge_minus")
    full(1, c3, d3)
    snap("FULL3")
    argument = [algebra.add(algebra.mul(c3, x), algebra.mul(feedback2, y))
                for x, y in zip(rows[2], response2)]
    if insert is not None:
        argument = [algebra.add(x, algebra.mul(insert, z))
                    for x, z in zip(argument, saved)]
    query(1, argument, "response4")
    snap("query4")
    bridge(1, 0, 1)
    for x, y in ((0, 1), (2, 3)):
        rows[x], rows[y] = rows[y], [algebra.neg(entry) for entry in rows[x]]
    plus(0, 2, algebra.one)
    plus(3, 1, algebra.neg(algebra.one))
    snap("left")
    return observed, [list(row) for row in rows], saved, before_query2


def derived_source(algebra):
    """Pair-0 X bank after the +1 bridge, from the schedule steps that write it."""
    q, qi = algebra.gen(1), algebra.inv(algebra.gen(1))
    c1, d1 = algebra.gen(2), algebra.D(0)
    row0 = [algebra.one, {}, algebra.neg(algebra.one), {}]
    response = [algebra.mul(qi, entry) for entry in row0]
    row1 = [algebra.add(x, algebra.mul(c1, y))
            for x, y in zip([{}, algebra.one, {}, {}], response)]
    row0 = [algebra.add(x, algebra.mul(algebra.neg(algebra.mul(q, c1)), y))
            for x, y in zip(row0, row1)]
    full1 = [algebra.mul(d1, entry) for entry in row0]
    idle_x = [{}, {}, d1, {}]
    saved = [algebra.add(x, y) for x, y in zip(full1, idle_x)]
    return full1, saved


def classify(algebra, bank, rho):
    if bank[1] == {} or bank[2] == {}:
        return "zero-column", None
    for index in (0, 3):
        if len(bank[index]) == 1:
            inverse = algebra.inv(bank[index])
            need(algebra.mul(bank[index], inverse) == algebra.one
                 and algebra.mul(inverse, bank[index]) == algebra.one,
                 "one-term column is not a two-sided unit")
            return "unit-kills", None
    need(len(bank[1]) == 1, "unclassified bank: y0 column is not a unit")
    inverse = algebra.inv(bank[1])
    need(algebra.mul(bank[1], inverse) == algebra.one
         and algebra.mul(inverse, bank[1]) == algebra.one,
         "y0 column is not a two-sided unit")
    operator = algebra.mul(rho[1], inverse)
    image = [algebra.mul(operator, column) for column in bank]
    if image == rho:
        return "works", operator
    return "unique-fails", (operator, image)


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
    q, qi = algebra.gen(1), algebra.inv(algebra.gen(1))
    c1, c3 = algebra.gen(2), algebra.gen(3)
    d1, d3 = algebra.D(0), algebra.D(1)
    published_f1, published_f2 = algebra.one, algebra.mul(c1, q, q)
    need(published_f2 == algebra.term((2, 1, 1), (0, 0)), "second operator is not C1 Q^2")

    published, targets, published_final = search.replay(algebra, published_f1, published_f2)
    labels = [label for label, _row in published]
    need(tuple(labels) == PRE_QUERY + POST_QUERY, "recorded bank list moved")
    need(len(published) == 39, "saved-bank count is not 39")
    by_label = dict(published)
    local, local_final, saved, before_query2 = schedule(algebra, published_f1, published_f2)
    need([(label, row) for label, row in local] == published, "local schedule drifted from search.replay")
    need(local_final == published_final, "local suffix drifted from search.replay")

    row = by_label["query4:3"]
    restored = algebra.mul(d1, qi)
    original_x1 = algebra.mul(qi, c3, d1, d3)
    coupling = row[1]
    extra = algebra.add(row[2], algebra.neg(original_x1))
    autonomous = [restored, {}, original_x1, {}]
    need(row[0] == restored and row[3] == {} and coupling != {} and extra != {},
         "published row is not A plus a y0 coupling plus an x1 defect")
    need(row != autonomous, "published feed is already autonomous")
    need(coupling == algebra.add(algebra.mul(qi, c1, q, d1),
                                 algebra.neg(algebra.mul(qi, c1, q, q, d1))),
         "y0 coupling is not Q^{-1} C1 Q (I-Q) D1")
    need(extra == algebra.add(algebra.neg(algebra.mul(qi, d1)),
                              algebra.mul(qi, c1, q, c1, d1)),
         "x1 defect is not (Q^{-1} C1 Q C1 - Q^{-1}) D1")
    rho = [algebra.mul(q, column) for column in [{}, algebra.neg(coupling), algebra.neg(extra), {}]]
    need(rho[0] == {} and rho[3] == {} and len(rho[1]) == 2 and len(rho[2]) == 2,
         "the required correction is not two monomials on y0 and on x1")

    need(algebra.mul(d1, q, c1) == algebra.mul(c1, q, d1),
         "D1 conjugation of Q C1 moved")
    full1, derived = derived_source(algebra)
    need(full1 == [ {}, algebra.neg(algebra.mul(c1, q, d1)), {}, {} ],
         "FULL1 pair-0 X is not the single monomial -C1 Q D1")
    need(full1 == by_label["FULL1:0"] == by_label["IDLE:0"],
         "FULL1/IDLE pair-0 X drifted from the derivation")
    need(derived == [ {}, algebra.neg(algebra.mul(c1, q, d1)), d1, {} ],
         "derived saved bank is not [0, -C1 Q D1, D1, 0]")
    need(saved == before_query2 == derived == by_label["bridge_query2:0"],
         "bridge_query2:0 is not the pair-0 X bank saved before bridge-minus")
    need(by_label["bridge_minus:0"][2] == {} and by_label["bridge_minus:0"] != saved,
         "bridge-minus did not delete the x1 monomial that the saved copy keeps")

    operator = algebra.add(algebra.one, algebra.neg(algebra.mul(c1, q, c1)))
    need(operator == algebra.add(algebra.term((), (0, 0)),
                                 algebra.neg(algebra.term((2, 1, 2), (0, 0)))),
         "named operator is not I - C1 Q C1")
    need(len(operator) == 2, "named operator does not have exactly two monomials")
    inverse = algebra.inv(saved[1])
    need(algebra.mul(rho[1], inverse) == operator, "y0 column does not force this operator")
    need([algebra.mul(operator, column) for column in saved] == rho,
         "named operator misses the required correction")
    for term in operator:
        partial = {term: operator[term]}
        need([algebra.mul(partial, column) for column in saved] != rho,
             "one monomial of the operator already corrected the row")
        need(len(algebra.mul(partial, saved[1])) == 1,
             "a monomial image on the unit column changed support size")
    need(len(algebra.mul(operator, saved[1])) == len(operator) == len(rho[1]),
         "left multiplication by the unit column did not preserve support size")

    identity = algebra.one
    signed = algebra.neg(algebra.mul(c1, q, c1))
    identity_row = [algebra.mul(qi, identity, column) for column in saved]
    signed_row = [algebra.mul(qi, signed, column) for column in saved]
    need(identity_row[0] == {} and identity_row[3] == {}, "identity monomial touched x0 or y1")
    need(signed_row[0] == {} and signed_row[3] == {}, "C1 Q C1 monomial touched x0 or y1")
    need(identity_row[1] == algebra.neg(algebra.mul(qi, c1, q, d1)),
         "identity monomial is not -Q^{-1} C1 Q D1 on y0")
    need(identity_row[2] == algebra.mul(qi, d1),
         "identity monomial is not Q^{-1} D1 on x1")
    need(signed_row[1] == algebra.mul(qi, c1, q, q, d1),
         "C1 Q C1 monomial is not Q^{-1} C1 Q^2 D1 on y0")
    need(signed_row[2] == algebra.neg(algebra.mul(qi, c1, q, c1, d1)),
         "C1 Q C1 monomial is not -Q^{-1} C1 Q C1 D1 on x1")
    need(algebra.add(identity_row[1], signed_row[1]) == algebra.neg(coupling),
         "the two y0 monomials do not sum to -B")
    need(algebra.add(identity_row[2], signed_row[2]) == algebra.neg(extra),
         "the two x1 monomials do not sum to -E")
    need(identity_row != [{}, algebra.neg(coupling), algebra.neg(extra), {}],
         "dropping C1 Q C1 still cleared both defects")
    need(signed_row != [{}, algebra.neg(coupling), algebra.neg(extra), {}],
         "dropping I still cleared both defects")

    inserted, inserted_final, _saved, _before = schedule(
        algebra, published_f1, published_f2, insert=operator)
    inserted_by = dict(inserted)
    need(inserted_by["query4:3"] == autonomous, "insertion did not autonomize query4:3")
    need(inserted_by["response2"] == by_label["response2"],
         "insertion changed response2 or the published second operator")
    for label in PRE_QUERY:
        need(inserted_by[label] == by_label[label], "insertion rewrote a bank saved before the argument")
    need(all(inserted_final[i] != targets[i] for i in range(4)),
         "a final bank matched its uncoded target")
    need(inserted_final != targets, "the suffix produced the four uncoded targets")
    bare = [algebra.add(x, y) for x, y in zip(saved, [{}, {}, {}, {}])]
    bare[2] = {}
    need([algebra.mul(operator, column) for column in bare] != rho,
         "the same operator worked after deleting the saved x1 monomial")

    groups = {"zero-column": [], "unit-kills": [], "unique-fails": [], "works": []}
    for label in PRE_QUERY:
        if label == "response2":
            continue
        kind, payload = classify(algebra, by_label[label], rho)
        groups[kind].append(label)
        if label == "bridge_query2:0":
            need(kind == "works" and payload == operator, "witness was not the unique solution")
        elif label in UNIQUE_FAILS:
            need(kind == "unique-fails", "paired Y bank was not a unique failure")
            failed_operator, image = payload
            need(image[0] != {} and image[1] == rho[1] and image[2] == rho[2] and image[3] == {},
                 "unique failure did not clear y0 and x1 while spoiling x0")
    need(tuple(groups["zero-column"]) == ZERO_COLUMN, "zero-column census moved")
    need(tuple(groups["unit-kills"]) == UNIT_KILLS, "unit-kill census moved")
    need(tuple(groups["unique-fails"]) == UNIQUE_FAILS, "unique-failure census moved")
    need(groups["works"] == ["bridge_query2:0"], "more than one legal saved bank worked")
    need(len(groups["zero-column"]) + len(groups["unit-kills"])
         + len(groups["unique-fails"]) + len(groups["works"]) == 29,
         "legal saved-bank census is not 29")
    for label in UNIQUE_FAILS:
        need(by_label[label] == by_label["bridge_query2:1"],
             "the three pair-0 Y labels are not the same bank")
    failed_operator = algebra.add(algebra.mul(c1, qi), algebra.neg(algebra.mul(c1, q, q)))
    need(classify(algebra, by_label["bridge_query2:1"], rho)[1][0] == failed_operator,
         "unique operator on the pair-0 Y bank moved")
    spoiled = [algebra.mul(failed_operator, column) for column in by_label["bridge_query2:1"]]
    need(spoiled[0] == algebra.add(algebra.neg(d1), algebra.mul(c1, q, q, c1, d1)),
         "x0 image on the pair-0 Y bank is not -D1 + C1 Q^2 C1 D1")

    post_groups = {"zero-column": [], "unit-kills": [], "unique-fails": [], "works": []}
    for label in POST_QUERY:
        kind, _payload = classify(algebra, by_label[label], rho)
        post_groups[kind].append(label)
    need(tuple(post_groups["zero-column"]) == POST_ZERO, "post-query zero-column list moved")
    need(tuple(post_groups["unit-kills"]) == POST_UNIT, "post-query unit-kill list moved")
    need(tuple(post_groups["unique-fails"]) == POST_UNIQUE_FAILS, "post-query unique-failure list moved")
    need(post_groups["works"] == [], "a bank recorded at or after response4 corrected the row")

    response = by_label["response2"]
    need(len(response[0]) == 1, "response2 x0 column is not a unit")
    need(algebra.mul(response[0], algebra.inv(response[0])) == algebra.one,
         "response2 x0 column lost its inverse")
    kind, _payload = classify(algebra, response, rho)
    need(kind == "unit-kills", "an extra operator on response2 could preserve x0")

    ledger = {
        "scalar_adds": 2 * C1_ADDS + 2 * BANK_ADDS,
        "monomial_passes": 2 * C1_MONOMIALS + 1 * MONOMIAL_PASS,
        "mode_clears": 2 * C1_CLEARS,
        "copies": 1 * BANK_COPYS,
        "extra_fields": 2 * BANK_COPYS,
        "mode_fields_reused": 8,
        "gaussian_children": 0,
    }
    need(ledger == {
        "scalar_adds": 2016,
        "monomial_passes": 560,
        "mode_clears": 32,
        "copies": 112,
        "extra_fields": 224,
        "mode_fields_reused": 8,
        "gaussian_children": 0,
    }, "ledger arithmetic moved")
    print("PASS_SAVED_BANK_QUERY_SOURCE")
    print("saved_bank", "bridge_query2:0")
    print("operator", "I - C1 Q C1")
    print("second_operator", "C1 Q^2")
    print("row_autonomous", True)
    print("legal_banks_tested", 29)
    print("legal_banks_that_work", 1)
    print("post_query_banks_that_work", 0)
    print("ledger", ledger)
    print("new_kappa", None)


if __name__ == "__main__":
    main()
