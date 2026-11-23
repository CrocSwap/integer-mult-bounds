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
  and remaining local-owner census obligation.
- [STOPPING.md](STOPPING.md): supplemental source predicate/serial-bit audit,
  conditional on entry-header and physical-field contracts.
- `audit_packets.py`: physical packet execution, independent matrix action
  oracle, dirty ancestor guards, recorded lifetimes and five source mutations.
- `audit_owner_windows.py`: historical slot holes, zero owners, differing child
  widths and a minimal rejected live-count-base mutation.
- `verify_stopping.py`: exact capped comparator, bounded serial-bit lowering,
  child-premise checks and failure controls.
- `SOURCE-BINDINGS.json` and `sources/pr8042/`: exact pinned source bytes and
  the original hash-checking predecessor bootstrap. No network is needed.
- `evidence/`: executed receipts, which corroborate the written argument.

## Reproduce

Requires Python 3.11 or newer and `git` for the original source patch installer.
No third-party Python package is required.

```sh
python3 -B scripts/research_package.py --package research/retimed-packet-storage-audit
# Standalone equivalent, from repository root:
python3 -B research/retimed-packet-storage-audit/verify.py --output /tmp/retimed-audit-results
```

The driver checks all retained source hashes, restores a fresh temporary
runtime and executes all three packet fixtures, six storage/ownership source
mutations and the stopping supplement. Expected final marker:
`PASS_RETIMED_STORAGE_AND_STOPPING_AUDIT`.

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

No new kappa, activation threshold, total storage constant or removal of a
foundational physical premise is claimed. The package performs no remote
publication. Prepared for @CubeJerry with OpenAI assistance; model cross-review
is not independent human or kernel acceptance.

## Open next questions

The production simultaneous-owner census and full fixed-tape tariff remain open; their concrete first steps are recorded in TASK.json. The standalone source export is self-contained and hash authenticated. SOURCES.json pins catalogue/selected-record provenance; SOURCE-BINDINGS.json binds the retained unmerged source bytes without relying on that foreign commit being available in a clean checkout.
