# Classify every optimal second callee in the ordinary wrapper

This contribution is produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite corroboration.
For every invertible linear first map P over every field, this package
classifies all second maps Q attaining the fixed ordinary wrapper's known
minimum error rank. The new condition is a square-zero endomorphism on
V/ker(P^2-I), with an explicit invertibility filter on Q.

Write A=P^2-I and R=Q-P. Choose any G satisfying A G A=A. Then an invertible
Q is optimal exactly when

    im R is contained in im A,
    ker A is contained in ker R,
    R G R=0.

When the two containments hold, the condition is independent of G.
[PROOF.md](PROOF.md) proves necessity and sufficiency, including singular A,
noncommuting maps and every field characteristic.

For P=lambda I over F_q with lambda nonzero and lambda^2 different from 1,
all optimal second maps are lambda I+R with R^2=0. Their exact number is

    sum_(r=0)^floor(n/2) [n choose r]_q [n-r choose r]_q |GL_r(F_q)|.

The r-th summand counts rank(Q-P)=r. At n=2 there are exactly q^2 attainers.
For P=2I over F5 there are 25, including Q=[[2,1],[0,2]]. Each agrees
with interchange on 25 of 625 input pairs. Optimal agreement does not imply
exact interchange. For an involutory P, the unique optimal Q is P itself.

## Relation to predecessor work

Jerry Chen / CubeJerry's merged [PR2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950)
already proves the optimal error-image/agreement value and supplies Q=P as
one attainer. That theorem is a cited premise, not an audit deliverable.
This package adds its complete linear equality classification and the scalar
finite-field count. No predecessor executable or census is imported or replayed.
The rank-equality and square-zero flag-counting techniques are standard linear
algebra; no priority over those techniques is claimed.

Nick Petalas / PR2808 and PR2786, David Arias / PR2753 and Jose Manuel /
PR2697/2899 retain the ordinary-wrapper, padding and stream lineage credit.
Wentao Li / PR4053, PR4063 and PR4070 studies paid normalization and reciprocal
weighted pairs. Those are different questions from the attaining set at the
unchanged two-callee boundary. Their package files and credit lines are untouched.
The predecessor README is pinned as historical provenance in SOURCES.json.

## Reproduce

From the repository root with CPython 3.12 and standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/optimal-second-callees
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/optimal-second-callees/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/optimal-second-callees/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/optimal-second-callees --check-source-history
```

Any CPython 3.12 interpreter path may replace the local path. The direct
marker is `PASS_OPTIMAL_SECOND_CALLEES no_new_kappa`. Normal execution
writes nothing. It prints a generated receipt binding the enumerated results
to SHA256 hashes of all six package files. No receipt is hand-written.

The verifier checks the new equality criterion against literal six-operation
execution on every basis column in its declared complete invertible-map
pair domains. It separately enumerates arbitrary A,R and every inner inverse
in two small fields, and square-zero matrices by rank. These are finite
corroborations of the written theorem, not all-field computational proofs.
Six control groups distinguish different optimal maps, omitted image/kernel
conditions, a non-square-zero perturbation, singular candidate Q and the
involutory boundary. Explicit exceptions retain checks under Python -O.

The finite domains contain 258,624 ordered invertible wrapper-map pairs,
6,817 arbitrary two-by-two A,R pairs, 1,087 inner inverses across all A in
the two declared fields, and 88,871 matrices for square-zero rank counts.
The wrapper domains are all P,Q in GL_3(F2) and GL_2(F5). The receipt lists
each domain and every observed count separately.

## Scope and limits

This is an algebraic side result. The `uniform-transfer-audit` card is
explicitly changed from auditing #4100 to a new equality statement at PR2950's
fixed wrapper interface. The source-bound selected-baseline orientation
passed; the selected construction itself was not replayed. Canonical base
is ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c, priority revision 7.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19146072)
records the question and bounded method. Live PRs, active Discussions, recent
account posts, local reservations, cached overlap, main READMEs and merged
PR terms were checked. Sparse notes and unpublished work limit that coverage.
TASK.json records the exact scope change and SOURCES.json pins provenance.

General finite abelian groups, nonlinear callees and changed surrounding
operations are outside scope. No attaining callee's physical implementation,
normalization, frames, restoration, hosting, tape, precision or recursive bill
is supplied. No supplier, new kappa, selected-frontier change or complete
multiplication theorem is claimed. Independent human and formal proof-kernel
review are unclaimed. Lean, Docker and the selected cold replay are unrun.

The checker has fixed prime-field domains and at most four logical coordinates.
Assembled error matrices have at most six rows and six columns.
Its loops have finite enumeration bounds, it has no recursion or dynamic
imports, and functions fit within 60 lines. Python allocation is dynamic;
the fixed matrix domains bound live storage rather than implementing fixed
allocation. The largest stored invertible group has 480 matrices, and every
individual enumerator visits at most 65,536 matrices. Warning-strict normal
and optimized execution supply interpreter diagnostics. This is not a
whole-repository static-analysis or proof-kernel pass.

## Open next questions

- Count the invertibility-filtered square-zero quotient maps for nonscalar P
  from its rational canonical data. Begin with one nonsemisimple block and
  retain every singular-Q rejection. The present theorem gives the exact
  set but no general closed form for that filtered count.
- Find an actual weighted caller with a less expensive second callee among
  the classified maps. First pin its first map, required correctness domain
  and complete paid invoice. No physical caller or cost advantage is supplied.

Structured questions, relevance and blockers are in TASK.json.
