# Scoped check of #4610: endpoint frames preserved, profile arithmetic and moment positivity

**Task:** independent-moment (independent check). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## The claim

intqwq's #4610 (head `4b4c75bc`) claims a conditional κ of 37769/12500000 = 0.00302152. The construction:

- substitutes 34 of PR4470's 72 independent warp generators with other invertible maps;
- relabels 422 scalar frames;
- keeps every scalar opcode and every external interface.

Its paid list changes from Pold = 2237 H1 + 388 H2 + 494 H3 + 147 H4 + 36 H5 + 8 H8 to Pnew = 2201 H1 + 412 H2 + 506 H3 + 135 H4 + 36 H5 + 8 H8.

## What is checked here

Nothing is imported from #4610. Its emitted `ACTUAL-WORD.json.gz` is vendored with blob `79dad65b` and pinned by SHA256. Its canonical payload hash equals #4610's frozen value `4409d2d9…`.

### 1. Endpoint frames

This is the test #4596 failed (see #4604). For all 632 roles, the emitted word's **start and final frames equal PR4470's** as subspaces of F₂⁹, using PR4470's word from main's pinned constructor. The 112 ports, v = 112 and h = 9 are also unchanged, while the warp layer itself does change. So, unlike the span{511} quotient in #4596, this construction keeps every output chart.

### 2. Profile arithmetic

- **Profile.** The emitted word's local profile is exactly Pnew.
- **Difference.** Pold − Pnew = 12(3 H1 − 2 H2 − H3 + H4).
- **Totals.** Paid rank mass is unchanged at 5,327, with 12 fewer jobs per call. Over the 18-call controller that is 216 fewer paid calls, from 64,620 to 64,404.

### 3. Moment positivity, with a written proof independent of #4610's intervals

For 0 < a < 1, put x = 2^a ∈ (1, 2) and c = log₂ 3. Then

```text
3 − 2·2^a − 3^a + 4^a = g(x) := (x − 1)² + 2 − x^c.
```

- **Convex:** g''(x) = 2 − c(c−1)x^{c−2} ≥ 2 − c(c−1) > 0, using x ≥ 1 and c < 2 (since 3 < 4).
- **Decreasing:** g'(2) = 2 − 3c/2 < 0, since c > 4/3 (because 27 > 16). With g convex, this gives g' < 0 on [1, 2].
- **Conclusion:** g(2) = 0, so g(x) > 0 on (1, 2).

The difference is therefore strictly positive for every 0 < t < 1, whichever of t or 1−t is the exponent. A 999-point grid is checked as a numerical sanity control.

## Verify

```text
python3 -B research/pr4610-endpoint-profile-check/verify.py
```

The check takes about 2 s and uses the standard library only.

## Limitations

**Not covered:**

- the native Clifford and absolute-phase lowering of the 34 changed maps;
- the Lean certificates;
- the outer crossing interval (0.0030215551, 0.0030215552) and the resulting κ;
- whether substituting generators of the free-group identity is admissible under the supplier contract (a maintainer question).

This package establishes only that the endpoints are preserved and that the claimed profile improvement is arithmetically and analytically sound.

## Open next questions

- **Native phase lowering.** Check it for the 34 changed G maps independently. First step: rebuild each K_G from the 9×9 binary G, using the transported-frame lemma's integer column formulas, and compare it with #4610's bound operators.

Credit: intqwq (#4610), Cinna Davis (#4470), DaysSky and the #4535 lineage. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
