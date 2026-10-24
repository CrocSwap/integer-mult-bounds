# Fixed-word frame-gauge limits

This package gives scoped negative results for the historical local scalar
word at commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
It does not improve the complete kappa calculation. It does not give a new
supplier or a lower bound for arbitrary centre encodings.

The [proof](PROOF.md) states the boundary condition and the exact classes.
The [source pins](SOURCES.json) bind the two source members, the original
certificates, the checker adaptations, and the retained notices.
The [replay](replay.py) uses integer and rational arithmetic only.
The fresh [replay receipt](evidence/replay/REPLAY.json) records the nine checks.

## Results

| Gauge class on the fixed scalar word | Proved result |
| --- | --- |
| One fixed nonzero translation line, with independent binary choices on scalar components | All 511 lines have minimum total native rank change zero. Each even line is nondecreasing on each native edge. |
| One of the 16 common odd lines; the binary product `C_128 C_256`; or the four states `I,C_128,C_256,C_128 C_256` | Every increasing concave native rank cost with `f(0)=0` is nondecreasing. Every zero-total-rank choice is constant on all 1,971 native components. |
| Binary `I,T_415` in forward coordinates | The rank minimum is zero. A cut saves one child count and adds rank 48. Every changed native cut adds more than `47/9800` to `sum r^(1-b)` for `0 <= b <= 2/5`. |
| Arbitrary products of lines from the common five-dimensional subspace | Each centre descent has rank at least six. `C_128 C_256` attains six at all eight centres. This is a local bound. |

Every graph result includes all 5,064 native events and all 1,570 old
rank-zero wrappers. The graph keeps the scalar word, native edge positions,
and exact endpoint. The general boundary condition is
`diag(G_out) P = P diag(G_in)`.

The translation-line results apply to both original orientations with the
same gauges. The backward full-frame result uses `F T_415 F^-1`, not
`T_415` in the backward coordinates. The all-line rank theorem does not
exclude child-moment gains for odd lines outside the common family.

## Reproduce

Use Python 3.10 or later. Only the standard library is needed. Use one
process and keep at least 3 GiB of free disk space. From this directory:

```sh
python3 -I -O -B replay.py --out /tmp/fixed-word-gauge-replay
```

The output directory must not exist. The last output line must be:

```text
PASS_FIXED_WORD_GAUGE_LIMITS
```

The replay checks both scalar endpoints on all 712 input columns. It
rebuilds the graph, checks the ranks by two methods, checks 10,488 integer
paths, and checks exact flow/cut witnesses for the rank and capped-cost
bounds. It also runs 13 damage controls. It performs no optimization or
mathematical search. The seven source certificates are unchanged; legacy
solver and timing metadata inside them are not proof premises.

The package contains the two compressed source members. A replay needs
neither Git nor the historical source checkout. Their compressed and
expanded hashes are in `SOURCES.json`. The original selected archive was
read and hash-checked during extraction. The replay verifies the member
pins and the complete package manifest before it uses them.

## Scope and current work

This package uses a historical construction. The publication base is
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`; its selected construction has
changed. These results are not asserted for that changed scalar graph.
No current selected cold replay, changed native lowering, full recursive
repricing, or new hosting construction is part of this package.

The original proofs and review receipts are retained under `proofs/` and
`evidence/historical/`. They are historical records. The present proof and
replay define the publication scope. Exploratory palette results,
geodesic normalization, and code-closure claims are excluded.

## Open next questions

- Can an odd fixed line outside the common family reduce a child moment
  while preserving total rank? First derive exact capped-cost witnesses
  for that line. The present path theorem does not answer this question.
- Can a larger common-product family improve complete cost while leaving
  rank-six centres? First price every native edge on the same scalar graph.
  The local rank-six bound alone does not exclude a gain.
- Can a different scalar schedule or a correlated child interface give a
  new supplier? First supply its complete physical contract and source
  binding. This package does not provide that construction.

These are continuation boundaries. No new research search was run for
this publication package.
