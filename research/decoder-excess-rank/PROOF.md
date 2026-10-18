# A sharp excess-rank budget for exact overcomplete decoders

This is a self-contained application of elementary rank inequalities. It extends
the search interface of joaqcoo's [PR1224, Theorem A and Corollary B](https://github.com/CrocSwap/integer-mult-bounds/blob/00e6ed0810b8ebc7f6133e2c036d0f1c9a3a4162/research/nine-term-decoder-normal-form-seed42/PROOF.md).
The general projection equations and the nine-term dichotomy belong to that
predecessor. The result here is the sharp feasible region for residual ranks,
its ten-term consequence, and the real/complex symmetric distinction. No
novelty is claimed for Sylvester's rank inequality or isotropic cancellation.

## 1. Model and ranks

Let `R` be any real `n × 8` matrix of rank eight, and let `F` be `R` or `C`.
For E8, its rows are the live true roots. All transposes below are ordinary
transposes, including over `C`. An exact `m`-term all-pairs decoder satisfies

```text
D T^T = 2 R R^T,                 D,T in F^(n × m).
```

Write `C = col_F(R)`. The real positive-definite matrix `R^T R` is invertible
over either field. Define

```text
L = (R^T R)^(-1) R^T,            P = I - R L,
A = L D,  B = L T,               N = P D,  M = P T,
s = rank_F(N),                   t = rank_F(M).
```

Thus `D=RA+N`, `T=RB+M`, and `R^T N=R^T M=0`. The numbers `s,t` measure
rank outside the root code. They are **not** term support sizes, binary copy
ranks, recursive child ranks, or operation counts.

Applying `L` and `P` on the two sides of the decoder identity gives precisely
PR1224's equations

```text
A B^T = 2I,   N B^T = 0,   A M^T = 0,   N M^T = 0.       (1)
```

Conversely, expanding the product shows that (1), together with the stated
decomposition, implies exactness. These equations are re-derived here, not
assumed from the open PR.

## 2. The sharp residual-rank region

**Theorem.** Every such decoder satisfies

```text
rank(D) = 8+s,    rank(T) = 8+t,
0 <= s,t <= n-8,  s+t <= m-8.                            (2)
```

Conversely, for this same `R`, every integer pair satisfying (2) occurs in an
exact real decoder with `m` terms, with both columns of **every** term nonzero.
For rational `R`, the attaining decoder can be rational.

**Necessity.** Because `R^T R` is invertible, `col(2RR^T)=C`. Exactness and its
transpose imply `C` is a subspace of both `col(D)` and `col(T)`. Restricted to
`col(D)`, the kernel of `P` is therefore exactly `C`; its image is `col(N)`.
Rank-nullity gives `rank(D)=8+s`. The argument for `T` is identical. The
image of `P` has dimension `n-8`, proving the two individual upper bounds.

For completeness, apply `D:F^m -> F^n` to `im(T^T)`. Its kernel on that
subspace has dimension at most `dim ker(D)=m-rank(D)`. Hence

```text
8 = rank(DT^T) >= rank(T) - (m-rank(D)) = 16+s+t-m.
```

This is Sylvester's rank inequality and proves the sum bound. It makes no
positivity assumption about `D,T`, and so remains valid over `C`.

**Attainment, including active terms.** Put `q=m-8`. Choose real matrices
`U` and `V` with respectively `s` and `t` independent columns in `ker(R^T)`.
Their column spaces need not be disjoint. Let `H` be the block diagonal matrix
of four copies of `[[1,1],[1,-1]]`; thus `HH^T=2I`. With block widths
`8,s,t,q-s-t`, set

```text
D0 = [ RH | U | 0 | 0 ],
T0 = [ RH | 0 | V | 0 ].
```

Their product is `2RR^T`, and their residual ranks are `s,t`. Some terms may
be inactive at this intermediate step. Let `J=11^T` be the `m × m` all-ones
matrix. The rational invertible matrix

```text
C0 = I+J,             C0^(-1) = I-J/(m+1)
```

gives `D=D0 C0` and `T=T0 C0^(-T)`. The decoder product and both residual
ranks are unchanged. Every column is now nonzero: its projection onto the
root code has coefficient, before multiplication by the invertible `H`,
either `e_k+1_8` or `1_8` for `D`, and either
`e_k-1_8/(m+1)` or `-1_8/(m+1)` for `T`. These vectors are all nonzero.
This proves sharpness, including when `s=0`, `t=0`, or there are unused
auxiliary slots. A rational nullspace basis suffices when `R` is rational.

## 3. Complete two-sided ten-term residual form

Suppose `m=10` and both factors leave `C`, so `s,t>0`. Then (2) forces
`s=t=1`, and `rank(D)=rank(T)=9`. Factoring the two rank-one residuals gives

```text
D = RA + u z^T,       T = RB + v w^T,                    (3)
```

where `u,v` are nonzero vectors in `ker(R^T)` and `z,w` are nonzero vectors
in `F^10`. Equation (1) becomes

```text
AB^T=2I,             Bz=0,           Aw=0,          z^T w=0.    (4)
```

These conditions are both necessary and sufficient. To see necessity, use
the nonzero vectors `u,v` to cancel the outer factors in (1). For sufficiency,
expand (3); all three residual terms vanish by (4). Since `u z^T` and
`v w^T` are nonzero and outside `C`, the two residual ranks are exactly one.
Thus (3)-(4) parameterize **all** two-sided ten-term all-pairs decoders in
their original term coordinates; this is not restricted to coordinate
readers, character gates or rational coefficients.

This also recovers PR1224's nine-term dichotomy: at `m=9`, two positive
residual ranks cannot fit. No eight-term copy-cost result is needed for
either rank conclusion.

## 4. Symmetric factors: real positivity has a precise boundary

Now impose `D=T`, still using ordinary transpose. Then `N=M` and (2) gives

```text
2 rank(N) <= m-8.                                      (5)
```

Over the reals, (1) gives `NN^T=0`. Every diagonal entry is a sum of real
squares, so `N=0`, regardless of `m`. Thus **every real symmetric exact
decoder stays in the root code**.

Over the complex numbers the diagonal argument is invalid. For any
`0 <= s <= min(n-8, floor((m-8)/2))`, choose a real rank-`s` matrix `U` in
`ker(R^T)` and form

```text
D0 = [ RH | U | iU | 0 ].
```

Then `D0 D0^T=2RR^T`, because `UU^T+(iU)(iU)^T=0`. Its residual rank is
`s`. If necessary, make every term active by right multiplying by the real
Householder matrix `O=I-2J/m`. Since `OO^T=I`, symmetry and exactness remain.
The root-code coefficients of its columns are
`H(e_k-2*1_8/m)` or `-2H1_8/m`, all nonzero in dimension eight.
Consequently (5) is sharp with every term active, for each fixed `R`.

The first symmetric complex escape is at ten terms and has residual rank
one. A Hermitian identity `DD*=2RR^T` would force the residual to zero even
over `C`; it is a different decoder model.

## 5. Identity-preserving gauges do not preserve the copy bill

Sections 2 and 4 use term gauges to establish feasibility of ranks. They do
**not** normalize a copy-cost minimization. The cost is a sum of binary
pairing ranks of the individual term supports, which gauges can change.

The checker constructs P112 by removing the eight root lines given by `H`
from the full 120-line E8 model. It chooses a nonzero projected coordinate
`u=P e_j` and checks every entry of the ten-term symmetric identity

```text
D = [ RH | u | iu ].
```

It records all ten support costs before and after the orthogonal gauge
`I-J/5`: `(8,8,8,8,8,8,8,8,9,9)` totals 82, whereas the transformed
vector is `(9,9,9,9,9,9,9,9,9,9)`, totaling 90. Both products are identical. Both
compensation terms must be charged even though their scalar matrices cancel.
This is a failure control against an invalid cost-preserving-gauge inference,
not a cheaper decoder or a copy-cost lower bound. PR1197 already supplies a
different gauge-cost counterexample in its fixed-reader setting.

## 6. Evidence and scope

`verify.py` constructs every feasible pair `(s,t)` for `m=8..14` on P112 and
P120: 168 real examples. It also constructs every feasible symmetric complex
residual rank in those term counts: 32 examples. Every term is active. Each
example is checked entrywise after denominator clearing. Residual and factor
ranks are computed by Gaussian-rational elimination and independently by
integer elimination of the realified matrix. Four ten-term examples also
reconstruct (3)-(4). Finite tests exercise the formulas and their failure
modes; Sections 1-4 are the universal proof, covering arbitrary `m` and
arbitrary complex coefficients.

The theorem only assumes a full-rank real root matrix; it needs neither a
classification of E8 flats nor a finite puncture threshold. The two named
punctures are fixtures, not exhaustive geometric domains. Rank-deficient
live root sets would require restating the rank-eight model.

Masked/E-graph-only identities, copied-rank optimality, physical frame paths,
source access, helper restoration, hosting, precision/tape, recursive moments,
supplier admission and the outer multiplication reduction are outside this
result. There is no new kappa and no Lean or human-review claim.

Prepared by Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
