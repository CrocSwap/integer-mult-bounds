# The sharp first-extension threshold

Let K=F_q, where q is any prime power. Fix n >= 1 and matrices A,B in M_n(K).
The pencil is **regular** when

```text
D(x,y) = det(xA+yB)
```

is not the zero polynomial. A projective slice [a:b] over an extension L/K is
invertible when D(a,b) != 0. Define e(A,B) to be the least positive integer e
with an invertible slice in P1(F_(q^e)). All fields may be embedded in a fixed
algebraic closure of K; the answer is independent of the embeddings.

Write I_q(k) for the number of monic irreducible polynomials of degree k in
K[t]. Define U_q(0)=0 and, for d >= 1, define

```text
U_q(d) = 1 + sum(k=1..d) k I_q(k).
```

## 1. Count the points seen through degree d

An algebraic element alpha over K belongs to F_(q^e) exactly when its degree
k over K divides e. This is the finite-field Frobenius theorem. Equivalently,
t^(q^e)-t is the product, once each, of every monic irreducible polynomial
whose degree divides e. Its derivative is -1, so all its roots are simple.
Counting roots gives

```text
q^e = sum(k | e) k I_q(k).
```

Integer Mobius inversion gives the closed formula

```text
I_q(k) = (1/k) sum(r | k) mu(r) q^(k/r).
```

The finite points in the union of F_(q^e), 1 <= e <= d, are precisely the
elements of algebraic degrees 1 through d. Every degree-k element is included
at e=k, and an element included at e<=d has degree dividing e, hence at most d.
Different irreducibles have disjoint root sets, each with exactly k roots.
Adding the common point at infinity gives exactly U_q(d) distinct projective
points. This counts the union, not the sum of the individual field sizes.

## 2. Sharp minimum dimension for simultaneous failure

For d >= 1 let

```text
P_d(t) = product of every monic irreducible p(t) with 1 <= deg p <= d,
S_d = deg P_d = U_q(d)-1.
```

Suppose every slice of the regular pencil is singular over each of the
extensions of degrees 1 through d. Set f(t)=D(t,1), a nonzero polynomial.
All roots of P_d are roots of f. Since P_d has simple roots, P_d divides f.
The infinity slice [1:0] is also singular. Thus the coefficient of t^n in f
vanishes, so deg f <= n-1. Therefore

```text
U_q(d)-1 = deg P_d <= deg f <= n-1,
so n >= U_q(d).
```

Conversely suppose n >= U_q(d). For a monic degree-k polynomial p, write
p_h(x,y)=y^k p(x/y). Choose the nonzero homogeneous polynomial

```text
D_d,n(x,y) = y^(n-S_d) product(deg p <= d) p_h(x,y).
```

It has degree n and vanishes on all the projective points just counted.
The exponent of y is positive, so infinity is included. Section 3 realizes
this polynomial as the determinant of a regular n-by-n pencil. Consequently
U_q(d) is exactly the minimum regular-pencil dimension for simultaneous failure
in every extension degree through d.

## 3. Literal attaining pencils

For a monic polynomial p of degree k, let C_p be its usual k-by-k companion
matrix, with ones below the diagonal and last column the negatives of p's
nonleading coefficients. Then

```text
det(x I_k - y C_p) = p_h(x,y).
```

This follows either by expanding the determinant, or by homogenizing
det(t I_k-C_p)=p(t). Form a block diagonal pencil with one such block for
every p occurring in P_d and n-S_d scalar blocks y. Its determinant is exactly
D_d,n, so it is regular and has the required dimension and failures.

There is a monic irreducible of degree d+1 over every finite field. If alpha
is any of its roots, none of P_d's factors vanishes at alpha. The slice
[alpha:1] is therefore invertible over F_(q^(d+1)). This pencil has first
successful degree exactly d+1. The scalar y blocks do not change that degree.

## 4. Exact worst-case first successful degree

Define

```text
E_q(n) = min { d >= 1 : n < U_q(d) }.
```

The minimum exists, since the union contains F_(q^d) and hence U_q(d)>=q^d+1.
Section 2 implies that every regular n-by-n pencil has an invertible slice in
at least one degree e<=E_q(n).

If E_q(n)>=2, minimality gives n>=U_q(E_q(n)-1). Apply section 3 with
d=E_q(n)-1 to obtain a regular pencil with first successful degree E_q(n).
If E_q(n)=1, the pencil x I_n has an invertible base-field slice and attains
the bound. Thus

```text
max over regular A,B in M_n(F_q) of e(A,B) = E_q(n).
```

This is an all-prime-power, all-dimension statement. The finite verifier is
corroboration and is not the proof of the quantified maximum.

## 5. One prescribed extension is a different guarantee

For a fixed e, P1(F_(q^e)) has q^e+1 points. The same argument says that every
regular dimension-n pencil has an invertible slice in this particular field
if and only if n<q^e+1. At or above that dimension the homogeneous polynomial

```text
x^(q^e) y - x y^(q^e)
```

and additional y factors give a regular counterexample, realized by companion
blocks as above. This criterion does not contradict the smaller first-success
bound, which lets the successful degree depend on the pencil.

For example U_2(3)=1+2+2+6=11, whereas 2^3+1=9. A dimension-nine pencil may
fail in degree three but must then have an invertible slice in degree one or
two. Also y*(x^16-x*y^15) has invertible slices in degree three and none in
degree four. An extension of larger integer degree need not contain an earlier
extension. No monotonicity in the integer degree is assumed anywhere above.

## Dependencies and limits

The argument uses classical finite-field existence/Frobenius facts, elementary
polynomial factorization and companion determinants. Its contribution is their
sharp union-through-degree threshold for this normalization question and the
matching regular-pencil construction. The motivator is Ali Romman's PR5689
no-base-slice interface, with the later PR5692/5712 decomposition/transport.
No theorem, receipt or numerical count from those packages is re-proved here.

Regularity is essential. An identically singular determinant can vanish at
every point over every extension. Rectangular pencils, choosing an efficient
field representation or witness from raw matrices, field descent and physical
native costs are outside the result. Invertibility after extension does not
assert original-field equivalence or transfer a determinant-character image.
Independent human and formal proof-kernel review are unclaimed.
