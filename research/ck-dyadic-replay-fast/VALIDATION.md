# Executed Verification

Base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`; macOS arm64.
CPython 3.14.5 and a temporary, isolated CPython 3.12.13 installation.
All dependencies are standard-library modules; no package-manager lockfile
was introduced or modified.

The following checks passed:

```sh
python3 -I -B research/ck-dyadic-replay-fast/test_fast_rows.py
python3 -I -B research/ck-dyadic-replay-fast/verify.py
python3 -I -O -B research/ck-dyadic-replay-fast/verify.py
python3.12 scripts/research_package.py --package research/ck-dyadic-replay-fast
```

The last command used `/private/tmp/seed89-python/cpython-3.12.13-macos-aarch64-none/bin/python3.12`.
It validates all Git blob/SHA256 provenance, declares all fourteen live inputs,
and runs the bounded registered command, ending with
`PASS_REGISTERED_RESEARCH_PACKAGE research/ck-dyadic-replay-fast outcome=completed`.
The deterministic RESULT.json file SHA256 remains
`5eba922d9fb41d90786a4b2e68e4890e86ca8e75ba7adc9caeed7a6a9c2a1bff`.

Coverage: 74,760 direct normalization calls and 151,450 addition returns,
compared exactly to separate frozen module instances; four complete streams,
374,606 primitives, all 725 arbitrary input columns; all endpoint/price/prefix
fields identical. Seven focused groups include 729 signed normalizations,
328,050 signed sums and a separate seeded 3,000-step Fraction oracle, all six
inherited arithmetic groups, aliasing/transient/private/domain defects,
context restoration, and drift rejection for all fourteen source files.

The complete unchanged predecessor replay recomputes its target/helper census,
Fraction checks, native emission, frame/wrapper audit and original ten circuit
plus twenty-five native controls. Its full canonical receipt is unchanged:
`5cf72786877f7049421ad23e9a2a832e61ca74d9547c9e59717415d9e1b4f881`.
The adapter's direct `run.py` command also passed separately.

Five alternating paired complete-stream timings per interpreter, preceded by
one warmup pair, are retained in BENCHMARK.json and BENCHMARK-PY312.json.
Medians: 1.50477x on Python 3.14, 1.45178x on Python 3.12. The same exact
word/result hashes appear in both reports. Host activity was not isolated;
these are descriptive integer-stage timings, not a full-verifier gain.

The final fresh overlap search had complete pagination for 787 open PRs and
146 discussion/comment/reply records; nearest PR1234 head
`8812ca21c43f5cea16276c7fa539fa8d1559b0f1` and PR1184 head
`2f1c9e0e671bb10aecd452e18449130b0601932d` were inspected. The former changes
frame geometry helpers; the latter changes the native macro auditor's row
representation. This targets the different canonical primitive executor.
No same-target claim was observed; this is not a novelty proof.

After refreshing main to `410026dc5513b87db92ae98571d1d5984c69a983`, a path-limited
comparison found no changes to the consumed predecessor/data/native files.
Only the new `research/ck-dyadic-replay-fast/` package is proposed.
No selected-frontier modification, selected cold replay, full repository suite,
full multiplication theorem proof or hosted-CI pass is asserted here.

Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance.
No independent human review. Apache-2.0.
