# P104 decoder: exact nine-row and rank-field controls

## Scope and attribution

The data are from CrocSwap/integer-mult-bounds PR #7852 at exact commit
`41beda1d6435760dc99e38bd7e65f36798aad212`, file
`research/p104-lowerbound-toolkit/lean/Nov15/DecoderWall4Data.lean`, Git blob
`90949f8d5dbcdee99974de505018768f4f9f640e` (SHA-256
`081bf16ed5e19930082ffb58548c6e6cded5c100f15332e797695e0cd07ef8c4`).
The source file is copied intact here; `data.json` extracts only `labs` and
`gramRows`. `control.py` verifies the complete Git blob hash, verifies the
extracted arrays match the source, and independently verifies each finite
identity below. The signed Gram entries use the decoding rule in the pinned
`DecoderWall4Defs.lean`, `((gramRows[i] >> 2j) & 3) - 1`. The 8-frame indexes
are the `F0` frame in `DecoderWall6.lean` and `DF.clique8` in `DecoderFacts.lean`.
The construction and computations below are an independent challenge to a
possible extension, not a claimed correction of those upstream theorems.

The #7852 source proves rigidity and an associated row-span bound for **exactly
eight** decoder rows; its README leaves broader general-decoder bounds open.
This control shows why that row-by-row conclusion cannot be copied to nine
rows without an extra hypothesis. It is not a counterexample to the source's
eight-row result, `Wall56`, `NetD56`, a legal word, or a kappa result. The
constructed object is a decoder, and no network or legal-word realization is
asserted.

## Exact construction

Index the 104 ports from zero. Let `q[i]` be their nine-bit labels, let
`Q[i,j] = parity(q[i] & q[j])`, and let `G` be the pinned signed integer
Gram. With frame

```
F = [0, 6, 16, 22, 29, 36, 45, 95],
A[i,k] = G[i,F[k]],       x_k = A[:,k]/2.
```

The verifier checks every identity below by integer arithmetic:

- `G[F,F] = 2 I_8` and `A A^T = 2 G`.
- `G[i,i] = 2` and `G[i,j] = 0` whenever `i != j` and `Q[i,j] = 1`.
- Thus `sum_{k=0}^7 x_k x_k^T = G/2` is a rational decoder: its diagonal
  entries are one and its live off-diagonal entries are zero.

Choose `p = 103`, which is outside `F`, and put `e = e_p`. Replace the first
eight decoder terms `(w_k,u_k)=(x_k,x_k)` with

```
(w_0,u_0) = (x_0 + e, x_0)
(w_1,u_1) = (x_1 + e, x_1)
(w_k,u_k) = (x_k, x_k)            for 2 <= k < 8
(w_8,u_8) = (e, -x_0 - x_1)
```

The net extra contribution is
`e x_0^T + e x_1^T - e (x_0+x_1)^T = 0`, so the **entire** decoder
completion is unchanged, not merely its constrained entries. Every factor
has half-integer entries. The checker separately verifies each factor is
nonzero and no two left factors, or two right factors, are proportional. The
terms can still be jointly recoupled back to eight rows; this example only
excludes a direct row-by-row nine-row extension, including an extension
that merely rules out zero rows and pairwise proportional merges.

The added row's left/deposit support is exactly `{103}`. Its label is the
nonzero 9-bit integer 290, so its label-span dimension is one. Its complement
contains `F`, whose `G` block is `2 I_8`, and therefore the complement's
signed-Gram rank is at least eight. This explicitly contradicts the
`RigidSet` consequence used in the eight-row proof if one omits the
exactly-eight hypothesis.

The true decoder row price is the rank over `F_2` of `Q[D_k,S_k]`, where
`D_k`, `S_k` are the exact nonzero supports of the left and right factors.
Exhaustive binary Gaussian elimination gives

```
8 rows: [9, 9, 9, 9, 9, 9, 9, 9]       total 72
9 rows: [9, 9, 9, 9, 9, 9, 9, 9, 1]    total 73
```

Hence the example stays above 56. It does not disprove a nine-row cost wall.

## Same support, three different ranks

For the first original row, `D_0 = S_0 = {i : G[i,0] != 0}`, a set of 49
ports. On that same 49-by-49 support the checker computes exactly:

| Matrix | Field | Rank |
|---|---|---:|
| signed integer Gram `G[D_0,D_0]` | rationals | 8 |
| binary label-pairing matrix `Q[D_0,D_0]`, viewed as an integer 0/1 matrix | rationals | 29 |
| that 0/1 label-pairing matrix | `F_2` | 9 |

The rational ranks use exact `Fraction` elimination; the actual decoder price
uses independent bitwise elimination over `F_2`. For this integer 0/1 matrix,
mod-2 rank is in general at most rational rank, because an odd determinant of
any mod-2 nonsingular minor is nonzero over the rationals. Equality need not
hold, as the displayed 9-versus-29 calculation shows. The signed Gram matrix is
a **different** matrix, so one must also justify any comparison to it; this
example is already 8 versus 9. These finite values are not themselves a
universal lower bound.

## Replay and negative control

Run using Python 3.10 or newer, with no external package:

```
python3 -I -B research/p104-nine-row-decoder-rigidity/control.py
```

All results are asserted before being printed. The script additionally
reverses the sign of the ninth right factor. This changes 40 constrained
entries and the first violated off-diagonal live cell is `(103,0)`, whose
incorrect value is `8/4 = 2`. Thus a missing or reversed cancellation is
caught. The pinned blob is also rehashed, and the extracted arrays are checked
against it on every run.

## Open next questions

Can a change of basis remove a dependent term without increasing the
pairing-rank price? Start with the displayed three-term cancellation and
check two-sided support changes around its circuit. A proof of
support-preserving recoupling is needed to use eight-row rigidity.

Credit DreamingOfClouds for the P104 toolkit, its decoder model and the
pinned E8 data. Clear1nsight prepared the extension test with substantial
OpenAI Codex assistance. The copied source retains its Apache-2.0 notice.
