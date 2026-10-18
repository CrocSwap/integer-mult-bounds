# Output sign frames replace large workspace restorations

This is a recursive-interface research construction with a sharp boundary
cost in a restricted model. It does not improve the selected multiplication
exponent. With five fixed children, an eight-coordinate dirty workspace and
one output coordinate, a complete source-dependent echo uses **96 ADD + 104
NEG**, versus **96 ADD + 160 NEG** with eager restoration. Both restore every
scratch coordinate on every input. The saving is 56 scalar negations.

The restriction matters: child calls are indivisible. The parent may negate
either the whole output register or the whole workspace between calls. A
compiler that can remove a child's internal drift can beat both words. For
example, the explicit matrix leaves below expose their final negations; direct
evaluation of their sum is cheaper than the echo. This is an exact interface
result, not an optimized matrix algorithm or a runtime benchmark.

## Interface and exact boundary cost

Work over the integers, rationals or complex numbers with exact arithmetic.
Let `D` have width `d`, `W` have width `N`, and let fixed children satisfy

```
C_i(D,W) = (D + R_i W, -W),       i = 1,...,k.
```

Each `R_i` is a linear map. A child's private scratch is arbitrary and restored;
its cost includes its reader, source access, source negation and private work.
The caller has both execution directions at the same declared scalar cost.
These children are involutions, but the implementation still emits the literal
reverse word for inverse calls. No sign-controllable reader is assumed.

The desired batch is `B(D,W)=(D + (sum_i R_i)W,W)`. Eager execution restores
`W` after every child, for `kN` additional scalar NEG instructions. The parent
can instead execute these operations:

1. Call the first child directly.
2. Before each subsequent child, negate all `d` output coordinates.
3. At exit, negate `W` if `k` is odd, or negate `D` if `k` is even.

Before child `i`, both registers are in sign `(-1)^(i-1)` relative to the
canonical eager state. Linearity makes the child's increment have that same
sign. It then flips `W`, and the next output negation aligns the two signs
again. The final operation restores both canonical registers. This proves the
batch identity for every dimension and every tuple of linear maps, including
nonzero readers of every changing workspace coordinate.

The additional cost of this schedule is `2 floor(k/2)d + (k mod 2)N`.
Choosing it when `d<N`, and eager restoration otherwise, gives

```
b(k,N,d) = (k mod 2)N + 2 floor(k/2) min(N,d).
```

This is the minimum **uniform** boundary cost over all maps `R_i`, using one
call to each fixed child in the fixed order and only complete-register
negations in the `k+1` gaps. It need not be the minimum for a special tuple
whose contributions cancel, for partial-coordinate operations, or for a
different call alphabet.

To prove the lower bound, track signs `t` on the original output and `w` on
the workspace. After normalizing the output by `t`, child `i` contributes
`tw R_i W`. Correctness for independently variable `R_i` requires `tw=1`
before every call. Every call flips `tw`. Consequently each of the `k-1`
interior gaps and the exit gap needs at least one boundary negation. If `a`
workspace and `b` output block negations are used, `a+b>=k`. Restoration also
requires `a = k mod 2` and `b = 0 mod 2`. Minimizing `aN+bd` under these
constraints gives the displayed formula, and the two schedules attain it.
Operations in the entrance gap cannot improve this lower bound.

Thus `d>=N` yields no saving in this model. For `d<N`, the batch saving is
`2 floor(k/2)(N-d)` scalar NEG instructions. Each NEG is paid; no metadata-only
reinterpretation of a physical register is counted as a free operation.

## A transparent echo and a recursive implementation

Let `X` be a width-`N` source that is preserved, and let `W` be arbitrary dirt.
With `R=sum_i R_i`, execute

```
W += X;  B(D,W);  W -= X;  B^-1(D,W).
```

The two batch calls contribute `R(W_initial+X)-R W_initial = R X`. The final
state is exactly `(D_initial+R X, X, W_initial)`. This includes both sets of
child calls, both source copies and all batch restorations. The inverse
reverses every instruction and changes every ADD sign. Oddness alone does not
make this echo transparent: `(W+X)^3-W^3` still depends on dirt. Linearity is an
explicit interface assumption, not a conclusion inferred from finite tests.

`word.py` recursively realizes this contract. A leaf performs its signed
matrix ADDs and negates its source port. An interior reader runs the echo
using its child readers, then negates its own source port. One dirty block per
active interior level suffices; siblings reuse the block after restoration.
No clean initialization, hidden accumulator or extra copy register is used.
This realizes a tree of sums of linear maps. It does not supply a missing
multiplication or supplier interface.

For a reader node `v` with `k_v` children, let `A_v,G_v` count all ADD and NEG
instructions, including descendants and both directions. With common widths
`N,d`, the complete recurrence is

```
leaf: A_v = number of nonzero signed matrix entries; G_v = N
A_v = 2 sum_i A_i + 2N
G_v = 2 sum_i G_i + 2 b(k_v,N,d) + N
```

For a root echo, omit the final `+N`. Eager restoration replaces `b` by `k_v N`.
All children are called twice. The last `+N` is the reader's source drift,
not scratch cleanup. A tree of maximum depth `h` uses `d+(h+1)N` scalar data
registers, counting output, source and all dirty scratch. There is no input
size recurrence or bound on kappa being inferred from this depth recurrence.

The frozen instruction format has four fields per ADD and two per NEG. For
`A` ADDs and `G` NEGs, the explicit interpreter invoice is:

| Resource | Exact count |
| --- | ---: |
| Arithmetic instructions and dispatches | `A+G` |
| Data reads | `2A+G` |
| Data writes | `A+G` |
| Instruction fields, including signs and addresses | `4A+2G` |

On a unit-cost addressed machine, assigning prices to these resources gives
a complete weighted execution bill by substitution. With atomic inclusive
ADD/NEG prices `alpha,gamma`, the recursive reader cost is
`T_v=2 sum_i T_i+2N alpha+(2b+N)gamma`. Source reads and restoration are already
included. Preparation is separate: the supplied compiler materializes the
whole frozen word. For source-description size `M` and `P=A+G`, it uses
`O(M+P+h)` compiler/program storage and `O(M+(h+1)P)` worst-case preparation
time; the frozen word must be read at execution as priced above.
Its construction and validation are not free online work. On a tape machine,
routing between addresses and address/control realization must also be
implemented and charged. No end-to-end saving is claimed before those costs
and the fixed-child contract are justified for a real supplier.

At the seed-selected dimensions, the echo has 17 scalar data registers, 200
dispatches, 296 data reads, 200 writes and 592 descriptor fields. Eager uses
256 dispatches, 352 reads, 256 writes and 704 fields. A depth-three reader
uses 33 data registers and 21,328 scalar instructions, versus 27,544 eager.
These are exact event counts, not elapsed-time measurements or bit costs.

## Reproduce and inspect the evidence

From the repository root, with Python 3.11 or newer and no dependencies:

```sh
python3 -I -O -B research/output-sign-restoration-seed51/verify.py
python3 -I -O -B research/output-sign-restoration-seed51/test_package.py
```

Expected markers:

```
PASS_OUTPUT_SIGN_RESTORATION schedules=21840 recursive_cases=384 saved_NEG=56 source_pins=3 kappa=unchanged
PASS_OUTPUT_SIGN_PACKAGE relocation=1 corruptions=4
```

`verify.py --emit` prints the complete recomputed certificate. The ordinary
command compares every field with `CERTIFICATE.json`. It also authenticates
the three retained predecessor notes by SHA256 and Git blob identity. These
checks run under Python's optimized mode; no required check uses `assert`.

The independent boundary enumeration replays all `4^(k+1)` words for each
`1<=k<=6`. Each gap chooses identity, workspace negation, output negation or
both. It tracks an independent formal coefficient for every child, without
using the sign-frame formula. All 21,840 schedules are covered, 126 are
admitted, and their minimum costs agree at all 384 width pairs `1<=N,d<=8`.
The stopping rule is completion of this finite domain. The lower bound above
is a written proof for general k; enumeration alone is not that proof.

The recursive census covers `1<=N<=4`, `1<=d<=3`, `1<=k<=4`, depths one and
two, both schedules and both echo/reader contracts: 384 cases and 3,168 basis
columns. Every case also checks the literal inverse and a rational dirty
probe. Leaves use `random.Random(51)` with coefficients in `{-1,0,1}`. The
separate dense selected example uses seed 51 and `{-1,1}`; deeper examples
use seeds `51+depth` at depths two and three. All coverage is completed.

Seven mathematical controls catch an omitted output sign, source uncopy,
workspace restoration or entire second pass; unframed deferral; a nonlinear
dirty echo; and a premature canonical-output observer. Seven invalid inputs
are rejected. The package test relocates the complete directory and rejects
four actual file corruptions. The selected source construction is untouched,
so its costly cold replay is outside this check's scope.

Local verification passed on CPython 3.14.8 in normal and optimized mode,
and CPython 3.11.17 in optimized mode. Both versions passed standalone
relocation and all package corruptions. Canonical certificate regeneration
was byte-identical. This archive-based package retains its own offline source
pins and commands; it does not opt into the optional catalogue-based generic
replay manifest introduced during the session.

## Open next questions

Does a currently supported recursive supplier expose an indivisible
`(D+R W,-W)` child with `d<N` whose internal drift cannot simply be removed?
This determines whether the boundary saving can improve an actual supplier
rather than only the stated interface model. The first step is to trace one
candidate's full source-return map and retained child boundary, then price
both schedules with its routing and precision requirements. No such supplier
has been identified here; that concrete contract and its complete physical
invoice are the blockers. A visible terminal source negation that the parent
can cancel is an immediate reason to reject the candidate.

## Observation contract, provenance and credit

The caller observes canonical registers only when a batch or echo returns.
During an output sign frame, the physical output can be the negative of its
canonical partial sum. Adaptive readers, exception exits or recursive clients
that demand a canonical intermediate output need an additional priced
interface. This example does not establish their safety. Exact arithmetic is
also essential here; fixed precision, overflow and rounded inverses are not
verified. The all-input basis checks establish the emitted finite linear
maps, not a formal proof of the full integer-multiplication theorem.

Base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`. The selected certificate at
that base is PR1094's conditional `836330098538459/500000000000000000`, by
Rohan Arun on Jeremy Kothe's packing and the retained slot/T16 and bit chains.
Its actual assembly, manifest, review and construction README were inspected;
their hashes are recorded in `SOURCE-PINS.json` as context, not dependencies.
None of that selected evidence or `upstream/` is edited.

Aaron Wang / navinor's [PR1155](https://github.com/CrocSwap/integer-mult-bounds/pull/1155)
provides the eager/deferred batch question. Sagar Thakrar's
[PR1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199), mightyOil's
[PR1203](https://github.com/CrocSwap/integer-mult-bounds/pull/1203), and Adam
Gall's [PR1205](https://github.com/CrocSwap/integer-mult-bounds/pull/1205)
already establish compatible nonzero readers and observation distinctions.
No priority for those results is claimed. The new mechanism pays for changing
the output sign while keeping each reader fixed, with a sharp uniform
boundary minimum and a recursively executable transparent echo. PR889's
common-factor dirty echo is also credited for the existing cancellation
method, by CubeJerry. Exact heads and byte-identical retained notes are pinned; no code is
imported from these contributions.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance, including
the algebra, implementation, evidence and prose. New material is Apache-2.0
under the repository license; retained notes keep their original notices.
No independent human review, hosted CI result, physical supplier admission,
new kappa, or complete formal multiplication proof is claimed.
