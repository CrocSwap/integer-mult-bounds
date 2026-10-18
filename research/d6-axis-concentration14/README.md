# Sharp D6 axis concentration at fourteen labels

For any orthogonal full-E8 root pair a,b and arbitrary binary space V of
rank at most six, fourteen labels in its 33-root projective axis force the
entire 120-root closure of V onto that axis. The threshold is sharp: an actual
six-space has thirteen axis roots and seven outside roots.

[PROOF.md](PROOF.md) gives the analytic argument. The bulk 32-root locus spans
a seven-space W with one exceptional axis label outside. A rank-five bulk
section has at most 12 labels. Thus a six-space outside W has at most 13 axis
labels. This improves PR3295's finite threshold 18 and removes that particular
support-space census dependency. Its earlier concentration and caller results
retain their credit; this package claims no new caller or common-cut theorem.

## Reproduce

With an existing Python 3.12 installation and a session-owned writable TMPDIR:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/d6-axis-concentration14
```

A committed package export includes the single canonical geometry input and
runs without Git. Execute ALL three commands from its root:

```sh
python3.12 -I -Werror -B research/d6-axis-concentration14/verify.py
python3.12 -I -Werror -B research/d6-axis-concentration14/independent.py
python3.12 -I -O -Werror -B research/d6-axis-concentration14/test_verify.py
```

The primary binds the exact quadratic model and full root closure, checks
2,667 bulk five-spaces and the literal 13-label witness, then transports the
model through all 7,560 ordered orthogonal pairs. The separate checker scans
all 10,795 six-spaces in the canonical fiber span, finding 120 nonconcentrated
maximizers of size 13. It shares authenticated root reconstruction and source
helpers, with a different coordinate-table/space enumeration. Arbitrary ambient
spaces are covered by the written proof, not by this contained-space scan.

Controls check sharpness, the rank-seven escape, optimized Git-free replay,
changed source bytes, JSON boolean schemas, input/provenance reclassification,
inventory duplication, missing predecessor proof and a false threshold 13.
Private control copies are freshly writable under TMPDIR. No source/export
permissions change. RESULT.json is compared by typed canonical JSON bytes.

## Scope and provenance

Canonical base 463113d675af7410ac91d53a4fed51ec6494eb9a, priority revision 6.
The only runtime scientific input is canonical geometry.py, with Git blob
and SHA256 in SOURCES.json. Exact PR3292 and PR3295 proof bytes are retained
under vendor/ and authenticated by PREDECESSORS.json. PR3295 is retained through
PR3299's unchanged export. Fresh replay needs no pending PR Git objects.
Source authentication establishes bytes, not mathematical admission.

The result concerns the full 120-root model and one full 33-root axis. It applies
to arbitrary support subsets over any coefficient field. It supplies no new
punctured-P112 capacity, coefficient realization, shortening/caller exclusion,
full C5, physical/native/restoration/consumer program, supplier, selected-frontier
change or kappa. Historical full censuses, selected cold replay, Lean, Docker
and human/proof-kernel review are unrun. CHECKS.json records actual checks;
REVIEW.json retains the designated internal receipt when available.

Entry overlap used the hash-verified shared corpus of 358 open PRs at 21:33:34Z,
2,152 Discussion records at 21:34:04Z and2,630 older closed PRs at 20:44:55Z. Exact 3295
and 3292 heads were checked separately. No metadata search proves novelty or
covers arbitrary diffs/unpublished work. Common-two/common-six direction-span and
worker 5 mixed 5/6/6 cut-33 and pair-union work are distinct; no tentative sibling lemma
is used. Family decision: narrow this concentration dependency and stop.

## Open next questions

Bind one actual caller whose singleton requirement lies between fourteen and
seventeen. First pin its common cut, coefficient columns and complete incidence
budget. Other geometric premises and physical/consumer costs remain separate.
This local lemma does not justify a new construction campaign.

## Credit and engineering

Credit Nick Petalas/PR3295/3292/3267, canonical PR3161/3162 root geometry,
David Arias's quadratic model, DreamingOfClouds/PR3154 and the retained E8/P112
lineage including joaqcoo. Original proof bytes and notices are unchanged.
Apache-2.0. Internal computational review is not independent human or proof-kernel
approval. Assistance is disclosed in TASK.json.

Separate Before Serializing Shared State kept scratch and controls session-owned,
with short OS locks for shared Git/claim transactions. Prove It Works required
actual committed read-only Git-free replay of all three commands. The new Python
code has bounded nine-bit spaces,120 roots, 7,560 orbit elements, 2,667 primary and
10,795 corroborating spaces, and 120-second command timeouts. Checks remain enabled
under optimization. Functions stay under 60 lines. Power of Ten rule 3 has a bounded
managed-runtime allocation deviation, with at most 10,795 normal-plane keys and
one 120-root closure live in corroboration. Rule 8 permits execution of one hash-bound
canonical geometry.py via runpy; there is no source discovery or generated code.
Its existing exact eight-dimensional Fraction arithmetic is retained without an
unrelated rewrite. Local package imports use one explicit package directory so
isolated Python works. Standard-library allocation is not statically inspected.
See CHECKS.json for actual diagnostics and any unavailable tooling.
