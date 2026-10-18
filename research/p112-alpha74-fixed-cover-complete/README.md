# Complete alpha74 directions for one fixed cover

For the EXACT P112 seven-flat/four-flat cover from PR3307, every nonzero
direction qualifying after ONE common root cut of size at most two is one
of the predecessor's eight root-normal lines. A normal qualifies exactly
when its corresponding root belongs to the cut. Thus the qualifying span
has dimension at most two on this cover, now over ALL directions and every
characteristic-zero field.

PR3307 checked the common-cut rule only among eight exhibited normals. This
package closes its explicit fixed-cover completeness handoff. It checks all
43,435 binary seven-spaces and 320 exact rational candidate nullspaces with
two implementations. [PROOF.md](PROOF.md) gives the finite-union and modular
rejection argument; [RESULT.json](RESULT.json) lists the eight exact kernels.
The original universal arbitrary-cover common-two span-five question remains
UNSETTLED. No caller exclusion or new kappa is claimed.

## Reproduce

With an existing Python 3.12 installation, from the repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/p112-alpha74-fixed-cover-complete
```

All three direct scripts also run from a committed Git-free export:

```sh
python3.12 -Werror -B research/p112-alpha74-fixed-cover-complete/verify.py
python3.12 -Werror -B research/p112-alpha74-fixed-cover-complete/independent.py
python3.12 -O -Werror -B research/p112-alpha74-fixed-cover-complete/test_verify.py
```

Set TMPDIR to your own writable scratch directory for controls on a read-only
export. Controls make new writable byte copies, without chmod or changing the
retained files. The main checker uses incremental dependencies over F101;
the second uses transpose RREF over F103 and reversed root order. Both accept
only exact rational nullspaces. Their source authentication, geometry and
primitive-vector normalization helpers are shared. The second enumeration
and linear-algebra implementation are separate; no independent root-model
audit is claimed.

## Sources and limits

Scientific baseline is canonical main 463113d675af7410ac91d53a4fed51ec6494eb9a,
priority revision 6. SOURCES.json pins the canonical geometry input and
historical card/selected record. LIVE-SOURCES.json fixes its exact inventory
for direct replay. PREDECESSORS.json and PREDECESSOR-PINS.json bind the two
verbatim PR3307 payloads at d1058eaafdb380f9e4e93de25b9968ffecafe64e. No
pending Git object or third-party dependency is needed for direct replay.
The retained predecessor proof is attribution/context, not a proof premise.

Public overlap covers 358 open PRs at 21:33:34Z and 2,152 Discussion records
at 21:34:04Z, with complete pagination, plus an older 2,630 closed-PR snapshot
at20:44:55Z. Exact common-two/alpha74 searches and relevant canonical handoffs
were read. Arbitrary diffs and unpublished work are nonexhaustive. Worker 3
yielded this predicate and suggested the nullspace reformulation before
computation; worker 1's one-seven-flat/common-six and worker 5's 566 cut 33 have
different hypotheses and are unused. The original universal reservation was
narrowed explicitly before freeze. This is a side result under the decoder
card, not synthesis passing its 5% supplier-improvement gate.

No arbitrary-cover theorem, actual caller, full C5, global decoder floor,
physical/native/restoration/consumer invoice, supplier, all-size multiplication
theorem, selected-frontier change or kappa follows. Historical heavy censuses,
Lean, Docker, selected cold replay and human/proof-kernel review are unrun.
Internal read-only peer review is recorded separately when available.

## Code inspection

All new loops are bounded by the fixed 112 roots, nine-bit labels, 43,435 spaces,
at most 112 choose 2 cuts per space, 8 matrix dimensions, 35 private files and
100,000bytes per input. Functions remain below 60 physical lines. Structured
exits propagate failures; require checks remain active under optimization.
No recursion, generated code, callbacks or new installation is used.

Power of Ten rule 3 has a managed-runtime deviation. Python/Fraction allocate
dynamically, with live state bounded by the fixed Grassmannian list, at most
112root rows and their 8-dimensional coefficients. Rule8 has one source
execution deviation for the sole hash-authenticated canonical geometry.py;
compilation of its exact source avoids importing stale bytecode. The second
checker similarly compiles this package's own verify.py to share only the
authentication/model and canonical-vector helpers. Diagnostics cover all three
new scripts. Source-model mathematics and standard-library internals remain
explicit dependencies. Separate Before Serializing Shared State kept scratch
private and used only short Git/claim locks. Prove It Works required actual
committed read-only Git-free replay of every registered/direct script.

## Open next questions

Does the universal common-two span-five claim hold for arbitrary covers U7,V4?
It could address the motivating historical caller seam under separate caller
hypotheses. Start with a cover-orbit reduction preserving the fixed-cut
nullspace contract. That reduction, arbitrary-cover coverage and the actual
caller reconciliation are absent here. This session stops after the named
fixed-cover completeness result; no additional construction round is reserved.

Credit Nick Petalas/PR3307, PR3289, DreamingOfClouds/PR3154, the canonical
PR3161/3162 geometry and retained E8/P112 lineage including joaqcoo.
Apache-2.0. The predecessor's retained proof keeps its own source credit.
