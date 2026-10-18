# Fixed-map butterfly experiment: scope and accounting

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0; predecessor attribution is in README.md.

The object is Alluri's PR681 exact eight-register matrix, retained at the pinned
repository base, in Jeremy Kothe's historical PR622 raw K-triangle constructor.
Its inputs include arbitrary helper dirt. All eight output rows, including the
four complementary coordinates, are fixed. Register permutations are charged
as actual operations. No clean-helper assumption, altered complement, free
output permutation or additional persistent scratch is allowed.

## Exact factorization criterion

For execution-order elementary matrices E_1,...,E_k, the resulting map is
E_k ... E_1. An addition is z_t <- z_t + q z_s (t != s); a scale is
z_t <- q z_t. Additions must have dyadic q; scales must be signed powers of two.
The finite recipe classes in SEARCH.json use explicit input/output butterfly
changes and deterministic elimination of the remaining exact matrix. The
recipe inventory and tie-breaking rules are implemented in factor.py.

No conclusion is drawn about other butterflies, elimination orders, intermediate
bases, larger circuits, helper stock or supplier architectures. In particular,
this bounded enumeration is neither a global circuit lower bound nor evidence
that a larger kappa cannot exist.

The submitted closest witness is checked independently against M, M^-1, M^-T
and M^T. The checker executes eight arbitrary input basis columns using scaled
integers, and independently inverts the explicit target matrix with rational
Gauss-Jordan elimination. Linearity makes this an exact finite matrix identity,
not a sample over clean data. Every primitive lowering also executes a ninth,
arbitrary private-work input column and must erase its influence and end with
private work zero. This is cleared private workspace, not public helper erasure.

## Primitive price and retained local allowance

The incumbent PR681 word contains 34 macros and costs 128 primitives per real
component under its historical Horner lowering. Sagar Thakrar's accepted PR696
lowering reduces that to 81. Every comparison includes source reads, private
initialization/copy, doublings, halvings, signed accumulation, sign changes and
private clears. A unit addition costs two under PR696 (unit update plus work
clear). A nonunit dyadic addition costs the historical Horner bill minus one.
A scale costs its binary shift count plus one when negative.

A full raw invocation contains fourteen windows and fourteen inverse cleanup
windows. Complex operations require two real components. Consequently a local
PR696 difference d contributes 14 * 2 * 2 * d = 56d primitives per orientation.
The complete raw forward and inverse-transpose scalar streams are rebuilt and
executed. Their measured cost differences must agree with this local price;
unchanged operations are retained in both complete bills. No saving from a
predecessor is added to another headline without composing the actual words.

## Physical and recurrence boundary

Each of the eight registers in each historical window enters at its own
rank-three frame and leaves at that block's rank-four frame. Every scalar
operation in a replacement is at the same block frame. There is no interleaved
external read within a window. Touching all eight registers therefore gives
the same eight frame climbs, regardless of the order of first touches.
All fourteen physical register lists, entry/exit frames and literal original
windows are rebound to a fresh execution of the unchanged constructor.
Cleanup is regenerated as the literal inverse of the full non-target word.

The native replay compares compensation, endpoints, helper inventory, paid
profile and directed phase-edge inventory. Thus every recursive child width
is unchanged. The homogeneous child-cost term of the inherited recurrence is
unchanged; even a scalar improvement would only change this finite invoice.
There is no proposed improvement to the selected exponent.

Native all-column scalar/frame replay is not a new full Clifford phase proof,
whole-owner hosting replay, selected-provider admission or analytic theorem.
All-size compilation, common-label/mutable-source realization, whole-call
hosting, uniform precision/tape and analytic transfer remain inherited.
The selected PR799 frontier and upstream source files are not changed.

## Enumeration algebra and negative scope

Let P be a chosen input-prefix matrix and B the chosen output prefix.
Elementary column operations compute M P^-1 in prefix execution order.
The residual elimination records R with R B M P^-1 = I. Inverting its complete
recorded output word (R B) yields M P^-1; executing P first therefore gives M.
Identical elementary generators combine only across commuting operations.
Every generated word is additionally checked on all eight dirty basis columns
with integer numerators and powers-of-two denominators. The independent
witness checker uses separate code and independently derived inverse targets.

The retained nearest witness fails the original 87-gate circuit sufficient envelope test
at `cleanup: endpoint growth increased`. No envelope domination or precision
improvement is asserted. Full native prefix measurements and the four local
envelope comparisons are separate receipt fields. The search's cost-only
negative result holds before imposing this additional restriction: a subset
passing stricter precision requirements cannot contain a cheaper member.

The complete primitive projection is not the entire local compiler allowance.
For the pinned invoice formula at m=73, C=64*(m+1)^3=25,934,336 and
A=16*(macros+children+registers+centers)+64*m. Children=3,472, registers=716 and
centers=8 are unchanged; macros increase by 224. Thus A grows by 3,584 and the
local PR696 recount grows by 3,584*C+672=92,948,660,896. The nearest witness is
inferior on this broader bill as well. We do not claim a total-local-cost
minimum across the enumerated family: the enumeration's objective is explicitly
primitive count, and the local recount is for the retained nearest witness.
