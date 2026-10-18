# Hyperplane-ended helpers: review and integration through PR599

This round reviews #589, #591–#596, #598 and #599 at the immutable heads in
`research/community-hyperplane599-audit/START.json`. The selected candidate is
Jeremy Kothe's #596 with eumemic's unchanged #543 bit supplier:
κ = 16127213726553/10000000000000000 = 0.0016127213726553.
See the integration receipt for execution and publication status.

## Construction and accounting

The previous #588 word makes every entering helper finish at FULL. In #591,
38 helpers in each local provider have one cleanup gate, with neither operand
touched by an earlier cleanup gate. Each such gate can move immediately after
part B. The join U of its operands' last frames has dimension eight. The helper
is untouched by the remaining cleanup and can terminate at U; its partner
continues to its required endpoint. The constructor checks the commuting move,
and the independent rational replay checks all 728 scalar columns in both
orientations, including arbitrary initial helper data.

An entering helper with entrance E and terminal U has residual T_U T_E⁻¹.
Its pre/post wrappers must use the pair (E,U), rather than E alone. Exact
Clifford checks, including global phase, establish
L_(E,U)⁻¹ T_U T_E⁻¹ R_(E,U)⁻¹ = C_[7] ⊗ I for the selected pairs.
The helper width becomes dim(U)−dim(E)=7. The local profile changes by
{1:+3, 2:−2} per affected helper; after residual accounting the deficit is
unchanged. The narrower helper fits alongside width-nine helpers in rank-16
owner slots. The gain is in the whole paid profile, not an increased deficit.

#592 changes the dispatch to 53 ck and 19 atm3 calls. #596 improves its literal
owner map. Their Python verifiers and provider definitions are identical;
#592's admission is rerun with independently checked #596 locals after exact
source/spec comparison. #596's baseline and both provider chains are rebuilt
fresh. #591's three providers are rebuilt with the already checked, unchanged
#588 baseline; this reuse is recorded explicitly.

The two exact moment engines, freshly reconstructed invoices, 47 strict outer
constraints and negative controls remain necessary. The selected bit supplier
is still #543. #589 is better bit headroom but is not needed by this complex-
limited composition. The conservative complex charge also passes at
κ = 0.001612721369804261. The selected native complex charge follows Rohan
Arun's #559 correction; the bit surcharge remains.

## Formalization and instance correspondence

Jeremy Kothe's updated #593 proves the arbitrary-terminal extension and the
three exact non-cold Clifford factorizations in Lean. Its source reuses the
Lemma A/G packages. DreamingOfClouds' #599 adds multi-gate cleanup tails and a
cold specialization. Integration retains both the newer exact proofs and
these extensions; it does not replace #593 with #599's older base.

The maintainer's `scripts/verify_hpe_lean_binding.py` compares every selected
helper's serialized left/right monomials with the literal recipes in
`HyperplaneEnd/Exact.lean`, with phase mutations rejected. The instance checker
was hardened to require denominator one in `h -= p`, with an extra `h -= p/2`
mutation. The multi-gate and cold theorems remain general extensions, not
new selected circuit instances. Their arbitrary-pair factorization and
physical hypotheses are not discharged by the three non-cold identities.

No complete multiplication theorem has been formalized here. Remaining
assumptions include all-size compilation, common-label/mutable-source
realization, pooled whole-call correlated-helper hosting, normalized residuals,
precision/tape/exact recovery and analytic transfer. The bit composition does
not instantiate the stricter one-helper-per-family PR458 contract.

## Research, parallel work and attribution

| PR | Contributor | Contribution and disposition scope |
|---|---|---|
| #589 | DreamingOfClouds | Two transports on the punctured bit word; full nine/eleven-stage replay. Retained separately at `research/e8-bit-p111-tuned`, leaving frozen #555 untouched. |
| #591/#592/#596 | Jeremy Kothe | Hyperplane-ended helpers, dispatch optimization and improved owner map; all intermediate packages retained. |
| #593 | Jeremy Kothe | Arbitrary-terminal interface and exact selected Clifford identities in Lean. |
| #594 | eumemic | Independent replay report, certificate and receipt auditor. Only the three files introduced by its final commit are integrated; the inherited historical diff remains open for reconciliation. |
| #595 | DreamingOfClouds | Format ceilings, spec/convention census, helper budgets and scoped structural research. |
| #598 | Dominik Scholz | Three reproducible Leech/Turyn packages: exact geometry/factors, code-space and full-port fitting obstructions, and scoped cost screens. |
| #599 | DreamingOfClouds | Multi-gate cleanup and cold-helper Lean extensions. |

The #595 ceiling is conditional on its S2 accounting axioms and cited premises.
Numerical certificates, finite toys, SAT results without proof logs, and
floating-point optimization comparisons are distinguished in its README.
It is not a universal ceiling on multiplication or every network interface.
The #598 obstructions likewise apply to the stated label/encoder classes;
there is no new complete supplier or exponent claim.

#594's declared independent run is preserved as contributor evidence. Its
original run directory/logs were not supplied, so their historical hashes
cannot be independently authenticated from the three submitted files alone.
Our fresh #591 replay checks the construction separately and exercises its
receipt auditor. Neither constitutes blanket approval of the older branch.

Earlier contributors and licenses remain credited, including Dominik Scholz,
Jonathan Capalbo, Chafik Boukhalfa, Dugongue, Rohan Arun, icekylinx and the
preceding OpenAI #109 framework. Original AI-assistance disclosures are kept.
Maintainer integration is by Douglas Colkitt with OpenAI Codex assistance.

## Reproduction

Run `make frontier596-verify` for a cold bit543 + complex596 replay and exact
composition binding. The pinned older #569 source subset is already bundled
at `research/promoted-kernel-coalescing/vendor/larger_gain`; the public runner
selects it explicitly. The package README's generic witness-tool command is
not the maintained reproduction entry point for this round.

Run `python3 research/hyperplane-end-lean/verify.py` for the combined Lean build
and axiom checks. Run its instance checker and `scripts/verify_hpe_lean_binding.py`
on the generated `ck-local`, `atm3-local` and (for #591) `jp8-local` directories.
The integration receipt distinguishes fresh work, unchanged dependency reuse,
source equality checks and local results from remote Linux CI status.
