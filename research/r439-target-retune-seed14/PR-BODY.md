Retuning one target step after PR967 helper mixing saves three fully paid
ADDs, reducing the complete local word from 11,783 to 11,780. The selected
step would add 18 ADDs on the unmixed PR915 matrix; the improvement appears
only on the coupled middle `E K H^-1`. Both full-word positive bounds stay
unchanged at F=72,847 and B=10,394,084.

The search scores all 12,210 directed one-target insertions, prices all
12 improving nominees and finds ten admitted by the exact prefix guards.
The unique three-ADD saving is the minimum in that fixed one-insertion
class. Both basis gates and all restoration are charged. An independent
set-based verifier reconstructs the source recipe, replays all 661 dirty
columns in both directions, and checks unchanged MOVE/COPY/ERASE records
and rank mass 5,129 through the owning exporter. Fourteen negative controls
and a paid neutral-pair control are included.

```text
python research/r439-target-retune-seed14/verify.py
```

Expected: `PASS_R439_TARGET_RETUNE_S14 pairs=12210 positive=12 admitted=10 ADDs=11783->11780 F=72847 B=10394084 columns=661 controls=14`.

This is a local finite semantic-D construction. The original syntactic H2
and literal K extraction remain false; native multistage replay, complete
hosted adoption and outer assembly are not claimed. No new kappa and no
unrestricted optimum. Only the new research package changes.

Prepared for @woklerx with substantial OpenAI Codex assistance, Apache-2.0.
Credit @theon199's PR967, @bitplane's PR915/926, DreamingOfClouds's PR589,
eumemic's PR555/543 and the predecessors identified in NOTICE.md.
