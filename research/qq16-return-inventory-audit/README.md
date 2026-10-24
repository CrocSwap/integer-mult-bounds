# Independent QQ16 protected-return ownership audit

**Scoped independent finite audit.** The unchanged PR4790 ownership adapter
and PR4167 protected-return transaction agree with a separately implemented
role oracle on all **120 arrangements and 480 directed transitions** of a
five-role quotient. A second check executes all 480 transitions consecutively
on one persistent fixture. All four return locations are covered: producer
bank, producer private slot, service bank and service private slot.

The complete fixed-copy versus adopted-return action difference also agrees
in **676 paired fixtures**, covering every old length `m=0..12`, return length
`n=0..12`, and the four locations:

```
saved (reads, writes, unit moves) = (5n+2, 2n, 4n+2).
```

This tariff and its independence from m are credited **prior results**, not
a new saving. The additional contribution is independently arranged coverage
of arbitrary order in this quotient, repeated ownership reuse, unequal and
empty payloads, preserved unrelated dirty tapes, and faults in the actual
cached bindings. Eleven invalid-precondition controls and six actual
in-memory implementation omissions reject. No defect was found in the
checked successful return boundary. No new kappa or full caller acceptance
is claimed.

## Exact boundary and independence

Audited PR4790 head: `38dd6b59d50d346bb34fea02a4ee1ac8d282ebbf`.
Its `adapter.py` blob `d25a04b9bbfd01851aabe905cc73837dda8ec2ed` is unchanged
on this package's main base `cef4b52f2a59009865bf8eabde1be3f159063703`.
[SOURCES.json](SOURCES.json) pins seven live inputs and the historical task
catalogue/selected record. The predecessor's merged, partially reviewed status
is not scientific acceptance and is not changed by this audit.

The verifier executes the actual `ReturnProtocol`, `owned_tapes`,
`CallerStorage` constructor and `_distinct` guard. It reads nested archives
without extracting them, compiles the original `Tape`/`Meter` sources, and
selects the unchanged AST function bodies for `adopt_return`, `transfer` and
`erase_marker`. It authenticates complete input bytes before execution; the
JSON output identifies the nested source hashes. It does not import PR4790's
verifier, receipt, expected counts or fixture implementation.

The independent fixture explicitly lists physical inventory and predicts the
swap of two identities. It uses small structural caller objects, not actual
`Machine`/`Ordinary` controllers. Each caller has one bank packet and one
private slot, plus dirty current/header/capsule/output/pool/parking tapes.
There is one native output, one fixed native tape, two auxiliary tapes and
three separate storage tapes. The returned result is already complete; all
heads initially meet the source return contract. This is an audit of the
return boundary, not a replacement implementation of the preceding child.

Five moving tape identities occupy the four packet locations and native
output. Their star transpositions generate all `5!` arrangements. The first
check constructs every arrangement independently and invokes each possible
return, varying saved engine-inventory traversal order and payload lengths.
The second follows a deterministic Euler tour of all 480 directed edges on
one live fixture, checking cached inventories after every step. Before each
step, the test environment supplies a new completed native result, rearms its
marker and preserves allocated high-water backing. This unmetered fixture
refill is explicitly not a native-child execution or a free implementation.

At every checked return the oracle verifies the exact role permutation,
engine membership, producer separation, external and parked bindings,
conservation of all physical tapes, unchanged returned bytes/head, full old
body/marker retirement, and unchanged unrelated dirty bytes and heads.
The fixed-copy arm is checked separately and meters the same complete interval.

The code does **not** test `rewrite_return`, installation into actual callers,
the producer/service fence, actual discard after interruption, native output
production, the 511014-Gamma census, numerical semantics or arbitrary larger
inventories. Finite quotient closure is not a proof of those contracts.

## Source argument reviewed

For disjoint inventories P, S and N, let o be a caller's obsolete target and
r the closed native backend's protected output. The retained transaction
preserves r's complete body, physically clears o and erases o's marker, then
exchanges their role bindings. On a producer return, P loses o and gains r;
N loses r and gains o; S stays fixed. On a service return, S and N perform the
same exchange while P stays fixed. Therefore disjointness and the complete
physical union are preserved, provided the actual caller has no escaped alias.

PR4790's cache updates match those substitutions, rebuild external roles and
run the original ownership guard. The current source graph traversal finds
the changed physical roles rather than following the separately owned backend.
An omitted `parking.roles` update leaves an old physical reference visible to
that traversal and is rejected in the service fixture. These observations
corroborate the predecessor's conditional invariant; they do not prove that
all production continuations meet its no-escaped-alias premise.

For dense canonical bodies, the source fixed transfer has tariff
`(5n+2m+7, 2n+m, 4n+2m+10)`. The adopted arm pays old-target clearing
`(2m+3, m, 2m+4)` and two origin checks `(2,0,4)`. Each arm also erases
one marker at the same tariff. Subtracting yields `(5n+2,2n,4n+2)`.
The finite paired checks meter the literal source bodies, including empty
cases, rather than evaluating that formula twice. Finite role-table control
is not priced by the Tape meter; its signed cost remains unknown.

## Controls and reproduction

The eleven precondition controls cover missing/duplicate engine membership,
stale external ordering, storage aliasing, producer/engine overlap,
service/native overlap, stale parked roles, an open backend, a noncanonical
result head, an unauthorized caller and a wrong protected result. The first
nine also compare physical bytes and heads before and after rejection.

Six copies of the actual implementation are mutated in memory: omit native
cache update, service cache update, external cache rebuild, parked-role update,
backend-output rebinding or old-marker erasure. Each fails at its named
semantic boundary. No source file, pin or frozen archive is modified.

Python 3.12 standard library; run from repository root:

```sh
python -I -W error -B research/qq16-return-inventory-audit/verify.py --json
python -I -O -W error -B research/qq16-return-inventory-audit/verify.py --json
python -B scripts/research_package.py --package research/qq16-return-inventory-audit --check-only
python -B scripts/research_package.py --package research/qq16-return-inventory-audit
```

The direct commands are read-only and need no Git or network. Normal and
optimized receipts agree on Windows, CPython 3.12.0. Each direct audit takes
about one second on the development machine. Only this package is added;
predecessors and the selected frontier remain unchanged.

**Separate full-replay limitation.** An attempted ordinary replay of
`research/qq16-protected-return-caller/verify.py` fails on this Windows host
before any return case executes. Inside the retained PR2753 verifier,
`physical = sorted(str(path.relative_to(here/'predecessor')) ...)` produces
Windows backslashes, while `FROZEN_FILES` uses POSIX separators. The failure is
`ValueError: no omitted or extra predecessor files`. No such guard was waived
or patched. The original complete integration replay is **not independently
reproduced here**; its earlier author/hosted evidence remains separately credited.
The direct audit authenticates and executes a smaller declared source closure
and makes a correspondingly smaller claim.

## Task, overlap and credit

Priority revision 7; picker nonce `3596dd4d3cb801c77cb9849b8b3e895d` offered
the `joint-query-controller` card. [TASK.json](TASK.json) records refinement
to a distinct verification obligation of its newer #4790 caller protocol.
The current selected-baseline orientation passed; it establishes only source
bindings and metadata consistency. No all-history or selected cold replay
was run. Stop at this audit; it does not justify a construction expansion.

The initial refreshed overlap corpus covered 313 open PRs, 4,017 Discussion
records and all 6,601 retained top-level notes (2026-10-23 03:09-03:11 UTC).
Focused searches found #4790 and #4865's separate parked-volume analysis;
no distinct ownership audit appeared within that coverage. Closed arbitrary
diffs and unpublished work remain outside it. Canonical coordination is the
[scoped claim in #4744](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19136902).

Credit JoyboyBrian's #4790 for installed inventory composition, its proof and
whole-root delta; Chris R / Clear1nsight's #4166/#4167/#4172/#4177 for the
actual caller, return transaction, tariff and complete-cost lineage; Tekalign
for the finite-role exchange idea; Jose Manuel for the physical tape,
controller, Ordinary and Compact machinery; and Sagar Thakrar, ywz65, Ali
Romman, Arham Tahir and all retained QQ16/native predecessors. Their source
archives and notices are unchanged.

Independent audit design, oracle, added fixtures and writing: Mihir Srivastava
with substantial OpenAI Codex assistance. Independence here means a separate
audit implementation and reasoning; source code and source-model assumptions
are deliberately shared. No independent human or formal-kernel review is
claimed. Apache-2.0.

## Open next questions

1. Can a separate portability repair make the original integrated replay run
   without altering frozen science? First isolate PR2753's path-format
   comparison in a successor launcher/checker and replay the original cases.
   The platform-dependent authentication boundary blocks this environment;
   the focused audit does not discharge actual caller/cleanup coverage.
2. Does D* beat B* with every unmatched physical and finite-control term
   priced? Use #4790's credited return delta exactly once in the complete
   matched nonchild/native/control ledger at an admitted geometry. Those
   remaining unpriced terms block an affordability or kappa conclusion.
