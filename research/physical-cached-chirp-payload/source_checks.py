"""Portable exact source controls; independent phase oracle is separate.

@CubeJerry, with substantial OpenAI assistance. Apache-2.0.
"""

from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rejected(operation, message):
    try:
        operation()
    except ValueError:
        return
    raise ValueError("negative control was accepted: " + message)


def run(C, I):
    fixtures = (((8, 4), (7, 3), 1, 10, 0),
                ((4, 2, 4), (3, 1, 5), 3, 8, 0),
                ((2,), (-7,), 1, 0, 0),
                ((32, 8, 16), (31, -19, 7), 4, 7, 0),
                ((256, 2), (10**30+1, -3), 3, 0, 0),
                ((8, 4), (7, 3), 1, 2, 24))
    receipts = []
    for radices, slopes, radius, target, incoming in fixtures:
        bundle = C.prepare(radices, slopes, radius, target, oracle=I,
                           incoming_precision=incoming)
        p = bundle.plan
        require(p.f >= incoming, "incoming precision preserved")
        require(p.payload_l1_error <= Fraction(1, 1 << target), "error allocation")
        require(p.table_component_error == Fraction(2, 1 << p.f), "two-ulp contract")
        require(p.W > p.f and p.W >= max(t.bit_length()+1 for t in radices),
                "record/field carrier")
        require(len(bundle.tables) == len(radices), "axis extent")
        for t, s, table in zip(radices, slopes, bundle.tables):
            require(len(table) == t and table[0] == (1 << p.f, 0), "table extent/zero")
            for x, point in enumerate(table):
                require(I.in_disk(point, p.f), "unit disk")
                phase = (-s*x*x) % (2*t)
                if (4*phase) % (2*t) == 0:
                    quarters = ((1 << p.f, 0), (0, 1 << p.f),
                                (-(1 << p.f), 0), (0, -(1 << p.f)))
                    require(point == quarters[(4*phase)//(2*t)], "exact quadrant")
        shifted = tuple(s + (2*t)*(i+3) for i, (s, t) in enumerate(zip(slopes, radices)))
        equivalent = C.prepare(radices, shifted, radius, target, oracle=I,
                               incoming_precision=incoming)
        require(bundle.tables == equivalent.tables, "exact slope-period reduction")
        receipts.append(bundle.receipt())

    bad = (((), (), 1, 0), ((2,), (), 1, 0), ((1,), (1,), 1, 0),
           ((6,), (1,), 1, 0), ((2,), (2,), 1, 0),
           ((2, 4), (1, 3), 1, 0), ((2,), (1,), 0, 0),
           ((2,), (1,), 1, -1), ((True,), (1,), 1, 0))
    for args in bad:
        rejected(lambda args=args: C.allocation(*args), "invalid source parameters")
    rejected(lambda: C.allocation((2,), (1,), 1, 0, -1), "negative input precision")

    # f=2, q=8: step=64. An interval crossing the half-grid boundary
    # has an inward encoded point at 64, whose farther endpoint is65 away.
    # Thus replacing the two-ulp certificate by one ulp is demonstrably false.
    zero = I.Interval(0, 0, 8)
    boundary = I.Interval(127, 129, 8)
    point, _ = C.certified_inner_point((boundary, zero), 2, I)
    require(point == (1, 0), "inner endpoint control")
    actual_endpoint_error = Fraction(129 - 64, 256)
    require(Fraction(1, 4) < actual_endpoint_error < Fraction(2, 4),
            "one-ulp false control")
    negative, _ = C.certified_inner_point((-boundary, zero), 2, I)
    require(negative == (-1, 0), "negative inward endpoint")
    crossed, _ = C.certified_inner_point((I.Interval(-1, 1, 8), zero), 2, I)
    require(crossed == (0, 0), "zero-crossing inward endpoint")
    rejected(lambda: C.certified_inner_point((I.Interval(0, 65, 8), zero), 2, I),
             "enclosure wider than one ulp")
    rejected(lambda: C.certified_inner_point((I.Interval(256, 256, 8),
                                              I.Interval(256, 256, 8)), 2, I),
             "unit disk violation")
    return {"fixtures": receipts, "invalid_parameter_controls": len(bad)+1,
            "wide_enclosure_rejected": True, "nonunit_point_rejected": True,
            "one_ulp_counterexample": str(actual_endpoint_error),
            "negative_and_zero_crossing_controls": True}
