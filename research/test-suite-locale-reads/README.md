# test-suite-locale-reads

**No kappa, no certificate change.** One reproducible environment failure
repaired: the repository's documented test command fails on a native Windows
cp1252 host because `tests/test_research_current_status.py` reads
`docs/research/current-status.md` with the locale codec.

## Task card

- **Task ID / scope key:** `verifier-engineering` / `portable-replay`
  (scope key `831cc1a3c8f9ff01b197`, chooser OS nonce
  `c7669648496a57422bfa478f1d356cad`, priority revision 3).
- **Base commit:** `0b1cccf86e2f5132ed286a26ef0a681a495740ea` (selected-record
  SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`).
- **Concrete object and question:** the suite's own document reads. On Windows
  with the Git-for-Windows defaults, `python3 -B -m unittest discover -s tests
  -p 'test_research_*.py'` (without `PYTHONUTF8`) fails with three errors in
  `test_research_current_status.CurrentStatusTests`, all from
  `STATUS.read_text()` decoding `docs/research/current-status.md` with cp1252
  while the document contains byte `0x9d` (in U+201D). Can this be repaired
  minimally and pinned by a regression?
- **Scope status:** refined, within the card's premise ("one reproducible
  environment failure repaired") and its allowed variation (one
  interpreter/environment mismatch). Reason recorded in [TASK.json](TASK.json).
- **Existing restriction being changed:** none in the mathematics. The prior
  Windows-encoding work (merged #1299/#1293-rgb line, credited below) covered
  `scripts/research_package.py`, `scripts/find_overlap.py` and
  `tests/test_research_onboarding.py`; its static guard
  (`TextEncodingTests.SCRIPTS`) covers five onboarding scripts only, and does
  not cover the suite's other document readers.
- **Method; parameter range:** reproduce on native Windows cp1252 (Python
  3.13.15), fix the module's text reads to explicit UTF-8, add a static
  locale-independence guard (the same AST pattern the onboarding tests use) and
  a load-bearing byte control, and register a bounded replay that forces a
  legacy codec (cp1252 on Windows, the C locale elsewhere).
- **Nearest overlapping PRs:** https://github.com/CrocSwap/integer-mult-bounds/pull/1702
  (makes the CP1252 overlap regression in `test_research_onboarding.py`
  self-contained; different file and object, no conflict with this change) and
  the merged #1299 line (predecessor). The gzip/canonical-payload variation of
  the card is under active concurrent work
  (https://github.com/CrocSwap/integer-mult-bounds/pull/1559,
  https://github.com/CrocSwap/integer-mult-bounds/pull/1824) and was not
  duplicated. Overlap refreshed at 2026-10-14 11:10Z and again before
  submission.
- **Optimistic full cost budget:** trivial runtime (the suite runs in about
  15 s). Required observable improvement: the documented command exits 0 with
  and without `PYTHONUTF8` on native Windows, and the new guard fails on the
  base-commit module.
- **Success evidence; falsification; cap:** see below. Falsification test: the
  static guard reports exactly the base module's bare reads (lines 10 and 26),
  and a bare locale read of the document fails in a forced-legacy child. One
  session, one pivot (the historical-failure candidate was killed first).

## Scope and evidence

**What was reproduced (before).** Windows 11, cp1252, Git 2.55.0.windows.5
(`core.autocrlf=true`), CPython 3.13.15. At base `0b1cccf8`, without
`PYTHONUTF8`:

```text
ERROR: test_current_section_matches_selected_record ... setUp
  File ".../tests/test_research_current_status.py", line 26, in setUp
    self.text = STATUS.read_text()
UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 1014
Ran 42 tests in 13.787s — FAILED (errors=3, skipped=2)
```

The same command with `PYTHONUTF8=1`, and everything under CPython 3.12,
passed. The three errors are one root cause: a locale-dependent read of a UTF-8
document.

**Obstruction recorded (killed first candidate).** The historical Windows
failures cited in many PR bodies no longer reproduce at base:
`test_research_onboarding` runs green natively (Python 3.13.15: 18 tests with 2
environment-gated skips; Python 3.12: all 18 pass, `core.autocrlf=true`),
including the formerly failing scaffold-pin and
`os.killpg` tests. Credit for that repair goes to the merged
#1299/#1293-rgb line ("UTF-8 metadata/pipe handling and Windows child-tree
timeout fallback", recorded in `research/community-efficient400-audit`) and to
the feedback report in
https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18910079,
which identified the same byte (`0x9d`) in `research_package.py`. This package
fixes the instance that line missed and pins it.

**What is established (after).** The module's reads now pass explicit
`encoding="utf-8"`. Two regression tests were added in the same module, in the
style of `test_research_onboarding.TextEncodingTests` ("a UTF-8 CI host cannot
observe locale-codec bugs, so check the calls statically"): an AST guard
requiring `encoding=` on every text read/write in the module, and a
load-bearing control asserting the document contains `e2 80 9d` and is
undecodable as cp1252 (deterministic on every host). Evidence:

```text
python -B -m unittest discover -s tests -p 'test_research_*.py'   # no PYTHONUTF8, 3.13.15
Ran 44 tests in 14.672s — OK (skipped=2)
python3.12 -B -m unittest discover -s tests -p 'test_research_*.py'
Ran 44 tests in 16.541s — OK
```

Failure controls (both run in this session): the static guard applied to the
base-commit module reports missing `encoding=` at exactly lines 10 and 26; a
bare `read_text()` of the document in a `PYTHONUTF8=0` child fails with the
same `UnicodeDecodeError` on this host. The registered replay
(`verify.py`) reruns all of this with a forced legacy codec.

**Limitations (not checked).** No mathematics: no kappa, certificate, frozen
pin, `upstream/`, selected-record or cold-replay change; the acceptance gate
"preserve immutable source hashes and proof-relevant content" is untouched
because no comparison logic changed. The roughly 100 remaining
locale-dependent text calls in `tests/` and the one-off `scripts/` generators
were inventoried but not swept (open question 1). The registered replay forces
the legacy codec only for the repaired module; whole-suite behavior under a
true POSIX ASCII locale is unmeasured (open question 2). macOS and Linux hosts
were not executed here. [SOURCES.json](SOURCES.json) pins
`tests/test_research_current_status.py` at its **base-commit** bytes as
provenance (the defective version this PR repairs); it cannot be a live input
under the pin contract because this contribution changes it.
`docs/research/current-status.md` is the live input and matches its pin.

## Reproduce

From repo root, on any host:

```sh
python3 scripts/research_package.py --package research/test-suite-locale-reads --check-only
python3.12 scripts/research_package.py --package research/test-suite-locale-reads
```

The second command runs `verify.py`: the cp1252 load-bearing control, the bare
legacy-locale read failure control, the module's unittest under a forced legacy
codec and the default environment, and the documented suite command in the
default environment. The native-Windows reproduction of the original failure
needs no `PYTHONUTF8`; on POSIX the replay forces `LC_ALL=C` with
`PYTHONCOERCECLOCALE=0` and `PYTHONUTF8=0`.

## Open next questions

1. **Sweep the remaining locale-dependent reads in `tests/`** (about 100 calls
   across about 40 modules). Why it matters: only `current-status.md` carries
   cp1252-undefined bytes today, so only one module crashes; the next
   typographic quote added to any read document recreates the same bogus
   errors elsewhere. First step: extend the static AST guard to all
   `tests/*.py` and fix the call sites that read documents already containing
   non-ASCII bytes. Blocker: mechanical churn across frozen-era test modules
   wants maintainer buy-in.
2. **Whole-suite guarantee under a POSIX ASCII locale.** Why it matters:
   "green on Windows cp1252" and "green on `LC_ALL=C`" are different claims;
   the registered replay only forces the legacy codec for the repaired module.
   First step: run the full discover command under `PYTHONUTF8=0
   PYTHONCOERCECLOCALE=0 LC_ALL=C` on Linux and triage failures. Blocker: this
   session ran on Windows only.

## Credit

Prepared by Aaron Wang, with help from opencode. New work is Apache-2.0.

Predecessor credit: the merged #1299/#1293-rgb Windows encoding line
(UTF-8 metadata and pipe handling, child-tree timeout fallback, cp1252
simulations and the `TextEncodingTests` static-guard pattern, summarized in
`research/community-efficient400-audit`); the failure report and environment
details from
https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18910079;
the `docs/research/current-status.md` consistency tests themselves
(`tests/test_research_current_status.py`, authored upstream of this base). This
package adds the instance their guard missed, a regression in the module that
failed, and a replayable legacy-locale check. No mathematical claim is made.
