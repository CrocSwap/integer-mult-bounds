# Independent check of #4610's warp-substitution claims on its emitted word

**Task:** independent-moment (independent check). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## The claim

intqwq's #4610 (head `4b4c75bc`, conditional κ 0.00302152) states that its emitted word:

- substitutes 34 of PR4470's 72 warp generators with other invertible binary maps, each transporting its declared input frame onto its output frame;
- relabels 422 scalar frames;
- keeps all 17,453 scalar opcodes, with their order and coefficients;
- pays 3,298 calls, 12 fewer than PR4470's 3,310.

#4610 certifies these claims in Lean shards. This package checks them independently in Python, against PR4470's word from main's pinned constructor and #4610's vendored emitted word (blob `79dad65b`, SHA256-pinned).

## Results

- **Warp maps.** All 72 bound G maps are invertible on F₂⁹, giving 512 distinct images. Each maps span(from_frame) **onto** span(to_frame). Exactly **34** differ from PR4470's maps, and op, lender and B_pos agree for all 72.
- **Scalars.** In both orientations, the **17,453 scalar opcodes and coefficients agree in order** with PR4470's, and exactly **422** scalar frame labels differ.
- **Paid calls.** Climbs drop from 3,302 to 3,290. With the 8 centre jobs, that gives **3,298 vs 3,310** paid calls.
- **Other events.** Adapters (448), warps (240), phases (10) and centres (8) keep their counts.

Together with my #4614 (endpoint frames and profile) and #4615 (raw crossing), every structural and arithmetic statement checked so far in #4610 holds.

## Verify

```text
python3 -B research/pr4610-warp-substitution-check/verify.py
```

The check takes about 2 s and uses the standard library only.

## Limitations

**Not covered:**

- the Clifford absolute phases and the monomial lowering of the changed maps;
- the 632-column symbolic endpoint identity;
- the outer-ledger checks;
- whether substituting generators of the free-group identity is admissible under the supplier contract.

## Open next questions

- **Absolute phases.** Check them for the 34 changed maps independently. First step: rebuild each K_G from its binary G via the transported-frame lemma's integer column formulas (`research/transported-warp-frames/PROOF.md`), and compare with #4610's bound operators.

Credit: intqwq (#4610), Cinna Davis (#4470). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
