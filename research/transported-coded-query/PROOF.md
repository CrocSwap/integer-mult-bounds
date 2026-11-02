# An exact transport contract for a coded child substitution

This scoped construction and written proof were produced by Nick Petalas.
It addresses the typed-child-substitution question in Dillon Amburgey's
[PR4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933).
The four-field scaffold comes from Ali Romman's
[PR6348](https://github.com/CrocSwap/integer-mult-bounds/pull/6348).
The new step is its exact intertwining condition, ordered residual and
transported-query construction. No predecessor result is reverified here.

## Contract and theorem

Let A, B and q be units in any unital ring, and let c be an arbitrary ring
element. Ring elements act on the left of four original, arbitrary fields
`(x,y,u,v)`. One may take the fields in the ring's left regular module;
more generally they may be in any left module. Products act rightmost first.
There are no commutation assumptions on A, B and q.

Put H=AB. Define the two child maps on the first two fields by

```text
child A = diag(A,A) [[1,c],[0,1]],
child B = diag(B,B) [[1,0],[-q^-1,1]].
```

Define the scalar bridges, thin query and complete complement by

```text
R(x,y,u,v) = (x+v,u,x,y),
S(x,y,u,v) = (x+u,y,u,v),
L(x,y,u,v) = (x,v,x-u,v-y),
C(q): u <- u+q(v-y),
I(H) = diag(1,1,H,H).
```

Use this chronological word, retaining the full complement:

```text
R, C(q), S^-1, I(H), child B, child A, S, L.
```

**Theorem.** Write E=A(cB-Bq). The exact endpoint is

```text
(H(x+qy), Hy, Hqu, Hq^-1 v)
    + (E(y-q^-1 v), 0, E(y-q^-1 v), 0).             (1)
```

Consequently the endpoint is the desired coded query supplier and two
independent coded jobs,

```text
diag(H,H,H,H) [ U(q) direct-sum q direct-sum q^-1 ],
```

if and only if `cB=Bq` as operators on the admitted module. For a ring
identity, or a faithful module, this is the ring equation `cB=Bq`.
Since B is a unit, the unique ring solution is

```text
c = BqB^-1.                                          (2)
```

In particular, taking the same query c=q in both children works precisely
when B commutes with q on that module. A need not commute with B or q.
Equation (2) gives a construction for arbitrary ordered, noncommuting
stage factors. It does not grant physical access to that transported query.

## Direct proof with all inputs retained

After R, C(q) and S^-1, the fields are

```text
(v-qy+qu, u, x+qy-qu, y).
```

After I(H) and child B they are

```text
(B(v-qy+qu), B(y-q^-1 v), H(x+qy-qu), Hy).
```

After child A, the first field is

```text
Hqu + (AcB-Hq)y + (H-AcBq^-1)v,
```

and the second is `H(y-q^-1 v)`. Apply S and then L. The identity
`H-AcBq^-1 = -(AcB-Hq)q^-1` gives (1), with no reordered factors.

For necessity, set x=u=v=0 and vary the independent original input y.
The first output defect is Ey. Thus correctness on a left module requires
E to act as zero. Multiplication by the invertible A gives exactly the
operator intertwining equation. In the left regular module, taking y=1
also proves the ring equation. Conversely E=0 in the admitted action makes
every displayed defect zero. This proves both directions.

For (2), multiply cB=Bq on the right by B^-1. All signs and inverses are
literal ring operations. The argument includes characteristic two and
noncommutative rings with zero divisors. It requires neither division by an
integer nor a finite-order relation on q.

## The next scalar bridge and the local bill

Every displayed scalar bridge is invertible over the integers. Their
inverses are

```text
R^-1(x,y,u,v) = (u,v,y,x-u),
S^-1(x,y,u,v) = (x-u,y,u,v),
L^-1(x,y,u,v) = (x,y-v,x-u,y).
```

The following in-place recipes require no initialized or borrowed field.
Here each SWAP exchanges whole fields.

```text
R: b+=x; SWAP(x,b); SWAP(y,a); SWAP(a,b).
C: b-=y; a+=q*b; b+=y.
S^-1: x-=a.
S: x+=a.
L: a=-a; a+=x; y=-y; y+=b; SWAP(y,b).
```

The recipe uses `(a,b)` for `(u,v)`. The middle instruction of C is one
complete thin query. Outside the supplied child and complement calls,
there are seven ordinary field additions/subtractions, four field swaps
and two field negations. These are finite operation counts, not a TM tariff.

The complete abstract bill contains one child A, one child B, one thin q
query and two H applications. In particular, I(H) has not disappeared.
Its H is the ordered product AB, not BA or a product declared Gaussian.
Transporting q inside child A and realizing each H are unpaid physical
obligations until a concrete implementation and invoice are supplied.

For a typed substitution, the two child types must therefore be
`Upper(A,BqB^-1)` and `Lower(B,q)`, with `Lower` using `-q^-1` as above.
The parent returns `Upper(AB,q)` and jobs `ABq`, `ABq^-1`. Its next scalar
bridge S is compatible because integer field mixing commutes with the
same left action AB on every field. This statement needs no mutual
commutation of the stage factors. Any independent child helper outputs
remain unchanged if all these operations act only on the four main fields.

All four main inputs remain arbitrary. The successful endpoint is
invertible, so the two returned terminal fields are independent jobs,
not initialized scratch or duplicate productive credits. Their coded
operators have not been assigned Gaussian ranks. This is one abstract
substitution contract; it does not admit the actual negative banks of
PR4933 or prove closure of its physical compiler.

## Evidence and limits

The new checker expands every entry in an integer free-group algebra.
It checks (1) with an independent c, (2) with transported c and all three
nonzero free commutators. The residual uses no inverse of c, so its
reduction also applies when c is not a unit. Six altered words reject.

A separate engine propagates literal two-coordinate vectors over F2 and
F3. It exhausts every A,B,q in GL2(F2), then every B,q in GL2(F3) with
A=[[1,1],[0,1]]. Every one of the eight arbitrary input basis columns is
checked. It separately verifies that c=q succeeds exactly for the
commuting B,q fixtures. Finite checks corroborate the written universal
proof; they are not proof-kernel acceptance or independent human review.

This does not establish a cheaper physical operation, native all-column
binding, transport/complement tariff, owned-erasure permission, uniform
compiler, precision/tape bound or analytic recovery theorem. No selected
frontier, improved kappa or complete multiplication theorem is claimed.

## Credit and distinction

Dillon Amburgey / PR4933 posed the coded recursive-substitution question and
supplies the phase-correct coded-caller context, following Dugongue's
PR4929 producer and noncommuting-controller work. Ali Romman / PR6348
supplies R, C, S, L, the paid complement and the four-field query extension
for commuting fresh-axis factors. Those maps and that original identity
are predecessor work. This proof adds their exact residual for a different
child query and the necessary and sufficient transport contract.

Cinna Davis retains the thin-query and query-thinned caller lineage;
Cao Yifan, zxv, Jacob Alan Sussman, Ryanson Jonathan and the retained native,
helper, compiler and outer authors keep their predecessor credit. Ordered
block multiplication and conjugation are classical tools. No global
literature-priority claim is made. Source text is linked and pinned as
provenance; no predecessor executable is imported or replayed. Apache-2.0.
