# Four source-bound frame1094 native matrices at width one

## Exact result and boundary

For the frozen PR6353 word, four compiled recipes equal their declared
canonical-frame operators on every one of the 512 standard basis vectors
of `C^(2^9)`, with absolute phase. Each equality covers all 512 output
coordinates. The four maps therefore cover 2,048 columns and 1,048,576
matrix positions, including zeros.

The word is PR6353 head `db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`.
Its exact ordered frame bases include

```
frame 3:    [],
frame 127:  [1,2,4,8,16,32,64,128,256],
frame 712:  [7,9,97,435],
frame 714:  [7,35,75,409],
frame 1094: [7,9,35,66,400].
```

The tasks exhaust this word's paid MOVE uses and public helper endpoint
involving frame1094:

| Kind | Source → destination | Role | Event index | Positive child rank |
|---|---|---:|---:|---:|
| Paid MOVE | 712 → 1094 | 703 | 12917 | 1 |
| Paid MOVE | 714 → 1094 | 704 | 12930 | 1 |
| Paid MOVE | 1094 → 127 | 704 | 12932 | 4 |
| Helper endpoint | 3 → 1094 | 703 | — | 5 |

Indices are zero based. The three moves are public ascents; no owned
transport is involved in this footprint. Exact source bytes, compiler,
integration API, retained native specification and notice are authenticated
by SHA256 and Git blob identity. `produce.py` executes the frozen source
compiler to reproduce `RECIPES.json`. Recipe production supplies data
provenance; it is not the independent mathematical check.

This result concerns these four instances at tensor width one. It supplies
no new generic Clifford compiler theorem, all-tensor-width native theorem,
whole-word native composition or multiplication admission.

## Operator conventions and closed frame kernel

Addresses are the nine-bit vectors `x` in `F_2^9`. Let `X_u` translate an
address by XOR with `u`, and retain the source primitive

```
C_u = ((1+i) I + (1-i) X_u)/2,
F_r = product_(j=0,...,r-1) C_(2^j).
```

All coefficients are Gaussian dyadic rationals `(a+i*b)/2^d`. No floating
point comparison or quotient by global scalar phase is used.

For an ordered partial frame basis `U` of dimension `r`, complete `U`
greedily by standard coordinate vectors in increasing axis order. Let `G`
have those completed vectors as columns, over `F_2`, and put

```
Q = I + G^(-T) G^(-1)  over F_2,
q_Q(x) = sum_j Q_jj*x_j + 2*sum_(j<k) Q_jk*x_j*x_k  modulo 4.
```

The monomial `K=D_Q P_G` sends `e_x` to
`i^q_Q(Gx) e_(Gx)`. The retained source circuit runs `K^dagger`, then
`F_r`, then `K`; its operator is consequently

```
Gamma_U = K F_r K^dagger.
```

For `s` supported on the first `r` axes, define

```
w_r(s) = (1+i)^(r-wt(s)) (1-i)^wt(s) / 2^r.
```

The closed kernel follows directly by applying those three factors:

```
Gamma_U(x+Gs,x) = w_r(s) * i^[q_Q(x+Gs)-q_Q(x)],
```

with zero entries outside those shifts. The empty chart is identity. The
full nine-dimensional chart is the source's special case `F_9`, independent
of how a full basis is presented.

For a transport from `A` to `B`, chronological source adjoint then
destination chart gives

```
T_BA = Gamma_B Gamma_A^dagger,
T_BA(y,x) = sum_z Gamma_B(y,z) * conjugate(Gamma_A(x,z)).
```

The adjoint must conjugate the transposed source entry. In the shift kernel
this conjugates `w_r(s)` while retaining the chart phase
`q_Q(z)-q_Q(x)` in the adjoint column. Conjugating the complete forward
column entry without transposing would use the wrong phase.

`verify.py` reconstructs these closed kernels independently. It enumerates
the completed binary coordinate map to obtain the inverse, computes the
phase polynomial, and performs exact finite Gaussian convolution. It does
not import the compiler, producer or author native checker.

## Compiled recipe interpretation and independent dense oracle

A recipe monomial with matrix `G`, offset `b`, quadratic/linear phase `q`
and global phase `phi` acts by

```
M e_x = i^[q(x)+phi] e_(Gx+b).
```

The phase is evaluated on the input address. The source recipe's chronological
order is right monomial, positive child, left monomial, hence the operator
`M_left F_r M_right`. Both checkers independently validate the monomial
permutation and phase records and compare this operator with `T_BA`.

`oracle.py` provides a separate expected-operator implementation. It builds
literal `P`, `D`, and signed `C` circuits for the source/destination charts,
uses high-to-low binary elimination for inverses, and propagates dense
Gaussian vectors through each gate. Its compiled-recipe side separately
expands the positive child and monomial factors. It imports neither the
producer/compiler nor the primary or author checker.

Both implementations agree on every entry, not merely on matrix hashes.
The hashes summarize the exact normalized columns after equality is checked.
The nonzero entry counts are respectively 1,024, 1,024, 8,192 and 16,384,
for 26,624 total. By complex linearity, equality on every standard basis
column gives equality on every vector in this finite 512-dimensional space.

The primary's phase controls add a global quarter turn and alter a right
monomial's input phase by `2*x_0`. The latter preserves the entire column
at input zero but changes column one; concrete unequal entries are retained.
Its wrong-rank control separately rejects inconsistent rank metadata.
The dense oracle changes the global phase and substitutes the inverse child
for the positive child, producing actual unequal coefficients for every task.
These comparisons occur after input authentication, so they are semantic
matrix checks rather than source-hash rejections.

## Prior coverage and the meaning of this contribution

Signed Pauli conjugations together with one exact nonzero state column
already determine a Clifford operator including global phase. The retained
author native checker uses that complete criterion. The present all-column
comparison supplies additional independently implemented, exact-source
execution evidence; it does not repair a logical omission in that criterion.
In particular, the column-zero-preserving control above is not a defect in
the predecessor's stronger signed-Pauli-plus-phase check.

The selected PR6030 [independent receipt](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/docs/research/pr-intake-evidence/pr6030-audit/independent-result.json)
records seven fresh dense tasks relative to PR5907:

```
helper: 3→189, 76→394, 749→127;
move:   3→189, 3→714, 595→637, 714→127.
```

The selected review separately reports all 2,922 primary native maps and
explicitly does not claim a fresh independent dense replay of all unchanged
predecessor maps. None of this package's four endpoint pairs is one of its
seven fresh tasks. That is a statement about exact recorded coverage, not
a claim that earlier generic native mathematics is inadequate.

The producer and primary checker also compare frame1094 with the preceding
1,094 entries of this frozen word. No identical ordered basis or equal
binary span occurs there. A new frame index alone would not establish that
fact. No cross-comparison of the four full operators against all historical
operators, including the seven selected matrices, is claimed; no global
operator-novelty or optimality conclusion depends on such a comparison.

## Remaining obligations and credit

The rational public-boundary audit is PR6355; the declared finite invoice
and fixed-saving moment audit is PR6359. Those scopes remain separate from
the present four finite matrices. This result does not replay other native
maps or main adapters, an explicitly compiled reverse helper-normalizer
instance, all tensor widths, the whole supplier, physical caller contacts,
ownership or erasure, complete nonrecursive funding, ordinary/outer
admission, uniform compilation, precision tape or analytic recovery. It
establishes no new admitted `kappa` or selected-frontier change. The five
framework assumptions `native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape`, and `analytic_recovery` remain.

Ali Romman, with substantial OpenAI Codex assistance, supplied PR6353's
construction and author native checks, on the PR6349/PR6348/PR6350 lineage.
The exact Clifford compiler, canonical native charts and Gaussian primitive
identities are retained work, not new general mathematics here. Retain the
native-channel/source lineage and complete `sources/NOTICE`, together with
DreamingOfClouds's PR6314 source, Cinna Davis's caller/interface work, and
Clear1nsight/Matarener's earlier dense-checking lineage recorded in the
selected review. The new contribution is the independent implementation,
source binding, four width-one instances and phase-sensitive controls,
prepared for ToikY with substantial OpenAI Codex assistance and separate
producer/primary, dense-oracle and mathematical-review agents. Same-session
agent review is part of the author process, not independent human or formal
acceptance.
