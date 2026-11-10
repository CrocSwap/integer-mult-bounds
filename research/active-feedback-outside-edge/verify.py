#!/usr/bin/env python3
"""One named feedback edge outside the 8,281-policy family.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The predecessor schedule and group algebra are imported unchanged. No call
is added. A one-edge failure is not an unrestricted impossibility.
"""
from hashlib import sha256
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
COEFFICIENTS = ("-2", "-1", "-1/2", "1/2", "1", "2")


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
    """The 91 choices on one edge of the published 8,281-policy search."""
    operators = [{}]
    for word in search.words(7):
        for coefficient in COEFFICIENTS:
            body = tuple(word) + ((1, 1) if second_edge else ())
            operators.append(algebra.term(body, (0, 0), coefficient))
    need(len(operators) == len({tuple(sorted(item.items())) for item in operators}) == 91,
         "policy edge did not produce 91 operators")
    return operators


def before_query2(algebra):
    """Prefix of search.replay through the bridge that precedes query 2."""
    q, qi = algebra.gen(1), algebra.inv(algebra.gen(1))
    c1, c3 = algebra.gen(2), algebra.gen(3)
    d1, d3 = algebra.D(0), algebra.D(1)
    rows = [[algebra.one if i == j else {} for j in range(4)] for i in range(4)]

    def plus(dst, src, op):
        rows[dst] = [algebra.add(x, algebra.mul(op, y))
                     for x, y in zip(rows[dst], rows[src])]

    def left(index, op):
        rows[index] = [algebra.mul(op, entry) for entry in rows[index]]

    def query(pair, argument, after=None):
        response = [algebra.mul(qi, entry) for entry in argument]
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

    rows[0][2] = algebra.neg(algebra.one)
    rows[3][1] = algebra.one
    query(0, rows[0], c1)
    full(0, c1, d1)
    late = list(rows[1])
    left(2, d1)
    left(3, d1)
    bridge(0, 1, 1)
    return [list(row) for row in rows], late


def finish_query4(algebra, frozen, response, feedback2):
    """Suffix of search.replay from the saved response through query 4."""
    q, qi = algebra.gen(1), algebra.inv(algebra.gen(1))
    c3, d3 = algebra.gen(3), algebra.D(1)
    rows = [list(row) for row in frozen]

    def plus(dst, src, op):
        rows[dst] = [algebra.add(x, algebra.mul(op, y))
                     for x, y in zip(rows[dst], rows[src])]

    def left(index, op):
        rows[index] = [algebra.mul(op, entry) for entry in rows[index]]

    rows[1] = [algebra.add(x, y) for x, y in zip(rows[1], response)]
    plus(0, 2, algebra.term((), (0, 0), -1))
    plus(3, 1, algebra.term((), (0, 0), 1))
    plus(2, 3, algebra.neg(algebra.mul(q, c3)))
    left(2, d3)
    left(3, d3)
    argument = [algebra.add(algebra.mul(c3, x), algebra.mul(feedback2, y))
                for x, y in zip(rows[2], response)]
    response4 = [algebra.mul(qi, entry) for entry in argument]
    return [algebra.add(x, y) for x, y in zip(rows[3], response4)]


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
    published_f1, published_f2 = algebra.one, algebra.mul(c1, q, q)
    named_f2 = algebra.mul(c1, q)
    need(named_f2 == algebra.term((2, 1), (0, 0)), "named edge is not the word C1 Q")
    second_family = family_operators(algebra, search, True)
    first_family = family_operators(algebra, search, False)
    need(published_f2 in second_family and published_f1 in first_family,
         "published edges fell outside the 8,281-policy family")
    need(named_f2 not in second_family, "named edge is inside the second-edge family")
    need(q not in first_family, "the boundary witness's first edge is inside the family")
    need(len(first_family) * len(second_family) == 8281, "policy count is not 8281")

    frozen, late = before_query2(algebra)
    x_at = list(frozen[0])
    base = finish_query4(algebra, frozen, [{}, {}, {}, {}], published_f2)
    original_x1 = algebra.mul(qi, c3, d1, d3)
    restored = algebra.mul(d1, qi)
    autonomous = [restored, {}, original_x1, {}]
    need(base == [ {}, {}, original_x1, {} ], "zero-response row is not the original x1 job")
    need(late[1] == d1 and late[2] == algebra.neg(late[0]) and late[3] == {},
         "saved FULL1 Y lost the column linkage")
    need(late[0] == algebra.mul(qi, c1, d1), "saved FULL1 Y column 0 moved")

    def response_of(feedback1):
        argument = [algebra.add(algebra.mul(c1, x), algebra.mul(feedback1, y))
                    for x, y in zip(x_at, late)]
        return [algebra.mul(qi, entry) for entry in argument]

    def row_of(feedback1, feedback2):
        observed, _targets, final_rows = search.replay(algebra, feedback1, feedback2)
        by_label = dict(observed)
        replayed = by_label["query4:3"]
        response = by_label["response2"]
        need(response == response_of(feedback1), "response2 disagrees with the prefix")
        predicted = [algebra.add(base[j], algebra.mul(qi, feedback2, response[j]))
                     for j in range(4)]
        need(predicted == replayed, "query4 row disagrees with Q^{-1} F2 response2")
        need(finish_query4(algebra, frozen, response, feedback2) == replayed,
             "local suffix disagrees with search.replay")
        return replayed, final_rows

    # The assigned test: this named edge, with the published first edge held
    # fixed, and with no added call.
    named_row, named_final = row_of(published_f1, named_f2)
    named_x0 = algebra.mul(qi, c1, qi, c1, d1)
    named_expected = [
        named_x0,
        algebra.add(algebra.mul(qi, c1, d1), algebra.neg(algebra.mul(qi, c1, q, d1))),
        algebra.add(algebra.mul(qi, d1), algebra.neg(named_x0), original_x1),
        {},
    ]
    need(named_row == named_expected, "named C1 Q row moved")
    need(named_row != autonomous, "named edge unexpectedly autonomized the row")
    need(named_row[0] != restored and named_row[1] != {} and named_row[3] == {},
         "named blocks do not match the recorded coupling")
    need(named_final != search.replay(algebra, {}, {}, codes=False)[2],
         "named edge must not be described as the uncoded caller")

    # Cancellation that makes every response contribution equal to Q^{-1} F2 S.
    carried = algebra.mul(qi, c3, d3, algebra.neg(q), c3)
    need(algebra.mul(d3, c3) == algebra.mul(qi, c3, q, d3), "D3 conjugation changed")
    need(carried == algebra.neg(d3), "FULL3 return did not cancel the saved response")
    need(algebra.add(d3, carried) == {}, "response return is not identically zero")

    # One second-edge replacement. Restoring x0 has a unique algebra solution,
    # and that solution is the published edge, whose y0 block stays nonzero.
    bare = [algebra.add(algebra.mul(c1, x), y) for x, y in zip(x_at, late)]
    need(bare[0] == algebra.mul(qi, c1, d1), "Z0 is not Q^{-1} C1 D1")
    need(bare[1] == algebra.add(d1, algebra.neg(algebra.mul(q, d1))), "Z1 is not (I-Q) D1")
    need(bare[3] == {}, "the first edge's total argument acquired a y1 term")
    unit = algebra.mul(qi, c1)
    inverse = algebra.mul(c1, q)
    need(algebra.mul(unit, inverse) == algebra.one and algebra.mul(inverse, unit) == algebra.one,
         "Q^{-1} C1 lost its two-sided inverse")
    unique = algebra.mul(qi, inverse)
    need(unique == algebra.mul(qi, c1, q), "unique restoring factor moved")
    need(algebra.mul(unique, bare[0]) == restored, "unique factor does not restore x0")
    need(algebra.mul(unique, bare[1]) != {}, "unique factor cleared y0")
    published_from_unique = algebra.mul(q, unique, q)
    need(published_from_unique == published_f2, "the unique second edge is not the published one")
    shifted = algebra.mul(d1, unique, bare[0])
    need(shifted != restored, "a nonzero D exponent cannot restore the degree")
    # Right multiplication by the unit is injective on this algebra: the inverse
    # returns every tested element, including a D exponent and a sum.
    samples = (c3, algebra.add(q, algebra.mul(c1, c3)), algebra.mul(d1, c3, qi))
    for sample in samples:
        need(algebra.mul(algebra.mul(sample, unit), inverse) == sample,
             "right multiplication by Q^{-1} C1 was not inverted")

    # One first-edge replacement, with the published second edge held fixed.
    # Every such replacement moves x0 and x1 by opposite amounts.
    zero_first, _final = row_of({}, published_f2)
    need(zero_first[0] == {} and zero_first[3] == {}, "published second edge with no first edge moved")
    extra_x1 = algebra.add(zero_first[2], algebra.neg(original_x1))
    need(extra_x1 == algebra.mul(qi, c1, q, c1, d1), "x1 contamination moved")
    required_x0 = restored
    required_x1 = algebra.neg(extra_x1)
    need(required_x1 != algebra.neg(required_x0), "the required one-edge corrections became opposite")
    only_first, _unused = row_of(q, published_f2)
    need(only_first != autonomous, "changing only the first edge autonomized the row")

    # Boundary witness, not a one-edge result: both published operators change.
    witness_row, witness_final = row_of(q, named_f2)
    _unused, targets, _plain = search.replay(algebra, {}, {}, codes=False)
    need(witness_row == autonomous, "two-edge boundary witness missed the row")
    need(witness_final[2] == autonomous, "final image of the witness row moved")
    need(witness_final != targets, "two-edge witness is not the four target banks")
    need(all(witness_final[i] != targets[i] for i in range(4)),
         "a two-edge final bank matched its uncoded target")

    published_row, _published_final = row_of(published_f1, published_f2)
    need(published_row[0] == restored and published_row[1] != {},
         "published edge no longer restores x0 with a nonzero y0 block")
    omitted, _omitted_final = row_of(published_f1, {})
    need(omitted[0] != restored, "omitting the second edge still restored x0")
    print("PASS_ACTIVE_FEEDBACK_OUTSIDE_EDGE")
    print("named_edge", "second feedback C1 Q, first edge held at I")
    print("named_row_autonomous", False)
    print("one_edge_algebra", "no single published-edge replacement autonomizes the row")
    print("two_edge_boundary_witness", "F1=Q and F2=C1 Q autonomize the row only")
    print("new_kappa", None)


if __name__ == "__main__":
    main()
