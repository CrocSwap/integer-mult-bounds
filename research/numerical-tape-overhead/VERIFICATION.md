# Replay record

Run the command from the repository root with the prerequisites in the [README](README.md).

```sh
python3 -I -B research/numerical-tape-overhead/verify.py
```

The script prints the checked-out Git SHA first. It verifies Lean 4.34.1 at `5045d0056413266e57c625dcd7c365b10e377c52`, Mathlib at `d13f23b723b8a846827a245b89c10fc7d3f11612`, all eight transitive Git revisions in Mathlib's manifest, and seven OpenAI source blobs. The C++ product oracle checks GMP 6.3.0. An empty temporary directory receives all 45 local Lean modules. The only compiled imports reused are the pinned toolchain, Mathlib and its dependencies. `leanchecker --fresh Review` replays the transitive expressions in a fresh kernel. [Lock file](dependencies.json) · [31 designated declarations](Review.lean)

## Results to compare

| Check | Reproducible result |
|---|---|
| Axioms | All 31 reports are subsets of `propext`, `Classical.choice` and `Quot.sound`. The integer native-height calculation uses only `propext`. |
| Native schedule | 29 historical vertices including zero. At each of the two adjacent tests, adding the test endpoint gives 30 candidates. The strict winner is $w=6201245580657120$, with $H(w)=890362700843914785456/158055205$. |
| $t=7519517465920987$ | Residual multiplied by $10^{12}$ is strictly between $-325836553$ and $-325836552$. |
| $t=7519517465920988$ | Residual multiplied by $10^{12}$ is strictly between $53248687$ and $53248688$. |
| Every later input | `LabelSharp.all_later` covers every real $t$ above the passing endpoint and every natural active width $X\le t+2$. `LabelSchedule.schedule_natural_clock` transfers this to the natural-log, coefficient-one estimate. |
| General search | $q=2$ uses the smooth-bound floor $1{,}572{,}864{,}480$. For $q=1000$ one obtains $j=54$ and $t_q=11664000000000000$, before the worked refinement. |
| Cumulative space | Two guarded families and the ordinary arenas give $453759460$ cells per $Nk$ in the written count. Lean proves $Nk\le8n$ and the final comparison, and bounds the union for the occupied wrappers under their head fences. |

The residual is the target binary-logarithmic allowance $t/1000$ minus the full charged exponent, including one extra bit for the natural-log conversion. The 24-term evaluator and the independent 52-term evaluator both use exact rational bounds and certify the two displayed signs. Lean independently proves the signs and the all-later inequality. A failed estimate at the preceding integer places no lower bound on the machine's running time. [First evaluator](checks/cutoff.py) · [Independent evaluator](checks/cutoff_independent.py) · [Endpoint declarations](S008/RecountTrueLabel.lean)

Representative output includes

```text
Axioms checked for 31 designated declarations.
PASS fresh kernel, 45 packaged modules.
t=7519517465920987   residual × 10^12 in (-325836553, -325836552)   peak width=6201245580657120
t=7519517465920988   residual × 10^12 in (53248687, 53248688)   peak width=6201245580657120
PASS arithmetic, adjacent cutoffs and four full-product fixtures.
```

The remaining checks exercise the small tape rule on 1,414 operand pairs, dyadic readout on 39 pairs, and the carry rule on 4,824 cases. Four full-product fixtures each use 1,000-bit operands, compare all 210 coefficients, and verify all 2,000 output bits. They cover all ones, a zero operand, a single set bit in each operand, and a dense input with leading zeros. Skipping inverse CRT changes 204 coefficients in the dense case. The fixtures force the large-branch arithmetic on a small legal box and execute the transform schedule on host arrays. They test product recovery; the tape-time and physical-space conclusions use the distinct arguments in the [review notes](REVIEW.md).
