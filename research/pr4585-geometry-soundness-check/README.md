# Soundness check of #4585's coarsened partitions against exact geometry

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

mihir-s-05's #4585 (head `025f37fe`) proves that no finite shear word improves any of the 128 #4470 receiver windows. It uses two necessary conditions: mandatory source contacts and admissible-contact-graph bridges. It coarsens each field's path at those contacts into a finite list of `relaxed_partitions`, and proves a capped-rank (majorization) floor over them. For the floor to cover every word, each **actually realisable** word profile must be listed or must **refine** (split into) a listed partition. Concavity then gives `cost(word) ≥ cost(listed partition) ≥ cost(incumbent)`.

#4585's lists are coarser than, and in 33 windows differ from, the identical profile sets of #4567, #4581, #4582 and #4587:
- smaller in 21 windows;
- larger in 11;
- incomparable in 1.

So this package checks the needed property directly against **exact geometry**. #4585's `CERTIFICATE.json` is vendored (blob `74424627`, SHA256-pinned).

## Method

- **Windows.** The 128 windows come from main's #4470 constructor, via `windows_lib.py`, which is my #4567 extraction and census code.
- **Exact profiles.** Every unit-shear word of length ≤ 5 with the window's endpoint is enumerated. For each word, an exact search over actual nested subspaces of `F₂⁹`, with joint incidence enforced across all gates, yields every exactly realisable profile.
- **Refinement.** Each realisable profile must be listed by #4585 or refine a listed partition (exact multiset bin-packing).
- **Incumbent.** The incumbent must be listed and must dominate every listed partition in capped rank sums (equal mass, `Σ min(r,k)` for `k ≤ 9`).

## Results

**All checks pass in all 128 windows.**
- **Profiles.** There are 235 exactly realisable profiles at length ≤ 5. **151 are listed and 84 refine a listed partition, with 0 violations.**
- **Incumbent.** It is realisable, listed and capped-rank dominant in every window.

**Length 6 (recorded run, about 20 min, not in the registered verifier because of runtime).** There are 239 realisable profiles, 151 listed and 88 refining, with 0 violations.

**A tightness observation.** For each window, the realisable set is contained in the relaxed set of #4567/#4581/#4582/#4587, because the relaxation contains every actual path. At length 6 the total, 239, equals those certificates' 239 window/profile pairs. So **every relaxed profile is realised exactly by some actual word of length ≤ 6**: the relaxation is tight for these 128 windows.

So #4585's coarsened lists are consistent with exact geometry where they differ from the relaxed sets of the other certificates. Its smaller lists still cover every realised profile by refinement.

## Verify

```text
python3 -B research/pr4585-geometry-soundness-check/verify.py
```

This runs in about 75 s with the standard library only.

## Limitations

- **Lengths.** Lengths above 5 are not enumerated. The all-length statement is #4585's written proof; this corroborates its key soundness property on every realisable short word.
- **Coefficients.** Unit coefficients only, as in #4585's windows. Nonunit words are covered by #4567's ceilings, not here.

## Open next questions

- None new. #4567's nonadjacent and retiming extensions lie outside #4585's scope.

Credit: mihir-s-05 (#4585), Cinna Davis (#4470); the exact-geometry search is from my #4567. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
