# Executed validation

Local validation on 2026-10-13 UTC (2026-10-14 Melbourne), at exact research base
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`. All outputs below refer to the frozen
29-ADD candidate. Environment details are retained in `ENVIRONMENT.json`:
CPython 3.14.6, macOS arm64, Apple Clang 17.0.0, Boost 1.87.0. Other platforms
and hosted CI are not inferred from these local checks.

## Checks completed

1. `python3 -I -B research/r439-frame520/verify.py --out /tmp/math-seed05-release`
   passed. The code-disjoint column evaluator proves the exact finite ordered
   integer matrix equality and signed inverse; all 4,096 local Boolean inputs
   agree. Set-valued complete replay covers 661 independent input columns.
   The unchanged source checker accepts E8 labels, all 636 closed frames,
   complete scalar endpoints and H1–H5/U/J/K/C. Both words' 661 frame paths and
   complete paid bills agree except the 24 removed ADDs. Output: `RECEIPT.json`.
2. Nine local controls distinguish omitted preparation, omitted final addition,
   a noncommuting order change, an F2-neutral but integer-nonneutral pair,
   uncharged extra gates, an exact-forward candidate with reverse growth,
   omitted cleanup, illegal descent and the stale-C case. The stale-C control
   **passes the scalar endpoint and fails literal H4**; it is not described as
   a scalar counterexample. The reverse-growth control is a genuine 30-gate
   identity from rejected trajectory 588, not a corrupted forward map.
3. `BOOST_INCLUDE=/private/tmp/boost_1_87_0 python3 -B research/r439-frame520/native.py
   --word /tmp/math-seed05-release/replacement.json.gz
   --out /tmp/math-seed05-release --expected-saving 24` passed after the final
   harness scope/H4 guards were added. Fresh unchanged C++ legality and
   `columns_k` at KPAIRS 2/4/5 pass on both full words: **883/1,327/1,549** formal
   columns, **6/18/24** omitted-bridge controls per word, **96** total. Source
   exporter and native payload counts agree exactly with the independent
   Python receipt. `NATIVE.json` retains every proof-relevant native field;
   only stage timing and temporary source path fields are omitted there.
   The raw receipts and command logs remain in the reproduction output.
4. `python3 -I -B research/r439-frame520/test_package.py` passes **12 tests**.
   These include a complete isolated optimized-Python replay from a minimal
   five-file closure in a path containing spaces, three immutable-source
   corruption cases, altered certificate matrices/bills/object/programs,
   frozen research metadata, coverage counts and existing-output preservation.
5. `python3 -I -B research/r439-frame520/search.py --output /tmp/r439-frame520-reproduced.json`
   regenerated the frozen candidate byte-for-byte after replacing search
   assertions with explicit rejection checks. Completed coverage: 1,833
   trajectories, 372 exact shorter factorizations; no global optimum claim.
6. `make selected-record-check` passed. All native consumed source pins and the
   source/history pins in `SOURCE.json` match their exact base Git objects.
   The retained PR844 candidate matches Git blob
   `7251a9922c9e5efedc8692a491c676fa9155fc35` at its cited head.
7. The scoped reviewer independently confirmed the matrices, the PR844/PR904
   overlaps, lack of a preserved fixed-factor boundary, and the two reverse
   coefficient increases versus PR844. The reported control, metadata and
   native-input-scope gaps were fixed and checked. This was AI-agent review,
   not independent human review.

## Coverage limits and handoff

This package changes only a research directory. It does not change `upstream/`,
the source supplier, selected certificate, main proof, review ledger or CI.
No full repository `make verify`, selected cold replay, changed whole-hosted
invoice/outer assembly, Linux run or formal multiplication theorem is claimed.
The existing conditional exponent remains unchanged. The next integration step
is for a reviewer to accept the finite witness and decide whether to compose it
with other pending bit edits and rerun the complete supplier invoice.

The final pre-submission fetch still had main at the exact base. The refreshed
PR inventory through #922 added no competing frame520 result. PR844's 31-ADD
word is explicitly preserved and credited; this package adds four complete
ADDs of savings beyond it. The local claim is updated once with the final PR.
