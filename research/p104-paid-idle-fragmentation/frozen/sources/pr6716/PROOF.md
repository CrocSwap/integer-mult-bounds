# A common-idle root with a new independent continuation

This is a conditional construction at the exact native boundary of PR6702.
The proof uses no approximate border, limiting parameter or unpriced
Gaussian repair. New notation below describes the actual emitted word.

## 1. Normalize the actual central operator

Let `q=Q^-1` be the source central Gaussian. The source physical checker
verifies `q^2=X`, where X is an ordinary translation with phase+1, and
`X^2=I`. Set

```text
lambda     = (1+i)I/2 + (1-i)X/2,
lambda^-1  = (1-i)I/2 + (1+i)X/2,
S = lambda*q.
```

Then `lambda^2=X`, `S^2=I`, and `lambda^-1*S=q`. All commute with the fresh
stage operators. A native full supplier `D U(q)` becomes `D U(S)` by
ordinary lambda conjugation on its query destination; an ordinary ADD
changes this to `D U(S-1)`. A thin query receives the same conjugation
and retains its paidH1 charge. Each emitted LAMBDA uses the retained
four-operation in-place two-address-pair map. It adds no productive input.

For each positive column multiplicity f, these formulas use the actual
global `q_f` and its square. The coefficients of lambda remain outside the
tensor power. In general this S is not the tensor power of a one-column S.

## 2. The exact root and its common idle subspace

`ROOT.json` lists the nine rational rank-one square-zero matrices R_i,
ordinary native bases and five commuting coordinate projectors P_i.
All coefficients are dyadic. The full sites are0,1,2,7,8. Direct exact
multiplication gives

```text
(I-2R_8) ... (I-2R_0) = -I_8.
```

At every full site, `P_i R_i=R_i P_i=R_i`, and P_i commutes with its
complete query prefix. Consequently each independent stage factor can
move past its query prefix. The plus/minus central characters give
`S*diag(stage products)`. The checker also multiplies the 64 combinations
of the two central characters and five stage nodes{1,2}. Degree at most
one in each independent stage variable makes this an exact coefficient
check, not a numerical sample.

The stage supports, in the eight input/output coordinates, are

| Site | Support | Rank |
|---|---|---:|
|0|0,1|2|
|1|0,1,6,7|4|
|2|0,1,6,7|4|
|7|0,2,4|3|
|8|0,2|2|

The eight Gaussian output masks are

```text
ABCDE, ABC, DE, empty, D, empty, BC, BC.
```

For the actual single ordinary basis C used across sites 1 and 2,

```text
C^-1 R_1 C = E01,       C^-1 R_2 C = -E10,
C^-1 P_1 C = C^-1 P_2 C = diag(1,1,1,1,0,0,0,0).
```

Both queries and both child suppliers touch only the first two active
coordinates and their separately named binary auxiliaries. Coordinates2
and 3 are neither read nor written by these operations. Each therefore
needs exactly `D_B D_C` on its own unchanged payload. The B and C axes
are disjoint fresh blocks; their two positive transforms combine into
one rank-`8(B+C)` job on each of these two coordinates. The emitted IDLE
opcode pays **two** such jobs. It does not treat two independent arrays
as one call or copy an input to gain another target.

The remaining rank-three site 7 pays its single wholeD idle. All native
two-field work and 17 thin queries remain paid.

## 3. Binary suppliers and the complete source interface

Use the retained binary query extension on child sizes `(4,2,3,4,5)`.
Its13 internal node sizes are `{2:8,3:2,4:2,5:1}`. Each internal node has
its own two arbitrary productive auxiliary inputs, two charged whole
idles and one paid thin query. The resulting unretired caller has 34
independent main inputs. None is assumed zero or supplied by copying
another productive input.

The18 LOCAL invocations are the exact PR6702 native word, in stage order
1 through 18. Every invocation gets all 563 independent native helpers,
the same771 public native labels and 29 owned labels. The47 native owned
lifetimes, peak14 and 18,577-event program are unchanged. Lambda and basis
maps occur only on main fields outside the source invocation. Thus
arbitrary-input native correctness applies to their current contents.

## 4. Source-specific two-sided cut

Let P be the literal unretired prefix through zero-based event 353, after
the lambda return following its first D-child thin query. This D child
contains fresh stages 10 through 13. Main fields 4,20,21 have the same
complete `S D` target after ordinary output normalization. Set

```text
a = e1^T - e20^T + e21^T,
b = -2e0 + 2e2 - 2e20 - e21,
c = e20^T - e4^T,
d = -e4 - e21.
```

Exact full-ring checks give

```text
ab = cd = 1,       aP = S c,       Pd = S b.
```

These identities retain all 18 distinct stage variables and `Q^4=I`.
They do not specialize the central square to identity. All four vectors
are ordinary rational dyadics; no unavailable S or stage transform is
hidden in a basis coefficient.

The literal ordinary words G and J in WITNESS.json satisfy

```text
e4^T G = c,       Gd=e4,
e4^T J = a,       Jb=e4.
```

G has three gates and J six. Applying `G^-1` at input and J at the cut
makes the pivot row and column of `J P G^-1` exactly `S e4`. It is
therefore `S ⊕ K`, with no coupling to any other independent input.
G mixes only fields 4,20,21 with equal complete normalized targets, so
G commutes with the complete endpoint. The matching suffix has pivot
block D and no coupling to the other fields.

Return the completed S pivot. Give that suffix a **new independent input**
in field34, and rename pivot4 to 34 in `J^-1` and all later gates, including
the final G. No gate touches field34 before this handoff. The two inputs
then receive S and D separately in place of one S D. Restore lambda on
the original group. The original pivot receives q and the new field
receives the plain rank 32 Gaussian, with no earned central factor.

The final caller has 35 independent main inputs and 586 instructions.
Forward and reverse-row engines check all 1,225 coefficient positions;
deleting the input basis, handoff or return, or giving the fresh field
an extra central target, is rejected. Every paid job before and after
retirement has the same stage set, sign and chronological order.

## 5. Full invoice and strict improvement

Count every LOCAL helper target/paid call18 times, every thin query104
times, both fields of every paired idle, the individualD idle, and all 35
main outputs. The independent formula equals the literal event/endpoint
invoice. The totals are13,774 productive fields,66,956 paid jobs,
target rank mass179,048 and paid rank mass178,288. Their surplus is 760.

For `H_r=r^t`, `0<t<1`, subtracting PR6702's **complete** signed invoice
gives exactly

```text
104*(H1+H16-H17) + 208*((H41-H40)-(H57-H56)).
```

Strict subadditivity makes the first term positive. The increment of
a strictly concave function decreases with its argument, so the second
is positive as well. The difference has zero linear rank mass. There
is one literal new retirement; “second-retirement-equivalent” describes
this signed comparison, rather than an extra operation assumed for free.

Two independent rational engines enclose the raw crossing in
`(0.0033042804235,0.0033042804236)` and prove the tested moment positive
at 0.003304205. A uniform negative derivative throughκ=.0034 proves
uniqueness. The claimedκ=.00330420 is strictly smaller than the tested
saving. The previous raw crossing is strictly below the new claim.

## 6. Fresh completion, compiler and ordinary constants

The old12/13 completion is invalid for this invoice: its completion ratio
is greater than one. The new cutoff 11, floor 12, offset 1/7, power 1920 and
decay 31/32 give all three charged ratios below one and a strict finite
completion bound. Splitting and rounding keep every paid rank below
every completed target rank. The explicit compiler uses logarithm
power 2100, theta 63/64 and strict grid gap `(tested-claim)/7`.
Its winning uniform rank is specified by `N=2^138100200000000`, with the
adjacent previous grid point rejected. The winning word is not materialized.

Ordinary constants are recounted from this word. `scalars.py` lowers each
actual rational scalar through binary Horner/halving operations, including
the new coefficient 37, and separately bounds every instruction's coefficient
height. No old maximum coefficient 16 is inherited. The110 global lambda
normalizations, all 586 caller instructions,18 native scalar/route bills,
all 35 output adapters and all thin-query work give the fresh conservative
ordinary upper bound 252,020,208, below10^9. Native owned storage remains
uncredited; thin queries reuse their uncredited copied-query stream.

For the completely expanded finite compiler, use its actual counts W of
productive roles, P of rank-one paid children, U of raw source invocations,
R of all monomial routes and normalizers, and O owned banks. Allocate one
bank for every live owned lifetime, or conservatively every compiled raw
instance/lifetime; do not reuse a live parent bank at another instance.
Use a fresh coefficient envelope `G=10^9 U+8R` and replace all finite
template constants, for example

```text
Z=W+O,
E=64*(Z+N+P+G+1)^3,
B=P+E,       C0=32*N*B^2.
```

The completed-child semantic recurrence has the same retained form
`A(e) <= A(floor(e/N)) + P*floor(e/N) + E`, hence a linear bound in e.
Every child is completed on the shared fine grid before the parent resumes.
All changed basis work is fixed and counted in G. Each newly named
productive source appears once; owned banks earn no output credit.
The source's admitted whole-job/movement/precision interfaces are still
assumptions. Under those same interfaces, huge fixed constants change
eventual thresholds rather than the precision exponent or stock exponent.

Finally, the retained ordinary/admitted BIT record and all 54 strict plus4
functional outer inequalities are recomputed at the new saving. No old
tail rejection, ordinary-work constant or selected result is silently reused.

## Open next questions and scope

Independent scientific review should first inspect the common idle bank
and the four exact cut identities, then replay the unchanged source and
the new physical/invoice checks. A further κ gain needs a changed paid
profile or target contract; the fixed-invoice ceiling is already enclosed.

The same five quantified framework assumptions remain. No full formal
integer-multiplication proof, practical speedup, materialized winning word,
selected-frontier update or external scientific admission is claimed.
Predecessor methods and authors retain the credit specified in README.md
and the unmodified source notices. New application and proof: thu-nmrc
with substantial OpenAI Codex and parallel-agent assistance. Apache-2.0.
