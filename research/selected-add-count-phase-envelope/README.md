# Joined count backing for one native ADD

This package closes the count/counter composition handoff from
[PR2912](https://github.com/CrocSwap/integer-mult-bounds/pull/2912) and
[PR2905](https://github.com/CrocSwap/integer-mult-bounds/pull/2905). For one
unchanged native ADD action, retained extent tapes and countdown tapes obey
the written bound

```text
total count backing <= K + max(E, R + max(C,H))
```

K is unchanged entry backing, E bounds extent preparation, R is exact
returned marginal backing, C is the exact native Counter maximum, and H
separately bounds a coefficient callback whose private count tapes are
released before return. [PROOF.md](PROOF.md) defines every quantity and
ownership premise. Clearing alone does not release backing.

The preparation and countdown results belong to their predecessors. This
contribution joins their source lifetimes through `stream_runner.action`
with the two-bank `layout.Layout`, checks the union on actual ADD executions,
and gives successful distinguishing examples. It is one component of the
action-private storage A requested by
[PR2882](https://github.com/CrocSwap/integer-mult-bounds/pull/2882), not a total
reserve, physical reuse theorem, supplier or new kappa.

## Evidence

The minimal M=3 fixture has E=21, R=12 and C=18. Its native phase reaches
30 private count cells, so the 21-cell preparation envelope alone is
insufficient. Adding E+C instead gives 39, although those peaks do not
coexist. A released callback with H=68 gives peak 80. Retaining its cleared
tapes instead reaches 166 while both coefficient values and the ADD
permutation remain correct. Padding the index to 256 digits gives a reached
267-cell preparation peak with the same 12 returned marginal cells.

[RESULT.json](RESULT.json) records 70 complete ADD fixtures and the escaping
counterexample. The unchanged-source checker samples every count Tape
creation/write without retaining tapes. It checks both suffix branches,
all coefficients modulo three, three gap locations, larger spectators,
padding, entry aliases and moduli five and nine. All nine origin basis
planes of the smallest fibre are also replayed. Every output is compared
with an independently written integer-address permutation.

Eight embedded controls and seven test groups address actual insufficient
quotas, wrong ADD behavior, source changes, typed receipt corruption,
module/observer restoration and Git-free relocation. Internal independent
source/observer checks corroborated the result. The evidence is
author-checked; no independent human or formal-kernel review is claimed.
Commands, environments and bounded-code deviations are in
[VALIDATION.md](VALIDATION.md).

## Reproduce

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/selected-add-count-phase-envelope --check-only
python3.12 -B scripts/research_package.py --package research/selected-add-count-phase-envelope
```

The registered hook authenticates the source, replays the committed receipt
and runs the tests. Direct optimized replay is also supported:

```sh
python3.12 -I -O -B research/selected-add-count-phase-envelope/verify.py
```

Expected direct output is
`PASS_SELECTED_ADD_COUNT_PHASE_ENVELOPE fixtures=70 controls=8 no_new_kappa`.
Normal replay is read-only; `verify.py --write` regenerates only this
package's RESULT.json. [SOURCES.json](SOURCES.json) authenticates the ten
unchanged inputs and pins the historical main/priority provenance.

## Open next questions

Bind one reached coefficient callback's numerical arenas, records, programs
and continuations at the same cuts. Join these with the separate
[PR2902 payload bound](https://github.com/CrocSwap/integer-mult-bounds/pull/2902)
and this count envelope before claiming total A. The first step is an exact
owner inventory at callback entry, pending allocation and return. The blocker
is the missing common-cut ledger for those categories, followed by physical
last-owner/reuse and movement costs. [TASK.json](TASK.json) records this scope
and the released claim. This result does not expand the construction family.

## Scope and credit

Initial canonical main `475fec190d5ad746bd4690574dca30d6901acdaf`, priority
revision five. The helper-contract draw was explicitly changed to this live
selected-interface handoff after the scalar H2/K implication was found
already covered. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18970664)
contains the overlap and publication status.

Jose Manuel/jmbarrancoml supplied PR2697 and its retained source lineage.
Nick Petalas supplied the PR2912 extent, PR2905 countdown and PR2902 payload
components. kumagi supplied PR2882's packet/action-private interface. Ross
Richardson supplied distinct caller/numerical lifetime and backing results;
starship-s supplied the residual component. Their results and the full
selected stream/hosting lineage remain credited in the unchanged input
NOTICE. This package adds the joined count-phase proof and replay only.

Nick Petalas. Apache-2.0. Substantial automated assistance was used.
Full selected GL64 execution, arbitrary failure cleanup, total private A,
physical reuse, recursive/outer reserve, supplier admission and a new kappa
remain outside this contribution.
