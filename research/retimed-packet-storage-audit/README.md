# Retimed packet storage and stopping audit

This independent source-bound audit of PR #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd` follows a nonidentity covered packet
through its odd number of same-rank exchanges, retaining high representatives,
pending/answer prefixes, both basis routes and full-cohort entry/return.

The scoped path passes. Named pages, banks, stage-root files and different-stage
ancestor spools remain live and charged. Newly opened **rank-local transient**
spools close before the next same-stage edge. The coupled packet invariant is

\[
(p-p_0)+(a-a_0)+\ell=V,
\]

and the real compiler caller gives `V=W/B`, then `ell=V/Q` in covered mode.
The proof binds these equalities to arbitrary-depth suffix return and historical
address reuse. A Gaussian child must start after the historical parent high,
not after the current count of live slots.

## Contents

- [PROOF.md](PROOF.md): dominant storage argument, source binding, limitations
  and the original local-owner census handoff, addressed by the supplement below.
- [STOPPING.md](STOPPING.md): supplemental source predicate/serial-bit audit,
  conditional on entry-header and physical-field contracts.
- `audit_packets.py`: physical packet execution, independent matrix action
  oracle, dirty ancestor guards, recorded lifetimes and five source mutations.
- `audit_owner_windows.py`: historical slot holes, zero owners, differing child
  widths and a minimal rejected live-count-base mutation.
- `verify_stopping.py`: exact capped comparator, bounded serial-bit lowering,
  child-premise checks and failure controls.
- [formal/SOURCE-CORRESPONDENCE.md](formal/SOURCE-CORRESPONDENCE.md): a Lean
  4.36 proof of the actual capped-power predicate and failed-caller relation,
  with exact source correspondence and separate author/root kernel receipts.
- `SOURCE-BINDINGS.json` and `sources/pr8042/`: exact pinned source bytes and
  the original hash-checking predecessor bootstrap. No network is needed.
- `evidence/`: executed receipts, which corroborate the written argument.
- [census/OWNER-CENSUS.md](census/OWNER-CENSUS.md): the source-bound bound of
  115,058 owned fields per calendar context, including zero inputs, output
  copies, half-column loans and suspended parents. Its production `<2B`
  consequence retains the universal mass enclosure explicitly.
- [census/review/CROSS-REVIEW.md](census/review/CROSS-REVIEW.md): the separate
  interval, custody, source-syntax and free-first review. A location-only
  [adapter](census/review/PORTABLE-REPLAY.md) preserves its exact checker bytes.
- [bytes/PROOF.md](bytes/PROOF.md): complete local historical byte bounds for
  the wide owner route (`<8V`), padded type route (`<9V`) and production repair
  (`<=8V`), with the production-header hypothesis and generic-API boundary.
- [bytes/review/REVIEW.md](bytes/review/REVIEW.md): independent source proof,
  stream/permutation checks and the corrected distinction between the
  17-bit tag comparison and a symbolic 33-bit total-volume counterexample.

## Reproduce

Requires Python 3.11 or newer and `git` for the original source patch installer.
No third-party Python package is required.

```sh
python3 -B scripts/research_package.py --package research/retimed-packet-storage-audit
# Standalone equivalent, from repository root:
python3 -B research/retimed-packet-storage-audit/verify.py --output /tmp/retimed-audit-results
```

The original driver checks all retained source hashes, restores a fresh temporary
runtime and executes all three packet fixtures, six storage/ownership source
mutations and the stopping supplement. Expected final marker:
`PASS_RETIMED_STORAGE_AND_STOPPING_AUDIT`.

The registered replay also executes the consolidated owner/byte supplements
with a separate fresh offline restoration:

```sh
python3 -B research/retimed-packet-storage-audit/verify_supplements.py \
  --output /tmp/retimed-owner-byte-results
```

Expected marker: `PASS_RETIMED_OWNER_AND_BYTE_SUPPLEMENTS`. This runs both
author checkers and both separate review methods. The byte author driver runs
in a temporary package copy, and every new receipt goes to the chosen output
directory, preserving committed evidence. The two registered commands have
600-second bounds, totaling at most 1,200 seconds. The supplements need no
Lean installation and do not rerun the formal supplement.

`--quick` omits only the 2,834,352-record full-high oracle and is not the complete
retained receipt. Detailed per-packet traces go to the selected result directory.

Each packet fixture has one weighted-child depth: at `N=2` the child receives
one atom and stops. The 1/3/5 calls are siblings. Arbitrary depth follows from
the actual caller volume equations and suffix-stack induction. Cover enumeration
is inherited from the source; the payload action oracle is separate. The
Gaussian fixture exercises the actual allocator, not the enormous positive word.

The stopping appendix credits #8042's existing `OuterStop.lean`. It supplies
caller binding and a serial lowering with operation counts, without treating
Python big integers or wall-clock measurements as a tape-machine implementation.

The consolidated formal supplement proves the universal Boolean predicate,
including its low-bit branch and omitted final square. It uses only `import Lean`;
no Mathlib is needed. With an installed Lean 4.36.0 binary, replay it
independently of the Python-only registered packet runner:

```sh
python3 -B research/retimed-packet-storage-audit/formal/replay.py \
  --lean /absolute/path/to/lean --output /tmp/retimed-capped-power-review
```

This wrapper restores the same pinned runtime offline, checks the reviewed
proof hash, source AST and caller, and audits all fifteen kernel axiom reports.
The only dependencies reported are standard `propext`, `Quot.sound` and
`Classical.choice`. Python operational semantics and machine costs are not
formalized. The source inventory now also retains the unchanged predecessor
`OuterStop.lean`, for 26 original source files; earlier 25-file receipts describe
the original packet package before this addition.

No new kappa, activation threshold, total storage constant or removal of a
foundational physical premise is claimed. The package performs no remote
publication. Prepared for @CubeJerry with OpenAI assistance. Model cross-review
is not independent human review; kernel acceptance is limited to the stated
formal propositions.

## Open next questions

The Gaussian simultaneous-owner census is now proved for the exact source
under its stated valid-call contracts. Its production exponent consequence
retains the universal mass enclosure. The local byte supplement covers three
named routes; the remaining ordinary role/ancestor-bank census, legal adapter
nesting, outer CRT/control allocations and full fixed-tape tariff remain open.
Their concrete first steps are recorded in TASK.json. The original proof and
review are retained as historical checkpoints, not silently rewritten.

The standalone source export is self-contained and hash authenticated.
SOURCES.json pins catalogue/selected-record provenance; SOURCE-BINDINGS.json
binds the retained unmerged source bytes without relying on that foreign
commit being available in a clean checkout.
