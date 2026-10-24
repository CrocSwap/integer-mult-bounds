# Coherent frame potentials need additive scalar compatibility

**Scoped written theorem and independent source audit; no new κ.**

PR4966 supplies exact inverse recipes for deterministic native realizations
and leaves a coherent-frame compatibility target for a future paired caller.
This contribution checks an additional requirement of that target: a shared
frame potential commuting through unchanged scalar ADDs on arbitrary inputs
must be additive. Inverses and unitary warp equations alone do not imply it.

For a nonzero dyadic unit c, commuting a potential A through
`(x,y) -> (x+c y,y)` is equivalent to

`A(x+c y)=A(x)+c A(y)` for all x,y.

Putting y=0, then x=0, and finally y=c^-1 z proves additivity. The converse
follows from dyadic homogeneity. [PROOF.md](PROOF.md) states the exact domains
and the gatewise claim boundary; there is no proof-assistant claim.

The independently written source parser checks both actual round-three
orientations, each with 21,449 events and 632 persistent fields. **All 1,002
active frames in each orientation have a distinct persistent-register ADD
with a unit dyadic coefficient, outside every owned-center macro.** The
certificate retains one exact source event per frame per orientation,
including its register pair and coefficient. Both persistent endpoint frame
lists, all eight owned macros, and the retained paid profile are checked.

Two exact distinctions prevent an invalid implication:

- The reversible rounded map `(x,y) -> (x+floor(y/2),y)` has exact two-sided
  inverses but fails ADD equivariance at x=y=(0,1).
- The radial bijection `v -> ||v||² v` commutes with **every unitary** but
  still fails ADD equivariance. Its all-unitary property is proved from
  norm preservation, rather than inferred from finite tests.

Separately, each paid occurrence graph has 1,002 vertices, 3,298 edges,
one component and 2,297 fundamental closed-walk tests for a potential
assignment. Identifying parallel unordered pairs gives 2,855 edges and
cycle rank 1,854. These counts do not show that a particular implementation
fails any test. They identify obligations that inverse pairs alone leave.

This closes one local implication in the **gatewise coherent-potential
recipe with unchanged scalar gates**. It does not exclude global correlated
error schemes, changed scalar circuits, additive coherent realizations, or
a different paired caller. Precision, independent fresh D factors, physical
Gaussian/frame compatibility, workspace, routing, recursive pricing and BIT
admission remain open. The selected conditional κ is unchanged.

## Reproduce

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -I -B research/coherent-frame-additivity/verify.py
python3.12 -I -O -B research/coherent-frame-additivity/verify.py
python3.12 -B scripts/research_package.py --package research/coherent-frame-additivity
```

Expected direct output:

```text
PASS_COHERENT_FRAME_ADDITIVITY frames_per_orientation=1002 paid_cycle_rank=2297 controls=5 no_new_kappa
```

[RESULT.json](RESULT.json) records the recomputed summary and the SHA256 of
the canonical decompressed [certificate](CERTIFICATE.json.gz). Default replay
is read-only. `--write-result NEW_PATH` explicitly creates a new summary and
its sibling certificate, without overwriting either. Gzip headers and streams
are not mathematical evidence: replay compares exact canonical payload bytes.

Finite corroboration includes 12,005 rational linear ADD cases, 98 rounded
two-sided inverse round trips and 147 rational radial/orthogonal cases.
Four semantic source mutations and a changed-source-byte control must fail
for their specified reasons. Conditions use exceptions and remain active
under `-O`. No native physical suite, selected cold replay, Lean build or
full multiplication theorem is part of this audit.

## Sources and overlap

Canonical base: `b91956876e5b4122fd89179f1b57557ff8378f15`, priority revision 7.
Assignment seed: `7497f9f029574287f7cf5b3d5415bf74`, independent-verification
track, `formal-interface-lemma` card. The scope change to a written local
boundary theorem is declared in [TASK.json](TASK.json).

[SOURCES.json](SOURCES.json) pins the sole executed scientific input,
Cao Yifan's actual round-three word, and historical assignment context.
[VENDORED.json](VENDORED.json) authenticates Yiyang's exact PR4966 inverse
proof at `039b6ea51ab7a7efb38fc6851f345839683251b0`; no predecessor
implementation is imported or executed.

The [overlap receipt](OVERLAP.json) records live open-PR/discussion and local
note coverage. PR4966 already distinguishes exact reversibility from linear
operator identities; the new evidence is the ADD criterion and complete
all-active-frame source binding. Nick Petalas's coherent-transvection
neighborhood proves geometric graph transport constraints, which receive
credit here; the elementary graph lemma is not claimed as new mathematics.
Coverage does not include every code diff or unpublished work and is not
a novelty certificate.

Canonical investigation:
[Discussion4611](https://github.com/CrocSwap/integer-mult-bounds/discussions/4611#discussioncomment-19138553).

## Open next questions

- Can additive actual frame potentials satisfy the paid closed-walk and
  unchanged warp equations at a charged precision? Start with one actual
  non-tree paid edge and its forest path, including their true recursive
  realizations. Such realizations and their full bill are not supplied here.
- If nonlinear potentials are retained, can a literal conjugated scalar
  gate or a paid quantitative error bound replace unchanged ADDs? Start with
  one emitted persistent-register witness and carry the correction through
  the actual two-call caller. Unknown correction and storage costs are not zero.

## Credit

Yiyang (@Lyy-iiis), with OpenAI Codex assistance, supplies PR4966's paid-site
precision census and same-realization inverse construction. Cao Yifan supplies
the round-three actual word and its retained predecessor lineage. The
two-full Laurent-border, native E8/Clifford and PR4610 predecessor attribution
remains with the source authors. Nick Petalas supplies the related binary
symplectic graph-neighborhood result. No claim of independent human review
is made. Prepared by Cinna Davis with substantial OpenAI Codex assistance
in research, proof explanation, implementation, verification and writing.
New work is Apache-2.0; the vendored predecessor retains its original notice.
