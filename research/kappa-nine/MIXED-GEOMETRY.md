# A local block decomposition and the two-regular-block obstruction

Ali Romman, with substantial OpenAI Codex assistance. October 13, 2026.
Apache-2.0. This work builds on Douglas Colkitt's `kappa-nine` investigation.

**Scoped negative result:** in uniform mode 3, at most one anchor block can
be regular. This excludes all 28 four-exception and all 21 five-exception
sets that survived `MIXED-RANK-TEST.md`. The seven six-exception sets and the
all-exception set remain open. These 49 patterns are regularity patterns inside uniform mode 3. They are
not the complete remainder-mode branches. Uniform mode 3 still has eight
open exception patterns, so it remains open, as do the other 102 complete
branch representatives. There is no new kappa.

The proof also gives a necessary local form for every anchor block. Its
restrictions split into two complementary idempotent parts. This form is
forced by the graph; it does not impose permutation covariance, a common
bilinear form, positivity, or a choice of scalar coordinates.

## Scope and notation

Use the pinned nine-point problem over Q. There are seven anchor planes
E_0,...,E_6 and one remainder coordinate. For every triple T, let

    P_T = A_T B_T,    B_T A_T = I_2.

For adjacent labels T,U, both B_T A_U and B_U A_T are zero. Adjacency means
that the triples intersect in one point. In uniform mode 3, the 42 Y labels
have no remainder coordinate in either factor. The other 35 variable labels
are X labels; this proof does not construct or constrain their extension.

Write the fixed Fano lines as

    012, 034, 056, 135, 146, 236, 245.

For a point p in {0,...,6}, let star(p) be the three anchor lines through p.
For z in {7,8}, the three labels

    C(p,z) = {(L minus {p}) union {z} : L in star(p)}

form a clique. Their common allowed support is the six-dimensional sum of
the planes in star(p). The six image columns and six dual rows are bases of
that support. Their projectors therefore sum to its identity.

Fix an anchor line K and its plane E. For p in K, define the singleton label

    S(p,z) = (K minus {p}) union {z}.

The other two members of C(p,z) are denoted N(p,z). Put a_T=A_T restricted
to the rows of E and b_T=B_T restricted to the columns of E. These are
2-by-2 matrices. Set

    D(p,z) = a_S(p,z) b_S(p,z),
    R(p,z) = sum over T in N(p,z) of a_T b_T.

The saturated clique identity gives D(p,z)+R(p,z)=I_E.

## The local decomposition theorem

**Theorem.** There are complementary idempotents C_7,C_8 on E such that,
for every p in K,

    D(p,z) = C_z,
    C_7 + C_8 = I_E,
    C_7 C_8 = C_8 C_7 = 0.

For singleton restrictions, the image of a_S(p,z) is im(C_z), and the
row space of b_S(p,z) is the row space of C_z. Both restriction ranks equal
rank(C_z). Each nonsingleton restriction in N(p,z) lies in the complementary
part: a_T=C_(15-z) a_T and b_T=b_T C_(15-z). In particular,

    rank(a_S(p,7)) + rank(a_S(p,8)) = 2,
    rank(b_S(p,7)) + rank(b_S(p,8)) = 2.

**Proof.** If p and q are distinct points of K, the allowed supports of
C(p,z) and C(q,w) meet only in E. The following pairs are adjacent:

1. S(p,z) and each member of N(q,z).
2. S(p,z) and S(q,15-z).
3. Every member of N(p,z) and every member of N(q,15-z).

Thus each global zero product for these pairs is a zero product on E.
The certificate checks all these pairs on all seven blocks. For the first
family, multiplication by the outer a and b factors gives

    D(p,z) R(q,z) = R(q,z) D(p,z) = 0.

Substitute R(q,z)=I-D(q,z). It follows that

    D(p,z) D(q,z) = D(p,z) = D(q,z) D(p,z).

Interchange p and q. The same products equal D(q,z), so D(p,z)=D(q,z).
Call the common value C_z. The displayed identity now gives C_z^2=C_z.
The second edge family gives C_z C_(15-z)=0 in both orders. The third gives

    (I-C_z)(I-C_(15-z))=0.

Expand this product and use C_z C_(15-z)=0. Then C_z+C_(15-z)=I.

The first edge family also gives R(q,z) a_S(p,z)=0 and
b_S(p,z) R(q,z)=0. Hence C_z a_S(p,z)=a_S(p,z) and
b_S(p,z) C_z=b_S(p,z). Since a_S(p,z)b_S(p,z)=C_z, these inclusions are
equalities of image and row spaces. The restriction ranks equal rank(C_z).
For T in N(p,z), use S(q,z), with q distinct from p. The first edge family
gives C_z a_T=0 and b_T C_z=0, which proves the complementary support
statements. The two rank sums follow from the direct sum of the images of
the complementary idempotents. This proves the theorem.

The argument works over any field. The package states the application over
Q and uses rational controls. A finite-field experiment is not used to
infer the result.

## Why two regular blocks are impossible

A block is regular when all its 18 allowed Y restrictions have rank one
for both A and B. The source line-alignment argument applies to each such
block. The graph of sole-common-block edges is connected and bipartite;
its two image lines are distinct, and the two dual lines select the same
coordinates. In each C(p,z), exactly one label uses one line on the block;
the other two use the other line. The singleton is S(p,z).

Take any two regular blocks E_r,E_s. Their anchor lines meet at a point p.
Let E_k be the third block in star(p). For each z in {7,8}, apply the
complementary-block lemma from `MIXED-RANK-TEST.md` to C(p,z), with the
label T_z=S_k(p,z) singled out on E_k. The lemma only needs the other two
blocks to be regular. It does not require a rank assumption on E_k.
It gives

    rank(A_Tz restricted to E_k) = rank(B_Tz restricted to E_k) = 2.

For completeness, concatenate the three A factors on their common support
into a 6-by-6 matrix A, and stack the B factors into B. Then B=A^{-1}.
Order E_k and T_z first. The two regular blocks have distinct singleton
labels among the other two labels. Their singleton rows and their rows on
the other regular block are independent. The corresponding B columns are
independent as well. This follows from the saturated clique identity: a
singleton diagonal entry is 1 and its off-diagonal entries are zero.
Thus the lower-right 4-by-4 blocks of both A and B are invertible after
permuting rows or columns. The block inverse formula forces both upper-left
2-by-2 blocks to be invertible. This is the source lemma; no stronger form
of it is assumed here.

Apply the local decomposition theorem to E_k. The two displayed A ranks
must sum to 2, but the complementary-block lemma makes their sum 4. This
is a contradiction. The B ranks give the same contradiction.

There are 21 unordered pairs of anchor blocks. The certificate gives the
common point, third block, two forcing labels and two clique witnesses for
each pair. It also checks the required singleton colors. Therefore no two
regular blocks can coexist.

For example, choose regular blocks 5=236 and 6=245. Their common point is
2, and the third block is 0=012. The labels 017 and 018 would both have
invertible restrictions on block 0. The local rank sum forbids this.
An equivalent zero-propagation proof uses the clique {027,357,467}:
018 forces the 027 restriction to vanish on block 0, and 017 forces the
357 and 467 restrictions to vanish there. Their clique identity cannot
then equal I on that block.

## Complete coverage of exception sets

The new argument excludes every exception set with at most five elements.
Here an exception means a block that is not regular, including a zero
restriction. This does not mean that every restriction on that block has
rank zero or two.

| Exception-set size | Source survivors | Survivors after this proof |
|---|---:|---:|
| 0-3 | 0 | 0 |
| 4 | 28 | 0 |
| 5 | 21 | 0 |
| 6 | 7 | 7 |
| 7 | 1 | 1 |

The survivor counts describe necessary patterns, not matrix constructions.
The rank sum and local decomposition remain necessary in the last eight
patterns. This proof does not classify all their nonsingleton restrictions.
In particular, a rank-one local summand can contain a zero restriction;
rank-one complementary idempotents do not make a block regular.

## Cost at the frozen experimental base

The base is `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`. At this base, the
selected PR942 record has kappa=1661960547713947/10^18. Its complex coarse
endpoint is b=0.001664727258740678855772 and its bit endpoint is
c=0.001733427039589844234749. The exact base selection is saved unchanged in
`mixed-geometry-base-selection.json`. Its digest is checked without reading
the mutable live selection. The historical PR82 comparator in
`ASSESSMENT.md` is not the selected result at this base.

The changed block geometry can change the gross rank deficit. It is outside
the fixed E8 profile and owner restrictions. That is why this necessary
nine-point problem remains relevant. Its relevance does not supply a
complete improved construction.

The replay also checks the inherited optimistic dimension-15, rank-two,
16-point ledger with five roles per label on each axis. Its normalized
volume is W=12, parent dimension is 225, and its charged child counts are

    {4: 1, 26: 4, 30: 10+26/525, 169: 2, 195: 10}.

These charges include the proposed endpoint, both data calls, four growth
calls, central rank mass and both role boundaries. They grant ideal full
batching. They do not implement source access, copies, restoration, frame
changes, ordered recursive children, or the physical producer.

Exact integer-power enclosures give moment <1 at a=1/511, approximately
0.999957094. Since b<c<1/511 and every child is proper, this hypothetical
profile also has moment <1 at both frozen supplier endpoints. This is
headroom in the relaxed ledger only. At a=1/99 the same complete relaxed
profile has moment >1, approximately 1.003682180. Thus this specific
profile cannot reach kappa>0.01 under the inherited balance condition,
even before the unbuilt interfaces are supplied.

A bit-only improvement cannot move the frozen outer grid point if the
complex supplier stays fixed. Its necessary ceiling is b/(1+b), which is
strictly between the selected kappa and the next 10^-18 grid point. A useful
complete improvement needs a compatible complex supplier as well. A new
nine-point rational geometry must also extend to 16 points, have a compact
charged producer, and satisfy the copied/ordered transfer interfaces.
Changed maximum children require a new row-stock and finite-bridge check.

## Separate live-main refresh

During the sprint, main moved to
`ba82555c64e1879e4b7decce28186f208fcb8262` and selected Jeremy Kothe's
PR1042. The immutable selected record has
kappa=1672188119205421/10^18. Its assembly records
b=0.001674989015937672328468 and the unchanged
c=0.001733427039589844234749. These values were read from that exact Git
commit, after the experiment. They do not replace the experiment's base pins.

The same comparisons hold: b<c<1/511, and exact rational arithmetic gives

    1672188119205421/10^18 < b/(1+b) < 1672188119205422/10^18.

Thus a bit-only improvement with this complex endpoint cannot move the
next outer grid point either. The geometry theorem is independent of both
supplier snapshots. This refresh is context, not a new construction or an
adoption of PR1042 as an experimental dependency.

Sources at the refreshed commit:
[selection](https://github.com/CrocSwap/integer-mult-bounds/blob/ba82555c64e1879e4b7decce28186f208fcb8262/certificates/selected-result.json),
[assembly](https://github.com/CrocSwap/integer-mult-bounds/blob/ba82555c64e1879e4b7decce28186f208fcb8262/research/community-frontier1042-audit/ASSEMBLY.json),
and [review](https://github.com/CrocSwap/integer-mult-bounds/blob/ba82555c64e1879e4b7decce28186f208fcb8262/docs/research/community-batch1047-review.md).

## Reproduction and validation boundary

Run this command from the repository root:

    python3 -B -O research/kappa-nine/verify_mixed_geometry.py

Expected result: 7 local block certificates, 378 sole-common-block edges,
21 excluded regular pairs, 49 new exception-set exclusions, 8 remaining
exception sets, 3 local rational controls and 7 rejected negative controls.
The replay also checks the exact relaxed moment bounds and current complex
ceiling. All checks use explicit exceptions and remain active under `-O`.

To rebuild the receipt without changing the saved one:

    python3 -B research/kappa-nine/build_mixed_geometry.py --output /tmp/mixed-geometry-certificate.json
    python3 -B -O research/kappa-nine/verify_mixed_geometry.py /tmp/mixed-geometry-certificate.json

The builder uses the source graph helpers. The replay imports none of them.
It reconstructs adjacency from the triples and support from the fixed
anchors. It checks all required edges, saturated cliques, graph connectivity,
singleton colors, all 21 pairs, and all 128 exception sets. It checks a full
42-label coordinate Y control. That control has no regular block and does
not include the X labels. Three rational block controls cover complementary
ranks (0,2), (1,1), and (2,0), including a non-symmetric rank-one projector.
They show that the isolated local equations are consistent.

The seven mutations test missing pair coverage, a repeated outside label,
a missing local edge, a wrong singleton, a wrong remaining pattern, a false
root interval and an omitted relaxed cost. Each must fail at its stated
mathematical or coverage check. This is finite verification of the proof's
combinatorial inputs and arithmetic. The algebraic proof is the argument
above, not a solver report or a finite replay of the full theorem.

The saved receipt and a fresh build were byte-identical. The optimized replay
passed on both the experimental checkout and an overlay of the pinned source
files from live commit `ba82555c64e1879e4b7decce28186f208fcb8262`. The overlay
had no live `certificates/selected-result.json`, which confirms that selection
changes do not invalidate the frozen-context check. Twelve predecessor tests
in `test_mixed_rank`, `test_local_rank`, and `test_geometry` passed. No existing
source or certificate was regenerated. Repository-wide `make verify`, full
supplier replay, hosted CI, and Lean were not run; this package changes no
emitted supplier or selected result.

## Selection, predecessor credit and limits

Three approaches were considered: propagate invertible restrictions and
zeros; derive a local form from saturated cliques; or construct exact factors
outside the parked private-coordinate family. The first probe gave a clique
capacity conflict. The second approach explained it with complementary
idempotents and an exact rank sum. These two approaches combine into the
proof above. No nonlinear solver or randomized search was used. The domain
is all rational factor matrices in uniform mode 3, and the finite coverage
is all seven anchor blocks and all 21 regular pairs. The stopping rule was
a proof with complete pair coverage and exact replay. The one-regular
private-coordinate sweep was not restarted.

The source complementary-block proof and its local rational control are
Douglas Colkitt's work. PR1066 by `woklerx`, at commit
`2e72784a7908d45511e953c182d42cdcb911e6cb`, independently verifies that
classical inverse-block obligation. The present result uses the source
lemma and adds the local decomposition and the 49 exclusions. It does not
claim that the inherited inverse-block identity is new. PR1066 was still
open at the final overlap check on October 13, 2026 at 18:28 UTC and is not a runtime dependency of this package.

The remaining six- and seven-exception cases are not solved. The earlier
103 complete branch representatives stay open. No selected certificate,
upstream source, supplier, full multiplication proof, or published PR is
changed by this package.
