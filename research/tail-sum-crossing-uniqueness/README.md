# One tail-sum sign change fixes the query-tree crossing globally

**Scoped proof with an exact finite check. No new κ; the selected frontier is unchanged.**

The complete signed raw moment of the merged binary query-tree bill
([PR6348](https://github.com/CrocSwap/integer-mult-bounds/pull/6348),
`research/balanced-query-tree`, Ali Romman, conditional κ 0.00314933) is

```text
F(t) = sum_r (T_r - P_r) r^t.
```

Its coefficients change sign 13 times, so a Descartes count allows 13 real
roots. Their tail sums `B_k = c_k + ... + c_n` change sign exactly once.
By Laguerre's classical rule, `F` then has at most one zero on all of
`t > 0`. With `F(0) = -56309` and `F(1) = 808`, it has exactly one, in
`(0,1)`. So for every saving `C < 1`, the complete raw target moment beats
the paid moment exactly when `C` is below the raw crossing. The source
package proves uniqueness only for `C <= 0.0034`, by a derivative bound.

[PROOF.md](PROOF.md) has the lemma, a short proof sketch with references, and the
application. [verify.py](verify.py) rebuilds the bill from the pinned source
`RESULT.json` and checks every step with exact integers.

## Reproduce

From the repository root:

```sh
python3.12 -I -B research/tail-sum-crossing-uniqueness/verify.py
python3.12 -I -O -B research/tail-sum-crossing-uniqueness/verify.py
python3.12 -B scripts/research_package.py --package research/tail-sum-crossing-uniqueness
```

Each verifier run prints `PASS_TAIL_SUM_CROSSING_UNIQUENESS` in well under
a second. Add `--json` to print the certificate. Checked:

- the bill's 14214 fields, 70523 paid calls and rank-mass surplus 808;
- 19 nonzero signed coefficients with 13 sign changes;
- tail sums with exactly one sign change, `F(0) < 0 < F(1)`;
- a 60-digit decimal sign check on both sides of the source enclosure
  (consistency control, not part of the proof).

Three rejection controls fail closed: the two-root invoice
`6 - 4·2^t - 3·3^t + 2·6^t` from `recursive-power-variation.md`, the reversed
invoice, and the bill without its rank-153 root targets.

## Limitations

Only invoice arithmetic is proved. The construction, native maps, compiler,
outer ledger and the five retained framework assumptions are untouched.
The crossing's location comes from the source package and is not
recomputed here. The lemma is classical (Pólya–Szegő; Karlin); the proof
in PROOF.md reduces it to the variation-diminishing property and cites
that property rather than reproving it. No proof-kernel check was run.

## Open next questions

1. **Does the rule settle inconclusive power-variation reports?** The
   Descartes budget of `scripts/compare_power_variation.py` also counts roots
   at `t <= 0`. The tail-sum count sees only `t > 0`; here it
   is 1 against 13. First step: run `certify()` on the invoices that script reports
   as inconclusive. This package does not modify the shared script.
2. **A count for `(0,1)` alone.** Roots at `t > 1` (negative savings) still
   consume the budget. Tail sums of `c_r r` bound the roots on `t > 1`, but
   subtracting two upper bounds gives no bound. A valid combination, or a
   proof that none exists, would sharpen the certificate.

## Credit

Produced by Nick Petalas. The invoice and its source pricing are Ali
Romman's PR6348, with the predecessor credits recorded in that package. The
general-rank Descartes certificate is Ali Romman's PR5788. Laguerre's rule and
the variation-diminishing property are classical. New work is Apache-2.0.
