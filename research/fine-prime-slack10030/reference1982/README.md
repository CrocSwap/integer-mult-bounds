# Independent enclosure of the pivot-566+554 T74 complex root

**Independent verification of a pending supplier number. No new κ, no change to the selected record, and no check of the outer reduction.**

The open claims from https://github.com/CrocSwap/integer-mult-bounds/pull/1800 to https://github.com/CrocSwap/integer-mult-bounds/pull/1928 all price the same pending complex supplier: the pivot-566 stack with the pivot-554 helper-donor kernel (lineage https://github.com/CrocSwap/integer-mult-bounds/pull/1625 and https://github.com/CrocSwap/integer-mult-bounds/pull/1672). At their "free ε → 1" point, κ approaches this supplier's complex moment root b. https://github.com/CrocSwap/integer-mult-bounds/pull/1928 takes b as its certified native endpoint minus 10^-10010. Up to now, the only certificates of that endpoint came from the authors' own engines.

This package checks the endpoint with code that shares no algorithm with those engines.

## Object

Both pinned PR heads record the same data in `new/SPEC.json`:

- global profile `{1:1560432, 2:336336, 3:278724, 4:84912, 5:54612, 8:5328, 48:22748}`, m = 73, live W = 66304;
- native and conservative endpoints on a 10^-70 grid (https://github.com/CrocSwap/integer-mult-bounds/pull/1672, head `b8ab040d`) and on a 10^-10000 grid (https://github.com/CrocSwap/integer-mult-bounds/pull/1928, head `07e4e423`).

`extract_inputs.py` copies these fields, the two provider profiles, the provider counts, the idle remainder and each PR's headline κ into [INPUTS.json](INPUTS.json), with the Git blob and SHA-256 of each source file. With the pull refs fetched, `extract_inputs.py --check` rebuilds the file byte for byte.

The moment definitions come from the repository's written review, not from code. The native moment is `sum_r H[r] (r/m)^(1-x) / W` ([native-complex-moment552/PROOF.md](../native-complex-moment552/PROOF.md)). The conservative model adds the inherited fallback of `32 m^2 N` rank-one children on a 10^-16 fraction, N = number of children ([three-stage-cover-assembly.tex](../../notes/three-stage-cover-assembly.tex), line 24). An endpoint e on a 10^-d grid is certified when M(e) < 1 < M(e + 10^-d).

## Method

`verify.py` uses only the standard library and imports nothing from the repository or from either PR.

- **Logs.** Write A = ln(16/15), B = ln(25/24), C = ln(81/80); each is 2 atanh(1/31), 2 atanh(1/49) or 2 atanh(1/161). Then ln 2 = 7A + 5B + 3C, ln 3 = 11A + 8B + 5C and ln 5 = 16A + 12B + 7C. The verifier checks these identities exactly from the prime factorizations. ln 73 = 3 ln 2 + 2 ln 3 + 2 atanh(1/145). Every rank here is 5-smooth, so each ln(73/r) is a nonnegative integer combination of four atanh series.
- **Exp.** Halve the argument s times, sum a Taylor polynomial with an explicit tail bound, then square s times.
- **Rounding.** Every quantity is an integer multiple of 2^-bits rounded outward. The final test compares two exact integers. A sign that the enclosure cannot decide counts as failure; precision is raised at most twice and never turns an undecided sign into a pass.

The authors' engines use a Mercator series and binary range reduction with atanh((x-1)/(x+1)) (`code/fine_mercator.py`, `code/fine_moment.py`). Earlier independent audits used a prime-by-prime log chain (pending-claims-independent-pricing) or binary reduction (pr1407-complex-moment-audit-seed39). This package uses neither.

## Result

`PASS_T74_K554_ROOT_ENCLOSURE_INDEPENDENT`, about 15 s on Python 3.12.

- **Brackets.** All four pass: native and conservative, at both grids. The 10^-70 cases decide at 360 bits and the 10^-10000 cases at 33,347 bits, without precision refinement.
- **Nesting.** For both models, the 10^-70 endpoint of https://github.com/CrocSwap/integer-mult-bounds/pull/1672 equals the 10^-70 floor of the 10^-10000 endpoint of https://github.com/CrocSwap/integer-mult-bounds/pull/1928.
- **Profile composition.** At both heads, 249 gauge44 calls and 417 extra calls with their recorded per-call profiles, plus 22,748 idle rank-48 children, sum to the global profile. Rank mass is 4,816,512 and the deficit is 73 × 66,304 − 4,816,512 = 23,680.
- **Headline κ.** The κ of https://github.com/CrocSwap/integer-mult-bounds/pull/1928 (`outer/OUTER-CLAIM.json`) lies 2.003 × 10^-10010 below the native endpoint, as its stated choice of b implies. The κ of https://github.com/CrocSwap/integer-mult-bounds/pull/1672 (`new/SPEC.json`, 47-inequality outer) lies 2.817 × 10^-6 below.
- **Controls.** All ten are rejected. At 10^-70: next grid point as endpoint, previous grid point as endpoint, one child moved from rank 1 to rank 2, m = 72, W − 1, conservative endpoint without the surcharge, native endpoint with the surcharge. At 10^-10000: the first two and the surcharge-omission control again.

The optional `crosscheck_decimal.py` (about 4 to 5 minutes) repeats the 10^-10000 case with Python's `decimal` ln and exp at 10,060 digits. It finds all seven log values inside the enclosures and the same four signs. `decimal` rounds to nearest, so this corroborates the result but does not certify it.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/t74-k554-root-enclosure --check-only
python3.12 scripts/research_package.py --package research/t74-k554-root-enclosure
python3.12 -B research/t74-k554-root-enclosure/crosscheck_decimal.py   # optional, slow
git fetch origin pull/1672/head pull/1928/head
python3 research/t74-k554-root-enclosure/extract_inputs.py --check     # optional, needs the pull refs
```

`verify.py --write` regenerates [RESULT.json](RESULT.json); without it the run must reproduce the file byte for byte.

## Scope

This checks one number per model and grid, plus the arithmetic that composes the profile. The following are taken as given:

- the global profile and the per-call provider profiles (no replay of words, owners or hosting);
- the moment model and the native, surcharge-free complex recurrence, from the review of CrocSwap/integer-mult-bounds#552 and CrocSwap/integer-mult-bounds#559;
- the outer reduction from b to κ, the fine source-prime padding and the ε → 1 transfer (see https://github.com/CrocSwap/integer-mult-bounds/pull/1797 for an audit of the CrocSwap/integer-mult-bounds#1786 lemmas on a different supplier);
- all inherited all-size/compiler, realization, hosting, precision/tape, exact-recovery, analytic and bit H1-H5 assumptions.

It is a finite check of recorded endpoints, not a proof of any multiplication theorem.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. **Outer ledger of https://github.com/CrocSwap/integer-mult-bounds/pull/1928.** Does `outer/LEDGER.json` follow from the endpoint certified here, checked by code that does not import `outer/*.py`? This package certifies b only. A first step is to re-derive the slack list from `outer/RETUNED-SLACKS.md` and the CrocSwap/integer-mult-bounds#1673 note and compare each slack exactly. Nothing blocks it.
2. **Profile against the emitted program.** Does the global profile equal the one emitted by the T74 hosted template and owner map? The seed78 emitted-ledger rebuild could be adapted to the two-provider layout (249 + 417 calls). The PR's template and owner archives are reproduced externally, so a maintainer replay capsule would make this cheap.

## Credit

Supplier construction: mdumitrean (https://github.com/CrocSwap/integer-mult-bounds/pull/1625, pivot-566 kernel), Jeremy Kothe (https://github.com/CrocSwap/integer-mult-bounds/pull/1672 and the refinement chain to https://github.com/CrocSwap/integer-mult-bounds/pull/1928), Rohan Arun (https://github.com/CrocSwap/integer-mult-bounds/pull/1319, T74 fill) and the lineage credited in those PRs. Outer: Vlado Vojdanovski (https://github.com/CrocSwap/integer-mult-bounds/pull/1673) and chafreaky (https://github.com/CrocSwap/integer-mult-bounds/pull/1786). The moment definitions are from the review of CrocSwap/integer-mult-bounds#552 and CrocSwap/integer-mult-bounds#559 and `notes/three-stage-cover-assembly.tex`. The audit pattern follows Sagar Thakrar's frontier1094-emitted-ledger-seed78 and the selected-suppliers-de-diagnostic and pr1407-complex-moment-audit-seed39 packages.

Prepared by Aaron Wang, with help from opencode. New material is Apache-2.0.
