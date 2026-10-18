# Rank-one residual on a shared readout core

**Scoped recursive-interface construction. No selected-supplier admission or new κ is claimed.**

## Result

The completed common-A broadcast construction covers the case where both output
maps are identical. This package extends that operation to a nonzero output-map
deviation. Over `F2`, take one source, a dirty connector `z`, and two dirty
targets with required updates

```text
y0 += C B x
y1 += (C + D) B x,
```

where `D` has rank one. At two connector-prefix boundaries, replace separate
`C` and `C+D` readouts by one paid broadcast of `Cz` to both targets and one
ordinary `D` readout to `y1` at each boundary. The correction calls are not
omitted or treated as free.

For arbitrary linear `B`, the two dirty connector values are `z` and
`z + Bx`. Therefore

```text
Cz + C(z + Bx)       = C Bx
(C+D)z + (C+D)(z+Bx) = (C+D) Bx.
```

The dirty connector cancels, `B` is called twice and restored, sources are
read-only, and neither target needs to be observed or clean.

## Exact fixture

The verifier exhausts all 1,024 states of `x,z,y0,y1` and a two-bit arbitrary
scratch row for

```text
B = I2
C = [[1,1], [1,0]]
D = [[1,0], [0,0]]
C+D = [[0,1], [1,0]].
```

Both output maps are full rank and distinct; `D` has rank one. The exact direct
and broadcast schedules agree on every dirty state. Four negative controls
reject a missing residual, a missing broadcast destination, a single-prefix
read, and omitted source restoration.

## Complete local invoice

Let `c_M` be the complete dirty-safe cost of one call that applies map `M` to
one target, including its recursive children, coefficient/source access,
arithmetic, target update, scratch restoration, frames and precision. Let `w`
be the extra target-row update for broadcasting to the second output, `r` the
additional broadcast routing and dispatch cost per call, and `P` all shared
storage, setup and entry/exit costs. For the two source-prefix boundaries,

```text
C_separate = P + 2 c_B + 2 c_C + 2 c_(C+D) + D_separate
C_broadcast = P + 2 c_B + 2(c_C + w + r + c_D) + D_broadcast
saving = 2(c_(C+D) - c_D - w - r) + D_separate - D_broadcast.
```

The fixture charges `P=3`, `c_B=2`, `c_C=4`, `c_(C+D)=4`, `c_D=1`, `w=1`,
and `r=1`, with no other schedule-level difference. The complete totals are
23 versus 21 units, a two-unit saving. This is an explicit tariff example,
not a measured tariff from an integer-multiplication supplier. The mechanism
is favorable only when the actual complete calls satisfy the displayed
break-even inequality.

## Reproduce

From the repository root:

```sh
python3 -B research/lowrank-common-readout-seed726b/verify.py
python3 scripts/research_package.py --package research/lowrank-common-readout-seed726b --check-only
python3.12 scripts/research_package.py --package research/lowrank-common-readout-seed726b
```

Expected direct verifier status: `PASS_LOWRANK_COMMON_READOUT` with 1,024
dirty states, five passing controls, and a two-unit illustrative saving.
The exact base, selected record and predecessor package are pinned in
[SOURCES.json](SOURCES.json). The verifier does not import the common-A
predecessor's checker. Locally, the direct verifier and package metadata/pin
check passed on Python 3.14.7. Python 3.12 is unavailable on this host, so the
registered Python 3.12 replay remains for CI.

## Scope and remaining obligations

The domain is exactly one source, two output targets and a two-coordinate
connector. The search stops after this complete dirty-state fixture and its
symbolic two-prefix identity; it does not search longer source words or larger
maps. The chosen tariff is a conditional local model. The selected #1094
supplier has not been shown to expose a costly common core `C`, a rank-one
residual `D`, or a broadcast route with the required tariff. This package
therefore makes no conditional-κ or full-supplier claim.

## Predecessors and credit

PR943 supplies the universal dirty-connector prefix identity. PR889 batches
outputs sharing a common right factor. Merged PR1707 supplies the identical-map
common-A broadcast, the `D=0` case. This contribution keeps one added broadcast
operation and changes the output-map hypothesis to `A0=C`, `A1=C+D` with
nonzero rank-one `D`; all residual evaluations and writes are paid.

Prepared by OpenAI Codex with substantial OpenAI Codex assistance in scope,
derivation, verifier, cost accounting and exposition. No independent human or
formal proof-assistant review is claimed. New material is Apache-2.0.

## Open next questions

Can a selected recursive supplier furnish two exact output maps with a useful
common core and low-rank residual while satisfying
`c_(C+D) > c_D + w + r` after all routing, restoration, precision and schedule
costs? Inspect the actual selected supplier's output-map factors and price
one qualifying pair before attempting integration. The current result alone
does not establish such a pair.
