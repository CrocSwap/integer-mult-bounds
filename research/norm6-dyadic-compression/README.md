# Norm-six decoder: at most 19,600 dyadic terms

**Scoped algebraic existence proof.** Cinna Davis's norm-six kernel admits
at most **19,600 dyadic factor pairs**, reducing the previous explicit upper
bound of 19,648 by 48. Its algebraic separate-copy support bill is therefore
at most **960,400**, improving the previous bound 962,752 by **2,352**.
No physical invoice or new kappa follows.

This contribution is produced by Nick Petalas. The new step is the dyadic
compression corollary below. The kernel, binary chart, rational rank bound and
integer-column factorization lemma are credited predecessors.

## Proof

Put D = Z[1/2]. Let X be the finite set of minimum-vector line representatives
in the 48-dimensional integral norm-six lattice used in
[Cinna Davis's PR2222](https://github.com/CrocSwap/integer-mult-bounds/pull/2222).
Write

    M[x,y] = ((x dot y)^3 - 4(x dot y))/192.

Take the source kernel and its norm-one binary labels in F2^49 as premises.
For every integer t, t^3-t is divisible by 3, so t^3-4t is also divisible
by 3. Consequently every entry of M belongs to D. This is the scalar
integrality behind PR2222's explicit 19,648-term factorization.

The rational rank bound is already in PR2222's PROOF.md and in
[DreamingOfClouds's PR2244](https://github.com/CrocSwap/integer-mult-bounds/pull/2244).
Here is its short coordinate-free form, to identify precisely the premise
being used. For fixed y, M[x,y] is an odd polynomial in x of degrees three
and one. On x dot x = 6, every linear coordinate is a rational combination
of cubic coordinates, since

    x_i = (1/6) x_i (x dot x).

Thus the columns of M lie in the evaluation image of homogeneous cubics
in 48 rational coordinates. That vector space has dimension

    C(48+2,3) = 19,600.

The same argument in integral lattice coordinates uses the Gram quadratic
form instead of a sum of coordinate squares. No full-shell enumeration,
independence of these evaluations, or exact rank of M is asserted.

**Dyadic compression lemma (existing).** Every finite matrix A over D of
rational rank r has A = UV with U over D of width r and V over Z of
height r. Dugongue's
[dyadic block compiler proof](../dyadic-block-compiler/PROOF.md), Theorem 1,
already proves this by classical unimodular integer column reduction.
For completeness, clear denominators by 2^b and choose a unimodular integer
matrix E with (2^b A)E = [H 0], where H has r columns. Then

    U = H/2^b,       V = first r rows of E^-1.

Both factors have the required coefficients, and UV=A. This is not a new
normal-form lemma. In particular no arbitrary rational pivot is assumed to
be dyadic: [[3,1],[6,2]] has the naive factor [3,6]^T [1,1/3], but also
the legal factor [1,2]^T [3,1].

Apply the lemma to the entire finite matrix M. Its dyadic factors have
r <= 19,600 columns/rows. Reading their entries as source and target
functions on X gives the claimed number of factor pairs. They reproduce
the same kernel, including every diagonal and forbidden zero. Zero terms
can be omitted; neither minimality nor equality of the full-shell rank
is needed.

Finally, the predecessor's binary pairing matrix is a dot-product matrix
of labels in F2^49. Every support submatrix has binary rank at most 49,
even after changing all factor supports. Summing over the at most 19,600
new terms gives

    algebraic separate-copy bill <= 49 * 19,600 = 960,400.
    previous bound minus new bound = 49 * 48 = 2,352.

This is a bound on the pairing-rank sum. It does not identify any recursive
child rank, frame itinerary, source preparation algorithm or scalar tariff.
The rational observation alone did not supply dyadic coefficients; applying
the existing integer-column lemma supplies that missing existence step.

## Evidence and reproduction

The proof above applies to the full finite kernel, conditional on the
predecessor geometry. The new verifier does not replay that geometry or
its 48-dimensional minimum-shell claims. It corroborates the compression
step on the complete integer norm-six shells in dimensions three and four
and on 120 additional bounded dyadic matrices. Integer column reduction
and separate Fraction Gaussian elimination check every product entry and
rank. It also enumerates the 19,600 cubic indices and the predecessor
term-count formula. Seven failure controls cover non-dyadic input,
shape/capacity, a wrong kernel coefficient, normalization and factor damage.
These small Euclidean shells are diagnostic fixtures, not the P48p shell.

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/norm6-dyadic-compression/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/norm6-dyadic-compression/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/norm6-dyadic-compression
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/norm6-dyadic-compression --check-source-history
```

Any CPython 3.12 path may replace the displayed path. The direct verifier
writes nothing and emits a generated JSON receipt with hashes of its package
files. Both registered commands retain every check under optimization.
SOURCES.json pins predecessor proof text as historical provenance; no
predecessor executable is imported or audited.

## Limits and expansion decision

The result is an existence upper bound. No 26,208,000-port factor table is
materialized, and no efficient or small-coefficient representation of the
new functions is supplied. The term count is not proved minimal. The
48-dimensional shell minimum and cardinality remain the cited Nebe/Sloane
and Nebe dependencies of PR2222. The proof itself only requires a finite
integral norm-six shell and the stated binary chart.

The standalone diagnostic implementation is deliberately bounded to at most
64 rows/columns. It cannot generate the full-shell factors. Classical finite
integer reduction supplies existence at that size without a useful complexity
or coefficient bound here. The small-shell runs do not establish such a bound.

Retain this algebraic improvement and stop. Physical preparation, legal source
access, I-M, dirty restoration, frames, owners, precision, tape, supplier
compilation, a matched bit supplier and all outer obligations are unknown.
Unknown costs are not zero. No selected cold replay, native build, Lean build,
independent human review or formal proof-kernel review is claimed. The selected
frontier is unchanged. This does not meet the historical card's five-percent
fully priced supplier gate; TASK.json records the changed scope.

## Open next questions

- Can the 48 norm-shell relations compress the symbolic features over D
  without full-shell enumeration? Start by finding a saturated relation-module
  basis with explicit coefficient bounds. Efficient evaluation of the new
  features is the missing obligation.
- Can a complete chronological physical side program use this bound?
  First specify one source/target contract and charge preparation, frames,
  restoration, ownership and precision. A favorable algebraic rank sum cannot
  replace those unknown costs or supplier admission.

## Credit and overlap

Cinna Davis / PR2222 supplies the kernel, dyadic integrality, original 19,648
pairs and the 49-bit chart. DreamingOfClouds / PR2244 supplies the corrected
rational rank perspective, also already recorded in PR2222's proof.
Dugongue's [PR4494](https://github.com/CrocSwap/integer-mult-bounds/pull/4494)
dyadic block compiler supplies the rank-factorization lemma and
classical integer-reduction method. Nebe/Sloane supply the lattice data and
Nebe the published minimum-shell theorem. Retain Dominik Scholz, David Ryan,
the Leech/PR598 and Niemeier investigations and their credited predecessors.
No new general linear-algebra or literature-priority claim is made.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19141424)
records the new application. Entry overlap covered live open titles and
relevant bodies, recent account PRs, handoffs, active Discussions, distinctive
main-README terms and merged searches. The helper reported 330 open PRs and
4,195 Discussion records with complete remote pagination; sparse local notes,
arbitrary diffs and unpublished work remain incomplete. No matching new
compression bound appeared in that coverage. No open PR on this norm-six
quantity was found. TASK.json records the scientific base and limitations.

New proof and code: Apache-2.0. Independent human and formal proof-kernel
review are unclaimed.

## Verifier implementation bounds

The call graph is nonrecursive. Matrix inputs are capped at 64 rows/columns,
64 numerator bits and 16 denominator bits. The fixed shell loops use at most
5^4 candidate vectors; index enumeration uses at most C(50,3) iterations.
Each Euclidean loop has an explicit 2B+3 bound for its B-bit initial pair.
Matrix loops are bounded by the validated dimensions. All assertions are
explicit ValueError checks and remain active under -O. Every function is
shorter than 60 lines.

Rational row reduction is only preconditioning: if M=A C with A the selected
original columns, clear C's denominators and reduce its integer column lattice.
The resulting U columns are integer combinations of M's columns, hence dyadic,
even when the preconditioner C has an odd denominator. The verifier checks this
and every final product. The 48-port fixture exercises that odd-denominator
case; no intermediate rational coefficient is billed as a native operation.

Power-of-Ten rule 3 deviation: Python exact integers and Fraction objects
allocate during this finite offline diagnostic. Live matrix storage is bounded
by O(64^2) scalar slots, with integer bit growth bounded by the finite operations
on capped inputs. No fixed byte or practical general bit-complexity bound is
claimed. The fixed registered fixtures and 120-second process timeout bound
execution operationally. A production implementation would require explicit
coefficient/storage bounds before use; this verifier is not that implementation.
Warning-strict normal/optimized execution supplies the available Python runtime
diagnostics; no separate static type-checker or formal kernel acceptance is
claimed. There is no dynamic code generation, callback dispatch or writable
shared state.
