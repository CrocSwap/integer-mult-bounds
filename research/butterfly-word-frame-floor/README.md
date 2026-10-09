# The frame floor of PR217's butterfly word

**No new κ, no certificate change.** PR212 bounded the bit coarse saving of one *word* --
#200's physical bit word, shared by #205, #206 and #207 -- over every admissible choice of
operation frames. PR217 builds a **different word**: 440 isolated four-input XOR
reassociations (880 graph nodes and scalar controls) on top of PR211's cascade frames and
PR200's construction. This note runs PR212's method unchanged on that word.

## Result

At 1,200 Lagrangian rounds, the round count of PR212's published run, on PR217's head
`b739fc226a54a4a507989aa1bef092d491287451`:

| Ledger | PR200's word (PR212) | PR217's butterfly word (here) |
|---|---|---|
| own: floor on `C` | 2,804,210 | 2,800,700 |
| own: coarse saving < | 6.904e-4 | **6.913e-4** |
| own: κ < | 6.900e-4 | 6.908e-4 |
| completed banks: floor on `C` | 2,780,144 | 2,776,634 |
| completed banks: coarse saving < | 6.964e-4 | **6.973e-4** |
| completed banks: κ < | 6.959e-4 | 6.968e-4 |

The like-for-like pair at 400 rounds moves together as well (own 6.909e-4 vs 6.918e-4,
banked 6.969e-4 vs 6.978e-4), so the comparison does not depend on the round count.

The word's own numbers, recomputed here from its certificate:

| quantity | PR200's word | PR217's butterfly word |
|---|---|---|
| certified coarse saving, own ledger | 6.7777395e-4 | 6.7938424e-4 |
| `D/C` of the certified layout, own | 6.7837287e-4 | 6.7998615e-4 |
| certified coarse saving, completed banks | 6.8366e-4 (PR207) | 6.8516596e-4 |
| `D/C` of the certified layout, banks | 6.8427e-4 (PR207) | 6.8578301e-4 |
| κ of the composition | 6.831904550365e-4 (PR207) | 6.84696826673891e-4 |

**So the butterflies raised the ceiling and the achieved value by about the same amount,
and the room left is slightly smaller than before.** On the completed-bank ledger the
distance from the achieved `D/C` to the ceiling is +1.68% here against +1.77% on #200's
word; on the κ basis, +1.77% against +1.86%. Changing the DAG is not a way to enlarge the
frame slack -- it is a different word with its own, slightly higher, ceiling. PR212's own
scope statement already said that non-frame changes are unbounded by it; this note only
confirms that the bounded part still binds after the change.

## Can PR216's admitted cuts be carried onto this word?

PR216 (`research/coordinated-crossover-pr200-v2`, head `34abdc5`) is a third layout on
this same lineage: it keeps PR211's cascade frames, adds 220 further operation-frame
changes, and admits them natively (κ = 6.838643131376e-4). Because the ceiling above
bounds *every* frame layout of PR217's word, the natural next question -- combine the
two -- has a bounded answer, and `transfer_check.py` checks its structural side against
the two packages themselves:

* **The two words are one operation-index space.** Both have 41,288 operations, and the
  parts that fix the DAG are identical: 11,856 arcs, 25,900 order entries, 1,760 reuse
  pairs, 3,960 gauges, 6,624 root roles, 17,688 phase-1 and 7,728 plain operations, and
  the same 1,760 sources and reads. Exactly **880 operation contents** differ -- PR217's
  reassociation set -- and 7,068 operation frames differ.
* **PR216's admitted frames are keyed by that same index.** Its records are
  `[op_index, [basis vectors …]]` pairs: 6,191 current bases, 6,258 override records and
  2,268 canonical subspaces, all with indices inside the shared list. Only **3 of the
  6,258** override records land on a rewritten operation, and **none of the 2,268**
  genuinely different subspaces does.
* **So a merge is well defined at the index level, and that is the whole of what is
  free.** PR216 admits its cuts with "scalar operations, source/target contracts, …"
  fixed, and PR217's change is exactly in those operations: a merged layout is a new
  submission that needs fresh global admission and a fresh column replay, not a
  transplant of an existing certificate.
* **And the prize is capped.** Any frame layout of this word gives κ < 6.968e-4, i.e. at
  most **+1.77%** over the 6.84696826673891e-4 record, while PR216's own layout on the
  plain word sits **0.122% below** that record -- the merge would have to recover the
  butterflies' whole contribution before it recovers anything. For scale, the bank
  absorption of #219 claims +2.30% over the same record with an accounting ledger, which
  is the route this comparison actually favours.

## How the word was obtained and checked

1. PR217's own constructor, `research/butterfly-coordinated-bit-211/candidate.py`, was
   called with `--bit-root` at PR202's head `8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d`
   (fetched from `pull/202/head`). It rebuilds the changed word from PR200's frozen word,
   PR211's pinned frame payload (`opframe-bases.json.gz.b64`) and the frozen butterfly
   overlay, checking each of those hashes itself.
2. The three emitted payloads reproduce PR217's own declared hashes exactly:
   `graph_p12.json` `2bb271df49780365…`, `word_p12.json` `ef77a7d30390a21c…`,
   `frames_p12.json` `4e0fce06f07a044e…`, and the word rebuilt here has 41,288
   operations, 18,908 roles, 1,760 reuse pairs, 3,960 gauges and **11,671 changed
   operation frames**, the number its `expected-bit.json` declares. That match is what
   ties this note's word to PR217's.
3. The tree handed to `ceiling.py --tree` carries PR217's emitted `graph_p12.json`,
   `word_p12.json` and `frames_p12.json`; PR202's unchanged `kchron_p12.json`,
   `sinks.json`, `profile_p12.json` and vendored PR168-v4 checker; and a certificate
   shim whose `bit` record is PR217's own post-terminal profile plus the pre-sink profile
   restored by the terminal record (`{3, 21} x -102`, i.e. +34 children of width 3 and
   +34 of width 21 and +34 roles, giving `W = 20,668` and rank mass 1,486,160).
4. `ceiling.py` accepted the tree and passed every self-test on this word: the certified
   layout lies inside every derived joint frame bound, **its slot chains reproduce
   PR217's certified ledger child for child** (`W 20,668`, rank 1,486,160) and the
   terminal substitution is exactly `[3, 21]` per sink and stage, with every per-slot
   floor below the actual chain cost. Fact 1 reproduces the certificate to eight digits
   (`6.7938424e-4 < D/C = 6.7998615e-4`, gap 0.089%).

## Reproduce

`rebuild_word.py` rebuilds the emitted payloads and checks them against PR217's
`expected-bit.json`; `build_tree.py` assembles the `--tree` input; then run PR212's
script unmodified:

```sh
python3 rebuild_word.py --package <pr217 checkout>/research/butterfly-coordinated-bit-211 \
                        --bit-root <pr202 checkout> --out <fresh dir>
python3 build_tree.py   --emit <fresh dir> --bit-root <pr202 checkout> \
                        --package <pr217 checkout>/research/butterfly-coordinated-bit-211 \
                        --tree <fresh tree>
python3 <pr212 checkout>/research/bit-frame-ceiling-200/ceiling.py --tree <fresh tree> --rounds 1200
```

`transfer_check.py` compares PR217's emitted word with PR216's, from the same emit
directory:

```sh
python3 transfer_check.py --emit <fresh dir> \
    --pr216-package <pr216 checkout>/research/coordinated-crossover-pr200-v2
```

## Scope and limits

* This bounds **frame layouts of PR217's word only**, and only in the sense PR212's floor
  has: joint per-operation frame bounds, an exact per-slot dynamic programme and
  Lagrangian coupling between the two registers of an operation, with the certified
  layout as its own control.
* The butterflies themselves are part of the word. Nothing here bounds further
  reassociation, other circuits, other reuse, gauges or sinks -- the escapes PR212 lists.
* The pre-sink profile in the shim is reconstructed, not read from PR217's own receipt:
  the delta is exact arithmetic and `ceiling.py`'s child-for-child self-test is the
  check, but a run of PR217's own `run_bit.py` would settle it directly. That run needs
  Linux (`resource` limits and `signal.alarm`) and the pinned numpy 2.3.5 / scipy 1.17.0;
  this machine has numpy 2.4.4 / scipy 1.18.1 and Windows, so the emission was driven
  through the package's own `candidate.py` instead, which is the stage that produces the
  word.
* All κ remain conditional on the interfaces each submission states.

## Credits

PR212 (Chafik Boukhalfa) supplies the method and the script, unmodified; PR217 (hcg890)
supplies the word, its overlay and `candidate.py`; PR211 (Rohan Arun) supplies the pinned
cascade frames; PR200/PR168 v4 (Chafik Boukhalfa, eumemic, icekylinx) supply the base
word and the vendored checker; PR216 (Dugongue) supplies the cut package whose admitted
frames are compared above -- that comparison reads PR216's own witness files, its native
admission was not run here. This note adds only the run, the shim, the comparison and the
reading.
Prepared with Anthropic Claude assistance; Apache-2.0.
