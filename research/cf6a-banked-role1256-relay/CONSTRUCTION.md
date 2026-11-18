# Role-1256 paid relay contraction

Fold the exact supplied #7700 word at head `7d84799a447867d36137d12ef7ca5646154d763c` into a banked graph using the chronological folding rule from Ali Romman's #7674. Store every paid return under its zero-based raw MOVE clock. A negative token `~r` denotes the arbitrary input of public role `r`. The public output for role `r` is form `154768+r`. The constructor checks the word, CLEAR certificates and exact decoded 16-stage caller, then rebuilds both archived graph bodies from the raw word. [Supplied word and evidence](https://github.com/CrocSwap/integer-mult-bounds/pull/7700) · [Banked folding source](https://github.com/aliromman/integer-mult-bounds/blob/28b2af322a1fab01b3734365988930920f9dda48/research/p104-banked-transfer-pivots/network.py) · [Constructor](construct.py)

| Raw MOVE clock | Public owner | Source → destination chart | Rank | Normalized source form |
|---:|---:|---|---:|---|
| 95828 | 1256 | 476 → 878 | 3 | `−89449 − 89561 − 95823 + 95825` |
| 104442 | 1256 | 878 → 127 | 3 | `+95828` |

The numbers inside a form are bank tokens. Clock 104442 is the only consumer of 95828 across the paid and terminal forms. Both sides of every original CLEAR certificate also avoid 95828. Keep clock 104442, replace its source by the four-term form at 95828 and route it directly from 476 to 127. Retire clock 95828. The new source uses four existing chart-476 donors. The constructor validates cocharts and computes a topological order for every surviving row. The retained key 104442 advances from zero-based schedule index 4114 to 3310. All 7,643 other surviving rows keep their relative order.

Charts 476, 878 and 127 have ordered binary bases `[75,164,265]`, `[3,4,48,72,144,265]` and `[1,2,4,8,16,32,64,128,256]`. Their spans are strictly nested with dimensions 3, 6 and 9. The canonical chart composition is $(T_{127}T_{878}^{-1})(T_{878}T_{476}^{-1})=T_{127}T_{476}^{-1}$. The direct pair is implemented at rank six. The native verifier checks its full forward and adjoint columns and absolute phase. Per native invocation two rank-three paid routes become one rank-six route. The 16 invocations charge 32 fewer rank-three jobs and 16 additional rank-six jobs, with the identical public ownership and productive target histogram.

The operator replay evaluates the raw chronological source over scaled integer rows independently of the folded evaluation. It checks every raw MOVE row and every original CLEAR equality to other live fields. It then checks all 7,644 surviving row observations in forward and adjoint order, including the 1,501 public rows, and the 235 raw CLEAR relations on both graphs. Those relations include 42 zero fields and 193 nonzero fields with other-live witnesses. Whole-field retirement, new map execution and resource accounting appear in the native and physical verification parts. [Operator receipt](evidence/OPERATOR.json)

The frozen canonical graph hashes are `72705b094d83d2ba24006661bbb031786a691b776bedb94515b1321e1535105f` for the source fold and `8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf` for the contracted graph. Run the self-contained checks from the package directory with Python 3.10 or later.

```sh
python3 -I -B construct.py
python3 -I -B check_operator.py
```

The constructor can also emit both independently rebuilt graph bodies with `--out-dir` and an existing destination directory. The operator check accepts `--out` with a fresh receipt path.
