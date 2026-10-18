# T74 anticipatory compensation: a grouped native prefix

**Finite local construction and exact certificate; no new supplier or kappa.**
For both 80-alias words in [PR2339](https://github.com/CrocSwap/integer-mult-bounds/pull/2339),
the 64 initial compensation terms have a phase-correct native implementation
with **64 monomial applications instead of 128**, retaining all 64 scalar ADDs.
It uses no positive-rank recursive child. Both forward and inverse-transpose
prefixes are checked on arbitrary dirty inputs, including all 512 address columns.

This instantiates a named missing interface in PR2339. The general
warp/add/unwarp expansion, the monomial convention, and the anticipatory
borrowing construction belong to PR2226/PR2269. They are not new here. The
new artifact is the explicit grouped prefix for these changed source words,
its exact serialized phases and address gates, and its complete local operation
inventory. It does not re-audit the remainder of either word.

**Current cost boundary.** [PR2360](https://github.com/CrocSwap/integer-mult-bounds/pull/2360),
head `16d4ea6c26cd45ebb9301ab90f33a73615627f8d`, reports primitive saving
`b < 0.0016870` for the full 400-helper inventory on unchanged T74 bins.
That pending result is context, not independently replayed here. It prevents
presenting the weaker rank-48 packing relaxation as evidence of a competitive
full inventory. Partial aliases or changed stock require their own whole-width
screen before a full construction effort. This prefix is useful as a concrete
component for such work; no hosted improvement follows from it.

The claim is in [discussion #2366](https://github.com/CrocSwap/integer-mult-bounds/discussions/2366).

## Exact boundary and proof

The scientific input is PR2339 head
`bf1742aee4d855efb8bbd44a8419eddb33a679e5`. Both raw source words are retained
byte for byte under `inputs/`; [UPSTREAM.json](UPSTREAM.json) gives original
paths, commit, Git blobs and SHA256 hashes. Their 32 lenders and 32 target
registers are disjoint and start at frame zero. Each lender supplies exactly
two terms with one fixed operator. All prefix register numbers precede the
first removed helper, so PR2269's native register compaction leaves them
unchanged.

For a binary invertible nine-by-nine matrix G, use precisely the predecessor's
Gaussian monomial convention

```
M = I + G^(-T) G^(-1)                       over F2
q_M(y) = sum_i M_ii y_i + 2 sum_{i<j} M_ij y_i y_j  modulo 4
K_G |x> = i^(q_M(Gx)) |Gx> .
```

The binary entries of M in this formula are lifted to 0 or 1. This fixes the
global phase as well as the permutation. The code verifies that convention
directly; unsigned symplectic equality would not suffice.

Fix a lender z and its two terms `y_j += c_j K z`. Apply K to z once, perform
the two scalar ADDs, then apply K inverse. This restores the arbitrary initial
value of z and gives exactly both desired target updates. Corrections from
different lenders commute: every read is from the lender set and every write
is to the disjoint target set. Grouping by lender is therefore valid even
when different lenders share a target. There are 32 such groups, so 64
monomial applications replace the inherited termwise expansion's 128.
No minimality among other possible synthesis methods is claimed.

For inverse transpose, the required map is

```
z <- z - sum_j c_j K^T y_j,       all y_j unchanged.
```

Since K is unitary monomial, `K^(-T) = conjugate(K)`. Apply conjugate(K) to z,
perform `z -= c_j y_j`, then apply `K^T`. The old z contribution is restored
because `K^T conjugate(K) = I`; the desired dual correction remains. In
particular K transpose is **not** K adjoint. The backward prefix changes the
lenders by its prescribed dual shear; it does not restore them to their
original values at this intermediate boundary.

All intermediate address operations are permutations or Gaussian unit phases.
They preserve the frame-zero contract and have no positive Fourier-rank child.
The certificate gives the retained compiler's monomial serialization and a
literal decomposition into address-coordinate XORs (`cnot`), single-bit
Gaussian phases (`z4`) and two-bit sign phases (`cz`). Each decomposition is
checked on all 512 columns. Thus both the compressed recipe and its expanded
address program are inspectable.

If the rest of a source word implements its stated map, substituting this
equal prefix preserves that map. This is a conditional substitution argument,
not a new full-word/native/hosting verification.

## Local bill

The following counts hold **per invocation and per orientation**. The same
counts apply to forward and backward; their maps are different.

| Operation | gauge44/base | extra |
|---|---:|---:|
| Scalar ADD macros | 64 | 64 |
| Monomial applications | 64 | 64 |
| Address-coordinate XOR gates | 1,234 | 1,300 |
| Two-bit sign-phase gates | 819 | 765 |
| Single-bit Gaussian-phase gates | 158 | 162 |
| Positive-rank recursive children | 0 | 0 |
| Real-component scalar primitive bound | 572 | 572 |

The monomial counts are not zero-cost assertions about routing. The address
gate counts explicitly cover that work in the finite nine-bit representation.
They are not a tape running-time bound, a stream-layout proof, or a scalar-ADD
price for every address operation. [EXPECTED.json](EXPECTED.json) also records
the complete entry-phase histogram and moved-address count for each orientation.

There are 34 coefficients of absolute value one and 30 of absolute value one
half. Each scalar macro uses the inherited owned coefficient-scratch protocol:
clear, read source, optionally halve, signed target accumulation, clear.
These are four or five complex-componentwise operations, hence
`2 * (34*4 + 30*5) = 572` real-component primitive passes. The emitted scalar
lowerings are executed by the checker, including the final scratch clearing.
One coefficient scalar suffices when addresses are processed sequentially;
no additional dirty helper or retained full-array copy is introduced. This
owned scratch is separate from the arbitrary dirty input registers.

At the tested address size, the scalar stage contains 32,768 indexed complex
additions and at most 292,864 elementary real-component scalar operations
under that protocol. Address routing and phases are the separate rows above.
The full supplier must still account for layout, ownership, precision and the
rest of the word; 572 is not its total overhead.

## Evidence and reproduction

Standard-library CPython 3.12.3; no network, optimizer or numpy required:

```sh
python3 -I -B scripts/research_package.py --package research/t74-anticipatory-native-prefix
```

The registered hook checks the complete certificate and controls, then
regenerates all recipes/programs and compares their parsed payloads. To run
the independent checker alone, including from a Git-free package export:

```sh
python3 -I -O -B research/t74-anticipatory-native-prefix/verify.py
```

Expected last line:

```
PASS_T74_ANTICIPATORY_NATIVE_PREFIX providers=2 orientations=2 terms=64 monomials=64 scalar_bound=572 controls=24 no_new_kappa
```

Registered replay and metadata/pin checks pass. The optimized independent
checker also passes from a read-only Git-free export (12.48 seconds), preserving
all files. Source corruption, changed receipt and occupied-output controls
reject; recompressing the generated certificate preserves acceptance.

`emit.py` reuses the exact retained Clifford compiler, with its assertions
enabled even under `-O`. `verify.py` imports neither that compiler, the
emitter nor a predecessor checker. It independently inverts the address
permutation, reconstructs M and its phases, decodes serialized monomials,
executes primitive address gates, and replays the complete prefix as sparse
Gaussian linear rows. It compares against the direct forward/transpose block
matrix. Four ungrouped predecessor-style prefixes are positive controls.

For each provider, 128 recipes are checked on all 512 columns. Each of four
programs explicitly replays 32,768 active complex input columns. The other
286,720 columns belong to 560 untouched registers and remain identity by the
checked event footprint. The scalar scratch is cleared after every macro.
All arithmetic is exact Gaussian integers with common denominator two.

Twelve rejecting controls per provider cover global phase, permutation,
address-phase gate, coefficient sign, omitted reference restoration, incorrect
gate order, wrong dual conjugation, understated scalar bill, uncleared scratch,
omitted halving, nonzero lender entrance and wrong operator-to-lender binding.
Each must fail at its specified semantic check. The default replay is read-only;
`--out PATH` writes exclusively to a new receipt. Generator output is likewise
exclusive. Regenerated gzip streams are compared by their complete parsed
payload, not their compression headers.

## Scope and open obligations

This is a finite native prefix, with a short algebraic grouping/substitution
proof. It does not certify whole-word phases or wrappers, the 44 cleanup
buffers, global owner windows (especially the initial lender reads), idle
refill, a complete moment, recursive precision, all-size addressing, tape
implementation, outer transfer or the selected cold replay. No selected
record or frozen predecessor is changed. The full construction acceptance
gate of the original task card is not claimed.

The initial planning screen reproduced PR2339's **inherited reported**
call-weighted rank-48 relaxation in
`[873979185987/500000000000000, 69918334879/40000000000000]`.
This was orientation, not a new profile audit. PR2360's stronger whole-helper
screen was found at the next shared-board checkpoint, so no full-inventory
hosting attempt was started. [TASK.json](TASK.json) records selection,
scope refinement and exact contextual predecessors.

## Open next questions

1. **Which partial low-alias inventory survives the actual bin stock?** Use
   PR2360's whole-width relaxation on a specified subset before native/global
   work. The grouped-prefix proof applies to retained lender groups, but this
   package does not choose or price a competitive subset. This matters because
   the full 32-low-alias stock loses the newer-record cost screen.
2. **Can a surviving subset be spliced into an admitted complete native word?**
   First map its chosen initial reads to actual owner lifetimes and integrate
   the serialized prefix with the remaining native stages. Then price routing,
   scalar work and buffers. The blockers are the selected subset, owner
   availability, whole-word checks and a favorable complete invoice.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Cinna Davis / @1337isnot1337 (PR2226) supplies anticipatory dirty borrowing,
the K_G convention and its Gaussian checks. Jeremy Kothe (PR2269, head
`b479fc5567bc09ab9185bffe89b62594f36d74e5`) supplies the T74 predecessor,
native warp/add/unwarp expansion and dual convention. Sagar Thakrar (PR2339)
supplies both 80-alias words, their initial corrections and the native-lowering
handoff. This package does not claim those contributions as new.

Zhihao Chen / icekylinx and the retained PR425/433/531 lineage supply the exact
Clifford compiler; the copy used here has Git blob
`166841a037f069249f6f7f6dedb89248812f59e2`, identical to PR2269's compiler.
Rohan Arun, Ali Romman, DreamingOfClouds and the retained T74/selected lineage
keep their credit. Douglas Colkitt's ceiling engine supplies the planning
screen. Jeremy Diviney (PR2360) supplies the later whole-width cost boundary;
PR2359's raw-word rank audit concerns a different source change.
Original [PR2226](notices/PR2226.md) and [PR2269](notices/PR2269.md) notices
are retained. Apache-2.0. Evidence is author-checked using two code paths by
the same AI-assisted contributor; no independent human or formal review is claimed.
