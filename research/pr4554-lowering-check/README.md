# Independent check of #4554: finite-precision lowering of linear programs (`PHASE-TABLES.md` §2, §4)

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

This is the last component of Dugongue's #4554 (head `4f46c6a9`) that had no independent check; #4556–#4562 cover the rest. `PHASE-TABLES.md` §2 proves a generic sufficient lowering. A linear straight-line program with scale constants `|c| ≤ C0`, data depth `≤ a·log₂(N+2)`, inputs `≤ N^b` and prepared-scalar errors `≤ ε`, with every data gate rounded within `ε`, has node errors at most `ε(V+1)(C0+3)^(h+1)` and magnitudes at most `N^b C^h`. §4 bounds the perturbed shear denominators. The text is vendored as `PR4554-PHASE-TABLES.md` (blob `2dab8f3e`, SHA256-pinned).

## Results

All checked claims are confirmed.

1. **Induction steps, exact rationals.** For every `h ≤ 200` and `C0 ∈ {1/2, 1, 3/2, 2, 7/3, 10}` (1,200 cases):
   - `2C^(h−1)` and `C0·C^(h−1)` are both at most `C^h`, with `C = max(2, C0)`;
   - the closed form `B_h = ε(V+1)(C0+3)^(h+1)` dominates both the add step `2B_(h−1) + ε` and the scale step `(C0+1)B_(h−1) + εV + ε`.
2. **Random programs.** 60 random layered ADD/SUB/SCALE programs (`N ≤ 32`, `b ≤ 1`, `C0 ≤ 2`, `a ≤ 2`, `P ∈ {16, 24, 32}`) ran in exact rationals against a copy with perturbed prepared scalars and gates rounded toward zero. At every node the error is at most `ε(V+1)(C0+3)^(h+1)` (worst ratio 0.0094), and the exact magnitude is at most `N^b C^h`.
3. **FFT instantiation.** On radix-2 FFT DAGs (depth `2 log₂ N`, `C0 = 1`, `N` up to 512), the observed rounded-twiddle error lies below the sharper `FFT-ERROR.md` chain (checked in #4557), which in turn lies below the §2 bound. **Observation:** the §2 bound is valid but very loose here, 2·10^9 against an observed 3·10^−6 at `N = 512`. That fits its role as a generic sufficient certificate: it shows `O(log N)` bits suffice, not how many.
4. **Bilinear extension and §4.**
   - `|âb̂ − ab| ≤ |a|E_b + |b|E_a + E_aE_b` holds in 2,000 random cases.
   - Shear denominators perturbed by up to 1/4 keep `|t1| ≥ 3/4` and `|t2| ≥ 1/2`. The exact identities behind this are checked in #4562.
5. **Binding.** 5 statements are bound verbatim to the vendored text.

## Verify

```text
python3 -B research/pr4554-lowering-check/verify.py
```

This runs in about 1 s with the standard library only.

## Limitations

- **Finite checks.** The random programs and FFT DAGs are finite. The universal statement rests on the written induction, whose steps are checked exactly.
- **Floating point.** FFT comparisons use double-precision floats, whose rounding is far below the compared bounds.

## Open next questions

- None new for #4554's constructive components; with #4556–#4562, each now has an independent check. The PR's own stated gap remains: a faster native cyclic transform satisfying `NATIVE-OUTER-ASSEMBLY.md`'s contract.

Credit: Dugongue (#4554). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
