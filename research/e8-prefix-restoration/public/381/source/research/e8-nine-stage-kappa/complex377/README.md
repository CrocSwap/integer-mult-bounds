# Compressed nine-stage complex component

This research package raises the **conditional complex coarse saving** from
`876248285600677/10^18` to **`999240641319551/10^18`** (about 14.04%)
using the same pinned E8 local word. It supplies a compressed nine-stage
construction, exact phase corrections, whole-block banks with paid padding,
a finite execution template and two independent rational pricing checks.

**This is a complex-side component result.** The frozen #361 bit supplier still
gives final `kappa = 804849251275843/10^18`. The component value exceeds
`2^-10`, but the combined integer-multiplication exponent does not.

## Reproduce offline

Python 3.11 or later, standard library only, with assertions enabled:

```sh
python3 -B research/nine-stage-complex-e8/verify.py --work /tmp/nine-stage-e8-check
```

Choose a work path that does **not** already exist and is outside this package.
The verifier checks all input hashes, copies inputs to that directory and
rebuilds its evidence without network access or pre-existing PASS receipts.
Typical runtime is about three minutes. Its final receipt is `VERIFICATION.json`.

The eight checks cover source integrity; fresh local scalar/frame admission;
data, banks and profile; exact Clifford adapters; data and cover phases;
the global template and finite invoice; independently decoded template pricing;
and the numerical outer assembly with the fixed bit value.

## Construction and evidence

The local E8 word has dimension 9, 120 ports, 783 helpers and copied-rank loss
72. Four data pairs and nine local stages are routed through dimension 73.
Each bank contains eight entire rank-9 residuals and one paid rank-1 padding
factor. Eight replicas give 7,680 data families and 7,047 bank families, for
14,727 live recursive families. Including reused private work gives 15,520
physical streams per cover.

The implementation includes the exact Clifford phases omitted by a
rank-only calculation: endpoint translations, the final `X_q` correction,
and the all-live-family cover correction `X_delta(g)`. It checks 946 local
frames, 3,120 directed transitions and 240 endpoint adapters, with exact
Gaussian arithmetic fixing global scalar phase. The fresh local invocation
replays all 1,023 dirty live input columns. The global finite template has
72 local invocations and 1,242,936 local events.

The paid profile is:

| Child rank | Calls |
| ---: | ---: |
| 1 | 157599 |
| 2 | 43488 |
| 3 | 37296 |
| 4 | 10080 |
| 5 | 15480 |
| 6 | 23832 |
| 7 | 3096 |
| 8 | 7488 |
| 9 | 576 |
| 16 | 3840 |
| 32 | 3840 |
| 48 | 3840 |

Thus `rank_mass = 1072575` and `73 * 14727 - rank_mass = 2496`.
Both rational moment engines admit the stated complex saving and reject the
next `10^-18` grid point. The largest child has rank 48, so the argument uses
**two-level halving**, `73^2 > 2 * 48^2`, with its depth and finite-work
overcharges explicitly included. It does not assert the false one-level
half-shrink inequality.

Relevant files:

- [Construction argument and assumptions](work/complex-nine-native/PROOF.txt).
- [Exact local Clifford arithmetic](work/odd-stages/clifford_exact.py) and
  [adapter verification](work/odd-stages/verify_clifford_frames.py).
- [Data and cover phases](work/odd-stages/data_phases.py).
- [Global template and invoice](work/odd-stages/global_nine.py).
- [Independent template decoder and pricing](work/odd-stages/audit_nine_template.py).
- [Fixed-bit outer check](work/odd-stages/outer_fixed.py).

Phase, padding, bridge and terminal-exchange omission controls are included.
The unchanged-bit outer check has 47 strict numerical constraints and rejects
the next final-kappa grid point. That check is a consistency check, not a new
bit-side construction certificate.

## Scope and provenance

The construction retains the pinned local E8 invocation theorem, general
Clifford/compiler interfaces, complete-stream tape primitives, common fine-grid
precision, row allowance and analytic recurrence interfaces. This package does
not build a new Lean kernel proof, enumerate the astronomical cover, regenerate
the E8 certificate producer, or establish an unconditional multiplication
theorem. The finite template and the written argument have the scope stated in
their receipts and proof.

The unchanged E8 certificate is pinned at SHA256
`4b92f00fc7454b9b15e6d71a3b05062792eacca0a0ca4efee46f87827d57c8aa`,
from Jacob Sussman's E8 source at
`9c94857bbaee886f8649edee0bc2d3c738f9555e`, preserved through the fixed
[#352](https://github.com/CrocSwap/integer-mult-bounds/pull/352) source and
local finite-invoice audit. The unchanged bit comparison is frozen at
[#361](https://github.com/CrocSwap/integer-mult-bounds/pull/361), head
`2eef66d847be4441e4f3af681ee7e94dd9b19316`.

Dependency licenses, notices, assistance disclosures and source manifests are
preserved in `work/native358/vendor/complex-reserve/`. They retain the local
E8, five-stage, completed-bank, compiler and analytic-framework credits.
The new nine-stage construction, verification code and argument were prepared
by Zhihao Chen with OpenAI Codex assistance. Apache-2.0; inherited notices and
licenses continue to apply.
