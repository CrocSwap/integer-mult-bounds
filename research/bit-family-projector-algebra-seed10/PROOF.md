# Exact projector decomposition

## Scope

Fix PR #1351's pinned family role map and its two interval descriptions. The
claim here is only the finite address-operator identity for those maps. The
schedule reconstruction, family selection, scalar word, helper lowering and
supplier admission remain inherited obligations.

## Projectors

The selected line q has eight rational entries and q-transpose-q equals 4.
Its perpendicular projector is

    K = I_8 - q q^T / 4.

Thus K is symmetric, K squared equals K, q is in its kernel, and trace(K)=7.
For a host or remainder axes record, the ambient 64-dimensional projector is
K on the first eight coordinates when the full q-perp block is present, plus
the coordinate projectors for its external axes. The verifier establishes
these statements over rational numbers.

## Frozen interval decompositions

Child 0 has host axes `[1,2,3,4,5,6,7,8]`, remainder axes `[9,...,14]`, and
source axes `[1,...,14]`. The host projector is K plus the projector onto
coordinate 8. The remainder consists of the six coordinate projectors 9
through 14. Their product is zero in either order, and their sum is the source
projector.

Child 7 has host axes `[36,...,43]`, `[44,...,51]`, `[52,...,59]`, remainder
axes `[60,...,63]`, and source axes `[36,...,63]`. These four projectors are
coordinate projectors on disjoint axes, so every pairwise product is zero and
their sum is the source projector.

## Block identity

For projectors P and Q with PQ=QP=0, direct block multiplication gives

    D(P)D(Q)
      = [[I-P-Q+2PQ, P+Q-2PQ], [P+Q-2PQ, I-P-Q+2PQ]]
      = D(P+Q).

Induction gives the same result for any finite pairwise-orthogonal list. Since
the verifier checks that each interval's listed factors are symmetric
idempotents, pairwise orthogonal, and sum exactly to its source projector, the
entire 128-dimensional address operator equals D(source). Orthogonality also
makes the product independent of the order of those factors. No finite basis
replay is used in this implication.

## Controls and limits

The checker confirms that dropping child 7's last helper, changing child 0's
external host axis from 8 to 22 while preserving rank, or duplicating a helper
breaks the orthogonal decomposition. These controls cover the algebraic
certificate's exact target; they do not test the complete supplier pipeline.

The input `PR1351-RESULT.json` is pinned to the open PR head recorded in
`SOURCES.json`. This audit does not independently regenerate the PR's role map
or prove its chronology. The selected kappa and all source files remain
unchanged; no new exponent bound follows.
