# No ten odd-step covering word on five sources

This supplement closes the higher-application gap in PR1518's price argument.
It does not change Riquelme Soares's six-million-word census or its source pins.
Prepared by Douglas Colkitt with OpenAI Codex assistance; Apache-2.0.

A universal paired-readout schedule must realize every vector of F₂⁵ as a
pairwise difference of its boundary prefixes. If every step has odd Hamming
weight, each step changes parity. A restored ten-step word consequently has at
most five distinct even prefixes and five distinct odd prefixes (the last
prefix repeats the first). Choose linear coordinates identifying the parity
kernel with F₂⁴, and the odd coset with another copy of F₂⁴. Let A and B be the
sets in these two copies. Their differences cover the whole group only if

    (A + A) ∪ (B + B) = F₂⁴,   A + B = F₂⁴.

Here addition is XOR. If either set has fewer than five points, enlarge it to
five: this can only add differences. It is therefore enough to exclude every
pair of five-point sets.

An invertible affine map on F₂⁴, applied to both A and B, preserves these two
coverage conditions: its translation cancels from each pair sum, and its
linear part is a bijection. There are exactly two affine orbits of five-point
sets, represented by

    A₃ = {0,1,2,3,4},   A₄ = {0,1,2,4,8}.

One conceptual classification uses their affine-span dimensions. Dimension
four gives an affine basis. In dimension three, the complement consists of
three distinct points in an eight-point affine space; all such triples are
affinely equivalent. Five points cannot lie in dimension two.

The checker independently establishes this reduction by explicit orbit
closure. It uses translations and invertible coordinate additions, checks
each generator's bijectivity and affine identity on all sixteen points, and
obtains disjoint orbits of sizes 1,680 and 2,688. Their union is literally all
4,368 five-subsets of the sixteen-point space. For each representative it then
checks all 4,368 choices of B. Separate set-based and full 32-bit difference
calculations agree. The maximum total coverage is 30 for A₃ and 31 for A₄;
none reaches 32. The frozen full histograms are in `parity.py`.

Thus no restored ten-step odd-word can be universal, regardless of how many
weight-three steps it uses. This is stronger than the original census restricted
to one TRIO and twelve applications. It even permits odd weight-five steps in
the relaxation. It does not exclude even-weight or non-atomic instructions.

## Price consequence in the original contract

Counting pairs already requires at least nine calls for 31 nonzero masks.
Restoration makes the number of odd steps even. Excluding ten therefore gives
at least twelve calls. If at least one call is a TRIO, the total source
applications A = k + 2t are at least fourteen. Every source occurs positively
and evenly: absence would prevent that source's mask from being realized, and
an odd occurrence would fail restoration for independent source inputs.
Consequently the source cost is at least

    2 Σ λ_j + 4 min_j λ_j.

The known twelve-toggle word uses four applications of one source and two of
each other source. Relabel its repeated source to the cheapest one, giving
`2 Σ λ_j + 2 min_j λ_j`. Both schedules pay at least twelve frames, so for
λ_j > 0 and f ≥ 0 the TRIO schedule costs at least `2 min_j λ_j` more. For three
sources, pair counting already requires six calls; a TRIO gives at least eight
applications, while the six-toggle repair applies each source twice. The same
gap follows. These are statements about the stated paired-readout contract,
not all possible implementations of the multiplication algorithm.

## Verification

`python3 -B research/atomic-trio-connector/parity.py` checks the complete affine
orbit inventory, both independent difference computations, histogram mutation
controls, and the original twelve-toggle positive control. It also works under
`-O`. The registered replay retains the original six-million-word census and
adds this supplement. A finite executable proof is not a Lean formalization.
