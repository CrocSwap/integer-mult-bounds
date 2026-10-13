# Uniform owner-profile optimum for the SW4/X4 inventory

**Research consolidation; no new κ.** For every real `0 < b <= 1/3`, the idle
profile

`I* = {48:2396, 44:1, 3:1, 1:1}`

uniquely minimizes `sum_r I(r) r^(1-b)` among all whole-helper packings with
the inventory below. Different assignments with this same profile tie.
The theorem permits any fixed local paid profile: it adds the same cost to
every packing. Thus it applies to PR799 and to later local circuit changes
that preserve these packing data and admit this owner assignment.

This extends **[chafreaky's PR795](https://github.com/CrocSwap/integer-mult-bounds/pull/795)**. That work supplies the integer prices,
packing exclusions, and eleven-step concavity reduction, and proves optimality
at PR741's single admitted endpoint. Here additional integer exclusions remove
its `[43,5]` relaxation. A uniform argument then covers an entire interval,
independently of the local paid profile. It does not improve a construction.

For the current recurrence, the complete moment is
`M_b = sum_r (72 L(r)+I(r)) r (73/r)^b / (73*7168)`.
Fixing L makes its contribution constant across owner assignments; the
remaining factor `73^b/(73*7168)` is positive. Thus the idle optimum also
minimizes this complete moment. The theorem concerns this billed objective.

The practical decision is specific: changing only this owner assignment cannot
improve a moment in this interval. A search must change widths, capacities,
dispatch counts, splitting rules, or another part of the hosting contract.
Local circuit changes remain useful and are explicitly allowed by this theorem.

## Precise model and proof

There are 72 calls. Each call supplies 80 helpers of width 4, 32 of width 5,
54 of width 7, 122 of width 8, and 216 of width 9. There are 112 bins per window,
with 48 windows of capacity 8 and 32 each of capacities 16, 32, and 48.
Every helper occupies its complete width in one bin. Bin occupancies do not
overlap. Unused capacity contributes one residual rank per bin; zero ranks
contribute nothing. The theorem covers all such integer packings, including
ones that ignore native timing and helper identities. Exclusions in this
larger class therefore apply to the native whole-call model.

The total capacity is 387072, total helper width is 272016, and residual mass
is `S=115056=2397*48`. A positive residual is at most 48. A residual other than
48 is at most 44, because the smallest helper width is four.

### Integer exclusions inherited and extended from PR795

Use helper prices

| width | 4 | 5 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|---:|
| price | -1 | -20 | -8 | -2 | 4 |

and capacity bonuses `d(8)=2, d(16)=4, d(32)=8, d(48)=-13`.
Let `u(r)` be the maximum bonus plus helper prices over all possible fills
with residual `r`. Impossible residuals have no value. The finite integer
knapsack in `verify.py` computes every possible fill of capacities at most 48.

Summing over all bins gives the necessary inequality

`-31136 <= sum_r I(r) u(r)`.

The left side counts every capacity bonus and every helper price exactly once.
The calculation gives `u(0)=0`, so zero residuals can be omitted. It also gives
`u(48)=-13, u(44)=-14, u(3)=7, u(1)=19`. The profile I* attains equality.
The all-48 profile violates this inequality by 25, as in PR795.

The new exclusion checks all twelve two-part candidates `[r,48-r]`,
`33 <= r <= 44`, after 2396 residuals of rank 48. Each candidate either contains
an impossible residual or violates the same integer inequality. The exact
certificate lists every case and its contradiction. Thus any feasible
two-part remainder of mass 48 has largest part at most 32.

### Reduction to twelve analytic inequalities

Write the number of rank-48 residuals as `2397-t`. Then `0 <= t <= 2397`,
and the other residuals have total mass `48t` with each part at most 44.
Fix `0<b<1` and write `f(r)=r^(1-b)`.

Strict concavity gives the following exchange rule: moving mass from a smaller
positive part to a larger part strictly decreases their total cost, until the
smaller part vanishes or the larger reaches its cap. Iteration proves that
fixed mass `m` and part cap `C` have minimum cost at copies of `C` and one
remainder. More generally, a vector that majorizes another has no larger
concave cost; the same exchanges prove this statement here.

* `t=0` is the excluded all-48 profile.
* For `t=1`, there cannot be just one part. With two parts, the integer exclusion
  leaves the lower-cost relaxation `[32,16]`. With at least three parts,
  `[44,3,1]` majorizes every possibility: the largest part is at most 44 and
  the first two sum to at most 47. Equality holds only at `[44,3,1]`.
* For `t>=2`, use `floor(48t/44)` copies of 44 and the remainder `48t mod 44`.
  Increasing `t` by eleven adds cost `12 f(44)-11 f(48)>0`.
  This follows from `12*44=11*48` and `44^-b > 48^-b`.
  Thus `t=2,...,12` suffice for all larger `t`.

Subtract I* from each relaxation. The twelve resulting functions have the form

`D(b) = sum_r c_r r^(1-b)`.

The certificate checks, for every one of them:

1. `D(0)=sum c_r*r=0`.
2. The coefficients in increasing rank order have exactly two sign changes.
3. `D(1)=sum c_r <= 0`.
4. `D(1/3)>0`, using rational bounds on the cube roots of `r^2`.

### Why these finite checks prove an interval

We give the root-count fact used here. A nonzero generalized polynomial
`g(x)=sum_i a_i x^lambda_i`, with strictly increasing real exponents and
nonzero coefficients, has at most as many positive roots, counting
multiplicities, as coefficient sign changes.

Proof: divide by the smallest power and induct on the number of terms.
The normalized function has constant term `a_0`; its derivative has the signs
of `a_1,...,a_n`. Rolle's theorem bounds its roots by the derivative's roots
plus one. If `a_0` and `a_1` have opposite signs, this gives the desired bound.
If they have the same sign, there is an extra derivative root before the first
function root: near zero the function has sign `a_0` and moves initially in
the direction of `a_1`, so it must turn before reaching zero. Counting this
root and the usual Rolle roots removes the extra one. Multiple roots count
with one less multiplicity in the derivative. This proves the induction;
the derivative bound also ensures there cannot be infinitely many roots.

Apply this to `x=exp(b)` and exponents `-log(r)`. Reversing coefficient order
preserves the number of sign changes, and the factors `r` are positive.
Therefore D has at most two real zeros, counting multiplicities.
It already vanishes at zero. If it had another zero in `(0,1/3)`, its positive
value at `1/3` and nonpositive value at one would force a third zero in
`(1/3,1]`. This is impossible. Thus D is strictly positive on `(0,1/3]`.

The exchange rule, integer exclusions, positive period, and these twelve
inequalities prove the stated optimum for every feasible profile. Strictness
holds for every different profile. No sampling of exponent values is used.

## Independent validation

`independent.py` imports neither the primary checker nor PR795's checker.
It enumerates integer width count vectors instead of using the knapsack
recurrence, and enumerates all capped partitions of 48 to check the new
classification. Its analytic argument uses no root-count assertion or
cube-root bounds.

It multiplies D by `48^b`, removes the zero constant term, and divides by b.
Rational logarithm bounds give a degree-23 Taylor lower polynomial. Positive
omitted tails are discarded; negative tails receive an explicit geometric
bound, valid uniformly for `0 <= b <= 1/3`. Conversion to the Bernstein basis
on this full interval gives strictly positive coefficients in all twelve
cases. Since Bernstein basis functions are nonnegative and sum to one, this
independently certifies the crucial continuum inequalities.

This is a different mathematical validation of the interval step and a
different enumeration of the integer fills. It is not independent human review,
a formal proof-assistant result, or an independent reconstruction of the full
native multiplication construction. Both checkers use the stated packing
model and the written concavity/period reduction.

## Reproduce

From the repository root, with standard-library Python 3.11 or later:

```sh
python3 -B research/owner-profile-uniform/reproduce.py
```

Expected: `PASS_UNIFORM_OWNER_PACKAGE`. The command verifies pinned inputs,
recounts the archived PR799 native paid profile and all 36288 owner roles,
checks both proof models, and runs mutation and scope controls.

`SOURCES.json` pins the imported main files. The current PR799 word comes from
`native/local/` in the retained `integrated799-replay.tar.gz`, not its older
R492 evidence snapshot. This run recounts those archived records; it does not
claim a fresh native scalar/phase/controller replay. Source PR799 is
`80e6463157cfc80b85af09e7e2f14748fe2dac60`; PR795 is
`56b626800c85026b10dada646c80c6b58179b427`.

## Limits and credit

The result does not cover different inventories, call counts, capacities,
split helpers, revised hosting rules, or competing local circuits themselves.
It proves no optimum outside the stated exponent interval. Any change to a
native word still needs its own complete scalar, frame, phase, owner, and
invoice validation. All-size compilation, common-label/mutable-source
realization, whole-call hosting, precision/tape and analytic-transfer
hypotheses remain inherited. No new κ or unconditional theorem is claimed.

Credit: chafreaky supplies PR795's integer dual and concavity reduction,
PR741's frames, and the PR685/660 owner construction; Jeremy Kothe supplies
PR799's X4 exchanges and the PR699 SW4 lineage. The PR676 ends, PR664 promotions,
icekylinx's gauge, Rohan Arun's recurrence correction, DreamingOfClouds' bit
transport and eumemic's supplier retain their predecessor credit.

Charles Bethin prepared this extension with substantial OpenAI Codex assistance
in the mathematics, code, verification, and writing. Apache-2.0 applies.
Existing source files, licenses, notices, and the selected frontier are unchanged.
