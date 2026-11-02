# Exact invocation prices for a distinguished dirty-echo factor

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. In the
ordered parent-reserved dirty-echo tree grammar of Koroffstrogov's
[PR758](https://github.com/CrocSwap/integer-mult-bounds/pull/758), the exact
minimum completed invocation multiplicity of factor i among n factors, with
at most s arbitrary dirty arrays, is

```text
2^d, where d is the first integer in 0..s satisfying
ceil(i / 2^(s-d)) + ceil((n-1-i) / 2^(s-d)) <= 2^d - 1.
```

The domain is `s>=0`, `1<=n<=2^s`, `0<=i<n`. A binary tree attains the minimum,
even though higher arities can improve the total cost. This is an exact new
individual-factor price law, not another replay of a predecessor total-cost
table. All inverses and dirty restoration calls remain in the multipliers.

For `n=2^s-1`, `s>=2`, even-position factors have minimum `2^(s-1)` and
odd-position factors have minimum `2^s`. For seven factors and three arrays,
the individual minima are `(4,8,4,8,4,8,4)`. A position-free capacity bound
misses this factor-of-two difference. Multiplying each individual minimum by
its fixed invocation price and adding gives a necessary weighted bill; these
individual optima need not share an attaining tree.

[PROOF.md](PROOF.md) proves the all-size theorem by binary replacement along
the distinguished path and separate dyadic prefix/suffix capacities.
`verify.py` supplies a bounded constructor and exact corroboration of the new
quantity. No predecessor executable, optimizer, count or scientific suite is
replayed. The source contract and capacity lemma are cited premises.

## Reproduce

From the worktree root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/distinguished-echo-factor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/distinguished-echo-factor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/distinguished-echo-factor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/distinguished-echo-factor --check-source-history --check-modes
```

Substitute another CPython 3.12 executable on other machines. The direct check
prints `PASS_DISTINGUISHED_ECHO_FACTOR` inside a generated JSON receipt with
computed coverage and SHA256 hashes of all six package files and the one
source proof. It writes nothing. No receipt is handwritten. Both registered
commands have a 120-second timeout. The universal theorem rests on the written
proof; finite execution is not formal proof-kernel acceptance.

The finite checks cover 2,794 all-arity marked optima through space six,
5,440 whole ordered trees through eight leaves with 93,266 factor comparisons,
and 43,946 emitted binary witnesses containing 6,435,096 leaf occurrences
through space eight. The separate parity specialization checks 2,035 positions
through space ten. Thirteen invalid inputs/trees are rejected and four semantic
controls pass. Explicit input/tree rejection and semantic controls distinguish
ceilings from floors, positional from total capacity, and the singleton and
saturated endpoints. All checks remain active with optimized Python.

## Scope, provenance and credit

The original `joint-query-controller` card is changed to a static composition
side theorem. It does not fulfill the complete native caller acceptance gate.
The baseline binding-only check passed; selected PR6030 remains unchanged.
[SOURCES.json](SOURCES.json) pins canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision eight, and the
unchanged source proof used as a live text input. The
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362439)
was posted before substantial work. Current main, open/merged/account PR
searches, active Discussions, handoffs and local reservations were checked.
Sparse notes, arbitrary historical diffs and unpublished work remain coverage
limits; these checks do not establish global novelty. The cached card scan
covered 394 open PRs and 6,334 Discussion records with complete remote paging,
but only 112 of 8,917 tracked notes were locally materialized at scan time.

Credit Koroffstrogov / PR758 for the ordered all-arity weighted grammar and
capacity lemma; androolloyd / PR673 for the multiway echo and restoration;
Dillon Amburgey / PR689, Sagar Thakrar / PR730, Ali Romman / PR744, Alexander
Schwartzman / PR784, Gareth Davidson / PR887 and Chafik Boukhalfa / PR628 for
the retained optimization, budget, formalization and rounded-leaf lineage.
Nick Petalas / PR4862 concerns total-unit-cost equality and is related context,
without being a theorem used or extended here. Dyadic trees and prefix coding
are classical. The new contribution is the exact individual multiplicity law,
its universal replacement/attainment proof and its standalone checker.

The result keeps static parent-reserved arrays, nonempty ordered factors,
fixed signed invocation prices and complete restoration words. It does not
cover connector reuse, clean checkpoints, interleaved lifetimes, alternative
echo identities, opened children, factor reordering or arbitrary reversible
programs. It does not assert identical rounded errors for different trees.
The predecessor's unfavorable full-transform adapter remains unfavorable;
this local theorem does not reopen that unchanged supplier.

No actual native caller, physical movement/storage bill, precision/stock proof,
compiler admission, analytic recovery or new kappa is supplied. The five
selected framework assumptions remain. Independent human and formal proof-kernel
review, predecessor or selected cold replay, Lean and Docker are unrun.

## Open next questions

When can several expensive factors attain their individual minima in one tree?
Start with two positions and their dyadic path capacities, retaining every
parent reservation. This theorem supplies no joint-attainment classification
or complete weighted optimum. The structured question and blocker are in
[TASK.json](TASK.json). A physical application also needs a distinct favorable
complete supplier contract before any expansion.

## Verifier bounds

The verifier uses bounded iterative traversals and no recursion, subprocesses,
network, dynamic code evaluation or file writes. Public constructor inputs are
capped at 1024 leaves and ten arrays. Witnesses have at most 2047 nodes. The
all-arity oracle stops at six arrays; whole-tree enumeration stops at eight
leaves. Every function is below sixty physical lines. Exceptions keep the
mathematical invariants active under optimization. Each receipt input is a
regular nonsymlink file of at most 256 KiB.

Power of Ten rules 3 and 9 have managed-runtime deviations: CPython allocates
integers, tuples, dictionaries and lists, and uses standard-library dispatch.
Fixed finite domains bound algorithmic live data; no allocation instrumenter
or separate static type analyzer is claimed. Warning-strict ordinary and
optimized execution, source inspection and the rejection controls provide the
available diagnostics. There is no production deployment or fixed-storage claim.
