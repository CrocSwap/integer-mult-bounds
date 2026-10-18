# PR1625's pivot-566 helper-donor kernel on the T74 exact fill, with certified 1e-450 endpoints and a 1e-470 outer witness

**Current claim (matches `CLAIM.json` and `new/SPEC.json`): conditional kappa = 0.00167689666902129930775071099726796267161149001633915961065846405551493368017298530816648329578987603391093506496057281357744132163388291479658285968957814604920528923726088482111926993572396387724842267073860167466860846835390782497592401638229372521828691024435767760818436694321206071473719642441257180091315126184635916779749908301326817322463434681590207653171784740473022951431618102685755994326607285095814925855357959732116035535244417050872462468224313198159193**.

## Credit and lineage
The construction gain is PR1625 (mdumitrean): a seven-insert helper-donor kernel for cold pivot 566 on the two local words of PR1297, as vendored in PR1319 (H1 +1, H2 -2, H3 +1 per call on both words; owners, dispatch, parent and idle remainder reused byte-for-byte). `new/gauge44-word-566.json.gz`, `new/extra-word-566.json.gz`, `new/EDITS.json`, `new/rebuild.py`, `new/rebind.py` and the rebound `new/PLAN.json`/`new/PROFILE.json` are PR1625's. The T74 construction is PR1319 (rohanarun) over PR1297's four cold kernels (rohanarun; kernel 531 PR1274 jeremykothe2, kernel 543 PR1286 rohanarun). The outer-witness / endpoint refinement lineage: PR1424, PR1485, PR1574, PR1629 (rohanarun); PR1479, PR1510, PR1513, PR1536, PR1578, PR1644 (jeremykothe2); PR1534, PR1549, PR1582, PR1640, PR1661 (midhatn); the soundness repair of the fine Mercator engine is PR1519 (philippeVV); PR1661's 400-digit grid is the baseline compared against.

## What this package adds on top of PR1661
1. **Certified complex endpoints (native and conservative) at 1e-450**: evaluated with outward-rounded integer Taylor recurrence engines (`code/fine_mercator.py`: DYAD 2^1800 outward rounding, 1800 (even) Mercator terms, 150 Taylor terms; `code/fine_moment.py`: 10^550 grid outward rounding, 600 log terms, 150 Taylor terms) certifying accept at the endpoint and reject at endpoint + 1e-450, both required.
2. **Independent verification of engine soundness**:
   - `log_enclosure_audit.py`: independent exact atanh oracle (width < 2^-2400) on 76 logarithm inputs, reproducing 3 predecessor parity failures.
   - `rounded_exp_audit.py`: compares 16 enclosures against reference unrounded evaluators and strictly rejects 5 invalid inputs.
   - `code/oracle_check.py`: package stage oracle verifying tightness < 1e-200.
3. **Outer witness settings in `new/SPEC.json:outer_refinement`**:
   - `grid_digits`: 470 (the final kappa grid)
   - `margin_digits`: 500 (eta = beta = 10^-500, backoff 10^-503)
   - `bootstrap_steps`: 190
   - `endpoint_digits`: 450
   - `dec()` prints 550 significant digits.
4. **Strict Rational Improvement over PR1661 (Breakthrough 20)**:
   Resolves 70 additional decimal digits ($10^{-401}$ to $10^{-470}$):
   $$\kappa_{21} - \kappa_{20} = +\frac{6607285095814925855357959732116035535244417050872462468224313198159193}{10^{470}} > 0.$$

All 47 strict outer inequalities, all 4 rejection controls (`next_grid`, `zero_eta`, `zero_beta`, `unit_beta`), and the full finite admission controls hold.
