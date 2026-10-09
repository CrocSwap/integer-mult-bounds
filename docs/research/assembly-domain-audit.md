# Assembly parameter ranges and scoped ceilings

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-09. Apache-2.0.

**No improved multiplication bound or enlarged theorem domain is established.**
The published conditional witness remains
`330942774629799/500000000000000000 = 0.000661885549259598`.
The original finite package, its verifier and its parameter restrictions remain
unchanged. This note separates a sufficient parameter domain from costs that
continue to constrain the assembly if that domain is enlarged.

## Three different restrictions

Write `a` for the effective bit saving admitted to the layer, `b` for the
complex saving, `q=a(1-2h)`, and `epsilon=(1-h)/(1+q)`, with positive backoff
`h`. These are the parameters of the selected
[balanced assembly](../../research/coordinated-frames-and-entrance-banks/arithmetic/balanced_shared.py).

| Restriction | Meaning and consequence |
|---|---|
| `a < (1-beta)b < b < 1/32` | The currently enforced supplier ordering and small-saving domain. Together with the balance below, this gives `kappa < 1/33`. |
| `kappa < epsilon*q`, `kappa < 1-epsilon` | Competing layer and normalization/assembly margins. Since `q<a`, they imply `kappa < a/(1+a)`. This is a scoped conversion bound, not a universal multiplication bound. |
| `r < 1/4`, `kappa < r-delta`, `delta>0` | The retained Gaussian parameter range, where `alpha^2=Theta(p^r)`. It independently gives `kappa < 1/4`, even if the explicit `b<1/32` restriction is removed. |

For the second row, the maximum over `0<epsilon<1` of
`min(1-epsilon, epsilon*a)` is `a/(1+a)`. The selected construction approaches
this balance with strict backoffs; it does not attain the supremum.
Its identities give `1-epsilon-G=h` and `r=G+h/2`, where `G=epsilon*q`.
For the third row, the fifth margin is
`min(1-epsilon-delta,r-delta)` and must exceed kappa.
No optimization or numerical extrapolation is needed for either implication.

The logarithmic exponents corresponding to the two fixed domain caps are
strictly above `32/33` and `3/4`, respectively. Neither is an unconditional
lower bound on integer multiplication. The Gaussian range could itself be
revisited, but changing it requires another dependency audit.

## What the number 1/32 does, and what has not been established

The selected checker explicitly tests `b_below_one_over32 = 1/32-b`.
The condition is also present in the earlier
[structured-bulk checker](../../scripts/structured_bulk_assembly.py) and
[copied-fixed balanced checker](../../research/copied-fixed/balanced_assembly.py).
It is not derived from a rank identity or a finite-network impossibility
theorem in those implementations.

Keeping `a<b<1/32` puts the parameter choice comfortably inside several
auxiliary ranges, including Gaussian width, short-record fallback and
geometric comparisons. This is consistent with a conservative sufficient
domain. The inspected sources do not establish that **1/32 is the sharp
threshold**, nor does this audit establish why that particular constant was
originally chosen. Its earliest provenance has not been exhaustively traced.

The distinction is testable. With hypothetical suppliers and positive bridge
slacks, the unchanged arithmetic body has the following outcomes. All rows
use `h=10^-8` and `beta=1/1000`.

| Hypothetical a | Hypothetical b | Proposed kappa | Failed displayed constraints |
|---:|---:|---:|---|
| 0.02 | 1/32 | 0.019 | Only `b_below_one_over32`, at equality |
| 0.04 | 0.05 | 0.038 | Only `b_below_one_over32` |
| 0.30 | 0.31 | 0.23 | Only `b_below_one_over32` |
| 0.40 | 0.41 | 0.28 | `b_below_one_over32` and `alpha_below_one_fourth` |

For each of the first three rows, all other 46 displayed constraints are
strictly positive. The normal fail-closed arithmetic rejects **every row**.
The final row demonstrates why deleting the small-saving restriction would
not remove all limits on the parameter range.

**These examples supply no finite network, valid new bridge, analytic
extension or multiplication algorithm.** In particular, kappa=0.038 and
kappa=0.23 are diagnostic inputs, not results of this repository.

## Diagnostic implementation and evidence boundary

The [diagnostic](../../scripts/audit_assembly_domain.py) pins the exact source
bytes and compiles the selected `assembly` function body without changing
its equations. For hypothetical rows only, it substitutes an explicitly
assumed bridge with positive scalar/row slacks, and records failed
requirements while allowing evaluation to finish. It then rechecks that a
strict requirement callback rejects each row with that same assumed bridge.
This observational execution is deliberately **not** a verification interface.

The positive control separately replays the published parameters with the
real numeric bridge validator and strict requirements, comparing all 47
rational slacks to the frozen certificate. That is an arithmetic and bridge
regression, not another replay of the complete finite word.

The [receipt](assembly-domain-audit.json) records exact fractions, source
hashes and failures. Tests cover the published control, the strict `1/32`
boundary, the independent Gaussian restriction, invalid leaf ordering,
excess kappa, source mutations and rejection of floating inputs. The standard
isolated test discovery includes the new test module.

```sh
python3 -B scripts/audit_assembly_domain.py --check docs/research/assembly-domain-audit.json
python3 -B -m unittest discover -s tests -p test_assembly_domain.py -v
make selected-record-check
```

## What an extension would require

1. Derive a larger sufficient parameter region from all displayed inequalities,
   with explicit strict backoffs. Passing a few rational examples is not a
   proof for a whole region.
2. Trace the supplier, stopping, router, Gaussian/precision, fallback,
   prime-supply, row-stock and uniform setup lemmas for assumptions absent
   from the arithmetic table. In particular, the bridge is not free: the
   hypothetical diagnostic does not verify it.
3. Audit certificate-enclosure ranges independently. For example,
   [the selected moment engine](../../research/coordinated-frames-and-entrance-banks/arithmetic/interval_moment.py)
   searches up to `denominator//32`, and its exponential enclosure requires
   an argument below `1/4`. Enlarging the theorem domain may require new
   range reduction or enclosures; simply editing the search bound is unsafe.
4. Supply actual stronger finite constructions and rebuild their complete
   paid bridges before claiming any improved kappa.

No production constraint should be removed on the strength of this note.
The current supplier is far below `1/32`, so relaxing the guard alone would
not improve the selected result.

## Consequences for the research roadmap

For a logarithmic exponent below 0.99, the balanced conversion requires
`a>1/99`, and the complex supplier must be sufficiently stronger to retain
leaf-ordering slack. This target lies below the current `1/32` cap; the
principal missing ingredient is stronger suppliers, not removal of this guard.

For an exponent of 0.5, extrapolating `1/(1+a)` alone is misleading.
That expression tends to 0.5 as `a` tends to one, but these values are outside
the current domain and eventually violate the separate Gaussian range.
Even after removing `1/32`, retaining `r<1/4` still excludes exponents at
or below 0.75. Approaching an endpoint with a family of algorithms also
does not establish an exact endpoint big-O bound without uniform constants.
A route to 0.5 therefore needs further analytic/assembly changes as well as
new finite primitives.

## Attribution

The balance `a/(1+a)` is already derived in the retained
[RaD / hipotures report](../../references/semantic-bulk/rad20/reports/downstream-semantic-bulk-assembly.md).
The inherited assembly also credits Zhihao Chen, James Chang and subsequent
community integrations. Romain Hedouin's
[PR #183](https://github.com/CrocSwap/integer-mult-bounds/pull/183) independently
organizes the fixed-domain arithmetic ceiling and constraint dependencies.
This note acknowledges that work without importing its implementation or
claiming the balance formula as new. The selected PR186 source and all its
contributor notices remain intact. This addition supplies a narrower domain
diagnostic and clarifies what would still need proof outside that domain.
