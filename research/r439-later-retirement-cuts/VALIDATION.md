# Local verification receipt

Date: 2026-10-13. Environment: macOS arm64, CPython 3.12.13 and 3.14.7.
Base and refreshed main: `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`.

Passed on Python 3.12.13:

```
python3.12 scripts/research_package.py --package research/r439-later-retirement-cuts
```

- Complete primary census: 4,278 pairs, 713 cuts per helper.
- Separate checker: 713 complete inverse reconstructions and equality at every boundary.
- Four later-cut test groups, including six corrupted census variants, boundary witnesses, source corruption, optimized relocation and exact regeneration.
- Six stationary fixture groups, including ten gate omissions, three target-cap failures/relaxed positives, six receipt faults in both engines, wrong station, damaged original cleanup, source corruption, relocation and overwrite rejection.
- Final marker: `PASS_REGISTERED_RESEARCH_PACKAGE research/r439-later-retirement-cuts outcome=completed`.

The four later-cut groups also pass with CPython 3.14.7 under `-I -O -B`.
The six stationary groups passed on the same interpreter before the directory
was renamed; the complete registered replay after the rename passed on 3.12.13.

Also passed:

```
python3 -B scripts/research_baseline.py
python3 -B scripts/verify_selected_result.py
python3 -m unittest discover -s tests -p test_selected_result.py
```

The baseline reports source bindings only, unchanged selected kappa
`836330098538459/500000000000000000`, and the complex side binding. The five
selected-result tests pass. No selected frontier file or upstream file changed.

Overlap: initial complete850-PR snapshot; refreshed complete855-PR snapshot
and12 discussions exposed PR1256 and caused the documented one-scope pivot.
Final latest100-PR refresh through PR1268 found no additional later-cut census;
newer work concerns other circuits, packing and ledger verification. These
bounded live observations do not constitute a novelty guarantee.

Not run or claimed: native 5/9/11-stage supplier replay, full selected cold
replay, new suffix construction, hosted admission, complete paid profile,
remote CI, proof-assistant verification or independent human review.
