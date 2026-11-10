# Independent written audit of the all-even attaining word

Prepared for **ferdy252 with substantial OpenAI Codex assistance**. Apache-2.0.

This note audits Section 7 of thu-nmrc's `PROOF.md` in PR #6717 at
`3c9072b8738323dda9f9c7dfb421d578ed3fc17a`. It proves that the displayed
construction attains stage ranks `(2q,3q,2q)` and its stated complete formal
endpoint. It does not audit the universal lower bound in Sections 2–6.
The source construction and theorem remain predecessor credit. This is an
AI-assisted written derivation, not an executed checker or proof-kernel result.

## 1. Definition of the constructed word

Fix an even integer `n >= 4` and a field `K` with `char(K) != 2`.
Use zero-based coordinate indices. Let `e_j` be the standard columns and
`h=(1,...,1)` the row. Define canonical query factors by

```
u_i = e_i                      (0 <= i < n),
u_n = sum_{j=0}^{n-1} (-1)^(j+1) e_j,
(v_i)_j = sign(i-j)             (0 <= i <= n, 0 <= j < n),
R_i = u_i v_i.
```

In particular, `v_n=h`. Each `u_i,v_i` is nonzero and `v_i u_i=0`;
for the final pair this uses the alternating sum of even length `n`.
Thus every `R_i` has rank one and is square-zero.
We will construct a common integral change of basis `H` and use
`R'_i = H R_i H^{-1}`. No normal-form theorem about other tuples is needed.

## 2. The displayed H is unimodular for every even n

Pad the following four-dimensional columns with zeros:

```
c0=(1,1,0,0), c1=(1,2,1,0), c2=(1,2,2,0), t=(0,1,1,1).
```

Put `J={3,...,n-2}` and `epsilon_j=(-1)^(j+1)`. This is an empty set
when `n=4`. Otherwise it has even size `n-4`, so
`sum_{j in J} epsilon_j=0`. Write the columns of `H` explicitly as

```
H_0=c0, H_1=c1, H_2=c2,
H_j=t+e_(j+1)                              (j in J),
H_(n-1)=t-sum_{j in J} epsilon_j e_(j+1).
```

Add `sum epsilon_j H_j` to the last column. Its value becomes exactly `t`.
Subtract that new last column from each column indexed by `J`. The resulting
ordered columns are

```
c0, c1, c2, e4, e5, ..., e_(n-1), t.
```

Move the last column to position 3. This makes `n-4` transpositions, an even
number, and gives `H4 direct-sum I_(n-4)`, where

```
H4 = [[1,1,1,0],
      [1,2,2,1],
      [0,1,2,1],
      [0,0,0,1]].
```

Its determinant is `2-2+1=1` by expansion of the upper-left three-by-three
block. All preceding column additions preserve the determinant, and the
permutation has positive sign. Hence `det(H)=1` over the integers, including
`n=4`. Consequently `H^{-1}` is integral and the change of basis is valid
over every allowed field, with no dimension-dependent denominator.

## 3. Both factors of all three selected queries are exact

The first two transformed columns are `H u_0=c0` and `H u_1=c1`.
For the final column, `(-1)^n=1` and the same alternating cancellation give

```
H u_n = -c0+c1-c2 + sum_{j in J} epsilon_j H_j + H_(n-1)
      = -c0+c1-c2+t
      = (-1,0,0,1,0,...,0).
```

Checking rows against `H` avoids assuming their extra coordinates vanish.
Let the following rows be zero outside the first four coordinates:

```
w0=(1,-1,0,0), w1=(1,0,-1,0), wn=(1,0,0,1).
```

Their evaluations on `(c0,c1,c2,t)` are respectively

```
w0: (0,-1,-1,-1),
w1: (1, 0,-1,-1),
wn: (1, 1, 1, 1).
```

They vanish on all `e_(j+1)` for `j in J`. Therefore their values on every
column of `H` are exactly the corresponding entries of `v0`, `v1`, and `vn`.
Thus `w_s H=v_s` and, because `H` is invertible, `w_s=v_s H^{-1}` for
`s=0,1,n`. This verifies both factors, including every extra coordinate:

```
R'_0 = (1,1,0,0)^T (1,-1,0,0),
R'_1 = (1,2,1,0)^T (1,0,-1,0),
R'_n = (-1,0,0,1)^T (1,0,0,1),
```

with zero padding. In particular their column and row supports lie in
`{0,1}`, `{0,1,2}`, and `{0,3}`, respectively.

## 4. The canonical query endpoint is verified directly

Put `T_i=I-2R_i`, `B_i=T_i ... T_0`, and `B_(-1)=I`.
For `0 <= i < n`, define

```
a_i = sum_{j=0}^i (-1)^j e_j,
J_i = diag(-I_(i+1), I_(n-i-1)).
```

We prove `B_i=J_i+2a_i h`. The same calculation includes the initial step
by setting `a_(-1)=0`, `J_(-1)=I`. We have

```
v_i J_(i-1) = e_i^T-h,
v_i a_(i-1) = sum_{j=0}^{i-1} (-1)^j,
2 sum_{j=0}^{i-1} (-1)^j = 1-(-1)^i.
```

Therefore `v_i B_(i-1)=e_i^T-(-1)^i h`. Multiplying on the left by `T_i`
changes `J_(i-1)` to `J_i` and `a_(i-1)` to `a_i`, proving the induction.
Since `n` is even, `a=a_(n-1)` satisfies `h a=0`, `u_n=-a`, and

```
B_(n-1)=-I+2a h,
T_n=I+2a h,
B_n=(I+2a h)(-I+2a h)=-I.
```

Every `T_i` is invertible, with inverse `I+2R_i`, because `R_i^2=0`.
Conjugation by `H` preserves this complete endpoint and all prefix products:
`B'_i=H B_i H^{-1}`, so `B'_n=-I`.

## 5. The selected projectors meet the actual prefix conditions

Let `P0`, `P1`, `Pn` be coordinate projectors onto `{0,1}`, `{0,1,2}`,
and `{0,3}`. Their ranks are `(2,3,2)`; they are idempotent and commute
pairwise. The factor supports above give

```
P_s R'_s = R'_s P_s = R'_s       (s=0,1,n).
```

For site 0, this implies that `P0` commutes with `B'_0=T'_0`.
For site 1, `P1` also contains both factors of `R'_0`, so it commutes with
both `T'_0` and `T'_1`, hence with their actual chronological product
`B'_1=T'_1 T'_0`. For the last site, `B'_n=-I` commutes with every projector.
These are complete-prefix checks, not merely local-query compatibility.

## 6. Pulling the selected stages through the chronological word

Let `A,B,C` be independent commuting indeterminates, and `S` another central
indeterminate with `S^2=1`. Define

```
Q_0=I+(A-1)P0, Q_1=I+(B-1)P1, Q_n=I+(C-1)Pn,
Q_i=I for the other sites,
X_i(S)=Q_i [I+(S-1)R'_i],
W(S)=X_n(S) ... X_0(S).
```

At `S=1`, all query factors are identity, and

```
W(1)=Q_n ... Q_0=Delta,
Delta=diag(ABC,AB,B,C,1,...,1).
```

At `S=-1`, the query factors are `T'_i`. For arbitrary invertible query
factors and any inserted `Q_i`, the following identity keeps the exact order:

```
Q_n T'_n ... Q_0 T'_0
 = B'_n [B'_n^{-1} Q_n B'_n]
          [B'_(n-1)^{-1} Q_(n-1) B'_(n-1)] ...
          [B'_0^{-1} Q_0 B'_0].
```

It follows by cancelling adjacent prefixes; equivalently it is an induction
on the final site. The actual prefix commutations established above make
each bracket equal to `Q_i`. At every unselected site this also holds since
`Q_i=I`. Thus

```
W(-1)=B'_n Q_n ... Q_0=-Delta.
```

Every entry of `W(S)-S Delta` has a unique representative `x+yS` over
`K[A,B,C]` modulo `S^2-1`. Its two evaluations are zero, so `x+y=0` and
`x-y=0`. Since 2 is invertible in `K`, both coefficients vanish. Hence the
complete formal matrix identity is

```
W(S)=S diag(ABC,AB,B,C,I_(n-4)).
```

No stage variables were specialized or identified. In particular, every
extra independent input is carried to `S` times itself; it is neither set
to zero nor discarded. The identity holds on the entire input module.

## 7. Coupled width and scope

Tensor every constructed coefficient-space matrix with `I_q`, for any
integer `q>=1`. Tensoring preserves products, the full formal matrix identity,
square-zero relations, compatibility, and prefix commutation. It multiplies
the three projector ranks by `q`, yielding `(2q,3q,2q)` on exactly `nq`
independent input coordinates. This is an existence construction for each
width; no inference about arbitrary coupled tuples or their lower bounds
is made here.

The result is the all-size attaining word claimed in the source's Section 7.
It does not establish the source's universal `7q` lower bound, a physical
native realization, a complete paid invoice, a new exponent, or any of the
selected multiplication framework assumptions. Scalar attainment,
canonical-query and controller lineage retain their original attribution;
the all-even extension audited here is thu-nmrc's construction. This audit
used the proof text only and neither imported nor executed the source's
checkers. Any finite corroboration supplied elsewhere is separate evidence.

## 8. A complete endpoint can pass while compatibility fails

This audit adds a small discriminating control. At `n=6`, omit the extra
alternating correction from the last column only. The altered basis has columns

```
Htilde=(c0,c1,c2,t+e4,t+e5,t).
```

It is still unimodular: subtract its last column from columns 3 and 4,
then move the last column to position 3 using two swaps. The first two
selected query factors and their prefix conditions are unchanged, as is
the complete query endpoint `-I` by conjugation. The final factors become

```
utilde_n=(-1,0,0,1,1,-1)^T,
vtilde_n=(1,0,0,1,0,0).
```

Keep all three original diagonal stage projectors. The final prefix is
still central, so the ordered argument in Section 6 still proves the entire
formal endpoint `S diag(ABC,AB,B,C,1,1)`. Nevertheless,

```
(I-Pn) Rtilde_n = (e4-e5)(e0^T+e3^T) != 0.
```

The final stage is not compatible with its query. Thus this altered word
is outside the source theorem's hypotheses despite its correct endpoint.
It is not a counterexample to that theorem. The executable control first
accepts its complete endpoint, then requires the separate compatibility
gate to reject it. This directly distinguishes the two obligations.
