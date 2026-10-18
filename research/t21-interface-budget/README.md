# Interface budget for the selected T21 complex supplier

**Status: research note (exact model pricing and scoped negative result). No new κ.**
Track: recursive interfaces (sprint seed 51). Started on `007664306fff84fbb1c9a1b4053b69f439764034`
(selected PR890 T21); rebased on `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`, where the T37 record
(PR942, κ = 0.001661960547713947) became selected. T37 reuses the same U8 word and PR589
bit supplier, so every finding below holds for it too (checked in the replay).

## Findings

1. **Where the U8 paid mass sits.** Every paid child of PR869's U8 word is tagged with the
   program phase and register role that pays it. Each register pays exactly
   `rank(end frame) − rank(start frame)`; the eight centres pay 8 each. The 5634 local
   mass per call splits as sources 896, targets 896, centres 64 and helper width 3778.
   The pure *boundary* climbs, paid only to meet the endpoint contract after the program
   ends, are 866 per call: 636 for helpers restored to FULL and 230 for sources.

2. **The complex side has under two units of headroom.** With PR589 unchanged, the outer
   assembly uses `s = min(c, (1−β)b)`. Removing one rank-1 child per call raises κ to
   0.001708817; removing two makes the bit side bind. No complex-side change of any size
   then exceeds **κ = 0.001730427469823602**. Every boundary class above is 32–1889 times
   larger than this headroom. The selected T37 record behaves the same way: one unit per
   call gives κ = 0.001708820, two units make the bit side bind.

3. **Bit-side changes alone do nothing now, and copy deletion cannot reach κ > 0.01.**
   The selected κ is complex-bound, so a better bit supplier alone leaves κ unchanged.
   The sprint target needs both savings above s* ≈ 0.0101010. On the complex side,
   deleting 176 rank-1 children per call would suffice in this model. On the bit side,
   deleting all nine PR589 COPY ranks, with its other children fixed, gives only
   c = 0.004803. The other bit children or the template parameters must also change.

## Exact model prices

Each row deletes the named U8 climbs in all 189 calls. Every other child, the live stock
W = 18816, the idle hosting profile and all 47 outer inequalities stay unchanged. The parent
or interface cost of the deletion is set to **zero**, so each row is an upper bound for that
mechanism under this recurrence, not a construction.

| Relaxed U8 class | Mass/call | Children/call | Deficit | Complex b | κ with PR589 |
|---|---:|---:|---:|---:|---:|
| none (selected) | 0 | 0 | 6720 | 0.0016647245 | 0.001661957774647029 |
| one rank-1 child | 1 | 1 | 6909 | 0.0017117425 | 0.001708817452122612 |
| two rank-1 children | 2 | 2 | 7098 | 0.0017587714 | 0.001730427469823602 (bit binds) |
| centre path | 64 | 8 | 18816 | 0.0046665 | cap |
| final source climbs | 230 | 112 | 50190 | 0.0126313 | cap |
| early cleanup tails | 256 | 196 | 55104 | 0.0140087 | cap |
| final helper climbs to FULL | 636 | 378 | 126924 | ≥ 0.02 | cap |
| all final endpoint climbs | 866 | 490 | 170394 | ≥ 0.02 | cap |
| target delivery climbs | 896 | 520 | 176064 | ≥ 0.02 | cap |
| all helper width | 3778 | 2484 | 720762 | ≥ 0.02 | cap |

Grid endpoints are certified by both pinned engines (accept `b`, reject `b + 10⁻²⁴`) up to
0.02. Above 0.02 only the lower bound is certified; that suffices, because κ is bit-bound.
Bit rows lower PR589's COPY ranks with all other children fixed. Each unit of the decoder
constant moves 288 rank-7 children to rank 6, matching `deficit = 32(888 − 9·cst)`. Full
values are in `RESULT-BUDGET.json`.

## What this means for interface work

- A recursive-interface mechanism for the complex supplier is worth at most a 4.1% exponent
  gain until the bit supplier improves. Its *net* saving, after all parent-side work, needs
  only 2 units of local paid mass per call. Larger complex mechanisms should be paired with
  a bit-side improvement.
- Improving the bit supplier alone currently changes nothing. Bit-side work should report
  its κ together with a complex profile that can absorb it.
- For κ > 0.01 the complex side needs about 3.1% of its local paid mass removed net. That is
  about 20% of either the boundary class or the target-delivery class. The bit template
  needs more than the elimination of copied information.

## Scope and limits

- These are **model prices**, not constructions or lower bounds. No mechanism here is
  shown to be realizable, and any real interface pays parent-side work set to zero here.
- Holding idle hosting fixed is an optimistic choice. A real interface could also change
  helper hosting, live stock, calls, the bad-class surcharge or the outer argument.
- The classifier partitions the already-admitted profile. Scalar exactness, compensation,
  cones, owners and hosting are checked by the selected replay and are not rechecked here.
- All inherited assumptions of the selected result remain: all-size compilation,
  common-label/mutable-source realization, whole-call hosting, precision/tape, analytic
  transfer and the bit H1–H5 interface.

## Reproduce

```sh
make t21-interface-budget-verify      # or:
python3 -B research/t21-interface-budget/verify.py --work /new/empty/dir
python3 -m unittest tests.test_t21_interface_budget
```

Expected last line: `PASS_T21_INTERFACE_BUDGET_REPLAY` (about 5 s, standard-library Python
3.10+, no network). The replay extracts only `native/local/FULL-WORD.json.gz` from the
hash-pinned `research/community-frontier890-audit/t21-replay.tar.gz`. It checks the U8
content digest `090fd574…c68c5a`, reruns both stages and compares them byte for byte with
the committed results. It then runs a float cross-check that shares no code with the exact
stages, and six negative controls:

| Control | Rejected because |
|---|---|
| C1 a B frame shrunk | non-monotone frame chain |
| C2 one low-end tail moved into FULL cleanup | FULL cleanup touches a low end |
| C3 a low end dropped | profile differs from the claimed U8 profile |
| C4 altered profile handed to the pricer | not the claimed local profile |
| C5 selected complex endpoint + 10⁻²⁴ | both engines prove moment > 1 |
| C6 one unit per call claimed to bind | b stays below c/(1−β) |

## Sources and pins

- U8 word: PR869 (Jeremy Kothe / NewBArch) at `73e86f69…`, as replayed in the selected T21
  archive. Its content digest matches `research/u8-independent-xcheck` (SethBurkart123,
  PR881), whose frame semantics this classifier follows with a different implementation.
- T21 profile and claim: PR890 (Chafik Boukhalfa), `research/complex-t21-owners/data/CLAIM.json`.
- Engines: `moment.py`, `base_two_moment.py` and `outer.py` with the SHA-256 pins recorded in
  the selected `ASSEMBLY.json`; the PR870 `outer47` driver (sha `53f8e62d…`).
- Bit supplier: PR589 (DreamingOfClouds) on PR555 (eumemic), blob-pinned record.
- T37 record: PR942, `research/complex-t37-owners/CLAIM.json` (sha `a383da34…`), selected on main
  at `bbc600db`; its κ is reproduced exactly before its headroom is priced.
- Related work: PR935 (open) already records the telescoping mass identity for X4/U8 and the
  sensitivity to idle children; this note adds the role/phase partition and the bit-binding
  budget. PR933 (open) is a scoped bit-side negative result on relocation. Owner-packing
  gains such as T37 stay below the cap computed here.

Prepared for Aviro (sprint participant) with substantial assistance from Claude Opus 5.5
(Anthropic) via Claude Code. Apache-2.0.
