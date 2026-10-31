# Fixed-capacity packing ceiling after the two release swaps

Local-only exact arithmetic certificate. The relaxed cap is an upper limit within the fixed word and helper inventory model; it is not a higher achieved kappa. No new allocation or supplier admission is claimed.

The changed local bill is `{1:2437,2:724,3:226,4:102,5:20,8:8}` per invocation. The 408 helper widths remain `{4:26,5:2,6:18,7:52,8:97,9:213}`, with nine invocations per replica. The fixed capacities per replica remain `{8:672,16:448,32:448,48:448}`, dimension 73 and live stock `896*T`.

Within that class, the continuous packing relaxation has moment root strictly between:

```
0.001730418899766071163804
0.001730418899766071163805
```

The independently re-evaluated literal T530 profile is:

```
{1:11747920,2:3453480,3:1112042,4:486540,5:103690,8:38160,48:202828}
```

Its moment root is strictly between:

```
0.001730394391813963415120
0.001730394391813963415121
```

Thus the literal moment-root value achieves 99.9985836983108% of this relaxation's root. The remaining possible root headroom in this fixed-capacity model is about `2.4507952107748684e-8`. These percentages compare the two roots themselves; they are not a claim that the packing is chronologically optimal or that this fraction of all possible multiplication improvement has been exhausted.

## Exact certificate

The PR3630 basis and inventory are retained. Its feasible primal idle bill per replica is:

```
{1:234,3:261/4,5:57/4,48:1531/4}
```

For every `b` in the displayed ceiling bracket, the script enumerates all 2,551 legal capacity/width count patterns and derives their exact reduced-cost coefficient vectors from the 10-by-10 rational basis inverse. Twelve patterns have symbolically zero reduced cost; the other 2,539 have a strictly positive rigorously enclosed lower bound throughout the bracket. The minimum lower bound is approximately 0.00408442896 (the exact rational is in the JSON receipt).

Let `x` be any feasible fractional packing for `T` replicas, with the stated capacity counts and helper inventory. The nonnegative reduced costs imply its idle moment is at least the displayed basis's idle moment times `T`. Adding the fixed local bill preserves this inequality. Normalization by `73*896*T` cancels `T`. At the upper bracket endpoint, the relaxed normalized moment is rigorously greater than one, so every such integral or fractional packing also has moment greater than one there. Consequently every feasible packing in this class has moment root below that endpoint, for every positive integer `T`.

The positive-binomial interval engine uses integer fixed point and positive geometric tails; it computes no floating logarithms or exponentials. The exact signs at adjacent 10^-24 grid points are recorded for both the relaxed and literal profiles. Pattern coefficient SHA256 is `11c3cadeeda1d3db40eb479af6835131f5e61bf26f63f2a62ec54de41a9f5c3a`.

## Reproduction

This directory is self-contained and requires only Python 3.10 or newer and its standard library. No network, repository checkout, or installed dependency is required. From this directory:

```sh
python3 -B check_retimed_cap.py
# Optional explicit fresh output directory:
python3 -B check_retimed_cap.py --out /fresh/retiming-cap
```

Runtime was approximately two seconds with Python 3.11.6 on macOS. The script and two small retained source files are sufficient for offline reproduction. Its validation conditions remain active under `-O`.

- `check_retimed_cap.py`: adapted exact enumeration and dual verification.
- `RETIMED-PACKING-CAP.json`: complete rational interval and source-hash receipt.
- `cap-source/pr3630-check_budget.py`: unchanged predecessor source, PR3630 at `bcac7fe04b9b7f7f5d3c27d620561f96c4ae5608`.
- `cap-source/binomial.py`: unchanged PR3531 interval engine at `550a660a97308d3aeb3620ee1f4218f77e2c2742`, SHA256 `03eebf2be23cab07e5f9e978980fee7b17e10847da5720c3e4e0adb243e8e4fa`.

## Scope and credit

This is the modern fixed-supplier primitive scope, where a resulting conditional kappa is approximately the moment saving `b`; it is not the obsolete transformed-exponent interpretation. It bounds this stated packing relaxation only. Chronology and physical-family attainment of the fractional optimum remain unknown. The current literal profile's ownership and operator-admission evidence is supplied separately; this arithmetic script does not authenticate that full external source closure. Native implementation, rounded recursive precision, physical hosting, all-size transfer and outer release remain separate obligations.

Credit Ross Richardson and the separate review underlying PR3630's exact dual; PR3531's positive-binomial engine; PR3605's staged entering helpers; PR3626's literal T530 ownership; PR3133/PR3148 and their retained contributors. The present local-profile change is the sibling circuit agent's two commuting release swaps, independently invoiced in the sibling release-retiming deliverable. Substantial OpenAI Codex assistance. Apache-2.0 inherited from the source repository.

## Publication adapter

The verifier now writes to a fresh temporary directory by default, or the new external directory supplied with `--out`; it does not rewrite the retained `RETIMED-PACKING-CAP.json`. Only output routing and documentation were adapted. `PUBLICATION-PROVENANCE.json` records original-to-public hashes; inherited sources remain unchanged. This component has no external repository inputs (`PUBLIC-INPUTS.json`).
