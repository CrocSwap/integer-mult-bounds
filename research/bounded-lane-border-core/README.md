# A bounded-lane actual-inverse border core

**Constructive local interface and conditional precision theorem; no new κ.**

This continuation replaces a missing boundary Gaussian by a smaller, explicitly
declared productive domain. For L lanes it retains all L X inputs and L−1 Y
inputs per main pair, every native helper input, and one owned terminal field.
The terminal field is initialized and cleared; it receives no output credit.
There is no independent Y0 input to recover and no exact boundary provider.

Let A be block lower triangular, B its **actual** inverse, P the projection
onto all but the last lane, J its inclusion, and C(A)=PAJ. Then

```
E = [[A, 0], [P(I−B), C(B)]]
F = [[B, 0], [P(B−I), C(A)]]
EF = FE = I.
```

Principal compression is multiplicative and C(A)P=PA. These identities prove
the result for noncommuting payloads. Assign X_j grade j and Y_j grade j for
j≥1: every cross-role defect has positive grade. Neither Toeplitz structure
nor an entire boundary column B P0 is needed. See
[the proof and literal owned-field program](core/PROOF.md), especially §7.
The earlier full-domain version, which pays for an exact boundary, is retained
as a comparison and is not confused with this reduced-domain contract.

At the ideal round-three native specialization, the local invoice is

```
T = {4:56, 7:14, 8:94, 9:652, 17:224}
P = {1:4656, 2:920, 3:1386}
target = L*T − 112 H17; paid = L*P.
```

At C=17/5000=.0034, rational enclosures prove that L=66 has margin
`[5.551473221217, 5.551473223332]`, while L=65 fails. This is a **local
screening inequality**, not an implemented recursion or bound. All 112 missing
rank-17 targets are removed from the input/output contract before crediting
outputs; they are not discarded arbitrary data.

A [separate precision theorem](precision/README.md) gives O(e) exact
denominator and intermediate-magnitude height for a fixed finite recursive
template with a compatible homogeneous endpoint expansion and fixed grades.
Its cancellation condition permits temporary reverse shifts. One outer
dyadic scaling recovers the Gaussian diagonal on a single common grid.
The preferred [exact Walsh extraction](precision/EXTRACTION.md) instead uses
K=2^ceil(log2(H+1)) complete root executions and dyadic averaging, avoiding
scale-dependent input magnification. K is charged once for fixed H; it is
not inserted at every child return. Input copies receive no productive credit.
Endpoint triangularity alone is insufficient: a checked fixed-template
example has height-one endpoints but needs e² numerator bits.

## Open next questions

1. **Actual native shears.** The core requires U(A) and L(−A⁻¹) at the
   declared native price, with all helpers, frames and both fresh D factors.
   A full native word and its actual inverse do not automatically have these
   ports. The [explicit inverse-correlated counterexample](native-gates/BOUNDARY-CONTRACTS.md)
   exhibits a positive-grade residue becoming grade zero. It is an abstract
   interface example, not a replay of a fault in the retained native word.
   First bind one literal forward/backward native pair to the proposed algebra.
2. **Whole-job recursive matching.** Prefix compression changes graded role
   populations. Formal repetition obeys d′_h=d_h+d_(h−1); it does not establish
   a fixed native interface family or preserve the L=66 invoice at every level.
   All Pascal sources, exits, complements and adapters must be constructed and
   priced. The independent review explains why polynomial role growth alone
   is insufficient. Start with one literal matched caller, not another scalar
   crossing calculation.
3. **Physical and outer admission.** Bind the proved precision premises to
   that caller, then charge scalar work, owned fields, routing, stock and BIT
   transfer. Unknown costs are not zero. The exact boundary-provider issue of
   the full-domain comparison is removed only for the reduced-domain variant.

## Verification

From the repository root:

```
python3 -I -B research/bounded-lane-border-core/verify.py
python3 -I -O -B research/bounded-lane-border-core/verify.py
python3 scripts/research_package.py --package research/bounded-lane-border-core
```

The runner authenticates declared live inputs, recounts the source profile,
checks the exact operator identities and local rational invoice, and runs
separately written [independent matrix and invoice checks](independent/REVIEW.md).
No predecessor scientific verifier is imported. The source census is not a
new native phase/all-column replay. [VALIDATION.md](VALIDATION.md) records
commands, environments and the precise limits of review.

## Assignment and credit

This is the user's requested continuation of the two-full border, a recorded
scope change from the rank-shape card. Base: canonical main
`f259dabc7d70e0db8d6d36bfda888f008bbfecc1`; priority revision 7. The selected
conditional κ=.00302015 is unchanged. The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/4611#discussioncomment-19129674)
records the expansion decision and [OVERLAP.md](OVERLAP.md) the bounded checks.

Predecessors: Yiyang's [paid-precision and inverse-interface PR4966](https://github.com/CrocSwap/integer-mult-bounds/pull/4966)
and [formal/triangular continuation](https://github.com/Lyy-iiis/integer-mult-bounds/tree/9fec4899e332d8a2afc928dd4cfb59ee8925a096/research/border-interface-continuation);
Dillon/#4623 for border/recovery work; Cao Yifan/#4610 for the exact
round-three native word; Jacob Alan Sussman and the finite-precompiler
contributors; the semantic bulk/precision source credited by
FINITE-TEMPLATE-CLOSURE; Cinna Davis/#4983 for the shared-additive-potential
boundary and #4998 for the distinct compensated-prefix pair. Retained
native/Clifford, helper, outer and AI-assistance notices remain applicable.
The block identities and standard character-averaging technique are not
claims to invent those general methods.

Prepared by Yiyang (@Lyy-iiis), with substantial OpenAI Codex and parallel-agent
assistance in research, proofs, implementation, review and writing. Apache-2.0.
Separate-agent review is not independent human or proof-assistant acceptance.
