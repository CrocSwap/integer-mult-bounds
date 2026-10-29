# Exact moment endpoint acceptance audit

This is a bounded arithmetic audit of the moment acceptance boundary in
[PR #3576](https://github.com/CrocSwap/integer-mult-bounds/pull/3576), head
`1630afea0fc1083717b5b2799b8de7a819a6ea02`. The moment uses the complete T74
profile and order from the source archive in
[PR #2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979).

The original `independent-moment` card proposed reconstructing a frame group,
single-change control, and invoice. Live overlap found that PR #3576 already
supplies the complete moment through two exact interval engines, together with
the direct ordinary-rate and one-extra-rank-one controls. This package changes
scope to the uncovered endpoint-consumption question: are the inequalities,
strict boundary, and decimal rounding direction used correctly when accepting
those intervals?

## Result

No endpoint-direction or rounding defect was found in the audited acceptance
code. The pinned source tests `upper < 1` for the accepted sigma moment and
`lower > 1` for the two rejected alternatives. It floors the lower endpoint and
ceils the upper endpoint using integer arithmetic.

The independent `Fraction` check reads the three intervals from the exact
PR3576 proof bytes and verifies these strict comparisons:

| Case | Exact interval over `10^30` | Exact comparison used |
| --- | --- | --- |
| `sigma = 998271/1000000` | `[999999903535664027556833879161, 999999903535664027556833879162]` | upper `< 1`, with `1 - upper > 9/10^8` |
| ordinary exponent `tau` | `[1000003022093731739239177793276, 1000003022093731739239177793277]` | lower `> 1` |
| sigma with one extra rank-one child | `[1000000111677363244276477808366, 1000000111677363244276477808367]` | lower `> 1` |

The test uses no floating point and imports neither enclosure engine. Its
canaries put a rational one third of a 30-place unit above and below one, verify
floor/ceiling enclose both values, and show that the corresponding inward
rounding mutations fail. Equality-at-one and intervals straddling one catch
non-strict and wrong-endpoint comparator mutations. The exact proof and rate
source bytes, their Git blob ids, and their SHA256 hashes are retained in
`inputs/` and `EXTERNAL-SOURCES.json`. The rate source's profile/order hashes are
also checked against the live #2979 inputs pinned in `SOURCES.json`.

These checks validate how the published intervals are consumed. They do not
rederive either enclosure, replay the full T74 package, or establish a supplier
or multiplication theorem. The source claim retains its physical, production,
and outer-transfer limits; the selected frontier is unchanged.

## Reproduce

From the repository root:

```sh
python3 -I -B research/moment-endpoint-boundary/verify.py
python3 scripts/research_package.py --package research/moment-endpoint-boundary --check-only
python3.12 scripts/research_package.py --package research/moment-endpoint-boundary
```

The first command runs only the independent endpoint arithmetic and controls.
The package replay runs the same bounded verifier after metadata validation.
The captured PR source bytes can be checked against its exact commit with:

```sh
git show 1630afea0fc1083717b5b2799b8de7a819a6ea02:research/t74-retuned-ordinary-layer/PROOF.md | sha256sum
git show 1630afea0fc1083717b5b2799b8de7a819a6ea02:research/t74-retuned-ordinary-layer/rate.py | sha256sum
```

## Open next questions

- **Does a future production T74 call path consume this same complete profile and strict moment contract?** This matters because the endpoint check covers the numeric acceptance step only. The first step is to trace the actual retuned constructor into the production T74 call and bind its profile to the pinned `ORDER.json` and `PROFILE.json`. The full production GL64/T74 payload was not run in PR #3576 and remains a blocker to resolving this question here.

## Credit

Credit Hiroki Kumazaki and PR #3576 for the rate transfer and its source-pinned
two-engine certificate; Douglas Colkitt and Nick Petalas for the retained
interval engines; Jose Manuel for PR #3562 and the PR #3477 T74 layer; Marius-Paul
Dumitrean and the cited predecessor authors for PR #2979 and its T74 profile.
This audit reuses their interval claims and does not claim a new enclosure
method. New audit code is Apache-2.0.
