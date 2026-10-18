# Actual native warp relations add no paired-extraction directions

The free-operator model distinguishes 72 warp IDs in the latest six-skip
construction, although only 58 native maps are distinct. Could those extra
native equalities unlock a better supplier? **For the fixed rational scalar
paired-extraction contract, the answer is no.** This is a scoped exact negative,
not a new κ or a general limitation on new constructions.

For both PR3042 words retained by PR3054:

- The identity plus the 58 distinct native maps are rationally independent,
  with all 512 columns and global phases included.
- Merging duplicate maps removes 184 symbolic terms from the complete
  non-target operator, but its allowed right and left extraction spaces stay
  exactly the same: dimensions **119 and 181**.
- Consequently their scalar pairing is unchanged for **every terminal support**,
  including simultaneous extractions. This is a kernel-equality proof, not
  a finite search that happened to find no candidate.

The practical implication is that substituting actual native equalities into
this fixed-word scalar search cannot provide new extraction directions. A
further attempt needs a changed word/interface or a better realization of an
already available direction. The [proof](PROOF.md) states the exact contract
and separates this result from the prior cost and frame obstructions.

## Reproduce

Python 3.12, standard library only, no network or solver:

```sh
python3.12 -B scripts/research_package.py --package research/native-warp-extraction-boundary
```

Expected: `PASS_NATIVE_WARP_EXTRACTION_BOUNDARY`, then
`PASS_REGISTERED_RESEARCH_PACKAGE` with `outcome=negative-result`.
The direct verifier regenerates the deterministic receipt and compares it with
[RESULT.json](RESULT.json). To export another copy, run
`python3.12 -B research/native-warp-extraction-boundary/verify.py --output /tmp/native-boundary.json`.

The independent sparse rational interpreter imports no predecessor Python.
Exact null vectors with a unit minor give nullity lower bounds; modular rank
certificates give matching upper bounds over Q. The tests include an example
where native aliasing **does** enlarge an extraction space, lost constraints,
corrupted null vectors, a rank-dropping prime, operator-phase faults, forbidden
target feedback, non-affine warp words, compensation omission, source corruption
and a separate two-dimensional noncommuting vector interpreter.

## Sources and scope

Base: `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
[INPUTS.json](INPUTS.json) pins the unchanged source words and retained notices.
[SOURCES.json](SOURCES.json) pins the native phase formula and selected record.
PR3042 head is `84cc406ad91ec53fff329a11a445d7effe564a77`; PR3054 head is
`4773c3ea67b471415870e38411fae313ec44a675`. PR3115's
`400bc83669f86917f69b6249cd0356d3a913293c` refines the arithmetic of the same
words; its claimed κ is not independently admitted here. The selected accepted
conditional value remains `0.001672660197076918` from PR1094.

PR3114's restore-only optimum and PR3065's fixed-scalar frame optimum leave
changed mechanisms open. This result tests a different premise: replacing
independent formal warp symbols by their actual finite native operators.
It does not reprove those earlier optima, optimize an invoice, or replace
supplier/native/outer admission. No selected-frontier change or full
multiplication theorem is asserted. All inherited physical, all-size/compiler,
precision, common-label, caller and analytic obligations remain separate.

## Open next questions

Can a changed scalar program create a genuinely new native cancellation, or can
an operator-valued preparation/readout exploit one while fitting its complete
bill? First exhibit the new exact M and a direction outside the old spaces;
then price frame crossings, compensation, source access, restoration, buffers,
owner capacity and both supplier constraints. Native phase-aware composition
and a legal consumer are blockers. Merely relabeling the present warp IDs or
repeating the fixed-word extraction search does not change this decision.

## Credit

Tekalign, with substantial OpenAI Codex assistance. Evidence is author-checked;
no independent human review or proof-kernel verification is claimed. Apache-2.0.

Credit Cinna Davis/PR2226 for the native warp convention; Jeremy Diviney/PR2908
for paired input/output extraction; Mason Hale/PR2917 and Marius-Paul Dumitrean/
PR2979 for its extension and joint rank-seven words; dcharb78/PR3042 for the six
skips; Nick Petalas/PR3054 for the pinned T740 composition and native bindings;
Jeremy Kothe for the scalar/frame/cleanup lineage; dataisfire/PR3115 for the
latest arithmetic refinement; and icekylinx, DreamingOfClouds, Dugongue, Yiyang Lu,
Ross Richardson, themilkman216 and the retained contributors in
[the original credits](inputs/CREDITS.md) and [notice](inputs/NOTICE).
