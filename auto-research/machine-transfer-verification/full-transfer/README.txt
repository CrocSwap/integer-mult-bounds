Complete ambient finite schedule and physical-interface checkpoint
==================================================================

The full integer multiplication theorem remains unfinished. This checkpoint
establishes new exact interfaces needed for it, independently reproduces the
new strongest finite candidate in the 73-PR snapshot, and records the precise
remaining physical contracts. It has not been pushed to draft PR64.

Strongest reproduced finite candidate
-------------------------------------
PR71's anchored split-pair construction (Chafik Boukhalfa), with PR73's tighter
parameter backoff (Dominik Scholz), has conditional

    kappa = 25707323052097/500000000000000000
          = 5.1414646104194e-5.

Network pin: 1bef94fd40a746452548c84a4a8f8834670a3113.
Parameter pin: 253ecc88faeed55a950c76026d1fe67a7f690123.
The snapshot records 73 PRs and main56b66d58297deca1d7dd130247d720e960f77a37.
Both compiler outputs regenerate byte-identically; complete dirty-basis,
frame/scatter, fresh CRT, 47 exact assembly constraints, seven margins and
23 focused tests pass. The parameter certificate regenerates byte-identically
from its pinned parent. The broad unchanged repository suite was not rerun.
All inherited construction credits remain applicable.

New proof and correspondence packages
------------------------------------
outerrows/ (22 audited Lean declarations): A constructive rho=14D(e) supplies
enough rows for every positive width, with 2rho<e and strict padding factor<2.
It removes the unspecified small-width exception in the original row argument.
Every complete-range descendant satisfies V0<=Vj^2, giving the explicit bound
(log(2V0))^k<=2(2k)^k Vj for all fixed positive integer k. Implementation of
the gathering, row and descriptor operations remains an explicit contract.

localization/ (31): Finite rational tables lift exactly into Z[1/D]. Rational
matrix identities reflect into that ring and reduce to every eligible
prime-power address ring. Reciprocals protect nonzero pivot numerators;
stored inverses imply units. A single odd eligible prime exists for all f.
Modular partial-swap gauge identities are derived, not assumed. Complete
selected rational tables and the concrete denominator preparation remain.

framed/ (21): Actual tensor-matrix identities and a complete compact ambient
schedule check cover both directions, copied centers, both data fronts,
exterior transitions and final correction. Both PR64 and PR71/73 complete
charged profiles match their certificates. The physical reverse word is
replayed without transposing XOR direction. Seven malformed schedules are
rejected. Existing exact local/exterior/data pivot certificates are reused;
the full finite trace is checked externally, not generated as one Lean term.

latest-analytic/ (14): The actual real characteristic for the 26-row PR73
profile is proved below one at a=12854322426487/250000000000000000. It also
instantiates the uniform state-cost theorem under the named physical contracts.
The exact rational upper-bound gap is
699597017858129667/4221114531250000000000000000000000000.

There are 88 audited declarations across these packages, excluding rebuilt
dependencies. The 14 PR73 declarations include one repeated generic identity;
the tensor package includes two helper lemmas. Counts do not mean 88 new
independent mathematical ideas. All audits use only standard Lean axioms.
Independent reviews and source-bound receipts accompany each major package.

A useful negative result
-------------------------
The PR73 profile does not dominate PR68 at every power. After normalizing each
by its own W, exact integer-square-root enclosures prove it is strictly worse
at power1/2. The newer small-saving certificate remains valid. See
audit/normalized-dominance-control.json and its standalone checker. Neither
fewer roles nor lower total rank alone proves a better characteristic at an
arbitrary exponent.

Remaining decisive work
-----------------------
1. Construct actual fixed-head digit demultiplex/merge and whole-row split/merge
   routines with arbitrary spectators, clean reusable tapes, returned heads,
   amortized counters and a uniform linear-volume bound.
2. Bind every ordered residual factorization to the finite child call plan,
   and generate a typed trace with the complete modular table preparation.
3. Compose the routines and child calls into one fixed-tape recursive scheduler,
   proving the named state-cost contracts rather than assuming them.
4. Integrate the analytic Gaussian/precision/exact-recovery interfaces and
   setup/prime-packing costs into the final deterministic multiplier.

The audit identifies PR69's balanced coarse sums as a possible combination
with PR71's graph. Compatibility is only a source-level hypothesis here; no
new combined construction or numerical improvement is claimed.

Reproduce and provenance
-------------------------
Package READMEs give commands. Lean uses existing cached4.21.0 with Mathlib
308445d7985027f538e281e18df29ca16ede2ba3; no installer is run. The archive
preserves paths relative to outputs/ and includes required prior local proof
dependencies, selected words, independent arithmetic helpers and profiler
inputs. Replaying external repository targets or source-bound ambient checks
also requires the specified immutable upstream Git checkouts. No checkout
is fetched or changed by the standalone proof/checker commands.

checkpoint.json records scope and counts. file-manifest.json binds archived
files except itself. The adjacent full-transfer-bundle.json records archive
hash and integrity verification. Earlier bundles remain historical snapshots;
research-addendum.tex and research-ledger.json contain the current account.
