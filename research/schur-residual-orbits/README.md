# Seven residual Schur-pair states and their full-guard counts

**Exact finite classification and counting, with a written multiplicity
argument. No new kappa.** Prepared by Mihir Srivastava with substantial
OpenAI Codex assistance, by one agent. Apache-2.0.

This answers one bounded instance of the residual-state handoff in
[ssafwann's PR4678](https://github.com/CrocSwap/integer-mult-bounds/pull/4678),
continuing the orbit question in Nick Petalas's PR4597. For the binary
commuting projector pair with joint-sector dimensions **(1,1,1,2)**, exactly
**seven ordered simultaneous-conjugacy classes** occur after a common scalar
pivot. Their complete-header weights are not uniform. The census yields
**93,564 full-guard headers out of 9,999,360**, a fraction **2599/277760**.

The sharp first-step event from PR4678 occupies just one residual class:
its **60,480** headers produce **5,040** distinct coordinate pairs, each
exactly **12** times. Only **3,240** of those headers pass the full guard
chain, a conditional fraction **3/56**. The 60,480 one-block count is credited
corroboration; its orbit classification and continuation count are the new
quantities here. Commutator rank alone cannot determine the continuation law.

## Fixed sample space and guards

Work over F2 and fix, before choosing the header,

```text
P0 = diag(0,1,0,1,1),  Q0 = diag(0,0,1,1,1).
```

The axes have joint sectors 00,10,01,11,11. Both projectors have rank three.
Choose a complete ordered header M uniformly from GL5(F2) and set
`P=M^-1 P0 M`, `Q=M^-1 Q0 M`. A full guard means that **both** leading
principal minors of each order 1,2,3 are nonzero. Orders 4 and 5 are not
required, since the requests have rank three. This is equivalent to three
successive nonzero scalar pivots without row exchanges. Using `G=M^-1`
gives the earlier `G P0 G^-1` convention and the same uniform sample space.

Conditional on P[0,0]=Q[0,0]=1, write the Schur complements S,T, of size four.
They are rank-two idempotents. States are orbits of the **ordered** pair
`(S,T)` under `(S,T) -> (K^-1 S K, K^-1 T K)` for K in GL4(F2).
Swapping the requests or transposing them is not part of this equivalence.

The same result holds for any fixed commuting binary idempotent pair with
these four sector dimensions: simultaneous diagonalization sends it to this
pair, and the fixed basis change permutes the complete-header sample space.
No claim is made for a different sector profile, field or restricted cover.

## State table

Every representative below has `S=(0,0,4,8)`. Matrices are encoded as integer
**rows**, with bit j representing column j, least significant bit first.
For example `(0,4,4,9)` has rows `0000`, `0010`, `0010`, `1001` when
columns are printed in increasing index order. The representatives minimize
the ordered tuple of all S rows followed by all T rows within each orbit.

Here b counts admitted split pairs reaching the state, o is its orbit size,
z its stabilizer size, and f counts orbit elements whose two remaining
guards both pass. Thus `o*z=20160`, header weight is `b*20160`, and the
full-guard contribution is `b*z*f`.

| State | T rows | rank [S,T] | b | o | z | f | Header weight | Full guards |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | (0,0,4,8) | 0 | 1 | 560 | 36 | 100 | 20,160 | 3,600 |
| 2 | (0,0,4,9) | 1 | 3 | 5,040 | 4 | 468 | 60,480 | 5,616 |
| 3 | (0,2,0,8) | 0 | 126 | 20,160 | 1 | 366 | 2,540,160 | 46,116 |
| 4 | (0,2,2,8) | 1 | 18 | 20,160 | 1 | 816 | 362,880 | 14,688 |
| 5 | (0,4,4,8) | 1 | 3 | 5,040 | 4 | 468 | 60,480 | 5,616 |
| 6 | (0,4,4,9) | 2 | 3 | 5,040 | 4 | 270 | 60,480 | 3,240 |
| 7 | (0,6,0,8) | 1 | 18 | 20,160 | 1 | 816 | 362,880 | 14,688 |
| Total | | | 172 | | | | 3,467,520 | 93,564 |

[RESULT.json](RESULT.json) includes every one of the 172 admitted split pairs,
their state assignments, and the exact guard-depth distributions within
each orbit. The total header denominator is `496*20160=9999360`.

The sharp state 6 has split pairs `(15,23)`, `(23,15)`, `(31,31)` in the
fixed five-axis basis. Its fraction among all first-guard headers is 3/172,
as in PR4678; it is 3/496 among all headers. Its later full-guard fraction
is 270/5040=3/56, giving 3*4*270=3240 headers.

Two tiny complete-header witnesses use the same integer-row convention in
dimension five. `M=(17,9,11,5,18)` has sharp first Schur commutator and
passes all three leading minors for both requests. `M=(23,3,5,9,16)` also
has sharp first Schur commutator, but fails the next common guard.
RESULT.json includes a passing and a first-guard-only header for every state.

Two explicit losses of information are useful for future recursion design:

- States 1 and 3 both have commutator rank zero, but their conditional
  full-guard fractions are respectively **5/28** and **61/3360**.
  States with commutator rank one also have unequal continuation fractions.
- States 2 and 5 have the same ranks of S, T, ST, TS, S+T and [S,T].
  They are still different orbits: `dim(ker S intersect ker T)` is one
  for state 2 and two for state 5. Their continuation fractions happen to
  agree. This witness refutes identification of those states by the listed
  ranks; it does not claim that their guard counts differ.

## Why the finite census counts complete headers exactly

**Split pair and completion.** Let a be the first column of M and b the first
row of M^-1. Then ba=1. Conversely every pair with ba=1 extends to exactly
`|GL4(F2)|` headers: append an arbitrary ordered basis of ker b to a.
There are 31 choices of nonzero a and 16 choices of b with ba=1, hence 496
split pairs. This is the credited equal-completion argument in PR4678 and
the preceding Petalas header work. No extra factor of 16 is applied after
the split pair has already been chosen.

The verifier constructs one deterministic kernel basis for each split pair,
inverts the resulting header, and checks the two scalar pivots literally.
Exactly 172 split pairs pass. For any fixed one of them, all other completions
are uniquely `M diag(1,K)` with K in GL4. Block substitution gives

```text
Schur(diag(1,K)^-1 P diag(1,K)) = K^-1 Schur(P) K.
```

Therefore a split pair contributes exactly one entire simultaneous orbit,
with each orbit element reached z times. Split pairs whose seed lies in
the same orbit have identical completion distributions. Summing their b
fibres gives the table's `b*z` multiplicity per orbit element.

**Residual ranks.** In characteristic two, write
`P=[[1,R],[C,D]]`, so `S=D+CR`. Idempotency gives RC=0, RD=0, DC=0 and
D^2+CR=D. Hence S^2=S; block elimination gives `rank(P)=1+rank(S)`.
The same applies to Q. Thus both residual ranks are two, and exactly two
further scalar guards are required. The determinant identity
`det(P[:j+1,:j+1])=det(S[:j,:j])` at the first unit pivot proves equivalence
with the original orders 2 and 3. Repeating it justifies the guard-depth test.

**Completeness of classification.** The independent-row generator visits
each ordered basis of F2^4 exactly once: at each level it extends by every
row outside the current span. Its size is `(16-1)(16-2)(16-4)(16-8)=20160`.
For each uncovered seed, the checker explicitly generates its entire orbit,
checks uniform fibre size and orbit-stabilizer equality, and verifies that
it is disjoint from all previously constructed orbits. Every admitted split
pair is assigned. This exhausts the stated finite domain, yielding seven
classes; it is not a random search or an extrapolated general classification.

For an additional direct check, choose one split pair in each of the seven
classes and form **all 20,160 complete five-dimensional headers** in its
completion fibre. Invert and conjugate the original P0,Q0 and evaluate their
leading minors using the Leibniz determinant formula, without Schur
elimination. All **141,120** direct header cases reproduce the per-class
continuation counts. Applying those counts to the other split pairs uses
the proved orbit-equivariance argument. This is not a raw enumeration of
all 9,999,360 headers.

## Reproduce and evidence boundaries

Python 3.12 standard library; no pending executable or external input needed:

```sh
python3.12 -B scripts/research_package.py --package research/schur-residual-orbits
python3.12 -B scripts/check_research_commit.py --package research/schur-residual-orbits --check-source-history
```

The registered normal and optimized (`-O`) modes use explicit exceptions and
compare every scientific field with RESULT.json. Direct Git-free replay is
`python3.12 -I -W error -O -B verify.py` from an exported package. The only
writing mode is explicit `verify.py --write`, which regenerates RESULT.json.

Verification covers all 496 split pairs, full GL4 orbits for all seven
classes, and the 141,120 literal complete headers above. A separately
enumerated raw domain of all **65,536** four-by-four binary matrices uses
the Leibniz determinant to check that the generated GL4 set is exact.
Seven rejection controls distinguish a singular header, a nonsplit pair,
a zero pivot, omission of the completion multiplier, replacing the full
guard with the first guard, collapsing states by commutator rank, and
collapsing the distinct same-rank states 2 and 5.

This is author-checked exact finite evidence plus the written reduction;
independent human or proof-kernel acceptance is not claimed. No Lean, Docker,
selected scientific cold replay, large-d classification or physical caller
replay is part of this package. Hosted CI is reported separately in the PR.

The counted binary shared-header event is an algebraic model. As explained
in the credited projector-header notes, the retained normalizer's executable
domain uses odd q; this F2 census is not an admission check for that caller.
Header selection/emission, physical reads, dirty restoration, owned storage,
stock, dispatch and the full consumer bill remain unpriced. No cost is
implicitly zero and no selected-frontier change follows from these counts.

## Scope, overlap and credit

This starts from canonical main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`,
priority revision 7, selected conditional kappa 0.00302015. It takes the fresh
PR4678 handoff in [Discussion4653](https://github.com/CrocSwap/integer-mult-bounds/discussions/4653#discussioncomment-19126925).
The `formal-interface-lemma` card is marked **changed** to this algebraic
side result. The first working object is the handoff's explicit n=5 profile;
the stale balanced-transfer baseline is not used. The family decision is
**narrow** to one state distribution and its continuation law, with no
automatic construction or adjacent-profile census.

TASK.json records overlap coverage and exact citation pins. At entry, 449
open PR bodies and 3,608 Discussion records were refreshed. Before submission,
coverage was expanded to all 5,860 tracked in-scope local notes, 453 open PR
bodies (15:59 UTC) and 3,614 Discussion records (16:00 UTC), with no coverage
warnings. Main was refreshed unchanged. Remote closed PR bodies, arbitrary
code diffs, nested source notes and unpublished work remain coverage limits.
PR4678 counts one block for general profiles; this contribution classifies
the subsequent ordered states and counts the remaining guards for one
profile. The earlier full-guard census covers other named families, not
this seven-state distribution. No priority over unknown work is asserted.

Predecessor credit is retained explicitly:

- **ssafwann, PR4678**, head `af9cf805c501e4e9e947c98c0b97b2281b6b6e97`,
  `research/schur-header-count/README.md`, blob
  `5e644cf316312c0fdd489c8d33911583f1b88af2`: the exact one-block count,
  this profile, completion-fibre argument and residual-state handoff;
  substantial OpenAI Codex assistance. PR4671 supplies its sector criterion.
- **Nick Petalas, PR4597**, head `dfeb8ca729a04aea4aa290438f2ed50a37a9c7cb`:
  block-Schur commutator factorization and orbit question. His retained
  PR4278 scalar Schur proof and earlier PR4259/4246/4228 header work supply
  the commutator and equal-completion lineage. The local scalar note is
  provenance-pinned in SOURCES.json; none of its code is imported.
- **Ryanson Jonathan**, the retained `full-guard-header-census`, with
  substantial Claude Code (Claude Opus 5.5) assistance: literal leading-minor
  guard convention and separate-family census. PR4609/4617 and **lee-phys's
  PR4634** retain their binary sharpness and dimension contributions.
- **Cinna Davis**, PR4100's BIT request context, and the earlier normalizer
  lineage credited there (source527, commdata2338 and Jose Manuel).

The source-bound tooling retains its existing contributors' attribution.
The pending PRs are citations, not runtime or provenance dependencies that
would require unpublished Git ancestry. All new files are Apache-2.0.

## Open next questions

Can an invariant-based transition rule recover these seven states and their
continuation counts without enumerating GL4? That would turn this exact
finite table into a useful test fixture for a scalable state-aware header
recursion. Start by deriving the stabilizers of the seven displayed pairs
and the next-pivot transitions using their image/kernel decompositions.
The blocker is a proved sufficient state invariant and its transition
multiplicities; commutator rank and the listed product/sum ranks are
insufficient for orbit identity. Larger fields/profiles and an actual
production header cover require a separate scope and cost allowance.
No follow-up claim is held by this package.
