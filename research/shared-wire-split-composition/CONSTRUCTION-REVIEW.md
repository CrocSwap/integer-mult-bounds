# Independent review of the composed wire and two splits

This review checks the construction's causal and linear interfaces. Complete
word endpoints, signed invoices, native Clifford lowering, scalar grids,
callers and the outer bound have separate checks. The source construction is
conditional on the framework premises declared by #6936 and #6937.

## Composition and causal ordering

The dependency graph uses three access classes. ADDs sharing only a
destination commute, as do ADDs sharing only a source. Every read/write
conflict and every MOVE, SCALE, INIT, CLEAR or COPY destination is ordered.
Consecutive noncommuting access runs suffice by transitivity. A topological
ordering therefore preserves operand versions and the frame at each scalar
access while allowing commuting runs to reorder.

After the construction's role renumberings, the retained branch-exclusive
pieces contain 236 events from #6937's `wh` word and 46 from #6936's split
word. Their register footprints are disjoint. Shared literal events have equal
multiplicities in both sources, so occurrence-token matching does not conflate
different multiplicities. The checker reconstructs these facts from the two
source words. They are specific to this composition; arbitrary separately
correct rewrites need not compose.

## The additional wire

The contacts `449 += 226` and `990 -= 1206` are replaced by dirty helper 1477
at frames `3,260,724,246`, whose dimensions are `0,3,6,8`. Its eight ADDs
realize exactly those two shears and restore its arbitrary independent input.
The checker verifies all five independent input columns of the local map.

Sources 226 and 1206 have no logical writes between their paired helper
loads. Targets 449 and 990 have no reads between their paired helper reads.
MOVEs preserve logical values, and other additions into a target commute
with the module. The four partners are distinct, the helper frames are
strictly nested, and each actual scalar contact occurs at a common frame.
These conditions justify the local identity despite intervening events.

The helper contribution to `P-T` is `2 H3 + H2 - H8`, with zero rank mass.
Merging each pair of partner MOVEs preserves that partner's rank mass. The
complete paid histogram and ordinary allowance are checked separately.

## The two source-bound splits

Let `P` map independent public inputs to the current fields, with owned
entries initially zero. Let `S` be the suffix, and `T=SP` the original public
endpoint. On the selected helper family, `T` is an independent identity, so
it commutes with a boundary basis change `B` supported on that family.
The split witnesses satisfy

`aP=c`, `Sb=d`, `ab=1`, `cd=1`.

The supports of `a,b` share the cut frame, while those of `c,d` share entry
and exit frames. Choose `C` with pivot row `a` and inverse pivot column `b`,
and `B` with pivot row `c` and inverse pivot column `d`. Then

`P'=CPB^-1`, `S'=BSC^-1`

have `e_p^T P'=e_p^T`, `S'e_p=e_p`, and `S'P'=T`.
Set `J=I-e_p e_p^T`. Retain the old pivot prefix output in the head field,
and substitute the independent new tail input `z` at the suffix pivot. The
suffix output becomes

`S'(JP'x+e_p z)=Tx-e_p x_p+e_p z`.

The head output is `x_p`, the renamed tail output is `z`, and all other
outputs are unchanged. Thus no independent public value is copied or erased.
All scalar basis operations remain charged ordinary work.

For `c_p!=0`, the basis constructor first makes row `p` equal to `c` and
then sets row `j=e_j^T-d_j c` for `j!=p`. This gives `Bd=e_p` from `cd=1`,
and determinant `c_p!=0`. No extra factor of `c_p` or `d_p` is missing.
When `c_p=0`, an initial coordinate swap, applied to both `c,d`, gives the
same required row and inverse-column properties. The second witness exercises
that swap case.

| Pivot | Reconstructed source word | Cut after event | Frame |
|---|---|---:|---:|
| 759 | `extra_wire_0.json.gz` | 42531 | 660 |
| 450 | `split759.json.gz` | 37192 | 595 |

The cuts are after the stated zero-based events. Both actual cut-witness
supports are public, and all entry, exit and cut frame conditions are checked.

## Independent replay

`independent_construction.py` imports no construction or extraction code.
It propagates a single covector backwards through the prefix to check
`aP=c`, and a single vector forwards through the suffix to check `Sb=d`.
This is dual to the constructor's forward-prefix/backward-suffix full-row
extraction. The checker also verifies both pairings, basis rows and inverse
columns, all support frames and the new wire's causal conditions. Altered
prefix and suffix witnesses are rejected. Checks remain active under `-O`.

After cold reconstruction into a temporary build directory, run:

```sh
python3 -I -O -B independent_construction.py \
  --package-root /path/to/package --build-dir /path/to/temporary-build
```

The package must contain `data/main_6936.json.gz` and `data/wh_6937.json.gz`.
The build directory must contain `composed.json.gz`, `extra_wire_0.json.gz`,
`split759.json.gz`, `split759.proof.json` and `split759_450.proof.json`.
The checker writes nothing and prints source/container and canonical-payload
hashes with the marker `PASS_CONSTRUCTION_INTERFACE_REVIEW`.

Credit: DreamingOfClouds' #6936/#6937 source constructions and Ali Romman's
#5599 independent-helper basis mechanism. The independent proof and checker
were prepared with substantial OpenAI Codex assistance. This is separate AI
review, not human or formal-kernel acceptance. Apache-2.0.
