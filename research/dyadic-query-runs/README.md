# Optimal dyadic-run BIT query batching

Batching centered native BIT shears on the same target removes repeated
ADDRESS-layout restoration boundaries. For a finite set J of dyadic indices,
with r indices in c consecutive runs, the completed batch uses **2r+c ordinary
recursive children instead of 3r**, with unchanged source, arbitrary dirty
spectators and no extra full private row. This count is optimal in the
specified target-query/source-XOR alphabet, including off-support excursions.

**Status: recursive-interface research construction; no new kappa.** The
selected PR890 result and `upstream/` are unchanged. This is not a new supplier,
a general circuit lower bound, a measured speedup or a formal multiplication
theorem. The complete coefficient-aware work/space recurrence and inherited
obligations are in [PROOF.md](PROOF.md), especially sections 1, 3 and 5.

OS assignment seed **55** selects `J={0,1,2,4,5}`. Its two runs give:

| Complete cost item | Separate PR840 pairs | Shared runs |
|---|---:|---:|
| Full ordinary recursive children | 15 | 12 |
| Ordered affine events | 90 | 72 |
| Full source-XOR scans | 10 | 10 |
| Additional full private rows | 0 | 0 |

Every query is lowered to six explicit affine events and one separately paid
child, including all layout return edges. Coefficient preparation and stream
costs differ; the count saving does not guarantee a finite runtime saving.
For three isolated indices `{0,2,4}`, the exact count is nine and this
mechanism saves nothing. Allowing nondyadic queries or a modulus-specific
program can beat the restricted count; both boundaries have concrete controls.

From the repository root, with Python 3.9+ and the standard library:

```sh
python3 -I -O -B research/dyadic-query-runs/verify.py
python3 -I -O -B research/dyadic-query-runs/test_package.py
```

Expected first lines:

```
PASS_DYADIC_QUERY_RUNS cases=63 seed=55 children=15->12 affines=90->72 XOR=10
PASS_DYADIC_QUERY_RUNS_PACKAGE relocation=1 regeneration=2 corruptions=8
```

The verifier imports no constructor or predecessor implementation. It checks
all 63 nonempty subsets of indices 0 through 5, exact Laurent endpoints,
native rational/modular columns, both full ADDRESS domains modulo 3 and 5
with two intervening binary spectator fields, and 252 dirty forward plus
252 inverse executions. A separate bounded shortest-walk census admits
off-support visits for all 15 nonempty subsets of indices 0 through 3.
Its finite coverage is distinct from the written universal proof. Fifteen
obligation-specific rejection controls and two positive scope controls pass.

[CERTIFICATE.json](CERTIFICATE.json) contains every literal word, baseline,
native lowering and recounted invoice. [EVIDENCE.json](EVIDENCE.json) contains
the deterministic complete receipt. `build.py` regenerates only this package's
certificate; `verify.py --write-evidence` regenerates its receipt. Ordinary
verification is read-only. [SOURCES.json](SOURCES.json) pins the base, retained
predecessors and inspected PR heads; [VALIDATION.md](VALIDATION.md) records
executed checks and limits; [CLAIM.md](CLAIM.md) records selection and handoff.

Exact base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`. Direct predecessor:
[PR840](https://github.com/CrocSwap/integer-mult-bounds/pull/840) at
`da2cd0dd2229e08b61b174a8835a2c2bb99d2230`. The new result batches several of
its centered pairs, rather than reproving the single-pair theorem. It does
not consume or combine the dirty connector results in PR889/934/943/944.

Prepared by **Ross Richardson (@RossRichardson)** with substantial **OpenAI
Codex assistance**, under Apache-2.0. Credit Wentao Li/PR840, Karl Appel/PR521,
commdata2338/PR677 and the retained OpenAI tape framework. Full attribution,
original notices and source licenses are in [NOTICE.md](NOTICE.md) and `vendor/`.
