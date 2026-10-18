# Exact audit of one P112 asymmetric pairing

## Statement

The `d0=76` witness from `research/format-limits` C.6 satisfies the stated
decoder support identity on the full P112 port set. Its pairing matrix has
rank 9. Its eight coordinate read blocks have rank 8 each, and one shared
extra-total read block has rank 1, for copy-rank sum 65. The two altered
decoder rows have 28 nonzero off-diagonal positions each; the corresponding
coordinate rows have 52 each.

This is an independent finite replay of one supplied witness. It is not a
classification of all P112 decoders and it does not show that the unit has a
cheaper complete recursive cost.

## Definitions and witness

Let `L_i` be the 120 integer vectors generated from the extended binary
Hamming `[8,4,4]` code, in the predecessor's order: coordinate vectors
`2 e_0,...,2 e_7`, followed by the signed representatives of the 14
weight-four code supports. Set

\[
G_{ij}=\frac{L_i\cdot L_j}{2},\qquad
M_{ij}=1+G_{ij}\pmod 2.
\]

The independent checker factors `M=UU^T` over `F_2` using a nine-dimensional
orthonormal basis derived from the Gram block of greedily selected independent
rows. P112 is the ordered set `P={8,...,119}`. Every label row is represented
as a 9-bit integer with the same coordinate order as the predecessor.

For P112, let `u_s` be the generated source label and `w_t` the sink label.
Use the predecessor's exact witness:

- distinguished root vectors `e=L_0`, `d_0=L_76`;
- changed target rows `t=75,76`, with sink labels `329,438`;
- coefficients `mu_75=-1`, `mu_76=0`;
- shared extra-source set `Q`, recomputed from the paired sink labels and
  orthogonality to `e` and `d_0` (24 source lines in total).

The binary pairing and rational decoder entries are

\[
B_{ts}=\langle w_t,u_s\rangle_{F_2},
\quad N_{ts}=G_{ts}/2\quad(t\notin\{75,76\}),
\]

and, for `t` in the two changed rows,

\[
N_{ts}=L_s\cdot(d_0+\mu_t e) + \alpha_s,
\qquad
\alpha_s=\begin{cases}-L_s\cdot d_0,&s\in Q,\\0,&s\notin Q.\end{cases}
\]

All values are exact integers or rationals. The verifier checks, entry by
entry, that for every off-diagonal position `N_ts B_ts=0`, and on every
diagonal position `B_tt=1` and `N_tt != 0`. Thus the decoder has precisely the
required diagonal support on all 112-by-112 entries.

## COPY-rank calculation

The global `F_2` row rank of `B` is 9. For each coordinate `a=0,...,7`, the
coordinate read block uses rows of P112 with `L_{t,a} != 0` plus both altered
targets, and columns with `L_{s,a} != 0`; each such submatrix has rank 8.
For the shared extra total, the two changed target rows restricted to `Q` have
rank 1. The reported sum is therefore `8*8+1=65`.

The correction-support comparison counts nonzero off-diagonal `N_ts` values
in these two rows. The modified rows each have 28; their coordinate-decoder
rows each have 52. These are support counts. They are not an implementation
invoice for scalar corrections or recursive calls.

## Negative controls and limits

The verifier changes sink label `329` to `328`, and separately changes the
first altered-row coefficient from `-1` to `0`. Both mutations fail the full
diagonal-support check. These controls detect a broken witness replay; they do
not prove uniqueness or a lower bound.

The audit does not charge construction or application of the extra total,
frame changes, source access, hosting, restoration, or recursive children.
It does not rerun the predecessor's SAT searches and does not certify any
assumption in the selected multiplication construction. A complete stage
contract is required before the 48 fewer correction positions can be compared
with the extra copy-rank unit in a supplier budget.

## Reproducibility

The exact base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The predecessor
generator and E8 geometry implementation are pinned by Git blob and SHA256 in
`SOURCES.json`; the standard-library checker verifies their working hashes.
`CERTIFICATE.json` stores the exact source set, row data parameters, all rank
and support counts, and canonical SHA256 digests of the 112 pairing rows and
112 rational decoder rows. Reproduce with:

```sh
python3 -I -O -B research/p112-off-pattern-unit-audit-seed52/verify.py
```
