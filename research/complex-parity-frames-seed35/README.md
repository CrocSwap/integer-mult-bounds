# Shared parity decoder: an exact frame-dimension floor

**Scoped negative result / finite research note; no new kappa.** A shared
two-source sum can have a nondegenerate separating frame and still fail the
historical orthonormal-residual interface. In the six-coordinate triple
kernel, 720 scalar-shareable rectangles admit a separating frame of dimension
three but require dimension two or four, according to orientation. The
obstruction below rules out the tempting dimension-three completion without
having to implement a supplier or search its recursive invoice.

The complete census also gives positive evidence: 360 rectangles with a
degenerate source span have legal dimension-four completions. Deleting every
degenerate source-span node would discard these possibilities. This does not
show that retaining them reduces a fully paid circuit's cost.

## Reproduce

From the repository root, with Python 3.11 or later, standard library only:

```sh
python3 -B research/complex-parity-frames-seed35/check.py
```

Expected first line:

```text
PASS_COMPLEX_PARITY_FRAME_CENSUS subspaces=2825 rectangles=1890 rank_one=1170 admissible=900 controls=PASS
```

The second line contains explicit positive and negative witnesses. The
command is offline and read-only. It works under `python3 -I -O -B` as well;
no acceptance condition uses Python `assert`. An optional positional path
selects a certificate to check, and a mismatch produces a nonzero exit.
`discover.py` independently regenerates the JSON certificate on stdout.
Neither program imports repository code or a solver.

## Object, restrictions and complete finite domain

Use the dot product on `F2^h` and label each source and target by a distinct
three-subset, encoded as a bit mask. A source pair and a target pair are each
unordered; the two sides remain distinguished. The historical joint complex
side kernel is

```text
K(s,t) = Re(i^|s intersection t|) = 1, 0, -1, 0  for intersection 0,1,2,3.
```

Its actual side contribution has the inherited common factor `1/2`. That
factor does not affect scalar rank or binary frame feasibility. We test all
two-by-two rectangles with nonzero entries. A single shared scalar sum can
serve both outputs only when this signed matrix has rank one over Q.
Even intersection alone is insufficient: the signs must also factor.

For source pair `s1,s2` and target pair `t1,t2`, let
`E=span(s1,s2)` and `T=span(t1,t2)`. A candidate intermediate frame `U` must
be nondegenerate and satisfy

```text
E subset U subset T-perp.
```

Every source/target label has norm one. The four incident residuals are
`U intersect si-perp` and `U-perp intersect tj-perp`. Each must admit an
orthonormal basis (equivalently, each nonzero residual is nonalternating).
The incoming source-line and outgoing target-hyperplane frames are fixed.
No additional helper, source copy, phase conversion, boundary move or
alternative decoder is allowed in this one-node completion problem.

Seed 35, drawn from OS randomness, selects `h=2*(2+35 mod 2)=6` from the small
even domains 4 and 6. All 2,825 subspaces are tested, including frames outside
the source span and outside any coordinate-space catalogue. There are 20
triple labels, 190 unordered pairs, and 36,100 ordered pair-of-pair choices;
1,890 satisfy the four cross-orthogonality conditions. The stopping rule is
exhaustion of this domain, with no timeout, randomized search or sampled
coverage. The seed also selects the coordinate permutation of a positive
ten-dimensional control. No complete census at dimension ten is claimed.

## Dimension obstruction, proved without enumeration

For a nondegenerate binary space `U`, its characteristic vector `w_U` is the
unique vector satisfying `w_U dot x = x dot x` for every `x` in `U`. For a
norm-one vector `s` in `U`, the residual `U intersect s-perp` is alternating
exactly when `w_U=s`: its annihilator inside `U` is the line spanned by `s`,
and `w_U` cannot be zero since `U` contains a norm-one vector.

Suppose two distinct norm-one sources satisfy `s1 dot s2=1`. Their
two-dimensional span has radical `r=s1+s2`, so it cannot itself be the
nondegenerate frame. If a separating frame `U` had dimension three, then
`E=r-perp` inside `U`. Since `r dot r=0`, the characteristic vector belongs
to `E`. Of the four vectors in `E`, the only ones pairing to one with both
sources are `s1` and `s2`. Thus one incoming residual is a nonzero alternating
plane. It has no orthonormal basis. An admissible frame must have dimension
at least four.

Apply the same argument to `U-perp` and the two targets for the outgoing
edges. Writing `alpha=s1 dot s2` and `beta=t1 dot t2`, every admissible frame
satisfies the necessary bounds

```text
dim U >= 2 + 2*alpha,
h - dim U >= 2 + 2*beta.
```

These are **necessary**, not generally sufficient, conditions. In particular,
when both pairs are degenerate, dimension at least eight is necessary.
The checker supplies an admissible dimension-eight example for general
norm-one labels (some are not triples), and an admissible dimension-ten
example using only triples. These controls prevent turning the six-coordinate
result into an unjustified all-dimensional obstruction.

## Exact census

“Separating” checks nondegeneracy and the two containments. “Admissible” also
checks all four residuals. Counts distinguish source and target orientation.

| alpha | beta | Scalar rank one | Nonzero E intersect T | Count | Separating dimensions | Admissible dimensions |
|---:|---:|:---:|:---:|---:|:---:|:---:|
| 0 | 0 | yes | no | 180 | 2, 3, 4 | 2, 3, 4 |
| 0 | 1 | yes | no | 360 | 2, 3 | 2 |
| 1 | 0 | yes | no | 360 | 3, 4 | 4 |
| 1 | 1 | no | no | 720 | 3 | none |
| 1 | 1 | yes | yes | 270 | none | none |

Thus 1,170 rectangles are scalar-shareable, and 900 admit a frame. The 270
remaining scalar-shareable rectangles have the previously known common-span
obstruction. **The initial hypothesis of additional infeasible scalar-shareable
rectangles after arbitrary frame completion was not supported on this domain.**
The additional restriction is on allowed frame dimensions, not on the total
number of scalar-shareable rectangles that can eventually be completed.

For an explicit example, take sources `7={0,1,2}`, `25={0,3,4}` and targets
`11={0,1,3}`, `19={0,1,4}`. The scalar matrix is all `-1`, and `E intersect T`
is zero. The nondegenerate frame with basis `(25,26,4)` separates the labels,
but its residual at source 7 is `{0,3,29,30}`: every vector has even weight.
Adding basis vector 32 gives a legal dimension-four frame. The checker
constructs orthonormal bases for its four residuals. This is a concrete
counterexample to **accepting a dimension-three frame from scalar exactness,
nondegeneracy and containment alone**, not a counterexample to a repository
theorem or to the current verifier.

## Cost decision and limits

The attempted local mechanism was a cheap nondegenerate completion of a
degenerate shared sum at dimension three. It fails an incident transfer
obligation even with all helper, scalar, restoration and recursive costs
optimistically set to zero. There is therefore no valid dimension-three
primitive in this class to price or feed to assembly. A legal dimension-four
completion is only a geometric witness. Turning it into a supplier requires
charging its source accesses, scalar gates, helper stock, frame transitions,
dirty compensation, inverse cleanup, recursive children, hosting and outer
assembly. None of those charges is claimed free here, and no helper-count,
paid-moment, runtime or exponent improvement is inferred.

The restrictions come from the *historical* orthonormal-residual interface in
`docs/research/parity-side.md`. This result does not restrict arbitrary
Clifford transport, mutable bases, multiple shared nodes, alternative labels,
copied/encoded carriers, or the current K492 supplier. It neither reopens the
rejected h=26 parity-DAG repair nor extends its negative result by more
computation. It changes the local search class to all completions of a fixed
small shared node. The dimension argument is a written proof; the census is
an exact finite exhaustive replay, not a formal proof of integer multiplication.

## Provenance, attribution and handoff

Intended base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected record
at orientation still names #626/#622/#623 with #543 and conditional
`kappa=51110230636731/31250000000000000`. The current review and certificate
were followed to the actual K492 construction and owner allocation; older
parity numbers were not treated as the selected frontier. See `SOURCES.json`
for exact source-head references and access limitations.

Credit Douglas Colkitt's preserved parity-side research for the signed kernel,
five-point common-span obstruction, characteristic-vector residual criterion
and rejected source-span repair. Related early complex compression by eumemic
(#3) is credited by the repository's contribution review. The selected-result
context credits Jeremy Kothe (#622/#623), Chafik Boukhalfa (#626), eumemic
(#543), DreamingOfClouds and Rohan Arun (#559), with the cumulative framework
retaining its original attribution. No code from those suppliers is copied.

Recent related PRs #681, #696 and #698 concern the K492 factory or its frames;
#651 and #683 concern face delivery. Their work informed scope selection but
is neither a dependency nor reproduced here. Browser-based overlap coverage
was limited; no exhaustive live-queue or priority claim is made.

Prepared for Arnav with substantial OpenAI Codex assistance in mathematical
analysis, implementation, verification and writing. Apache-2.0, matching the
repository. The two implementations are algorithmically independent, not
independent human peer reviews. The original OpenAI #109 framework and all
uniform, physical, precision, tape and analytic transfer obligations remain.

This environment could not clone/fetch Git objects or authenticate to GitHub.
The contribution is an addition-only patch on a local branch, intended for
the base above; it is not a full checkout or a submitted PR. `upstream/` and
the selected frontier are untouched. See `VALIDATION.md` for completed checks
and the repository-wide checks that could not be run.
