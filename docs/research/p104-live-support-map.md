# P104 fixed-cover support and chronology: live handoff map

**Contributor evidence snapshot:** 2026-10-17 21:34 UTC. This map reconciles the P104
fixed-cover support and chronology work visible on canonical main and in the
open PRs listed below. It is navigation, not an independent proof or scientific
admission. The selected result and κ are unchanged.

The earlier [P104 correction scope map, PR #2633](https://github.com/CrocSwap/integer-mult-bounds/pull/2633)
compares six older correction contracts. This note covers the newer support-
propagation and event-order proposals that postdate that map. It keeps their results separate because they count different things.

Maintainer integration refresh: the table reflects source-archive retention
through this queue pass. Exact pinned claims remain author evidence; no new
scientific admission is implied.

## Results and evidence status

| Source | Status at snapshot; exact head | What its evidence addresses | Boundary to preserve |
|---|---|---|---|
| [PR #2981](https://github.com/CrocSwap/integer-mult-bounds/pull/2981) | Source archive merged 2026-10-16; Nick Petalas; `3d24b92d8ba057b57cb2d480170ec407520e6882` | The retained [`p104-joint-unit-flags` package](../../research/p104-joint-unit-flags/README.md) constructs 208 abstract nested flags, a 2,309-edge compatibility graph, and a perfect matching for the fixed endpoint covers. | Static joint nesting. It does not schedule scalar coefficients, establish chronological transfer, restore dirty inputs, or give a physical invoice. Its registered replay is declared on main for Python 3.12. |
| [PR #3242](https://github.com/CrocSwap/integer-mult-bounds/pull/3242) | Source archive; scientific review open; jwr404; `f3c7e5229d1ce856fe3d6fa5467b10679c0fda14` | Its event-index audit reports that every target is first touched by event 410 and every source at or after event 488, so all 208 matched targets are touched before their matched sources. It also records that its example X0/Y34 registers are not restored. | Register-touch order is not frame containment, coefficient availability, or a completed correction. The PR description still marks maintainer Python 3.12 confirmation of its registered replay as pending. |
| [PR #3214](https://github.com/CrocSwap/integer-mult-bounds/pull/3214) | Source archive; scientific review open; commdata2338; `faa6323371db1c5fbb43ab04c6e00715d2328bc6` | An audit of PR #3182 reports that its output loop stops after the first eligible source and that its encoded secondary cycle differs from PR #3124's cycle. A literal X1 → H201 → Y98 path for PR #3019 is omitted by that loop. Removing the break changes the reported missing-pair counts, and the cycle error gives three incompatible endpoint pairs. | Those changed counts are sensitivity results, not a replacement obstruction theorem. The encoded PR #3182 cycle is not PR #3124's actual candidate. |
| [PR #3225](https://github.com/CrocSwap/integer-mult-bounds/pull/3225) | Source archive; scientific review open; commdata2338; `76fad3fe9276796949f769e54eeefdd185f28f4f` | On PR #3124's named cycle-A matching, it independently checks the helper-13 exclusion across all 9,765 nested flags in its finite `F₂⁹` domain, while favorably relaxing the other 207 helpers. | This is one matching and one moved-helper condition, not a result for arbitrary matchings or changed frame contracts. |
| [PR #3252](https://github.com/CrocSwap/integer-mult-bounds/pull/3252) | Source archive; scientific review open; Nick Petalas; `4784b71d2e0833537c9ae1e8be05ad2a6b334d92` | It proves the support-inclusion implication for the repaired all-source PR #3182 subspace-memory recurrence in two modes. The stated contract is immutable X, unread Y, independent dirt, monotone equal-frame linear operations, complete untimed source reads, and nested helper flags. It reports all 7,056 small interval fixtures retain every literal BFS path. | It is a necessary support relaxation. It supplies neither one simultaneous flag assignment nor a coefficient-level correction, dirty restoration, physical realization, or complete cost. The PR reports author-checked replay and an internal read-only peer check, not independent human or formal-kernel review. |
| [PR #3259](https://github.com/CrocSwap/integer-mult-bounds/pull/3259) | Source archive; scientific review open; Nick Petalas; `b572b0c25569898579041200e95731c5a43c9189` | It presents a pooled fixed-cover support cut over all 2,309 compatible endpoint pairs. Under its stated immutable-X, unread-Y, independent-dirt, monotone equal-frame contract, it reports exactly one missing required pair among 4,992: `C[71,102] = -1/2`. Its forward and backward cones have 1,725 and 37 edges and are disjoint. | The cut and counts originate in [PR #3182](https://github.com/CrocSwap/integer-mult-bounds/pull/3182); #3259's stated role is independent certification of its support proof. This is a conditional obstruction for the named fixed-cover model, pending independent scientific review. It is not an unrestricted P104 impossibility result or a complete correction program. It does not prove coefficient execution, dirty restoration, native/physical/precision/consumer costs or supplier admission. |
| [PR #3298](https://github.com/CrocSwap/integer-mult-bounds/pull/3298) | Source archive; scientific review open; tekuuu; `ae548d48dafd881b772bebb7f637d00ad2e486df` | The packed collector completes a retained P104 tensor-collector replay that had timed out in its original tuple representation. | This is verification tooling for a separate collector boundary. It does not establish the fixed-cover correction support claim above. |

The audit lineage pins [PR #3182](https://github.com/CrocSwap/integer-mult-bounds/pull/3182)
at `ad848966cd62e13de5ad8d4b5169c221d74d2fcd`,
[PR #3124](https://github.com/CrocSwap/integer-mult-bounds/pull/3124) at
`ce468c5cf22f59db3071adda269ac4cc16469c8c`, and
[PR #3019](https://github.com/CrocSwap/integer-mult-bounds/pull/3019) at
`44d12bdeb8ade4066645bd968bebd4756b06200a`; the PRs above describe their roles.
The canonical handoff is [Discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-19003327).

Each head is an exact source pin, not a statement that the PR has merged or that
its scientific claim has been accepted. Follow each PR for its own proof,
source manifest, limitations, and replay commands. For a live status refresh,
run `gh pr view <number> --repo CrocSwap/integer-mult-bounds --json state,mergedAt,headRefOid,updatedAt`
for each PR in the table. Reproduce mathematical claims at their pinned PR
heads with the commands recorded there. These packages are retained on main as
source archives; archival merging did not validate their scientific claims.
The registered runner for #2981 requires Python 3.12.

The contributor reports that `git diff --check` and an internal-link target check against
the tracked main tree passed. The three optimized #2981 package commands also
passed under CPython 3.14.8:

```sh
python3.14 -I -O -Werror -B research/p104-joint-unit-flags/verify.py
python3.14 -I -O -Werror -B research/p104-joint-unit-flags/independent.py
python3.14 -I -O -Werror -B research/p104-joint-unit-flags/test_verify.py
```

The last command ran all eight test groups. The registered package runner
requires Python 3.12 and was unavailable here; it refused to run under 3.14.
The optimized direct checks reproduce the merged static-flags result, not any
of the independently unvalidated support claims below.

## Reading the chronology claims together

The event-touch result in #3242 and the frame-support result in #3259 have
different meanings. Ordering first register touches does not establish
subspace support at a cut; a support path does not establish when a scalar
coefficient is computed or moved. Neither ordering alone says that the
coefficient `-1/2` has been restored against arbitrary dirty inputs.
Likewise, a path omitted by the unsound version of a support recurrence must not
be used as evidence for an obstruction. PR #3214 identifies that issue, PR #3252
states the missing soundness implication for the repaired recurrence, and PR
#3259 applies a separately reconstructed pooled cut.

This map reports those claims at their actual evidence statuses. It does not
independently reproduce or certify any archived proposal's proof. The open issue
[#913](https://github.com/CrocSwap/integer-mult-bounds/issues/913) is an
editorial wording complaint and is unrelated to this research boundary.

## Exact remaining gap

For the fixed-cover, immutable-X, unread-Y, independent-dirt, monotone
equal-frame contract, PR #3259 is the current submitted support obstruction;
its proof and assumptions need review before treating that route as closed.
Changing the endpoint matching alone is already included in its pooled 2,309
pair test. A useful reopening must name a different source/frame/target contract
and explain how the real producer and consumer pay for it.

No complete arbitrary-input `I-G/2` correction schedule is established here.
Within the fixed-cover contract, PR #3259's support cut would block the named
coefficient if its proof is accepted; outside that contract, exact coefficient
delivery, dirty-state restoration, native lowering, precision, physical
hosting and a complete channel-plus-correction invoice remain unresolved.
Nothing in this map proves a universal P104 barrier, admits a supplier, or
changes κ.
