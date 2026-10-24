# Exact nondegenerate-hyperplane intersection law over F4

This contribution was produced by Nick Petalas. It proves a scoped algebraic
intersection theorem and counting law, with exact finite corroboration.
It answers the intersection obligation left by Maximus Putnam's
[PR #831](https://github.com/CrocSwap/integer-mult-bounds/pull/831).
That package's phase calculus and census are cited predecessors, not audit
subjects here. No new kappa is claimed.

Let V be a nondegenerate Hermitian space of dimension n over
F4 = F2[t]/(t²+t+1), with conjugation a -> a². Take the form linear in
its second argument. A restriction is nondegenerate when its radical is zero;
the zero-dimensional space counts as nondegenerate.

## Result

For n >= 2, write H_u = u-perpendicular for the hyperplane with normal line
F4 u. Nondegeneracy of H_u is equivalent to h(u,u)=1. For distinct
nondegenerate hyperplanes H_u,H_v:

- Their intersection is nondegenerate exactly when h(u,v)=0.
- Otherwise its Hermitian radical has dimension one over F4. Its binary
  trace radical has dimension two over F2.

Define

    N_n = (4^n - (-2)^n)/6,
    Z_n = (4^n + (-2)^n)/2.

There are exactly N_n nondegenerate hyperplanes. For each fixed one,
exactly N_(n-1) other nondegenerate hyperplanes have nondegenerate
intersection with it, and exactly Z_(n-1)-1 have degenerate intersection.
The ordered-pair counts are therefore

    nondegenerate: N_n N_(n-1),
    degenerate:    N_n (Z_(n-1)-1).

For a uniformly chosen ordered pair of distinct nondegenerate hyperplanes,
the degeneracy probability is (Z_(n-1)-1)/(N_n-1), tending to 3/4.
This probability describes the stated finite sample space. It does not
model a supplier's distribution of frames.

The verifier enumerates these complete finite domains:

| Ambient dimension | Nondegenerate hyperplanes | Nondegenerate ordered pairs | Degenerate ordered pairs |
| --- | --- | --- | --- |
| 2 | 2 | 2 | 0 |
| 3 | 12 | 24 | 108 |
| 4 | 40 | 480 | 1080 |
| 5 | 176 | 7040 | 23760 |

A family of distinct nondegenerate hyperplanes whose pairwise intersections
are all nondegenerate has size at most n. Its normal lines are mutually
orthogonal, and every intersection of any subfamily is nondegenerate.
The n coordinate hyperplanes attain the bound. This supplies a precise
sufficient contract for retaining nondegeneracy throughout intersections.

## Proof

### Hermitian coordinates and normal lines

Every nondegenerate Hermitian F4 space has an orthonormal basis. Here is
an elementary argument to fix the field-specific premise. If every vector
had norm zero, choose x,y with a=h(x,y) nonzero. Such a pair exists by
nondegeneracy in positive dimension. For c=t/a,

    h(x+cy,x+cy) = ca + conjugate(ca) = t+t² = 1,

a contradiction. A vector of nonzero norm has norm one, since Hermitian
norms lie in F2. Split off its nondegenerate line and repeat on the
nondegenerate orthogonal complement. Thus h can be written as
h(x,y)=sum_i conjugate(x_i)y_i.

Nondegeneracy of V identifies its hyperplanes with normal lines. The
radical of u-perpendicular is its intersection with F4 u. It is zero
exactly when h(u,u) is nonzero, hence one. Each normal line has three
nonzero vectors, all with the same norm, because every nonzero F4 scalar
has multiplicative norm one.

### Intersection criterion

Let U=span(u,v), where the normal lines are distinct. Then dim U=2 and
H_u intersect H_v = U-perpendicular. The radicals of U and U-perpendicular
are the same subspace U intersect U-perpendicular. In the basis u,v, the
restricted Hermitian Gram matrix is

    [ 1       z ]
    [ z²      1 ],       z=h(u,v).

Its determinant is 1+z³. Every nonzero element of F4 has cube one.
Consequently the matrix has rank two for z=0 and rank one for z!=0.
This proves the criterion and the exact Hermitian radical dimension.
Maximus Putnam's #831, PROOF.md section 1, proves that the radical of the
binary trace form is the same set as the Hermitian radical. Its F2
dimension is therefore twice its F4 dimension. That trace lemma is a
credited dependency, not a new result here.

### Exact counts

In orthonormal coordinates the norm of a vector is the parity of its number
of nonzero coordinates. Let Z_n and O_n count vectors of norm zero and one.
Each coordinate has one zero and three nonzero possibilities, so

    Z_n + O_n = 4^n,
    Z_n - O_n = (1-3)^n = (-2)^n.

The displayed Z_n follows and O_n=(4^n-(-2)^n)/2. Dividing O_n by the
three vectors per nonisotropic line gives N_n. This includes n=0,
where N_0=0 and Z_0=1.

Fix a normal u and use orthonormal coordinates with u=e_1. A second normal
has representative v=(a,w), with a in F4 and w in F4^(n-1), and
h(v,v)=a³+h(w,w)=1. If a=0, the vector w has norm one. These are exactly
the N_(n-1) nonisotropic lines orthogonal to u, and the intersection
criterion says precisely these pairs are nondegenerate.

If a!=0, w must have norm zero. The 3 Z_(n-1) vector representatives
form Z_(n-1) normal lines. One is the original line u, arising from w=0.
Removing it leaves Z_(n-1)-1 distinct normal lines. Their pairings with u
are nonzero and all their intersections are degenerate. This also checks
N_n-1=N_(n-1)+Z_(n-1)-1 and proves both ordered-pair counts. Dividing by
N_n(N_n-1) gives the probability; its limit follows from the leading
powers of four.

### Smallest failure and families closed under intersection

In dimension three take u=(1,0,0) and v=(1,1,1). Both have norm one.
The two input hyperplanes have Hermitian rank two and binary trace rank
four. Their intersection is the line spanned by (0,1,1), whose restriction
is zero. In dimension two, distinct hyperplanes intersect in zero, so
dimension three is the smallest possible failure. Dimension one has no
pair of distinct hyperplanes.

If a family has only nondegenerate pairwise intersections, the criterion
makes its normal lines mutually orthogonal. Choose a norm-one vector
from each. Their Gram matrix is the identity, so they are independent
and their number is at most n. The span of any chosen subfamily is
nondegenerate, as is its orthogonal complement. That complement is
exactly the intersection of the corresponding hyperplanes. Coordinate
normal vectors attain size n. In particular, under this hyperplane
hypothesis pairwise checking suffices for every higher intersection.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

    /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/hermitian-hyperplane-intersections/verify.py
    /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/hermitian-hyperplane-intersections/verify.py
    /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/hermitian-hyperplane-intersections
    /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/hermitian-hyperplane-intersections --check-source-history

Another CPython 3.12 interpreter may replace the absolute local path.
The local environment was CPython 3.12.15 on macOS 27.0.1, arm64.
The two registered commands took 1.62 and 1.61 seconds in direct timed runs;
each has a 120-second registered limit.
The direct check prints a generated SHA-256 receipt binding all five package
files, then PASS_HERMITIAN_HYPERPLANE_INTERSECTIONS. It writes nothing.

The checker constructs every normal line in dimensions two through five.
For each of the 32,494 ordered distinct pairs it computes an actual
intersection basis by F4 elimination, its restricted Hermitian Gram rank,
and its binary trace Gram rank by separate packed-binary elimination.
It checks each individual normal's two counts, not only their aggregate.
It also checks all 21,845 vectors in dimensions zero through seven for the
norm formulas, all 64 field triples for the stated field identities, and
all 4096 subsets of the twelve normals in dimension three. The numbers
of pairwise-safe subsets by size zero through three are (1,12,12,4).
Every safe subset's full intersection is checked directly.

Eight rejection controls cover repeated hyperplanes, isotropic normals,
a dimension outside the pair domain, an invalid field entry, false
intersection closure, a count-sign error, omitted conjugation, and the
wrong binary radical dimension. Positive controls include a nonbinary
coefficient witness and orthogonal normals. All checks remain active
under optimized execution. The universal quantifiers follow from the
written proof, not extrapolation from this finite certificate.

## Limits and engineering decisions

This is a scoped Hermitian hyperplane theorem. It does not identify a
supplier's actual supports or intersections. For subspaces of higher
codimension, pairwise nondegeneracy is a different question. No fitting
labels, physical caller, native conversion, routing, precision, restoration,
stock or complete paid invoice is supplied. The full complex supplier and
complete multiplication theorem remain unproved here. Independent human
and formal proof-kernel review are unclaimed. Lean, Docker and the selected
construction's full replay were not run.

The original rank-shape card is explicitly changed to this algebraic side
question, following #831's stated gap. It does not pass that card's supplier
admission or five-percent improvement gate. The current source-bound baseline
passed. The card's historical first command,
research/complex-local-word-ceiling/verify.py, fails with
KeyError: 'complex_profile' because its selected-profile schema is historical.
That predecessor remains unchanged; the new verifier does not invoke it.

The checker computes the literal restricted forms and imports no predecessor
verifier. All loops have fixed finite domains, every function is shorter than 60 lines,
and validation uses ordinary exceptions. Power-of-ten rule 3 has a bounded
managed-runtime deviation: Python allocates tuples, lists and integers during
this offline computation. At most 176 normal lines are retained; matrices
have at most ten rows and columns; vectors and pairs are streamed. Rule 9
has eight fixed, immediate, nonescaping callbacks only for rejection controls.
There is no service or persistent resource. Warning-strict normal and
optimized commands provide the available diagnostics. No separate static
analyzer is required by this standard-library environment.

## Open next questions

1. Which families of nondegenerate subspaces of codimension two have every
   intersection nondegenerate? The hyperplane result gives a complete safe
   contract only in codimension one. Start with two-dimensional normal
   spaces in F4^4 and classify the restricted Gram matrix of their sum.
   Pairwise orthogonality of normal spaces is sufficient but its necessity
   is unproved and is not asserted here.
2. Can an actual Eisenstein producer keep all required hyperplane normals
   mutually orthogonal, with a complete paid consumer? Start by extracting
   one producer's literal normal lines and checking this theorem's criterion.
   The missing supports and physical invoice block a supplier conclusion.

These follow-ups are not investigated here. TASK.json records their first
steps and blockers.

## Credit and source boundary

Produced by Nick Petalas. Maximus Putnam / Maximooch's #831 supplies the
explicit unresolved intersection obligation and the trace-radical lemma.
Its retained credit includes Joel Pulikkan / GamingPuzzled's #620 report,
hipotures' alternating-block predecessor #41 and the endpoint-phase authors.
The new contribution is the exact intersection criterion, all-dimension
counts, smallest failure and pairwise-safe family consequence in this
repository's F4 interface setting. The Hermitian linear algebra and parity
counting tools are elementary; no historical priority for them is claimed.

SOURCES.json pins the predecessor documents, catalogue and selected record
at canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf as historical
provenance. They are not live mathematical inputs to the standalone finite
checker. No predecessor code is copied. Apache-2.0.
