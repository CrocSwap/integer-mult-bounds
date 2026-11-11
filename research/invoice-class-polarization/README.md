# The polarized invoice ceiling for the signed concave screen

produced by Nick Petalas

## Scope

The documented comparator `scripts/compare_recursive_invoices.py` decides the
order of two declared invoices for every increasing concave tariff, in
particular for the power tariff `r^(1-C)` with saving `C`. Each invoice is a
paid multiset and a target multiset of ranks in `[1, m]`, and its signed net at
exponent `x = 1 - C` is

    N(x) = sum_paid r^x - sum_target s^x.

The comparator answers a comparison question about two *given* invoices. This
package answers a different question about the same arithmetic screen: over the
whole class of invoices that share the four summary numbers

    paid entry count Kp, paid rank mass Mp, target entry count Kt, target rank mass Mt,

which invoice is the most favourable for the screen, and is that extreme
independent of `x`?

## Result

Claim type: **scoped written proof with exact finite corroboration.**

For `m >= 2` and every exponent `0 < x < 1`, the most favourable invoice in a
class `(Kp, Mp, Kt, Mt)` is the *polarized* invoice

* paid ranks: `Kp - 1` entries as spread as the mass allows, namely `j` copies
  of `m`, one remainder `r0`, and the rest `1`, where
  `j = min(Kp - 1, (Mp - Kp) // (m - 1))` and `r0 = Mp - Kp + 1 - j(m - 1)`
  (the greedy spread vector `G`);
* target ranks: the balanced vector `B`, with entries `q = Mt // Kt` and
  `q + 1`.

Every invoice in the class satisfies `N(x) >= N_canonical(x)` for all
`0 < x < 1` simultaneously, with equality exactly at the canonical invoice.
The canonical invoice depends only on `(Kp, Mp, Kt, Mt, m)`, so one 2-rank
invoice is the pointwise extreme of the whole class.

Two consequences that cost no construction replay:

1. **Necessary condition.** A candidate in class `(Kp, Mp, Kt, Mt)` can beat an
   incumbent with net `Psi(x)` only if `Lambda(x) < Psi(x)`, where `Lambda` is
   the canonical net. The cruder mass-only form is
   `Mt > Mp m^(x-1) - Psi(x)`.
2. **Sufficient class certificate.** Let `U` be the *antipodal* invoice of the
   incumbent class (paid balanced, targets spread). If
   `Lambda_candidate(x) > U_incumbent(x)` for all `0 < x < 1`, then every
   invoice in the candidate class is uniformly worse than every invoice in the
   incumbent class. Both sides are 2-rank invoices, so the existing hinge
   comparator verifies the hypothesis exactly in constant time.

The proof is an exchange argument: the increments of a strictly concave power
are strictly decreasing, so spreading paid mass and equalizing target mass
never hurt, and the terminal configurations are unique. `PROOF.md` states the
lemmas, the uniqueness argument and the sharpness controls.

## What is not claimed

* No physical, native, compiler, precision, hosting, ownership or supplier
  admission. Ranks are declared histogram entries, exactly as in the
  comparator, whose own assurance block records the same restriction.
* No paid *call* count, scalar instruction count, or charge outside the raw
  signed moment.
* No `kappa` change, and no claim that a canonical invoice is realizable by a
  word. The bound is over declarations and cannot be improved inside the
  declared class.
* The result is about the documented arithmetic screen, not a new supplier.

## Evidence

`PROOF.md` contains the written argument: two exchange lemmas, the uniqueness
of the spread-terminal and balanced vectors, the class theorem, the sharpness
of the exponent range, and the two consequences.

`verify.py` checks the argument with integer interval arithmetic only (rank
powers are bracketed by integer k-th roots; there is no floating point):

* both exchange lemmas for every admissible pair with `m <= 6` and five
  exponents `1/2, 1/3, 2/3, 1/5, 3/7`;
* Proposition 1 (unique paid minimum) and Proposition 2 (unique target maximum)
  exhaustively on every integer multiset in four boxes: `(m, max entries)` =
  `(5, 3)`, `(4, 4)`, `(6, 2)`, `(3, 5)`;
* the class theorem on every ordered pair of invoices in those boxes: 40,705
  strict comparisons and 16,995 equality cases;
* the `x = 1` and `x = 0` boundary controls that make the exponent range sharp
  (at `x = 1` the inequality is an equality for every invoice with the same
  masses, so the strict statement genuinely needs `x < 1`);
* composition with `scripts/compare_recursive_invoices.py` on schema-valid
  invoices: the comparator classifies a non-canonical invoice against its
  canonical replacement as `uniformly_worse` with a strictly positive power
  sign, the reverse as `uniformly_better`, identical canonical invoices as
  `equal`, a rank above the declared ambient rank as invalid, and it confirms
  the antipodal class certificate;
* mutation controls (balanced paid, spread targets, a half-spread paid vector)
  and hypothesis controls (infeasible counts and masses, ambient rank one).

The comparator integration is an independent implementation: its hinge
criterion is not the exchange argument used here, so agreement is a genuine
cross-check rather than a restatement.

## Reproduction

From the repository root, with CPython 3.12:

```sh
python3.12 -B research/invoice-class-polarization/verify.py
python3.12 -W error -B research/invoice-class-polarization/verify.py
python3.12 -O -W error -B research/invoice-class-polarization/verify.py
python3.12 -B scripts/research_package.py --package research/invoice-class-polarization
python3.12 -B scripts/check_research_commit.py --package research/invoice-class-polarization --check-source-history
```

The verifier prints a census and `PASS_INVOICE_CLASS_POLARIZATION`, and rewrites
`RESULT.json` with the source hashes of the package files.

## Open next questions

1. **Signed target counts with multiplicity caps.** The theorem treats target
   entries as freely repeatable. If a construction can host at most `c` targets
   of a given rank, the target extremum becomes a bounded-composition problem.
   *Why it matters:* multiplicity caps are the realistic constraint on
   independent helper refinements, and they can only lower the ceiling.
   *First step:* derive the exact maximum of `sum s_j^x` under per-rank caps.
   *Blocked by:* no declared cap inventory for a concrete word.
2. **Which summary quadruples are physically achievable?** The ceiling is exact
   over declarations; the useful screening version needs the achievable set of
   `(Kp, Mp, Kt, Mt)` for a fixed controller.
   *Why it matters:* an unachievable canonical invoice is still a valid bound
   but a weaker one. *First step:* count the four numbers for one audited
   invoice and compare against the ceiling. *Blocked by:* no source inventory
   is bound in this package.
3. **Tightening with the number of distinct ranks.** The canonical invoices use
   at most two distinct ranks per side. A bound that also fixes the number of
   distinct ranks could separate proposals that the four summary numbers
   cannot. *Why it matters:* it would sharpen the class certificate at fixed
   cost. *First step:* solve the two-constraint extremal problem with a
   distinct-rank budget. *Blocked by:* the extremal vector is no longer unique,
   so the equality characterisation needs a tie-breaking rule.

## Related open work

* PR #5973 (josecarlosgonzalezroque-design) keeps the selected-invoice stdout
  bytes consistent with its receipt. It studies the invoice tooling's output
  contract, not the signed moment or its class extremum, so it neither
  overlaps nor supplies the quantity bounded here.
* PR #7175 (petalas) certifies fixed-profile helper-split first-crossing
  ceilings for the selected frontier. It bounds a different model (a fixed
  helper-split profile at one crossing), so its numbers are not comparable with
  the class ceiling here; the two would compose only after that profile is
  expressed as a declared paid/target invoice.
* The comparator itself and its documented screen are the subject here; the
  live tool files are pinned in `SOURCES.json`.
* `docs/research/recursive-invoice-preflight.md` records the signed-invoice
  comparison procedure and its "not a new theorem" disclaimer for the
  concave-order interface; this package supplies the class-extremal theorem
  that the interface left open, and changes nothing in that document.

## Credit

The comparator and its hinge criterion are by zxv, on the classical
concave-order and majorization lineage recorded in its docstring, including
mightyOil's `research/t16-moment-order-audit` and its credited predecessors.
The signed-invoice preflight procedure is recorded in
`docs/research/recursive-invoice-preflight.md`. This package reuses that
arithmetic interface unchanged and adds the class-extremal theorem, its
uniqueness proof and the sharpness controls.

Apache-2.0.
