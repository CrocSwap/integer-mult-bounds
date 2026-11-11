# Conditional κ = 0.003645473221716 from a shorter funded return

This candidate improves exact [#7244](https://github.com/CrocSwap/integer-mult-bounds/pull/7244)
by **0.000000100853884** with the same signed 17-stage caller
from [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The selected
[#7000](https://github.com/CrocSwap/integer-mult-bounds/pull/7000)
remains at κ = 0.00363005817.

Continuation 1499 now stops at chart 245 on its existing path to 127.
It supplies the same scalar correction that previously required both
donor outputs at 127. After that correction and the existing terminal
basis, helper 991 returns at rank eight. Per native, the **entire**
profile change is `T8 +1, T9 −1, P4 +1, P5 −1`. The complete signed
caller has 22,461 productive positions, 110,553 paid positions, rank
surplus 1,424 and zero empty-root credit. The 76,444-event word retains
1,501 public fields, 67 owned labels, 70 owned lifetimes and peak 49
owned fields. The canonical emitted word SHA-256 is
`be20da577573b70989a052d814b4701c72eaf9053e159078a28e7d1f90280d32`.

The complete signed invoice crosses in
`[0.00364547322171601989948043948889132, 0.00364547322171601989948043948889133]`
with the independent directed engine. This is a fixed-invoice ceiling.
The compiler tests 0.003645473221716007, below that crossing, and
the outer checks leave strict headroom at the stated claim. The old
invoice rejects the new price. The exact totals and both price checks
are in [RESULT.json](RESULT.json).

Run with CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-funded-shorter-return
```

[PROOF.md](PROOF.md) explains the operator and cost changes.
[INPUTS.json](INPUTS.json) pins every exact #7244 archive member by
Git blob, size and SHA-256. The archive retains the predecessor's
source closure and notices so no unmerged Git branch or network
access is needed during replay. The verifier first uses #7244's
authenticated adapter, then rebinds the comparator, new chart maps,
ownership, exact price and full caller to this word. Registered commands
work on private temporary copies. See [REPLAY.txt](REPLAY.txt) for the
executed stages and [TASK.json](TASK.json) for scope and overlap.

This is a conditional frontier proposal under the same five framework
assumptions: all-column native maps, owned erasure, compiler closure,
precision and tape bounds, and analytic recovery. It is finite source
and application evidence. Maintainer selection, independent human
review, a materialized multiplier and formal kernel acceptance are
outside the result.

Credit Clear1nsight and the #7244 lineage, Rohan Arun/dillona and the
#7161 rechart/split chain, the exact #7113 signed caller and retained
work by ToikY, Ali Romman, Jerry Chen/CubeJerry, DreamingOfClouds and
the other contributors named in the frozen sources. Prepared with
substantial OpenAI Codex and ChatGPT Pro assistance, Apache-2.0.

## Open next questions

- Can the maintainers select the new conditional bound? Reproduce the
  exact submitted head and compare its signed application and inherited
  assumptions to #7000. See [TASK.json](TASK.json).
- Can a coframed continuation already using chart 245 deliver the same
  correction without splitting 1499's rank-five move? Compare exact
  chart-245 rows before the terminal basis. The fixed-itinerary screen
  did not supply 1499's row there.
