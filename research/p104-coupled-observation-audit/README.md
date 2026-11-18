# Two coupled P104 observations: separate exact audit

The two local observations in edit 26 of PR7756 pass a separate exact
check. All six banks at chart 144 observe only the first source direction;
all six at chart 177 observe only the second. Their full two-pulse responses
cancel the errors at terminals 130 and 166. Two explicit 7-by-7 minors,
each with determinant `1/512`, certify the complete intersections.

Read [the proof](PROOF.md), [full bank coefficients and rank certificates](RESULT.json),
[forward expansion and determinant code](audit.py), [verifier](verify.py)
and [source credit](CREDITS.md). No new kappa or whole-supplier acceptance
is claimed. The earlier source graph construction is a pinned dependency.

Use Python 3.12 and the standard library from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-coupled-observation-audit
```

Both registered commands print `PASS_P104_COUPLED_OBSERVATION_AUDIT`.
The package also works after export, without Git or repository imports.
The source constructor is stopped through its observer before edit 26.
The new checker uses forward integer vectors, rational elimination and
fraction-free determinants. The unchanged source local checker then
provides a reverse-expansion cross-check.

The source has 1,262 public fields. The audit checks twelve complete bank
rows, both pulse columns, and every terminal at the two charts. Four
changed pulse signs and two changed observation signs fail their controls.
Only this local scalar claim is covered. Complete native, caller and price
review, all five compiler assumptions and physical admission remain open.

## Open next questions

- Can a separate implementation verify every grouped return and source
  replacement in the exact 32-edit journal? Check one unclaimed group,
  including every incoming pulse, before expanding the audit.
- Do all sixteen visits of one mixed root share one physical head after
  both charged view changes? This is the separate caller review request
  in PR7756; check live coordination before taking it.
