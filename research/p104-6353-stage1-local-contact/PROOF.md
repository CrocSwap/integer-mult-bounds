# Stage-1 LOCAL contact of the PR6353 port set

## Statement

Let the caller be the frozen PR6348 word in
`research/balanced-query-tree/CONTROLLER.json`. Its event 21 is

```text
LOCAL(stage=1, src=0, dst=1).
```

The declared scalar action of that opcode, read off the caller replay rule, is

```text
dst <- dst + Q^{-1} src,
src <- D_1 src,
dst <- D_1 dst.
```

`D_1` is the phase polynomial of the eight fresh caller axes `9,...,16`.
`Q^{-1}` is the central port `q` with coefficient `-1` (equivalently `3` mod 4).

On the PR6353 supplier word, head `db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`,
the 104 values `ports` equal the PR6349 source ports. For every such port,
and for the orthogonal 8-frame stored under that port in the pinned
`DATA-PHASES.json` recipes, the four physical contacts

```text
raw_X -> entry_X, raw_Y -> entry_Y, exit_X -> out_X, exit_Y -> out_Y
```

of balanced-query-tree stage 1 succeed. Each contact is an orthogonal
involution route, fixing `q`, whose forward and inverse phases differ by one
even translation of Hamming weight at most 17. The two raw-to-output
differences are exactly `D_1` and `D_1 Q^{-1}`.

This is an operator identity of phase polynomials. It does not specialize
the input vector. It is not a materialized matrix on `(C^2)^{\otimes 161}`.

## What the nine output edits do not touch

Relative to `research/p104-native-input-lifting/WORD.json.gz`, PR6353 changes
exactly nine public finals:

| Role | New frame |
|---:|---:|
| 226, 297, 393, 484, 485, 707 | 246 |
| 361, 451 | 245 |
| 703 | 1094, basis `[7, 9, 35, 66, 400]` |

Event 12917 is `MOVE 703: 712 -> 1094` with ownership flag false. Labels
770 through 778 each have an `INIT` and a `CLEAR`, and at least one owned
`MOVE`. Those labels are disjoint from caller roles 0 and 1. The stage-1
contact reads `ports` and the phase recipes only. It does not read `final`,
`frames`, or the supplier program, so these nine edits do not change this
contact. The frame-1094 entrance is a supplier transport, not this LOCAL event.

## Boundary

Stages 2 through 19, endpoint phases, whole idles, central-square columns,
funding, the compiler, and the outer predicates are not checked. The five
framework assumptions remain. No new kappa is claimed. Selected kappa stays
`781451/250000000`.
