# Code-disjoint pricing of the pending κ claims

**Status: independent verification. No new κ; the selected result is unchanged.**
Track 75–84 (independent verification), assignment seed 83 (OS CSPRNG via Python `secrets`).
Base commit `2921874911956718fcaaaf9396fe8267b3cfa9f0`. The snapshot covers all **16 open PRs claiming
a conditional κ at or above the selected 0.001661960547713947**, as listed at 17:34 UTC on
2026-10-13. Each claim is pinned to its PR head.

## What is checked

These claims, including Jeremy Kothe's rapid leaver/slot/T16 series, have so far been priced only
with the retained engines in their own packages. PR1049, from another session of this contributor,
independently checks the leaver cells' *local words* and explicitly excludes moment/outer pricing.
This package checks the **pricing chain** of every claim from its committed record, with code that
does not import or read `moment.py`, `base_two_moment.py` or `outer.py`:

1. **Deficit.** Rank mass and deficit come from the committed global profile. The test is the
   coverage form D = W − 64N of the nine-stage hosted template (one free coordinate per live
   family, minus 64 per complete invocation; see PR1012).
2. **Halving guard.** 73² > 2·r_max².
3. **Endpoint certification.** The recorded complex endpoint b must certify: the moment is below
   one at b and above one at b + 10⁻²⁴. The arithmetic computes logarithms through the prime chain
   ln p = ln(p−1) + 2·atanh(1/(2p−1)) and exponentials with a Taylor polynomial and Lagrange
   remainder, using exact rationals rounded outward to 2⁻³²⁰. It extends PR1051's arithmetic to
   every prime.
4. **κ.** κ is recomputed through the selected outer reduction with PR589's bit endpoint, which
   every record cites unchanged, and compared with the record and the PR title. PR1019 uses its
   own 10⁻²⁴ objective grid.

## Result

| PR | Head | Author | W | N | Deficit | D = W − 64N | Endpoint certified | κ recomputed | = record and title |
|---|---|---|---:|---:|---:|:---:|:---:|---|:---:|
| [#962](https://github.com/CrocSwap/integer-mult-bounds/pull/962) | `50c6ae8151` | GamingPuzzled | 33,152 | 333 | 11,840 | yes | yes | 0.001661960547713947 | yes |
| [#987](https://github.com/CrocSwap/integer-mult-bounds/pull/987) | `0beb9476d1` | rohanarun | 33,152 | 333 | 11,840 | yes | yes | 0.001662039077758742 | yes |
| [#1004](https://github.com/CrocSwap/integer-mult-bounds/pull/1004) | `1974578f82` | jeremykothe2 | 7,168 | 72 | 2,560 | yes | yes | 0.001664233607446043 | yes |
| [#1005](https://github.com/CrocSwap/integer-mult-bounds/pull/1005) | `779e80aef4` | jeremykothe2 | 7,168 | 72 | 2,560 | yes | yes | 0.001671387264390146 | yes |
| [#1018](https://github.com/CrocSwap/integer-mult-bounds/pull/1018) | `eac7547cb1` | jeremykothe2 | 7,168 | 72 | 2,560 | yes | yes | 0.00167166528321877 | yes |
| [#1019](https://github.com/CrocSwap/integer-mult-bounds/pull/1019) | `eff6576441` | 1337isnot1337 | 33,152¹ | 333 | 11,840 | yes | yes | 0.001661960547713947858091 | yes |
| [#1022](https://github.com/CrocSwap/integer-mult-bounds/pull/1022) | `58618bcbfe` | jeremykothe2 | 14,336 | 144 | 5,120 | yes | yes | 0.001672081255752945 | yes |
| [#1028](https://github.com/CrocSwap/integer-mult-bounds/pull/1028) | `be4bd89cb4` | jeremykothe2 | 14,336 | 144 | 5,120 | yes | yes | 0.001672166670891177 | yes |
| [#1030](https://github.com/CrocSwap/integer-mult-bounds/pull/1030) | `d71857cd0a` | AlexS-scale | 7,168¹ | 72 | 2,560 | yes | yes | 0.00166202617947539 | yes |
| [#1031](https://github.com/CrocSwap/integer-mult-bounds/pull/1031) | `e900534f0b` | jeremykothe2 | 14,336 | 144 | 5,120 | yes | yes | 0.001672167430672016 | yes |
| [#1042](https://github.com/CrocSwap/integer-mult-bounds/pull/1042) | `7e8ef087c0` | jeremykothe2 | 14,336 | 144 | 5,120 | yes | yes | 0.001672188119205421 | yes |
| [#1050](https://github.com/CrocSwap/integer-mult-bounds/pull/1050) | `c87242f846` | jeremykothe2 | 14,336 | 144 | 5,120 | yes | yes | 0.001672241870811633 | yes |
| [#1053](https://github.com/CrocSwap/integer-mult-bounds/pull/1053) | `6f92ce8884` | jeremykothe2 | 14,336 | 144 | 5,120 | yes | yes | 0.001672245809535804 | yes |
| [#1055](https://github.com/CrocSwap/integer-mult-bounds/pull/1055) | `a8ea308976` | jeremykothe2 | 14,336 | 144 | 5,120 | yes | yes | 0.001672251604432734 | yes |
| [#1061](https://github.com/CrocSwap/integer-mult-bounds/pull/1061) | `223f581afb` | jeremykothe2 | 14,336 | 144 | 5,120 | yes | yes | 0.00167259071506618 | yes |
| [#1065](https://github.com/CrocSwap/integer-mult-bounds/pull/1065) | `387d935e35` | jeremykothe2 | 14,336 | 144 | 5,120 | yes | yes | 0.001672644568760139 | yes |

¹ PR1019 and PR1030 do not record W or N in their JSON. They are priced with the selected T37
values (33,152, 333) and with (7,168, 72) respectively. The latter is the unique W with
mass = 72W + 64N for the 72-call template. These two rows check the arithmetic under that stated
assumption only.

- **All 16 recorded endpoints certify, and all 16 recomputed κ values equal both the record and
  the title.** The complex side binds in every claim. All 12 slot/T16 and leaver claims use
  PR589's bit endpoint unchanged.
- **Every claim has deficit exactly W − 64N**, which is 320 per replica. The recent gains (+0.64%
  for the top claim, PR1065) do not come from the deficit. They come entirely from the shape of the
  child-rank profile, through helper removal, re-hosting and owner packing. This is the
  mass-neutral consolidation mechanism PR1012 prices.
- One documentation trap is worth noting for reviewers. PR1005's head also carries the stacked
  PR1004 package `research/gauge44-leaver/`, whose `RESULT.json` and README state 0.001664233607446043.
  PR1005's own claim lives in `research/gauge44-leaver8/`, and that package is consistent. GitHub's
  file list for PR1005 is capped at 100 entries and does not show `gauge44-leaver8/`.

## Scope

This checks the arithmetic from the committed profile to κ, and the deficit identity. It does
**not** verify the following; for the local words, see PR1049:

- that the profiles are realized by the claimed words, owners and hosting;
- the local words;
- the invoices and prefix bits;
- the owner audits;
- any inherited all-size, realization, precision/tape, analytic or bit H1–H5 assumption.

Claims opened after the snapshot are not covered. A passing row is consistency evidence, not
acceptance of a claim.

## Reproduce

```sh
make pending-claims-pricing-verify     # offline: table regenerated and compared, 6 controls, 3 tests (~2 s)
python3 -B research/pending-claims-independent-pricing/rebind.py   # optional, network: re-bind every head and blob
```

Expected: `PASS_PENDING_CLAIMS_PRICING_REPLAY`, and `PASS_PENDING_CLAIMS_REBOUND` from the optional
rebind. Standard-library Python 3.10+.

[`SNAPSHOT.json`](SNAPSHOT.json) holds each claim's profile, W, N, endpoint and κ, with the git
blob id of every source file at the pinned head. `rebind.py` refetches the pull refs and requires
those blobs and values. Nothing from the PRs is executed.

Each negative control uses the top claim:

| Control | Rejected because |
|---|---|
| C1 one extra rank-one child | moment not below one |
| C2 one replica's live stock (896) removed | moment not below one |
| C3 endpoint + 10⁻²⁴ claimed | moment not below one |
| C4 κ + 10⁻¹⁸ | not admissible under the margin |
| C5 a bit endpoint below b | the binding side and κ change |
| C6 exponential truncated at degree 2 | the enclosure is too wide, so the check fails closed |

## Credit

- The claims and their constructions belong to their authors: Jeremy Kothe (PR1004, PR1005,
  PR1018, PR1022, PR1028, PR1031, PR1042, PR1050, PR1053, PR1055, PR1061, PR1065), rohanarun
  (PR987), GamingPuzzled (PR962), 1337isnot1337 (PR1019) and AlexS-scale (PR1030), and to the
  lineage credited in their packages.
- The retained engines' authors are credited for the reduction this replicates.
- Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic)
  via Claude Code. New material is Apache-2.0.
