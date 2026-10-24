# Exact radical reachability counts over every finite field

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped counting proof with finite corroboration. This answers
Open next question 2 of [#4745](https://github.com/CrocSwap/integer-mult-bounds/pull/4745),
at `3edea13af13b755932852e9306a714b317630dda`. That predecessor proves the
reachability criterion over arbitrary fields and gives its binary count.
The new result is the exact count over every finite field. No new kappa is
claimed, and the predecessor theorem is used as a cited step, not audited.

Let K=F_q and R=K direct-sum J be a split unital central K-algebra with
J squared zero and finite d=dim_K J. The alphabet has paid factors I+u y^T,
u in R squared, y in K squared, and common free GL_2(K) maps. For radical
targets M in M_2(J), put z=q^d and

```text
A_r(z) = product_(i=0,...,r-1) (z-q^i).

unreachable(q,d) = A_4(z) + q(q^2-1) A_3(z)
                  + [q^2(q-1)^2/2] A_2(z),
reachable(q,d)   = z^4 - unreachable(q,d).                 (1)
```

Every target counted as reachable has exact paid cost two; every remaining
target is unreachable at any finite word length. This cost interpretation
is #4745's theorem. The counts include d=0, when the only target is zero
and its formal cost is still two. Products with r>d vanish because one
factor is zero.

At q=3,d=2 the counts are **5,697 reachable and 864 unreachable** out of
6,561. At q=3,d=3 they are **250,641 and 280,800** out of 531,441.
At q=4,d=2 they are **52,576 and 12,960** out of 65,536. F_4 here is the
field F_2[t]/(t^2+t+1), not integers modulo four.

## Proof

Choose a basis epsilon_1,...,epsilon_d of J and write
M=sum_j A_j epsilon_j, with A_j in the four-dimensional space V=M_2(K).
Use the nondegenerate entrywise pairing on V. By #4745, M is reachable
exactly when some nonzero row phi and column v have phi A_j v=0 for every j.
Equivalently, S=span(A_1,...,A_d)-perpendicular contains a nonzero rank-one
matrix, whose entries are phi_i v_j. Thus M is unreachable exactly when
every nonzero matrix in S is invertible.

We count such subspaces S by their dimension s. Evaluation T maps to T e_1
is injective on S, because a nonzero matrix killing e_1 would be singular.
Therefore s<=2. The numbers N_s of possible subspaces are

```text
N_0=1,   N_1=q(q^2-1),   N_2=q^2(q-1)^2/2.                (2)
```

The line count is |GL_2(K)|/(q-1)=q(q^2-1). To prove the plane count,
count ordered bases (A,B) of all allowed planes. Necessarily A is invertible.
Set C=A^-1 B. The plane has no nonzero singular matrix exactly when
det(a I+b C) is nonzero for every (a,b) other than (0,0). For b nonzero,
this says that C has no eigenvalue in K. For a two-by-two matrix this is
equivalent to its characteristic polynomial being irreducible of degree two.

There are (q^2-q)/2 monic irreducible quadratic polynomials: partition
F_(q^2) minus F_q into its two-element Frobenius orbits. All matrices with
one such polynomial are conjugate to its companion matrix. Its centralizer
is K[C], since any nonzero vector w makes (w,Cw) a basis and a commuting
map is determined by its value on w. The invertible centralizer therefore
has q^2-1 elements. Each conjugacy class has
|GL_2(K)|/(q^2-1)=q^2-q matrices. Hence the number of possible C is
(q^2-q)^2/2. This reasoning works in even characteristic too.

There are |GL_2(K)| choices for A, and then B=A C is determined. Each
allowed plane is counted by its (q^2-1)(q^2-q) ordered bases. Dividing gives

```text
N_2 = |GL_2(K)| (q^2-q)^2 / [2(q^2-1)(q^2-q)]
    = q^2(q-1)^2/2.
```

For each fixed S of dimension s, put W=S-perpendicular. The coefficient
tuple (A_1,...,A_d) must span the fixed (4-s)-dimensional W. Relative to
any basis of W, these tuples are precisely full-row-rank (4-s)-by-d
matrices. Choosing their independent rows gives A_(4-s)(q^d) tuples.
The annihilator S of each tuple is unique, so there is no double counting.
Summing N_s A_(4-s)(z) for s=0,1,2 proves (1).

For q=2, expansion gives reachable=9z^3-30z^2+42z-20, exactly the
predecessor's binary law. That specialization retains predecessor credit.
The matrix-space and finite-geometry counts in (2) are classical. In
projective language the planes are external lines to the determinant
hyperbolic quadric. See, for example, Tatsuya Fujisaki's
[2003 paper](https://www.kurims.kyoto-u.ac.jp/~kyodo/kokyuroku/contents/pdf/1299-12.pdf)
for that established geometric setting. The contribution here is their
application to the all-field formal-alphabet target count, with the proof
given above; no novelty is claimed for the classical plane enumeration.

## Evidence and reproduction

The standard-library verifier imports no predecessor executable. It directly
enumerates coefficient tuples and intersects their literal bilinear-zero
sets. Over q=2 it covers d=0,...,4, over q=3 it covers d=0,...,3, and
over q=4,5,7 it covers d=0,...,2.
These are **6,832,236 target tuples**. Every reachable/unreachable count
agrees with (1). It separately enumerates **5,580 subspaces** by unique
reduced row-echelon bases and checks each for rank-one matrices. The allowed
plane counts at q=2,3,4,5,7 are respectively 2,18,72,200,882. A third
calculation counts matrices with no field eigenvalue and checks the
irreducible-matrix formula used in the proof.

Seven control groups distinguish a shared chart from separate coefficient
charts, reject three changed counting expressions against literal target
censuses, distinguish F_4 from Z/4Z, and enforce field/domain capacities.
The binary overlap gives (reachable,unreachable)=(244,12) at d=2 and
(3004,1092) at d=3, agreeing numerically with #4745/#4276. At binary d=4,
the new census gives (29836,35700), including the full-span term A_4(16)
that vanishes at every lower dimension. This is a
compatibility check accompanying the new count, not a predecessor review.
All reported census totals are generated by the loops that enumerate them.

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/radical-all-field-count/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/radical-all-field-count/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/radical-all-field-count
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/radical-all-field-count --check-source-history
```

Any CPython 3.12 installation may replace the absolute local path. The marker
is `PASS_RADICAL_ALL_FIELD_COUNT`. Each execution prints a generated JSON
receipt binding all five package files by SHA256 and writes nothing. No
handwritten receipt is committed. Ordinary and optimized Python use the same
explicit checks. The universal claim rests on the written proof and the
cited reachability theorem, not extrapolation from the finite census.

## Scope, source boundary and implementation decisions

The algebra is split, has scalar residue K, has two roles, and has J^2=0.
Only targets with all entries in J are counted. Other singular targets,
higher nilpotency, more roles and nonfield residue rings are outside scope.
No request producer, native coefficient preparation, physical routing,
restoration, stock, precision or complete consumer invoice is supplied.
Those costs remain unknown. No supplier admission, complete multiplication
theorem or selected-frontier change follows. Independent human and formal
proof-kernel review are unclaimed. Lean, Docker and selected cold replay
were not run, and no proof-assistant formalization is claimed.

The formal-interface-lemma card is explicitly changed to this algebraic side
question because #4745 leaves it open. The historical card's first baseline
was attempted and stopped at the omitted sparse input
`research/fresh-helper-thinned/PROOF.md`; it did not pass. This is not a
supplier expansion. The predecessor is an exact-head citation in TASK.json,
not an imported executable or an undeclared dependency on its Git objects.
The package is self-contained computationally. SOURCES.json pins main's
catalogue and selected record as historical provenance only.

Verifier loops have fixed q<=7, d<=4, four-dimensional vector spaces and
at most 5,764,801 streamed tuples in one census. Only at most 2,401 masks,
64 bits per mask, field tables and one basis/tuple persist during a scan.
No recursive calls, subprocesses, dynamic code or indirect callback targets
are used. Functions remain under 60 lines. Explicit exceptions remain active
under -O, and warnings are errors. CPython allocates integers and containers
while scanning; this is the managed-runtime deviation from Power of Ten
rule 3, bounded by the fixed domains above. No additional static analyzer
is configured or claimed. A larger census must declare fresh capacities.

## Open next questions

1. For a named radical target, what is the distribution of its number of
   projective bilinear-zero pairs, rather than just whether that number is
   zero? Start by classifying intersections of its annihilator with the
   determinant quadric. This could price a restricted common-chart choice;
   an actual physical choice/emission bill remains missing.
2. What second-order obstruction replaces the criterion when J^3=0?
   Start with F_2[x,y]/(x,y)^3 as already proposed in #4745. Products of
   radical entries survive, so neither this count nor that predecessor's
   square-zero invariant settles the question.

## Credit

Produced by Nick Petalas. Nick Petalas's #4745 supplies the arbitrary-field
reachability theorem, binary law and explicit all-field counting question;
#4276/#4243 supply the two-factor and free-map lineage. ToikY's #4334 supplies
the shared-chart interface context. Wentao Li's #4099, following #2513,
supplies the right-vector alphabet. Classical irreducible-polynomial,
matrix-centralizer and finite-geometry counts retain their existing credit.
No predecessor files or credit lines are changed. Apache-2.0.
