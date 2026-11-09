# Admit nonempty production Core interiors in original coordinates

**Exact source-geometry theorem; no new kappa.** Prepared for **@CubeJerry**
with substantial OpenAI assistance. Apache-2.0. Canonical base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

This package supplies an exact decision for whether the original capped
Gaussian source carve has a nonempty interior in any ordinary target window,
including identity holes, original phase boundaries and endpoint half-cells.
It also gives a finite guard admitting **every original start at once**:

`S >= e(6W+1)` and `L >= 12W+2`.

Here S is the source period, e its excess, N=S+e the target period, W>=1 the
actual carve width, and L the window length. With the source's positive
dyadic cap and `2cap<=S`, each window satisfying the guard has a genuine
production interior and a boundary of at least 2W rows. Dyadic alignment and
`N-L>=W` remain additional admissions when applying this to the actual Core.

## Result and relevance

The actual source uses `q(j)=j+floor(e*j/S+1/2)` for selected target coordinates.
The inverse image of `[a,b)` is computed exactly by two ceiling divisions.
The clipped endpoint phases and the exact total length of the complete middle
phases then give the largest selected phase run M using a fixed number of
integer operations. The unchanged capped carve has a nonempty interior
**if and only if M>6W**.

The uniform guard uses only internal full-cell lengths; it allows short
endpoint half-cells. Both displayed integer thresholds have explicit one-unit
counterexamples in the general ordinary-window domain that also retain
`N-L>=W`. No separate sharpness claim is made for dyadic aligned windows.
The exact classifier still applies
when the simple uniform guard is inconclusive.

In the cited conservative complete-Core source family, theta=e/S<=p^-2,
W=O(sqrt(p) polylog p) and L>=p^400 make this guard hold eventually. Thus a
separate nonempty-interior hypothesis for every original context is unnecessary
in that family. The other source geometry, row-gap, numerical, compiler,
ownership, native and recovery obligations remain. This is one source
admission, not removal of a foundational assumption as a whole.

The added guard has O(d^2) bit cost for d-bit descriptors. Its sufficient
version is checked once per axis when that axis's descriptors are shared by
all K contexts, with no field scan. Heterogeneous descriptors and exact
per-context checks retain their O(K g d^2) setup cost. No multiplier recurrence or selected
certificate changes. [PROOF.md](PROOF.md) gives the full statement and argument.

## Evidence and scope

| Method | Coverage | Scope |
|---|---|---|
| Independent literal coordinate oracle | All 772,850 ordinary windows for 2<=S<=40 and every e; 10,660 hole-only windows | Exact finite corroboration of the closed formula |
| Authenticated source geometry and partition bodies | 77,793 configurations, including 855 admitted uniform-guard windows | Original Reference geometry prefix, interior method, Core.partition and carve; no numerical Gaussian calculation |
| Sharp controls | Both adverse families for W=1 through 16 | Integer-window sharpness; dyadic optimization unclaimed |
| Failure detection | 17 controls; corrupted source inputs, wrong coordinates/ties/origin/width, invalid domains | Explicit exceptions remain active with Python -O |
| Large descriptors | 64, 257 and 1024-bit source sizes | The closed formula enumerates no periods or cells |

The complete N=128,L=64 fixture at S=127,e=1,W=4,cap=4 has two original
windows. Each actual source carve has five interior blocks, 20 interior rows
and 44 boundary rows. This is a geometry fixture, not a native Core execution.

## Reproduction

Python 3.12 and its standard library suffice. Three actual executable source
files and the credited proof provenance are pinned by [SOURCES.json](SOURCES.json).

```sh
python3 -B scripts/research_package.py --package research/core-production-nonempty --check-only
python3 -B scripts/research_package.py --package research/core-production-nonempty
python3 -B research/core-production-nonempty/verify.py
```

Expected final marker: `PASS_CORE_PRODUCTION_NONEMPTY`. Registered ordinary
and optimized runs compare the complete scientific output to RESULTS.json.
The written proof supplies the all-size result; finite coverage does not.

## Novelty and credit

Nick Petalas's CrocSwap/integer-mult-bounds#6259 supplies the phase cut and
endpoint length facts for the different retained 4w physical-source carve.
Vlado Vojdanovski's capped phase-fusion lineage supplies the current 6W cap,
separation and boundary-density reasoning. Jose Manuel / jmbarrancoml supplies
the exact common Reference and Core source, with Cinna Davis, Jeremy Kothe,
Mason Hale and the retained Gaussian contributors. Those results are cited;
this package does not reclaim their proofs or asymptotic density order.

The new contribution binds the target-coordinate inverse image, identity-hole
treatment, exact empty-window decision and sharp finite uniform guard to the
current production bodies. Earlier density estimates already imply eventual
nonemptiness qualitatively; this makes the actual finite source admission
explicit and directly checkable. Full source attribution is in NOTICE.md.

## Open next questions

1. **Apply the guard in the complete uniform source constructor.** It removes
   one geometric case, but source accuracy, original partition validation,
   row/column norms and complete source heights still need a common admission.
   Start with the current complete-Core preparation and feed its actual S,e,W,L,
   cap descriptors through this guard. The numerical source certificates remain
   the blocker; finite tiny interiors should not stand in for production carve.
2. **Classify sharper dyadic aligned guards.** The exact decision is available,
   but both sharp counterexample families here use arbitrary integer windows.
   Start with powers-of-two N,L and starts divisible by L. A new claim must keep
   the original phase and period cuts; current sharpness is deliberately wider.
3. **Implement truly empty short sections.** The classifier identifies them
   without ambiguity. Start with one such actual source window and trace the
   zero-dimensional dense branch and complete sparse inverse. Source/shape
   ownership and complete numerical/cost contracts are still required.
