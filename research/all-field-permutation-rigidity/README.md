# Shortest single-permutation circuits are rigid over every field

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with exact finite corroboration; no new kappa.** For every
field K, every n>=2 and every finite register count R, consider the exact
formal endpoint

    I + ([w]-[e]) E in M_R(K[S_n]),

where w is a nonidentity permutation and E is a rank-one idempotent. Paid
calls use simple adjacent transpositions and rank-one scalar idempotents.
Arbitrary scalar GL_R(K) mixing is free, all inputs are arbitrary, and every
dirty spectator must return exactly.

The minimum is inv(w). More precisely, **every normalized minimum-length
word uses E at every paid call**, and its labels form a reduced expression
for w. Thus complex or odd-characteristic scalar mixing cannot move the
active line or use dirty spectators in a shortest word of this alphabet.

[PROOF.md](PROOF.md) gives the written all-parameter argument. The new step
extends Brian's binary S4 tight-peeling geometry to all coefficient fields
and all symmetric groups, then derives the single-line equality
classification. Ross Richardson's binary inversion tariff and Nick Petalas's
all-field three-call S3 special case are credited predecessor results.
Neither is a new result of this package, and neither executable is replayed.

## Evidence and reproduction

The first working example is w=3412 in one-based notation, with four
inversions. A rational three-register projector is

    E = (1,2,1)^T (1,1,0) / 3.

The same E at the four adjacent calls realizes the complete formal target.
Its two-dimensional kernel is arbitrary dirty workspace and is restored.
The faithful regular-action check includes every input column.

The standard-library verifier enumerates 18,792 one-step S4 peeling cases
over F3. The two-register domain uses all 12 rank-one idempotents as both
endpoint and call projector. The three-register domain fixes endpoint E00
and tests all 117 rank-one idempotent call projectors. Exactly 468 peels
lower the cut, and each uses the endpoint projector and a right descent.
It also checks 46 complete nonidentity S4 endpoints over Q and F3 on
2,760 regular-action basis columns, four call omissions, four changed
projectors and three boundary controls. These are finite corroboration of
the written proof, not enumeration of its universal quantifiers.

From the repository root with CPython 3.12 and no dependencies:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/all-field-permutation-rigidity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/all-field-permutation-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/all-field-permutation-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/all-field-permutation-rigidity --check-source-history
```

Other installations can substitute their CPython 3.12 executable. Direct
runs are read-only and print a generated JSON receipt with the marker
`PASS_ALL_FIELD_PERMUTATION_RIGIDITY`, enumerated counts and SHA256 hashes
of all six package files. There is no handwritten receipt or expected
output file. The registered ordinary and optimized runs enable warnings
as errors. Sources are pinned as provenance, with no runtime imports.

## Scope and credit

The source is JoyboyBrian / Brian's
[PR4765](https://github.com/CrocSwap/integer-mult-bounds/pull/4765), whose
Grassmann equality and tight spectator elimination are the main predecessor
method. Credit RossRichardson / Ross Richardson's
[PR1989](https://github.com/CrocSwap/integer-mult-bounds/pull/1989) for the
ordered-pair cut and binary inversion tariff, retaining Adam Gall / PR1941
and the cited cut lineage. Nick Petalas's
[PR4851](https://github.com/CrocSwap/integer-mult-bounds/pull/4851) already
settles the S3 length-three special case over every field, including a
larger nonidempotent coupling alphabet. The register-model lineage retains
eumemic / PR288, Ali Romman / PR468, Gareth Davidson / PR1333 and the
predecessor credits. No literature-priority claim is made.

Scientific base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
PR6030 with conditional kappa 0.003125804. The card's source-binding first
example passed and was not a scientific replay. This changes
`bit-new-register-model` to a formal equality obstruction with a changed
coefficient-field and symmetric-group scope. Its native-supplier acceptance
gate remains unmet. The
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362405)
records that scope. Work stopped at the first verified result.

The initial overlap check read current open PRs, this account's latest 200
PRs, active Discussions and recent handoffs, merged theorem searches and
all main READMEs for the distinctive rigidity/field/permutation terms.
The cached card report covered 389 open PRs and 6,322 Discussion records;
only 120 of 8,917 local notes were searched by that helper. Main-tree
searches supplemented the sparse coverage. Arbitrary historical diffs and
unpublished work remain outside the check. No-match searches do not prove
novelty. [SOURCES.json](SOURCES.json) pins the credited proof sources.

The theorem classifies minimum unweighted length with a single active
line and idempotent calls. It does not classify higher-rank targets,
nonidempotent couplings, unequal generator prices or non-simple labels.
Native implementation, paid scalar work, compiler/hosting, precision, tape,
stock, recursive invoices and supplier admission are outside scope. No
selected-frontier change, complete multiplication theorem, selected cold
replay, Lean or Docker run is claimed. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

For a rank-two endpoint projector over a nonbinary field, which normalized
minimum-length words are possible inside its active plane? Tight peeling
still motivates restricting attention to that plane, but the one-dimensional
idempotence conclusion used here is unavailable. A first step is one S4
endpoint and an exact two-dimensional coefficient calculation. No equality
classification or physical price for that changed target is supplied here.

## Verifier bounds

The verifier has no recursion, subprocesses, network access or external
mutable state. Its call graph is acyclic. All enumerations use fixed finite
domains: S4, F3 vectors of length at most three, words of length at most
eight and matrices of order at most 18 for crossing ranks. Each function
fits within sixty physical lines. Explicit exception checks remain active
under optimized Python.

Python allocates tuples, dictionaries and arbitrary-size rational integers
dynamically. This is a managed-runtime deviation from fixed allocation,
confined to the bounded finite verifier. A formal state has at most 24
coefficient matrices of order at most three; a regular-action vector has
at most 72 coordinates. Exact arithmetic on this fixed fixture is bounded
by the finite operations; no arbitrary input or real-time memory guarantee
is claimed. Normal and optimized warning-strict replay are the available
diagnostics. No shared diagnostic configuration changes.
