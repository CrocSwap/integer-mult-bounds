# Exact certificates for PR1212 Lemmas 5 and 6

**Conditional independent audit; no new kappa.** The complete-class and gluing
lemmas in [PR1212](https://github.com/CrocSwap/integer-mult-bounds/pull/1212),
head `57099cb5684f38877f31d149d598801671a633db`, hold under their stated
hypotheses. [The audit](audit.md) expands the universal argument and supplies
independently implemented exact certificates. It finds no substantive flaw.
Zero exclusion remains an explicit inherited premise.

This follows the [independent-check handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18912316)
and [claim 1448](https://github.com/CrocSwap/integer-mult-bounds/discussions/1448).
The contribution is corroboration of the predecessor proof, not a new rigidity
theorem, decoder-cost floor or supplier.

## What the new checker adds

- Exact polynomial identities and explicit unimodular matrices classify the
  nonzero local ratio system. Its exponent quotient is `Z^3 + Z/2`, retaining
  both sign branches; the class-rank condition excludes the negative branch.
- A universal sign-normalization argument and symbolic ordinary-transpose
  calculation give the claimed factor of four in the dual class matrix.
- A separate integer-vector implementation reconstructs the E8 geometry for
  the explicit P112/P120 pivots, all complete classes and every required witness.
- Integer matrices satisfy `MP=0`, `QP=I` and `I-PQ=WM` on the actual gluing
  variables. These certify a saturated relation lattice and global potential,
  rather than only a rational rank or sampled scaling assignment.

| Exact finite quantity | P112 | P120 |
|---|---:|---:|
| Complete live classes | 26 | 28 |
| Four-point blocks | 14 | 14 |
| Class/group witness obligations | 312 | 336 |
| Distinct-block class overlaps | 288 | 336 |
| Class-coordinate variables | 104 | 112 |
| Gluing lattice rank | 71 | 77 |

The checker generates all explicit witnesses and sparse integer matrices without
a checkout of the pending predecessor or an external solver. The written proof explains why the
identities imply field-valued statements; finite checks do not replace that proof.
An optional `--certificate-out PATH` exports the generated certificate; no saved
certificate is needed for the default replay.

## Reproduce

From the repository root, Python 3.12 and the standard library:

```sh
python3 -I -B research/complex-rank8-ratio-gluing-audit/verify.py
python3 -I -O -B research/complex-rank8-ratio-gluing-audit/verify.py
python3 scripts/research_package.py --package research/complex-rank8-ratio-gluing-audit
```

Expected: 28 named checks for each direct command, exit status zero. The
registered replay uses the second command. Neither direct command writes files.
Optional `--out PATH` and `--certificate-out PATH` produce a report or certificate.
Passing an exported certificate to `--check-certificate PATH` adds one comparison
check, for 29 checks in total.

Local replay on Python 3.12.14, macOS arm64 passed the ordinary 28-check run and
an optimized 29-check run against a saved certificate in under half a second
each. The generated certificate and both successful stdout logs matched the Pro
research-session outputs byte for byte. That historical saved-certificate replay
is retained as evidence; the redundant generated file is omitted from this
package. Its canonical SHA256 is
`102cb8ddda027286b010b6edfd80c2b1c201a24020dfe32b0caee0f2a827c57e`.

Controls reject damaged local/gluing identities, an incorrect transpose or
normalization, and a damaged design. Explicit counterexamples distinguish the
nonzero, cross-block and global cycle conditions. Separately, changing the saved
Smith diagonal entry from 2 to 1 was rejected under `-O` with exit status 1 and
`saved certificate differs from fresh exact reconstruction`. All guards remain
active with Python assertions disabled.

A separate GPT-6 Pro chat reviewed the displayed universal algebra and lattice
implications and corroborated them conditionally. Its two presentation
clarifications are included: the signed pair transfer when an arbitrary anchor
has `k=0!=a`, and comparison-graph connectivity separately for each coordinate
pair. That review did not inspect this checker, its certificates or the geometry.
Its six groups of displayed-identity checks also passed local normal and `-O`
replay; this is additional AI review, not independent human or formal review.

## Scope and source pins

This checks only the named conditional lemmas and explicit P112/P120 geometry.
It does not independently prove the predecessor's zero-exclusion DRUP, the
PR717/PR968 cost theorems, arbitrary-frame symmetry transport, later puncture
extensions, physical realization, all-size/precision/tape/analytic transfer or
the full multiplication theorem. No proof assistant or independent human review
is claimed. The selected frontier and frozen packages are unchanged; the full
selected-supplier cold replay is outside this additive audit.

The original predecessor checker was also reproduced separately: 61 P112 and
41 P120 checks passed on Python 3.13.1. That is original-checker replay, distinct
from this independently implemented checker and its scope.

[SOURCES.json](SOURCES.json) pins main provenance and the external predecessor's
commit, Git blobs and SHA256 hashes. `external_predecessors` is attribution
metadata outside the generic hook's pin validation; those files are not runtime
inputs. [TASK.json](TASK.json) records the explicit change from the selector's
construction card to the requested audit. [VERIFY.json](VERIFY.json) registers
the bounded self-contained replay.

## Open next questions

Can the integer-retraction implication be checked by a proof assistant? A first
step is to formalize that `MP=0`, `QP=I`, `I-PQ=WM` identifies the quotient of the
integer exponent group with the free parameter group, then connect that result
to monomials in a field's multiplicative group. This would check the universal
bridge from finite certificates to scalar gluing. The blocker is a formal
encoding and kernel replay; this package supplies written mathematics and
Python checks only. The structured question is in [TASK.json](TASK.json).

## Credit and license

Brett Halligan (@burntout76) and Ninefold supplied PR1212 and the original proof;
DreamingOfClouds supplied the PR717 model; themilkman216 supplied PR968. Their
claims and licenses remain attributed. New audit and exact checker prepared by
Andrey Mas with substantial GPT-6 Pro assistance through ChatGPT; Codex handled
coordination, repository packaging and local replay. This is AI-assisted
independent reimplementation, not independent human review. Apache-2.0.
