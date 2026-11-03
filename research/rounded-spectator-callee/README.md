# A rounded Gaussian callee with exact spectator-row padding return

**Constructive numerical interface; no new kappa.** This package connects the
actual fixed-grid C0 routine from
[PR5485](https://github.com/CrocSwap/integer-mult-bounds/pull/5485) to the
spectator-row planner from
[PR6070](https://github.com/CrocSwap/integer-mult-bounds/pull/6070).
Every numerical call stays inside a complete row. Whole-row permutations
are allowed, but their final permutation is restored before padding disposal.
The result supplies a concrete sufficient answer to the rounded-return part
of [the released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/6056#discussioncomment-19233739).

All padded rows return exactly to zero despite internal nearest-even rounding.
On the live rows, the completed error is less than `2^-P` per complex coordinate.
Inverse exposure precedes the next coarse-dependent diagonal. A subsequent
Gaussian-unit diagonal preserves the error bound. The source C0 accuracy
estimate is inherited; the contribution is its exact row boundary and
executable connection to the spectator layout.

The backend pays its direct cost. It does not supply the fast recursive
Gaussian tariff, a production global-H export, or a selected supplier.
The selected kappa and its five framework assumptions are unchanged.

## Actual interface

The source `plan(n, selected, K, G, Q)` supplies a valid complete-neighborhood
layout. Let `f=len(selected)/K`, `R=plan.R`, and `V=2^n`. Input values are
arbitrary correlated complex grid integers. Their physical complex magnitude
is at most `2^H`. Set

```text
g = P + ceil(f/2) + 1,
w = H + g + 2f + ceil(f/2) + 9,
V' = Q * ceil(2^R / Q) * 2^(n-R),       V <= V' < 2V.
```

A stored pair `(a,b)` represents `(a+ib)*2^-g`. `backend.execute` checks
its integer type, rectangle length and magnitude domain. It uses the pinned
source planner and sparse exposure map, appends complete zero rows, applies
the literal rounded kernel, checks every padded output, removes padding,
and restores the original coordinate layout. It returns a new array;
it is an indexed reference, not an in-place tape implementation.

For each row, map source bit `3j` to the first bit of selected neighborhood j.
Use two distinct passive bits for source bits `3j+1` and `3j+2`. The source
C0 routine never mixes those two bits. Fix every remaining passive bit to
obtain disjoint blocks of size `8^f`. Each block executes the unchanged
`rounded.call(vector, f, 0, w)`. The same call also runs on every padded
block; no work is removed because its input happens to be zero.

The planner has at least `2f` passive bits: its front and back controls
alone occupy at least `3fG` bits, with `G>=1`. Thus this embedding exists
for every valid source plan. This is a statement about payload address
coordinates. It does not treat a physical control field as free data storage.

## Exact zero-row proof

The literal butterfly forms signed sums, differences and half numerators.
All of these are zero on zero input. Nearest-even of zero is zero.
Induction over the `f` butterfly stages proves that every call fixes its
complete zero vector exactly. No error ball is substituted for this fact.

The block index map is a bijection: the kernel and remaining passive bit
sets are disjoint and together cover every bit of the row. Thus the row
map is a product of zero-fixing maps. It fixes the complete zero row.
A whole-row permutation moves the zero row without mixing its entries
with a live row. After the inverse row permutation, every padded row is
again in its original position and is exactly zero. Its payload can be
removed without discarding a live numerical residual.

This proof permits arbitrary data correlations across live rows. It does
not require linearity of the rounded map, cancellation of rounding errors,
or an exact rounded inverse on nonzero inputs. More general row schedules
need the same invariant at every arithmetic cut; an ideal completed
identity on row labels alone does not imply it.

## Completed error and next diagonal

Before rounding, each native block acts on exactly the selected physical
bits with the C0 matrix. The passive coordinates are unchanged. The block
product is therefore the same `I_ROW tensor C` target used by PR6070.
Sparse exposure and inverse exposure are exact permutations.

PR5485 proves that, on the actual stored input, the completed complex
coordinate error after f factors is at most

```text
eta_f * 2^-g,
eta_f = (2^(f/2)-1)/(2-sqrt(2)) < 2 * 2^(f/2).
```

Our choice of g makes this strictly less than `2^-P`. Taking a maximum
over disjoint blocks and rows introduces no row-count factor. The chosen
signed width is the conservative source width, so the source's numerator
and intermediate range bounds apply. Exact zero padding creates no error
term at disposal.

A later exact diagonal D multiplies the error norm by at most its largest
coordinate magnitude. In the actual reference context, D has Gaussian-unit
entries, so the maximum complex error is unchanged. It must be applied
after inverse exposure: the table depends on the original coordinate
labels. A rounded or differently normalized later diagonal needs its own
error and coefficient contract.

## Complete direct cost and storage

There are exactly `V'/8^f` native calls and `f*V'/2` butterflies. The source
charges 28 integer operations, four real reads and four real writes per
butterfly. The new receipt therefore charges

```text
native integer operations = 14 f V',
native real reads = native real writes = 2 f V'.
```

These counts include all padded rows. They exclude no paid native call.
The index construction, gathering, scattering, row permutation, zero
initialization, padding check, array copies and inverse exposure add
`O(n V')` word work. The complete indexed reference thus uses
`O((n+f)V')` word work and `O(V'(w+n))` bits of owned logical storage.
Address words have n bits; arithmetic words have w bits. These are direct
bounds, not an accelerated recursive tariff or a constant-workspace claim.
Python object overhead and allocations are not a fixed-tape lowering.

The sparse support-router theorem stays with PR6070. This reference uses
explicit indexing and does not claim that Python gathering implements
that router's asymptotic physical cost. The proof of padded payload return
also does not prove erasure of every compiler or routing control field.

## Evidence and reproduction

The default verifier reads and compares [RESULT.json](RESULT.json). It checks
actual rounded calls, exact source and physical-coordinate oracles, all
padded zeros, arbitrary payloads, exact basis columns, nonconstant next
diagonals, source/destination overlap, widths f=1,2,3, K=1,2,3, stock Q=1,3,5,
and varied precision/magnitude inputs. The finite fixtures corroborate
the written all-size argument; they do not establish it by sampling.

The original four-call port loop remains a negative control. With a live
x bank and zero y bank, it returns two nonzero y coordinates. Interpreting
that y bank as disposable padding violates this package's row-local cut
contract. Other controls reject the wrong native axis, an early coarse
diagonal, invalid stored inputs, insufficient word width and changed
source bytes.

From the repository root, CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/rounded-spectator-callee
python3.12 -B scripts/check_research_commit.py --package research/rounded-spectator-callee --check-source-history
```

Expected markers: `PASS_ROUNDED_SPECTATOR_CALLEE`,
`PASS_REGISTERED_RESEARCH_PACKAGE`, and `PASS_RESEARCH_COMMIT_BYTES`.
The registered runner executes the full normal and optimized checks.
The verifier is read-only unless `--output NEW_FILE` is given. It refuses
to overwrite an existing output file. [SOURCES.json](SOURCES.json) binds
both executed source files to canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Open next questions

Can an accelerated, source-owned recursive Gaussian callee preserve complete
zero rows at every rounding cut while meeting the same error bound? First
export its literal call order, ownership map, complete simultaneous stock,
rounded boundaries and full cost. If it mixes padded and live rows, supply
a different proved return/disposal invariant. This package does not supply
that callee or the missing production global-H descriptor.

No selected cold replay, native all-width supplier admission, uniform
compiler, fixed-tape schedule, full precision/recovery theorem, Lean or
Docker run is claimed. Independent human and proof-kernel review remain
open. The current source planner's compact-control guard and physical
layout assumptions remain in force; small executable layouts are semantic
fixtures, not production-size compact-control demonstrations.

## Credit

JoyboyBrian / @JoyboyBrian supplied the actual rounded arithmetic, all-width
error and range contracts in [PR5485](https://github.com/CrocSwap/integer-mult-bounds/pull/5485),
and the genuine nonzero-bank counterexample in the linked handoff.
zxv / @zxv supplied the spectator planner, sparse exposure and exact reference
in [PR6070](https://github.com/CrocSwap/integer-mult-bounds/pull/6070).
The elementary zero-fixed-point argument is not claimed as a new general
theorem. The new work is the source connection, exact padded-row invariant,
completed error transfer and full direct cost receipt.

Retain Dugongue's native-port lineage, Nick Petalas's conditioning work,
Arham Tahir's rounding precedent, Vlado Vojdanovski, Jeremy Kothe,
Chafik Boukhalfa, DreamingOfClouds, and the retained support-router,
compact-layout, compiler, precision and analytic authors. Source notices
remain in their unchanged packages. Prepared by Ali Romman with
substantial OpenAI Codex assistance. New work is Apache-2.0.
