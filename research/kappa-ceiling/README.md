# A κ ceiling for #168's word

This package proves that no choice of operation frames for #168's complex word (eumemic, `4a3c769`) can certify more
than

    κ < 7010/10^7 = 7.010e-4.

#168's κ = 6.558894e-4 is 93.6% of that. So every frame refinement still possible on this word is worth at most
**+6.9%** in total. Going further needs a different circuit, different reuse or gauges, or a different design.

The package makes no κ claim and changes no existing file. #168's word is not on main, so the package carries the 48
files of #168 it reads as a pinned archive (`baseline-pr168.tar.gz`, 0.6 MB), following the convention of
`research/coordinated-frames-and-entrance-banks`.

## What is bounded, and what is not

The ceiling covers one word. Its DAG, operations, carrier arcs, 2,310 gauges and reuse pairs, and 47 terminal sinks
stay fixed, and only the operation frames vary. It does not bound constructions that change any of those, which is
how every large past gain was made.

## The argument

For a shared-core supplier with deficit `D = 2v − 3ℓ` and cost `C = Σ n_r·r·ln(m/r)` over its children:

1. **Every certified saving satisfies `a < D/C`,** from `e^x ≥ 1 + x`. On #168 the certified savings sit within
   0.09% of `D/C`.
2. **κ is below the assembly's ceiling `G`** of each supplier's saving, using PR #183's closed form.
3. **Splitting a frame climb into more steps only costs more,** because `r·ln(m/r)` is subadditive.
4. **No frame layout can push `C` below a floor `C_floor`.** The floor comes from three ingredients:
   - frame bounds propagated jointly through both registers of every operation;
   - an exact per-register dynamic programme over frame dimensions;
   - Lagrangian coupling of the two registers of each operation (400 integer rounds; each round is a valid floor).

   So `κ < G(D/C_floor)`.

[PROOF.md](PROOF.md) has the statements and proofs.

| Floor used | Ceiling on κ |
|---|---:|
| two steps per register (Fact 3 alone) | 1.153e-3 |
| joint bounds + per-register programme | 7.158e-4 |
| **+ Lagrangian coupling** | **7.010e-4** |

Design ceilings for any word with #168's ports and decoder (h = 22, v = 1,320), under the hypotheses of PROOF.md:

| Hypothesis | Ceiling on κ |
|---|---:|
| one auxiliary register per source | 4.08e-3 |
| no auxiliary registers | 6.24e-3 |
| no auxiliary registers and no centre loss | 1.25e-2 |

## Run

    python3 research/kappa-ceiling/ceiling.py --check     # stdlib only, about 50 seconds; -O is refused

The script first rebuilds the pinned #168 files in a temporary directory. It checks the archive's sha256 and every
file's sha256 against `SOURCE.json`, whose hashes are those of commit `4a3c769`. Anyone can confirm them with
`git show 4a3c769:<path> | sha256sum`, or rebuild the archive byte for byte with
`git archive --format=tar 4a3c769 <paths> | gzip -n -9`. It then regenerates #168's complex word with #168's own
producer, reads the frozen physical layer and the terminal sinks, computes every bound, and compares the results with
`expected.json`. `--tree PATH` runs on a full #168 checkout instead.

It checks itself:

- #168's own layout lies inside every derived frame bound;
- its slot chains reproduce #168's certified complex ledger child for child, and the sink record;
- every per-slot floor, and every Lagrangian round's total, lies below #168's actual cost.

All bounds use exact integers with rounded-down logarithms, so the printed ceilings are upper bounds.

## Credits

- eumemic: #168, its physical-layer word and checker, and the terminal-sink gate.
- icekylinx: the paired-cube framework, compiler, gauges, shared cores and assembly (#144, #130).
- romainhedouin: the closed-form assembly ceiling (#183), used for `G`.
- jamesyc: the terminal-sink lemma (#166).

The bounds, the frame floor and this script were prepared by DaysSky, assisted with Claude.
