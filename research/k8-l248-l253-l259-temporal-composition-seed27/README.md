# Three temporal gauges on the frozen k8 word

**Finite scalar-circuit composition; no new κ and no selected-supplier change.**

Seed 27’s index 27 anchors the composition at L253 in PR1263’s sorted 218-helper support; the question then tests its interaction with the pinned L248 and L259 schedules on that frozen word. The L248 schedule from PR1353, L253 schedule from PR1350, and L259 schedule from PR1385 were mapped back to the same ordered source-ADD stream. Their supports have sizes 71, 96, and 144. In both orientations, every pair of supports is disjoint. Therefore no source ADD price depends on two changing helper exponents; the exact cost objective separates into the three inherited one-coordinate objectives. The schedule transitions remain separate scale operations on their respective helpers and are all replayed and invoiced.

The resulting word saves 494 complex primitives per orientation over PR1263’s constant-gauge word. Its complete invoices are 135,508 forward and 135,524 backward, down from 136,002 and 136,018. The paid recursive profile is unchanged. The result is a finite complex circuit construction; it does not change the selected κ or establish native supplier/controller admission.

## Exact evidence

`RESULT.json` records both directions’ 311 source-ADD IDs, all six pairwise empty intersections, predecessor and pair-control hashes, the 54 inserted scale macros, complete ADD/SCALE invoices, paid profiles, payload checks, all 712 formal input columns, and failure controls. `SOURCES.json` pins the exact base and the PR1263/PR1350/PR1353/PR1376/PR1385 commits and vendored bytes. The L259 exact DP is rerun from the pinned PR1385 temporal optimizer; the L248/L253 exact single-coordinate optima are inherited from their pinned, checked predecessor receipts.

The composed word’s exactness follows from three separable pieces: disjoint ADD-price supports, additive per-helper transition/restoration costs, and an exact full-word replay. This proves optimality for composition of these three pinned per-coordinate optima with all other PR1263 gauges fixed. It does not search over other helpers or other schedule families.

## Overlap review

The final live refresh at 2026-10-14 00:19 UTC covered 869 open PRs and 128 discussions with complete pagination and no warnings. The nearest active scopes were checked directly: PR1376 composes L248/L253 only; PR1385 supplies L259 only; PR1397 optimizes L225/L350/L367 on the original PR1094 word; and PR1398 optimizes L284 alone on the PR1263 frozen word. This result composes the pinned L248/L253/L259 schedules on the PR1263 word and records their three-way source-ADD incidence.

## Reproduce

From the repository root:

```sh
python3 -I -O -B research/k8-l248-l253-l259-temporal-composition-seed27/verify.py
python3 scripts/research_package.py --package research/k8-l248-l253-l259-temporal-composition-seed27 --check-only
```

Expected verifier result begins:

```text
PASS_COMPLEX_L248_L253_L259_TEMPORAL_COMPOSITION
forward support 71 96 144 shared {'248_253': [], '248_259': [], '253_259': []} complex_primitives 135508 columns 712 no_new_kappa
backward support 71 96 144 shared {'248_253': [], '248_259': [], '253_259': []} complex_primitives 135524 columns 712 no_new_kappa
```

The registered package replay uses Python 3.12. Local replay used the available Python 3.14.7 interpreter; the registered Python 3.12 CI replay remains the authoritative environment check.

## Scope and limits

The scope is only the PR1263 frozen word and these three pinned schedules. Source-incidence disjointness does not establish compatibility with other circuit changes. The complete local invoice preserves the PR1263 paid profile and its inherited 192-bit payload charge, but this package does not certify the native adapter, whole-call hosting, new recursive profile, or a multiplication theorem. The selected record remains κ = 0.001672660197076918.

## Open next questions

Can a native complex supplier/controller admit this exact schedule with a complete hosted invoice? The first step is to port the three-helper schedule into the native adapter and rerun its source, restoration, frame, copy, and precision checks. The missing artifact is a reviewed adapter and whole-hosted receipt.

## Credit and disclosure

Credit Philipp / @mightyOil for the PR1263 frozen word, and Cinna Davis / @1337isnot1337 for PR1350 (L253), PR1353 (L248), PR1376 (their pair composition), and PR1385 (L259). This result verifies and extends that chain with the three-way incidence/composition evidence. Prepared by Cinna Davis with substantial OpenAI Codex assistance; no independent human review is claimed. New material is Apache-2.0; predecessor source notices and receipts are retained.
