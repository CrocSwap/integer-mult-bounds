# One changed odd entry cannot beat the P112 copy floor, even with nine new factors

**Scoped negative result; no new supplier or kappa.** On the fixed P112 E8
unit, change one odd matrix entry by any nonzero complex amplitude. The
resulting completion has rank nine. **Every exact nine-term complex
factorization has total label-pairing copy cost at least 64**, equal to the
original eight coordinate terms. Every factor may change: this covers the
whole GL(9,C) factor-basis family, rather than holding six or seven terms
fixed. Ordinary transpose is used throughout.

The separate copy power bill also stays at least `8 * 8^q` for `0<q<=1`.
The statement is about separate term costs in PR717/PR968's label model.
It does not price a whole supplier, exclude savings in other operations,
or establish a physical copy lower bound under changed gathering rules.

## What establishes the claim

[PROOF.md](PROOF.md) gives the universal argument. The finite checker
classifies every complex normal whose support, after one singleton
deletion, spans a proper binary label subspace. The only possibilities
are the eight punctured frame normals and the deleted root normal.
This is an exact finite linear-algebra result, with no flat-classification
premise or heuristic coefficient search.

The completion forces both nine-dimensional factor spaces. Comparing
their coefficients leaves either eight or nine terms with nonzero root
components on both sides. With nine such terms, having all costs seven
would put the left normals in a space of dimension at most five. With
eight, lowering one term to seven requires a compensating singleton-side
term of cost one. Those two cases prove the floor and power inequalities.

[CERTIFICATE.json](CERTIFICATE.json) and [verify.py](verify.py) cover:

- All **57,232** hyperplane/deletion cases: 1,008 exact one-dimensional
  normal kernels, and 56,224 full-rank exclusions.
- All 1,008 survivor hyperplanes, 112 even-neighbor spans, 14,400
  root-hyperplane pairings, and **5,824 ordered odd singleton locations**.
- Five exact Q(i) fixtures, checking all **62,720 matrix entries**:
  attaining cost 64, an imaginary completion, a singleton-side cost 65,
  a nontrivial attaining profile `(7,8,8,8,8,8,8,8,1)`, and a factor
  change that mixes all nine columns and costs 81.
- Thirteen tests: one positive fixture and **12 failure controls** for
  missing/corrupted evidence, incorrect coefficients, nonreciprocal basis
  changes, accidental conjugation, discarded compensation, invalid scope,
  source drift and singular mixing.

Rank eight modulo three is used only as an exact nonzero-minor lower
bound over Q/C. Every rank-seven case also checks an integer null vector
against every row, giving a matching upper bound and its entire complex
kernel. The checker imports no predecessor implementation or pricing engine.
The finite lemmas and fixtures do not themselves quantify all complex
factorizations; that step is the written proof.

## Reproduce

From the repository root, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/p112-singleton-rank9
```

Expected: `PASS_P112_SINGLETON_RANK9_LEMMAS`, 13 passing tests, and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.
The explicit commands and timeout bounds are in [VERIFY.json](VERIFY.json).
Direct read-only replay also works with Python 3.10+ and under `-O`:

```sh
python3 -I -O -B research/p112-singleton-rank9/verify.py
python3 -I -O -B research/p112-singleton-rank9/test_verify.py
```

`verify.py --write` regenerates only this package's certificate. Source
commit/blob/SHA256 pins and the originating catalogue are in
[SOURCES.json](SOURCES.json). The selected record is historical provenance;
the model definition is a live pinned input. Full Git history is needed
for the registered provenance check. The direct finite replay needs only
the package and that declared model input.

## Scope, overlap and limitations

Task `complex-masked-decoder`, refined to **one changed odd entry, all nine
terms allowed to change**; chooser nonce `8546cf43704f750d58dc187afac16177`,
base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. See
[TASK.json](TASK.json) for the bounded card, exact overlap heads and next
questions. Coordination is in [Discussion1360](https://github.com/CrocSwap/integer-mult-bounds/discussions/1360).

Arham Tahir's [PR1331](https://github.com/CrocSwap/integer-mult-bounds/pull/1331)
covers an arbitrary free rectangle mixed with one coordinate term.
commdata2338's [PR1375](https://github.com/CrocSwap/integer-mult-bounds/pull/1375)
covers two coordinate terms with small free rectangles. Hanson Sun's
[PR1432](https://github.com/CrocSwap/integer-mult-bounds/pull/1432) and
[PR1473](https://github.com/CrocSwap/integer-mult-bounds/pull/1473) cover
larger two-mode rectangle classes. This package takes a smaller correction
support but removes the restriction on which factor terms may change;
it gives a different whole-factor-space proof. Those pending claims are
credited overlap leads, not theorem dependencies.

Gareth Davidson / bitplane's
[PR1468](https://github.com/CrocSwap/integer-mult-bounds/pull/1468) covers
arbitrary one-column corrections with two coordinate modes; its six
unchanged terms distinguish it from this nine-factor statement.
The final refresh found 726 open PRs and 231 Discussion records with
complete pagination and no warnings. This is overlap evidence, not a
proof of novelty. Local environments, commands and the read-only optimized
export check are recorded in [VALIDATION.json](VALIDATION.json).

Only exactly nine terms, one changed odd entry, P112 and separate binary
label-pairing costs are covered. Multiple changed entries, larger free
rectangles, ten or more terms, other punctures and shared-copy pricing
remain open. No complete cold replay, physical gathering, helper/frame
realization, restoration, precision/tape or supplier adoption is performed.
All inherited all-size/compiler, common-label/mutable-source, hosting,
analytic-transfer and bit H1-H5 obligations remain. The selected frontier
and every predecessor file are unchanged. No independent human review or
formal multiplication theorem is claimed.

## Open next questions

1. **Two changed odd entries with all factor terms free.** This tests whether
   a larger correction space escapes the nine-direction classification.
   First enumerate the 511 normal kernels after two deletions and separate
   rank-nine from rank-ten completions. The blocker is a new coupled
   coefficient argument; the one-entry proof does not automatically extend.
2. **Ten-term factorizations of this same completion.** Extra pure-side terms
   might alter the compensation argument. First solve the rank-nine space
   factorization with one additional dependency, granting all physical
   overhead zero. A new bound on the simultaneous cross-coefficient
   cancellations is needed before physical synthesis is justified.

## Credit and license

DreamingOfClouds supplied PR717's masked model and PR595's format lineage;
Mihir Srivastava supplied PR845's E8 geometry; themilkman216 supplied
PR968's pairing-rank cost convention and frame-pair theorem;
GamingPuzzled / Joel Pulikkan supplied PR620's coordinate cost 64.
woklerx's PR1077 extended the earlier eight-term theorem over C. The
selected PR1094/PR589 chain is orientation only. The broader nine-term
all-pairs work in PR1224 is also distinguished in TASK.json.

Prepared by Arham Tahir (@Arham-Tahir64) with substantial OpenAI Codex
assistance in research, proof, code and documentation. Apache-2.0.
