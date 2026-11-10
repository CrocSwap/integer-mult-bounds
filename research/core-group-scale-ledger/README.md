# A complete scale ledger for the actual Gaussian bridge

**Conditional enabling lemma; no new kappa.** Prepared for @CubeJerry with
substantial OpenAI assistance. Canonical base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Apache-2.0.

The source already normalizes completed Gaussian maps and restores their
accumulated scale. The new physical Core/halo bridge introduces explicit
inverse normalizers. This package shows exactly how to spend those shifts
inside the source's existing budget, and supplies an actual-state precision
ledger for a sequence of completed compression groups.

## Exact result

For group j the bridge approximates `B_j=2^-U_j tensor_i H_i^-1`.
The source's declared completed target is
`G_j=2^-K_j Dtilde_j tensor_i H_i^-1`. Therefore the remaining diagonal must
be `A_j=2^{U_j-K_j}Dtilde_j` if the original final restoration 2^gamma is kept.
Keeping the old remaining diagonal instead requires restoration 2^{gamma+sum U_j}.
Using both adjustments double counts normalization.

The actual source bound `D<= (16p)^2` and its least dyadic inverse normalizer
give an explicit sufficient admission `K_j>=U_j+V_j`, where V_j bounds the
remaining diagonal norm. A concrete dyadic p^100 budget passes this gate.
Both exact bridge and remaining diagonal then contract the component-l1 norm,
including arbitrary hole errors.

Let E_j be the **unchanged public bridge's** actual Core/halo error. If the
remaining-diagonal implementation has paid common-grid defect e_A,j on radius
3R0, its complete group error is at most `c_j E_j+e_A,j`, c_j<=1. With the
proved budget, every bridge input stays within radius 2R0 and

`final contribution <=2^gamma sum_j(c_j E_j+e_A,j)`.

[PROOF.md](PROOF.md) gives explicit simultaneous q, t and rational tail guards,
the whole-field Euclidean input radius and the actual remaining-diagonal
accuracy obligation. The padded target grid is retained until final extraction;
the inherited T/S<2 admission funds its complete volume. No arbitrary rounded
operation is commuted past extraction.

The full global relation `d=Theta(p^(1-10^-30))` implies both sum U_j and
gamma are O(d log p)=o(p). The common online widths remain O(p) under the
other explicit source premises. A single group's o(p) normalizer does not
suffice for this conclusion. The proof gives an explicit, potentially enormous
sufficient onset rather than claiming practical finite production parameters.

## Evidence

| Check | Executed coverage |
|---|---|
| Exact two-policy scale endpoints | 6,216 cases through four groups |
| Independent signed cumulative-grid oracle | 36,720 cases |
| Common precision guards against unchanged bridge allocation | 324 families, 891 source calls, 135 zero-tail groups |
| State-dependent nonlinear error trajectories and independent weighted suffix | 128 cases, all on one funded grid |
| Literal authenticated Reference identity-hole branches | 285 entries across three original geometries |
| Dyadic p^100 source budget | All integer p=2 through 257 |
| Negative controls | 20 source, scale, radius, rounding and admission controls |

The q=15 versus q=16 erasure witness is explicitly **before extraction**:
final C deletes that hole-supported direction. It is not a lower bound on
the final extracted transform or its reachable inputs. The source's zero
halfwidth identity matrix is not substituted as an admitted stronger witness,
because its unchanged narrow-gap certificate is negative.

## Reproduction

Python 3.12 and its standard library suffice:

```sh
python3 -B scripts/research_package.py --package research/core-group-scale-ledger --check-only
python3 -B scripts/research_package.py --package research/core-group-scale-ledger
python3 -B scripts/check_research_commit.py --package research/core-group-scale-ledger --check-modes
```

Expected verifier marker: `PASS_CORE_GROUP_SCALE_LEDGER`. Registered ordinary
and optimized modes compare the full scientific receipt with RESULTS.json.
SOURCES.json pins three live canonical inputs; DEPENDENCIES.json pins three
unchanged public bridge files at commit
`73d5adaba2b7dc662e86eb901e81369a3f73be9f`.

## Limits

This package supplies no new diagonal engine, Gaussian coefficient backend,
native execution or complete transform. Diagonal products and pages, the
Core's full K-context source bill, halo archives, copying, restoration and
retained backing remain paid. A new exact shift costs its full field pass
unless folded into a separately admitted existing operation. No scalar
multiplication is treated as a free shift.

The rational Reference-to-ideal-N comparison, full padded physical integration,
earlier errors, suffix amplification and final CRT/product recovery remain
distinct. All five foundational assumptions and the accepted multiplication
bound remain.

## Open next questions

1. **Bind the remaining diagonal.** Start with the actual Dtilde coefficients,
   scale K_j-U_j and final q-grid truncation. It must meet the displayed e_A,j
   on actual radius 3R0 with its complete production and physical bill. A
   diagonal norm certificate alone does not supply that implementation.
2. **Integrate the padded compression.** Retain the full original target field
   through disjoint groups, then bind final extraction and the actual source
   restoration. The inherited T/S<2 admission bounds volume; source layout,
   earlier errors and the physical caller still need verification.
3. **Find a final-output precision control.** Start from a selected-coordinate
   input or an actual-prefix state at a positive certified-gap Reference.
   Hole-only witnesses disappear at final extraction; zero source halfwidth
   fails the retained gap admission. No final-output lower bound is claimed.

## Credit and overlap

Cinna Davis's outer source supplies the Gaussian identity and polynomial
normalizer budget. Jose Manuel/jmbarrancoml supplies the immutable rational
Reference and Core lineage. The public Core/halo bridge is prior @CubeJerry
work. CrocSwap/integer-mult-bounds#6880 supplies the splice and scale warning;
Ali Romman's CrocSwap/integer-mult-bounds#5325 joins a different physical Tensor.
Those contributions and the Gaussian, locality, native and precision authors
are credited in NOTICE.md. The claim is the source-specific budget/remaining
diagonal join and its failure controls, not a new perturbation principle or
an independent proof of the source's complete theorem.
