# A common gauge for affine port labels

This note gives a component identity. It does not give a cheaper complete
terminal decoder.

Let the payload address space be F_2^n. Put

```text
X_a |x> = |x+a>,
S_b |x> = i^(b.x) |x>,
C_a = ((1+i)I + (1-i)X_a)/2.
```

Let A have independent columns a_1,...,a_k. Choose columns b_1,...,b_k
of B such that B^T A=I_k. Define

```text
W_i = S_(b_i) C_(a_i) S_(b_i),
W = product_i W_i.
```

The factors W_i commute. For i different from j, the required identity
is b_i.a_j=0; all diagonal factors commute with one another, and all
translation functions commute with one another. No condition on A^T A,
B^T B, or the offset label is required.

For any q, set t=B^T q and c=q+A t. Direct Pauli conjugation gives

```text
W X_q W^-1 = X_c Z_(B t),       B^T c=0.                 (1)
```

For one factor, the two cases are

```text
b.q=0:  W(a,b) X_q W(a,b)^-1 = X_q,
b.q=1:  W(a,b) X_q W(a,b)^-1 = X_(q+a) Z_b.
```

These equations fix the phase, not only the symplectic map. The second
case has no scalar factor. Applying the commuting factors proves (1).

Now let q range over one affine space q_ref+ran(A). The vector c in (1)
is the same for every q. For two labels q and r, write
t=B^T q, u=B^T r, and e=(t+u).B^T x. Then

```text
W C_q C_r^-1 W^-1 |x>
  = |x>,                                  if e=0,
  = -i (-1)^(t.B^T x) |x+c>,              if e=1.       (2)
```

To prove (2), put P=X_c Z_(B t) and R=X_c Z_(B u).
On the indicated address sector, R=(-1)^e P. If e=0, the two
quarter-turn factors cancel. If e=1, their product is -i P.
Since B^T c=0, the translation preserves the sector and its phase.
Thus (2) is an invertible address map with a quadratic phase.

For tensor width f, apply (2) to each address column. The total phase
is the product of the displayed column phases. The same finite address
map acts on every column. This proves the identity for arbitrary inputs
and every width. It does not replace all column sectors by one sector
of the simultaneous translation.

## Native rank and a restricted minimum

The X-from-Z block of W is A A^T and has rank k. Thus W has Fourier
rank k. A native rank-k child with monomial boundary maps can implement
this gauge, subject to the actual child contract and the map cost.

There is a matching minimum in the following restricted family.
Require one Clifford gauge V, identical on every field in a connected
port component, to make every nonzero edge quotient C_q C_r^-1
monomial. Write M for the X-from-X block of V and N for its
X-from-Z block.

The two conjugated translation Paulis commute. Their quarter-turn
product has X-from-Z block

```text
(M q)(M q)^T + (M r)(M r)^T.
```

It is zero exactly when Mq=Mr. Therefore M kills every edge difference.
If these differences span a k-dimensional space U, then
dim ker(M) is at least k. The symplectic identity
M D^T + N C^T=I gives rank(N) at least dim ker(M).
Consequently every such common gauge has Fourier rank at least k.

For the six actual eight-port components in the pinned geometry,
k=3. Encoding and decoding all eight independent fields with this
common gauge costs 48 units of native rank per component. The direct
two-line mass is 16 per component. This common-gauge construction alone
therefore gives no terminal saving.

This minimum does not cover coupled field gauges, interleaved native
operations, a changed response, a changed controller, or fusion with
productive native work. It is not a lower bound for the full terminal.

## Source and scope

The exact port lists and labels come from
`controller-followthrough-20261017/matching-geometry-20261018/GEOMETRY.json`,
SHA256
`21e14a24dbe8776038e4deea3181509d23c43fa9314776c4c14c90a5180573fd`.
The checker uses the actual six components and also checks a rank-four
space whose offset need not be perpendicular to that space.

No stage route, full-cover scalar pass, child host, terminal cost, or
kappa improvement is inferred. No PR, commit, or push was made.
Before a future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
