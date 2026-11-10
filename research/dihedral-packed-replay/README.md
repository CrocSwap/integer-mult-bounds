# Packed transitions for the complete D8 replay

The complete pinned PR1443 replay takes 27.09% less median wall time locally,
30.78 ms versus 22.44 ms, over fifteen alternating fresh-process pairs. Every
pair improves, every process succeeds, and scientific stdout is byte-identical.
This is a small absolute saving, about 8.34 ms per invocation on this host.

Claim type: scoped implementation-equivalence proof, exact finite conformance,
and local performance evidence. The eight-call mathematical minimum remains
woklerx's PR1443 result. This contribution was produced by Nick Petalas.
No new mathematical minimum, supplier admission or kappa is claimed.

## The one change

[run.py](run.py) authenticates the four live inputs in [SOURCES.json](SOURCES.json),
loads the fixed original program with its main block disabled, and replaces
only its `step` function. The original `ball`, `run`, source checks, finite group
law, both complete radius-four searches, state hashes, witness selection,
independent matrix-set products, direct word, eight omission controls and
certificate comparison all remain active. The adapter accepts no arguments
and cannot enter the original `--write` branch.

The original transition allocates four coefficient cells and loops over the two
columns and rows. The replacement gathers two coefficient bytes into a 16-bit
row, applies two 256-entry delta tables, and scatters the result with one
integer multiplication. It retains 512 delta entries and four scatter constants.
It caches no search states or scientific result across invocations.

## Equivalence for every packed state

Write the coefficient matrix as `[[a,c],[b,d]]`, with byte entries. A legal
source generator is `(g,x,y)`, where `x,y` are nonzero two-bit vectors.
Let `L_g` be the original permutation of the eight group coefficients.
On the first column, the original code computes

```text
v = y_0 a XOR y_1 b
h = v XOR L_g(v)
a' = a XOR x_0 h
b' = b XOR x_1 h
```

The second column follows the identical rule on `c,d`. The packed code gathers
`R = (y_0 (a | c<<8)) XOR (y_1 (b | d<<8))`. Its low and high bytes are exactly
the two original `v` values. The precomputed table is `D_g(v)=v XOR L_g(v)`.
Consequently `H=D_g(R_low) | D_g(R_high)<<8` contains precisely both deltas.
Multiplying `H` by `x_0 + 2^16 x_1` puts those deltas in exactly the selected
rows. Since `0<=H<2^16`, its two copies have disjoint bits and introduce no
arithmetic carry. XOR with the original state gives the same four output bytes.

Thus the replacement agrees for all `2^32` packed states and all twelve legal
generators. This written argument supplies the universal state quantifier;
the program does not enumerate four billion states. Deterministic transitions
with unchanged search order give identical first-witness maps by induction on
search depth. Neither argument changes or re-establishes the predecessor's
mathematical minimum.

## Exact checks

[verify.py](verify.py) checks all 65,536 byte pairs in each column for every
legal generator, totaling 1,572,864 comparisons. It compares every state and
first witness in both complete balls. Their union has 5,650 states, and all
67,800 outgoing transitions agree. It also runs both complete scientific
calculations and requires equality of the full certificate payload.

Eleven controls cover missing/short/out-of-range tables, an incorrect coefficient
permutation, scatter, label and dropped row, and independent corruption of each
of the four live source inputs. Source mutations occur through read interception;
no source file is edited. The same checks run with assertions disabled. The
verifier prints a generated receipt containing counts and every package file's
SHA256. It neither writes nor regenerates a stored scientific receipt.

## Timing evidence and limits

[BENCHMARK.json](BENCHMARK.json) contains all thirty full-process measurements,
flags, environment, source hashes, stdout hash and statistics. CPython 3.12.15
on macOS arm64 was used. The original command's range was 29.79 to 32.13 ms;
the adapter's range was 21.61 to 23.19 ms. The ranges do not overlap. Each pair
alternates its first side. Both sides use `-I -O -W error -B` and the exact same
complete fixture. Startup, table construction, pin reads, original scientific
checks and certificate comparison are inside the timed region. There were zero
failed processes and every stdout matched the exact expected success output.

[PROFILE.json](PROFILE.json) records separate instrumented executions, excluded
from the timing sample. The original transition has 13,568 calls and dominates
the search cost. The adapter removes the repeated cell allocation and Python
row/column loops. Process startup, imports, unchanged search bookkeeping and
independent witness checks limit the complete-command gain. The median wall
saving is smaller than the original transition's profiled cumulative time.

The host was shared, with eighteen logical CPUs and load averages 3.82, 3.33,
2.83 at intake. Alternation limits drift; it does not isolate every scheduling
or filesystem-cache effect. Fresh processes do not imply a cold filesystem.
The claim is local to this short command and host. Hosted CI checks exact
conformance and execution, not the timing percentage or acceptance of the proof.
No selected scientific cold replay, native implementation, physical caller,
compiler closure, tape/precision proof, Lean or Docker job is provided or run.
The five selected framework assumptions remain.

## Reproduce

From the repository root, the exact local interpreter is
`/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12`.
Another CPython 3.12 installation can run the same standard-library commands.

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/dihedral-packed-replay/run.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dihedral-packed-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/dihedral-packed-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dihedral-packed-replay
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dihedral-packed-replay --check-source-history
```

The adapter prints the unchanged `PASS_DIHEDRAL_COMMUTATOR` line. Conformance
prints `PASS_DIHEDRAL_PACKED_REPLAY`. The registered hook and publication checks
print `PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.

For new local timings, use `benchmark.py --pairs 15 --out /path/to/new/benchmark.json`
with the same interpreter. The output path must not exist. The driver uses
bounded thirty-second children, counts errors by failing on any unsuccessful
or differing output, and times fresh complete invocations. Timings are optional
and are excluded from CI acceptance. To inspect the limiter, profile each
complete command separately with Python's `-m cProfile -o /path/to/new/profile`.

## Implementation bounds

The adapter runs the unchanged depth-four search and builds only two 256-entry
delta tables. The conformance domain and all controls have explicit finite
bounds. The optional benchmark accepts five through fifty pairs and runs its
children sequentially. All new functions fit within sixty physical lines.

Python's managed allocation is a declared deviation from allocation-free steady
operation. Live search memory is bounded by the fixed two-register depth-four
fixture. Integer widths stay within the source's 32-bit state and intermediate
scatter bounds. Dynamic source execution is limited to the fixed, authenticated
predecessor script with its main block disabled; dynamic importing is limited
to the local adapter. Read interception has four explicit mutation targets.
These mechanisms preserve source checks and do not execute supplied text.

## Open next questions

Can a table of complete column transitions repay initialization and memory costs
on a genuinely larger complete replay? First pin that larger fixture and compare
full-process time, including construction and exact conformance. The present
512-entry method and short fixture do not establish such a gain. No larger
implementation or follow-on optimization is reserved here.

## Credit and overlap

Credit woklerx / [PR1443](https://github.com/CrocSwap/integer-mult-bounds/pull/1443)
for the source replay, complete balls, exact certificate, independent matrix-set
checks and mathematical result. Retain its scalar-idempotent normalization
lineage through Ali Romman, eumemic / PR288 and Gareth Davidson / PR1333.
Original source notices remain unchanged. The new adapter, equivalence argument,
conformance checks and timing driver were produced by Nick Petalas. Apache-2.0.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363476)
pins canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8
and selected PR6030. The card is refined to this source-bound runtime step.
Open/account PRs, recent handoffs, local reservations, distinctive main-tree
terms and merged D8/UT3 runtime searches found no matching transition adapter
in their coverage. Sparse notes, unpublished work and arbitrary historical diffs
remain outside that coverage. The source's larger-register question has known
successors; this package does not target or re-audit that question.
