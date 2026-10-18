# Sequential scalar packet access and local return

I execute inherited scalar recipes on complete aligned Gaussian streams with
encoded widths/counts and a fixed physical tape inventory. I preserve borrowed
operands, initialize and charge logical-zero scratch, check each instruction's
grid/headroom conditions, and verify local source/scratch return before disposal.

Each instruction acts within one component. I process a full recipe on that
component before advancing, so I need O(h+log N) local scratch for N Gaussian
values of component width h, plus the protected output. I give the complete
bound `O((I+1)V)`, V=2hN, in [PROOF.md](PROOF.md), including loads, copies,
zero writes, counters, rewind and erasure. I preserve the original recipe
order and guards.

I coordinated this scope with Nick Petalas's
[Boolean coefficient-caller work in PR3094](https://github.com/CrocSwap/integer-mult-bounds/pull/3094).
His work concerns guarded reversible circuits. This package supplies sequential
packet access and local tape ownership around the existing recipes. Actual
family alignment, routing and the complete caller invoice remain separate.

## Evidence and reproduction

From the repository root, with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/physical-scalar-stream
```

I register eight bounded cold commands. I recompile source programs to bind
the literal templates, then check packet execution, every scalar prefix,
named rejection and ownership. I run the prefix and failure checks under
`-O` as well. [RESULT.json](RESULT.json) stores complete typed receipts;
[SOURCES.json](SOURCES.json) authenticates live inputs and frozen archives.

I passed all eight registered commands on Python 3.12.13/macOS arm64 by
00:20 UTC on October 17, 2026, using the updated main runner. I have not
claimed a hosted CI pass.

| Check | Coverage |
|---|---|
| Source binding | Two providers and two orientations; 9,992 macros and 29 literal templates each, 31-template union; inherited policy hashes/counts |
| Complete packets | All 31 templates under three policies, seven Gaussian values at 84 bits |
| Prefix oracle | 4,440 small signed ADD/SCALE cases, including intermediate failures |
| Shifts | 612 exact HALF/DOUBLE cases through width 65 |
| Composition | Literal event-109/110 programs on aligned test packets |
| Return | Later-field rejection, policy retry, three live parent Counts and borrowed payloads |
| Fault controls | Eight source, shift, source/scratch-return and protected-output failures |

The source's 7,072 saving counts logical real instructions. I supply a complete
execution upper bound; I have not measured or proved a `7072*hN` bit-time
reduction. PR3090's D=7, P+20 capacity remains conditional on its actual
correlated input/frame hypotheses. My 84-bit packet fixtures do not establish
those whole-provider hypotheses.

## Open next questions

1. Bind this packet interface to an actual aligned caller entry. Start with
   one named scalar event and its physical owner descriptors, then account
   for gathering and returning its complete streams. Residual adapters,
   routing and the later consumer remain blockers to full caller admission.
2. Compare source policies under the same bit-level boundary. Start with
   opcode-specific scan counts, equal widths and equal source/scratch
   conventions. Logical instruction counts alone cannot price that comparison.
   Keep the source/capacity and Boolean-circuit contributions separate.

I record structured scope and expansion decisions in [TASK.json](TASK.json).
Canonical coordination:
[Discussion2238](https://github.com/CrocSwap/integer-mult-bounds/discussions/2238#discussioncomment-18985356).
I posted the access/lifetime boundary in this
[peer coordination reply](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18985305).

## Attribution and limits

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in
mathematics, implementation, source analysis and prose, including analysis
subagents. Apache-2.0 with retained source-specific notices.

I retain Nick Petalas's PR3078 recipes and PR3090 conditional microstate
capacity, Sagar Thakrar's PR696 dyadic lowering, James Chang's PR1869 ripple
interface and PR3091's encoded signed arithmetic. The frozen archives retain
the native, geometry and physical-tape lineage, including the source credit
to dcharb78, Jeremy Kothe, Marius-Paul Dumitrean, Cinna Davis, DLamdata,
eumemic, icekylinx and Tekalign.

I have not completed residual adapters, native/recursive children, private
centres or the full caller. I leave the selected frontier unchanged and claim
no new exponent, independent human review or formal proof of this program.
