# Factor the quarter in copied-center delivery

**Finite complex-supplier circuit construction and cost audit; no new kappa.**

The selected #626 CK and JP8 programs each scatter/gather through eight private
copied centers. Each center has 28 signed quarter-coefficient taps. Moving the
common factor `1/4` into one scale of that private center saves **864 real scalar
primitives per complete program**, under the retained binary-Horner lowering.
All copies, source reads, coefficient preparation, scales and clearing are paid.
The literal rewrite adds eight scalar macros, however, and its complete
conservative local invoice **increases by 3,319,594,144** because of the generic
per-macro adapter allowance. This is a scalar circuit saving with a verified
integration limit, not a net supplier-cost improvement.

| Selected program | Original real primitives | Factored | Saving |
|---|---:|---:|---:|
| CK forward | 224,938 | 224,074 | 864 |
| CK inverse-transpose | 224,986 | 224,122 | 864 |
| JP8 forward | 257,232 | 256,368 | 864 |
| JP8 inverse-transpose | 257,280 | 256,416 | 864 |

There are eight additional scalar macros per program, each a charged quarter
scale. No register, recursive child, frame transition, wrapper or restoration
is added. The exact positive prefix envelopes remain unchanged: CK uses 40/62
bits and JP8 uses 64/101 bits in the two orientations, below the inherited
192-bit local allowance. These are operation counts, not measured runtime gains.

## Reproduce

From the repository root, with Python 3.11+ and no third-party dependencies:

```sh
python3 -I -B research/complex-center-quarter/verify.py
python3 -I -B research/complex-center-quarter/check_blocks.py
```

The first command checks every source pin, rebuilds the four modified programs,
executes all changed blocks as literal primitives, replays all 724 formal input
columns of both original and modified scalar programs, and runs the unchanged
native frame/wrapper auditor on the candidates. It compares the complete result
against [EXPECTED.json](EXPECTED.json). Expected final line:

```text
PASS_COMPLEX_CENTER_QUARTER programs=4 centers=32 saving=864_each columns=724 controls=32+50 invoice_delta=+3319594144 kappa=unchanged
```

The second command separately executes the 64 original/candidate block matrices
on an integer quarter grid and compares them against the gather/scatter formula:

```text
PASS_CENTER_QUARTER_INTEGER blocks=64 matrix_entries=57600 clear_controls=32
```

Both commands leave repository inputs unchanged. The first uses and removes a
temporary directory for the inherited auditor's generated receipts. A writable
system temporary directory is required; on restricted Windows installations,
`TEMP` and `TMP` can name a writable scratch directory. `--write-receipt PATH`
creates a new receipt and refuses to overwrite an existing file. Normal runs
always compare the committed receipt. The native subprocess uses `-I -B`, so
its required assertions remain enabled even under an optimized parent process.

## Circuit identity and recursive boundary

Let `C` be the private center, `s` its persistent source, and let the 28 taps
have signs `epsilon_j` in `{+1,-1}`. The exact native program has one paid
rank-eight center call between its center frame and frame zero. All taps are
at frame zero; the checker exhausts these conditions in both providers.

Forward, the old and new blocks are:

```text
old: clear C; copy s -> C; paid descent; y_j += epsilon_j*C/4; clear C
new: clear C; copy s -> C; paid descent; C /= 4;
     y_j += epsilon_j*C; clear C
```

The paid descent receives exactly the old input. For every possible output of
that call, the target increments agree term by term. The source is unchanged,
arbitrary incoming target values are retained, and the private center is erased.

Inverse-transpose, the blocks are:

```text
old: clear C; C += epsilon_j*y_j/4; paid ascent; s -= C; clear C
new: clear C; C += epsilon_j*y_j; C /= 4;
     paid ascent; s -= C; clear C
```

Here the center is zero before gathering, so dividing the completed sum by four
gives exactly the original recursive-call input. The persistent subtraction and
final clear are unchanged. The scale is **before the ascent and after the
descent**: no commutation with a recursive operator is assumed. A control moves
it across the call, preserves the scalar endpoint under identity interpretation,
and is rejected because the input to the recursive call changes.

The reverse gather temporarily has four times the old center value. The full
positive-envelope recount includes this intermediate and the coefficient-work
stream and still produces the exact original global envelope. Endpoint equality
alone would not establish this precision statement.

The primary block checker executes the original primitive lowering on every
formal input, including arbitrary incoming center and coefficient-work dirt.
There are 31 inputs per block. The full scalar replay includes all 716 native
register inputs and all eight private centers. Work clearing for the unchanged
macros follows the retained lowering, whose `clear W` is also checked explicitly
on each modified block. No clean-helper or clean-center premise is used.

## Scalar cost and complete local invoice

The retained emitter charges a nonzero dyadic addition with absolute coefficient
`a/b`, reduced and `b` a power of two, the following primitives per real component:

```text
3 + (bit_length(a)-1) + popcount(a) + (bit_length(b)-1).
```

The three fixed operations are initial work clearing, signed accumulation and
final work clearing. The other terms pay Horner doublings/additions and halvings.
Thus a signed quarter addition costs six and a signed unit addition costs four.
One private quarter scale costs two. Each block saves `28*(6-4)-2 = 54`
primitives per real component. Eight blocks and two real components give
`8*54*2 = 864`. The forward block falls from 171 to 117 primitives per component;
the reverse block falls from 174 to 120. Their differences include every copy,
clear, subtraction and newly introduced scale.

All non-scalar events remain equal as ordered lists. The independent native
auditor checks their incidence with the new scalar gates, the exact paid rank
histograms, wrapper ordering, helper restoration and the 192-bit bound. Each
provider's histogram matches its selected SPEC.

The pinned `invoice_allcold.py` also charges a conservative adapter allowance
`A = 16*(macros + children + n + centers) + 64*m`, with `m=73`, compiler cost
`K = 64*(m+1)^3 = 25,934,336`, and local bound
`max(real_primitives) + A*K`. The checker independently reconstructs both
original bounds against SPEC, then prices the new program's actual macro count:

| Provider | Original local bound | Literal factored local bound |
|---|---:|---:|
| CK | 11,058,401,095,386 | 11,061,720,689,530 |
| JP8 | 11,334,342,462,720 | 11,337,662,056,864 |

The eight extra scale macros add 128 adapter allowances. Consequently the
bound changes by `128*K - 864 = +3,319,594,144` for each provider. Both remain
below the inherited `2^48` local cap, but the rewrite does **not** lower this
complete bound. This stops the experiment at a finite circuit construction
and scoped accounting result. A grouped center-microcircuit admission rule could
be a separate investigation; no such rule or saving is implemented or claimed
here. All recursive children and other inherited local charges are retained.
The global owner allocation, invoice and exponent assembly have not been rebuilt.

## Pins, scope and completed coverage

- Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Selected #626 source: `660de893d27bb7abd1d5b01b1640207528a5c851`.
- #622 construction: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
- #623 dispatch: `e39a615ca601ce5d62abeb24f3fcdb8644ca1005`.
- #543 bit supplier: `2065fe4f72a914d907f1046603f5a36f17018535`.

[SOURCES.json](SOURCES.json) pins all 14 consumed inputs. The selected record is
followed through its inventory to the #626 SPEC and original emitter/auditor.
Program and canonical-word payload hashes are checked against the selected
SPEC, and each individual program hash is checked as well. Compressed artifacts
are pinned by their exact decompressed payload, allowing gzip repackaging.

OS assignment seed **35** selected the complex track, JP8 first and center 3
for the initial witness/controls. The completed domain is all eight centers of
both selected providers in both orientations: 32 transformed blocks, all using
the same exact identity. The stopping rule is completion of that domain and
its validation. There is no randomized circuit search or optimality claim.
The [local claim](CLAIM.md) records three candidates and the overlap review.

The 32 new block controls cover missing/wrong scaling, wrong tap signs, omitted
source copying, dirty-center initialization, terminal and coefficient-work
clearing, omitted paid children and scales moved across recursive calls. The
native auditors reject their 50 inherited controls. The separate integer checker
rejects 32 private-clear omissions. See [VALIDATION.md](VALIDATION.md) for the
additional frame, prefix, packaging and corruption checks actually run.

This package imports no pending PR implementation. It adds a local replacement
to already emitted programs; production integration would require an admitted
emitter/typed construction step, refreshed program bindings, and a global
hosting/invoice/outer replay. The original all-size/compiler, common-label and
mutable-basis realization, pooled hosting, normalized residual, precision/tape,
exact recovery, bit-supplier and analytic assumptions remain. Finite exact
replay is not a Lean proof or a formal multiplication theorem. The selected
frontier and `upstream/` are unchanged.

## Attribution and related work

Prepared for **@ssteeper with substantial OpenAI Codex assistance** in research,
implementation, exact checks and writing. All work here was performed in one
agent session; no independent human review is claimed. New files are licensed
under the repository's Apache-2.0 license.

Credit to icekylinx's copied-center, direct-delivery and primitive-emitter
lineage; Jeremy Kothe/AtomScout's #622 construction and CK/JP8 predecessors;
Chafik Boukhalfa's #626 package; DreamingOfClouds' cold-helper and native auditor
work; Dominik Scholz, Dugongue, Rohan Arun, eumemic and the cumulative sources
credited in the retained maintainer review and package notices. The unchanged
auditor itself retains its PR514/PR433 notices.

Concurrent [#745](https://github.com/CrocSwap/integer-mult-bounds/pull/745)
(Sagar Thakrar) motivates explicit arbitrary private-center inputs and the
initial-clear control. [#750](https://github.com/CrocSwap/integer-mult-bounds/pull/750)
(Sagar Thakrar) relocates a live CK cleanup scale; this contribution factors a
disposable center at its recursive boundary. [#696](https://github.com/CrocSwap/integer-mult-bounds/pull/696),
[#723](https://github.com/CrocSwap/integer-mult-bounds/pull/723) and
[#734](https://github.com/CrocSwap/integer-mult-bounds/pull/734) lower individual
coefficients; [#722](https://github.com/CrocSwap/integer-mult-bounds/pull/722),
[#739](https://github.com/CrocSwap/integer-mult-bounds/pull/739) and
[#751](https://github.com/CrocSwap/integer-mult-bounds/pull/751) share or gather
cleanup work; [#749](https://github.com/CrocSwap/integer-mult-bounds/pull/749)
changes the compensation target basis. They are distinct and are credited as
concurrent context, not dependencies. No additive saving with them is claimed.

The final refresh also found [#755](https://github.com/CrocSwap/integer-mult-bounds/pull/755)
by @taizaki69, pinned at `a1dd9f819102c40e0b5e4a75215cf69ee864f480`.
Its forward-center runs cover the same 224 JP8 taps using retained coefficient
work and #696's cheaper macro lowering. This overlap is explicitly credited;
no priority or stronger primitive-saving claim is made for forward JP8 centers.
This package adds the reverse gather's common-target factor, CK coverage, exact
recursive-input equality and a complete cost audit of the literal extra-scale
encoding. Coefficient work remains cleared after every addition. The observed
adapter increase is part of the result. [#769](https://github.com/CrocSwap/integer-mult-bounds/pull/769)
by @24kHandsome1201 reuses varying CK coefficient magnitudes in cleanup and
preconditioning; it does not cover these center blocks. Neither pending source
is imported.
