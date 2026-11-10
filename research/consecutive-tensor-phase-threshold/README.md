# First phase-aliasing threshold for tensor widths 2 through k

For fixed unitaries A and B whose tensor powers at every width 2..k agree
within operator-norm error eps, this package gives the exact budget at which
the sharp bound on ||A−B|| first jumps, and the value it jumps to, for every
k ≥ 3. It was produced by Nick Petalas.
**Scoped analytical theorem with exact finite corroboration. No new κ.**

Put `a = asin(eps/2)`. Below the threshold `eps*`, the sharp bound is the small
branch `||A−B|| <= 2 sin(a/k)`. At `eps*` it jumps:

| widths tested | eps* | left limit | value at eps* |
|---|---|---|---|
| 2, 3 (PR5916) | 2 sin(π/5) | 2 sin(π/15) | 2 sin(2π/5) |
| 2..4 and 2..5 | 2 sin(2π/7) ≈ 1.5637 | 2 sin(2π/(7k)) | 2 sin(3π/7) ≈ 1.9499 |
| 2..6 and 2..7 | √3 | 2 sin(π/(3k)) | 2 sin(4π/9) ≈ 1.9696 |
| 2..k, k ≥ 8 | √3 | 2 sin(π/(3k)) | √3 |

Scalar unitaries attain every value in every positive finite dimension.
The threshold includes equality. For every k ≥ 6 the jump is at the same
budget √3, because the phase exp(2πi/3) passes every width test at that
budget. Extra widths beyond six shrink the small branch, but they cannot
exclude phase aliasing for budgets eps ≥ √3. From k = 8 on, the error after
the jump equals the budget.

[PROOF.md](PROOF.md) gives the proof. It reduces to scalar phases as in
PR5916, splits the width-two feasible set into a near branch and a far branch
around 1/2, and excludes the far branch with the width-three, width-four and
width-six tests.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/consecutive-tensor-phase-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/consecutive-tensor-phase-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/consecutive-tensor-phase-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/consecutive-tensor-phase-threshold --check-source-history
```

The marker is `PASS_CONSECUTIVE_TENSOR_PHASE_THRESHOLD`. Each direct run takes
under one second and writes nothing.

[verify.py](verify.py) computes the exact sublevel set
`{phi in [0,1/2] : ||j phi|| <= alpha, j = 2..k}` as a union of closed rational
intervals with `fractions.Fraction`, for every k from 3 to 64. It checks that:

- at eight rational budgets below each threshold, including `alpha* − 2^-200`,
  the set is exactly the small branch `[0, alpha/k]`;
- at the threshold, the farthest feasible point is the stated jump point, and
  every far component is a single point;
- the witnesses `1/3`, `4/9`, `3/7` and `2/5` pass and fail at the stated widths.

Four controls fail as designed: width two alone, a false threshold for k = 5,
a false jump point for k = 8, and a falsely strict threshold. The finite range
corroborates the written proof; the all-k claim rests on PROOF.md. The scalar
reduction is proved in PROOF.md and is not checked by enumerating unitaries.

## Scope

This changes the `uniform-transfer-audit` card to a quantitative interface
side result, as PR5916 did. It does not apply the theorem to a selected
caller or discharge `native_all_columns`. It does not cover the envelope above
the first threshold, non-consecutive width sets, unequal per-width budgets,
projective comparisons, independently rounded factors, or any physical
precision, tape or storage cost. All five framework assumptions keep their
status. No supplier admission, selected replay, new κ, frontier change or
complete multiplication theorem is claimed. Independent human and formal
proof-kernel review are unclaimed.

Overlap: searches of merged packages and PRs for tensor powers, consecutive
widths and phase thresholds found PR5916 (widths 2, 3, equal budgets) and
PR6330 (widths 2, 3, unequal budgets). Neither treats more than two widths.
This is bounded evidence; unpublished work is outside coverage.

## Open next questions

- **Envelope above the threshold.** Determine `R_k(eps)` for `eps* < eps < 2`.
  The next valleys of `max_j ||j phi||` lie at 4/11 (k = 8, 9), 5/13 (k = 10, 11)
  and 2/5 (k ≥ 12). Each finite k is an exact interval computation; the blocker
  is a uniform description in k.
- **Other width sets and budgets.** Find the first threshold for a
  non-consecutive width set or unequal per-width budgets. The arc-family method
  of PR6330 applies, but the branch argument here uses widths 2, 3, 4 and 6.
- **An actual chart.** Bind a fixed native-chart comparison to certified
  defect budgets at several widths, as PR5916 and PR6330 ask. Physical
  precision and tape evidence are still missing.

## Credit

Nick Petalas supplied PR5916's width-two/three theorem and scalar reduction,
which this package extends. Credit Jerry Chen (@CubeJerry) for PR6330's
asymmetric two-budget envelope, unpaidmoon for PR5837's motivating
finite-width phase question, and DLamdata for PR5894's selected
absolute-phase coverage. Exact provenance pins are in
[SOURCES.json](SOURCES.json); no predecessor code is run. Spectral theory and
trigonometry are classical; no literature-priority claim is made.
New work is Apache-2.0.
