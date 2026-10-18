# Scoped overlap and model audit

Reviewed at base `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe` by a separate
Codex research agent. This is an AI-assisted source and scope audit, not
independent human mathematical review.

## Evidence inspected

- The coordinator's 786-open-PR title/body snapshot, SHA-256
  `9315dea89e7fe7c2339ea1a9c213aa22de01603bcc0d7fc0748fbc7f166e2d9f`.
  Searches covered `masked`, `root-linear`, `bilinear`, `E-graph`, and
  decoder titles; relevant bodies were read. This does not inspect all
  code in every open PR and does not establish universal novelty.
- The coordinator's discussion snapshot, SHA-256
  `930b7951464c5934dec7ca32b847f78493a84bdcdecfe8f65b904b73fdf9ddc7`,
  contains the three starter discussions #1163/#1166/#1167 and no comments.
- Local PR968 and PR1077 proof, README, source records and relevant notices;
  the PR717 open body; the relevant PR620 decoder research files; and
  incorporated-head entries in the central ledger/disposition records.

## Closest predecessors and precise difference

| Predecessor | Pinned head | Relation |
|---|---|---|
| DreamingOfClouds, [PR717](https://github.com/CrocSwap/integer-mult-bounds/pull/717) | `4a97676294f9fa413b65986e9984fddeda71e4cc` | B14 label-pairing/decoder model, P112 floor research and P111/P104 examples. Its mixed-beta overcomplete problem is not closed by this package. |
| themilkman216, [PR968](https://github.com/CrocSwap/integer-mult-bounds/pull/968) | `6a99e7240b961ac5e115ae6aa0301ec7c4a45d77` | Exact **all-pairs**, eight-term real decoder floor and complete 1260-frame / 7168-decoder census. Its proof explicitly excludes E-graph-only exactness and nine or more terms. The new claim compares masked and all-pairs feasible products within an explicitly root-linear class. |
| woklerx, [PR1077](https://github.com/CrocSwap/integer-mult-bounds/pull/1077) | `1459f58a829e616ddf32a3da2782e166700e3218` | Arbitrary-complex extension of the eight-term all-pairs floor; explicitly excludes masked and overcomplete decoders. The new restriction is root-linearity of at least one factor, with the opposite factor unrestricted and arbitrary term count. |
| Josie Elliston, [PR1071](https://github.com/CrocSwap/integer-mult-bounds/pull/1071) | `ce9531beba1ce115fdcdc44925ded995a29b8bac` | Physical delivery lower bounds for specified frame-pair centers; does not decide the masked identity. |
| Ali Romman, [PR1125](https://github.com/CrocSwap/integer-mult-bounds/pull/1125) | `9f7c0679d64bab954b7161d8586dc626a59b92ee` | Asynchronous delivery bound across the 7168 mixed P104 decoders, with physical path restrictions; distinct from an identity constraint. |
| 3xcalibur-tech, [PR1171](https://github.com/CrocSwap/integer-mult-bounds/pull/1171) | `ab74c73b5b512f459b9be97680f41390d45a3bf3` | All-puncture root-only **star label-decoder** ratio exclusion and p=56 classification; a different decoder/cost model. |

The incorporated PR968 and PR1077 heads above come respectively from
`research/community-batch970-audit/DISPOSITIONS.json` and
`research/community-batch1099-audit/DISPOSITIONS.json`. The open heads come
from the coordinator's snapshot. Attribution also retains Joel Pulikkan /
GamingPuzzled PR620, icekylinx's P112 construction, and DreamingOfClouds PR595
as recorded in PR968/PR1077.

No matching masked, root-linear feasible-product rigidity result was found
among the inspected evidence. This is a bounded overlap finding.

## Model checks that materially affect the claim

1. The label pairing is `N_ij=(<r_i,r_j>+1) mod 2`. Thus the constrained
   entries are the **even** inner products, including diagonals. The odd
   inner-product entries have label pairing zero and are the potential
   cost-zero correction locations discussed by the predecessors.
2. Diagonals are essential: if only distinct orthogonal pairs were
   constrained, `M=I` would be a nonzero invisible bilinear form. A checker
   must include `(i,i)`, where `N_ii=1` and `(2G)_ii=4` for norm-two roots.
3. Use ordinary transpose over the complex numbers. Hermitian transpose
   is a different decoder model.
4. For arbitrary term count, at least one of `D=RA` or `T=RB` is an explicit restriction.
   Masked exactness does not establish it. Even an all-pairs product with
   more than eight terms can contain cancelling factors outside `col(R)`.
   The covariance proof strengthens the initial both-factor claim to this
   one-sided statement; the independent oracle checks its stronger local span condition.
5. Equality of the masked and all-pairs feasible products closes only the
   mask relaxation within this class. It does not prove the eight-term cost
   floor for nine or more terms, exclude unrestricted masked decoders, or
   construct/admit a physical supplier.

Recommended semantic controls are diagonal deletion (the identity matrix
survives) and an unrestricted label-orthogonal singleton correction outside
the root-linear class. These distinguish the claimed result from the two
most tempting overstatements.

## Pre-submission refresh

On 2026-10-13, immediately before submission, refreshed metadata contained 798 open PRs; main remained at the recorded base. The discussion board had one unrelated PR279 provenance claim. No matching masked-neighbour rigidity claim was found.

A new, complementary contribution is woklerx [PR1180](https://github.com/CrocSwap/integer-mult-bounds/pull/1180), head `75b408646d558147a4eb250fc407d1fbfcb8df4e`. Its proof and README were inspected: it extends the all-pairs copy floor to arbitrary term count when **both** factors stay in the root code, and explicitly excludes graph-only masked identities. Our contribution instead equates masked and all-pairs feasibility when **one** factor stays in the root code, using covariance and local spans. The results are distinct. We do not import, certify, or rely on PR1180's new cost theorem. The cancellation fixture used here has a transposed analogue in PR1180; it is a scope control, not a claimed new cancellation mechanism.

Refresh snapshot SHA-256: `bbe11beaa4062fb6faa2137ae1c7418d8d24e04b433a5cc06f450134c9a83a1c`.
