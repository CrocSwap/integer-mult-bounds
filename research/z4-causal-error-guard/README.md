# One fewer sufficient guard bit for the persistent z4 forward word

**Scoped proof with exact finite corroboration. No new kappa.** The unchanged
PR1410 joint forward word needs only **13 sufficient fractional guard bits**
under PR2502's explicit relative-ADD error model. Its earlier sufficient bound
was 14. This result does not claim minimum actual precision.

For exact initial registers bounded by B, exact NEG, no overflow and local ADD
error at most u times the sum of the two approximate operand magnitudes,
the error in every register at every chronological cut is at most B*2^-b
whenever u <= 2^(-b-13), for every b >= 0. All workspace may be dirty.

The [proof](PROOF.md) replaces a uniform feedback maximum with a strictly
causal triangular recurrence. Exact signed impulses of earlier errors bound
each new error before the next ADD. Integer upward rounding at scale 2^32
gives the all-cut coefficient bound

    30186730759261 / 4294967296 < 7029 < 8192.

The maximum occurs at record cut 1730, register 4. [RESULT.json](RESULT.json)
is a generated receipt bound to the package and input source hashes.
The standalone [verifier](verify.py) computes the recurrence forward, then
reconstructs every local inequality and every changed output row by a separate
backward covector traversal. It compares 1,720 ADD recurrences and 1,904 cuts.
The inherited word is identified by its existing hash; its endpoint and the
predecessor's aggregate error constants are cited, not audited or recomputed.

## Reproduce

From the repository root, CPython 3.12 and standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/z4-causal-error-guard
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/z4-causal-error-guard/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/z4-causal-error-guard/verify.py
```

Another Python 3.12 interpreter may replace the machine-specific path.
Expect `PASS_Z4_CAUSAL_ERROR_GUARD q=13 upper_C<7029 allowance=8192`,
`PASS_BACKWARD_CAUSAL_CHECK adds=1720 cuts=1904`, and the registered runner's
completion marker. Normal execution writes nothing. The explicit option
`--write-receipt NEW_PATH` generates a receipt and refuses occupied paths.
The manifest [VERIFY.json](VERIFY.json) registers normal and optimized replay.

## Scope and predecessor credit

This contribution is **produced by Nick Petalas**. Credit ywz65 / [PR2502](https://github.com/CrocSwap/integer-mult-bounds/pull/2502)
for the local relative-error model, chronological error impulses, its earlier
sufficient guards and the observation that its bound may be conservative.
Credit Cinna Davis / [PR1391](https://github.com/CrocSwap/integer-mult-bounds/pull/1391)
and [PR1410](https://github.com/CrocSwap/integer-mult-bounds/pull/1410) for the unchanged
word and endpoint, Aaron Wang / [PR2464](https://github.com/CrocSwap/integer-mult-bounds/pull/2464)
for the precision handoff, Ross Richardson / PR1287 and Sagar Thakrar / PR1227
for the retained paired-frame lineage. Original source notices remain unchanged.
The elementary triangular majorization argument carries no literature-priority
claim. Apache-2.0. Independent human and formal proof-kernel review are unclaimed.

This is a precision side result under a changed `uniform-transfer-audit` scope,
not another check of a predecessor theorem. [TASK.json](TASK.json) records the
scope and [SOURCES.json](SOURCES.json) pins canonical base, guidance and inputs.
The selected source-binding orientation check is distinct from a supplier replay.
There is no physical host, internally rounded child, initial-data uncertainty,
inexact NEG, overflow, range or tape-cost analysis. Separate-call and inverse
precision bounds are unchanged inherited claims. Supplier admission, all-size
implementation and analytic recovery remain unrun. The selected frontier is
unchanged.

## Open next questions

- Can the causal certificate be charged to a named physical host's precision
  bucket, including input uncertainty, child errors, integer range and enlarged
  workspace lifetime? Start by stating that host's local error contract. This
  is blocked by the physical interface, not by another aggregate guard estimate.
- Can a rounding-specific argument show that 12 bits suffice or are insufficient
  for this same forward word? First state an actual rounding rule and construct
  reachable error signs. The present sufficient majorant proves neither side.
