# Exact common-child versus ADD tradeoff on dirty outputs

## Contract

Fix any q>=1 and bit-vector width w>=1. The q required output rows start at
independent arbitrary values a_i in F2^w. Every common oracle P_i performs
`A_i ^= p`, where p is the same arbitrary source-dependent value on every
call. Its inputs are read-only and disjoint from all A rows. The oracle is a
**complete call**: its own source preservation, scratch restoration and other
caller obligations are included in its tariff. It changes no other output.

The only row operations are `ADD(i,j): A_i ^= A_j`, i!=j. Every such gate is
paid. There is no extra helper, clean row, COPY, CLEAR, free basis change,
SWAP, or observation of intermediate outputs. Words are fixed straight-line
words independent of the input values. The endpoint required here is

    A_i = a_i XOR p, for every i.

Optionally, independent private complete oracles T_i toggle only A_i by t_i,
with fixed positive tariffs nu_i. The endpoint then also includes t_i.
Such calls may interleave arbitrarily. We prove bounds allowing that freedom;
our attaining construction puts the private calls last. The result is uniform
over p, t_i and all dirty values. It does not assert arbitrary physical
providers can realize this interface at any given price.

## Lemma: a row cannot be an ADD destination exactly once

Project the whole computation onto the coefficients of the q independent dirt
symbols a_i. The projected state is a q by q binary matrix M, initially I.
Common and private oracles do not change M. Each ADD is an elementary
invertible row operation, so every prefix M is invertible.

Suppose row i is an ADD destination exactly once. Before that gate its dirt
row remains e_i. At the gate it becomes e_i+M_j for some distinct source row
j. Invertibility of the prefix implies M_j!=0. Row i is never again changed
by an ADD, so its final dirt row differs from e_i. This contradicts the
required identity dirt map. Hence a destination row occurs at least twice.

The argument concerns original dirt coefficients, not just the clean map or
the common-product coefficient. It permits arbitrary gate order, feedback,
oracle multiplicity, and interleaved independent private calls.

## Theorem 1: exact count frontier

For 1<=r<=q, the minimum number of ADDs among words with exactly r common
oracle calls is

    N_ADD(q,r) = 2(q-r).

Let O be the set of rows receiving at least one common oracle call. It is
nonempty, since the endpoint depends on p. Every row outside O must acquire
p through an ADD into that row. By the lemma it is an ADD destination at
least twice. Therefore

    N_ADD >= 2(q-|O|) >= 2(q-r).

For equality, partition the rows into r nonempty blocks. In each block pick
a root h and execute

    A_i ^= A_h      for every nonroot i in that block
    P_h
    A_i ^= A_h      for those same nonroots

The root changes from a_h to a_h+p. Each nonroot changes from a_i through
a_i+a_h to a_i+a_h+(a_h+p)=a_i+p. The blocks are disjoint. There are exactly
r common calls and twice as many ADDs as nonroots. Private calls, if needed,
then add each t_i once, yielding q+r total complete child calls.

No scratch buffer or child uncompute is used. Every gate is an involution;
the exact inverse reverses the entire word, including private children.
The inverse has the same bill and restores all initial dirty rows. If a caller
requires this inverse as a separate stage, it must pay that stage as well.

The quantified theorem does not address fixed r>q or allow a larger alphabet.
The checker exhausts full affine-state spaces only for q<=3. The written
argument, rather than that finite computation, establishes the all-q claim.

## Theorem 2: destination-dependent positive tariffs

Assume ADD(i,j) costs alpha_i>0 independently of j, and P_i costs mu_i>0.
Prices are stationary and additive. The exact minimum, with arbitrary finite
common-call multiplicity, is

    C* = min over nonempty O subset {0,...,q-1}
         [ sum_{i in O} mu_i + 2 sum_{i not in O} alpha_i ].       (1)

For any word take its actual common-oracle support O. At least one P_i is
paid for each i in O, and every i outside O is an ADD destination at least
twice. Positivity makes all remaining calls nonnegative additional work,
proving the corresponding bracket as a lower bound. Since every nonempty O
is allowed in (1), its minimum is a global lower bound.

Conversely, pick any nonempty O. Let one root h in O serve all rows outside
O using its two-wave echo, while every other root in O forms a singleton
block. This pays exactly the bracket in (1). It preserves arbitrary dirt,
so it proves attainability, not just a cost relaxation.

An explicit optimizer is obtained by setting d_i=mu_i-2 alpha_i. Include
every negative d_i. If there are none, choose one index minimizing d_i.
Zero d_i can be included or omitted subject to nonemptiness. Add the fixed
private bill sum_i nu_i when private outputs are required. Each independent
t_i requires its own oracle at least once, and the construction attains that
minimum, so permitting extra private calls cannot lower the result.

This is an all-parameter written proof for arbitrary positive real tariffs.
The numerical verifier uses positive integer tariffs; rational/real tariff
coverage comes from the argument above. Edge-dependent ADD prices, scheduling
constraints, variable frame prices and simultaneous operations are outside
the claimed optimum. For them (1) is not automatically the right model.

## Fully charged consequence at uniform prices

For common-child price mu and complete full-width ADD price alpha, the fixed-r
common-product bill is r mu+2(q-r)alpha. If all q private children have price
nu, the total is

    q nu + r mu + 2(q-r)alpha.                              (2)

The dependence on r is affine. If mu>2 alpha, r=1 minimizes (2); if mu<2 alpha,
r=q minimizes it; if mu=2 alpha, every r ties. Thus a second dirty output
anchor cannot strictly improve the complete homogeneous work bill over both
endpoint choices. A lower parallel depth would be a different objective.

At q=112 and nu=mu the endpoints are 113 mu+222 alpha and 224 mu. At r=2
the bill is 114 mu+220 alpha. The additional child removes exactly two ADDs,
so the new point cannot beat both endpoints. This is a paid-child tradeoff,
not a scalar-count improvement or a selected recursive-moment substitution.

Heterogeneity can change the conclusion. For q=3, alpha=(10,1,10) and
mu=(1,5,1), roots O={0,2} cost 1+1+2=4, compared with 7 for three direct
common calls. The best single root costs 23. These are exact abstract complete
tariffs, plus any private bill, not measured physical prices.

If mu(n) and alpha(n) are complete recursive-child and ADD costs at a fixed
width n, the comparison holds pointwise whenever those costs satisfy this
stationary model. A physical recursive conclusion still needs an actual
caller, legal target/source routes, frames, storage, precision and a proved
complete price model. Unknown terms cannot be discarded as zero. This lemma
does not derive a new supplier, kappa or multiplication theorem.

## Attribution and proof level

Cinna Davis's PR1944, head 4e5159867eeb161995bdb3b51dfd184be1ce90cf, supplies
the one-common-child dirty echo and its sharp 2(q-1) bound. The retained
predecessor is research/dirty-output-anchor-seed-da1ec3f0; SOURCES.json pins
its proof and README. The contribution here is the arbitrary-multiplicity
frontier, destination-weighted optimum and resulting complete tariff decision.
PR1968 instead accumulates different common products before one fanout wave
pair; that remains a separate contract. The predecessor's PR1872 clean-helper
and PR1907 clean-output lineage retain their credit.

New proof/checker by Ross Richardson, with substantial OpenAI Codex assistance,
Apache-2.0. This is a written algebraic proof with exact finite checks and an
independent automated internal mathematical check. It is not independent human
review or formal-kernel verification.
