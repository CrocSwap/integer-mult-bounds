# Shrunk frames under paired lockstep on three-stage covers

Conditional κ = 174051/500000000 = **3.481020 × 10^-4**: **+1.897% over PR #132**
(3.416202e-4), +4.79% over PR #131, +10.65% over PR #130. The complex side binds; the next
κ grid point at denominator 10^10 is rejected.

PR #130 (icekylinx) runs PR #117's h = 24 local complex word at every vertex of an O(70,2)
cover, with every frame equal to its full backward intersection. PR #132 (ikeboy) pairs
first-stage vertices in lockstep. Neither changes the local frames. PR #130's general Clifford
lemma prices any nested transition U ⊆ V of binary subspaces, including degenerate ones, as
one child of width dim V − dim U. A smaller frame is therefore admissible if three conditions
hold: it contains the node's label and every predecessor frame, it lies inside the full backward
intersection, and it is nested in every successor frame.

`lift_shrunk.py` keeps PR #130's lift, then makes one forward pass. It replaces a frame by
that minimal span when the local one-child cost t·log(m/t), with m = 70, decreases. Merging
increments a, b into a + b is cheaper because t·log(m/t) is subadditive. The pass shrinks
15,697 frames. PR #130's unrestricted source-gauge selection then selects 4,553 gauges.

| complex local word on the cover | PR #130 frames | shrunk frames |
|---|---:|---:|
| unpaired saving (PR #130 cover) | 3.147998e-4 | 3.202924e-4 |
| paired saving (PR #132 lockstep) | 3.418543e-4 | **3.483450e-4** |
| κ | 3.416202e-4 (PR #132) | **3.481020e-4** |

## Checks

```sh
make shrunk-paired-cover-verify
```

- `producer.py` is PR #130's producer with the shrunk lift. It regenerates PR #117's pinned DAG,
  the carrier matching, the physical word and the gauge selection, and requires byte-equal
  agreement with the frozen `complex-input.json`.
- `verify_shrunk.py` is PR #130's complete verifier with one assertion changed: a frame must lie
  inside its full backward intersection rather than equal it. Every other check passes unchanged:
  exact supports and divisor 21, labels contained in frames, dependency and carrier nesting,
  236,902 replayed physical frame transitions, histogram recount, full incident source gauges,
  and reverse readout chains.
- Control: `producer.py` also runs PR #130's **unmodified** verifier on the same data. It must
  reject the frames, and only with `Not the full backward intersection`. Every check that precedes
  that assertion in PR #130's code (supports, labels, nesting) therefore passes in the original too.
- `certificate.py` is PR #132's paired certificate on the new inventory. It checks the exact
  moment, the finite bridge, all 47 strict constraints and 7 margins, and next-grid rejection.
  It also checks that the shrunk unpaired saving exceeds PR #130's.

All PR #130 and PR #132 hypotheses remain unchanged:
- PR #132's lockstep and sharing arguments are written proofs, not machine-checked.
- PR #130's cover, bit interface and the inherited analytic and tape interfaces are assumed.

This is a finite conditional witness, not an implementation or a runtime claim.

Credits: icekylinx (PR #130 covers, Clifford frames, producer and verifier); Avi Eisenberg /
ikeboy (PR #132 lockstep, Anthropic Claude assistance); eumemic (PR #117 DAG); an664 (PR #128
sharing); Swapnil Jain and Zhihao Chen (bit word); all inherited contributors. The shrunk-frame
pass, which first appeared in PR #125, and this composition were prepared by Joel Pulikkan with
Anthropic Claude assistance.
