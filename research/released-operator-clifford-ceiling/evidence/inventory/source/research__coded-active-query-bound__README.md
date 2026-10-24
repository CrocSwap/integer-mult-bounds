# Sharp active local query cost for the physical eight-mode code

**The physical code's one-sided correction and eight-mode extraction/expansion each require exactly 112 unary field calls in the stated local model, attained by 112 H1 calls.** The conjugated adapter `J=Q^-1 C Q` and `J-I` each require at least 112 unary paid calls. The proof permits arbitrary chronological linear feedback, saved inputs, copies, owned resets, fanout and free mixing across any fixed number of independent blocks. No new κ or complete-caller lower bound is claimed.

Here `C_ij=a_ij K_i^-1 K_j` is the actual 112-port code from [#4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933), `P=(I-C)/14`, and Q is the central rank-one Gaussian. A field call operates on one owner-width field. Free operations are finite linear owner programs over a fixed finite projective group of one-column invertible monomial maps; they have ordinary scalar/routing/precision cost but no recursive Gaussian call. Paid unary maps may be arbitrary zero-preserving linear maps, so the lower bound also applies when those maps are Gaussian calls of any rank.

The free permutations may be non-Clifford; no finite ambient Clifford group is assumed. The theorem concerns identities required at every positive tensor width; its obstruction holds at every sufficiently large width. Each admitted one-column map h acts by the same tensor lift `h^⊗f` in every column; independent per-column choices are not admitted. Scalar coefficients and finite control choices may depend on width. At width one, Gaussian operators can lie in the scalar span of monomials, so the lower bound is deliberately not asserted for every small width. It excludes wider packed channels, arbitrary noncolumnwise address maps, nonlinear or data-dependent controls, approximate endpoints and preexisting nonfree observations of the fresh inputs. A running native caller may already possess such observations, so this result does not exclude an active three-query p2 construction.

Write `U=diag(K_i^-1) M` and `V=M^T diag(K_i)/56` for the actual source mode maps. Then `P=UV` and `VU=I_8`. The local endpoints have the following exact call bounds at sufficiently large width:

| Endpoint | Fresh input fields | Output fields | Paid unary calls |
|---|---:|---:|---:|
| QP or PQ | 112 | 112 | Exactly 112 |
| QU, mode expansion followed by Q | 8 | 112 | Exactly 112 |
| VQ, Q followed by mode extraction | 112 | 8 | Exactly 112 |
| J or J-I | 112 | 112 | At least 112; 224 H1 suffice |

The mode bounds also cover every free eight-mode retraction basis `P=U'V'`, `V'U'=I_8`, since these differ from U,V by invertible free boundaries. They do not classify arbitrary unrelated eight-output operators.

## What changes relative to the predecessors

[#4932](https://github.com/CrocSwap/integer-mult-bounds/pull/4932)'s [coded-port adapter ceiling](../coded-port-adapter-ceiling/README.md) treats one parallel query bank and forces 112 grade-two channels. The [passive saved-query ceiling](../passive-saved-query-ceiling/README.md) keeps its later paid inputs fixed. This package uses a different invariant: the physical port transports occupy distinct monomial cosets. An input or output kernel cut then covers **arbitrary chronological paid calls and active linear feedback** for the standalone local endpoint. Its 112-call result counts calls of any grade; it does not extend the predecessor's grade-two conclusion to the larger model.

The core source fact is that the 112 vectors `G_i e0` are distinct. For each fixed output i, the words `Q^-1 K_i^-1 K_j Q` lie in distinct right monomial cosets. Each source column has 52 nonzero off-diagonal entries. Consequently `J-F` has no nonzero free input column for any free bypass F. A circuit with fewer than 112 unary calls has a nonzero free input direction that vanishes at every paid input, even when later calls use previous responses. These statements contradict each other. The output-cut version proves the QP bound; the input-cut version proves PQ. Applying Q to all 112 fields before or after the free P realizes each one-sided upper bound.

For m independent copies, arbitrary cross-copy free mixing still requires 112m calls. The one-sided 112m-H1 upper constructions attain those bounds. This is a direct-sum statement about the declared local endpoints, not about amortization into already-paid FULLs, IDLEs or native internal prefixes. For J/J-I, 112-call attainability remains open; the elementary conjugation uses 224 H1 calls.

An isolated repair that restores one backward coded FULL to the ordinary uncoded FULL is also priced sharply. Since `C=I−14P`, the exact entry patch is `X ← X−14QP Y`; it needs 112 H1 calls in the enlarged local model. The inherited producer removes only 8 H8 calls, worth at most 64 in every moment with exponent `1−c`, `0≤c<1`. Thus such an independently implemented repair increases the recursive paid bill by at least 48 per FULL, or 48m for a direct sum. The eight-H8 removal is an inherited source invoice, not replayed by this checker. Absorbing the patch into already-paid native operations is outside the corollary.

The mathematical argument, finite phase treatment and all-width scope are in [PROOF.md](PROOF.md). [INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) records a separately derived proof audit and binary census. [EXTENSION-REVIEW.md](EXTENSION-REVIEW.md) audits the finite-H extension, rectangular modes, rebasing, direct sums and isolated-patch tariff. Neither is independent human or proof-kernel acceptance.

## Evidence and reproduction

Python 3.12 for the registered runner, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/coded-active-query-bound
```

Direct replay, including after an official package export with its declared inputs:

```sh
python3 -I -W error -B research/coded-active-query-bound/verify.py
python3 -I -O -W error -B research/coded-active-query-bound/verify.py
python3 -I -O -W error -B research/coded-active-query-bound/independent.py
```

The main verifier authenticates the code, normalizers and exact Clifford implementation before executing the latter's source bytes. It checks all 12,544 ordered port pairs by both a separately written binary formula and source tableaus: 112 self pairs have grade 0; 12,432 distinct pairs have grade 2; all 5,824 supported off-diagonal code terms are grade 2. It also checks 12,544 left-coset conjugates, 12,544 one-sided grade-one transports, the 52-entry column supports, all 12,544 entries of `a=I-MM^T/4`, all 64 entries of `M^T M=56I`, and four mode contacts per owner. Four rejection controls alter a direction, a source column, the diagonal or a mode factor. The independent checker imports no Clifford implementation. Both compare exact finite receipts; checks remain active under `-O`.

[RESULT.json](RESULT.json) and [INDEPENDENT.json](INDEPENDENT.json) are finite source receipts. They do not enumerate the monomial group algebra, test every circuit, or mechanically prove the tensor/kernel argument. [SOURCES.json](SOURCES.json) pins frozen main `4c0a359d88f22f05189d51f48387750b801a45d4`, live inputs and proof provenance. [VERIFY.json](VERIFY.json) declares every live input. The submission base is refreshed canonical main `20a1e31bc6009b9b3f4d084bbaadc6350e34fcba`; the earlier scientific pins remain unchanged. No predecessor package is copied or altered; provenance-only proof references resolve through the pinned Git history. [VALIDATION.md](VALIDATION.md) states executed checks and unrun obligations.

## Open next questions

Can a complete coded caller use nonfree observations that its FULLs and IDLEs already produced to recover all prescribed independent Gaussian outputs? This is the meaningful route left by the local result. The first step is one explicit changed paid input with its retained observations, followed by all terminal operator identities and a complete invoice. The current package supplies no such global endpoint. The final checkpoint also reviewed Cinna Davis's [common-code moving-stage interface](../common-code-moving-stages/README.md), whose transported Gaussian stages fail the inherited commutation relation, and JoyboyBrian's [fresh-D coherent-pair countermodel](../two-full-fresh-d-coherent-pair/README.md). Their changed interfaces and endpoint obligations remain distinct from this local query theorem.

What is the exact complexity of J or J-I between 112 and 224 calls? A smaller explicit chronological circuit or stronger cut invariant would resolve the gap. The sharp 112 result for QP/PQ does not settle it. Structured first steps and blockers are in [TASK.json](TASK.json).

## Credit

Prepared for Dillon with substantial OpenAI Codex assistance from separate proof, independent-review, construction and packaging agents. Credit Dugongue's center-free producer [#4929](https://github.com/CrocSwap/integer-mult-bounds/pull/4929), the real signed normalizers/physical C in #4933, Chris R/Clear1nsight's #4932 finite phase algebra and one-bank theorem, the passive package's uniform-alphabet clarification, Cinna Davis/1337isnot1337's #4694/#4698, Cao Yifan/intqwq's #4610 native source, zxv and the retained Clifford/helper/compiler lineage. See [ATTRIBUTION.md](ATTRIBUTION.md). Standard causal/image/row-space rank cuts retain earlier method credit to eumemic's PR288 and Ali Romman's PR468, as summarized in [fixed-support unary-query bounds](../fixed-support-unary-query-bounds/README.md); that different carrier theorem does not imply the physical-code result here. New work is Apache-2.0. The selected frontier remains unchanged.
