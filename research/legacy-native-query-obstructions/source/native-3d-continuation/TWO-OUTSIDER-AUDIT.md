# Independent two-outsider proof audit

Audit date: 2026-10-12. A read-only review of TWO-OUTSIDER-PROOF.md
found no gap in the stated lemma or its stated lane applications.
No search was run, and no new agent was used.

## Subgroup coefficient comparison

Every native factor is invertible because its control is a constant
binary idempotent. Native words, their inverses, and the endpoint
I+(z-1)D augment to identity. Since z belongs to H, the matrix
K=U^-1 T_D Y^-1 is supported in H and augments to identity.

In F_N(g)X=K F_M(h^-1), the selected left term has support in gH
and the selected right term has support in Hh^-1. Both sets are
disjoint from H because g and h are outside H. Projection onto the
H coefficients is a linear operation; the proof does not assume it
is multiplicative. It gives (I-N)X=K(I-M), regardless of overlap
between the two outside cosets. Augmentation then gives N=M.
No normality of H, relation between g and h, or centrality of z is
needed.

## Character and rank calculation

The character is applied only to the equality over F2[H]. It need
not extend to G. In F2[C2], the elements 1 and t=s+1 are independent,
and t^2=0. Thus coefficient comparison in this basis is valid.

The images of X and K are I+tA and I+t(D+B), respectively. The
inverse H-words contribute the same active-control sums because
the field has characteristic two. All matrix cross terms contain
t^2 and vanish; no DATA matrices are reordered.

Put V=I-N. The coefficient equation is VA=(D+B)V. It gives

    D=DN+VA+BV.

These are matrices over F2. The three ranks are bounded by one,
rank(A), and rank(B). Each character-active control has rank one,
so rank(A)+rank(B)<=k. Therefore p<=k+1. In particular, the term
DN has not been replaced by ND, and no D/N commutation is assumed.
There is no rank calculation over a group algebra or over the
dual-number ring.

With zero outsiders, the same character directly gives p<=k.
With one outsider, its selected term is supported in HgH, disjoint
from H. Vanishing of that term contradicts invertibility of the
outer words and the nonzero control. Thus p=3,k=1 needs at least
three outsiders.

## Exact control and dirty helpers

The p=1,k=0 control is valid. It uses z=S1S2 and H={I,z}, not
the current -I3 endpoint. Both flips are outside H, and their
common idempotent N gives F_N(S1)F_N(S2)=I+(z-1)N. It meets the
bound with equality and prevents an overclaim that every pair of
outsiders is impossible.

For restored dirty helpers, the only endpoint properties used are
H support, identity augmentation, and the binary rank p of D.
Orthogonality of D and commutation with the query controls are not
required. Free binary DATA changes must first be absorbed into
effective native controls. Initialized, discarded, and partial
helper contracts do not impose the same endpoint and are not covered.

## Lane consequences and closure

For a coordinate plane, the block subgroup contains the plane queries,
all coordinate flips, and z. Only the spectator flip has nontrivial
character. Any two query maps outside that subgroup are excluded
for rank-three production, even if they are distinct, non-unipotent,
or higher-rank ADDRESS updates. No bridge intersection proof is needed.

The upper-parabolic application requires one common spectator row
line, all remaining queries in that subgroup, and k=1. Positive
unipotents in the subgroup have spectator scalar one. This covers
the ongoing affine-triple families with their two dense bridges.
The corresponding lower-parabolic character gives the column version.

For elementary shears, each coordinate row-line subgroup contains
all queries except shears that receive into that row. Its only active
H query is the corresponding fixed coordinate flip. Each row thus
needs at least three positive shears. Each shear updates one row,
so at least nine positive shears and the three fixed flips are needed:
at least twelve native queries in this restricted lane. The column
version is also valid. General dense rank-one unipotents can affect
several row and column lines, so this counting argument does not
produce an unrestricted twelve-query bound.

All ongoing literal plane-plus-two-outsider and stated affine-plus-two
bridge families are now excluded by this lemma, including the pivotal
and even-pivotal reflection nominations. Their saved DATA blocks are
diagnostics, and no additional CPU search on them is needed. Other
families with at least three outsiders remain outside this conclusion.
No general eight-query or integer-multiplication lower bound is claimed.
