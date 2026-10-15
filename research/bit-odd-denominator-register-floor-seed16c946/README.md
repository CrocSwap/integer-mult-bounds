# Extra registers do not reduce the odd-denominator call bill

**Exact scoped result:** for $W$ invertible data targets in address dimension $m$, the minimum is $mW$ rank-one paid calls when all frames and targets lie in one full odd-denominator lattice and each cleared target is invertible modulo two. The result permits any number of auxiliary scalar registers and arbitrary free scalar mixing. It gives no new $\kappa$ or physical supplier.

For three $3\times3$ data targets, the minimum is nine calls for any number of auxiliary registers in this model. The lower bound uses a square-zero augmentation of the formal additive group algebra and a matrix-rank argument. It allows any number of rational relations among the paid frames; the address alphabet is restricted to one common odd-denominator lattice.

The exact instance uses

$$
C_1=I_3,\qquad C_2=I_3+E_{21},\qquad C_3=I_3+E_{32},
$$

all with determinant one. Its nine-call column decomposition is replayed in the complete formal group algebra. In the general statement, a fixed odd $q$ clears the lattice $q^{-1}M_m(\mathbb Z)$ and each $qC_i\bmod 2$ must be invertible. The proof gives all auxiliary storage and free scalar mixing away, so an extra-register saving cannot occur inside this model.

This is an algebraic register-model contribution. The selected conditional result remains unchanged: there is no native supplier, recursive-hosting bill, precision result, all-size lift, or $\kappa$ improvement. Any larger-register call saving outside this theorem must use an even-denominator frame or a target singular after clearing the common odd denominator.

## Source and scope

Cycle seed `16c9467a282673c96099aae5db2415a9`; track `bit-mechanisms`; task `bit-new-register-model`; priority revision 4; exact base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Exact source pins and predecessor files are in [SOURCES.json](SOURCES.json); the task card, claim, and proof are in [TASK-CARD.md](TASK-CARD.md), [CLAIM.md](CLAIM.md), and [PROOF.md](PROOF.md).

The result extends the model domain left open by `bit-dirty-auxiliary-registers` (three data roles plus auxiliary storage), but does not imply that general rational or dyadic frames obey the same floor. The arbitrary-register one-relation lemma has a different hypothesis and proof method. PR #1974's `GL3(F2)` address census and PR #2027's `UT4(F2)` tariff use different address groups.

## Reproduce

From the repository root:

```sh
python3 -I -B research/bit-odd-denominator-register-floor-seed16c946/verify.py
python3 scripts/research_package.py --package research/bit-odd-denominator-register-floor-seed16c946 --check-only
```

The direct replay checks the exact nine-call formal word with no auxiliaries, one auxiliary, and three auxiliaries; the rank-nine data block; a deleted-call control; a rank-one frame mutation; an altered endpoint; and the even-determinant boundary. It also checks odd-lattice additivity, sampled rank-one idempotents, free-mixer rank preservation, and the even-denominator scope guard. The written proof establishes the uniform theorem; finite controls are supporting evidence.

## Open next questions

Can even-denominator address frames, such as dyadic frames, use auxiliary registers to beat $mW$ calls for the same data endpoints? Begin with one dyadic denominator and two explicit frame relations, then derive the complete dirty-input endpoint and paid bill before increasing the search. The blocker is the absence of a concrete exact word or a rank invariant that survives even-denominator frames.

## Credit

The three-register abelian bound, dirty-auxiliary result, arbitrary-register one-relation lemma, and related model distinctions are credited in the pinned source files. This package uses none of their checker implementations. Prepared for Cinna Davis with substantial OpenAI Codex assistance; no independent human review or proof-assistant formalization is claimed. Apache-2.0.
