# Coordinate-plane temporal frame rail (seed `ca04ccbf`)

**Outcome: scoped negative result. No new conditional bound or supplier admission is claimed.**

## Question and result

The selected PR1094 word has local paid profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`. This experiment changed frame timing: inject one coordinate two-plane at one helper-to-helper addition, then propagate the least common-frame closure through later gates. It held the scalar program, helper inventory, start frames, exact A/B target-level and centre-frame interfaces, and all final target and dirty-helper endpoints fixed. Every induced climb was priced at its actual rank.

The complete domain is 36 coordinate two-planes by 2,525 eligible seed gates (90,900 pairs). The exact result is 569 no-ops, 89,737 endpoint or internal-interface conflicts, and 594 valid schedules over 13 distinct rank profiles. None reaches the task's 5% ceiling improvement. The highest profile is exactly the baseline profile, with ceiling bracket `[1690054109/10^12, 169005411/10^11]`. Its lower endpoint exceeds the largest other profile's upper endpoint, `1690012017/10^12`, by `42092/10^12`. The best candidate word passes the pinned independent exact native audit.

This closes only the coordinate-plane, single-injection subfamily on this exact word. The first exploratory sweep omitted internal A/B interface barriers and its candidate failed the native audit; that sweep was discarded. The packaged rerun includes both exact target-level and centre-frame barriers, and the counterexample control exercises a centre-frame conflict. No global κ, asymptotic improvement, or general impossibility statement follows.

The selected result is resolved from `certificates/selected-result.json`; source identity and base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea` are pinned in [SOURCES.json](SOURCES.json). The actual word is member `candidate/strict/global/base/providers/gauge44/FULL-WORD.json.gz` of the pinned selected replay archive, not the historical PR699 word.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/complex-frame-plane-rail-seedca04cc --check-only
python3.12 scripts/research_package.py --package research/complex-frame-plane-rail-seedca04cc
```

The registered replay reruns all 90,900 cases, compares the exact evidence, audits the committed candidate, and verifies that corrupting its claimed paid histogram is rejected. It needs no third-party packages. On systems without Python 3.12, run `python3 -B research/complex-frame-plane-rail-seedca04cc/verify.py` directly; the package metadata check still requires 3.12 for the repository's generic replay.

## Proof and cost accounting

See [PROOF.md](PROOF.md) for the closure invariant, completeness of the finite enumerator, exact interval comparison, and limits. All state and arithmetic needed for the claim are in `SEARCH.json`, `BEST-WORD.json.gz`, and `NATIVE-AUDIT.json`.

## Open next questions

Can a non-coordinate two-dimensional subspace of `F2^9` beat the selected ceiling under the same one-gate closure and exact interface constraints? There are 43,435 such subspaces in total. The first useful step is to compute the automorphism group preserving the pinned gate supports and interfaces, then quotient this Grassmannian before screening representatives. This run does not cover that domain.

## Predecessors and credit

The source is the selected complex provider associated with PR #1094. PR #699 and `research/complex-sw4-frame8` provide historical frame-coalescence context; PR #1429 studies a fixed late-block rank optimum; PR #1517 studies a cross-block floor under that interface. Adjacent open PR #1186 supplies an exact frame solver and delivery-rewrite search for an older PR #1148 word. Open PR #1825 investigates a paired plane-port decoder on selected E8 labels, while PR #1900 studies five plane queries for the P111 bit decoder. Those constructions change the coverage contract or decoder. This package instead tests forced coordinate-plane propagation on the selected PR1094 word with its coverage, helper inventory, and exact interfaces fixed. Source-specific notices remain with their pinned files. New research artifacts are Apache-2.0. OpenAI Codex autonomously designed, implemented, and packaged this experiment; see [TASK.json](TASK.json) for disclosure.
