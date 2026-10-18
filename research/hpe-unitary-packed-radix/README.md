# A smaller sufficient packed radix under unitary gate premises

For gate-valid normalized Clifford circuits, **B=2^(K+2)** suffices for the
retained packed exact-equality argument, where K is the larger C-gate count.
The existing Lean checker uses `B=4^(K+1)` and a bound valid for arbitrary
literal gate lists. Its theorem and source are unchanged. This is a written
stronger-premise successor lemma, with an independently implemented packed
executor and source-bound tests, not a new kernel-checked theorem.

All three `Exact.lean` pairs have nine C gates on the left and seven on the
right. The new sufficient radix uses 11 bits instead of 20. The largest
packed input integer has **5,622 bits instead of 10,221**. Both radices accept
the three exact identities and reject the phase/character controls. These
are deterministic bit lengths, not a claimed wall-time or Lean speedup.

## Quantified proof and its additional premise

Work on complex N-dimensional vectors, N a power of two. Permutation gates
must be actual bijections with the stated inverse. X must be an involutive
permutation. Diagonal and global-phase gates multiply coordinates by powers
of i. A normalized C gate is

`C_s=((1+s*i) I+(1-s*i) X)/2`, where `s=+1` or `-1`.

Since X is a self-adjoint involution, its eigenspaces have eigenvalues +1
and -1. C_s acts there by 1 and s*i, respectively; hence C_s is unitary.
All remaining gates are unitary by their stated premises, so a normalized
circuit U is unitary. Omitting 1/2 in each of its k C gates yields the exact
Gaussian-integer matrix `Z=2^k U`. Every column has squared Euclidean norm
`4^k`, and every real and imaginary entry has absolute value at most `2^k`.

For circuits with counts k1,k2, put K=max(k1,k2) and compare

`D = 2^(K-k1) Z1 - 2^(K-k2) Z2`.

Every real and imaginary entry of D has absolute value at most `2^(K+1)`,
strictly less than `B=2^(K+2)`. Executing both sides on `u_j=B^j` tests
every output row's sum `sum_j D_ij B^j`. If this is zero, reduction modulo B
forces the constant digit to be divisible by B; its strict absolute bound
forces it to be zero. Divide by B and induct over the remaining digits.
Apply separately to real and imaginary parts. Thus packed equality implies
entrywise equality, including global phase. The converse follows by linearity.

The existing `vec_digits` argument is retained; the new ingredient is the
unitary entry bound replacing the generic gate-by-gate `4^k` bound. A radix
strictly greater than `2^(K+1)` is enough; the chosen next power of two is
convenient and is not claimed minimal for these particular matrices. Their
observed scaled component peak is only 32, but it is not used for admission.

Gate validity is material. The new compiler validates the literal permutation
and inverse on all 512 addresses, XOR masks and signs, and the diagonal/phase
grammar. The comparator's compiled-circuit arguments must come from that
validated compiler; arbitrary hand-built compiled lists are not its contract.
The general original Lean theorem does not require these extra unitary guards.

## Source-bound replay and controls

```
python -I -O -B research/hpe-unitary-packed-radix/verify.py
python scripts/research_package.py --package research/hpe-unitary-packed-radix
```

Only the closed literal parser is reused from `hpe-lean-semantic-binding`.
Its compiler, executor, operator kernels and bounds are not imported. The new
integer executor implements the pinned Lean pullback, phase and C conventions.
For all six source circuits it also runs each ordinary basis vector: 3,072
unpacked columns have exact squared energy `4^k`, the two scaled matrices
agree, and every coefficient obeys the theoretical bound. These checks use
the same new executor and are calibration evidence, not an independent human
proof or independent implementation of each gate formula.

Twelve controls include a phase change, an input character and omitted scale
for each pair; a nonunitary permutation; and an undersized radix. The last
control demonstrates an actual unitary collision at B=1: identity and XOR-1
agree on the all-ones packed input but differ on basis input zero. The strict
radix guard rejects that invocation. Both old and new sufficient radices
reject all six phase/character mutants.

Normal replay checks immutable input hashes and compares the complete receipt
without writing. Registered replay adds Git provenance and source pins.
No frozen source, formal theorem, selected recipe or frontier is changed.
No fresh Lean build, kernel benchmark, complete compiler/hosting/cold replay
or multiplication theorem is claimed.

## Open next questions

Can the norm-preservation and scaled-entry bound be proved in Lean and fed
into `vec_digits`? First formalize unitary semantics for the guarded five-gate
grammar, then state the stronger-premise check theorem. That missing formal
proof and kernel timing block any replacement of the existing checker.
The structured question appears in TASK.json.

## Credit and overlap

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`, priority revision 3,
draw `65cca57f64b00caf9e5994c08eb4ae34`. SOURCES.json pins the exact inputs.
Credit Jeremy Kothe/jeremykothe2's PR593 for the Clifford formalization,
digit uniqueness and three literal pairs; commdata2338's semantic binding
audit for the parser and source correspondence; and the retained Lemma A/G,
icekylinx, Chafik Boukhalfa and jacklightChen lineage.

Concurrent PR1781 by Sagar Thakrar independently checks 2,896 selected child
recipes and 224 adapters with the original `2K+2`-bit radix. Its source head
`dafbaadeb423b3bc80fbf6fcd6f415400dc0ffbf` was inspected through the cached
open-PR body. No code or receipt from that pending PR is imported or claimed
replayed here. This package concerns the changed radix theorem and only the
three retained Lean pairs; it is not another selected-recipe census.

Prepared by woklerx with substantial OpenAI Codex assistance. Apache-2.0.
