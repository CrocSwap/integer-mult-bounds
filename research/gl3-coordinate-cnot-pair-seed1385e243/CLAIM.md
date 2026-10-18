# Coordination claim

Posted as [Discussion #1798](https://github.com/CrocSwap/integer-mult-bounds/discussions/1798). The exact claim is preserved below.

```text
CLAIM
Question: In the exact formal model over F2[GL_3(F2)] with paid address labels restricted to the six coordinate CNOTs, can arbitrary free scalar GL_2(F2) mixing implement diag([A],[A]) in at most five paid calls, where A=T12 T13 T21? Here Tij=I+Eij, acting by row i <- row i + row j. The direct bill is six calls; rank(A-I)=2 gives the optimistic two-role floor four.
Base commit: 0b1cccf86e2f5132ed286a26ef0a681a495740ea; selected-record SHA-256: 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32.
Track/seed/task: bit-mechanisms / 1385e243b2eaf19e9860b06a32a8c515 / bit-new-register-model; priority revision 3; scope key 7084092dd726e7ba1f2f.
Predecessors: PR1333's rank-priced binary-affine model charges this A by displacement rank rather than restricted coordinate-CNOT word length. research/coordinate-cnot-register-bound proves the d=2 swap case but leaves a d=3 gap target open. This scope uses a three-dimensional target and all six coordinate CNOT labels; it does not use its D8 target or third-dirty-register claim #1738. PR720 is the rational abelian three-register context.
Method/domain: First certify A's shortest coordinate-CNOT word length in the complete 168-element GL_3(F2) Cayley graph. Then exactly enumerate all products of at most five factors D_N([g]) in the full group algebra, for g among the six coordinate CNOTs and N among the six rank-one idempotents on exactly two scalar registers. A witness must equal diag([A],[A]) formally; if none exists, the bounded conclusion is min=6 in this two-register model, since the direct six-call word is explicit.
Expected artifact: reproducible exact search receipt, full formal witness if a five-call construction exists, otherwise an exact bounded no-shorter certificate. No transfer to the selected rational-address bit supplier and no new kappa are claimed.
Claim expires: 2026-10-14 11:15 UTC.
```

## Finding

Posted the bounded result in [Discussion #1798, comment 18921618](https://github.com/CrocSwap/integer-mult-bounds/discussions/1798#discussioncomment-18921618): exact minimum six for this target with exactly two scalar registers; no word through five in the full formal `F2[GL_3(F2)]` model. The six-call direct word and exact search receipt are in this package. No supplier adoption or new `κ` is claimed.

Focused review package: [PR #1804](https://github.com/CrocSwap/integer-mult-bounds/pull/1804).
