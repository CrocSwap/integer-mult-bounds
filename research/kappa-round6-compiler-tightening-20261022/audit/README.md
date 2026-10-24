# Independent audit of the compiler reserve tightening

**PASS.** The complete unchanged native/controller invoice supports the tested
saving `0.00302177581` with contraction reserve `10^-11`. Its strict outer
transfer supports claimed conditional kappa `0.0030217758`, an increase of
`0.0000000158` over `0.00302176`. No material discrepancy was found.

This audit changes no native word, helper credit, controller, external
hypothesis, or raw moment root. It certifies the new numerical choice within
the retained conditional framework. It does not prove an unconditional integer
multiplication theorem.

## Independent checks

`replay.py` reconstructs the paid profile from both actual native words and
reconstructs productive endpoints from all 408 arbitrary native helpers. It
then assembles all 18 local invocations, 15 query shears, controller idle costs,
and controller diagonal endpoints directly from the frozen physical controller.
The resulting invoice has 10,928 productive fields, 64,404 paid calls, and
rank-mass surplus 752. Owned centers are paid and receive no productive credit.

The checker verifies that the producer arithmetic script differs from its
pinned predecessor by exactly the four declared literal replacements. It does
not invoke that producer's moment, pricing, or outer-ledger functions.

Real moments are independently enclosed with the retained second rational
interval engine, using its 256-bit outward rounding and separate logarithm and
exponential series. The computed intervals fit the producer's claimed bounds.
The reserve `10^-9` fails at the new tested saving; `10^-11` passes. Both tail
ratios are below `97/100`, and `(97/100)^128 < 1/16`. With product power 1024,
Bernoulli's inequality and all four `2^-32` allowances give the normalized bound

```
104857600097656251 / 104857601073741824 < 1.
```

The independent proof also checks the coarser rational witnesses used by Lean:
the target lower bound and paid upper bound leave contraction slack
`273771612285125076737 / 25000000000000000000000000` after the new reserve.
It checks the signs at both recorded raw-root bracket endpoints without a root
search or monotonicity assumption.

For the finite compiler, it checks the sufficient integer predicate
`(H+1)^1000 < 2^55099` at `H = 38569300000000000`, the eta capacity inequality,
initial range, shifted-exit capacity, and nonrecursive work allowances. No
minimality claim is made for this very large finite threshold.

All 54 strict outer formulas, four functional formulas, and nine margin
formulas are independently evaluated as exact rationals from the pinned source
expressions. Both stock exponents are also checked to lie strictly between
zero and one. The ordinary BIT allowance is unchanged. Four mathematical
controls fail in their expected places: old BIT saving, closed uniform saving,
unfunded claimed endpoint, and closed epsilon.

## Lean evidence and its boundary

The parent's successful fresh replay contains **four new modules and 31 axiom
reports**. The audit checks the exact source, log, and object hashes, zero exit
codes, compiler executable hash, new 262144 KB compile-stack argument, and the
axiom reports against the source declarations. Allowed axioms are only
`propext`, `Classical.choice`, and `Quot.sound`.

The replay separately reuses **31 native modules with 14 printed axiom
reports**. Their source/log/object hashes and recorded predecessor object
dependencies match the pinned native receipt. Those native modules were not
freshly compiled for this tightening. The independent auditor did not run a
second successful Lean compilation.

The four new sources establish real contraction and tails, real compiler
capacity inequalities, exact arithmetic/transcribed outer formulas and finite
threshold, and an aggregate binding to the existing finite native invoice and
productive helper endpoints. The aggregate theorem explicitly stops at this
conjunction. Native amplitude/phase semantics, controller extraction, compiler
transfer, tape, precision, and recovery remain within their stated external
proof boundaries.

Pinned fresh Lean receipt SHA-256:
`fdcfe850605ba339c008b35306f438a731e31a891cf6625d2b9cc8d0fb67fb61`.

Pinned native reuse receipt SHA-256:
`fc9b6aac05556f63d8800154773ce9dc98654a490e0b9d94888593bec6a78590`.

Pinned arithmetic receipt SHA-256:
`b4f720a7ccbb5b46e472eaf85dc8739a40598986f19b37d26c4f9ecfbd31f0de`.

## Actual-verifier rejection controls

`controls.py` imports the actual unchanged verification wrapper and runs three
isolated corruptions in temporary copies under `audit/.scratch`. Its `HERE`
points to the temporary package while native sources, runtime, canonical
generator sources, and root remain the original pinned tree. Relocated loader
path globals are restored; no verification predicate is replaced.

Each corruption is rejected before any Lean compilation:

| Corruption | Actual wrapper rejection |
| --- | --- |
| Claimed kappa changed | `Saving contract` |
| Rank-one paid count incremented | `Complete arithmetic recomputation` |
| Numerical proof coefficient changed and prepared hash updated | `Nonreproducible generated TightenedNumerical.lean` |

The harness guards against reaching Lean compilation, checks original
source/data hashes remain unchanged, and verifies scratch paths before cleanup.
These expected failures test artifact binding; they do not constitute a
successful Lean replay.

Pinned actual verifier SHA-256:
`a69d5f4c628ed87a009d6ffb9c67adab08db237420b637ad21f60fa52f0ff832`.

## Reproduce

From the checkout root, using the shared global Python 3.14 interpreter:

```powershell
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round6-compiler-tightening-20261022/audit/replay.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round6-compiler-tightening-20261022/audit/controls.py
```

`AUDIT.json` and `CONTROLS.json` contain the detailed source pins, exact
results, and fresh-versus-reused evidence separation. These two commands write
only their audit outputs and isolated scratch files. They require the retained
source tree and recorded native/Lean objects; they do not download artifacts.
