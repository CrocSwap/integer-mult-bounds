## Summary

This package implements one authenticated selected MOVE, event24476 `[MOVE,727,3,470,false]`, as a literal Gamma6/HOME graph. Its exact map is `M_left C^tensor3 M_right`; the right monomial has output offset 5 and absolute phase 2. It also proves and implements generic fixed nine-coordinate monomial factors under explicit phase, prefix-integrality, signed-width, and supplied-owner promises.

## Uniform fixed-recipe composition

The reviewed appendix proves that every valid pair of fixed nine-coordinate monomials and every fixed central rank rho=1..9 admit the same flattened31-tape construction. The complete core bounds are `T <= 2^25(fV+E+1)` and incremental history `4096(V+E+1)`. The fixed-table HOME wrapper schema adds `128(F+1)` time and `64(F+1)` backing on35 tapes. Its stored API remains event24476-specific: no arbitrary-recipe dispatcher or additional physical execution is claimed. The actual rank-three event retains the tighter2048 core-history bound.

The common-root prefix corollary also identifies the exact sufficient row/view invariant from #7000 for completed Clifford prefixes; the selected producer and address view still have to supply it.

## Evidence

- The source archive is bound to canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, Git blob `74563a7867d9d762b6588f65362369668841bb3e`, compressed SHA-256 `2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883`, and canonical-word SHA-256 `91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097`.
- The exact independent kernel checker matches the direct source-frame Gaussian kernel for all 512 one-column basis inputs and 4,096 nonzero amplitudes. Its five orientation/order/phase/offset/central-sign negative controls reject.
- Root's separate sparse HOME replay checks a fresh `f=1`, `P=2`, `w=10` packet in 118,744,836 tape steps, with 20,496 late HOME writes, complete return and all 35 heads/private bodies/exteriors restored. The full reported cost and history ceilings are in `implementation/PROOF.md` and `review/root/ROOT-REVIEW.md`.
- Registered replays include author normal and `-O`, portable independent checker normal and `-O`, AST identity checks for all mathematical kernel/negative-control functions, and the root sparse machine review.

## Reproduction

```sh
python3 -B scripts/research_package.py --package research/literal-source-affine-move
```

The seven registered commands pass; expected frozen JSON receipts are packaged beside each checker. Metadata/pin validation is separate from mathematical review. No hosted CI or selected cold replay is claimed.

## Scope limits

This is a fixed-recipe direct leaf, not a full source dispatcher or selected caller. The proof assumes that the caller supplies a complete packet, correct six-Gamma header, owner entry, cutoff and numerical prefix promises. It does not establish that an actual selected producer supplies the required common-grid row, that B1 gathering/return/setup fit a faster recurrence, or that any selected framework assumption or kappa changes.

The event has both a multibit offset and nonzero phase, but #7000's retained source shows an earlier selected MOVE (event24472) already had both. The contribution here is the source-bound rank-three recipe and physical composition in the existing ABI, not “first nonzero offset/phase.”

## Related work and credit

The exact source family/all-column algebra and central fixed-rank service are retained from #7000 and #6978. The fixed offset and binary-map primitives retain #7428 and #7430. Upstream commit/blob pins and notices remain in `implementation/SOURCES.json`.

Prepared for @CubeJerry with substantial OpenAI ChatGPT/Codex assistance. Root's machine and source-kernel review are separately implemented but assess the shared proposed construction; this is not blind or human peer review, nor formal-kernel verification.
