# Rank149 bit kernel and eleven-stage hosted complex supplier

Conditional **κ = 0.001265931727546219**, **0.00655% above PR447** at
`d3cf3079091bb7e93a23e9cd98e82ccb89697328`, and **0.2031% above PR445**.
The exact bit endpoint is `0.001267536342017397153864`; the complex endpoint
used in the assembly is `0.001268142296690675`. The bit side binds.

Two changes compose:

- The R740 bit word has a checked rank149 response kernel: 121 pivots,
  114 donor slots and 18 explicit residual isometries. It retains PR440/441's
  primitive and B-frame retiming. All 65,120 helper occurrences are hosted
  in PR445's eleven-stage dimension78 schedule, with eight replicas.
- The unchanged PR433 split-centre complex local word runs in eleven
  compressed stages of dimension89. All 49,280 rank-nine helper occurrences
  are hosted. Exact data, idle and terminal phases are regenerated and
  independently checked, including the all-live orthogonal-cover correction.

Neither supplier has helper banks or padding children. Both use 9,600 live
families and deficit3,264. Physical reserves are 9,609 bit families and
10,178 complex families. Fresh finite invoices include every hosted route,
local call, scalar work family, phase adapter, bridge and cover correction.

The largest complex child has rank64. The coarse three-level row estimate
21,948 exceeds the inherited allowance. The new depth proof uses
`89^9 > 16*64^9`: nine levels give four halvings. Including its additive
constant, the row charge fits **20,161** for `log2(width) >= 32`; smaller
widths use the retained finite leaves. The external row allowance and degree
gap are unchanged. See `PROOF.md` for the uniform argument.

## Reproduce

Python3.11+, SymPy, a C++17 compiler and Boost headers are required:

```sh
python -m pip install -r research/e8-r740-replica32/parent436/requirements.txt
E8_REPLAY_PHASES=1 python -B research/r740-hosted-rank149/verify.py /tmp/dual-eleven-new
```

The output directory must not exist. Set `BOOST_INCLUDE` if needed. The
`E8_REPLAY_PHASES=1` setting also regenerates the inherited unchanged local
Clifford phase recipes; otherwise their exact frozen evidence is hash-bound.
New eleven-stage phases are always regenerated. `--quick` skips only the
inherited exhaustive PR443 controls; every new check still runs.

Verification reconstructs the complete PR445 parent, then checks the new
bit kernel, official C++ records, integer source spans, positive Gram forms,
nested/reflected projectors, all9,340 unbanked global bit columns and
1,320 routes per supplier. Complex scalar composition combines the freshly
checked 800-column local theorem with ten exact global integer rows; its
phase audit verifies8,520 exact equalities. Both templates have independent
ownership and instruction-digest checks. There are22 bit and19 complex
mutation controls, plus all24 omitted bridge-shear controls on each side.
Both rational moment engines, both invoices, row bounds, six bootstrap
levels and all47 strict outer inequalities must pass.

`SOURCE.json`, `MANIFEST.json` and `EXPECTED.json` bind the source bytes and
exact results; `RECEIPT.json` records completed runs. No optimizer is needed.

## Scope

This is a conditional finite certificate. It retains PR442 idle-data hosting
and the inherited local mutable-basis, correlated dirty-helper, restored-work,
compressed-window, all-size compiler, tape/common-grid, precision, row-divisor
and analytic interfaces. The row-depth improvement is proved here within that
same reserve contract. No unconditional multiplication theorem, κ=1 result,
new Lean proof or earlier-assumption record is claimed.
