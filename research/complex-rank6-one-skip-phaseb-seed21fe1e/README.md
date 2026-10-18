# One skipped child in the selected Phase B rank-six search

**Outcome: scoped negative result. No decoder, conditional bound, supplier, or new \(\kappa\) is claimed.**

## Question and result

For the exact heterogeneous tensor \((3,1,1,1)\to6\) established in PR #1866, can four child calls of ranks \(1,1,1,3\) form a rank-six block in Phase B of the pinned PR1087 provider when exactly one other child call is skipped between them? The scope requires four distinct selected registers, a skipped-child register disjoint from those four, and every intervening scalar operation to touch none of the selected registers. These conditions make the skipped call and scalar gap commute without a buffer.

The source-pinned census covers both Phase B orientations (3,870 events each, with 1,952 climbs and 1,918 scalars). In each orientation it finds 67 raw five-child windows meeting the rank and register conditions. All 67 contain intervening scalar events touching selected registers: 63 windows have two such events and four have twelve. Thus **zero** meet the stated no-buffer commutation condition. The package records the exact source and target \(\mathrm{GF}(2)\) union bases for all 67 raw candidates; the two orientations agree exactly.

The four-consecutive-child control finds 12 rank/register windows per orientation. To give the proposed mechanism every favorable assumption, the cost screen nevertheless grants all 67 one-skip candidates plus all 12 consecutive windows as if all 79 could be used at once. This is only a candidate-count upper bound; it does not assert those windows are mutually compatible.

## Exact optimistic cost screen

Starting from the selected per-call profile \(\{1:2412,2:418,3:432,4:142,5:82,8:8\}\), each ideal rank-six block replaces three rank-one and one rank-three children, preserving paid rank mass. At \(k\) blocks the hypothetical profile is

\[
n_1=2412-3k,\quad n_2=418,\quad n_3=432-k,\quad n_4=142,\quad n_5=82,\quad n_6=k,\quad n_8=8.
\]

The exact interval ceiling engine gives an upper endpoint \(1738849794997/10^{15}\) at \(k=79\), below the exact 5% target \(35491136290869/20000000000000000\). The moment relaxation is strictly decreasing in \(k\) at that target, so every \(k\le79\) also fails. The independent boundary controls remain 134 blocks failing and 135 passing. Scalar, frame, copy, hosting, precision, and restoration costs are all waived in this screen; charging any of them cannot rescue the capped profile.

This excludes only the claimed one-skipped-child, register-disjoint scalar-commuting class in Phase B under the pinned provider. It does not exclude a construction with additional buffering, different gap patterns, another phase, or a changed tensor/provider. It is not a selected-word construction or a \(\kappa\) update.

## Reproduction

From the repository root, run the standalone verifier and registered package replay:

```sh
python3 -I -O -B research/complex-rank6-one-skip-phaseb-seed21fe1e/verify.py
python3 scripts/research_package.py --package research/complex-rank6-one-skip-phaseb-seed21fe1e --check-only
python3 scripts/research_package.py --package research/complex-rank6-one-skip-phaseb-seed21fe1e
```

Expected verifier line:

```text
PASS_PHASEB_ONE_SKIP_COMMUTATION_BOUND raw= 67 commuting= 0 consecutive= 12 cap= 79 k79= 1738849794997/1000000000000000
```

`SOURCES.json` pins the base, selected record, catalogue, provider archive, selected ceiling engine and profile, and PR #1866 tensor certificate inputs. `RESULT.json` contains the full bounded candidate census and exact union bases. `VERIFY.json` registers the replay and controls.

## Open next questions

The next narrow question is whether the same one-skipped-child block has a viable placement in another pinned selected-provider phase under an explicit scalar-crossing tariff. The first step is to pin that phase interval and run this exact rank/register/frame-union census; before enumeration, charge scalar crossings against the 135-block zero-overhead threshold. This requires a new phase-specific compensation and restoration model, which the current upper-bound screen deliberately waives.

## Claim and predecessors

Cycle 41 seed `21fe1e68893bfa4b5c8e1ec66cfcf4b9`; task `complex-rank-shape-decoder`; refined scope key `cf82678d6b12180adc5a`; base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; priority revision 4. Claim: [Discussion #2119 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/2119#discussioncomment-18937481); hub status: [Discussion #1167 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18937484).

PR #1866 supplies the exact tensor and dirty-output contract. Open PR #2124 and its completed Discussion #2119 result cover consecutive Phase B windows; this package adds the source-pinned one-skip census and its zero-overhead count bound. No existing source, selected certificate, or frontier record was changed.

## Credit

Prepared by Cinna / commdata2338. The tensor construction is attributed to PR #1866; the pinned Phase B source archive preserves PR1087 and its source notices. New work is Apache-2.0. Substantial OpenAI Codex assistance in scope refinement, exact census and cost screening, verification, and exposition is disclosed in `TASK.json`; no independent human proof review is claimed.
