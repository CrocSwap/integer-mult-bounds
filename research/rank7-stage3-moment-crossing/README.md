# PR2979 stage-3 moment crossing

**Status:** scoped arithmetic check passes on launch base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6. No κ or selected-frontier change; PR2979 remains an archive-only, partially reviewed source.

## Question and result

On PR2979's T74 allocation and its fixed final fill, does the published stage-3 change (Jeremy Kothe's fourteen PR2957 gate rewrites, re-addressed in PR2979) move the complete rank histogram across PR2979's claimed saving? The check uses the final profile and the published stage-2 local profile. The source's final and stage-2 owner-width inventories agree, so the arithmetic holds the idle histogram and fill fixed while changing only the per-call local profile.

**Yes, for that source-bound histogram implication:** at the claimed `κ = 0.0017290339826465135177169999999999999999999998999999999999999999999999`, the exact interval check gives

| T74 fixed-fill profile | Moment at claimed κ |
|---|---:|
| After stage 3 | `0.999999999999999999999998320604425983823778507700737932554275… < 1` |
| Before stage 3 | `1.00000347984274075060604378718186654149117208974282071172482… > 1` |

The exact upper bound for `M_after − M_before` is negative (displayed as approximately `−0.00000347984274075060604546657744055766739358204208277917054574848`). The local profile delta is `−4` at ranks 1, 2, and 3, and `+6` at rank 4 per call; its rank mass is exactly zero. Repeating it over 666 calls reconstructs the complete change while leaving the same idle histogram in place.

For a profile `P = {r: n_r}`, saving `b`, and live width `W`, the checked quantity is `M(P,b) = Σ_r n_r r (73/r)^b / (73W)`. Here `W = 896 × 74 = 66,304`; the source order has `9 × 74 = 666` calls.

The checks also find both profiles below one at the prior PR2969 headline and equal at zero saving. Adding one rank-1 charge to the final profile, omitting the transition, or overstating the saving by `10⁻²²` fails the corresponding semantic check. The printed decimal intervals are truncated for display; all decisions use exact rational interval endpoints.

## Method and source binding

`verify.py` independently encloses each `(73/r)^b`. It uses integer bisection to enclose a rational 32nd root, then bounds `(1+y)^(32b)` between adjacent partial sums of the alternating generalized-binomial series. Eighty terms and a `10⁻¹⁰⁰` root grid suffice. Every bound and sign check is a `Fraction`; the verifier imports neither source moment function and uses no logarithm, exponential, floating-point or decimal value in a proof decision.

Live inputs are pinned by Git blob and SHA256 in [SOURCES.json](SOURCES.json). The source package's manifest and allocation pins bind the selected profile, order, fill, stage-2 certificate, and rewrite-price record. Source head: PR2979 `be191346391661f4d35fc0d1508d0a6029572576`; canonical base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

The retained `tools/audit_allocation_moment.py` and `tools/root.py` are exact rational checks, but both enclose powers through logarithm and exponential series. The source package's registered checks are set up to establish the final profile/root and per-stage capacity bounds; I did not rerun that registered or full replay here. This artifact adds a direct, code-disjoint enclosure of the *stage transition at a common saving*: `M_after < 1 < M_before` on one frozen T74 fill. It does not independently rebuild the fourteen rewrites, the source frames, the owner assignment, or the physical invoice.

The live overlap check and the exact heads inspected are recorded in [OVERLAP.md](OVERLAP.md).

## Reproduce

From the repository root:

```sh
python3 -B scripts/research_baseline.py
python3 -B research/rank7-stage3-moment-crossing/verify.py --write-result
python3 scripts/research_package.py --package research/rank7-stage3-moment-crossing --check-only
python3.12 scripts/research_package.py --package research/rank7-stage3-moment-crossing
```

The first command verifies selected-record bindings only. The last command runs this bounded arithmetic verifier; it is not the PR2979 registered replay or full cold replay.

## Open next questions

Can an independent source replay confirm that the frozen T74 fill is valid on the stage-2 word and that its pre/post rank profiles equal the published 14-rewrite transition? Start by replaying the re-addressed rewrite preimages and comparing only the resulting local histogram and unchanged helper-width inventory; then apply the pinned fill. This would validate the premise behind the moment crossing. It requires word/owner reconstruction and is outside this numeric pass.

## Credit

Credit Marius-Paul Dumitrean (PR2979 and its retained source lineage), Jeremy Kothe (PR2957 rewrites), and Dugongue (PR2969 comparator). The rank7 source package retains all earlier construction and verifier attribution. The binomial enclosure and staged moment check are new here, produced by OpenAI Codex worker homelab-13 with substantial AI assistance. No independent human or formal-kernel review is claimed. Apache-2.0.
