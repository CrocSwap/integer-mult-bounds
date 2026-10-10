# A constructive sufficient region for the displayed assembly arithmetic

Prepared 2026-10-10 with substantial OpenAI assistance. Apache-2.0.
Arithmetic diagnostic only; not an official OpenAI release or endorsement.

## Result and scope

The selected repository witness is unchanged:
κ = 330942774629799 / 500000000000000000.

We give an explicit rational construction satisfying the selected assembly's
displayed inequalities over a whole region, rather than a list of isolated
diagnostic examples. Retaining the source's scalar-domain preconditions
`0 < h < 1/2` and `κ > 0`, and assuming abstract positive bridge gaps,
the exact κ ranges of this system, restricted to rational κ, are:

- Retaining all 47 displayed inequalities: every 0 < κ < 1/33 is realizable;
  1/33 is the unattained supremum.
- Excluding only `b_below_one_over32`: every 0 < κ < 1/4 is realizable;
  1/4 is the unattained supremum.

These are ranges of a rational inequality system. They are **not improved
multiplication bounds, a theorem-domain extension, or valid new finite bridges**.
The production guard is retained by default in the diagnostic code and is not
edited in the repository. No pre-existing repository program is run.

In addition to the 47 displayed slacks, the actual assembly function calls
`validate_shared_bridge(finite_bridge, complex_row)` and requires that the
requested bit saving is at most the bridge's actual ordinary saving. Neither
gate is established for the hypothetical constructions here. The literal scalar
gap and row-degree gap below are independent positive assumptions, represented
by 1 in examples. They are not substitutes for a genuine bridge validator.

Finite suppliers, complete word realization, moment enclosures, uniform
recursion, routing, prime supply, precision/recovery and analytic fixed-tape
interfaces remain unproved for these hypothetical parameter rows.

## Pinned source and credit

All comparisons refer to main at
`3b6b66891c0ac888521cf591fe306c6286601d4f`, not an evolving PR frontier.

- [Selected assembly equations](https://github.com/CrocSwap/integer-mult-bounds/blob/3b6b66891c0ac888521cf591fe306c6286601d4f/research/coordinated-frames-and-entrance-banks/arithmetic/balanced_shared.py)
- [Main's arithmetic-domain audit and its requested whole-region proof](https://github.com/CrocSwap/integer-mult-bounds/blob/3b6b66891c0ac888521cf591fe306c6286601d4f/docs/research/assembly-domain-audit.md)
- [Romain Hedouin's PR #183, fixed-domain reduction of the 47 constraints](https://github.com/CrocSwap/integer-mult-bounds/pull/183)

The balance a/(1+a) and the necessary caps 1/33 and 1/4 are existing results,
not claimed as new. The assembly lineage credits Zhihao Chen (PR23/29), the
RaD project, James Chang (PR34), icekylinx and Rohan Arun (PR100/103/141), with
the selected supplier composition by Dugongue and its credited dependencies.
The domain audit is by Douglas Colkitt with OpenAI Codex assistance.

The candidate contribution is a constructive sufficient-region lemma beyond
the 1/32 guard, proving the diagnostic Gaussian cap is sharp for the displayed
arithmetic. PR183 supplies related reductions inside the original domain.
No global novelty or priority claim is made.

## Constructive lemma

Let a, b and κ be rational and satisfy

    0 < a < 1/3,   a < b,   0 < κ < G₀ := a/(1+a).

For a natural saving interpretation one may additionally choose b < 1; both
corollaries below choose b < 1/3. Set

    d = G₀ − κ,
    β = (b−a)/(2b),
    h = min(1/8, (1−3a)/(4(1+a)), d/(6a)),
    q = a(1−2h), ε = (1−h)/(1+q), G = εq,
    c = q+h/4, r = G+h/2, δ = h/8,
    τ = 1−a, σ = 1−b, λ′ = 1−q, λ = (τ+λ′)/2.

Assume the literal scalar gap and row-degree gap are strictly positive. Then
all displayed slacks except the explicit 1/32 cap are strictly positive,
all seven margins exceed κ, and their minimum is G.

### Basic bounds and the target margin

Every entry in the minimum defining h is positive. Thus 0 < h ≤ 1/8 < 1/2,
0 < q < a < 1/3, and 0 < ε < 1. Also 0 < β < 1/2 and

    L := (1−β)b−a = (b−a)/2 > 0.

Exact subtraction gives

    G₀−G = ah [(3+a)−2h(1+a)] / [(1+a)(1+a−2ah)].

Its numerator and denominator are positive. The expression is smaller than
3ah: after multiplying positive denominators, the required residual is

    5a + 3a² + 2h(1+a)(1−3a) > 0.

Consequently G₀−G < 3ah ≤ d/2, and

    G > G₀−d/2 = (G₀+κ)/2 > κ.

The exact balanced identities are

    1−ε = G+h,    r = G+h/2,    1−ε−r = h/2.

### The inequalities not implied by signs alone

The chosen h is at most 1/4−G₀, so

    0 < r < G₀+h/2 ≤ (G₀+1/4)/2 < 1/4.

Since h ≤ 1/8 and q < 1/3,

    ε > (7/8)/(4/3) = 21/32.

It follows that ε−a > 31/96 and
ε−(1−r)/2 > 5/32. These are respectively the short-record fallback and
cell-above-band slacks. Also c < 1/3+1/32 = 35/96 < 1,
0 < δ ≤ 1/64 < 1/8, and 1−r > 3/4.

### All remaining displayed slacks

Because a < b, the source's internal exponent is exactly τ. The nontrivial
source expressions factor as follows (each right-hand side is positive):

    a−q = 2ah
    1−leaf−q = λ′−leaf = L+2ah
    c−q = λ′−(1−c) = h/4
    λ−τ = λ−internal = λ′−λ = ah
    λ−σ = b−a+ah
    1−ε(1+c) = h(1−ε/4)
    1−ε−δ = G+7h/8
    r−δ = G+3h/8
    1−ε−r = h/2
    1−ε−G = h
    8−ε+r−δ−G = 8−ε+3h/8 > 7.

The seven margins are exactly

    (G+h, a, G, a, G+3h/8, G+7h/8, ε).

We have a > q > G since ε < 1, and ε > G since q < 1. Thus their minimum
is G and every margin strictly exceeds κ. The remaining rows are directly
a, b−a, β, 1−β, L, q, c, 1−c, ε, 1−ε, εc, r, 1−r, 1/4−r, δ,
1/8−δ or the two explicitly assumed bridge gaps. The source has 40 such
rows including the cap and seven margin rows. The checker independently
matches all 47 names to the pinned source's inert syntax tree.

## Sharp arithmetic ranges

Both ranges here include the scalar-domain preconditions `0 < h < 1/2` and
`κ > 0`. Without the latter requirement, the slack dictionary alone would also
admit nonpositive κ. Neither range includes the unverified bridge-entry gates.

### Retained cap

Given 0 < κ < 1/33, put u = κ/(1−κ) and choose

    a = (u+1/32)/2,    b = (a+1/32)/2.

Then u < a < b < 1/32 < 1/3 and κ < a/(1+a). The lemma supplies all 46
non-cap slacks; b < 1/32 supplies the last one. Conversely, the retained
slacks imply a < b < 1/32 and κ < G < a/(1+a) < 1/33. Hence the projected
κ range of the displayed system with those scalar-domain preconditions and
abstract positive bridge gaps is exactly
(0,1/33). This does not mean the actual assembly entry point accepts these rows.

### Relaxed diagnostic cap

Given 0 < κ < 1/4, put u = κ/(1−κ) and choose

    a = (u+1/3)/2,    b = (a+1/3)/2.

Then u < a < b < 1/3. The lemma supplies every non-cap slack. Conversely,
the retained Gaussian and fifth-margin inequalities give

    κ < g₅ ≤ r−δ < r < 1/4.

Thus the projected κ range is exactly (0,1/4) with the scalar-domain
preconditions retained, only the cap row omitted, and bridge gaps abstract
positive parameters. Neither endpoint is attained.

The sufficient interval a < 1/3 is **not** claimed to be the maximal feasible
input interval. For example a=1/3, b=2/5, β=1/20, h=1/100, κ=6/25 satisfies
the relaxed displayed slacks. The tests preserve this counterexample to an
overstrong interpretation of the lemma.

## What was actually checked

The new stdlib-only code evaluates the displayed equations and separately
evaluates the factorizations. It does not import or execute the pre-existing
assembly function. Its exact source bytes are verified against
their Git blob and SHA-256, and the full source text is parsed only as inert
Python syntax. Both source and certificate are read from their existing paths
in the repository; no source bundle is added.

The tests reproduce all 45 published non-bridge slack fractions and all seven
published margins. It does not convert the very large unused bridge integers
or disable Python's integer-string safety limit. Tests cover 1,710 constructed
rational parameter rows, strict-boundary and malformed-input mutations,
source and certificate drift, zero/negative assumed bridge gaps, cap retention by default,
and sequences within 10⁻¹⁰⁰ of the two arithmetic suprema.

The proof above, rather than the finite sample tests, establishes the
whole-region assertion. It received a separate AI-assisted algebraic review;
this is not human peer review or formal proof-assistant verification.

## Reproduce

From the repository root, using Python 3.11 or later (standard library only):

    python3 -B -m unittest discover -s research/constructive-assembly-region -p 'test_*.py' -v
    python3 -B research/constructive-assembly-region/assembly_region.py --output /tmp/constructive-assembly-region.json

The first command runs 22 targeted tests. The second writes a generated report;
all output fractions are exact. The source and certificate hashes are pinned to
commit `3b6b66891c0ac888521cf591fe306c6286601d4f`; any drift fails closed and
requires a new review before updating the pins. No network access is needed.

The repository-wide `make verify` and selected `make entrance-bank-verify`
checks were not run for this contribution: verification here is restricted to
newly authored code, without executing upstream repository programs. This
addition does not change the production arithmetic, selected certificate,
manuscript, or inherited patches.
