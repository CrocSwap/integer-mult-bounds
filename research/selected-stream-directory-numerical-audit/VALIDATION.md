# Validation receipt

2026-10-15, macOS arm64. Parent checker and separate math-storage-lifetimes
specialist used disjoint implementations and file ownership. The specialist's
final source/proof/coverage review found no mathematical or material coverage
issue; two wording clarifications were incorporated. No human or formal-kernel
review is claimed.

## Executed checks

- CPython3.12.12 registered replay:
  `python3.12 -I -B scripts/research_package.py --package research/selected-stream-directory-numerical-audit`
  passed, including all three declared commands.
- CPython3.14.6 optimized main, independent and six external-control tests
  passed. The primary receipt has 228 complete stream cases, 152 one-hot basis
  cases, 25,500 payload bits, 18,542 stream residue allocation events,seven full
  directories and 1,283 literal occupied-cell scans.
- The separate source execution versus integer allocation-event model covers
  all 135 canonical coefficient cases for 2<=M<=16, five full directory fixtures
  and four callback compositions. It also retains three failure-leak witnesses
  and an accepted unequal-coefficient semantic witness. Exact coverage and
  all-parameter proof premises are in INDEPENDENT.md.
- Five internal controls reject two undercharges, a borrowed result, a leaked
  callback Word and a changed repeated coefficient's resulting permutation.
- Six external tests reject source corruption, a missing manifest entry, a
  changed source path and a Boolean substituted for an integer receipt field.
  An extra fully restored multiplication temporary preserves values and final
  ownership but fails the max-bound guard; suppressing only that guard admits
  its seven-Word peak. A timestamp-valid bytecode sentinel is first proved
  effective under ordinary import, then bypassed by the authenticated source
  loader. All package bytes, including caches, are unchanged by that replay.
- Every vendored file was independently compared with its exact PR2801 Git
  object. The six executable modules also match original PR2697 paths;
  SOURCE-CHAIN.json records those second-hop comparisons. The complete
  predecessor notice is retained.
- The selected-record source/proof binding check passes. It is an integrity
  check, not a complete selected cold replay or supplier acceptance.

The external-control positive run is a relocated Git-free package execution.
The final preserved commit is additionally exported for read-only direct replay;
its exact hash, command logs, publication verification and cleanup receipt are
recorded outside the disposable checkout in the automation handoff. This file
makes no hosted-CI claim.

## Reproduce

```
python3.12 -I -B scripts/research_package.py --package research/selected-stream-directory-numerical-audit
python3 -I -O -B research/selected-stream-directory-numerical-audit/verify.py
python3 -I -O -B research/selected-stream-directory-numerical-audit/independent.py
python3 -I -O -B research/selected-stream-directory-numerical-audit/test_verify.py
```

Direct scripts need only the package files and Python standard library. Normal
replay reads the fixed receipt; `verify.py --emit` only prints a candidate
receipt and never overwrites it. The independent checker uses explicit guards
that remain enabled with `-O`.

No full selected GL64 Boolean execution, multi-lift dimension 64 directory,
whole-caller/category storage theorem, arbitrary exception cleanup, fixed-tape
bank/movement invoice, selected cold replay, kappa gain or formal kernel is
established. The two exact source-level phase bounds and their conditional
callback composition have the explicitly written successful-call premises.
