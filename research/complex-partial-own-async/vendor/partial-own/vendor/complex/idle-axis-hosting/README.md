# Idle-axis hosting on #434: conditional κ ≈ 1.2375517·10⁻³

This package moves whole dirty-helper residuals of both E8 suppliers from bank streams onto the pending coordinates of
idle data families. Those coordinates would otherwise be advanced by idle children later in the nine-stage template.

Neither local word changes:

- complex: #433's split-centre word, R = 560;
- bit: #434's early-reset kernel word, R = 747.

**Result:** κ = 618775866623647/(5·10¹⁷) ≈ 1.237551733247294·10⁻³, bit-bound, **+9.218% over #434**
(1.133100552284434·10⁻³).

| supplier | parent saving | hosted saving | live stock | max child |
| --- | --- | --- | --- | --- |
| bit, m = 64 | 1.134386·10⁻³ | **1.239085·10⁻³** | 14,259 → 9,457 | 42 → 8 |
| complex, m = 73 | 1.183987·10⁻³ | **1.267453·10⁻³** | 12,720 → 8,400 | 48 → 8 |

**Why it gains.** Idle advance children are about a sixth of the paid cost of the compressed window. A dirty helper
residual acts on its stream as the same kind of coordinate factor an idle child applies. Hosting the residual there
removes the bank stream, its padding, and that part of the idle child, and the rank deficit stays at 2496.

The validity condition is a window: the host family must be untouched between the hosting invocation and its
scheduled advance. [PROOF.md](PROOF.md) gives the argument and its scope.

## Verify

```sh
python3 -B research/idle-axis-hosting/verify.py /absolute/new/output
```

- Uses Python 3.11+ and the standard library only.
- The output directory must not exist.
- It runs #434's complete `verify.py` from scratch, then the bit and complex hosting generators, the independent
  audit (nine mutation controls) and the exact assembly. It compares every value with `EXPECTED.json`.
- `SELECTION.json` freezes the integer-programme choice. `--discover` on either generator recomputes it with scipy.

## Scope

This is conditional, like its parents. The extension of the correlated dirty-bank interface to idle data streams is
the new review point. All-size compiler, compressed-window, restored-work, tape/common-grid, precision and analytic
interfaces are inherited. No Lean proof or unconditional theorem is claimed.
