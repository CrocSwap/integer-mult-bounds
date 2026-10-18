# P104 rounding defects through 201 real output channels

The fixed rank-seven P104 integer-lifting correction occupies an exact
**201-dimensional real output space**, inside its 256 real output coordinates.
It admits an integral Walsh packet with a sufficient **1910-bit** allocation,
compared with a particular sufficient 3072-bit uniform full-defect bank.
This changes correction delivery, rather than the input residue code.

The cost comparison stops at the interface. An explicit, fully restored
delivery oracle pays **7676 signed modular ADD macros, 3072 target CNOTs and
27648 clean work-bank bits**, in addition to the packet and target. ADD
implementations, source access, the encoder, physical routing, exact wide
backend and recursive children remain paid obligations. No favorable complete
recursive cost, admitted supplier or new kappa is claimed.

Scientific base is canonical main
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6; selected record
unchanged. The [canonical investigation claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18983489)
records the bounded question and coordination. [PROOF.md](PROOF.md) gives the
derivation, precise norms/widths, whole delivery boundary and stopping decision.

## Result and coverage

Let N=2^r, L_r be Tekalign's signed-floor word and U_r its ideal Gaussian
linear map. For integer x define D=N*(L_r(x)-U_r(x)). With unnormalized Walsh
H, the encoded vector `c=H*(L_r(x)-U_r(x))` is Gaussian integral and `D=H*c`.
In each Walsh mode m, the defect belongs to the real span of
`(1-i)*i^popcount(m>>(j+1))` over zero bits j of m. This yields an all-rank
written upper dimension `2^(r+1)-F_(r+3)` and explicit independent annihilators.

Exact integer witnesses attain that upper bound at ranks 1,..., 7:

| r | Real span / available coordinates | Encoded packet bits | Uniform full-D bank bits |
|---|---:|---:|---:|
| 1 | 1/4 | 2 | 8 |
| 2 | 3/8 | 10 | 32 |
| 3 | 8/16 | 37 | 96 |
| 4 | 19/32 | 111 | 224 |
| 5 | 43/64 | 305 | 576 |
| 6 | 94/128 | 781 | 1280 |
| 7 | 201/256 | 1910 | 3072 |

At these ranks, 201 in particular is the minimum number of real channels for
a fixed real-linear decoder of every actual defect. This is not a bit count
minimum or a lower bound for nonlinear decoders. The width columns are
sufficient allocations, not optimal widths or total live storage. No rank-seven
defect-image census is performed; all-rank attainment beyond rank 7 is unproved.

The source-authenticated primary checker uses prime 65537 and one source
schedule. The separate internal checker imports no primary or predecessor
executable, uses prime 65521 and a different source schedule, and independently
checks all seven dimensions and bounds. Nonzero modular minors give exact
integer/real independence. The universal upper proof plus these finite witnesses
establishes the stated all-integer rank 1..7 result. No formal-kernel or
independent human review is claimed.

The complete delivery macro circuit preserves the encoded source, updates an
arbitrary target by XOR, and literally uncomputes every clean work bank.
Arbitrary dirty spectators are untouched. Its clean work premise is explicit;
it is not an arbitrary dirty-workspace supplier. The credited retained-source
dirty-buffer consumer is also checked, without treating its exact wide backend
as free. A wrong sign extension and an output-invisible cleanup omission are
separate rejection controls.

## Reproduce

From the repository root with standard-library CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/p104-defect-output-channels
```

The registered primary replay checks its typed RESULT.json without rewriting it;
the independent replay and seven behavioral groups follow. Direct normal and
optimized commands are supported, including a Git-free package export. Source
provenance is in PREDECESSOR.json and SOURCES.json. The sole vendored executable
is byte-identical Tekalign/PR3033 `vendor/lifting.py`; the source comparisons are
inherited-source checks, not an independent proof of physical native semantics.
Run `independent.py --summary` for the independent witnesses' hashes and bounds,
or `--json` for every descriptor and pivot.

Finite verification limits: ranks 1..7, 256 real coordinates, 4096 magnitude bits
at primary entrances; at most 2816 generated candidate inputs per rank and 256
elimination rows. The seven result certificates and fixed macro words bound
allocation; Python allocator/collector behavior is not physical tape evidence.
The independent checker uses at most 8*256+500 candidates per rank. Default
replay writes no evidence. The selected cold replay is unrun because selected
sources and the construction are unchanged. Hosted CI is separate.

## Relation to prior work and cost decision

PR3033 splits the word into an exact wide ideal evaluation and a bounded-width
lifting correction. PR3035/3037 concern its input period lattice and 343-bit
coset code. PR3043 prices a reversible input reducer; PR3046 supplies the
inverse-coordinate identity. PR3059 tests pointwise defect images and code-only
source updates, and supplies the dirty-buffer consumer. These premises remain
unchanged. This package instead factors the **real output span** of the exact
defect and explicitly prices one delivery/restoration program.

It does not remove any of the 448 narrow lifting pair sites. Computing the
packet from an already formed full defect adds an encode transform; direct
encoded production has no cheap recursive implementation here. Decoding and
its restored backing also add work. The smaller packet alone therefore gives
no recursive-cost improvement. Stop after this local result; no dependent
search or new selected-frontier claim is proposed.

## Open next questions

1. Specify one direct encoded producer and actual consumer that eliminate enough
   work to pay the complete delivery and literal cleanup bill. Compare full
   rank profiles, access, exact backend, real/imaginary mixing, widths, backing
   and physical routing at the same cuts. Unknown costs remain unknown.
2. Prove or refute attainment of the all-rank upper dimension beyond rank 7 with
   an explicit witness family. Finite low-rank certificates do not establish it.

Structured relevance, first steps and blockers are in TASK.json. Batch members'
restricted source-update, repeated-lattice and block-split questions are distinct.

Ross Richardson, with substantial OpenAI Codex assistance including a separate
internal carry-and-rounding specialist. Credit Tekalign/PR3025/3033, Nick
Petalas/PR3035/3037, Ross Richardson/PR3043/3059, Arham Tahir/PR3046, ywz65 and
the retained P104/native lineage. Apache-2.0. Generic Walsh transforms, modular
shears and rank certificates are not claimed as new. Frozen sources, shared
checkers, selected frontier and maintainer priorities are untouched.
