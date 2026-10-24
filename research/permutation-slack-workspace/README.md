# Dirty workspace from inversion-weighted permutation slack

A fixed formal word with arbitrary nonidentity permutation labels can be
restricted to at most

```text
active roles + floor((sum label inversions - endpoint crossing rank)
                     / smallest label inversion count).
```

This is a scoped all-field algebraic proof with exact finite corroboration.
The restriction preserves every original rank-one idempotent, paid label,
written order and full arbitrary-dirty-input endpoint. When every label has
the same inversion count d, the bound is `w+m-ceil(L/d)` total roles.
There is no new kappa or complete multiplication theorem.

This answers the first Open next question in Brian/JoyboyBrian's
[PR #4783](https://github.com/CrocSwap/integer-mult-bounds/pull/4783), read at
`c46cf15df53f3dad2ce59faec9cdc54184e643e5`. That predecessor proves the
simple adjacent S4 case and leaves non-simple labels open. Its local-charge
method, nested spectator splits and fixed-word sharpness mechanism retain
predecessor credit. The new step replaces one crossing by the complete
inversion-sized coordinate crossing space. Non-involutive labels use their
literal inverse when peeling. The theorem covers all symmetric groups and
all scalar fields.

## Exact boundary and result

Let F be any field, `R=A direct-sum S` a finite scalar role space, `dim A=w`,
and `n>=2`. A paid factor in `M_R(F[S_n])` is

```text
G_g(u,v) = I + ([g]-[e])uv,       vu=1,       g != e.
```

A nonempty normalized word has full formal endpoint `Q_A direct-sum I_S`.
The active block may be non-diagonal. Every spectator input is arbitrary
and must be restored; every off-diagonal formal coefficient is constrained.
Define `d_i=inv(g_i)`, `d_*=min d_i`, and `L` as the endpoint's crossing rank
in the ordered-distinct-pair representation, increasing pairs to decreasing
pairs. Then one spectator-only scalar basis change fixing A supports every
original factor on at most `w+floor((sum d_i-L)/d_*)` roles.

The [proof](PROOF.md) gives the exact crossing decomposition and four-case
local inequality

```text
d_i * (1[dirty image != 0] + 1[dirty functional != 0])
    <= d_i + phi(peeled residual) - phi(current residual).
```

Each right-hand side is nonnegative. Explicit nested splits and telescoping
prove the bound; full group-algebra intertwiners prove the retained endpoint.
The ordered-pair representation supplies a necessary geometric charge and
is never used as a full endpoint oracle.

The coefficient is sharp for preserving the given factors. A nonidentity
coordinate call followed by a canceling non-simple gate/inverse pair has
inversion slack `2d` and needs two dirty directions under the stated basis
restriction. Their nonzero image and functional have zero pairing, which
cannot happen on a one-dimensional retained dirty space. This says nothing
about the endpoint's minimum workspace after resynthesis: the pair cancels.

Identity labels can be removed first. The empty word needs no extra roles.
The inversion count is a geometric weight, not an asserted native-call tariff.

## Evidence and reproduction

Python 3.12 and the standard library suffice. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/permutation-slack-workspace
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/permutation-slack-workspace/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/permutation-slack-workspace/oracle.py
```

On another machine substitute its CPython 3.12 path. Normal replay writes
nothing. `verify.py --emit /absolute/new/path.json` explicitly generates a
receipt with every package source hash and the recomputed transcript. It
refuses an occupied output path. `--receipt /absolute/path.json` recomputes
and compares every receipt field. Default replay checks the mathematical
invariants directly; no generated output stays in the checkout. The source
hashes authenticate bytes, not mathematical truth or independent authorship.

The primary check covers 5,625 local peels. Every permutation label and
rank-one projector is enumerated within these six finite domains; active
maps are a declared deterministic sample of invertible maps on one active
role's ordered-pair space, not an exhaustive GL census.

| Permutations | Field | Total roles | Active maps per label/projector | Peels |
| --- | --- | ---: | ---: | ---: |
| S2 | F2 | 3 | 4 | 112 |
| S3 | F2 | 3 | 4 | 560 |
| S4 | F2 | 3 | 3 | 1,932 |
| S3 | F3 | 3 | 3 | 1,755 |
| S4 | F3 | 2 | 2 | 552 |
| S5 | F2 | 2 | 1 | 714 |

It also checks 576 literal crossing-space decompositions, four sharpness
words in the full formal algebra, 300 complete regular-action dirty-input
basis columns, and two constructive nested mixed-label compressions over
F2 and F3. The nested words reduce six roles to four by one computed scalar
basis, preserving every factor. Seven controls cover malformed permutations,
nilpotent couplings, unsupported fields, unreturned dirt, forward-for-inverse
substitution, unit crossing undercharge and the one-dimensional sharpness
boundary.

`oracle.py` imports no primary code. It enumerates actual 512-element binary
subspace sets and computes intersection dimensions from their cardinalities.
All 840 cases cover every S3 active permutation, every nonidentity paid S3
label and every rank-one idempotent on three scalar roles. All crossing
lengths 1,2,3 and dirty-component counts 0,1,2 occur. This checks the local
charge without matrix Gaussian elimination or the predicted decomposition.
Both registered normal and optimized modes use explicit runtime checks.

The written proof establishes the quantified theorem. These finite domains
do not establish an arbitrary-word exclusion or audit a predecessor result.

## Scope, sources and credit

Scientific base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133755).
The original card was `formal-interface-lemma`; this is a declared scope
change to an elementary quantified proof of an explicitly open interface
question. The selected source-binding positive control passed. The historical
card command `research_baseline.py` raises `KeyError: 'bit_lower'` against the
current selected certificate schema; neither command is a scientific replay.

`SOURCES.json` pins the catalogue, selected record and merged predecessor
notes as Git provenance. The pending #4783 is an exact external citation,
not an imported executable or a source-history dependency. The proof is
self-contained. No predecessor checker or finite receipt was replayed.

The live overlap helper at 22:17-22:18 UTC on October 22 covered 380 open PRs
and 3,860 Discussion records with complete pagination. Its local sparse scan
covered 69 of 6,319 main notes. Distinctive `git grep origin/main` searches
separately searched main README objects, and live merged/open PR searches
and this account's last-hour claims were checked. No matching non-simple
slack theorem was found in that coverage. Arbitrary diffs, unretained closed
work and unpublished investigations remain outside coverage. This is not a
novelty certificate.

Related open work is #4783, the simple-label slack theorem; #4847, the exact
scalar minimum for a supplied factor list under the same basis restriction;
and #4851, shortest S3 word rigidity. This contribution proves a geometric
slack inequality for a changed label alphabet. It does not extend the scalar
classification or shortest-word result and compares no predecessor numbers.

Credit Brian/JoyboyBrian #4783/#4765, Ross Richardson #1989/#1966,
Adam Gall #1941, Sagar Thakrar #3888, Arham Tahir #2998,
Nick Petalas #2583/#3408 and their retained register-model predecessors.
The elementary Grassmann distance and linear complement arguments are
standard; no literature-priority claim is made.

This contribution is produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Limits

This is a fixed-word formal reduction. Native realization, physical scalar
basis conversion, gauge restrictions, source access, ownership, hosting,
precision, tape and complete supplier/outer admission remain unknown here.
They are not zero-cost assumptions. No selected frontier changes.

## Open next questions

- Does a specified changed permutation-label target and paid budget make
  this finite-role bound materially reduce a necessary search? First give
  its full alphabet and endpoint crossing rank. A candidate with an actual
  physical allowance is missing; this package does not justify a large census.
- Can higher-rank scalar idempotents support a corresponding workspace
  charge? First derive their exact crossing subspace and split requirement.
  The rank-one image/functional argument does not establish that extension.

## Implementation bounds

Both Python files use explicit finite domains. Control flow is
nonrecursive, functions are below 60 lines, and all domains are explicitly
bounded: n<=5, at most six roles, prime fields 2,3,5 and at most 120 group
labels. The largest regular-action fixture is 120 by 120. The nested split
enumerates at most 3^5 scalar candidates; the independent oracle holds
512-element sets in an 18-dimensional binary space. Python and standard-library
allocations are bounded by these finite domains. There is no dynamic code
generation or external process. Registered normal and optimized replays
treat warnings as errors.
