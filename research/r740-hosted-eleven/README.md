# Eleven-stage hosted R740 supplier

Conditional **κ = 0.001263365464781156**, **1.3877% above PR444**.
The bit saving is `1264963576077378514188 / 10^24`. The freshly rebuilt
PR442 complex supplier remains `1267453159029119 / 10^18`; the bit side binds.

This uses PR443's unchanged R740 rank138 local word in **eleven compressed
stages**, dimension **78**, and **eight replicas**. PR442 idle-data hosting
places **all 65,120 helper occurrences** on pending idle coordinates. There
are no helper banks or padding children. The emitted template has 88 local
calls, 9,600 live families, 9,609 physical families and rank deficit 3,264.

The largest child has rank 56, so halving needs three levels. The new finite
invoice charges the 153-bit prefix at 192 bits and the 513-bit three-level
coefficient at 1,024 bits. An elementary orthogonal-cover count gives complete
row coefficient 19,431, within the unchanged 20,161 allowance. The old coarse
matrix-count estimate would not fit; `PROOF.md` proves the sharper bound.

## Reproduce

Python 3.11+, SymPy, a C++17 compiler and Boost headers are required:

```sh
python -m pip install -r research/e8-r740-replica32/parent436/requirements.txt
python -B research/r740-hosted-eleven/verify.py /tmp/r740-eleven-new
```

The output directory must not exist. Set `BOOST_INCLUDE` if needed. `--quick`
skips only PR443's inherited exhaustive mutation suite; all new checks and the
full hosted complex reconstruction remain enabled. No optimizer is required.

The wrapper reconstructs PR444, generates the 78-dimensional geometry and all
88 calls, replays all 9,340 unbanked scalar columns, rejects each of the 24
missing bridge shears, and independently audits the changed schedule, owners,
idle windows, residual routes and remainder children. It rejects 22 template
mutations and checks the complete renamed instruction digest. Two rational
moment engines, both finite invoices, three-level halving, six bootstrap levels,
47 strict outer inequalities and adjacent-grid/parameter controls must pass.
Source bytes and exact results are frozen by `SOURCE.json`, `MANIFEST.json`
and `EXPECTED.json`. `RECEIPT.json` records each completed run.

## Scope

This is a conditional finite certificate. PR442's idle-data hosting extension,
the inherited all-size compiler, correlated dirty-helper, restored-work,
common-grid, precision and analytic interfaces remain assumptions. The new
finite geometry, column identity, stock count and numerical inequalities are
explicitly checked. No unconditional multiplication theorem, κ = 1 result or
new Lean proof is claimed.
