"""Share the encoded radix validator while retaining small-q Count division.

Produced by Nick Petalas. Apache-2.0.
Based on David Arias's fresh_rows quotient and ToikY's shared-radix method.
"""

from contextlib import closing

from cardinal_counts import Count, positive
from cardinality import radix_power
from words import need


def quotient(fresh, context, families):
    """Opt-in refinement on valid fixed q, m and encoded modulus q**w.

    No runtime exponent is decoded. The fixed m**2 loop is unrolled control;
    radix_power yields at most the fixed residue-word bit width times.
    """
    positive(fresh)
    unused = Count(fresh)
    try:
        need(unused.divide_small(families) == 0, "complete fresh family factor")
        need(unused.divide_small(context.codes.size) == 0,
             "complete fresh GL low factor")
        with closing(radix_power(context.ring, context.q)) as powers:
            first = True
            for _ in powers:
                if first:
                    first = False
                else:
                    for _ in range(context.dimension * context.dimension):
                        need(unused.divide_small(context.q) == 0,
                             "complete fresh high factor")
        need(not unused.zero(), "nonempty unused row quotient")
        return unused
    except ValueError:
        unused.close()
        raise
