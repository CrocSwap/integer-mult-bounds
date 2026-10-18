# Sharp outside-span E8 A2 joint capacity 30

The outside-span bound30 from PR3288 is attainable. For every full E8
27-root A2 fiber A, exactly 1080 binary six-spaces outside span(A) attain
|R intersect V|+|A intersect V|=30. The analytic classification gives 216
eligible intersections, each with five outside extensions. A literal
20-root closure, ten in A, avoids the actual P112 frame. For the canonical
fiber the exact census finds 144 such P112 equality spaces.

This settles the explicit outside sharpness gap. PR3262's original joint 32
bound and PR3288's analytic joint 32/contained equality 27 remain predecessor
results. No new shortening threshold, literal caller, decoder floor,
scalar factor realization, native/physical program, restoration, consumer,
supplier or kappa is claimed. See [PROOF.md](PROOF.md) for the equality
conditions, analytic count and inherited premises.

## Reproduce

Python 3.12+ and standard library, from the repository root:

```sh
python3 -W error -B scripts/research_package.py --package research/e8-a2-outside-rank6
```

The registered replay runs all three direct scripts below. In an official
committed export these run without Git or network. Set TMPDIR to your own
writable disposable directory for the private mutation controls.

```sh
python3 -W error -B research/e8-a2-outside-rank6/verify.py
python3 -W error -B research/e8-a2-outside-rank6/independent.py
python3 -W error -O -B research/e8-a2-outside-rank6/test_verify.py
```

The primary checker enumerates 2667 dual-RREF kernels in the canonical
seven-space and twelve outside extensions each. The separate checker
uses canonical nonzero dual triples, dense elimination and bitmasks. Both
compare all 32004 relevant six-spaces and their complete joint histograms.
They share the authenticated root model; this is independent combinatorial
verification, not an independent reconstruction of all geometry.
The seven control groups test the live witness, the contained 32 and rank 7
countercontrols, malformed binary data, schema/type/usage/inventory changes,
private source mutations and linked inputs. They use writable byte copies
inside TMPDIR and never change source/export permissions.

SOURCES.json binds the live geometry by base/blob/SHA256 and retains exact
PR3288 proof/fixture payloads with original paths, source commit and hashes.
The direct verifier fixes the canonical inventory including JSON types and
usage controls. Pending-PR Git objects are not needed by fresh CI or direct
replay. The generic metadata hook resolves only canonical base provenance.
The universal 3360-fiber configuration binding and global 12/20 capacities
are inherited from the pinned proof. Their old censuses, selected cold
replay, Lean and Docker are unrun. Internal automated checking is separate
from human or proof-kernel review and selected-frontier admission.

## Implementation bounds

All loops have fixed binary-domain bounds. A span holds at most 512 integers,
the root model has 120 labels, and the 32004-space census streams one 64-point
space at a time. Python and its libraries allocate dynamically, a deviation
from Power of Ten rule 3. These fixed input and live-set bounds control this
small finite checker; no persistent worker or unbounded queue exists.
Functions remain below 60 physical lines. Explicit exceptions preserve checks
under optimized execution. Warning-as-error replay and source compilation
are the available interpreted diagnostics; no linter installation is made.
These bounds do not certify the Python allocator or library internals.

Rule: 3, fixed memory capacity.
Location: verify.py, independent.py and test_verify.py.
Reason: Python and standard-library operations allocate dynamically.
Scope: This bounded, terminating finite checker only.
Compensating control: Nine-bit domains and streamed candidate spaces bound live data.
Verification: Registered/direct replays and fixed dimension/count assertions.
Follow-up: Use fixed arrays if a future native checker needs allocation guarantees.

## Open next questions

A stronger outside-space argument must use more than the separate 20 and 10
capacities, since they are jointly attained. Does a named actual caller
force incompatible equality supports? First reconcile a literal caller
with current public work, then state its simultaneous compatibility
conditions. No caller or complete-cost contract is supplied here. This
package does not open another construction or search round.

## Credit and scope

Nick Petalas/PR3288/3280/3269/3262, David Arias's quadratic model,
DreamingOfClouds/PR3154 and the retained E8/P112 lineage including joaqcoo
supply the predecessor context. Exact PR3288 source is retained unchanged.
New material is Apache-2.0. Substantial automated assistance in analysis and
local verification is recorded in TASK.json. No independent human review
or formal verification of the multiplication theorem is claimed.

Canonical base 463113d675af7410ac91d53a4fed51ec6494eb9a, priority revision 6.
The original rank-shape card is explicitly changed to this geometric side
result. Public corpus coverage is 342 open PRs through 21:05:35Z and 2137
Discussion/comment/reply records through 21:06:07Z with complete pagination;
2630 closed/merged bodies have the older 20:44:55Z cutoff. Exact 3288/3280
heads and current 3156 handoffs were checked separately. Arbitrary diffs and
unpublished work are not exhausted. The simultaneous rank 7capacity,
5/6/6 common-cut and QQ16 depth packages have distinct predicates and are unused.
