# Paired lockstep vertices in a three-stage cover

Conditional κ = 1708101/5000000000 = **3.416202 × 10^-4** (+8.59% over PR #130, +2.83% over PR #131).

In PR #130's first stage a core occupies only its 24-dimensional active space kA of the 70-dimensional cover space.
The coordinate involution κ (e_i ↔ e_{24+i}, i < 24) makes kA and (kκ)A orthogonal, so the first-stage vertices k
and kκ can share every auxiliary stream. Run in lockstep, each joint frame step is one nested transition of rank
d_1 + d_2, hence one child under PR #130's general Clifford lemma, and the shared tail has rank m − 2h + 2 dim σ.
Stages two and three, all data streams and the bit side are PR #130's, unchanged.

See [PROOF.md](PROOF.md).

## Reproduce

From the repository root (standard-library Python 3; seconds):

```sh
python3 research/paired-cover/paired_cover.py
```

It checks the pinned PR #130 inputs, rebuilds PR #130's unpaired per-vertex profile exactly, verifies the involution,
builds the paired profile, its exact moment, the finite bridge and the 47-constraint assembly, and writes
`certificate.json`.
