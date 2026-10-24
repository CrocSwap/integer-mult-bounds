# Support obstructions for a source-consuming productive helper

**Scoped obstruction; no improved bound.** A proposed encoder would prepare
native input 34 on the one-dimensional chart `span(73)`, replacing its source
five-dimensional chart. Its desired value is exactly the sum of source entry 13
and arbitrary dirty entry 416. Computing that value is easy; returning the other
independent inputs is the obstacle.

This package proves that **no invertible basis change on the fifteen cold
helpers 417–431, including distributing the compensation among them, can finish
this particular source-consuming construction by ascending scalar transports**.
The same obstruction holds after replacing the entire scalar encoder, allowing
an arbitrary basis on all **457 zero-chart entry registers**, including cold
main registers. Enlarging the local replacement alone therefore does not help.
The result allows arbitrary local exit charts compatible with either declared
suffix. It even drops every suffix native relation, every helper final-frame
constraint, and every intermediate adapter pin. Two retained paths to fixed
main outputs still force the contradiction.

There is also a simpler, stronger obstruction for this same retained suffix:
the required transfer from main input 51 to main output 51 is `1/2`, its input
chart is `span(100)`, but the greatest permitted output chart is `span(45,76)`.
It excludes 100. This rules out **every ascending pure-scalar realization of
the nominated whole-encoder map**, including interleaved compensation and
preparation on cold inputs. The original encoder and original suffix pass all
forward and inverse support checks, providing a positive control.

These are proofs about specified families, not conclusions from an unsuccessful
pivot search. They do not exclude changed scalar suffix contacts, paid
nonmonotone transports, or other productive-helper constructions. In particular,
undoing `T` immediately after the paired native operations changes the suffix
and falls outside both theorems. Ascending means inclusion of the actual binary
subspaces, not merely nondecreasing dimension. There is no new physical supplier,
compiler admission, multiplication theorem, or value of kappa.

## Exact mechanism and result

The source is the integrated [98-instruction compression certificate](../productive-helper-fusion-certificate/README.md),
with decompressed canonical payload SHA256
`aa4a8241da76abd2c06e6576a3ac09e77781321deaac3ad7d3ce4519342a36e6`.
Indices below are zero-based after removing `climb` records.

The scalar interval `[9961,10111)` contains 150 instructions on 24 independent
roles. Let its rational matrix be `M`. Change the output basis of helpers
417/419 by `T = [[1/2,-1],[1/2,1]]`, then exchange roles 416/417 by `P`.
The desired output on 416 is exactly `entry13 + entry416`. Prepare that output
with `E: 416 += 13`. In coordinates with 416 first,

```
S = P T M E^-1 = [[1, 0], [c, D]],    alpha = D^-1 c.
```

Here `alpha` is supported on the fifteen initially zero-chart outside helpers.
For an arbitrary invertible basis `Q` on these helpers, prefix compensation
installs `beta = Q alpha` copies of the protected value. The remaining exact
outside transformation must be `D Q^-1`. The checker reconstructs, over the
rationals, the following identity on **all fifteen cold coordinates**:

```
alpha = -D^-1[:,78] + (1/2) D^-1[:,431].
```

If `beta_i != 0`, that input slot must carry direction 73. Reversing an ascending
scalar circuit shows that a nonzero inverse coefficient requires its input chart
to be contained in the corresponding output chart. Both outputs 78 and 431
exclude 73, so both entries in row `i` of `Q D^-1` must vanish. The displayed
identity then gives `beta_i = 0`, a contradiction. Invertibility of `Q` ensures
some component of `beta` is nonzero. [PROOF.md](PROOF.md) gives the full argument.

The independently rebuilt suffix bounds are:

| Local output | Greatest relaxed suffix chart | Shortest retained path |
| --- | --- | --- |
| 78 | `span(25,45,462)` | 8 paid edges to main 125 |
| 99 | `span(45,76,411)` | 8 paid edges to main 114 |
| 431 | `span(45,76)` | 9 paid edges to main 125 |

All exclude 73. Outputs 78 and 431 suffice for the universal cold-basis argument;
99 is retained as a supplementary suffix-cap check. Both program orientations
and both the literal and coalesced suffix are
checked. Coalescing uses the credited commuting-ADD rule from PR4692, checking
every crossed instruction. No claim of arbitrary suffix equivalence is made.

The stronger replay replaces `[6347,10315)`, the complete scalar part of phase A
after its last early native operation. It keeps all 632 independent inputs and
reconstructs its sparse rational matrix and inverse. The same two-column
annihilator identity holds on all 457 zero-chart entry coordinates; the
compensation now has seven nonzero entries. Fresh suffix graphs from cut 10315
give the same excluding caps at 78 and 431. The proof is therefore unchanged.

The main-input obstruction uses the same whole-encoder interval. Since `P T`
fixes output 51, its required coefficient on input 51 remains `1/2`. An explicit
13-edge paid path from output 51 to main 114 at fixed frame 144 excludes input
direction 100, even after every native relation, helper final pin and adapter
pin is released. Both declared suffix variants and orientations are checked.
The original source control checks all 3352 forward and 3168 inverse nonzero
coefficients with no violation. See section 6 of [PROOF.md](PROOF.md).

## Reproduction

From the repository root, using Python 3.12 and its standard library:

```sh
python3 -I -B research/productive-helper-inverse-support/verify.py
python3 -I -O -B research/productive-helper-inverse-support/verify.py
```

The default replay is read-only and needs no solver, network, Git history, or
discovery artifacts. It authenticates its live source, reconstructs the local
matrix and Schur factorization, verifies the exact annihilator, rebuilds both
suffix graphs, and validates explicit paths to main pins. Sixteen corruption
controls address source coefficients, compensation, the identity, native pairing,
path continuity, and terminal constraints. The checked source preserves all
632 arbitrary inputs; this local result never treats dirty helpers as zero data.

The new argument has been checked by separately developed agent scripts and
the packaged replay. This is AI-assisted verification, not independent human
review or proof-kernel verification. Source pins and executable dependencies
are listed in [SOURCES.json](SOURCES.json) and [VERIFY.json](VERIFY.json).

## Open next questions

The structured questions are in [TASK.json](TASK.json). A useful next test is
to change an actual suffix dependency, then check
the corresponding exact inverse-support equations before synthesis. Another
escape is to price a nonmonotone realization; it must beat the complete
paid-minus-helper invoice, including any return transport and native changes.
Passing the necessary equations alone would not establish a cheaper circuit.

## Attribution

This starts from Cao Yifan's PR4610 round3 word and Cinna Davis's PR4692 scalar
compression, through flyingviper's PR5301 combined source. Retain Cinna Davis's
PR4470/controller lineage, Dugongue's frame and physical-interface work, zxv's
native/compiler work, Jacob Alan Sussman's flow work, and all predecessor credits.
The elementary reverse-dependency and block-matrix arguments are not claimed
as new general linear-algebra results. The contribution is their source-bound
application, the exact annihilator, and the suffix certificates.

Prepared for flyingviper with substantial OpenAI Codex assistance and independent
agent checks. Apache-2.0. The selected result and frozen sources are unchanged.
