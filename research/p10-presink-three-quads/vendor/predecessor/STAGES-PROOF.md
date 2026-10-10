# Mandatory stages of the pre-sink retiming successor

This package starts from PR #320 commit `1b37957d1520c80b6ea796bf418e52be5109c2d4`.
Its untouched stage proof is preserved as `UPSTREAM-PR320-STAGES-PROOF.md`; that text describes the predecessor.
The active stage list in `portable_bit.STAGES` is:

    descent -> target -> kernel -> restore -> presink -> sink -> reorder

Parity fusion precedes this list; exact five-stage lowering follows it. `verify.py` requires a nonempty receipt
for every stage, and its negative controls reject omission of each mandatory stage, including `presink`.

| stage | frozen selection | actual operation |
| --- | --- | --- |
| descent | `descent-selection.json` | inherited 480 frame retimings |
| target | `target-selection.json` | inherited 120 target-prefix groups |
| kernel | `kernel-selection.json` | inherited 1,047 shared-donor entries, entrance rank 1,200 |
| restore | `restore-selection.json` | inherited 240 early-restored helpers |
| presink | `presink-selection.json` | four constructed-frame retimings, three 8→9 and one 13→14 |
| sink | `sink-selection.json` | inherited seven terminal sinks, rebound to the new input word |
| reorder | `reorder-selection.json` | same 133 scalar incidences and delta, with rebound records and 24 equivalent anchor choices |

The initial four selections and all original transform implementations are byte-identical to the pinned
predecessor. The sink selection retains its operations and binds to the new raw-record hash. The reorder selector
chooses the same 133 scalar incidences and exact ledger delta, but 24 equal-cost side-root placements use
later rank-19 frames instead of rank-18 frames. Its literal scalar ordering and projection hash therefore
differ from the predecessor; full integer and all-column checks verify the identical map.
The separate `presink_transform.py` adapts Rohan Arun's descent checker to an intermediate word with already
restored helper endpoints: it checks exact equality to the incoming final-state map. No full-helper-endpoint
assumption is applied to helpers already restored by the preceding stage.

`PRESINK-PROOF.md` gives the four operations, exact delta, and full obligations. The raw ledger is rebuilt after
this new stage, then the inherited sink/reorder ledger builders and five-stage lowering run on actual emitted
records. All earlier frame obligations are retained in `used_frames`, so adding the stage cannot drop an
inherited prime or chart obligation.

The final construction has 336,253 scalar ADDs, 386,909 local records, R = 8,223, normalized W = 131,658,
and literal stock 658,290. The bit root is 770149364272199/10¹⁸ and
κ = 30782267613603/40000000000000000. The scalar, prime, bank, complex, exact moment, outer and finite stages
remain mandatory. Every inherited conditional interface stated in `PROOF.md` remains a hypothesis.

Prepared with OpenAI Codex assistance; inherited authors and mechanisms are credited in `NOTICE.md`.
