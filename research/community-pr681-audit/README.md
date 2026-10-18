# Independent replay of PR #681's complex-factory resynthesis

Audit of [#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681) by
Alluri (@alluri-ritual), pinned at head
`e536f6fc8aad65adef8ac4682d13625598a5c3f9`. Credit for the construction belongs
to #681. This audit covers its own contribution,
`research/complex-factory5-resynthesis/`: one 34-gate exact replacement for the
87-gate coordinate-total window in all fourteen blocks of the PR622 raw
K-triangle constructor. The bundled #696 lowering was audited separately in
[#783](https://github.com/CrocSwap/integer-mult-bounds/pull/783).

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60` (current `main`, also the
merge base of #681). Only `research/community-pr681-audit/` is added.

**Verdict: the 1,484-operation saving is confirmed exactly, for the raw
constructor word. It does not touch the selected providers and does not change
κ.**

## Reproduce

From the repository root, Python 3.11+, standard library, offline, about 30 s:

```sh
python3 -B research/community-pr681-audit/replay.py
```

Expected last line:

```text
PASS_PR681_INDEPENDENT_REPLAY windows=14 scalar_saved=1484 fwd_primitives_old=170488->160296 fwd_primitives_pr696=128696->123768 kappa=51110230636731/31250000000000000
```

No #681 code is imported. The 87-gate template and 34-gate witness are
transcribed (without frames) from #681's `CIRCUIT.json`, sha256
`f64a9e88491af13fe564f0512e8455eb268d1732a978b1b4fe3b93e601b59f71`.
Temporary files are removed.

## What the replay checks

1. Runs the unchanged constructor on `main` directly, not through #681's
   tracing extractor.
2. Scans the fresh `A` word for the 87-gate template under injective register
   relabeling with a constant frame. It finds exactly 14 windows on pairwise
   disjoint registers; `BLOCKS.json` is not used.
3. Checks the template and witness give the same exact rational map, forward and
   inverse.
4. Splices the witness into each window with that window's frame. Before
   rebuilding the cleanup, it confirms the old cleanup equals the literal
   inverse rule.
5. Compares exact sparse linear forms of all 716 registers after `A`, `A+B` and
   `A+B+cleanup` for the old and new words. All other word fields are identical.
6. Runs the inherited native audit, emitter and local auditor from `main` on
   both words, then recounts the emitted programs.

| Quantity | Before | After | Saved |
| --- | ---: | ---: | ---: |
| Raw scalar events (precondition+cut+A+B+cleanup) | 6,340 | 4,856 | **1,484** = 2·14·(87−34) |
| Native scalar operations (incl. 10,632 compensation adds) | 16,972 | 15,488 | 1,484 |
| Forward primitives, inherited Horner lowering | 170,488 | 160,296 | 10,192 (5.98%) |
| Backward primitives, inherited Horner lowering | 170,536 | 160,344 | 10,192 (5.98%) |
| Forward primitives, #696 lowering | 128,696 | 123,768 | **4,928 (3.83%)** |
| Backward primitives, #696 lowering | 128,712 | 123,784 | **4,928 (3.83%)** |
| Forward / backward prefix L1 bound | 86,491,024,246 / 2,028,759,644,357/2 | 68,417 / 1,649,462 | — |

- **Beyond #696.** Once #696's lowering applies, #681 adds 4,928 primitives per
  orientation on the raw word, not 10,192. The consolidation's 170,488 → 123,768
  (27.40%) breaks down as 41,792 from #696 plus 4,928 from #681. It is
  composed correctly, not added from headlines.
- Paid profiles and phase/adapter/center events are unchanged. The 98 frame-climb
  events within the windows are reordered because the new circuit touches
  registers in a different order. Each register's climb path is unchanged, and
  the inherited audit reports identical frames and edges.
- A randomized replay of the emitted scalar programs with dirty inputs, including
  the private register, gives identical final states.
- Mutating one witness coefficient makes the replay fail.

## κ

#681 changes no existing file except a ledger note. In particular it leaves
`certificates/selected-result.json` and the selected CK/JP8 provider words
unchanged. Its README states that the edits are not transported through the
selected provider recipes. The 1,484 operations are therefore raw-constructor
operations, not selected-factory operations. As #783 showed, scalar primitives
enter only the finite per-vertex invoice, not the κ assembly. The selected κ
remains `51110230636731/31250000000000000`.

## Limits

The prefix bounds come from the inherited auditor and were not re-derived.
`make verify`, `make frontier626-verify`, Lean and #681's hosted replay were not
run. #681's local `verify.py` and the consolidation's local `verify.py` were run
and pass. The other five consolidated packages (bit-supplier R420 work) were not
audited. Transporting the edit into the selected providers remains open work.

Rohan Guliani (@Rohansguliani), with substantial AI assistance. New files are
under the repository's Apache-2.0 license.
