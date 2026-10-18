# Executed validation

Environment: Linux x64, CPython 3.14.4, GCC15.2.0 build. Only Python's standard
library is required. Base and final refreshed upstream were both
`1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.

## Complete checks

Certificate generation:

```sh
python3 -I -B research/ck-all-dyadic-forest-seed23/verify.py --record
```

Observed output (364.05 seconds in the shared research environment):

```text
PASS_CK_ALL_DYADIC_FOREST cases=13501152 floor=16364 margin=63 columns=716x2 controls=10 no_new_kappa
```

Final isolated optimized replay, followed by the separately implemented full
integer oracle:

```sh
python3 -I -O -B research/ck-all-dyadic-forest-seed23/verify.py && python3 -I -O -B research/ck-all-dyadic-forest-seed23/independent.py
```

Observed output (609.15 seconds combined):

```text
PASS_CK_ALL_DYADIC_FOREST cases=13501152 floor=16364 margin=63 columns=716x2 controls=10 no_new_kappa
PASS_CK_PACKED_ORACLE cases=13501152 exact_lane_bits=20 full_receipt_match
```

Fast packaging controls on isolated temporary copies, including a path with
spaces, payload-preserving gzip corruption, recipe corruption and a missing
runtime input:

```sh
python3 -I -O -B research/ck-all-dyadic-forest-seed23/test_package.py
```

Observed output (18.87 seconds):

```text
PASS_CK_DYADIC_PACKAGE source_corruption=2 missing_source=1 optimized=1 outputs_preserved=1
```

The primary and oracle agree on all13,501,152 finite cases, full margin histogram,
8,275 grouped cost streams and digest
`b52788e8fc41293379c05dc693baf494426302e8733d98bc2930435685f0f571`.
No nonunit tie or improvement survives the same-parent unit/root comparison;
941 cases beat their root, with minimum root margin−116. The finite minimum
against the valid alternative is63. The infinite tails are the separate written
proof in README, not an assertion of infinite execution.

## Interrupted development invocations

An initial uncompressed-list/Fraction-heavy certificate generation hit its
300-second invocation deadline; no failed mathematical predicate was reported.
A subsequent packed-vector but Fraction-heavy run was explicitly cancelled
before completing. A bounded traceback showed Fraction-heavy source processing;
row-wise dyadic-integer endpoint replay and integer-gcd tariff normalization
then replaced those avoidable operations without changing the census domain.

The original packaging controls stalled awaiting child subprocess completion
and hit60 seconds; a30-second diagnostic showed the parent inside subprocess
communication. Final controls load the same isolated temporary verifier with
`runpy`, then exercise exactly the source-loading failure paths. The final
successful command above supersedes those interrupted invocation attempts.
These timings are execution records, **not** a controlled before/after performance
benchmark or a verifier-speedup claim.

## Boundaries and overlap

The final overlap refresh inspected new proposals through PR1205 and confirmed
PR961 (`4257ddf4b755cd0ac3bd3b0f6281cc5b2b1f72ad`) and PR964
(`7a3bf8460cf6ca16a2bf008ff51fdb06df1af938`) are merged. Their ledger entries and
PR816 are incorporated. The new scope is CK non-power dyadic numerators;
PR964 closes CK powers of two and PR961 closes the different X4 matrix.
PR1080/1081 alter the helper side or source matrix/lowering, and are not composed.

No full native/emitter/Clifford replay, global hosting/invoice/outer assembly,
selected cold replay, repository-wide suite, formal theorem prover or hosted CI
was executed for this unchanged-supplier research note. The original source,
selected result and upstream trees are not edited. The finite exact checks do
not discharge inherited all-size/compiler, realization, physical, precision/tape
or analytic obligations. No new κ is claimed.
