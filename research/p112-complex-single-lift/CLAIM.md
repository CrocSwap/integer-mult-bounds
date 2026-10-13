# Local sprint claim

- Track: structural decoder research (40--49); assignment seed **40**,
  generated once with the operating system's
  `System.Security.Cryptography.RandomNumberGenerator.GetInt32(0,100)`.
- Exact base: `407d52ff15b2217b6e22bce44728b4c3907b6515` (fetched main).
- Selected conditional kappa at base: `1661960547713947/10^18`, reviewed
  #942 U8/T37 composition; no selected-supplier change is proposed.
- Scope: extend or refute #845's fixed-reader P112 single-lift obstruction
  for arbitrary **complex** coefficients and complex source corrections,
  retaining the eight real coordinate reader columns and exact equality
  on all entries of `XX^T`. Transpose is algebraic, without conjugation.
- Hypothesis/method: phase freedom could change cancellation supports.
  Partition nonzero lift coefficients by equality up to sign, reduce
  cancellation constraints to the predecessor's signed binary systems,
  and check the full-support exceptional kernel. Use exact Gaussian
  rational diagnostic examples and an independently reviewed argument.
- Three candidates considered: (1) this complex single-lift extension;
  (2) two simultaneously added totals on P112, a larger mechanism whose
  nonlinear support classification is unlikely to finish in the budget;
  (3) higher-level stars on paired hypercubes, adjacent to #231/#669.
  Candidate 1 was selected after inspecting its explicit predecessor
  exclusion. Seed 40 fixes diagnostic values and the full-matrix pair
  `40 mod 28 = 12`. Novelty comes from the scalar domain, not the seed.
- Expected deliverable: one scoped negative result or exact counterexample,
  proof note, reproducible checker/certificate, source pins, and controls.
  No new kappa without an implemented complete paid construction.
- Budget: about 50 minutes from 2026-10-13 08:43 PDT; expected finish
  09:33 PDT. Reserve the final 25% for verification and handoff.
- Coordination: the live issue page showed only #650 and #913, with no
  pinned sprint issue. This local claim substitutes for a sprint comment;
  no separate issue is opened. GitHub access was verified.
- Initial overlap review: current status, selected certificate, actual
  #942 assembly/source manifest and maintainer review, contribution index,
  review ledger, #620 decoder report, and #845 proof and sources read.
  Curiosity Bot's live all-state P112/hypercube search returned
  #620/#669/#715/#717/#845/#968/#231. #968 concerns exact eight-term
  frame-pair decoders under punctures; this scope retains eight readers
  and allows a ninth term. #912 treats adaptive Hurwitz transcripts,
  not this P112 algebraic factorization. No duplicate complex single-lift
  extension was found in these scoped searches.

Prepared for GitHub contributor **@woklerx**, with substantial OpenAI Codex
assistance. Delegated verification stays within this claimed mechanism.

## Method refinement within the claimed mechanism

Independent reasoning found a simpler, stronger proof than the proposed
sign-class analysis: a generic real-linear projection, applied reciprocally
to source coefficients, preserves every term's supports exactly. The lemma
holds for any finite real X. It transfers the existing real P112 theorem
to complex scalars without adding a new sign census. The bounded experiment
therefore tests the explicit transfer, with exact Gaussian-rational cases,
and replays the inherited finite premises. This is a change of proof method
within the same fixed-reader/single-added-total scope, not a new search.

Concurrent unrelated work appeared in the initial shared checkout during
the sprint. The contribution was copied with byte-hash verification into
an isolated worktree on `research/seed40-complex-domain` at the same exact
base, and only its own duplicate untracked directory was removed from the
shared checkout. No unrelated contribution files were edited.

## Result and final overlap refresh

Completed: a general support-preserving complex-to-real single-lift
theorem, and its scoped P112 copy-cost floor of 64. The exact projection
and two implementations preserve individual costs; all stated finite
domains and negative controls pass. The inherited real theorem and both
of its premise checkers remain credited to #845. See PROOF.md,
RESULTS.json, INDEPENDENT.json and VALIDATION.json.

Result artifact: [research/p112-complex-single-lift](https://github.com/woklerx/integer-mult-bounds/tree/research/seed40-complex-domain/research/p112-complex-single-lift).

The final Curiosity Bot refresh covered the twelve newest PRs through
**#991**, plus all-state searches for `P112 complex` and
`single-lift complex`. The former returned #620/#717/#845/#968; the
latter #845/#256. No matching scalar-domain transfer was found in that
scoped coverage. #968 is now closed and addresses eight-term frame-pair
decoders, not this ninth-total mechanism. This is not a claim to have
audited every open PR. The issue page again showed only #650/#913 and
no pinned coordination issue, so this is the single local result update.

The final Git refresh observed main at
`8bddbee377e2f3ce1f1247196c4b290d55767d20`; the pinned #845 dependency
directory had no changes relative to the original base and the selected
kappa remained `1661960547713947/10^18`. The original base is retained.

Verification and packaging used the final part of the session: a full
relocated Python 3.11 optimized replay, three rejected file/certificate
corruptions, source binding, selected-record checks and whitespace review.
The result makes no new kappa or physical implementation claim.
