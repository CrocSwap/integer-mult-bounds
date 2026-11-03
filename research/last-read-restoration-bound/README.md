# Sharp error boundary for deferred delivery through restored workspace

This contribution was produced by Nick Petalas. Apache-2.0.

A helper cannot retain an earlier input after its last read, deliver a
nonzero target later, and restore all workspace under the following contract:
the output at the cut contains no earlier-input dependence, the continuation
reads no earlier input, and its workspace map is injective and independent
of output contents. This includes arbitrary nonlinear workspace computation
and independent randomness, with every persistent control/log included.

For a uniform source in F_q^d and a rank-r deferred target, the sharp law is

```text
Pr[correct output AND exact workspace restoration] <= q^(-r)
output error probability + restoration failure probability >= 1-q^(-r)
```

Every point on the lower boundary is attainable by mixing two explicit
logical programs. One delivers the target exactly and leaves a rank-r
workspace defect; the other restores exactly and guesses the zero target.
Over any field, a linear implementation has
`rank(deferred target) <= rank(final workspace dependence on earlier input)`.
For a general finite source distribution and arbitrary target F, replace
q^(-r) by the largest probability of a fibre of F.

Claim type: scoped written mathematical proof with finite corroboration.
[PROOF.md](PROOF.md) gives the contract, argument, attaining programs and
explicit escapes. Elementary counting, injectivity and rank facts are
classical. The contribution is their sharp application to this declared
causal/restoration interface, with its exact error frontier and controls.
No literature-priority claim is made for the underlying facts.

## Evidence and reproduction

From the repository root, using the recorded interpreter or another CPython
3.12 installation with the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/last-read-restoration-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/last-read-restoration-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/last-read-restoration-bound
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/last-read-restoration-bound --check-source-history
```

The direct marker is `PASS_LAST_READ_RESTORATION_BOUND`. The verifier writes
nothing and emits a generated JSON receipt bound to all six package files.
It exhausts prefix functions, suffix permutations, output functions and
initial states on the declared domains. It separately executes the attaining
programs, independent four-outcome coin mixtures, and changed-premise escapes
on finite-field inputs with arbitrary dirt and output values. Rationally
stated probabilities are checked by integer counts. Matrix elimination checks
the rank inequality on every 2x2 cut/readout matrix and invertible suffix over
F2 and F3. Explicit requirements stay active under optimization.

The universal result rests on the written proof. The finite checks certify
their enumerated domains. Hosted execution and independent mathematical
acceptance are separate.

Local warning-strict normal and optimized direct checks passed. The three
abstract scans enumerate 6,649,846 protocol/initial-state cases and 26,245,090
input executions: all target functions on 4/2/2 and 3/3/3 source/work/output
alphabets, and the identity target on 4/4/4. Six finite-field gate fixtures
enumerate 81,162 input/dirt/output triples and five four-outcome coin mixtures
each. All 316,464 linear matrix triples pass, with a separate image-cardinality
rank oracle. Ten invalid domains reject. Four changed-premise escapes and
the complete hidden-log debt are checked. Each registered command was
timed locally below six seconds against its 120-second limit; no runtime
improvement is claimed.

## Scope and connection to the bottleneck

This is an original changed-scope result under `coverage-law-change` at main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected PR6030.
The selected metadata orientation passed. The selected supplier's complete
signed bill remains the binding question; this package changes neither that
bill nor any selected record.

A proposed one-pass helper cannot omit its inverse input operation while
silently assuming deferred delivery and full restoration under this contract.
Source rereads, readable outputs, early accumulation, noninjective workspace
steps or a retained transcript change the conclusion. The verifier exhibits
these escapes. In particular, whole-program reversibility does not imply an
injective workspace-only suffix when outputs feed back into workspace.

No existing selected schedule is asserted to satisfy the excluded contract.
There is no physical/native implementation, complete paid/target invoice,
compiler closure, ownership, precision, stock, tape, outer recovery or new
kappa result. All five selected framework assumptions remain. Selected cold
replay, Lean and Docker were unrun. Independent human and formal proof-kernel
review are unclaimed. Family decision: finish this scoped obstruction; a
physical expansion needs a named feedback/reread contract and complete bill.

## Related work and credit

The current construction and its historical contributors retain their credit
through the selected record. No predecessor executable, fixture, count or
proof is replayed as the result. PR1203's dirty-state wrapper uses both a
source call and its inverse; that explicit reread is outside the excluded
contract. PR6015 concerns exact finite-menu endpoint choices, and PR6134
concerns random observation cost/error tradeoffs. Neither is being audited
or extended as the question's source. The local source pins are historical
orientation provenance only. No mathematical input is imported.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363385)
records this original target. Main README/general-form searches, merged
searches, live open PRs and the last hour of handoff posts were checked.
Sparse local notes, arbitrary historical diffs and unpublished work remain
coverage limits; an absence of matches is not a novelty proof.

## Open next questions

Can one actual helper/caller use output feedback to avoid the second source
call at a favorable complete cost? Start with one concrete late target and
implement its two swaps or another feedback map with all arbitrary inputs,
legal frames, owned lifetimes and the complete signed invoice. The missing
physical interface and favorable bill block a supplier claim. The structured
question is in TASK.json. This package stops at its first proved result.

## Verifier constraints

The standalone verifier has fixed domains: source/work/output cardinalities
at most four for the abstract scan; q in {2,3,5}, ranks one/two for the literal
gates; 2x2 matrices over F2/F3 for the linear scan. Loops have explicit bounds,
there is no recursion, subprocess, source import, dynamic code or file write,
and all functions are below sixty lines. Reads are confined to the six local
files, each capped at one MiB, for the output receipt. Failures propagate
without a success marker.

Power of Ten rule 3 deviation: CPython allocates tuples, integers and Counter
entries during replay. Fixed fixture domains bound live collections; the
largest materialized function table has 256 entries and protocols are scored
one at a time. No fixed-allocation runtime is claimed. Revisit storage before
accepting arbitrary sizes or production use. Warning-strict normal/optimized
replay and in-memory syntax compilation provide the available diagnostics;
no separate static analyzer or production backend is claimed.
