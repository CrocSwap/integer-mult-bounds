# Exact minimum for a mixed S4 double-transposition target

## Formal model

Let (S_4) act on (mathbb F_2^4) by permutation matrices. Put

\[
s_1=(12),\quad s_2=(23),\quad s_3=(34),\qquad
p=(13)(24),\quad q=(12)(34).
\]

The target on three arbitrary dirty scalar roles is

\[
T=\operatorname{diag}([p],[q],[e])\in M_3(\mathbb F_2[S_4]).
\]

A paid call is

\[
D_N([s_i])=I+([s_i]+[e])N,
\]

where (N=xy^T\in M_3(\mathbb F_2)), (x,y\ne0), and (y^Tx=1). There
are (7\cdot4=28) such rank-one idempotents and 84 paid factors. Every call
costs one. Arbitrary interleaved free scalar (GL_3(\mathbb F_2)) changes
are included by moving them to the end and conjugating each (N); augmentation
maps every paid factor to (I), so the final scalar map must be (I) for this
endpoint. The resulting normalized alphabet is exactly the 84 factors above.

No address operation outside the three paid adjacent transpositions, clean
inputs, extra roles, hosting, frame changes, restoration wrappers or supplier
conversions are present in this finite model.

## Cost screen and direct word

The adjacent-transposition lengths are \(\ell(p)=4\) and \(\ell(q)=2\), so
the direct bill is six calls. In the full rank-one-displacement alphabet of
PR #1333, each target has displacement rank two and the exact paid-rank floor
for this target is (2+2=4). Thus a four-call word is the optimistic saving
candidate; every one of its four calls would still be fully charged.

An attaining six-call word is

```text
D_E00(s2), D_E00(s1), D_E00(s3), D_E00(s2), D_E11(s1), D_E11(s3)
```

The first four factors multiply to ([p]) on role 0; the final two multiply
to ([q]) on role 1. Role 2 remains exactly the identity. Both the C++ and
Python implementations replay equality in every coefficient of the formal
group algebra.

## Lower bound below six

Any coefficient in a product of (k) calls is the ordered product of a
subsequence of the (k) adjacent-transposition labels: each factor expands as
\(I+[s_i]N+[e]N\). Since the target has a nonzero ([p]) coefficient and
\(\ell(p)=4\), no word with (k<4) can reach the endpoint.

For parity, map (S_4\) to (C_2=\{1,t\}) by the sign character and extend
linearly to group algebras over \(\mathbb F_2\). Each adjacent transposition
maps to (t), so a paid factor maps to (I+(t+1)N). A rank-one idempotent is
conjugate over \(\mathbb F_2\) to \(\operatorname{diag}(1,0,0)\); therefore

\[
\det(I+(t+1)N)=t.
\]

The target (p,q,e) consists of even permutations, so its determinant after
this quotient is 1. A word of length (k) has determinant (t^k); equality
requires (t^k=1) in \(\mathbb F_2[C_2]\), hence (k) is even. Below six,
the only remaining possible length is four.

The complete exact four-call meet finds no word. All 84 factors are formed as
24-bit coefficient masks in each of nine matrix entries. The verifier stores
all 7,056 ordered pair products (A=F_1F_2) and indexes the 4,698 distinct
states. For each ordered suffix pair (F_3,F_4), every factor is an
involution, so

\[
A F_3F_4=T\quad\Longleftrightarrow\quad
A=T(F_4F_3).
\]

It checks all 7,056 ordered inverse-suffix pair words against the complete
prefix index. There are no hits for (T). Therefore lengths 0 through 5 are
excluded; the six-call word proves the exact minimum is six.

The pair-state digest, exact counts, and hit receipts are in `RESULT.json`.
The C++ implementation exhausts the full domain, and `verify.py` independently
rebuilds the group law, idempotents, factors and pair meet in Python before
cross-checking the native replay.

## Controls and scope

The positive control \(\operatorname{diag}([q],[q],[e])\) has the
four-call word

```text
D_E00(s3), D_E11(s3), D_E11(s1), D_E00(s1)
```

which is found and replayed by both implementations. The negative
control \(\operatorname{diag}([p],[p],[e])\) has no four-call word. The mixed
six-call direct word is a separate positive control.

This is an exact result for one target and one restricted alphabet. It does
not determine costs for other S4 tuples or for other transposition sets. No
operation is mapped into the selected rational-frame supplier, so the result
changes no paid profile or \(\kappa\).
