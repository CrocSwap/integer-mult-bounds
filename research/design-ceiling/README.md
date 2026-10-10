# A κ ceiling for #144's paired-cube design

This package proves that no word on #144's paired-cube design can certify more than

    κ < 2.5592 × 10⁻³        (complex saving a < 2.5657 × 10⁻³),

whatever its circuit, root groups, gauges, reuse pairs, terminal sinks, frames and `p`. It makes no κ claim and
changes no existing file.

For comparison, the selected construction on main certifies κ = 6.618855 × 10⁻⁴. The ceiling is about 3.87 times
that. Going beyond it needs a change of design, not a better word.

## What is fixed, and what is not covered

The design is the paired-cube ports, the identity `K + H + B = I`, the coordinate-star decoder, the `K` step on the
source registers and the three-stage shared cores. A word must obey the eight rules of [PROOF.md](PROOF.md) §3.4.
They describe #144's word format, as checked by `scripts/paired_cube/verify.py`, the frame-and-reuse layer of
#155–#168 and the terminal-sink gate of #168.

The ceiling does **not** cover:

- **source-assisted words** (#184, #191, #193, #194), which use the original source registers as controls and reuse
  registers after exact cancellation;
- a different decoder, port family or stage structure;
- the bit supplier. The bound is on the complex saving, and κ is also below the bit saving.

## The argument

Write `D = 2v − 3ℓ` for the deficit and `C = Σ n_r·r·ln(m/r)` for the cost of the ledger's children. Every certified
saving satisfies `a < D/C`, and `κ < a/(1+a)`. So it is enough to show that every word pays a cost of at least
`C(p)`.

The floor `C(p)` comes from one structural fact: along any path of a source value from its injection to a target,
frames never decrease. Three lemmas follow.

- **Every source enters at its own line.** Its role's register starts at dimension 1 and must climb to the full
  space.
- **Every source needs two registers that leave its line and stop again before the full space.** One subspace
  larger than the line misses at least `4(p−3)` of the source's targets.
- **Every target needs two registers at its own hyperplane, or an extra stop of its own register.** Each such
  register can only go to the full space afterwards.

A charging argument adds these to the fixed cost of the data registers. Each ingredient lowers the ceiling:

| Floor | Ceiling on `a` |
|---|---:|
| data registers and star copies only | 6.3627e-3 |
| + one register per source | 4.2121e-3 |
| + a second register per source | 2.9420e-3 |
| + registers at each target's hyperplane | 2.7868e-3 |
| + source roles enter from frame 0 | 2.7653e-3 |
| **+ the `K` itinerary of the source registers** | **2.5657e-3** |

The maximum over `p` is at `p = 13`. Every `p` from 7 to 99 is evaluated exactly, and a tail bound covers `p ≥ 100`.

[PROOF.md](PROOF.md) is self-contained: the ledger, the rules, each lemma with its proof, the charging argument and
the numbers.

## Run

    python3 research/design-ceiling/ceiling.py --check     # the ceiling, exact; under a second
    python3 research/design-ceiling/ceiling.py --brute     # counting lemmas at small p; a few seconds
    python3 research/design-ceiling/model_check.py         # the lemmas on #144's word; about 15 seconds

All three use the Python standard library only and refuse `-O`.

- **`ceiling.py`** evaluates `D/C(p)` in exact rational arithmetic, with every logarithm enclosed between two
  rationals, and asserts the side conditions of the charging argument at every `p`. `--check` compares the results
  with `expected.json`.
- **`ceiling.py --brute`** enumerates the counting lemmas: over every vector at `p = 7, 8`, and over one vector from
  each symmetry orbit for `7 ≤ p ≤ 16`. This is a sanity check; the proofs cover every `p ≥ 7`.
- **`model_check.py`** rebuilds the proof's abstraction for the certified #144 word (`p = 12`) with the repository's
  own producer. It checks that the abstraction lists exactly the certified children, and that every lemma's
  conclusion holds on that word. `--tree PATH` runs it on another checkout; on #168's word (`p = 11`, with frame
  layer, reuse pairs and sinks) it also passes.

## How far from tight

On #144's and #168's words the floor is 19% and 26% of the certified cost. The proof charges two registers per
source, and the certified words use about eight auxiliary registers per port. Closing that gap needs a lower bound
on frame-constrained circuits for `H`, which this package does not have.

## Related

- #183 (romainhedouin) gives the assembly's acceptance ceiling in closed form. This package bounds the supplier
  saving that enters it.
- #192 bounds one fixed word (#168's) over all frame layouts, at 7.010e-4. This package bounds every word, far less
  tightly.

## Credits

- icekylinx: the paired-cube design, its compiler and independent checker, shared cores and assembly (#144, #130).
- eumemic: the frame-and-reuse layer and terminal-sink gate (#155–#168), used here to state the rules and for the
  local check on #168's word.
- jamesyc: the terminal-sink lemma (#166) and birth-read reuse (#124).
- an664: completed-core sharing (#128).
- romainhedouin: the assembly ceiling (#183).

The lemmas, the charging argument and the scripts were prepared by DaysSky, assisted with Claude.
