# Executed validation

Run: 2026-10-13 UTC. Contributor: Ross Richardson, with substantial OpenAI
Codex assistance. Research base `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`;
submission base `ba82555c64e1879e4b7decce28186f208fcb8262`.

## Local evidence

- Independent complete receipt passes with `python3 -I -O -B .../verify.py`.
  All six complete source-derived histograms, claimed endpoints, next-point
  lower bounds, original conservative rational margins and strict status
  flags are checked. The 70-object Merkle capsule anchors every source to
  its recorded commit and consumes every captured object.
- All **18 tests pass** on CPython **3.14.6** and **3.9.6**, macOS 26.5.2 arm64,
  including optimized mode. Controls corrupt and remove each of the 70 Git
  objects, rehash a modified supplier, append an unused valid object, omit
  each of four bridge terms, alter divisibility/geometry, falsify interval
  engines and old margins/flags, preserve rank while changing the moment,
  and corrupt eight on-disk receipts/capsules.
- Exact Fraction oracles enclose all **66 used log ratios plus four distinct
  boundary cases** and 27 seeded exponential inputs. The test seed is 97;
  no additional supplier or parameter search is performed.
- Minimal relocation passes using only `verify.py`, `sources.json.gz` and
  `EXPECTED.json`, with an empty PATH/PYTHONPATH and no repository checkout.
  A before/after file comparison confirms the verifier writes nothing.
- Both unmodified original PR225 checkers pass in separate temporary trees,
  with complete original receipts: four profiles at the reviewed head, six
  at the current head. See [original-replays.txt](original-replays.txt).
- Capsule recapture gives the same **decompressed bytes** and the complete
  independently regenerated receipt is byte-identical. Gzip container bytes
  are not used to decide mathematical equality.
- Selected-record integrity and its **five tests** pass. The **14 ledger
  tests** and complete **682-entry ledger verifier** pass. Only the PR225
  ledger row and its Markdown link change; counts, disposition and other
  entries are preserved. Whitespace checks pass.

The final script and receipt SHA256 values are:

```text
5e6843c106df4173f23ada44982ec505cca399ddd57976e43d4159eea35d8384  verify.py
92b51aca131d02a54a0c655243701406a7f4180f30036adf0ff6c7004276e55b  test_package.py
ab3e927b30fc13d0cff3b076be791ef5be8a41305f046cb2068da23f61b618ca  capture.py
812b92da4564e27665b2847e27d9644f5e8abe32abb03dabf89c3e38a956f53c  replay_original.py
438e2bacd4f6bce925d436e37b7f5b7d9c33b340318ea64d49ea5fe262a892dd  EXPECTED.json
```

## Submission and limits

Before submission, the open queue was refreshed through PR1106 (761 open
PRs); PR225 remained at the same exact head, with no competing PR225
reconciliation found. The recent frontier update is unrelated to the pinned
historical sources and leaves PR225's recorded gap unchanged.

The focused Linux workflow is supplied, but no hosted CI result is claimed
by these local receipts. No repository-wide `make verify`, native supplier
rebuild, external Lean compilation, or all-size transfer audit was performed.
These checks concern a standalone historical capsule and one ledger row.
No timing improvement or new multiplication bound is claimed. Neither
`codex` nor `codex-automation` exists in the repository's available labels.
