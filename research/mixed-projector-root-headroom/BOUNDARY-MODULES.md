# Helper consumption and a five-call border

These are exact module results. They do not increase the complete kappa.
The source-bound prices use the final PR6375 composition at 0.00328620.
The native caller and recursive precision transfer for these changed
interfaces have not been constructed.

## 1. A three-field module that consumes one helper

The module has three full sites with stage ranks 2,3,2. The middle site
uses one independent B*S Gaussian output in addition to its two-field
query. There is no extra thin query or idle. In the basis

```text
F = [[ 0, 1,-1],
     [-1,-1, 0],
     [ 1, 1, 1]],
```

the endpoint is S diag(ABC,AB,BC). `boundary_modules.py` gives the three
projectors, rank-one queries and the middle Gaussian selector. It checks
both central characters and every stage coefficient. Each stage occurs
once, so each entry has degree at most one in each of A,B,C. Equality at
the two nodes 1 and 2 for each variable proves the polynomial identity.

The consumed output must be debited. With child sizes a,b,c and n=a+b+c,
the optimistic signed invoice is

```text
H(8n+1)+H(8(a+b)+1)+H(8(b+c)+1)-H(8b+1)
  -nL-C(a)-C(b)-C(c).
```

Here L includes every paid native call minus every retained helper, per
port, and C is the minimum complete binary-node bill. The subtraction of
H(8b+1) removes the consumed helper from the independent outputs. This
price already gives the module a matching helper; it does not assert
that a complete physical source supplies that interface.

`boundary_prices.py` checks every positive triple with n<100, up to the
exchange of a and c. It uses outward rational bounds and a 2^40 integer
grid. All upper bounds are negative. For n>=100, C(a)+C(b)+C(c)>=-(n-3).
Jensen bounds the two pair outputs by 2H(4(n+b)+1). The difference
2H(4(n+b)+1)-H(8b+1) decreases with b<n. Thus

```text
margin <= H(8n+1)+2H(4n+5)-H(9)-n(L-1)-3.
```

The replay verifies that this concave function and its derivative are
negative at 100. This excludes all positive binary child sizes and all
binary shapes of this particular helper-consuming module.

## 2. A border that uses two paid central Gaussian calls

Use four arbitrary fields, three full stages on supports {0,1}, {0,2},
{0,3}, and two paid rank-one Gaussian calls. Let e be a nonzero scalar.
The five chronological factors are I+(S-1)u_i v_i. The full stages occur
at sites 0,2,4, and multiply their query on the left.

| Site | u_i | v_i | Kind |
| --- | --- | --- | --- |
| 0 | (1,0,0,0) | (0,1/e,0,0) | full, stage A |
| 1 | (-1/e,1,0,0) | (0,1,-e^2,0) | paid Gaussian |
| 2 | (-e,0,1,0) | (-1/e,0,-1,0) | full, stage B |
| 3 | (-e,0,1,-1) | (-1/e,0,0,0) | paid Gaussian |
| 4 | (1,0,0,1/e) | (-1,0,0,e) | full, stage C |

At each full site v_i u_i=0. At each paid Gaussian site v_i u_i=1.
The exact endpoint is

```text
W(e)=S diag(ABC,A,B,C)+(1-S)(-e C E_03+e^2 E_12).
```

Put E(e)=diag(e,1,e^2,e^2). Each factor is
E(e)^(-1) R_i(1) E(e), so one global scalar wrapper gives this family.
The wrapper is undefined at e=0. At every permitted nonzero e, two
off-diagonal entries remain. The diagonal limit is not an exact caller.

Write D=diag(ABC,A,B,C) and N=(1-S)(-e C E_03+e^2 E_12).
The two error paths do not compose: N D^(-1) N=0. Therefore

```text
W(e)^(-1)=S D^(-1)-D^(-1) N D^(-1).
```

For unitary S,A,B,C, both the forward endpoint and inverse-transpose
endpoint have error norm at most 2e+2e^2 for 0<e<=1/2. This finite norm
bound does not fund recursive precision or error recovery.

The replay keeps e formal in Q[e,e^-1]. It verifies the common wrapper,
the forward formula, both inverse products and both direct corrections.
The forward entries have stage exponents 0 or 1. The proposed inverse
has stage exponents -1 or 0. Inverse products therefore have exponents
between -1 and 1 in each stage. Multiplication by ABC gives degree at
most two in each variable. The grid {1,2,3}^3 proves every coefficient by
interpolation; it is not a numerical sample. Both central characters are
checked. A missing small input term and a false exact endpoint are rejected.

## 3. Formal price and the cost of direct recovery

For children a,b,c, the diagonal-limit invoice is

```text
H(8n+1)+H(8a+1)+H(8b+1)+H(8c+1)
  -nL-C(a)-C(b)-C(c)-2,    n=a+b+c.
```

The final 2 pays both central Gaussian calls. The fixed children 6,6,6
have binary-node counts {2:9,4:3,6:3}. Their complete formal inventory
includes all 18 native invoices, native helper debits, binary thin
queries, binary idles, and the two Gaussian calls. The exact crossing
and a positive rational margin above 1.01 times the current complete
kappa are recorded in RESULT.json. This is a feasibility test of the
diagonal limit. It omits the recovery of N and is not a kappa result.

Two direct rank-one queries restore the exact endpoint:

```text
after site 1: field 1 += e^2 (S-1) field 2;
after site 4: field 0 += e   (S-1) field 3.
```

Their two additional paid H1 jobs change the final fee from 2 to 4.
The new exact price proof excludes every positive binary child triple
and shape at the current saving. It enumerates n<100. For n>=100,
Jensen and C(a)+C(b)+C(c)>=-(n-3) give

```text
margin <= H(8n+1)+3H(8n/3+1)-n(L-1)-7.
```

This concave bound and its derivative are negative at 100. Thus the
direct two-query recovery loses for all sizes, not only the earlier
bounded numerical search. Other recovery methods are not excluded.

## 4. Why the star has no exact five-call endpoint

Fix four fields, three rank-one square-zero full queries on the three
distinct star supports above, and two rank-one central reflections.
Allow any order and arbitrary scalar coefficients in characteristic
other than two. If the endpoint at S=-1 were -I_4, the chronological
identity would give U(I+2L)^(-1)V=I_4. Hence

```text
Z=I+2L-VU
```

has rank one. At each of the three full sites its diagonal entry is one.
Writing Z=xy forces, for the three full sites i<j<k,

```text
G_ij G_jk G_ki=1,       G_ik G_kj G_ji=-1.
```

Two distinct star supports intersect in coordinate 0 only. Every cross
pairing is consequently G_ij=v_i[0]u_j[0]. The two displayed products
are equal products of the same six scalars, a contradiction. This rules
out the exact five-call star with arbitrary coefficients and order. It
does not cover a triangle, repeated supports, more calls or ordinary
coefficients that do not commute with S. The existing Gram checks in
the main verifier check the signs used in this argument.

## Open next questions

- Find a recovery method with a complete price below the two-query fee.
- Prove a precision transfer for this chronological border. It must
  include amplified scalar coefficients, owned restoration, both
  orientations and the recursive cost. A finite endpoint norm estimate
  or an ordinary matrix tensor-degree estimate does not supply it.
- Test a changed helper interface whose complete signed bill is positive.

PR4623 and Discussion4611 contain the earlier scalar-filtration and
finite-approximation work; their recursive precision obligation remains
open. The present five-call identity and source-specific price are
separate results. PR6348 supplies the binary module. PR6353, PR6372 and
PR6375 supply the native invoices, with their original authors and notices.
The caller lineage is by Cinna Davis; all native, compiler, recursion,
BIT and analytic predecessors retain their source credit.

New research and exact replay: Ali Romman with substantial OpenAI Codex
assistance; no subagents. Apache-2.0. All checks are author checks.
