# Coupled coarse-grid dirty-reader minimax

**Scoped written proof, with an executable reversible integer-word model and
bounded exact corroboration. No new kappa or productive target credit.**

For the retained two-channel cut

\[
 A=\begin{pmatrix}1&2\\-2&1\end{pmatrix},\quad M=2^b,
\]

keep the source and output on a coarse grid of spacing `gamma`, use two dirty
helper words on the refined grid `gamma/M`, and allow any integer lift `L`.
For an integer source box `|x_j|<=B`, the exact minimum over **all** such lifts
of the worst squared Euclidean output error is

\[
 \boxed{\gamma^2\min\!\left\{
       \left\lceil3B/M\right\rceil^2,
       2\left\lceil B/M\right\rceil^2\right\}.}
\]

The helper and source are restored exactly for arbitrary dirty inputs. The
proof covers every integer `B,b>=0` and every integer two-by-two lift; the
checker exhausts stated finite domains. [PROOF.md](PROOF.md) contains the
quantifiers, attainable residual lattice, lower bounds, constructions,
rounding convention and complete logical resource/headroom contract.

## What changes at the rounded boundary

[Nick Petalas #6666](https://github.com/CrocSwap/integer-mult-bounds/pull/6666)
establishes approximate dyadic **algebraic response** capacity equal to
rational rank in an exact refined dyadic model. The matrix above is a concrete
member of that package's complete 625-matrix two-by-two census, retained here
as an inert source snapshot. It is not bound to a literal P104 native caller
cut. This distinction limits the physical conclusion.

[ToikY #6685](https://github.com/CrocSwap/integer-mult-bounds/pull/6685) already
solves the fixed coarse-grid scalar factor-three case. A coordinatewise norm
replacement would miss the choice proved here. Write `D=AL-MI`. The attainable
residuals obey **cross-row congruences modulo five**. If one residual row is
zero, the other has coefficient absolute sum at least three. If both rows are
nonzero, a single source activates both. These cases give the two lower-bound
branches, and explicit integer lifts attain each branch.

For `M=8, B=2`, the two choices illustrate the effect:

| Lift | Residual `D` | Worst squared error in coarse cells |
|---|---|---:|
| `[[2,-3],[3,2]]` | `[[0,1],[-1,0]]` | 2 |
| `[[2,-3],[4,2]]` | `[[2,1],[0,0]]` | 1 |

Concentrating error in one output improves the joint Euclidean budget even
though the nonzero residual row is larger. The second output becomes exact.
This is an optimization over all integer lifts in the specified four-block
architecture, not a minimum over unrestricted reversible circuits. Singular
lifts are allowed because the source is preserved; the coarsest balanced lift
is zero. Meeting an absolute error budget alone does not prove useful channel
independence.

For `B>=1`, the sharp common precision thresholds are:

| Desired worst Euclidean error | Exact condition |
|---|---|
| Strictly less than `gamma` | Impossible for every finite `b` |
| At most `gamma` | `2^b >= 3B` |
| At most `sqrt(2) gamma` | `2^b >= B` |

The corresponding least precisions are `(3B-1).bit_length()` and
`(B-1).bit_length()`. No arbitrary dirty-phase correlation is assumed: the odd
determinant makes all joint phases attainable. For even determinant readers
this independence can fail; the verifier includes an explicit example in
which the false product-phase bound is twice the actual squared error.

There is a sharp caller restriction: if `L` must be complex-linear, meaning
it commutes with `J=[[0,-1],[1,0]]`, the optimum is always
`2 ceil(B/M)^2`. The balanced lifts attain it; the concentrated lift fails
this constraint. Thus the one-cell improvement cannot be imported into a
caller that requires complex-linear lifts. This is not a claim of quarter-turn
covariance for ties-up rounding or for the whole word.

The same Smith factors do not determine this fixed-box rounded error.
Unimodular matrices take `A` to `diag(1,5)`, whose Euclidean minimax is
`ceil(s_b B/M)`, with `s_b=1` for even `b` and 2 for odd `b`. At `M=2,B=2`
the coupled chart is better; at `M=4,B=2` it is worse. Applying Smith charts
changes the source geometry and output metric unless those changes are
explicitly transported and paid.

## Reversible implementation and bill

[reader.py](reader.py) compiles a literal gate list on the six words
`(x0,x1,h0,h1,y0,y1)`. The inherited chronological blocks are

```
H += L*x
Y += floor((A*H + c)/M)
H -= L*x
Y -= floor((A*H + c)/M)
```

where floors are coordinatewise and `c=floor(M/2)`. Every reader call itself
restores the helper. It forms one numerator temporarily in a helper word,
adds the offset, translates an output by a non-mutating arithmetic-right-shift
view, then reverses the helper operations. No bits are discarded from a stored
word. The negative reader reverses the gate sequence and the ADD signs; it
does not incorrectly replace the rounded function by rounding its negation.

With `P(L)=sum popcount(abs(L_ij))`, the exact logical bill is six roles,
zero clean scratch words, `2P(L)+12` signed word ADDs including four quotient
view ADDs, and eight constant translations for `b>=1` (zero for `b=0`). The
lift coefficients use binary ADDs and are compiled before execution. There
is no runtime division by five. [PROOF.md](PROOF.md) gives explicit guards
for every intermediate register and sufficient signed widths, including
arbitrary declared bounds on incoming helper and output dirt.

The model treats fixed shifted and sign-extended word views as readable
sources of ADD gates. This is an explicit logical capability. Its Boolean
implementation, bit access, carries, movement, interconnect, precision volume,
ownership, scheduling and complete recursive paid bill remain to be supplied.
The program claims no physical word-time or multiplication improvement.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
python3.12 -W error -B research/coupled-coarse-grid-reader/verify.py
python3.12 -O -W error -B research/coupled-coarse-grid-reader/verify.py
python3.12 -B scripts/research_package.py --package research/coupled-coarse-grid-reader --check-only
python3.12 -B scripts/research_package.py --package research/coupled-coarse-grid-reader
```

Expected scientific marker: `PASS_COUPLED_COARSE_GRID_READER`. Each direct
run writes a fresh JSON receipt to stdout, binds all regular package files
by SHA256, and writes no package files. It loads `reader.py` directly from
source bytes, so an adjacent Python bytecode cache cannot replace the kernel.
Normal and optimized runs must generate identical receipts when package bytes
are unchanged. Save a receipt **outside** this package and check it with:

```sh
python3.12 -W error -B research/coupled-coarse-grid-reader/verify.py > /tmp/coupled-receipt.json
python3.12 -O -W error -B research/coupled-coarse-grid-reader/verify.py --check-receipt /tmp/coupled-receipt.json
```

[VERIFY.json](VERIFY.json) registers the two bounded runs. It declares no
external live inputs: the scientific replay is self-contained. The selected
record and task catalogue in [SOURCES.json](SOURCES.json) are base-commit
provenance, not live scientific inputs. The full source-history checker refused this shallow checkout. Committed-byte
and source-hash checks are available, but no ancestry PASS is claimed. These
are separate from availability of every selected supplier artifact.

## Evidence and interpretation

The exact verifier reports:

| Check | Finite coverage |
|---|---:|
| Compiled forward and literal inverse executions | 17,050 fixtures |
| Complete joint error histograms | 250 |
| Exhaustive phase classes across `b=0..4` | 341 |
| Global residual-lattice optimization problems | 93 |
| Admissible candidate residual matrices in those problems | 14,091 |
| Residual lattice/integrality cases | 9,604 |
| Construction and exact gate-bill cases, through `b=64` | 130 |
| Complex-linear versus concentrated lift checks | 130 |
| Precision boundary cases | 237 |
| Headroom corner fixtures | 640 |
| Large signed integer fixtures, through `b=257` | 8 |
| Smith diagonal attaining cases | 15 |
| Semantic, source and receipt rejection controls | 16 |

The finite optimization covers `b=0..4`, `B=1..3*2^b`. It does not pick an
arbitrary coefficient cutoff: every contender at or below the known balanced
upper bound has an explicitly derived bound on each residual row's absolute
sum, and **all** residual matrices within that bound are tested. These are
finite certificates for the listed parameters. The universal result rests on
the written lattice case proof, not on their extrapolation.

The rejection controls distinguish missing cleanup, wrong inverse signs,
non-odd tie rounding, a nonexistent exact dyadic residual, false independent
phases, fixed-chart Smith invariance, insufficient headroom, altered retained
source bytes, and both inconsistent and coherently rehashed false receipts.
[VALIDATION.md](VALIDATION.md) records executed commands and their outcomes.

## Source, overlap and scope

The original `coverage-law-change` card is retained exactly in
[TASK.json](TASK.json). Its full physical productive-credit acceptance gate
was not met. The expressly changed scope is this coupled rounded-boundary
side result. It explains why a response rank of two need not satisfy a chosen
coarse output error contract and gives an executable attaining logical model.

The base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
Selected #6030 remains conditional kappa `0.003125804`, with admitted BIT
`0.0034` and the complex side binding. All five assumptions remain. No full
selected cold replay, selected source-closure PASS, native build, Lean,
Docker, hosted CI, independent human acceptance or formal proof-kernel
acceptance is claimed here. Parent orientation reported the sparse baseline
refused a missing selected checkpoint. Package-local checks do not repair it.

[SOURCE-PINS.json](SOURCE-PINS.json) records exact predecessor heads, file
paths, Git blobs and SHA256 hashes from explicit-commit reads. Only #6666's
census definition is retained as [census-source.txt](census-source.txt), byte
for byte and never executed. Other predecessor proofs are context citations;
the standalone replay does not claim to audit or reproduce their suites.

[OVERLAP.json](OVERLAP.json) records bounded live PR keyword searches and
nearest-work distinctions. #6614's dyadic two-wire unitary approximation,
#6564's connector carry law, #6277's integer fanout operation tariff, and
#5889's affine dyadic feasibility use different contracts. The parent supplied
a broad bounded archive orientation; no repeated broad survey was performed.
Unindexed Discussion replies, arbitrary historical proof text and unpublished
work remain outside this novelty check. No global priority claim follows.

## Open next questions

1. **Actual caller binding.** Does a retained producer/consumer present this
   determinant-five cut with the same source box and fixed output metric?
   Start from one exact caller head and transport all charts and tolerances.
   Without that binding, approximate responses grant no productive target
   credit.
2. **Physical lowering.** Supply a reversible Boolean or tape implementation
   of the declared shifted-view ADDs, then price all six word widths, access,
   restoration and scheduling in the complete signed caller invoice. The
   word-level count is not a substitute for that bill.
3. **Unequal precision and larger lattices.** Derive the attainable residual
   lattice and actual phase image for unequal helper precisions or another
   retained nonunit cut. The present theorem has one shared precision and
   fixed `A`; it does not establish a general capacity/error law.

## Attribution and license

New work: **@CubeJerry, with substantial OpenAI Codex assistance**, including
mathematical exploration, proof drafting, code and documentation. Apache-2.0.
The retained census bytes keep their original Apache-2.0 notice and are by
Nick Petalas (`petalas`). Credit Ali Romman #1135 for the rounded four-call
endpoint and general residue-image method, with Gareth Davidson #1057 and the
#985/#1054 dirty-borrowing lineage; Ali Romman #5615 for exact dyadic
Smith-factor capacity and its credited helper lineage; Nick Petalas #6666
for approximate dyadic capacity, four-shear construction and the census;
and ToikY #6685 for the scalar coarse-output minimax. Floor identities,
Smith theory, reversible shears and binary coefficient synthesis are
classical tools, not new general mechanisms.
