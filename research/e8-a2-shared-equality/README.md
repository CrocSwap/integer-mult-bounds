# Exactly three A2 fibers share each rank-six equality support

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with an exact finite
certificate. For the full E8 leading-one root labels, every binary
rank-six support attaining the individual joint bound 32 for one 27-root
A2 fiber attains it for exactly three distinct fibers. A fourth distinct
fiber cannot attain 32 on that same support. Two distinct fibers share
at most one equality six-space.

There are 30,240 equality supports, each with three incidences. Every one
of the 3,360 fibers has exactly 54 compatible neighbors. The individual
bound, its 27 equality spaces per fiber and the E8 model remain credited
premises from PR3288 and its predecessors. This contribution answers the
separate simultaneous-equality opening, with a new three-projection proof
and complete cross-fiber incidence.

[PROOF.md](PROOF.md) gives the theorem, the exact hypotheses and a literal
16-root attainer. The primal enumeration constructs equality hyperplanes
inside fiber spans. The separate dual enumeration constructs singular
radical three-spaces and their affine cosets. They compare every support
and every incident fiber. They share the specified quadratic model, but
neither imports predecessor executable code. This is separate
combinatorial checking, not independent human review.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/e8-a2-shared-equality
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/e8-a2-shared-equality/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/e8-a2-shared-equality/verify.py
```

The registered replay runs both direct commands. Expected status is
`PASS_A2_SHARED_EQUALITY`, with 30,240 supports, multiplicity three and
54 neighbors per fiber. The complete canonical incidence SHA256 is
`be65d72f039eaf568a318133a63a07166d6cf29e1d1d0ee5254f57741f393b62`.
The optional `--receipt /absolute/path/outside/checkout.json` writes a
generated receipt bound to package and input hashes. Receipt files and
other run outputs belong outside the checkout.

The dual enumeration covers 7,560 radical three-spaces, 30,240 affine
cosets and every zero-projection exclusion. The primary checker also
checks the explicit simple-root transport at all 256 points, the witness
rank, a genuine balanced hyperplane containing its omitted singleton
whose joint score is 31, and four invalid binary domains. Explicit
exceptions preserve these checks under optimized Python.

## Scope and source status

The individual-fiber results are cited dependencies, not this deliverable's
audit targets. [SOURCES.json](SOURCES.json) pins their proof and the exact
simple-root convention. These inputs are authenticated as bytes, without
executing their verifiers. Historical catalogue and selected-result pins
are provenance. No unmerged source commit or network is needed at replay.

This full-E8 theorem supplies no new P112 threshold, pairwise-clique
classification, actual decoder or physical caller, native program,
restoration implementation, paid moment, kappa or selected-frontier change.
The five selected framework assumptions remain. Predecessor scientific
replays, selected cold replay, Lean and Docker were not run. Independent
human and formal proof-kernel review are unclaimed.

This is a changed `complex-rank-shape-decoder` card and a scoped
support-geometry side result. A real caller must specify its fibers and
show that they require saturation on one common support before this
obstruction can affect its budget. A finite compatibility improvement
does not authorize a further construction campaign.

## Implementation bounds

All mathematical domains are fixed subsets of F2^8 or F2^9. The primal
loops through 3,360 fibers and at most 127 hyperplanes of each. It retains
30,240 support keys, 90,720 incidences and at most 90,720 compatibility
pairs. The dual loops through at most 255 radical candidates and 1,120
normal planes, then eight cosets for each of 7,560 three-spaces. Every
point scan has 256 iterations. Basis construction has at most 512 input
vectors and nine pivots. There is no recursion, subprocess, network,
dynamic code evaluation or unbounded input search.

Power of Ten rule 3 deviation: CPython allocates integers, tuples and
dictionaries during these bounded finite enumerations. The fixed domains
bound collection sizes; this is not a fixed-allocation implementation or
a certified Python allocator bound. All functions are below sixty lines.
Warning-strict normal and optimized execution are the available local
diagnostics. No separately installed linter or formal proof checker is
claimed.

## Open next questions

- Which pairwise-compatible triples actually share an equality space?
  Start with the explicit compatibility graph and the support triples.
  No clique classification is provided here.
- Does a named current decoder or caller require four distinct fibers to
  attain their individual maxima on the same rank-six support? First bind
  its literal support and complete paid invoice. No such caller is supplied.

Discovery stopped at the first verified simultaneous-compatibility result.

## Credit and coordination

Credit Nick Petalas / PR3288, PR3280 and PR3262, David Arias's quadratic
model, DreamingOfClouds / PR3154, joaqcoo and the retained E8/P112 lineage.
Quadratic restriction and binary symplectic linear algebra are classical.
No global literature-priority claim is made. PR3302 concerns outside-span
capacity 30 and supplies no simultaneous equality result used here.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371205)
states the delivered question. Base main is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision eight,
selected PR6030. The overlap snapshot covered 522 open PRs, 6,536
Discussion records and all 8,917 tracked local notes. Main/merged object
and general-form searches, account history and current reservations were
also checked. Arbitrary historical diffs and unpublished work remain
coverage limits. Metadata and archive retention do not imply scientific
acceptance or a selected-frontier update.
