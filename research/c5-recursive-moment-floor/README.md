# Sharp recursive moment on one physical C5

On the named, already cost20-certified physical core `(13,23,35,16,34)`,
every finite asymmetric strict-scalar decomposition over Q, R or C satisfies

```text
sum_t r_t^(1-a) >= 5 * 4^(1-a),     0 <= a <= 1/20.
```

Here r_t is the complete-plane binary pairing tariff, not scalar matrix rank.
Five rank-four edge terms attain the bound. For a>0, equality requires five
positive-cost terms of rank four. Zero-cost terms can be discarded legally.

The new result rules out a rank-concentrated recursive-moment improvement
on this one local core, including decompositions with more than five terms.
It is not a new scalar cost20 floor or a claim that all cost20 histograms
coincide. Splitting an edge gives the valid six-term profile `2,2,4,4,4,4`.
No supplier, selected-frontier or kappa change is claimed.

## Evidence and method

[PROOF.md](PROOF.md) gives the arbitrary-coefficient reduction and quantified
moment argument. The exact new finite premise is a rank-product bound.
Every cost20 fitting decomposition with at least six positive-cost terms has

```text
product_t r_t^r_t <= 640000000000 < 4^20 = 1099511627776.
```

Jensen's inequality converts this to the moment bound. The credited five-term
classification handles five terms. The exact integer comparison
`9*20^20 < 4*21^20` handles every larger total cost over the stated interval.

The primary checker rebuilds all 1,024 physical rectangular tariffs, checks
the predecessor weighted-rank inequality, and exhausts all 60 slack cases
at costs18,19,20. It maximizes an exact integer product by cost layers.
The separate implementation uses dense binary elimination, Fraction trace
systems and exact term-count layers. It agrees on every case. Neither
imports a predecessor executable or needs pending fork objects.

Six behavioral groups include complete tariff comparison, independent trace
solutions, dropped-trace and too-few-term counter-controls, a complete exact
six-term fitting identity, a one-unit undercharge, the saving-interval seam,
source corruption and input/provenance reclassification. They pass under
optimized execution. These are finite checks supporting a written proof,
not independent human or proof-kernel review.

## Reproduce

From the repository root, using Python3.12 and only its standard library:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/c5-recursive-moment-floor
```

Direct checks, also valid from a package export with its two inputs:

```sh
python3 -I -O -Werror -B research/c5-recursive-moment-floor/verify.py
python3 -I -O -Werror -B research/c5-recursive-moment-floor/independent.py
python3 -I -O -Werror -B research/c5-recursive-moment-floor/test_verify.py
```

Replay is read-only. `verify.py --emit` prints a reconstructed receipt to
stdout, without overwriting RESULT.json. The registered environment is
CPython 3.12.15, Linux x86_64. CHECKS.json records local verification.
Committed-byte, export and hosted-check results are reported separately.

## Scope and research decision

Base is canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority
revision6. TASK.json records the changed `complex-rank-shape-decoder` scope.
The card's ceiling positive control passed before this local lower-bound
question. Scalar rank-mass bounds alone leave recursive rank shape undecided;
this package closes that implication for the named support alphabet.

Only one of PR3268's eighteen covered cores is addressed. Its five unresolved
cores are excluded, as are the other seventeen covered cores. The moment
question is separate from residual scalar cost-floor work.

Family decision: narrow and stop. This is an optimistic local obstruction,
not a construction expansion. Native payload, frame changes, dirty-state
restoration, chronology, owners, physical hosting, precision/tape, sharing
across cores and the complete consumer bill remain unproved or unpriced.
A common width normalization preserves the local comparison, but cannot
justify adding these bounds across overlapping cores. The saving interval
is sufficient and is not claimed maximal. Full selected cold replay, Lean,
Docker and the full multiplication theorem are unrun.

## Open next questions

Does the same moment floor hold on another already cost20-certified core?
First inspect its cost20 rank-product relaxation, not another scalar cost
calculation. Actual changed tariffs and the five-term boundary must be
retained. No broader census or further construction round is reserved.

Can changed labels, scalar masks, block-linear factors or shared physical
children evade this local result? Start with an exact fitting identity and
an explicit complete tariff. A local identity alone does not resolve its
native realization or full supplier bill. Those are the blockers to an
actual exponent improvement.

## Sources and credit

The two live inputs are canonical-main bytes under
`research/c5-dyadic-decoder-gate/inputs/`, pinned by Git blob and SHA256 in
SOURCES.json and declared in VERIFY.json. Historical card and selected-result
pins are provenance only. No pending-PR input closure is required.

Credit thakrarsagar for the weighted-rank/equality-trace cost20 method in
[PR3256](https://github.com/CrocSwap/integer-mult-bounds/pull/3256), exact head
`1ea98246dabb46fc7bedf6127eff63f008414a39`, and its physical extension
[PR3268](https://github.com/CrocSwap/integer-mult-bounds/pull/3268), exact head
`ee5d4f466e6e44a1897896324a36aa4c64cf3912`. Credit Nick Petalas's
[PR3248](https://github.com/CrocSwap/integer-mult-bounds/pull/3248), exact head
`96e3ccd00c62f73d30a23f8d774eea59bfe3b97c`, for the five-term classification
and six-term split boundary. Those results are reproduced or explicitly
reproved, not claimed as new. The canonical predecessor investigation is
[Discussion1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19003538).

Retain Tekalign/PR2782 for the physical inputs and complete-plane tariff,
Arham Tahir/PR2879 for principal-block rank accounting, Sagar Thakrar/PR2484
for the named C5 and scalar minimum, Cinna Davis/PR1825 for the matching,
Adam Gall/PR1889 for the strict scalar mask, ctoth, Philippe Van Velzen and
the retained E8/P112 and selected geometry lineage. New rank-product/moment
result and checks by Nick Petalas. Apache-2.0.

## Engineering constraints

Build the Lever led to an exact rerunnable rank-product certificate rather
than a sampled moment. Prove It Works led to actual physical tables, a
separate reconstruction, semantic counter-controls and Git-free replay.

Power-of-Ten deviations are limited to Python managed allocation and bounded
standard-library dispatch. Live files and decompression are capped at 2MB;
the inventory at 32KB; geometry at 112 ports and five local planes; matrices
at 10-by-10; trace systems at 11-by-6; cost at 20; and each primary state domain
at `35*product(target_i+1)`. Products are bounded by `9^20`. The separate
checker retains only two exact-count layers. It uses at most 20 term layers,
with `5*product(target_i+1)` states per layer. No service or unbounded search
is introduced. Standard-library allocation internals are not audited.
Functions remain below 60 physical lines after formatting. Explicit runtime
checks remain active under `-O`; Ruff E,F,B,I,UP,C4,SIM and warning-as-error
replay cover the new scripts. Test-only dynamic imports have exactly two
local targets; unittest dispatch is bounded to six methods. A larger domain
or external service must revisit these limits before reuse.
