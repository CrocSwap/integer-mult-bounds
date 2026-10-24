# Cross-copy idle-axis hosting on #442: conditional κ ≈ 1.3307340·10⁻³

This package lets a hosted helper residual lie across the pending coordinates of two copies (two data families) of
the same idle child. The two copies share the child's window, so #442's hosting lemma applies to each piece. Every
child's capacity, copies × rank, is then a multiple of the residual width, and the idle remainder children almost
vanish.

Neither local word changes: complex #433 (R = 560, m = 73), bit #434 (R = 747, m = 64). The windows are #442's.

**Result:** κ = 1330733966732373/10¹⁸ ≈ 1.330733966732373·10⁻³, bit-bound, **+17.44 % over #434** and +7.53 % over
#442 (1.2375517·10⁻³).

| supplier | #442 saving | this saving | live stock | hosted residuals |
| --- | --- | --- | --- | --- |
| bit, m = 64 | 1.239085·10⁻³ | **1.332507·10⁻³** | 9,457 → 8,592 | 39,568 → 46,160 (12,496 split) |
| complex, m = 73 | 1.267453·10⁻³ | **1.437532·10⁻³** | 8,400 → 7,680 | 34,560 → 40,320 (13,720 split) |

[PROOF.md](PROOF.md) gives the extension, its argument from #442's two facts, and its scope; §7 answers the trace note of #451, and `toy_two_family_check.py` checks the two-family program identity exactly in that note's model.

## Verify

```sh
python3 -B research/cross-copy-hosting/verify.py /absolute/new/output
```

- Python 3.11+ and the standard library only (scipy only for `--discover`, which recomputes `SELECTION.json`).
- The output directory must not exist.
- It runs #434's complete `verify.py` from scratch (about two minutes), then both generators, the independent audit
  (twelve mutation controls) and the exact assembly, and compares every value with `EXPECTED.json`.

## Scope and credits

Conditional, like its parents. The new review point is the two-family slot; #442's data-stream hosting and all
inherited interfaces remain assumptions. No Lean proof or unconditional theorem is claimed.

Builds on and runs unchanged: #442 (DaysSky, idle-axis hosting; its windows and bank tilings are reused), #434 (Rohan
Arun), #433 (icekylinx), #435/#417 (chafreaky), #426 (ai-nanachi), #425/#386 (Zhihao Chen), #370 (Dylan Crow),
Jacob Sussman's E8 unit and interfaces. The cross-copy selection, generators, audit and assembly were prepared with
Claude (Anthropic) assistance.
