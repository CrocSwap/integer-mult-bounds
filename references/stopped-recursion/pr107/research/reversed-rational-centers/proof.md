# Why the order-only refinement composes

This argument is conditional on the complete interfaces in PR104. It proves
the compatibility of the local change, not those interfaces themselves.

For a fixed pair `(a,b)`, let the leaves be the independent scalar variables
indexed by triples `{a,b,i}` with `i` different from `a,b`. For any permutation
of these leaves, the prefix strictly before a leaf and suffix strictly after
it have disjoint supports. Adding them produces exactly the sum omitting
that leaf. Thus reordering changes neither a pair-total output nor any
leave-one-out output. The h24 disjoint-center circuit is untouched.

Every intermediate prefix or suffix still has the common pair `{a,b}`.
Its triple indicator vectors are pairwise orthogonal over F2, each with
self-pairing one. Their span is therefore nondegenerate with dimension
equal to the number of included leaves. An addition joins disjoint leaf
sets, so its source frames nest in its target frame. Existing support-based
reuse is valid because identical support specifies the same scalar form
and the same frame in this class. The retained generator verifies these
facts for every active node, and the exact scalar scatter identity remains
unchanged. In particular the center decoder is still division by 21.

The selected permutation sorts by pair-partner membership first and by
descending coordinate second. The inherited matcher works on the resulting
DAG. Every selected carrier must share the appropriate input, satisfy frame
inclusion, respect the inherited rank/temporal ordering, and use a distinct
matching endpoint. Its residual histogram, including output and retained
center calls, is recomputed from that concrete matching. No optimal-weight
matching claim is made or needed.

The same copied-center transformation replaces exactly 24 width-24 cleanup
calls by width-one calls, retaining all width-23 transforms. For `h=24`,
`v=binomial(24,3)`, `R=44918`, let `B=vR`, `N=v²`, `m=h²`,
`W=2N+2B`, and `L=2v h(h−1)`. The complete child list has `2B` children
of width `m−h`, `2N` of width `(h−1)²`, `4N` of width `h−1`,
`2v H'[r]` of each producer width `r`, and `N` additional width-one calls.
It has total rank `Wm−N+L`. All these classes remain paid.

The source-pinned verifier checks this rank identity and an exact rational
upper bound on the complex moment at `b=7799647191/10^14`. The enclosure
uses the inherited atanh logarithm series and rational exponential bound.
The next point on this specified grid fails that enclosure; this is an
arithmetic boundary for this certificate, not a global lower bound.

All geometry parameters, selected dimension, scalar node counts, row-stock
rules and denominator remain those of PR104. Its finite bridge is recomputed
from the complete selected profile. With actual bit saving
`803380799/10^13`, phase stop `β=10^-6`, and assembly bit parameter
`a=min(actual_bit,(1−β)b−10^-10)`, the inherited assembly supplies 47
strict inequalities and seven margins. The minimum margin strictly exceeds
`κ=7798412662809/10^17`. The following point on that final grid fails the
selected assembly margin. The source-pinned exact certificate records all
values. This concludes only the conditional finite refinement.
