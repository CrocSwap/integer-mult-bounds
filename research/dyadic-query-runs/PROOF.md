# Dyadic runs in a restored native BIT query batch

This is a local recursive-interface construction and a query-count optimum
in an explicitly restricted alphabet. It does not change a supplier or kappa.
The one-query native lowering is credited to PR521 and its signed dyadic
extension to PR840; their original proofs and notices are in `vendor/`.

## 1. Contract and alphabet

Let `h` be the VALUE permutation induced by the ADDRESS **push** map

```
M(k) = I + (k/4) s r^T,
s = (1,0,1,-1,0,-1)^T,  r = (1,0,-1,-1,0,1)^T.
```

The six selected fields have equal width b over `Z/(ell^b)`, with ell odd.
They are physically ordered; arbitrary intervening and exterior ADDRESS
fields and suffix VALUE records are spectators. Since `r^T s=0`, the query
`Q(k): x <- h^k x` has inverse `Q(-k)` and `M(k)M(l)=M(k+l)`.
The other instruction is `X: x <- x XOR y`. Only the target x is queried;
source y and all other dirty roles are never changed. Every query power must
be a nonzero **signed power of two**. Every full ordinary recursive child,
its affine wrappers and the full XOR scan are paid.

For a finite nonempty index set `J subset Z_{>=0}`, define

```
D_J(x,y,z) = (x + sum_{j in J}(h^(2^j)+h^(-2^j)) y, y, z).
```

VALUE sums are in F2; ADDRESS arithmetic is not. The program is uniform over
all odd prime-power field moduli. The target is exclusively owned throughout
the batch: intermediate contents cannot be observed or used by other calls.
No clean, disposable or additional full private role is available. Role
mixing, queries on y or z, nondyadic queries and modulus-specific programs
are outside the optimization alphabet. PR840's more permissive single-pair
three-query lower bound is neither strengthened nor contradicted here.

## 2. Retain the target layout across one run

For an interval `[l,u]` of indices, follow this walk of cumulative powers:

```
0, -2^u, -2^(u-1), ..., -2^l, +2^l, ..., +2^(u-1), +2^u, 0.
```

Execute `Q(next-current)` at each edge and X at every nonzero listed vertex.
Every edge is dyadic: the two exterior edges are `-2^u`, each interior gap
on either side is a positive power of two, and the middle edge is `2^(l+1)`.
If the interval has t indices there are `2t+1` queries and `2t` XOR scans.

An X at prefix power p contributes `h^(-p)y` at the endpoint, because the
total query power is zero. The visited powers are precisely `+/-2^j` for
the interval. Thus the endpoint is D for that interval on arbitrary dirty
inputs. Concatenate this word for all maximal consecutive runs of J. Each
word restores the target layout; the VALUE shears add and source/spectators
remain unchanged. If r is `|J|` and c is the number of runs, the complete
word uses

```
q(J) = 2r+c queries,  2r XOR scans.
```

The baseline concatenates PR840's optimal single-pair word
`Q(-a), X, Q(2a), X, Q(-a)` for every `a=2^j`, costing `3r` queries and
the same `2r` XOR scans. The saving is `r-c` full queries, without assuming
any previously restored boundary is free. Reversing all literal events,
inverting each Q and keeping X, gives the exact inverse. D itself is an
involution, but the inverse literal word need not equal the forward word.

## 3. Exact optimum in this alphabet, including off-support excursions

Consider any finite program in the alphabet, not just the run constructor.
On a full-order orbit the ADDRESS action is multiplication by t in
`F2[t,t^-1]/(t^m-1)`, m an odd prime power. Such an orbit exists: starting
at the first coordinate vector gives `e0 + k*s/4`, distinct for k modulo m.
Uniform equality for arbitrarily large m implies equality of the corresponding
finite Laurent polynomials. Choose m larger than their exponent span to see
that no nonzero finite difference can vanish in every quotient.

Restoring arbitrary x therefore forces the total **integer** query power
to zero. At cumulative prefix p, an X adds `t^(-p)y` at the endpoint.
To produce D_J, the closed walk must visit every member of
`S={+/-2^j: j in J}` and tap it oddly; off-support taps must cancel evenly.
In particular it needs at least `2r` XOR scans.

Join two distinct elements of S when their difference is a signed power of
two. For distinct magnitudes, same-sign vertices are joined exactly when
their indices differ by one: `2^b-2^a = 2^a(2^(b-a)-1)`. Opposite-sign
vertices of different magnitudes are not joined, since their sum has an odd
factor larger than one. The two signs of a single magnitude are joined.
Consequently this induced graph has exactly c components, the consecutive
runs of J. This is a graph property of the required vertices, not a ban on
off-support visits.

Write a closed walk with q edges cyclically as its first q vertices (omit
the repeated endpoint). Let a count occurrences in S and b occurrences
outside S. Then `q=a+b` and `a>=2r`. The walk starts at 0, outside S, so
`b>=1`. Every block of S vertices between consecutive outside occurrences
lies within one component of the induced graph. There are at most b such
blocks. All c components must be visited, so `b>=c`. Thus

```
q >= 2r+c.
```

This also covers repeated vertices, untapped intermediate states, arbitrary
large dyadic jumps and off-support XOR cancellations. Section 2 attains the
bound. The empty set separately admits the empty word. This is a written
universal argument; the finite certificate is supporting evidence, not a
proof-assistant theorem.

Two scope controls matter. For J={0,2}, allowing nondyadic jumps gives the
five-query walk `0,-4,-1,1,4,0`, beating the six-query restricted optimum.
For J={0,1} modulo 3, the four monomials cancel and the empty program works.
Neither is a counterexample to the uniform dyadic-alphabet theorem.

## 4. Literal paid native lowering

For each query k, set `a=k/4`. The retained PR840 chronological lowering is

```
z2 <- z2-z0
z3 <- z3+z0
z5 <- a*z5+(1+a)*z0-a*z2-a*z3
CHILD_C(0,5)
z2 <- z2+z0
z3 <- z3-z0
z5 <- -(1/a)*z5+(1/a-1)*z0+z2+z3.
```

The child interchanges equal-width fields on the entire queried row. It
preserves all spectators and returns its own workspace. Every affine control
precedes its target. Each diagonal coefficient is a signed power of two,
and every coefficient denominator is a power of two. Hence these operations
and their literal inverses specialize to every odd modulus. Removing the
child or treating the ADDRESS coefficients as binary VALUE coefficients is
invalid. The exact certificate contains all seven events for each used k.
This lowering is inherited; the new contribution is the shared batch schedule
and its exact restricted optimum.

## 5. Complete work and storage recurrence

Use the same three genuine equal-volume roles as PR840. Let each full row
have volume U (including all spectators and VALUE bits), `V=3U`, `N=3b`.
Let `C(U,b)` pay one ordinary restored ADDRESS interchange. Let `L_k(U,b)`
pay all six affine events of the above lowering: coefficient preparation,
coefficient/source access, descriptors, counters, primitive temporary streams,
routing and head returns. Let `X(U)` pay one aligned XOR scan. Let `R_J`
pay all further schedule preparation/dispatch, full-row splitting/rejoining,
parking, source access and additional head returns, avoiding double counting
those already in L, C or X. J is supplied as a finite fixed program parameter.

The literal invoices for the baseline B and fused run program F are

```
B_J(V,3b) <= 3r C(U,b)
             + sum_{j in J} (2 L_{-2^j}(U,b) + L_{2^(j+1)}(U,b))
             + 2r X(U) + R_B(J,U,b),

F_J(V,3b) <= (2r+c) C(U,b)
             + sum_{[l,u] a run of J}
                 (2 L_{-2^u}(U,b) + L_{2^(l+1)}(U,b)
                  + 2 sum_{i=l}^{u-1} L_{2^i}(U,b))
             + 2r X(U) + R_F(J,U,b).
```

Each query has exactly one full-row child and six affine events. No copy,
clear, uncompute child or frame change is omitted: X reads unchanged y;
queries act only on x; all target-layout return edges are present; all
address-chart work is in the six-event lowerings. There are no extra full
private roles, copied sources or recursive product children. Any future
supplier adapter or incompatible frame must be separately charged, and is
not provided by this construction. The child interface is inherited, not
implemented by these finite replay arrays.

For the two literal invoices, the saving is `(r-c)C + L_B-L_F + R_B-R_F`.
Different coefficient tables may change L, so no universal wall-clock or
finite total-work speedup is inferred from the counts. In particular the
seed-selected J={0,1,2,4,5} lowers 15 to 12 children and 90 to 72 affine
events, retaining ten XOR scans; its coefficient-aware inequality still
needs the actual implementation costs.

The children execute sequentially on actual volume V/3 and width N/3. For
fixed J, the retained stream premises give `L_k,X,R=O_J(V)`, so the child
coefficient is `(2r+c)/3` instead of r. For growing J, retain all coefficient,
program-storage and dispatch dependence explicitly: coefficients have
`O(1+max J)` bits, but the inherited stream constants can depend on their
values. No polynomial dependence on max J is asserted. A safe peak bound is

```
W_F(V,3b) <= V + B_F(J,U,b) + W_C(U,b),
```

where B_F pays live coefficient/descriptor/counter state and the maximum
nonchild stream workspace retained across a child. This is not an exact
physical tape count. The target and source may not alias.

F is a completed DATA shear and C an ADDRESS interchange. Substituting F for
C and solving a self-recurrence would require a compiler not supplied here.
Neither selected supplier nor any assembly inequality changes. Common labels,
mutable-source realization, frames/owners, full-row hosting, arbitrary widths,
all-size compilation, tape/precision and the outer analytic transfer remain
open. No new kappa follows from this result.

At the pinned base the selected assembly explicitly reports `binding: complex`:
the complex lower endpoint is `1664724476433282815289/10^24`, below the bit
endpoint `1733427039589844234749/10^24`. Even an integrated improvement only
to this BIT interface would not by itself establish a stronger selected
exponent. No such integration or recomputed supplier moment is supplied here.

## 6. Bounded evidence

All 63 nonempty subsets of indices 0 through 5 are compiled. Seed 55 is the
six-bit mask choosing the gapped five-pair example. A separate verifier reads
literal words and lowerings without importing the constructor, independently
recounts graph components, and replays Laurent coefficients, rational and
modular ADDRESS columns and full-domain dirty VALUE executions. It checks
baselines, inverses, native spectators and obligation-specific faults.
An independent breadth-first traversal exhausts all walks represented by
`(position, visited-support-mask)` with position in `[-32,32]`, dyadic steps
through 64 and support indices 0 through 3. All 15 nonempty target selections
agree with the formula. This allows intermediate visits outside their support
but is still a bounded experiment, separate from section 3's unbounded proof.
The stopping rule is completion of these domains, with no adaptive search.
No exhaustive optimization over arbitrary circuits, new supplier invoice,
full multiplication proof or literature-priority claim is made.
