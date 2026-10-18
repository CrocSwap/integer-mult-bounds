# Restoration deferral in the selected T37 complex supplier

**Status: research note and scoped negative result. No new κ; the selected result is unchanged.**
Track 50–59 (recursive interfaces), assignment seed 57 (OS CSPRNG via Python `secrets`).
Analysis base `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`, where PR942's T37 record
(κ = 0.001661960547713947) is selected. Rebased onto `29218749` and re-verified there: the selected
record is unchanged and all pinned inputs are byte-identical.

## Question

At the end of every U8 invocation, 378 helpers and all 112 sources climb back to the full
frame. PR974 calls these 866 mass units per call "pure boundary climbs" and prices their
deletion with zero parent cost. This note prices one explicit way to remove the helper part,
counting every child the change creates.

**Mechanism (restoration deferral).** A helper ends at the frame it holds before its
restoration climb, as a low end. The host coordinates that the climb advanced go back to the
pending set of the same hosting window. That window's idle child then advances them, as in the
hosting lemma of `research/idle-axis-hosting/PROOF.md` §2. Coordinates returned to one window
form a single child, merged with any remainder the window already has.

## Findings

1. **Coverage identity (exact, every live family).** On the selected T37 payload, every one of
   the 33,152 live families satisfies

   ```
   8·k_f + 1 + hosted_f + idle_f = 73,     k_f ∈ {2, 3} data incidences.
   ```

   The same holds for all 18,816 families of T21. So rank mass = 72W + 64N, and the deficit is
   exactly **D = W − 64N** (T37: 33,152 − 64·333 = 11,840; T21: 18,816 − 64·189 = 6,720). This is
   the per-family form of the per-replica relation `8v − 9C` in Dominik Scholz's
   `research/larger-gain/geometry`. Outside the eight centre paths, paid mass equals advanced
   live coordinates family by family: 8 per data incidence, the hosted residual widths and the
   idle ranks. One coordinate per family is unpaid. The centre paths act on private work
   families `[W, W+8)`.

2. **The full-frame inverse cleanup consumes every helper restoration climb.** 378 helpers carry
   636 mass of restoration, with children `{1:272, 2:12, 3:64, 4:2, 5:28}`, and every one of them
   is touched by a full-frame cleanup gate (8,492 incidences). The other 126 helpers are already
   low ends with zero restoration, and targets have none. The 112 sources carry another 230; the
   data contract fixes their full endpoint, and the cleanup also touches them (3,618
   incidences). Index by index, the helper restoration equals that of the canonical provider
   word bound by the hosted template. In both emitted programs, the 490 `final` climbs have
   exactly the replay's rank multiset `{1:350, 2:18, 3:64, 4:2, 5:56}` and run in a phase that
   precedes `full_frame_cleanup`, with only exit adapters between.

3. **Deferral is mass-neutral, and its whole value is consolidation.** Removing a restoration
   climb returns the same number of coordinates to an idle child, so total rank mass is
   unchanged. Only the shape of the profile can move. Deferring one helper index alone changes
   nothing unless that index recurs in a window: 32 of the 378 indices leave the profile
   unchanged. The best single index (helper 9, all 333 calls) is worth +0.00998%. The value is
   strongly superadditive. Single-helper moment drops sum to 53.9 (× mW), while joint deferral
   drops the moment by 325.0.

4. **Exact ceilings.** The table below uses the pinned engines and the selected outer witness.
   With the selected owner map, deferring all 636 restoration mass per call is worth at most
   **κ = 0.001708640379500299 (+2.81%)**. That is about what PR974's model assigns to deleting
   *one* rank-one child per call. Under ideal re-hosting into capacity-48 windows, the complex
   side passes the PR589 bit side, and κ stops at the bit cap 0.001730427469823602.
   As a relaxation, one rank-one climb merged into an existing rank-48 idle child is worth at
   most about 1/124 of a zero-cost deletion. No re-hosting realizes that merge: every selected
   window has capacity at most 48, and every rank-48 child already fills a whole idle window.

5. **Source restoration has no deferral target in this template.** A source's restoration
   coordinates belong to the current invocation level of its own family. In the fixed nine-stage
   template, no idle window of that family contains them, and later bridges touch the family.
   This note therefore does not price source deferral. This finding is argued from the
   template's level structure and is not machine-checked here.

## Exact prices

Every row is certified the same way. Both pinned moment engines accept the complex endpoint b
and reject b + 10⁻²⁴. All 47 outer inequalities pass at κ, and κ + 10⁻¹⁸ is rejected.
The bit endpoint is the unchanged PR589 value 0.001733427039589844234749.

| Scenario | Rank-mass neutral | Realizable in selected windows | Complex b | κ | Gain |
|---|:---:|:---:|---|---|---:|
| selected baseline (reproduced exactly) | yes | yes | 0.0016647272587406788557 | 0.001661960547713947 | — |
| baseline under free concentration (relaxation control) | yes | no | 0.0016647297816280879 | 0.001661963062222440 | +0.00015% |
| defer all helper restoration, selected owner map | yes | yes* | 0.0017115648282780278 | **0.001708640379500299** | +2.809% |
| same, free concentration into capacity-48 windows | yes | no | 0.0018366218598730563 | 0.001730427469823602 (bit binds) | +4.120% |
| best single helper index (9), all calls | yes | yes* | 0.0016648937103306857 | 0.001662126446464193 | +0.00998% |
| one rank-one climb per call into an existing 48-child (48 → 49) | yes | no | 0.0016651079081149250 | 0.001662339932746932 | +0.0228% |
| PR974-style deletion of one rank-one child per call | **no** | no | 0.0017117453687937428 | 0.001708820303553035 | +2.820% |

\* The window placement is realizable. The local obligations listed below are not attempted.

"Free concentration" places all idle coordinates in children of rank 48. It ignores helper
indivisibility, window capacities and chronology, so it bounds every re-hosting from above.
On the unchanged word it moves κ by only +0.00015%, so the selected packing is already
nearly concentrated. The last row reproduces PR974's T37 value for comparison. It leaves 333
live coordinates unadvanced, so it does not correspond to any coverage-preserving mechanism.

## What this means for interface work

- In the hosted recursion, helper and source restoration climbs are **coverage-productive
  work**, not removable boundary overhead. PR974's rows "final helper climbs to FULL", "final
  source climbs", "all final endpoint climbs", "early cleanup tails", "target delivery climbs"
  and "all helper width" all delete live advances. A coverage-preserving version has mass value
  zero and keeps only the shape value priced above.
- Of PR974's classes, only the **centre path** (64 per call, on private work families) is
  non-productive. Its existing obstructions are recorded in `research/larger-gain/geometry`.
  Apart from the centre path, the deficit can grow only through the template, by giving each
  family more unpaid coordinates or each invocation more families (D = W − 64N).
- Restoration deferral could still be worth up to +2.81% with the current owner map. Getting
  there needs most of the 378 helpers deferred **jointly**, because the value comes from
  merging inside shared windows. Retiming a few helpers at a time is nearly worthless.

## Remaining obligations (none attempted here)

Realizing any part of the ceiling requires all of the following:

1. Retime the full-frame inverse cleanup so that the deferred helpers are never needed at the
   full frame. PR601 did this with commuting-prefix cleanup for 46 hyperplane-ended helpers per
   call at the time. PR935's bounded retiming census found no local gain, but it held the final
   caps fixed, which excludes this mechanism.
2. Establish low-end validity: inverse-row and dirt-column cone conditions and dirty
   compensation, as checked in PR881.
3. Supply exact phase recipes and adapters for the changed word, in both orientations.
4. Pass hosting-window and owner admission for the changed residual widths.
5. Recompute the finite invoice and assembly, including prefix bits, row coefficient and
   idle-child count.

## Scope and limits

- These are exact identities on the frozen payload and exact model prices, **not a construction
  and not a new κ**. Neither ceiling is a lower bound for any mechanism.
- The census checks that one coordinate per live family is unpaid. It does not re-derive the
  route by which the nine-stage template supplies that coordinate.
- The frame semantics follow `audit_local.py` and PR881's independent checker: monotone nested
  F₂⁹ frames, one paid child per climb, a centre path at the cut and fixed endpoint frames. The
  implementation here is new. Scalar maps, compensation and cones are not rechecked.
- All inherited assumptions of the selected result remain: all-size compilation,
  common-label/mutable-source realization, whole-call hosting, precision/tape, analytic transfer
  and the bit H1–H5 interface. This is not a Lean proof of anything.

## Reproduce

```sh
make t37-restoration-deferral-verify
```

The same check without make:

```sh
python3 -B research/t37-restoration-deferral/verify.py --work /new/empty/dir
python3 -B -m unittest discover -s research/t37-restoration-deferral -p test_package.py -v
```

The expected last line is `PASS_T37_RESTORATION_DEFERRAL_REPLAY`. It takes about 8 s with
standard-library Python 3.10+ and no network. The pinned engine files are loaded from the
repository and hash-checked. `verify.py` reads five members of the committed T37 archive and
two of the T21 archive in memory, without extracting them. It recomputes `CENSUS.json` and
`PRICES.json` and requires them to equal the committed files. A double-precision bisection
that shares no code with the pinned engines must then agree with every certified endpoint and
κ to within 10⁻¹³, including the best single-helper row. Finally it runs nine negative
controls. C4, C5 and C7 test this package's own checks; the others test the inputs and the
certification:

| Control | Rejected because |
|---|---|
| C1 one rank-48 idle child dropped | coverage identity fails (a family covers 25) |
| C2 one idle child shrunk to rank 47 | coverage identity fails |
| C3 one idle child duplicated | coverage identity fails |
| C4 full-frame cleanup removed for one restoration helper | its restoration climb is no longer consumed |
| C5 zero-cost deletion presented as a deferral | rank mass changes |
| C6 corrupted payload pin | payload digest mismatch |
| C7 a child of rank 52 | halving guard `73² > 2r²` fails |
| C8 complex endpoint b + 10⁻²⁴ | both engines exceed one |
| C9 one extra rank-one child | baseline κ no longer equals the selected record |

## Sources and pins

[`SOURCES.json`](SOURCES.json) records every input. The selected T37 archive is
`research/community-frontier942-audit/t37-replay.tar.gz` (`48285025…`). From it, the census
reads the hosted template (payload `956e0c0e…`, equal to the `template_sha256` of the selected
`ASSEMBLY.json`), the U8 word (content `090fd574…`) and the emitted local programs (container
`8b6a9e3a…`, bound by the template) and the canonical provider word (container `387a2266…`,
bound by the template). T21 is read from `t21-replay.tar.gz` (`6dcd7040…`). The engines
`moment.py`, `base_two_moment.py` and `outer.py` are taken from
`research/native-complex-moment552/engines` and carry the SHA-256 digests recorded in the
selected assembly. `price.py` transcribes `outer_witness` from the archive's
`runtime/code/assemble.py`. It checks that file's digest (`d89ed7a6…`) and the literal lines it
transcribes, and it cross-checks the bit endpoint against the selected `ASSEMBLY.json`.

## Credit

- **Selected construction:** Jonathan Capalbo (PR942); Chafik Boukhalfa (PR890); Jeremy Kothe
  and NewBArch (PR869/PR870); Hao Yan (PR858); DreamingOfClouds (PR589) on eumemic (PR555).
- **Concurrent work, PR974 (avirazza, open, same track).** It supplies the role/phase partition
  and the zero-parent-cost budget. This note reproduces its T37 one-unit price independently and
  adds the coverage-preserving recurrence for its restoration rows.
- **Building blocks:**
  - Dominik Scholz's `research/larger-gain` (`8v − 9C`, centre obstructions).
  - DaysSky's idle-axis hosting (PR442) and its hosting lemma.
  - Jeremy Kothe's hyperplane-ended helpers (PR601).
  - goatliamia's cleanup retiming census (PR935).
  - SethBurkart123's U8 independent cross-check (PR881).
- **This note:** prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from
  Claude (Anthropic) via Claude Code. New material is Apache-2.0.
