# P112 rank-five shortening through common support 46

Three arbitrary residual pieces of binary support rank at most five, outside
ONE common cut of at most 46 P112 coordinates, span at most one restricted
root-code dimension over every characteristic-zero field. This increases
PR3257's sufficient threshold from 45 to 46. Sharpness is unproved.

[PROOF.md](PROOF.md) closes the previously missing D6 normal-plane branch.
Its equality budget forces three disjoint twelve-root singleton pieces into
two axis fibers. The eight removed frame roots puncture each axis in four
orthogonal roots. Exact finite enumeration proves that the surviving maximum
supports always intersect. Full unpunctured fibers have disjoint maxima, so
the puncture is essential.

The replay checks 194,310 axis five-spaces, 5,334 smaller-fiber five-spaces,
240 orthogonal four-root punctures, all 3,780 orthogonal root planes and
960 reflection/label identities. A separate five-label-basis implementation
recovers the same 240 maximum supports from 474,672 subsets. Seven behavioral
controls include malformed labels/punctures and the support47 boundary.

## Reproduction

From the repository root, with a session-owned external TMPDIR:

```sh
python3.12 -W error -B scripts/research_package.py --package research/p112-rank5-support46
```

For a source-authenticated Git-free export, run the two scripts directly:

```sh
python3 -I -W error -B research/p112-rank5-support46/verify.py
python3 -I -O -W error -B research/p112-rank5-support46/crosscheck.py
```

Both scripts read sources and compare committed evidence. They write nothing
unless the primary verifier receives an explicit external --output path.
SOURCES.json retains the exact pending PR3249 and PR3257 proof/receipt bytes,
with their source commits and Git blob/SHA256 digests. Fresh CI does not need
those pending Git objects. Geometry is the one declared main-branch input.
The generic wrapper needs Git provenance; the direct scripts do not.

## Scope and dependencies

The global five-flat capacity12, A2 union78 and A2 joint incidence bound21
remain inherited pending dependencies. Their older censuses are not rerun.
The Weyl-chamber theorem remains written mathematics. No actual TWOSIDE
caller, full C5, complete decoder floor, supplier, native/physical program,
all-size multiplication theorem or new kappa is claimed. Selected cold
replay, Lean, Docker and human/proof-kernel review are unrun.

The family decision is narrow: close one named missing implication rather
than expand a supplier construction with unpaid costs. Frame routing,
restoration, precision and the complete consumer invoice remain unknown and
are outside this theorem. The concurrent mixed5,5,6 support38 investigation
has a different predicate and is not used as an established premise.

## Open next questions

- Can support47 hold uniformly? It matters for the shortening frontier.
  First classify the additional 29-zero normal planes and improve or falsify
  the A2 incidence budget. Both current counts stop at that boundary.
- Which literal current caller meets this common-cut/rank contract? First
  reconcile the caller source and coefficient-deletion map against its exact
  head. No historical profile is inferred from this generic theorem.

See TASK.json for structured questions. Credit Nick Petalas/PR3249/3257,
DreamingOfClouds/PR3154 and the root-simplex/E8/P112 lineage including joaqcoo.
Apache-2.0.
