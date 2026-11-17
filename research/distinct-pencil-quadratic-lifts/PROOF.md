# Exact cost of distinct-factor quadratic lifts

Let K be any field, R=K[x,y]/(x,y)^3, and J=(x,y). There are exactly two
roles. The paid alphabet is P(u,v)=I+u v^T with u in R^2 and v in K^2.
Arbitrary GL2(K) factors are free anywhere; singular paid factors are allowed.
The endpoint acts on every input in R^2, with no auxiliary roles.

Write

```
M = [[a,b],[c,d]] = diag(x,y) + Q,       Q in M2(J^2),
b = alpha*x^2 + beta*x*y + gamma*y^2,
c = delta*x^2 + epsilon*x*y + zeta*y^2.
```

Then the exact minimum number of paid factors is

```
cost(M) = 2   if gamma=0 or delta=0;
cost(M) = 3   if gamma and delta are both nonzero.
```

The contribution is this distinct-factor pencil classification and its
attaining words. Ali Romman's #5320 asks for another first-order pencil and
classifies a different, repeated-factor binary pencil. Nick Petalas's #4276,
Theorem B, supplies the exact two-factor criterion used below. We cite that
criterion, rather than reprove or scientifically replay its package.

## Three factors always suffice

Set s=alpha*x+beta*y. Since J^3=0,

```
a*s = alpha*x^2 + beta*x*y,
c*s = 0,            y*c = 0,            y*d = y^2.
```

Consequently the following is an exact identity in M2(R):

```
M = [[1,gamma*y],[0,1]] [[a,0],[c,1]] [[1,s],[0,d]].
```

The factors are respectively

```
P((gamma*y,0)^T,e2),
P((a-1,c)^T,e1),
P((s,d-1)^T,e2).
```

Thus all three are legal paid factors, and there are no free endpoint maps
or preparation assumptions in this formal identity. Multiplication order is
algebraic; execution on column inputs is from right to left. This proves
cost at most three for every Q over every field.

If gamma=0, omit the identity first factor to obtain a two-factor word.
If delta=0, put r=epsilon*x+zeta*y. Then d*r=c and b*r=0, giving instead

```
M = [[1,b],[0,d]] [[a,0],[r,1]].
```

These are paid factors with right rows e2 and e1. They prove the stated
two-factor upper bounds, including their intersection.

## No other lift has a two-factor word

Use #4276's criterion: cost(M)<=2 exactly when some G,H in GL2(K) give
N=GMH with N12 in N11 R. Suppose this occurs. Let phi be the first row of
G and t,s the first and second columns of H. There is h in R with

```
phi*M*s = (phi*M*t)*h.
```

Write h=lambda+h1, with lambda in K and h1 in J, and put v=s-lambda*t.
The vector v is nonzero and t,v remain a K-basis. The equation becomes

```
phi*M*v = (phi*M*t)*h1.
```

The right side has no linear part. Write phi=(p,q) and v=(v1,v2)^T.
The linear part of the left side is

```
p*v1*x + q*v2*y.
```

The two linear monomials are independent, so p*v1=q*v2=0. Since both phi
and v are nonzero, exactly one of these cases holds:

1. phi is a nonzero multiple of e1^T and v is a nonzero multiple of e2.
   Then t1 is nonzero because t,v are independent. The left side is a
   nonzero K-multiple of b. The linear part of phi*M*t is a nonzero
   K-multiple of x. Multiplication by h1 can therefore give only an element
   of xJ=span_K{x^2,xy}. Quadratic parts times h1 vanish. Hence b is in xJ,
   which is precisely gamma=0.
2. phi is a nonzero multiple of e2^T and v is a nonzero multiple of e1.
   Now t2 is nonzero. The same argument places c in
   yJ=span_K{xy,y^2}, which is precisely delta=0.

Thus the cited criterion excludes every word of cost at most two when
gamma and delta are nonzero. This argument includes all constant free charts,
all paid right rows, and factors not aligned with coordinate columns.

Finally, M has zero scalar residue modulo J. A free endpoint has invertible
residue. A single paid factor has residue I+u0*v^T of rank at least one,
because it fixes ker(v^T) if v is nonzero and is I if v=0. Free factors
preserve that rank. Therefore cost is at least two for every Q. Together
with the constructions, this proves the exact classification.

## Finite-field count

For a finite field K of size q, Q has twelve independent coefficients.
The cost-three condition makes gamma and delta nonzero and leaves the other
ten coefficients arbitrary. Therefore, among all q^12 lifts,

```
number of cost-three lifts = (q-1)^2*q^10,
number of cost-two lifts   = (2*q-1)*q^10.
```

For q=2 these counts are 1,024 and 3,072. The total and the classification
are proved by the preceding argument; the software exhaustively enumerates
this binary case. It samples F3, F5 and F7 and does not enumerate their
entire lift spaces or any extension field.

## Limits

This is a scoped theorem in the specified formal alphabet. It does not
classify arbitrary first-order pencils or all cube-zero radical targets.
It supplies no native coefficient producer, routing, restoration, precision,
stock, physical caller or recursive supplier bill. Those obligations are
unrun and unknown. No new kappa or complete multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed.
