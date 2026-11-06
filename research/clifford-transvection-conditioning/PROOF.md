# A transvection certificate for three-qubit conditioning

## Statement and inherited mathematical inputs

Use the full Gaussian-dyadic three-qubit Clifford alphabet and conventions of
[alephnan's PR6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714),
at head `f7f32a18dde54e67624a9ed9cc7e1b266d9585c0`. For representatives
`U_a` of its 92,897,280 projective classes, put

\[
 H_f(a,b)=\left(\operatorname{tr}(U_a^*U_b)/8\right)^f.
\]

For every integer `f >= 10`, this package proves the sufficient bounds

\[
 \boxed{\frac{2835}{131072}I\preceq H_f
              \preceq\frac{2287845}{131072}I.}                 \tag{1}
\]

Consequently the spectral condition number is at most **807**.
The predecessor's sufficient bounds were `945/262144` and `762615/32768`,
with ratio 6,456. The lower bound in (1) is six times larger and the upper
bound is three quarters as large. No optimality for the actual spectrum is claimed.

The following are cited predecessor results, rather than claims reproved here.
They are in its [PROOF.md, Sections 2 through 7](https://github.com/CrocSwap/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md).

1. Let `V` be the natural eight-dimensional representation, and `sigma` run
   over the thirty irreducible characters of `Sp(6,2)`. The odd central-sector
   irreducibles are `V tensor sigma`. Their multiplicities in `V^(tensor 9)`
   are the nonnegative integers `m_sigma` retained in the source result.
2. If `mu` is an even-sector irreducible relevant at width ten, then

   \[
   \overline V\otimes\mu
       =\bigoplus_\sigma n_\sigma(V\otimes\sigma),\qquad n_\sigma\ge0.
   \]

   Write `d_sigma = dim sigma` and `d = dim mu`. Dimensions and reciprocity give

   \[
   d=\sum_\sigma n_\sigma d_\sigma,\qquad
   m_\mu(10)=\sum_\sigma n_\sigma m_\sigma.             \tag{2}
   \]

3. There is `N` equal to 28 or 36 and an integer `a >= 1` with `d=Na`.
   For a transvection `tau` of `Sp(6,2)`, set

   \[
    T=\sum_\sigma n_\sigma\chi_\sigma(\tau).
   \]

   Then `|T| <= 16a = 16d/N`. This follows because exactly sixteen quadratic
   forms in either Pauli-character orbit are fixed by a transvection.
   In the source's phase convention, the quotient-character sum differs from
   the character of `mu` at its Clifford lift by a scalar of absolute value one.
4. The eigenvalue on the regular matrix block of `mu` is

   \[
   \lambda_\mu(10)=\frac{92897280}{8^{10}}
                       \frac{m_\mu(10)}{d}.             \tag{3}
   \]

   Also `H_(f+1) = H_f circ H_1`, where `circ` is the Schur product,
   `H_1` is positive semidefinite, and its diagonal is one.

The exact source numerical files are retained unchanged. Their origin and hashes
are in [ORIGIN.json](ORIGIN.json). The published character table is due to
Chin-Yen Lee, Wei-Hsuan Yu, Yung-Ning Peng and Ching-Jui Lai. This proof uses
the predecessor's identification and multiplicities as inputs. It does not
reconstruct the table, audit that identification, or rerun its decomposition.

## The new finite certificate

For every one of the thirty types, write `t_sigma = chi_sigma(tau)`. The
retained data satisfy the two integer inequalities

\[
 4m_\sigma-5d_\sigma-7t_\sigma\ge0,\qquad
 1345d_\sigma+1883t_\sigma-12m_\sigma\ge0.               \tag{4}
\]

These are the new supporting lines. The verifier reads the cited width-nine
multiplicities and the transvection column, evaluates every residual in (4)
exactly, and prints all thirty pairs. This is a finite arithmetic certificate
for new inequalities in the predecessor data, rather than another verification
of its threshold or multiplicity calculation.

The source row numbers and the three tight data points explain the constants:

| source row | `d_sigma` | `t_sigma` | `m_sigma` |
| --- | ---: | ---: | ---: |
| 1 | 1 | 1 | 269 |
| 2 | 7 | -5 | 0 |
| 9 | 56 | -24 | 28 |

The lower supporting line passes through normalized rows 2 and 9. The upper
supporting line passes through normalized rows 1 and 2. Checking only these
three points would be insufficient; (4) is checked for **every** type.

Multiply (4) by the nonnegative integers `n_sigma` and sum. By (2),

\[
 \frac54d+\frac74T\le m_\mu(10)
        \le\frac{1345}{12}d+\frac{1883}{12}T.           \tag{5}
\]

Both slopes are positive. Applying `-16d/N <= T <= 16d/N` gives

\[
 \left(\frac54-\frac{28}{N}\right)d
   \le m_\mu(10)
   \le\left(\frac{1345}{12}+\frac{7532}{3N}\right)d.   \tag{6}
\]

Thus the two orbit-specific intervals for `m_mu(10)/d` are

| `N` | lower bound | upper bound |
| --- | ---: | ---: |
| 28 | 1/4 | 807/4 |
| 36 | 17/36 | 19637/108 |

The first interval contains the second. Since
`92897280/8^10 = 2835/32768`, (3) proves (1) at width ten.

For propagation, if `alpha I <= H_f <= beta I`, Schur positivity gives

\[
 (H_f-\alpha I)\circ H_1\succeq0,\qquad
 (\beta I-H_f)\circ H_1\succeq0.
\]

The unit diagonal means `I circ H_1=I`. Therefore the same interval holds at
`f+1`, proving (1) for every `f >= 10`. This is a written universal implication
from the stated representation-theoretic inputs, not a finite-width extrapolation.

## What is sharp, and what is still open

The two bounds in (6) are sharp for the following **relaxation only**. Assign
arbitrary nonnegative weights `x_sigma` summing to one, retain the thirty points

\[
 (r_\sigma,c_\sigma)=(t_\sigma/d_\sigma,m_\sigma/d_\sigma),
 \qquad \left|\sum_\sigma x_\sigma r_\sigma\right|\le16/N,
\]

and minimize or maximize `sum x_sigma c_sigma`. The following explicit mixtures
attain all four bounds; weights refer to the indicated source rows.

| `N` | extremum | nonzero weights |
| --- | --- | --- |
| 28 | minimum | row 2: 1/2; row 9: 1/2 |
| 28 | maximum | row 1: 3/4; row 2: 1/4 |
| 36 | minimum | row 2: 1/18; row 9: 17/18 |
| 36 | maximum | row 1: 73/108; row 2: 35/108 |

Together with (4), these mixtures prove the relaxed optimum, including its
orientation at the two ends of the trace interval. The independent primal route
in the verifier lists every simplex vertex in the trace slab and every intersection
of a simplex edge with its two bounding hyperplanes. These cover the vertices:
at a vertex, at most two weights can be positive since there is the sum constraint
and at most one active trace constraint. If two trace coordinates coincide, a
nontrivial edge interior is not a vertex. All arithmetic is rational.

The relaxation discards additional representation and multiplicity constraints.
Its attaining mixtures are not claimed to come from any actual irreducible `mu`.
In particular **807 is a sufficient uniform bound, not the exact condition
number**, and neither endpoint is claimed to be an actual eigenvalue.

## Scope

This is a scoped native-algebra conditioning theorem with exact finite
corroboration. It does not improve the already proved threshold ten. It supplies
no new paid-call construction, recursive invoice, physical implementation,
selected supplier admission or multiplication exponent. All five selected
framework assumptions retain their status. Independent human and formal
proof-kernel review are unclaimed.
