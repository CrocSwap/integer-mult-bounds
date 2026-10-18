# R439 phase-B block 509, source 22: the inverse-column invariant closes the second exception

**Scoped all-length obstruction; no new kappa or supplier.** In the eleven-wire
F509 model of [PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368),
the only wire its forward dependency rule leaves below the rank-four block frame
is exceptional source 22. The all-length inverse-column frame invariant of
[PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) (Andrey Mas),
applied to this separately pinned boundary, forces source 22 to exit on F509 as
well: the inverse column indexed by 22 includes wires 17 and 468, whose entry
labels are already the full block frame. Combined with the predecessor's forward
bounds, all eleven exits equal F509, and the original single-climb invoice
`{2:7, 3:2}`, block moment `7·2^q + 2·3^q` at `q = 1-a`, is minimal for
`0 < a < 1`. The unchanged continuation and the literal inverse cleanup cannot
turn any replacement into a complete paid-frame improvement.

This closes the *other* exceptional source of the [PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368) handoff
([source-22 request](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18911407)),
which [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) left
open as its next question. With source 19 closed there and source 22 closed
here, both exceptions are resolved and all ten blocks of that handoff are
covered in the stated model. The invariant and its proof are [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511)'s; the
new work is the separately pinned block-509 boundary, its inverse column, the
complete forced-exit table, and the full invoice/continuation/cleanup
conclusion on this block. No synthesis search was needed.

## Concurrent work and what this adds

This is **independent corroboration**, submitted with no priority claim. The
pre-submission overlap refresh found that the same question was claimed and
answered concurrently while this session was working:
[discussion 1515](https://github.com/CrocSwap/integer-mult-bounds/discussions/1515)
posted the same corollary (same inverse-column mask `1423`, same support,
same `{2:7, 3:2}` conclusion), and
[PR1535](https://github.com/CrocSwap/integer-mult-bounds/pull/1535) (CubeJerry)
certifies the same obstruction with two exact implementations, full
661-column scalar replays across three current-main words, and its own
registered package. That submission is the stronger one; treat this package
as a third independently written data point for review, not as the primary
certificate. Relative to the summary of
[PR1535](https://github.com/CrocSwap/integer-mult-bounds/pull/1535), this
package adds only: (i) an explicit orientation control — the inverse *row* of
source 22 has label rank two and does not close the case, only the inverse
column does; (ii) a recorded continuation boundary — source 22's first later
visit is `C[293]` at the full cleanup frame, and all eleven first later visit
frames contain `F509`; (iii) a dependency audit of both invariants at every
prefix of the constructed fixture, mirroring the [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) checker discipline;
and (iv) a single-file self-contained checker with no generated artifacts.
None of these change the theorem. If the maintainers prefer one certificate
per question, closing this as a duplicate of
[PR1535](https://github.com/CrocSwap/integer-mult-bounds/pull/1535) loses no
mathematics.

## Model and exact inputs

The source word is
`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`, SHA-256
`e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`,
Git blob `85a4499bf9e4911a705d50567a2c2ef6cf23739a`. The block is
`B[283:314]`, 31 ADDs, on registers

```text
R = [17, 22, 33, 38, 50, 60, 67, 77, 87, 92, 468].
```

Register 468 is a dirty helper: its input is arbitrary. A **block circuit** is
any finite sequence of `dst ^= src` gates on exactly these registers, distinct
operands, where both operands move to a common rational frame containing their
previous frames. Frames are retained, inclusion-monotone, and contained in the
rank-four block frame `F = F509`. There are no new registers, COPY/ERASE
operations or cross-block changes; proactive promotions are allowed and paid.
Write `q = 1-a`, `0 < q < 1`; a positive rank increment `d` costs `d^q`
(`0^q = 0`).

The geometric labels live over **Q**, independently of the binary circuit
field. Root coordinates (from the pinned word's `lines`) and entry frames
(ids after replaying `D, A, B[:283]`; spanning roots from `frames`):

| Register | Entry frame | Spanning roots | Rank |
|---:|---:|---|---:|
| 17 | 509 | all ten roots | 4 |
| 22 | 182 | 17, 22 | 2 |
| 33 | 185 | 33, 38 | 2 |
| 38 | 188 | 38, 77 | 2 |
| 50 | 52 | 50 | 1 |
| 60 | 62 | 60 | 1 |
| 67 | 192 | 50, 67 | 2 |
| 77 | 186 | 33, 77 | 2 |
| 87 | 189 | 38, 87 | 2 |
| 92 | 184 | 22, 92 | 2 |
| 468 | 509 | all ten roots | 4 |

`F` is the rational span of the ten root lines; `(17, 22, 33, 60)` is a basis,
with ordinary dot-product Gram matrix

```text
(4 0 2 2)
(0 4 2 2)
(2 2 4 2)
(2 2 2 4)
```

determinant 64 (4 under the `<x,y>/2` convention). No reduction modulo two is
used for these spans or determinants.

For an arbitrary independent dirty input column `x`, the block output is `Mx`
over **F2**; rows are bit masks in the register order above:

```text
M     = [1023, 2, 1020, 1011, 943, 991, 959, 891, 1018, 508, 1524]
M^-1  = [7, 2, 262, 271, 80, 33, 65, 391, 958, 516, 1807]
```

The verifier checks `M M^-1 = M^-1 M = I` by exact binary arithmetic. Row 22 of
`M` is the identity row `e_22^T`: output 22 equals input 22 exactly.

## The invariant and its application to source 22

[PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511)'s invariant, restated for this boundary: for any finite legal block
circuit, with `T(t)` the binary matrix from original inputs to current wire
values and `U(t) = T(t)^{-1}`, wire `i`'s current frame `W_i(t)` always
contains

```text
S_i + sum_{j: T_ij = 1} S_j + sum_{j: U_ji = 1} S_j,
```

where `S_j` is register `j`'s entry label. The proof is [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511)'s forward-time
induction (its audit.md Section 3): a gate `d ^= s` changes forward row `d`
and inverse column `s`, and every surviving dependency of either lies in the
union of the old operand supports, whose labels already sit in the common
operand frame. It allows temporary writes, cancellation, carrier preparation
and arbitrary finite circuit length. I restate it with credit and use it; I do
not reprove it here.

Exact inversion gives column 22 of `M^-1` as mask `1423`, support

```text
[17, 22, 33, 38, 77, 87, 468],
```

in particular `(M^-1)_{17,22} = (M^-1)_{468,22} = 1`. Since
`S_17 = S_468 = F`, the endpoint of the invariant forces

```text
W_22^exit >= S_17 + S_468 = F,
```

and every allowed block frame lies inside `F`, so `W_22^exit = F`. This excludes keeping source 22 in a proper rational subframe through the
block exit. Its lower initial frame and earlier intermediate frames remain
permitted until the required promotion. The identity row of `M` at 22 does not help a
replacement: it removes forward output dependencies, not the inverse-column
obligation.

**Orientation control.** The inverse *row* of 22 is also the identity row:
`U_{22,*} = e_22^T`, label rank two. The forward row gives rank two as well.
Only the inverse column closes the case; the checker asserts both orientations
so the distinction cannot be lost.

## Forced exits and the minimal invoice

Forward and dual (inverse-column) forced exit ranks for
`R = [17, 22, 33, 38, 50, 60, 67, 77, 87, 92]`:

| Wire | 17 | 22 | 33 | 38 | 50 | 60 | 67 | 77 | 87 | 92 | 468 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Forward | 4 | 2 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| Dual | 4 | 4 | 4 | 4 | 3 | 3 | 2 | 4 | 4 | 4 | 4 |
| Combined | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |

Every combined label is exactly `F` (a rank-four subspace of the rank-four
`F`). For wire `i` of entry rank `e_i`, the positive frame increments thus sum
to `4 - e_i`. Since `t^q >= t` on `[0,1]` for `0 < q < 1`, any positive
increments `d_k` summing to `D` satisfy `sum d_k^q >= D^q`, strictly when
split. Summing over all eleven wires (including carriers) the block cost is at
least

```text
C_B(q) = 7·2^q + 2·3^q,
```

the original single-climb profile `{2:7, 3:2}` (seven rank-two entries, two
rank-one entries, two wires entering at `F` for free). The original 31-ADD word
attains it; so does the verifier's fixture. Any wire that splits its forced
climb pays strictly more. Scalar ADD count cannot compensate: the objective is
the retained-frame invoice. This is exactly the shape of [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511)'s Section 5
conclusion on the block-508 numbers; the arithmetic here is
entry ranks `(4,2,2,2,1,1,2,2,2,2,4)`.

Unlike the block-508 treatment, no favorable fully charged relaxation is
needed: the invariant rules out the low-source endpoint outright, so no
delayed-promotion scenario exists to price.

## Unchanged continuation and inverse cleanup

Since every replacement-block wire must exit on the same subspace `F` with the
same boundary map `M`, the unchanged continuation starts from identical frames
and data; every later prescribed frame visit and inherited charge is
unchanged. In the pinned word, source 22's first later visit is `C[293]` at
the full cleanup frame (rank 8); every block wire's first later visit frame
contains `F` (the adapter checks all eleven).

For the regenerated literal inverse cleanup: every wire is essential, with a
nonidentity row or column in both `M` and `M^-1` (row 22 is the identity row in
each, but its column is not). Any realization of either map must touch every
wire, so both the old and any replacement inverse slice visit all eleven wires
at their prescribed common cleanup frame, with identical entry frames to that
slice, and the frame charge is unchanged. Writing `C_outside` for everything
outside the replacement slice,

```text
C_complete,new - C_complete,old = C_B,new - C_B,old >= 0    for 0 < a < 1.
```

This uses the fixed surrounding interface and the prescribed full-frame
cleanup. It is not a statement about alternative continuation compilers,
changed readouts, new registers or cross-block rewrites.

## Evidence and reproduction

Standard library only, from the repository root:

```sh
python3 -I -O -B research/r439-source22-dual-frame-obstruction/verify.py
python3 -I -O -B research/r439-source22-dual-frame-obstruction/verify.py \
  --word research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz
```

Expected final lines:

```text
PASS_R439_F509_SOURCE22_DUAL_BARRIER
failure_controls=11 inverse_column=[17, 22, 33, 38, 77, 87, 468] all_exits=F509 bill={2:7,3:2}
```

The default run is self-contained. It computes the rational spans and Gram
determinant, both binary matrix products, the critical inverse column and both
orientations, the full forced-exit table, essentiality of all wires, the exact
invoice, and the concavity premise by integer arithmetic on sample splits
(`d1^p D^(d-p) >= d1^d`). It builds a deterministic 32-gate Gaussian fixture
for `M` at `F`, audits both dependency invariants at every prefix, replays all
2,048 dirty assignments forward and through the reversed-gate cleanup, and
rejects eleven failure controls: proposed rank-two and rank-three source-22
exits (which pass the forward-only bound), a corrupt critical inverse bit, a
singular map, a self ADD, an extra register, one-sided operand hosting, frame
descent, a truncated positive circuit, an omitted inverse gate, and corrupted
source bytes. The fixture is a checker control, not a shortening claim.

The optional `--word` adapter is read-only and binds the constants to the
pinned bytes: SHA-256 and Git blob, root transcription, block frame `F509`,
entry frame ids and rational spans after `D, A, B[:283]`, the 31-ADD slice
`B[283:314]`, its endpoint matrix and `{2:7,3:2}` bill, all eleven first later
visits (each frame containing `F`), and the literal full-frame cleanup shape
(`C` equals the reversed `A+B` z-destination gates at the full frame, rank 8).
It does **not** replay the whole 661-wire dirty word. Finite checks support the
written argument; they are not a proof assistant or an independent human
mathematical review.

Local runs: Python 3.12.14 on Windows, normal and optimized (`-I -B` and
`-I -O -B`), with and without `--word`, all exit status zero.

## Scope and remaining obligations

The result is confined to the fixed eleven-wire block-509 map, the original
wire set, reversible XOR gates with retained monotone common-frame operand
promotion, frames inside `F509`, and the fixed continuation plus literal
inverse cleanup above. It does not settle enlarged seams, new registers,
nonmonotone frame reuse, different gate rules, different targets or changed
continuation compilers. It is not the eight-block result of
[PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368) nor the
block-508 result of [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511);
together the three packages cover all ten blocks of that handoff in this
model. Inherited H2/K bit-interface, native/hosting, precision/tape, all-size
realization and analytic-transfer obligations remain separate. No physical
hosting, supplier adoption, kappa improvement, selected-frontier change, or
complete multiplication theorem is claimed.

## Credit, provenance and license

Predecessor credit: **Arham Tahir** (with substantial OpenAI Codex assistance)
for [PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368) — the
block data, entry labels, forward dependency bounds, the two named exceptions
and the inverse-matrix prefix calculation; **Andrey Mas** (with substantial
GPT-6 Pro assistance through ChatGPT) for
[PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) — the
all-length inverse-column frame invariant and the block-508 closure, whose
audit.md Section 3 argument is used unchanged here. Retained lineage: Aaron
Wang / [PR1015](https://github.com/CrocSwap/integer-mult-bounds/pull/1015);
Ross Richardson /
[PR923](https://github.com/CrocSwap/integer-mult-bounds/pull/923); Sagar
Thakrar / [PR1062](https://github.com/CrocSwap/integer-mult-bounds/pull/1062);
Sricharan Vagvala /
[PR967](https://github.com/CrocSwap/integer-mult-bounds/pull/967); Gareth
Davidson / [PR915](https://github.com/CrocSwap/integer-mult-bounds/pull/915)
and [PR926](https://github.com/CrocSwap/integer-mult-bounds/pull/926);
DreamingOfClouds /
[PR589](https://github.com/CrocSwap/integer-mult-bounds/pull/589); eumemic /
[PR555](https://github.com/CrocSwap/integer-mult-bounds/pull/555) and
[PR543](https://github.com/CrocSwap/integer-mult-bounds/pull/543).

Prepared by **Aaron Wang / navinor** with help from opencode, for the
block-509/source-22 question left open by [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) and requested in the
handoffs thread. The verifier is written for this boundary and imports no
predecessor implementation. Apache-2.0.

## Open next questions

- **Does the same invariant close any lower-frame exception outside these ten
  blocks?** [PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368)'s model covers the ten phase-B blocks only. Why it
  matters: the phase-A slices and `D` sit at other wires and frames, where a
  lower-frame opportunity could still exist. First step: pick one phase-A
  slice, pin its entry labels and map, and compute its inverse-column
  supports; look for a column with no full-frame label. Blocked by: nothing
  but session time; the pinned word supplies all data.
- **Can a same-frame resynthesis lower the scalar ADD count at the forced
  invoice?** The frame bill `{2:7,3:2}` is now minimal, but scalar counts are
  a separate question. Why it matters: scalar reductions still shrink
  complete words even without a moment change. First step: compare against
  `research/r439-frame509-seed08`'s 21-gate factorization and check whether
  any search class is left unexplored. Blocked by: the existing bounded
  searches there; a new mechanism, not more seeds, would be needed to claim
  an optimum.
- **Formalize the invariant and its two applications in Lean.** Why it
  matters: the all-length induction is the load-bearing step for both the
  block-508 and block-509 closures. First step: state the invariant over
  `F2` matrix updates with rational frame inclusion and prove the gate step
  for one update rule. Blocked by: no Lean environment is set up in this
  session; `make formal-pr442-verify` shows the repository's existing Mathlib
  pin pattern.
