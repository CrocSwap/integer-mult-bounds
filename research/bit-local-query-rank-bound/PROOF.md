# Four QUERYs with retained BIT LOCAL stage incidence

The pinned selected paired #7001 caller has 38 scalar roles per
port pair, 111 replicated port pairs, 18 independent body
variables and two real LOCAL calls per stage. Its exact target is
diagonal with head factor $q$ on every role. Keep those 36
LOCAL occurrences and that target. Allow arbitrary placement
and constant conjugation of the LOCAL, QUERY and IDLE factors,
including a fixed ambient space of auxiliary roles initialized and
returned to zero. Constant gates are invertible. The scope retains each LOCAL's original stage assignment and its
literal two-dimensional body contribution and rank-one head
transvection. [Pinned #7001 source](https://github.com/CrocSwap/integer-mult-bounds/tree/e54523517d0f03e58352e647c403a5af3e525a57/research/paired-query-only-bit)

## Independent stage derivatives

Work over F₂ and write $q=1+\epsilon$ with $\epsilon^2=0$.
Differentiate each body variable $z_s$ independently at all
$z_s=1,q=1$. Normalize every event by its value at this base
and conjugate by the accumulated constant prefix. The resulting
normalized factors all have constant term the identity.

At stage s each normalized LOCAL gives a rank-two projector P
in the body derivative and a rank-one square-zero map N in the
head derivative. Its original two local coordinates imply
$PN=NP=N$, and conjugation preserves that identity. An IDLE
serving s gives a rank-one projector. The sum of serving
projectors equals the exact diagonal target projector E_s on the
public input space A. The retained serving ranks sum to
$\operatorname{rank} E_s$ for every stage, as checked on the
actual word.

This saturation holds with clean helpers too. The full body
derivative has rank at least $\operatorname{rank} E_s$ from
its restriction to A and at most the sum of serving ranks.
Thus the images of the serving projectors are a direct sum
whose sum is exactly $\operatorname{im} E_s\subseteq A$.
On each serving image E_s acts as the identity. Uniqueness in
the direct sum implies that all other serving projectors kill
that image. In particular the two normalized same-stage LOCAL
defects annihilate each other. This argument allows the LOCALs
to be separated by arbitrary constant operations, other stages
or QUERYs.

## Head rank

On A the normalized head derivative is the identity of rank
38. Write its rank-one decomposition as UV, using the 36 LOCAL
defects and r QUERY slots. For clean auxiliary roles, compress
each QUERY defect to input and output A. Its rank is at most
one. The LOCAL terms have image in A, and their reciprocal
pairings and self-pairings stay zero under compression. The
base whole word is the identity on A, so removing its constant
factor does not change these public derivatives.

From $UV=I_{38}$, the matrix $I-VU$ has rank
$36+r-38$. On the two same-stage LOCAL indices it has a
principal $2\times2$ identity minor. Thus its rank is at
least two, so $r\ge4$. This does not require a trace or
diagonal condition on compressed QUERYs. The argument extends
the dual-number method from a fixed central cut to independent
body stages and arbitrary placement.
[Related dual-number scopes](https://github.com/CrocSwap/integer-mult-bounds/pull/6825),
[Related rank method](https://github.com/CrocSwap/integer-mult-bounds/pull/6800)

## Arbitrary idle masks with extra incidence

Retain the same 36 LOCALs and target. At each stage the IDLE
incidence cannot fall below the original required value, because
the rank of the stage derivative is at most the sum of serving
ranks. If every incidence stays equal, the rank argument above
applies. Otherwise at least one stage has an extra incidence.

For a required incidence vector $a_s$, form nested masks
$S_j=\{s:a_s\ge j\}$. The sum of the k largest mask lengths
in any realization is at most $\sum_s\min(k,a_s)$, which
the nested masks attain for every k. Thus their sizes majorize
every realization. Concavity of $r^{1-\kappa}$ makes the
nested assignment cheapest even when granting unrestricted
cross-stage mask grouping. The minimum is nondecreasing in
each required incidence.

At $\kappa=.0040075385047236$, all 18 directed profiles
with one extra incidence cost more than four paid units per
port above the original IDLE bill. The least is about
4.08432343047. Deleting every QUERY would rebate only four
per port. Thus an extra body incidence cannot make this
lower-QUERY proposal price-positive, even with all packing
and realization barriers waived. This concerns the retained
LOCAL count and stage assignment, and the original rank-one QUERY and body-only IDLE charging rules.
An IDLE mask contains distinct stages and pays rank seven per stage.
Combined higher-rank QUERYs, altered IDLE operators and interfaces
that erase live auxiliary data are outside this scope.

The independent replay checks 1,444 original polynomial
coefficients, all 18 stage derivatives, and the head rank.
Changing one QUERY to a constant ADD keeps the base and body
derivatives but changes the head derivative by rank one.
Omitting one IDLE stage changes just that stage derivative by
rank one. A two-helper padding control uses the added lanes
inside a LOCAL and a QUERY and preserves all ranks. No caller
with a smaller paid bill was built.

Run with CPython 3.12 and assertions enabled from the repository root.

```sh
python3.12 -I -B research/bit-local-query-rank-bound/verify.py
```
