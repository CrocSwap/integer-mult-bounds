# E8's first decoder rank drop: exact star costs 50 and 57

**Structural research note / scoped negative result. No new κ.**
Deleting 56 of the 120 real E8 root lines first permits a binary decoder
rank drop. The complete boundary consists of **255 deletion sets**:

| Sets | Available reader dimension | Required live-target dimension | Optimal star cost on 64 ports |
|---:|---:|---:|---:|
| 120 | 8 | **7** | **50** |
| 135 | 8 | 8 | **57** |

The seven-dimensional case needs separate accounting: totals outside its
required target span are allowed and can attain the same minimum with eight
totals. The certificate prices both possibilities. Both cost ratios are
worse than **63/111**. The other 56-deletion sets retain nine dimensions;
a proved relaxation gives cost at least 44. Together with PR939, this
excludes a better fixed-star copy ratio through **56 deletions**.

This examines the explicit rank-loss boundary left open by PR939, rather
than repeating its rank-nine search. The selected frontier and upstream/
are unchanged. Base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`, selecting
PR890's conditional `κ=1661957774647029/10^18`. Its actual construction is
`research/complex-t21-owners`, reviewed in
`docs/research/community-frontier890-review.md`.

## Reproduce

Python 3.10+ and the standard library, offline, from the repository root:

```sh
python3 -I -B research/e8-first-rank-drop/verify.py
python3 -I -B research/e8-first-rank-drop/independent_check.py
python3 -I -B research/e8-first-rank-drop/test_package.py
```

Expected main marker:

```
PASS_E8_FIRST_RANK_DROP cases=255 orbits=120+135 target_dimensions=7,8 costs=50,57 retained_lower=44 controls=7 no_new_kappa
```

The primary reconstructs all 255 cases and all their rational rank tables.
The independent implementation uses Fraction elimination and explicit root
isometries to check all cases from two representatives. Both checkers retain
their checks under `-O`. The package test adds evidence/source mutations and
an isolated replay after relocation. See [VALIDATION.md](VALIDATION.md) for
actual completed runs and their limits.

To regenerate the exact certificate without replacing the committed file:

```sh
python3 -I -B research/e8-first-rank-drop/verify.py --write /tmp/e8-first-rank-drop.json
cmp research/e8-first-rank-drop/CERTIFICATE.json /tmp/e8-first-rank-drop.json
```

The output path must not already exist. The primary is read-only by default.
The certificate includes explicit bases, complete rank-table digests,
filtrations, all 255 punctures and the two isometry orbits. Root indices use
this package's sorted doubled coordinates, not a supplier's port numbering.

## Scope and credit

[PROOF.md](PROOF.md) defines the fixed binary star model and proves the
coverage and cost reductions. It distinguishes restricted original readers
from required live-target rows and accounts for extra totals. This is neither
an optimum over arbitrary decoders nor a complete supplier invoice. Physical
window rank remains eight. Better helper work, different geometry, 57+
punctures and the inherited compiler/hosting/analytic obligations remain open.

Credit **Chi Zhao / PR631**, **Ross Richardson / PR939**, **Philipp
(@mightyOil) / PR875**, **Joel Pulikkan / GamingPuzzled / PR620**,
**DreamingOfClouds / PR595/602** and **eumemic / PR543**, with their earlier
E8 lineage. [SOURCES.json](SOURCES.json) pins the two retained predecessor
documents; no predecessor code is imported. [CLAIM.json](CLAIM.json) records
OS-random seed **40**, three candidates, the bounded scope and stopping rule.
No pinned sprint coordination issue existed, so the claim is local.

Prepared by **Ross Richardson (@RossRichardson)** with substantial **OpenAI
Codex assistance** in the proof, both implementations, checking and writing.
No independent human review or formal verification of integer multiplication
is claimed. Apache-2.0; predecessor documents retain their original notices.
