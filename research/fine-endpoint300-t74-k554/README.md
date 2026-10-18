# 1e-300 supplier endpoint and 1e-310 slacks over PR1839

Conditional **κ = 0.0016797549561255445213356709939207025769983114385025802954603275201628645482603256388263056561328446322744513169085862209720704481201654121427713006366929567157349625273906229277148454180995537563371124755588139767841405530386745578819565618798006892541712197674874836946756930569827889227573192555649999999997996640490086748910957328658012158594**

This is **6.5613284483e-91** above PR1839 (jeremykothe2, `836ef6a1`), the current leader. It uses the identical construction: the pivot-566 + pivot-554 T74 supplier with the PR1673 capped phase-cell fusion outer, PR1786 fine source-prime padding, PR1758 gauge-free interiors and the radix-distributed union schedule.

## What changes (numbers only)

The construction, paid profile, owner map and outer formulas do not change.

1. **Supplier endpoint recertified to 1e-300.** PR1839 certified the native complex endpoint on a 1e-90 grid. The moment root lies 6.56e-91 above that pin. Both endpoints are recertified on the 1e-300 grid:
   - native: accept at `complex_lower`, reject at `complex_lower + 1e-300`;
   - conservative (surcharge) side: the same accept/reject pair.

   This uses finer-constant copies of the package's two fine engines with the same algorithms:
   - `code/fine_mercator.py`: DYAD 2^1100, 1100 (even) Mercator terms, 100 exponential terms;
   - `code/fine_moment.py`: grid 1e-330, 360 atanh terms, 100 exponential terms.

   The retained 1e-24 engines still certify the inherited coarse bracket. The package's independent log oracle (`code/oracle_check.py`, 900-term atanh) checks the new engines' log enclosures for soundness and tightness.
2. **Free strict slacks at 1e-310.** b = endpoint − 1e-310, q = b − 1e-310, r0 = layout slack = 1e-310, zeta = 1e-312 and stop = 1e-316. epsilon = 1 − 2e-310 and beta = 1 − 6e-310. The floor grid is 1e-346 and the backoff is 1e-322.

   The ledger encloses the native moment on a 1e-340 grid with 360 log terms and 100 exponential terms. It shows moment(b) < 1 and rejects endpoint + 1e-300.
3. **Ledger results.** The regenerated ledger has 59 strict inequalities: the previous 58 plus `improvement_over_pr1839`. The same 17 rejecting controls are rejected. The independent balance derivation includes the PR1839 comparison and an epsilon sweep down to 2e-310.

Every changed slack is still a fixed positive constant, so the inherited eventual absorption arguments apply unchanged, with a larger unspecified cutoff. See PROOF.md.

## Files

The package is an overlay on PR1839's immutable package `research/capped-fusion-t74-k554`. `DEPENDENCY.json` pins it by head and MANIFEST SHA256. `overlay/` holds the 11 replaced files plus the patched package's `MANIFEST.json`; no file is added or removed.

## Reproduce

```sh
PYTHONINTMAXSTRDIGITS=0 python3 -B research/fine-endpoint300-t74-k554/verify.py --work /absolute/new/work [--dependency /path/to/capped-fusion-t74-k554] [--native-cache DIR]
```

`verify.py` runs these steps:

1. checks this package's MANIFEST;
2. fetches the dependency, or takes `--dependency`, and checks all 381 files against PR1839's own MANIFEST;
3. applies the overlay and checks the patched tree file by file;
4. runs the patched package's own `verify_release.py`. That covers the fresh native supplier admission, the strict T74 admission with both 1e-300 endpoint brackets, the regenerated outer ledger compared byte for byte, the independent balance derivation, the schedule, gauge-free and fine-padding checks, and PR1673's 19 evidence replays;
5. binds the release receipt to CLAIM.json and requires a strict gain over PR1839.

`--arithmetic-only` regenerates and compares only the outer artifacts.

**Evidence.** `evidence/RELEASE-RECEIPT.json` is `PASS_RELEASE` with fresh native replays of all four words. It comes from the patched package's own `verify_release.py`, run on the overlay-patched tree; that tree's MANIFEST `b24c5072…` equals `overlay/MANIFEST.json`. `evidence/SUPPLIER-RESULT.json` is `PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION`. `evidence/ASSEMBLY-ENDPOINTS.json` holds the coarse and 1e-300 accept/reject moment rows on both the native and conservative sides.

## Scope

This is a conditional arithmetic refinement of PR1839's parameter point, not a new supplier or analytic theorem. All inherited PR1839/1800/1786/1758/1673 all-size, compiler, hosting, precision, prime-packing, recovery and analytic assumptions remain, plus the cited Trudgian prime theorem. No unconditional theorem, practical cutoff, independent human review or maintainer acceptance is claimed.

## Credit

- jeremykothe2 and PR1839/PR1800 contributors: the package, the free-epsilon composition, the ledger and the 1e-90 recertification this extends.
- Chafik Boukhalfa / chafreaky (PR1786): fine source-prime padding.
- Tim Trudgian: the cited prime theorem.
- Vlado Vojdanovski (PR1673).
- IdeaOuter and PR1758 contributors.
- LeverRank.
- mdumitrean (PR1625), midhatn (PR1661), the PR1672 pivot-554 kernel, and the PR1319/PR1297/PR1274/PR1286 supplier lineage.
- philippeVV (PR1519): the odd-term Mercator finding behind the even-term rule kept here.

Prepared by Rohan Arun with substantial AI assistance (Anthropic Claude). Apache-2.0; inherited notices are retained in the dependency.
