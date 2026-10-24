# Port-dependent C_u charts match a data line only when they are equal

**Partial negative result. No new κ.** The selected conditional exponent stays
`60403/20000000` (`0.00302015`, #4470).

## Result

In the chart family used by the uniform-commutation gap, an adjacent data line
matches every character if and only if the exit chart and the next entrance
chart are the same chart.

The address space is `F_2^4`. For each `u` in that space the chart is

```text
C_u = ((1+i) I + (1-i) X_u) / 2,
X_u |z⟩ = (-1)^{u·z} |z⟩.
```

So `C_u` fixes the even characters of `u` and multiplies the odd characters by
`i`. The changed premise, relative to PR #4136, is that the next entrance may
be an arbitrary chart `C_b` in this family, not only the common chart `I`.
The exit is `C_a`. These two charts transport every data character by `1` if
and only if `a = b`.

There are 16 charts and 256 ordered pairs:

| Pairs | Count | Data-line outcome |
|---|---:|---|
| `a = b` | 16 | Match on all 16 characters |
| `a ≠ b` | 240 | Fail on exactly 8 characters |

The eight failures are the odd set of the nonzero form `a + b`. On that set
the multiplier is `i` or `-i`. The 15 pairs in #4136, exit `C_u` for `u ≠ 0`
against entrance `I`, are one column of this table.

Replacing the odd eigenvalue `i` by `1` makes every chart the identity and
every pair a match. The obstruction is that relative phase.

The argument is in [PROOF.md](PROOF.md). `verify.py` evaluates `C_u` from the
displayed formula, checks the four-case multiplier, and enumerates all 256
pairs. It does not import the #4136 package.

## Scope

Task card `p104-side-correction`, priority revision 7, base
`fbc9ea0249746acca4f504d4fda2b84e0e36cf0d`. Scope status is **refined**.

The card asks whether a changed producer/consumer contract can escape the
scoped chart obstruction with a favorable full bill. This package changes one
hypothesis of the published chart obstruction: the entrance chart is any
`C_b`, not only `I`. Inside this family the data-line mismatch survives for
every port-dependent pair. Helper roles, dirty restoration, an intertwiner
and a hosting bill are not in the model, so this is not a supplier and not a
complete channel bill.

Ordered eligible list for this session, after dropping obligations already
delivered on main or by the listed unpaidmoon PRs. Order is the
priority-revision-7 table in `docs/research/current-priorities.md`, with the
first row expanded by the shortest unaudited list in
`docs/research/pr4100-audit-coverage-map.md` and then by the successor
questions those audits still leave open:

1. PR2809 encoded-stack visited-space bound (open question of `bit-stock-recurrence-audit`).
2. One PR4088 global program's frame-label cancellation (open question of `complex-cover-lift-audit`).
3. QQ16 matched parent park/restore bill (open question of `qq16-caller-install`).
4. R437 residual binding to uniform fixed-tape primitives (open question 1 of `r437-carrier-integration`).
5. **This package.** The fifth remaining item is the P104 row. Its delivered
   static obstructions (#4133, #4136, #4140, #4153, #4154, #4370 and the other
   listed P104 PRs) are excluded. The distinct remaining piece is open
   question 1 of #4136: an adjacent pair whose entrance chart may depend on
   the port. The data-line half is answered here. The helper half is still open.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/p104-port-chart-pair --check-only
python3.12 -B scripts/research_package.py --package research/p104-port-chart-pair
```

Direct checks:

```sh
python3 -B research/p104-port-chart-pair/verify.py
python3 -B research/p104-port-chart-pair/test_verify.py
```

Expected marker:

```text
PASS_P104_PORT_CHART_PAIR address=F2^4 charts=16 ordered_pairs=256 matching_pairs=16 failing_pairs=240 failures_per_unequal_pair=8 entrance_I_failures=15 data_match_iff_equal_charts=true helpers=out_of_model no_new_kappa
```

Not run: Lean, Docker, the selected cold replay, a helper-role model, and any
hosting or moment calculation.

## Open next questions

1. Does one helper block, written in this same chart family, have an exit and
   a next entrance that match on every helper role when the data charts already
   differ? The first step is to name the helper roles and their charts. This
   package has no helper roles, so it cannot answer that half.
2. Is there a chart family outside `{C_u}`, still legal for the P104 encoding,
   in which two different charts transport every data character by `1`? A
   positive example would reopen the adjacent-pair search. This classification
   does not search that family.

## Credit

The chart formula, the uniform-match statement, and the 15 entrance-`I`
failures are PR #4136 (unpaidmoon), from the two-axis gate in PR #3954
(Chris R / Clear1nsight). The request for one adjacent pair is discussion
#1166 comment 19034066. Predecessor lineage named in #4136 remains theirs,
including Rohan Arun, Chafik Boukhalfa, and Adam Gall.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review is claimed.
