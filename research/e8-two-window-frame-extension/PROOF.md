# Two fixed commuting-window witnesses

The frozen parent is `research/e8-six-edit-frame-extension`, manifest
`d236791aaee0072cd6dd7dd2d8d90b5c1bc04cbb60bf00a00137ce4211787f52`.
Its entire source-bound builder executes unchanged. Starting ordinary hash is
`c146daa0153a81f4050bc16bb607288233ee95085dd006688717ea2ecce2f79a`.

For a target-register addition with a helper source, its off-diagonal matrix
unit has a target row and helper column. Products of any two such off-diagonal
parts vanish because target and helper roles are disjoint. Thus all additions
in each selected window commute pairwise, even where the targets differ.
The wrapper checks those role conditions for every gate. It also checks the
source/intermediate/final hashes and every register's subspace containment.
This scalar argument does not assert commutation of arbitrary partially
emitted Clifford subwords; the full frame-aware invocations are rerun.

The five-gate window starts at B1489 and uses permutation `[4,0,3,2,1]`.
Its new first operation is target 180 minus one-half helper 801, at frame 940.
The intermediate ordinary hash is
`414f7ded771407339f67c725594c43b0a64631a05435b49104ed0ee4f1a8b786`.
The fifteen-gate window starts at B1638 and uses `[14,0,1,...,13]`.
Its new first operation is target 221 plus helper 784, at frame 940.
The final hash is
`a2a1e957cec4f86fa7447037d757218d72b7f70c67391cc4dfb81ed60c0d00e6`.
All other non-histogram metadata is unchanged; helper climb delta is
`{1:-4,2:+2}`. Both newly first frames have rank seven, versus rank eight.

The heterogeneous helper403 uncompute belongs to a separate inserted program.
It is regenerated from its unchanged last source use, with freshly derived
preconditioning and full exact scalar maps. It is not included in the ordinary
fifteen-gate permutation. Removing an endpoint uncompute or reversing the
preconditioning order must fail the fresh live-column check. Both full dirty
orientations restore every helper input column and private work.

The ordinary supplier is `25094722134999 / (25 * 10^15)` and the heterogeneous
supplier is `1003811542742011 / 10^18`. The complete fused candidate has hash
`cf0ce85d2dd4775ac9f59dbb5d548b6a74279416b2e50f1a1731978b490e2d10`.
Its supplier is `1003978426913831 / 10^18`; no independent gains are added.
All 3139 used phase edges, the three rank-three ten-axis tensor children,
both exterior occupancy cases and explicit endpoint `C72` flags execute again.
In particular, `C72^2 = X72`, not a subspace union. Ten fusion mutations reject.

The bank and global templates bind every one of 24992 helper placements, 288
owner maps and 864 unique padding removals, leaving 27171 rank-one padding
children. Paid calls 1232163 have rank mass 4284387 and deficit 9984 at live
58827. Physical stock is 59618. The full primitive invoice charges 6912 extra
fusion compiler groups, local bound 8390276548412 and per-vertex coefficient
2621822828217291. Row 15449, degree-two halving, gap 49B and all stock/router/
literal/common-reserve guards are recomputed with inherited assertions intact.

Both exact moment engines include fallback and adjacent-grid exclusion. The
unchanged signed-bit coefficient 56223565818967 and source-template-bound
71-bit signed prefix are used by eight finite continuations and 47 strict
outer inequalities. Positive eta=beta=`10^-30` retains the counted outer
log2 cutoff `14 * 10^30`. The original-slack comparison is also recomputed.

Whole endpoint operators, arbitrary correlated dirt and exact finite templates
support only the documented conditional chronological substitution interfaces.
All-size chart/compiler, precision, setup/recovery, restored-row, analytic and
stage-specific dominating constants remain separate obligations. No separately
materialized astronomical global scalar IR, unconditional multiplication
theorem or new Lean proof is claimed.
