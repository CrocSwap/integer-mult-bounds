# Four idle positions cannot exchange rank across the fixed schedule

This is a scoped mathematical proof under the inherited completed-call
contract, with a finite source check. It is not a proof-assistant verification
or an audit of the native implementation of that contract.

## Statement and assumptions

Fix one replica, one port, and cover identity in the pinned data schedule.
Number its streams `(X0,Y0,X1,Y1,X2,Y2,X3,Y3)` by `0,...,7`.
Allow simultaneous replacements of idle children **8, 10, 12, 13** only.
At each position, both the original and replacement child have a linearly
independent axis set in `F_2^m`, followed by an optional address translation.
An orthonormal axis set, as required by the source construction, is sufficient.

Assume:

1. A completed child with axes `A` and translation `t` acts on its one physical
   stream as the product of the `C_v` for `v in A`, followed by `X_t`, in the
   source convention below. The number of independent axes is its rank.
2. Every operation outside the four positions is fixed. The completed local
   data calls are the source F/B shears conjugated by diagonal Fourier frames;
   completed hosted-helper actions on this replica/port are nonzero diagonal
   multipliers. They keep the character fixed. In particular, a replacement
   cannot silently alter a hosted helper, its frame, or its scheduling.
3. The unchanged prefix, intervening operator and suffix are invertible on
   arbitrary inputs to the eight streams. Equality means equality of these
   physical operators, not equality on a proper subspace of inputs.

**Theorem.** If the replacements preserve the physical operator for every
Fourier character at cover identity, then each child separately preserves
its Fourier phase function and its rank. In particular, arbitrary matched
swaps, cycles and simultaneous changes confined to these four positions
cannot change any of their individual ranks.

There is no assumption that different children's axis sets are orthogonal,
that the combined multiset of axes is retained, or that only a few axes move.
Preserving the operator over every cover implies preserving it at cover
identity, so this necessary condition suffices to rule out a rank change.
No claim that cover identity alone suffices for full admission is needed.

## 1. The schedule separates the two phase positions

All event indices below are zero-based. `verify.py` derives them from
`TEMPLATE.json.gz` and checks the physical child mappings against `PLAN.json.gz`.
The exact input pins are in [SOURCES.json](SOURCES.json).

| Event | Operation | Streams mixed |
|---|---|---|
| 14 | idle children 8, 10 on pair 3 | diagonal on 6, 7 |
| 15 | bridge, pair 2 receiving from pair 3 | 4, 5, 6, 7 |
| 16 | local stage 6 on pair 2 | 4, 5 |
| 17 | idle children 9, 11 on pair 3 | diagonal |
| 18 | inverse bridge, pairs 2 and 3 | 4, 5, 6, 7 |
| 19 | local stage 7 on pair 3 | 6, 7 |
| 20 | local stage 8 on pair 3 | 6, 7 |
| 21 | idle children 12, 13 on pair 0 | diagonal on 0, 1 |

For a fixed character `u`, write `M(u)` for everything strictly between events
14 and 21, including any interleaved completed hosted-helper phases. Put
`V = span(e_0,e_1)`. Every listed factor preserves `V`; so does every diagonal
frame or helper factor allowed by the contract. The factors are invertible:
F/B and bridges are elementary shears and the diagonal factors are nonzero.
Consequently `M` is invertible and `M(V)=V`. Neither the values of its phases
nor the actual hosted occupancy are needed for this fact.

Write the original interval as `D_B M D_A`, where `D_A` acts only on streams
6, 7, and `D_B` only on streams 0, 1. Primes denote the replacement factors.
Cancel the unchanged invertible prefix and suffix from physical equality.
Then multiply on the left by `D_B^(-1)` and on the right by `D_A^(-1)`:

```
D'_B M D'_A = D_B M D_A
E_B M E_A = M,
E_B = D_B^(-1) D'_B,   E_A = D'_A D_A^(-1).
```

For every `v in V`, `E_A v = v`, so `E_B M v = M v`. Since `M(V)=V`,
`E_B` is identity on `V`. It is identity off `V` by its support, hence
`E_B=I`. Invertibility of `M` then gives `E_A=I`. The four diagonal entries
are individual child multipliers, so **each of the four phases is unchanged**.
Apply the same argument separately at every `u`.

This strengthens the single-stream interval argument in Nick Petalas's
[PR #3187](https://github.com/CrocSwap/integer-mult-bounds/pull/3187), following
Gareth Davidson's physical-stream obstruction in
[PR #1387](https://github.com/CrocSwap/integer-mult-bounds/pull/1387).
The two-coordinate invariant subspace makes the argument simultaneous and
removes the need to isolate one moved axis by choosing a character.

## 2. Polarization recovers rank from a child's phase

In the source convention,

```
X_v f(x) = f(x+v),
C_v = ((1+i) I + (1-i) X_v)/2.
```

For `chi_u(x)=(-1)^(u dot x)`, the multiplier of `C_v` is
`i^(u dot v mod 2)`, and that of `X_t` is `(-1)^(u dot t mod 2)`.
Thus a child has multiplier `i^q(u)`, where

```
q_A,t(u) = sum_{v in A} (u dot v mod 2) + 2(u dot t mod 2)  (mod 4).
```

For bits `a,b`, `a+b-(a xor b)=2ab`. Therefore the even residue
`q(u)+q(w)-q(u+w)` can be divided by two as a map from `{0,2}` in `Z/4`
to `F_2`, giving

```
B_q(u,w) = (q(u)+q(w)-q(u+w))/2
         = sum_{v in A} (u dot v)(w dot v)
         = u^T P_A w                 (over F_2),
P_A = sum_{v in A} v v^T.
```

The translation term disappears: its contribution before reduction is
`4(u dot t)(w dot t)`. Let `R` be the `r by m` binary matrix with the axes
as rows. Then `P_A=R^T R`. Because the rows are independent, `R:F_2^m -> F_2^r`
is surjective and `R^T:F_2^r -> F_2^m` is injective. The image of `R^T R`
is exactly the image of `R^T`, which has dimension `r`. Hence

```
rank_F2(P_A) = r = |A|.
```

Equal phase functions have equal polar forms. If both axis sets are
independent, their ranks are therefore equal, even if their translations
and their bases differ. Combining this with section 1 proves the theorem.
Notice that this rank argument does not require a nondegenerate restriction
of the dot product to the axis span.

## 3. An exact, small representation of phase equality

Expanding a binary parity modulo four gives

```
q(u) = sum_j d_j u_j + 2 sum_{j<k} (P_A)_{jk} u_j u_k  (mod 4),
d_j = sum_{v in A} v_j + 2t_j  (mod 4).
```

Terms of degree three or more have coefficients divisible by four.
Consequently a complete phase signature consists of the linear residues
`d_j` and the off-diagonal binary coefficients of `P_A`. The diagonal of
`P_A` is redundant, equal to `d_j mod 2`, but is retained for rank computation.
Equivalently the phase is determined by `q(e_j)` and `q(e_j+e_k)` for `j<k`.
At `m=73` these are **2,701 nonzero character values**, rather than `2^73`.
The checker computes the coefficients directly; it does not enumerate the
large character domain. This is a representation of one child's phase,
not a 2,701-probe completeness theorem for an arbitrary eight-stream circuit.

## 4. Application, coverage and boundaries

The pinned phase catalogue contains 112 ports. At each port the four **full
recipe** axis sets at positions 8, 10, 12, 13 are orthonormal and rank 48.
`verify.py` checks all 448 sets and their polar ranks. Where these four
children are unhosted, the theorem rules out the target `[51,51,51,39]`,
as well as every other change of those four ranks, with the rest fixed.
For a hosted instance the same theorem preserves the original residual rank
at each position; the full-recipe rank 48 must not be substituted for it.

This package does **not** reconstruct the T740 fill or certify that these
four positions are unhosted at every replica/port. The current literal
unhosted witness and its hosting chronology were checked in #3187; #3196
extends the occupancy-bound paired census over all 112 ports of replica zero.
Our source check authenticates the common template, plan and full phase
catalogue. Their completed helper semantics remain an inherited assumption.

The proof is not a general barrier to better suppliers. It excludes rank
redistribution at exactly four fixed positions. Other positions, changed
intervening interactions, changed child semantics or a different input/output
contract require a new argument. It does not audit native words, the all-size
compiler, precision, tape recovery, or outer analytic assumptions. It gives
no new kappa and does not assert full correctness of the baseline supplier.

The verifier includes controls demonstrating these limits:

- In dimension six, standard axes and the six vectors `63 xor (1<<j)` are
  different orthonormal bases with the **same phase**. Rank rigidity does
  not imply basis uniqueness.
- In dimension four, standard axes and `15 xor (1<<j)` have equal polar
  matrices but different phases (`u=1` is a witness). Translation 15 repairs
  the difference. A polar matrix alone is insufficient for phase equality.
- Four copies of axis 1 have zero phase. Without independence, the number
  of axes is not recovered by polar rank.
- If `M` swaps streams 0 and 6, the phase changes `(3,0,1,0)` satisfy
  `E_B M E_A=M`. This violates the invariant-subspace hypothesis and admits
  a transfer. A singular zero `M` also accepts nontrivial changes, showing
  why cancellation needs invertibility.

The finite checks are independent arithmetic controls and source-hypothesis
checks, not the logical justification for the unrestricted theorem. That
justification is the argument in sections 1 and 2.

Tekalign (@tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.
