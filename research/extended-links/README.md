# Extended carrier matching on #161's complex word

Built on #161 (eumemic, `d14e291`). Under #161's retained interfaces this package certifies

    T(n) = O(n (log n)^(1 - kappa)),   kappa = 5901881/10^10 = 5.901881e-4

That is +0.394% over #161 (5878747/10^10). #161 is complex-bound, so a complex-side change moves kappa directly.
Only the complex word's carrier arcs and its physical layer change. The graph, the gauges, the bit supplier, the
phase stop, the atom exponent and the assembly are #161's, unchanged.

#161 is not on main, so the package carries the 32 files of #161 it reads as a pinned archive
(`baseline-pr161.tar.gz`, 0.3 MB), following `research/coordinated-frames-and-entrance-banks`. `baseline.py`
rebuilds them in a temporary directory after checking the archive and every file's sha256 against `SOURCE.json`
(commit `d14e291`). Set `EXTENDED_LINKS_TREE` to a full #161 checkout to use that instead. No existing file changes.

| | carrier arcs | roles R | W per vertex | complex saving | kappa |
|---|---:|---:|---:|---:|---:|
| #161 | 6,201 | 16,011 | 15,681 | 5885669/10^10 | 5878747/10^10 |
| #161's arcs, layer rebuilt here | 6,201 | 16,011 | 15,681 | 5893384/10^10 | 5886444/10^10 |
| **this package** | **6,249** | **15,963** | **15,633** | **5908857/10^10** | **5901881/10^10** |

## What changes

1. **48 more carrier arcs.** `scripts/paired_cube/frames.py` accepts an arc only if the donor's coordinate-padded
   maximal frame already lies inside the receiving frame. That pre-test is sufficient, not necessary. What the
   construction needs, and what the repository's independent checker verifies, is weaker: the dependency graph
   with the arcs is acyclic, and every value span still lies in its full backward-intersection frame. `cxlinks.py`
   compiles with exactly that condition. Every arc of #161 is kept; 48 arcs that the pre-test rejects are added.
2. **The physical layer is rebuilt** for the new word with #161's own rules (frame descent, each gauged role in a
   dead donor's slot, late old-value reads). The pairing here is chosen by first-order saving; on #161's own arcs
   that alone is worth +0.13%.

Further output merges (`s`, `w12`, and a pair-level merge of face 1 with edge 01) and two other all-but-one modules
were tried under this pipeline. The merges are cost-neutral and the modules are worse, so none is used.

## Verify

    python3 research/extended-links/verify.py      # stdlib only, about 15 seconds; do not use -O

`verify.py` checks, in order:

1. **Control.** `cxlinks.compile_closure()` with #161's arcs and the repository's operation order returns #161's
   certified complex record exactly. #161's frozen physical record prices to 5885669/10^10 and 5878747/10^10.
2. **Word.** The extended arcs compile, the repository's gauge selection runs unchanged (2,970 rank-18 gauges), and
   the repository's `scripts/paired_cube/verify.py` passes on the result: 1,742,400 signed scalar pairs, K, full
   backward intersections, the physical replay of every frame movement, gauges and target chains.
3. **Physical layer.** The repository's `scripts/paired_cube_physical.py` passes on `data/frames.json` and
   `data/pairs.json`: value spans, nested spliced role chains, pair chronology, target chains in read order, the
   telescoping deficit and the exact aliased dirty-scratch replay, with its three controls rejected.
4. **Pricing.** #161's `exact_moment`, `finite_bridge` and 47-constraint assembly give the complex saving and kappa
   as the largest points of the 10^-10 grid; the next points are rejected. One check of #161's code is relaxed:
   the complex role count is not pinned to 16,011, it must equal `c + q - matched` and not exceed 16,011.

`make_plan.py` regenerates the three data files byte for byte (about 20 seconds). Verification does not use it.

[PROOF.md](PROOF.md) gives the argument and the limits.

## Credits

- eumemic: #161 and its lineage (#117, #131, #143, #152, #155, #157): the complex DAGs, output merging, the
  physical layer and its checker, used here unchanged.
- icekylinx: #144 and #130 (paired cubes, the compiler and its independent checker, gauges, shared cores, assembly).
- an664: #128 completed-core sharing. jamesyc: #124 birth-read reuse. geckods: #153, #158 phase stop.
- Zhihao Chen and Swapnil Jain: the bit lineage behind #161's unchanged bit supplier.

The closure-condition compile, the extended arcs and this physical layer were prepared by DaysSky, assisted with
Claude. No priority over concurrent work is claimed.
