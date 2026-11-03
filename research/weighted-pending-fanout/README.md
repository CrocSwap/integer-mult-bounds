# Exact dirty-fanout tariff under weighted pending capacity

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof and constructive scheduler with exact finite
corroboration. If unfinished output i reserves positive integer weight w_i
under capacity C, let b be the minimum bin count for those weights. In the
signed common-source query alphabet with permanent commits, the exact bill is

```text
N_Ai = 2 for every output,
N_B  = 2 ceil(b/2),
Q_min = 2 sum_i c_Ai + 2 ceil(b/2) c_B.
```

The new step replaces Sagar Thakrar's [PR1168](https://github.com/CrocSwap/integer-mult-bounds/pull/1168)
cardinality cap by unequal lifetime reservations. The proof covers arbitrary
longer words and gives an attaining schedule. The unweighted formula is a
cited predecessor result. No predecessor executable is imported or replayed.

For weights `(3,3,3,3,3,1)` and capacity 5, the five large outputs require
different bins. Exactly six shared-source calls and twelve readouts are
necessary and sufficient. Pricing capacity by total weight alone permits
four shared-source calls. At declared complete prices `c_B=52,c_Ai=1`, that
relaxation gives 220 while the exact optimum is 324. These are abstract query
prices, not physical primitive counts or a runtime benchmark.

## Contract and construction

Arrays x,z,y_i are initially arbitrary. The only queries are
`z += s Bx` and `y_i += s A_i z`, where s is +1 or -1. Every query preserves
its source, spectators and private work and returns its heads. The fixed
word must work universally for characteristic-zero linear maps A_i,B and
all initial arrays, with endpoint `y_i += A_i Bx`, x,z unchanged. Commutation
and invertibility of the maps are not required. Special relations or zero
maps can change the optimum for a particular instance.

An output is unfinished from its first readout until a correct permanent
commit. No later query touches it. The sum of unfinished weights may never
exceed C. Storage of unstarted and committed outputs is retained, not freed
as scratch. Weights declare a scheduling resource; the theorem does not
identify them with physical memory or unequal payload widths.

Partition outputs into optimal feasible bins. For consecutive bins alternate
s=+1,-1 and emit

```text
for i in bin: readout_i(-s)
shared_source(s)
for i in bin: readout_i(s); commit i
```

If the bin count is odd, append one inverse shared-source query. Each bin
finishes before the next opens. [PROOF.md](PROOF.md) proves that every output
must be active at some shared-source query; assigning it to such an event
gives a feasible bin packing. Restoration forces an even query count.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/weighted-pending-fanout/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/weighted-pending-fanout/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/weighted-pending-fanout
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/weighted-pending-fanout --check-source-history
```

Another CPython 3.12 path can replace the local interpreter. Direct replay
prints `PASS_WEIGHTED_PENDING_FANOUT` in a generated JSON receipt binding all
six package files by SHA256. It writes nothing and needs neither Git nor a
predecessor package. The source manifest pins the retained README and notice
as historical provenance, not live executable inputs. No receipt is handwritten.

The fixed finite domain contains all weight multisets of length zero through
six with weights in 1..C, at C=1..6. Its 1,715 contracts compare subset dynamic
programming with independent enumeration of feasible bin-load states. Every
emitted schedule is executed on all basis columns of every arbitrary initial
array by literal two-by-two integer maps. A checked pair is noncommuting.
The executor checks all commits and capacity boundaries, source and connector
restoration, and every target. It executes 24,126 complete queries in this
domain; 144 contracts strictly exceed the total-weight bound rounded up to
an even integer.

Four separate breadth-first searches over signed query words have minima
10,8,8,8 for weights `(2,2,2)`, `(1,2,2)`, `(1,1,2)`, `(1,2,3)`, all at
capacity 3. The searches visit 11,416, 36,719, 54,041 and 20,093 distinct
states, respectively, including all layers through the shortest endpoint.
They use neither the packing optimizer nor its proposed price to prune
words. The proof justifies sign symmetry and immediate correct commits.
Eighteen rejecting controls cover invalid resource domains, incomplete or
overweight bins, a missing restore, premature/late output access, a changed
source-query sign and an invalid instruction. A ten-output maximum-capacity
fixture exercises the implementation's boundary. The universal theorem
rests on the written argument, not these finite checks.

## Limits and implementation constraints

This reference accepts at most ten outputs and integer capacity at most
65,536. The optimal packing computation is exponential in output count,
using O(3^k) arithmetic checks and O(2^k) table entries. An implementation
must pay packing preparation or supply a separately justified packing.
Admission, reusable coefficient preparation, schedule/control storage and
access add to the complete query bill; they are not set to zero here.

There is no recursion, subprocess, network, dynamic evaluation or verifier
write path. Functions fit within 60 physical lines. Packing has at most
1,024 table entries; independent load enumeration has at most 203 states;
word search has depth at most ten and at most 100,000 distinct stored states.
The literal executor has at most 24 basis columns and 44 instructions.
Six file reads are capped at 256 KiB each. Explicit exception checks remain
active under `-O`. Normal and optimized warning-strict commands are registered.

Power of Ten rule 3 has a managed-runtime deviation: Python integers, tuples,
sets and matrices allocate dynamically. The enforced dimensions and search
bounds limit live data; runtime allocator overhead is not instrumented.
Rule 9 has a bounded control-callback deviation: eighteen immediately executed
rejection callbacks call only packing, emit or literal. They retain no state.
AST compilation and warning-strict execution supply local diagnostics. No
separate lint/type analyzer or fixed-allocation native runtime is claimed.

No selected producer/consumer or physical reservation assignment is supplied.
Nonlinear maps, finite-characteristic torsion, free output mixing, changing
sources, state-dependent tariffs, output-storage reuse and adaptive data-based
words are outside the theorem. Native frames, precision/tapes, owned erasure,
stock, compiler closure and outer transfer remain separate obligations. All
five selected assumptions remain. No kappa, selected-frontier update, complete
multiplication theorem, independent human review or proof-kernel acceptance
is claimed. Selected cold replay, native suites, Lean and Docker are unrun.

## Credit and scope

Sagar Thakrar / PR1168 at `b53b07b5aed4e00358a0d0061ad99dbf5190ca2b` supplies
the unfinished-output and permanent-commit interface and its unweighted
all-word lower bound. Ross Richardson / PR938 supplies the coefficient state
and equality-word context. CubeJerry / PR889 supplies shared dirty-source
fanout and complete accounting; Chafik Boukhalfa / PR628 supplies the retained
commutator lineage. The selected native/compiler contributors retain their
existing attribution. Classical bin packing, dynamic programming, summation
by parts and linearity are background; global literature priority is unclaimed.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
[TASK.json](TASK.json) explicitly changes the uniform-transfer-audit card to
this recursive-interface side theorem. It does not discharge a selected
assumption. Selected-baseline orientation passed and is source binding only.
Discovery stopped at this first verified result.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375366)
followed live handoffs, active Discussions, open/account PRs, local reservations
and main/merged searches for weighted pending capacity, bin packing and general
fanout formulas. Sparse cached notes and unpublished work remain coverage
limits. No absence of overlap is claimed as a novelty certificate.

## Open next questions

- Bind one actual common-source caller to proved reservation weights and a
  favorable full invoice. Start with its exact lifetimes and include query
  implementation, packing, control, restoration and movement. No such caller
  or physical reservation assignment is supplied.
- Find a useful caller weight family with an exact cheaper packing algorithm.
  Start with a source-bound restriction on its weights; the present general
  reference is exponential and schedule preparation must be paid.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
