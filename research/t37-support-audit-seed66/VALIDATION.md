# Local validation and handoff

Experimental base: `407d52ff15b2217b6e22bce44728b4c3907b6515`.
Refreshed upstream: `8bddbee377e2f3ce1f1247196c4b290d55767d20`; all four
consumed predecessor files are byte-identical there. CPython 3.9.6, macOS arm64.

Completed checks:

- Main `verify.py` passes normally and with `-I -O -B`: 1,163 complete bin
  vectors, all 45 attainable scores and all 42 strict-rank obligations;
  exact minimum conservative normalized margin `24274/28675`.
- Independent checker passes under `-I -O -B`, reconstructing the same entire
  score table by exact-fill DP, with direct fixed-point log sums and outward
  geometric repeated squaring. Every certified normalized margin is above 3.
  Parent checks its full table and coverage, not only its final marker.
- Seven mathematical mutations reject; four exact boundary controls pass.
  These distinguish counterexamples to altered credit/range statements from
  the corroborated accepted supporting lemma.
- `test_package.py` passes: optimized standalone relocation with spaces,
  byte-identical complete certificate regeneration, preservation of existing
  output, 12 actual on-disk corruptions and two independent arithmetic changes.
- All four retained SHA256 and Git-blob bindings match the exact base and
  refreshed upstream. Source constants are checked as literal data.
- `make selected-record-check` passes, as do all five existing selected-result
  tests. Staged whitespace is checked before publication.
- Separate AI proof review checks the integral inequality, elementary bounds,
  signed-credit direction, exact wider-range counterexample and distinction
  between real count equality and integer replica divisibility.

One reproducible command:

```sh
python3 -I -O -B research/t37-support-audit-seed66/verify.py
```

Expected: `PASS_T37_UNIFORM_SUPPORT_AUDIT bins=1163 ranks=42 z=(0,1/500] minimum_margin=24274/28675 no_new_kappa`.

The final overlap refresh found PR995 (wider uniform support by monotonicity
and integer cube roots) and PR992 (sharp integrality penalties). Their result
and scope are credited in README/NOTICE. This submission contributes a distinct
rational integral proof/check near the selected endpoint. No PR995 code is
consumed, no source/frontier is changed and no larger kappa is claimed.

Not run: full repository/global regeneration, native supplier cold replay,
owner/controller/invoice/outer replays, hosted CI or Lean. The input sources
and selected construction are unchanged. This is a scoped analytic audit with
exact finite certificates, not a full multiplication theorem proof or a new
physical construction. Human peer review remains the next step.
