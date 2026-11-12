# Conditional kappa 0.00309839 from independent helper splits

This construction raises complete conditional **kappa to 0.00309839**.
The gain over [PR5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580)
(0.00308189) is **0.00001650**, about **0.5354%**. The gain over selected
0.003027288235 is **0.000071101765**. The selected record is unchanged.

The mechanism changes the independent helper basis. At a common-frame cut,
one helper combination can finish early and a fresh independent input can
use the remaining program. Fifteen explicit splits replace 527 helper
jobs by 542 helper jobs. They add 362 scalar events and no recursive Gaussian
call. Both input and output support are checked over every field; a local
pure row alone does not earn a new target.

Read the [proof](PROOF.md), [exact cuts](SPLITS.json), [complete word](WORD.json.gz),
[receipt](RESULT.json), [source pins](SOURCES.json), and [validation record](VALIDATION.md).
The first split is an explicit 20-ADD change from one H9 target to independent
H5 and H4 targets. The complete caller uses the new word at all 18 full sites.

| Quantity | Result |
| --- | ---: |
| Local public inputs | 750 |
| Independent helpers per full call | 542 |
| Owned lifetimes / peak owned fields | 8 / 1 |
| Local events | 25,502 |
| Complete paid calls | 66,852, unchanged |
| Complete productive fields | 13,084 |
| Complete rank-mass surplus | 760, unchanged |
| Tested saving | 0.0030983905 |
| Complete conditional kappa | 0.00309839 |
| Raw crossing | (0.00309839352211, 0.00309839352212) |
| Exact native maps | 2,926 |

The added helpers enter the complete completion-tail calculation. The tail
bound changes to 39/40, with `(39/40)^128 < 1/16`. The compiler logarithm
power changes from 1000 to 1024. Every native map, helper normalizer, main
adapter, scalar basis operation, route, COPY/CLEAR cost, thin query and
whole idle is included. The ordinary BIT saving remains 0.0034. Two exact
moment engines and all 54 strict plus four functional outer conditions are
checked. The receipt gives the raw crossing and the finite compiler threshold.
A negative derivative bound supplies the raw ceiling for this fixed invoice
on [0,0.0034]; it does not bound other constructions.

## Reproduce

Use Python 3.12 and the standard library, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-helper-subspace-splits --check-only
python3 -B scripts/research_package.py --package research/p104-helper-subspace-splits
```

The registered hook runs normally and with `-O`. Its success markers are
`PASS_P104_HELPER_SUBSPACE_KAPPA_00309839` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Direct replay needs no Git or network:

```sh
python3 -I -B research/p104-helper-subspace-splits/verify.py
python3 -I -O -B research/p104-helper-subspace-splits/verify.py
```

Normal replay is read-only. `--write` explicitly regenerates the two result
artifacts. Inputs are authenticated before imported source code executes.
Each replay uses a fresh bytecode-cache path. The checks reject contaminated
prefix and suffix vectors, missing boundary basis operations, an unearned
whole target, extra helper credit, a missing paid call, a wrong native phase,
a missing central translation, an inadequate cutoff and insufficient BIT stock.

## Scope and coordination

The scientific base is canonical main
`5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority revision 7.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19183208)
records the changed question and local screens. The final publication overlap
cache covered 334 open PRs and 4,863 Discussion records, with complete remote
pagination and incomplete sparse local coverage. Source and coverage details
are coordination evidence, not a novelty proof.

The consumed PR5580 word is pinned to
`6efa248cf456d6101d757e9d09ba29711d18a13a`. It retains the released PR5569
handoff and PR5561 helper endpoints. The new basis splits were first found
on PR5569. Two different greedy cut orders reached the same fifteen-split
histogram. All fifteen were then composed with PR5580 and checked again. The exact
source copy is retained in this branch at commit
`29fe88ba218b5d2192d8e31f07a01d1141afdacd`. Its SHA256 and Git blob match the
recorded PR5580 source. Registered replay needs only this branch history;
it does not need cached objects from unmerged PR branches.
No new Gaussian itinerary is introduced. Active frame-extension work in
[Discussion5575](https://github.com/CrocSwap/integer-mult-bounds/discussions/5575)
is a separate investigation.

The final refresh also found [parallel coupled-basis and handoff work](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19154639).
It uses the same rank-one mechanism and separately changes paid boundary
work. The [public composition handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19183908)
releases these fifteen cuts and leaves the six paid-boundary changes with
the parallel claim. No exclusive method novelty or combined gain is claimed.
The new scalar contacts and input count change the hypotheses of
[PR5590](https://github.com/CrocSwap/integer-mult-bounds/pull/5590)’s fixed-contact floor.

The scope changes the scalar word, the input count and the target contract.
It therefore differs from a scalar-only simplification or a fixed-input
helper stop. The unchanged paid histogram now supports a different,
fully independent target histogram.

The five selected framework assumptions remain: native implementation at
all widths, owned erasure, uniform compiler closure, precision and tape cost,
and analytic recovery. The helper-endpoint contract also remains.
The complete rounded multiplier and enormous uniform compiler word are not
materialized. The same AI-assisted author constructed and checked this
package. Independent human review, proof-kernel acceptance and global
optimality are not claimed.

## Sources and credit

- **Ali Romman**: [PR5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580)
  supplies the exact source word; [PR5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544)
  and [PR5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545) supply
  the complete P104 caller and source replay.
- **Joel Pulikkan / GamingPuzzled**: [PR5569](https://github.com/CrocSwap/integer-mult-bounds/pull/5569)
  supplies the priced helper handoff; [PR5472](https://github.com/CrocSwap/integer-mult-bounds/pull/5472)
  supplies an earlier successor-handoff construction.
- **DreamingOfClouds**: [PR5561](https://github.com/CrocSwap/integer-mult-bounds/pull/5561)
  supplies free helper endpoints and PR5568 supplies search tools.
  **thu-nmrc** supplies the PR5551 contact improvements.
- **Gareth Davidson / bitplane**, **David Arias** and **Cinna Davis** supply
  the PR2305 composition, PR2152 coalesced word and PR2219 private reuse.
  Cinna Davis also supplies the controller lineage.
- **Jacob Alan Sussman** supplies productive mixed-target recursion.
  **zxv** and **Cao Yifan** supply the retained interval, compiler and
  native/pricing lineage. Source notices preserve earlier geometry, BIT
  and analytic credit.

The elementary rank-one basis identity is not claimed as a new general
linear-algebra theorem. The contribution is this explicit independent-target
construction and its complete conditional price. New work is by Ali Romman
with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
See [NOTICE](NOTICE).

## Open next questions

An independent reviewer can check the first split and then replay the complete
package. Further gains could use a different compatible cut order, basis or
frame itinerary. Both prefix and suffix support must be proved before a
new target receives credit. The two greedy runs do not establish a global
maximum. [TASK.json](TASK.json) gives the first checks and remaining obligations.

The optional continuation screen is reproducible with:

```sh
python3 -I -B research/p104-helper-subspace-splits/search.py
```

It tests exact elimination-basis pairs at cuts immediately after MOVE events,
inside equal-boundary helper groups. On the final word it finds no further
candidate in 53 groups. This result covers those tested pairs. It does not
exclude different cut sequences, arbitrary basis combinations or new frames.
The complete-kappa verifier does not depend on a discovery search failure.
