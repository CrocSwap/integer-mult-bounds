# Current binary owner census and production capacity

This source export supplies the binary counterpart to the recovered Gaussian
owner census at Ali Romman's #8042 head
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`.

The frozen [census proof](PROOF.md) establishes the exact per-context coefficient
22,339 and the bound

\[
\mathrm{capacity}\le B+22339\sum_e
\mathrm{count}[e](104904\,\mathrm{delay}[e]+1).
\]

Its literal graph is used at every production rank: 630 public registers,
39,600 instructions, 3,433 private owners at peak, 18,906 target positions and
104,904 paid labels. The proof includes private zero inputs, pending loans,
suspended contexts, opening and closing microsteps, and free-first historical
allocation. It does not count work-tape bytes. The independent reviewer found
a useful negative witness: paid cuts expose at most 2,803 private owners, while
closing cleanup reaches the full 3,433. Counting only yielded jobs is unsound.

The separate [production corollary](COROLLARY.md) combines that census with the
accepted mass enclosure published in PR #8091 at
`de02b59fa9a74d4958d0d114d25e9083ab91b022`. Its exact source-level delay bound
gives `sum count < 2*N^6` and `104904*delay+1 < N^77`, proving
`capacity < 2*B` for successful production binary calls, with `B=N^92`.
It answers the final count/delay question left explicit in the frozen census;
that earlier proof remains unchanged.

This proves the local binary beta=2 premise used in ordinary ancestor
composition. Complete selected storage and tape obligations, source admission
and selected kappa remain unchanged. A reused physical head retains the maximum
of its initial reserve and its new field-volume charge. An empty owner set
does not imply that old physical allocation has vanished.

## Reproduction

Python 3.11+ and its standard library suffice. No network, Git object database,
production-size calendar or runtime bootstrap is needed for these local checks.

```sh
python3 -I -W error -B check.py
python3 -I -W error -B check_corollary.py
```

Both commands work by absolute path from another directory and are bounded
well below the repository's 600-second replay limit. `RESULT.json` and
`COROLLARY-RESULT.json` retain author outputs. `FROZEN.json` records scientific
file hashes and strict normal/optimized-Python parity. The parent incorporates
independent reviews separately, preserving these scientific files.

`check.py` executes the complete source raw interpreter and native label
validator at columns 1 and 3. Actual allocation, retirement and clone methods
operate on one-byte fields; chart geometry and field transformations use an
ownership oracle. This tests allocation structure and labels, not numerical
field correctness. The source `Plan.events` and `Plan.decode` run on 18 small
supplied count/delay fixtures, bypassing numerical Plan construction. A mutation
removes descending loan custody and is rejected. The test counts are not claimed
to arise from a production mass measure.

The corollary checker captures actual production constructor arguments,
executes the source level/count loop on exact bounded fixtures and validates
the integer inequalities in the universal proof. Strict normal and optimized
Python yield identical receipts; explicit `require` checks remain enabled.

## Provenance and credit

`SOURCE-BINDINGS.json` authenticates resolved interpreter sources and two
compressed immutable literals. They were resolved through the pinned #8042
bootstrap retained by the parent audit package. Uncompressed JSON copies are
compared semantically with the immutable compressed payloads.

`COROLLARY-BINDINGS.json` separately authenticates the published mass proof,
its accepted review and grade bindings, and the installed binary constant.
Those four files are exact Git-object copies at the publication head above.
The inherited `powered.py` and archive provenance were resolved independently
by the capacity reviewer. Its literal ambient and unchanged raw grade tuples
are checked without tensor expansion.

The concurrent numerical mass enclosure retains its separate credit. Earlier
Gaussian census, byte envelope, coordinatewise-history principle and ancestor
composition retain their attribution. Source construction and runtime remain
credited to Ali Romman and all inherited contributors. Prepared for Jerry Chen
/@CubeJerry with substantial OpenAI Codex assistance, under Apache-2.0.

## Open next questions

Substitute this reviewed local beta=2 result in ordinary joined storage while
retaining its exact source and warm-entry scopes. The first step is independent
review and a source-hash checked join in the parent package. Remaining global
supplier and tape obligations require their own source-bound proofs; this owner
count alone does not establish them.
