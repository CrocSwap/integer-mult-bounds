# Linear BIT supports cannot close with arbitrarily many owners

This contribution was produced by Nick Petalas. Claim type: scoped written
algebraic proof with exact finite corroboration. No new kappa is claimed.

In PR5456's independent-stage BIT model, allowing a field to belong to
three or more calls does not rescue a controller whose coordinate supports
meet pairwise in at most one field. The final native main chain still
cannot close its diagonal endpoint. The result holds for every finite
number of calls and field-ownership multiplicity, including four-field
call supports and helper writes outside their own supports.

The new terminal-block theorem is more precise. Group the final support
by each coordinate's latest earlier owner, making private coordinates
separate singletons. Every completed word has a block-diagonal final
response in that partition. Every such matrix is attainable in the
linear endpoint relaxation, which does not require earlier native chains.
Thus a final native chain requires a repeated pair with the same latest
earlier owner. Extra ownership of separate coordinates is insufficient.

[PROOF.md](PROOF.md) states the model and proves necessity, relaxation
attainment and the ownership-cap removal. A full three-call, three-owner
binary word outside the linear-intersection hypothesis closes exactly
and has all three native chains. It is a boundary control, with no
physical implementation or favorable invoice claimed.

## Reproduction and evidence

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/bit-linear-support-ownership/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/bit-linear-support-ownership/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bit-linear-support-ownership
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bit-linear-support-ownership --check-source-history
```

Run the last command after committing. Substitute a local CPython 3.12
path on another machine. The direct command emits
`PASS_BIT_LINEAR_SUPPORT_OWNERSHIP` inside a generated JSON receipt, with
enumerated counts and SHA256 hashes of all six package files. It writes
nothing. No receipt is handwritten or retained as a frozen result.

The finite corroboration uses only support histories with at least one
field owned by at least three calls. It checks all 18,795 ordered histories
of nonempty supports on three coordinates at lengths three through five,
after that filter. Their 33,048 terminal off-diagonal slots include exactly
11,106 that are feasible in the stated linear relaxation. An
independent literal matrix-product interpreter checks every elementary
response at length three, totaling 2,943 impulses and including rows outside
a call's support. It also constructs all 781 allowable terminal matrices
at length three, with a specified diagonal, and checks their complete
formal endpoints.

The four-support Fano fixture has seven triple-owned fields and seven
private fields. Every one of its 5,040 call orders has a diagonal final
restriction. Eight boundary control groups include the full three-owner
positive word, an omitted response, unequal latest owners, private
coordinates, differing complete histories with equal latest owner,
forbidden completion, invalid source columns and permitted outside rows.
The universal theorem rests on the written argument, rather than a
finite search or the Fano fixture.

## Scope, provenance and overlap

Ali Romman / [PR5456](https://github.com/CrocSwap/integer-mult-bounds/pull/5456)
at `0d64d4d5d73f370182ada9825a611c86cfbf0049` supplies the model, coefficient
equation and two-owner last-call theorem. Its explicit more-than-two-owner
opening is the source question. The new result removes that ownership
cap. Credit Dillon Amburgey / dillona's
[PR5388](https://github.com/CrocSwap/integer-mult-bounds/pull/5388) early-helper
interface and the retained BIT, native, ownership, geometry, COPY and
compiler lineage. Those results are cited premises. No predecessor
scientific executable, certificate census or solver receipt is replayed.

Brian / [PR5507](https://github.com/CrocSwap/integer-mult-bounds/pull/5507)
at `1691a6024b60bdf28d7a2eed13cb32d78e2ea5b4` permits parallel support
intersections with at most two owners, proving a complete funding
obstruction there. Our arbitrary-owner linear-support theorem changes
the other hypothesis. Neither result covers arbitrary intersections with
arbitrary ownership. PR5527 has one shared D symbol and different rank
hypotheses; our proof requires independent D symbols.

The base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The selected binding-only positive control passed. The
bit-helper-contract card changes to this algebraic interface obstruction;
its source-bound G20 construction and physical acceptance gate are not
claimed. [TASK.json](TASK.json) records the change and stopping rule.
[SOURCES.json](SOURCES.json) pins only historical provenance. The verifier
has no external scientific input or runtime import.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372282)
was posted before developing the proof and checker. Live open and account
PR lists, recent handoffs, active Discussions, local reservations, main
README searches and merged-PR searches covered the object and its general
unbounded-owner form. The card overlap helper supplements those searches.
Its snapshot contains 540 open PRs, 6,569 Discussion records and all 8,917
HEAD research-note paths. Arbitrary package files, historical diffs and
unpublished work remain coverage limits. Search absence is not proof of novelty.

The theorem does not allow dependent stage symbols, non-coordinate
supports, additional thin calls or arbitrary free interleaved address
maps. It does not rule out many-owner callers with repeated support pairs.
No complete invoice, native supplier, uniform compiler, physical routing,
stock, precision/tape, analytic recovery or all-size multiplication
theorem is supplied. All five selected framework assumptions remain.
The selected frontier and predecessor packages are unchanged.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Can a source-compatible many-owner caller with a repeated terminal pair
improve the complete signed bill? First write one completed native word
whose final chain is contained in a nontrivial latest-owner block. Then
charge all distinct productive helpers, paid calls, restoration and
consumer costs. The terminal-block condition is only a necessary test;
no funded candidate is supplied. This is also recorded in TASK.json.

## Verification design

Build the Lever led to one standalone exact checker. Prove It Works led
to literal formal products and a full positive native-chain control.
The checker has no recursion, subprocesses, network, code generation or
mutable external state. It reads six fixed local files for its receipt
and writes nothing. All enumeration domains are fixed: at most five
stages in the three-coordinate census and seven stages in the Fano
fixture. Formal matrices are bounded by the declared coordinate and
stage capacities. Explicit checks survive optimized Python. Functions
fit within 60 physical lines.

Power of Ten deviation: CPython allocates tuples, sets and integers
dynamically. The fixed fixture bounds constrain their live sizes;
this is not a fixed-allocation service. Warning-strict ordinary and
optimized execution are the available interpreter diagnostics. No
shared configuration or predecessor implementation is changed.
