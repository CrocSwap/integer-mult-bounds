# Four pure shear stages cannot improve the three-stage swap tariff

This contribution was produced by Nick Petalas. Apache-2.0.

For two arbitrary K-coordinate data banks over any field, the exact minimum
rank charge of a complete swap using at most four one-direction shear stages
is 3K. Arbitrary invertible within-bank bridges do not lower it. Every optimal
alternating four-stage word has a projector P and rank profile
`(rank P, K, K, rank(I-P))`. Every rank split is attained.

Claim type: scoped proof with exact finite corroboration. No new kappa.

For nondecreasing subadditive directional rank tariffs f_U,f_L, the exact
minimum is

```text
f_U(K) + f_L(K) + min_(r=0..K) [f_U(r) + f_L(K-r)].
```

For a common concave power tariff r^theta, 0<theta<=1, this is exactly
3 K^theta. A fourth pure stage buys no saving. The named K=4 witness has
profile `(1,4,4,3)` and total rank 12. Any 11-unit four-stage witness in
PR2052's larger model must include a simultaneous mixed-direction stage.
Unpaidmoon already reports a finite exclusion of the full mixed K=4 model
over F2 in [fork PR125](https://github.com/unpaidmoon/integer-mult-bounds/pull/125),
head `d9f9103be548e5b1b4a4ee1bf216ac5084ca7824`. Its broader F2 exclusion is
cited without replay. The mixed question here remains open over other fields.

[PROOF.md](PROOF.md) gives the complete block classification, bridge reduction,
projector equality criterion and tariff theorem. These are written all-field,
all-K results. They are not inferred from finite examples. For the alternating
four-stage class alone, the displayed tariff formula needs monotonicity only;
subadditivity allows merging equal-direction neighbors in a general word.
The convex square tariff at K=2 is a useful control: four stages cost 10
while three cost 12, so the subadditive/common-tariff hypothesis matters.

## Reproduce

From the repository root, CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/four-stage-pure-shear-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/four-stage-pure-shear-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/four-stage-pure-shear-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/four-stage-pure-shear-tariff --check-source-history
```

Another CPython 3.12 path can replace the local path. The direct command emits
`PASS_FOUR_STAGE_PURE_SHEAR_TARIFF` inside a generated JSON receipt with actual
enumeration counts and SHA256 hashes of all six package files. It writes
nothing. Normal and optimized commands have identical mathematical coverage.
No predecessor executable or scientific replay is imported.

The oracle exhausts all alternating four-stage words on two-dimensional
banks over F2 and one-dimensional banks over F2,F3,F5,F7. It compares literal
full-matrix execution with the independently transcribed block criterion,
checks every accepted word's rank bound and equality condition, and records
actual minima for linear and square tariffs. A separate oracle checks every
monotone directional tariff pair with values in 0..4 on these finite
profiles. Separate complete-input constructions cover K=1..8, every projector rank and four fields, including
within-bank basis transport. Exact integer tariff fixtures extend through
K=32. Controls exercise omission, singular versus invertible endpoints,
nonprojectors, field-dependent rank, identity versus exchange and the convex
tariff escape. The receipt contains the exact finite coverage.

## Limitations

A pure stage acts in one direction on any number of pairs. This theorem does
not allow both directions simultaneously in one stage. Splitting a mixed
stage changes the depth and cannot apply this bound to PR2052's whole model.
The physical price of free bridges and all helper/native/owner/precision,
tape, compiler and outer costs remain unpriced. No selected cold replay,
Lean, Docker, complete supplier or multiplication theorem is supplied.
Independent human and formal proof-kernel review are unclaimed. The selected
record and all five framework assumptions remain unchanged.

## Open next questions

Can a four-stage simultaneous mixed-direction word over Q attain the eleven-unit
K=4 lower bound? Start with nonzero H and E in at least one stage and enforce
HE=EH=0, every bridge and the complete arbitrary-input endpoint. The present
pure-stage classification cannot price that altered depth contract. This is
the unclosed part of PR2052's question, with its structured first step in
[TASK.json](TASK.json).

## Credit and overlap

Credit themilkman216 / [PR2052](https://github.com/CrocSwap/integer-mult-bounds/pull/2052)
for the model, general stage bound and even-stage open question; Johnny
Franks / cross-shear-stage-bound for the earlier stage potential; Jacob Alan
Sussman and the archived borrowing-chain/controller lineage for the standard
three-stage exchange. Exact main-tree source documents are pinned as
provenance. No predecessor result is reverified or claimed as new. Block
elimination, rank subadditivity and projector decompositions are classical.
The new repository contribution is the complete four-stage pure classification,
its equality condition and directional tariff formula.

Base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. The selected source-binding positive control passed. Live open
PRs, active Discussions, recent account work, local reservations, merged
object/formula searches and main README searches were checked before the
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360723).
The entry cache covers 351 open PRs and 6251 Discussion records with complete
remote pagination; sparse local notes cover only 108 of 8917 tracked notes.
Targeted all-main searches supplement that incomplete local coverage. No
search miss certifies novelty or covers unpublished work.

## Implementation bounds

The checker is finite, deterministic, nonrecursive and read-only. Matrices
have at most 16 rows; exhaustive banks have dimension at most two; the
largest alphabet has 16 matrices. The main complete word census visits
16^4 candidates. Construction loops cover eight widths, four fields and
at most nine projector ranks. Tariff loops cover 32 widths and 25 positive
price pairs. Functions fit within 60 physical lines, checks remain enabled
under -O, state is local and there is no subprocess, network, dynamic import
or code generation.

Power of Ten rule 3 has a bounded managed-runtime deviation in verify.py.
Python allocates tuples, lists and integers during each finite calculation.
The exhaustive oracle stores at most 256 pair matrices with 16 scalar
entries each, 81 possible rank profiles and 15 monotone tariffs. Construction
matrices have at most 256 entries. Each hashed package file is limited to one megabyte before reading. These are storage
bounds for this checker, not fixed-pool or measured runtime heap guarantees.
Reassess the bounds and introduce fixed buffers before lifting any input cap
or using the code in a steady service. Warning-strict normal and optimized
runs are the available Python diagnostics; no repository-wide analyzer or
native allocator check is claimed.
