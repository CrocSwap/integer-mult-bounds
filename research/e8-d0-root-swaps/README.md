# E8 root swaps close the d=0 kernel branch

**Result: a characteristic-zero proof of the `d=0`, nonzero-kernel branch
explicitly left open by [PR3074](https://github.com/CrocSwap/integer-mult-bounds/pull/3074).**
The newer [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154)
and [Discussion3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156)
retain this exact obligation as **C7**.
Every lift S of the full E8 root code in that branch has basis weight cost
at least 72. The bound is sharp, including for lifts with nonzero kernel.

The reusable step is a shared-coefficient root-swap bound: if R(L) consists
of roots whose own coordinate can be changed using L while every other
orthogonal coordinate remains zero, then

    rank_K R(L) <= cost(L).

This holds for every correction space L over a characteristic-zero field K.
The [proof](PROOF.md) establishes the uniform statement; the finite checks
verify its geometric inputs and actual coefficient-space examples. They do
not enumerate all L. Three checked Lean files formalize coefficient and covering cores;
the complete E8 theorem is not proof-assistant certified.

## Exact obligation and added value

Use the fixed dense-pairing/Gram model of
[PR2816](https://github.com/CrocSwap/integer-mult-bounds/pull/2816).
E is the 120 E8 root lines, F its specified orthogonal eight-line frame,
P=E minus F, and rho is restriction to P. Labels are
`(1, r mod 2E8)` in F2^9; a vector's weight is its support's binary label rank.
`cost(S)` minimizes the sum of these weights over bases of S. Let C_E be
the full root code, C_P its restriction, and

    C_E subset S,
    T = span{v in rho S : w(v)<=7},
    d = dim_K(C_P intersect T),
    Z = ker(rho) intersect S.

The theorem is **d=0 and Z nonzero imply cost(S)>=72**.
PR3074 originally names this kernel case separately from the 38 open d>=4
ledger rows, seven prior-only rows and seven conditional E6-slack rows.
PR3154 now claims further ledger closures and retains C6 (DEG2) and C7 on
the one-sided track. Its other claims are neither imported nor audited here.
This package closes C7. The follow-up [EXTENSION.md](EXTENSION.md) also closes
C1's precise d=0 rigid-shape subcase with actual low-basis total Sigma=7.
Theorem F in EXTENSION.md additionally closes actual total eight with a
minimum (7,1) basis. Other C1 cases and C2-C6 remain outside the closure claim.
Every C1 decoder consequence is conditional on PR3154's rigid shape,
the ledger `cost(D') = sum_j w(A_j) - n_c`, the pivot rebate
`epsilon_k in {0,1}`, and N8 (at most eight corrections with distinct
corrected frame indices). This package does not independently validate
that reduction, even where the source marks its premises PROVEN.
The result alone does not establish L120, the one-sided P112 floor for every
correction pattern, a two-sided decoder floor, a supplier, or a new kappa.

[PR2862](https://github.com/CrocSwap/integer-mult-bounds/pull/2862) proves the
restricted carrier argument only through correction cost kappa<=3. Merely
extending that counting shortcut is unsafe: the algebra checker reproduces
a cost-five correction with six carrying vectors. Here the argument instead
bounds the rank of roots eligible in the *same* coefficient space.

The proof has three substantive steps:

1. The root-swap rank bound handles every space of cost at most seven by
   separating exceptional basis members. A weight-three exceptional support
   is an orthogonal quartet; only profiles (3,3), (4,3) and (3,3,1) require
   further cases. The first two reuse PR1590's two-factor lemma with an
   explicit finite-order extension to arbitrary fields.
2. A complete parabolic normal classification and deletion-rank filter rule
   out nonroot directions at restricted correction cost at most six. On the
   full E8 set, every root's 56-line remainder needs at least 24 deletions to
   lose rank, while the full correction support has at most 21 lines. This
   converts feasible directions into exact root swaps.
3. A hypothetical cost-at-most-71 lift in the named kernel branch would
   require at least k+1 independent feasible directions for a correction
   space of cost k<=7. The rank bound permits at most k.

## Stronger filter and a downstream subcase

The [extension](EXTENSION.md) proves that the restricted root-only filter
also holds at correction cost seven **when the correction space has dimension
at least two**. A connected twelve-point binary matroid excludes the only
new nonroot configuration. All 56 configurations have explicit six-pair
circuit certificates, checked in two coordinate models. Two actual boundary
examples show why the dimension and cost bounds matter: a one-dimensional
cost-seven nonroot survives, and a two-dimensional cost-eight nonroot
survives while carrying four frame labels.

Theorem C also settles **CONJG2 Section 2(ii) for every kappa<=7** in the
rigid d=0 shape: every weight-eight high normal is an E8 root direction,
so no nonroot D7/E6-type direction survives. This conclusion permits frame
roots and does not require actual low-basis total Sigma=7. The kappa=8
directions and the remaining invoice/coefficient obligations are separate.

In PR3154's d=0 rigid basis shape, this limits corrected weight-eight high
members to four. When the **actual low-basis total is Sigma=7**, the corrected
one-sided invoice is at least 65 and the pivot invoice at least 64. This
closes that C1 subcase with one unit of slack, without the unresolved F1 or
T_v coefficient steps. It does not close every cost-seven statement or all
of C1. Actual total eight is also excluded if the minimum space cost is at
most seven. The extension also proves a sharp **F1 support threshold of 24**,
with an actual failure at 25. This settles the F1 input for the entire
d=0, dim(T)=3 rigid C1 branch. Its exact-cost-eight, dimension-two boundary
violates unrestricted F1, but does not construct a complete C1 decoder or
satisfy every additional pivot condition. A separate frame-plane and
incidence argument nevertheless excludes the entire actual-total-eight
minimum-(7,1) decoder branch: at least 168 cancellations would need at most
148 available frame incidences. The other minimum-cost-eight profiles
remain open. Combining the support bound with that exclusion discharges
C1's entire F1 obligation on surviving d=0 rigid low-invoice candidates.
Exact hypotheses and limitations are in EXTENSION.md.

## Reproduce

From the repository root, with Python 3.12 and no external dependencies:

```sh
python3.12 -I -B scripts/research_package.py --package research/e8-d0-root-swaps --check-only
python3.12 -I -B scripts/research_package.py --package research/e8-d0-root-swaps
```

For a source export containing only this package:

```sh
python3.12 -I -B research/e8-d0-root-swaps/verify.py
```

The registered replay checks pinned Git provenance, recomputes
the finite geometry by both methods below, runs the exact algebra and extension controls,
and compares its result and scientific source hashes with [RESULT.json](RESULT.json).
It does not edit the receipt. `verify.py --emit NEW_PATH` creates a new
receipt for deliberate regeneration and refuses to overwrite an existing file.

The final registered replay, including the new extension and F1 checks,
passed after the audit fixes on CPython 3.12.11 in 8.40 seconds; the read-only
Git-free optimized export passed in 7.97 seconds. Two additional source
mutants changing the dimension-eight cap to 65 were rejected by the respective
mathematical guards under optimized Python. An earlier optimized extension
replay and five mathematical mutants (wrong pair mate, unit coefficient,
admitted frame roots, F1 cancellation sign and cycle elimination) passed in
9.29 seconds; that extension code is unchanged.

The original C7 replay passed in 4.45 seconds. A read-only
Git-free export also passed with `-O -Werror`. Separate temporary-copy probes
rejected a changed receipt, changed proof bytes, an existing emit destination,
an intersection substituted for the normal-plane union, and a support-only
coefficient shortcut. The last two failed in the mathematical checks before
the final source-hash comparison. Those temporary probes are additional local
evidence; the updated registered command runs eighteen rejection controls, plus the
positive and boundary fixtures listed below.

| Evidence | Coverage |
|---|---|
| Euclidean coordinate checker, `verify.py` | All 120 roots, 511 binary hyperplanes (including the dimension-eight cap 64), 256 standard parabolics, and all five nonroot normal families |
| Cartan/Weyl cross-check, `geometry_audit.py` | Reflection-generated roots and normal/plane orbits; exact agreement on the complete deletion profiles; Fourier identity and full-E8 caps, including a direct dimension-eight check |
| Full root remainders | All 120 directions; 56 lines each; minimum nonzero character support 24 |
| Coefficient checker, `algebra_check.py` | 13 actual spaces over Q(i), 42 reconstructed swap witnesses, and a sharp cost-seven example |
| Exceptional supports | All 32,130 binary-dependent quartets, including 9,450 overrank orthogonal quartets and 151,200 signed half-sums |
| Kernel sharpness | Seven explicit cost-72 bases of C_E plus one through seven frame units |
| Cost-seven extension, `extension_check.py` | Two models; all 56 connected critical deletions; complete threshold-27/Off-85 additions; private-frame bound four; literal dimension-one cost-seven and carrying dimension-two cost-eight boundaries; sharp F1 support-24 theorem and support-25 failure; all 57,120 frame-plane cases per model |
| Failure controls | Five geometric, ten algebraic, and three corrupted six-pair-certificate controls |
| Partial Lean core | Generating-family one-exception rank bound, low-overlap quartet/singleton argument and overlapping connected-cover obstruction; compiled separately |

Both geometry implementations compute exact integer/rational ranks. They
share the mathematical reduction, `EXPECTED_PROFILES` and attribution to
the same author, and use different root coordinates, orbit generation and
plane enumeration. They provide an internal cross-check, not independent
review or certification of the complete written proof in Lean. Coefficient fixtures are controls,
not an exhaustive search over arbitrary scalar spaces. No predecessor's long
DP/LP/RRC census is imported or rerun; none is needed for this branch.

The three Lean files use the repository's existing `formal/lean` environment
(Lean/mathlib v4.21.0, exact pins in SOURCES.json). With that environment
prepared, run from the repository root:

```sh
cd formal/lean
lake env lean ../../research/e8-d0-root-swaps/formal/RootSwapOneExceptional.lean
lake env lean ../../research/e8-d0-root-swaps/formal/RootSwapQuartet.lean
lake env lean ../../research/e8-d0-root-swaps/formal/RootSwapConnectedCover.lean
```

All three passed without warnings and are byte-identical to the separately
audited candidate; those compilation results are reused for this revision.
Printed axioms are only `propext`,
`Classical.choice` and `Quot.sound`. Python replay binds their source bytes
but does **not** execute Lean. The E8 instantiation, geometric classification,
two-factor lemma and final C7 assembly remain outside this formalization;
see EXTENSION.md Section 7. No hosted CI or predecessor long suites were run.

## Sources, overlap and credit

The base is `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
Exact file blobs, SHA256 hashes, PR heads and roles are in [SOURCES.json](SOURCES.json).
Its `files` inventory is authenticated against Git objects reachable from the
base. Its `related_work` pins the unmerged PR2985/PR3074/PR3154 documentary citations;
those hashes were checked locally and are not fetched or validated by generic
CI. The C1 applications retain the stated model premises as assumptions;
the broader pending reduction is not validated here. Replay executes only
this package's standard-library code. Frozen packages and the selected result
are untouched.

DreamingOfClouds' [PR1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590)
provides the two-factor lemma;
[PR2816](https://github.com/CrocSwap/integer-mult-bounds/pull/2816) provides the
model, peeling framework and classical parabolic reduction;
[PR2862](https://github.com/CrocSwap/integer-mult-bounds/pull/2862) is the
kappa<=3 predecessor;
[PR2985](https://github.com/CrocSwap/integer-mult-bounds/pull/2985) supplies
full-E8 cap context; and
[PR3074](https://github.com/CrocSwap/integer-mult-bounds/pull/3074) states the
open kernel case and padding implication. CubeJerry's
[PR3095](https://github.com/CrocSwap/integer-mult-bounds/pull/3095) independently
certifies the exact support chart and clarifies the field/normalization scope.
Those results retain their credit. No predecessor implementation is copied. The Lean coefficient and covering cores
use the existing mathlib library, under its upstream license.
DreamingOfClouds' PR3154 and Discussion3156 supply the fresh C7 target and
remaining-conjecture map, rigid C1 shape and corrected-invoice identity.
Their broader claimed reduction is not validated by this package.
[PR3158](https://github.com/CrocSwap/integer-mult-bounds/pull/3158) (Nick Petalas)
and [PR3160](https://github.com/CrocSwap/integer-mult-bounds/pull/3160) address
adjacent C5 deletion-quantifier/common-cut questions.
[PR3161](https://github.com/CrocSwap/integer-mult-bounds/pull/3161) closes the
pinned TWOSIDE `(5,3)` beta residue; its follow-up
[PR3162](https://github.com/CrocSwap/integer-mult-bounds/pull/3162) proves a
ten-deletion bound and another `(5,4)` exclusion.
[PR3163](https://github.com/CrocSwap/integer-mult-bounds/pull/3163) certifies
a fixed-first-space rank-seven/common-deletion slice. These concern C5,
not the C7 or scoped C1 results here; none is an imported proof premise.
The reduction's author announced a
[PR3154 follow-up consolidating the C5 results](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-18998364)
and subsequently claimed C6, explicitly leaving C1-C4 and C7 open. Any
publication should coordinate with that active thread.

Overlap was checked against the open and closed PR corpus and paginated
Discussion comments, then against the named predecessor heads and target
comments. The bounded search coverage and timestamps are recorded in
[TASK.json](TASK.json); absence of a matching search result is not proof of
priority. No public claim or coordination update has been posted because the
donor requires local review before any upstream action.

This is a **changed** scope from `complex-rank-shape-decoder`, selected after
the donor requested a deeper opportunity review. It closes a named decoder
proof obligation instead of constructing a larger-rank child. It is a scoped
lower-bound result, with no family-expansion or selected-frontier claim.

Prepared by **conorholds** with substantial OpenAI Codex assistance, including
GPT-6.1 SOL agents at xHigh reasoning for independent geometry, algebra and
proof audits. No independent human review is claimed. Apache-2.0.

## Open next questions

1. **Remaining C1 profiles and pivot cases.** Start with PR3154 CONJG2 Section 2: separate
   actual basis total from minimum correction cost, and retain the pivot
   rebate and T_v coefficients. The cost-eight carrying boundary here
   rules out a direct extrapolation of the root-only filter.
2. **Complete formalization.** Instantiate the checked coefficient cores for
   E8 and binary labels, then formalize the remaining exceptional cases and
   geometric/greedy bridge. The current Lean files establish partial cores.
3. **C6 (DEG2) and the remaining reduction.** PR3154 retains the one-sided
   ledger row 579 conditional on DEG2. First inspect its coverable triples
   and the unfinished orbit representative, then retain coefficients through
   the fourth/fifth-flat extension with an independent check. The larger
   reduction and its imported claims still need their own review. This
   package supplies neither a C6 result nor a validation of that reduction.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
