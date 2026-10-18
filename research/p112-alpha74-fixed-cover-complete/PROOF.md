# All directions for the fixed alpha74 cover

The canonical P112 geometry is the 112 doubled integer root vectors r_i and
leading-one labels l_i in F2^9 supplied by the pinned geometry.py. For a binary
space U, write L(U)={i:l_i in U}. For a characteristic-zero field K and h in
K^8, write Off(h)={i:r_i dot h !=0}. All transposes and pairings are ordinary.

Fix EXACTLY the seven-space U and four-space V whose complete root closures
are the U_roots and V_roots lists in retained PR3307-WITNESS.json. Their sizes
are 32 and eight; the closures are disjoint. The eight primitive normal vectors
h_j and distinct corresponding roots t_j are also that predecessor's data.
They are orthogonal, with Gram matrix 8I. No other covers are quantified below.

## The new statement

For EVERY ONE common set P of at most two of the 112 roots, the nonzero
qualifying directions are exactly

    {c h_j : c in K, c !=0, t_j in P}.

Here qualifying means rank_F2{l_i:i in Off(h) outside L(U) union L(V) union P}
is at most seven. Consequently their span has dimension exactly the number
of t_j in P, at most two. Among the 6,216 two-root cuts, the numbers with span
zero, one and two are 5,356, 832 and 28. Empty and singleton cuts follow too.
In particular, a sum of two different qualifying normal vectors need not be
qualifying, even though it belongs to their span.

PR3307 proved this eligibility rule only INSIDE its exhibited eight-normal
family. The new obligation is completeness over ALL h, including nonroot,
nonreal and algebraic directions. The original arbitrary-cover common-two
span-at-most-five question remains UNSETTLED. This fixed-cover theorem is
neither a universal proof nor a counterexample to it.

## Reduce the whole direction set to finite exact nullspaces

For every binary seven-space W, define

    S_W = {i:i outside L(U) union L(V) union L(W)}.
    N_W(P) = {h:r_i dot h=0 for every i in S_W outside P}.

Then the full qualifying set, including zero, is precisely the union of
N_W(P) over all binary seven-spaces W. If h qualifies, its residual labels
span a space of dimension at most seven, which extends to such a W. The
annihilation equations follow. Conversely those equations put every remaining
nonzero pairing inside L(W), so its label rank is at most seven.

Worker 3 suggested this reformulation during internal coordination, before
computation. It requires no classification of real hyperplane zero patterns,
root subsystems or Weyl chambers. The matrices defining N_W(P) have integer
entries. Their rational nullspace bases remain bases over EVERY
characteristic-zero K, by ordinary row reduction. Checking the rational
nullspaces therefore covers all the stated fields and directions.

The two-dimensional annihilator W-perp uniquely has a reduced binary basis
with pivots p<q. The first row is 2^p plus arbitrary lower bits; the second is
2^q plus arbitrary lower bits except bit p. There are

    sum_{0<=p<q<9} 2^p * 2^(q-1) = 43,435

such bases. The primary enumerator uses this form. The second enumerator
instead takes pairs 0<a<b<a xor b<512, the smallest two nonzero vectors of a
two-space. Both enumerate the SAME entire binary Grassmannian, including
spaces not spanned by their P112 roots. No root-closure deduplication is used.

## Find all relevant cuts without repeating 6,216 full scans

Let A have the rows r_i for i in S_W. For every one of the 43,435 W, the replay
finds rank 8 over F101. Thus rank_Q A=8, and N_W(empty)={0}. Independently,
the second checker proves this using F103 and a different row order.

Choose eight independent rows B over the prime field. Write each other row
as a linear combination of B. The resulting relations form a basis of the
left kernel H of A. In H the columns for nonbasis rows are signed unit
vectors, while a basis-row column consists of its coefficients in those
relations. Signs do not matter to the following projective comparisons.

Deleting D of at most two rows lowers rank over the prime field exactly when
H has a nonzero vector in its kernel supported inside D. Equivalently, D
contains a zero column of H or consists of two nonzero proportional columns.
To see this, extend a functional on the eight-dimensional column image of A
to its coordinates indexed by S_W. Its supported coordinate vectors are
precisely ker H. The support-one and support-two conditions are the stated
zero/proportional alternatives.

The primary checker constructs H from an incremental row echelon basis. The
second uses dense RREF of the transpose 8-by-|S_W| matrix, constructing every
left-kernel column directly. Both include every zero-column singleton,
EVERY pair containing such a singleton, and all pairs of proportional nonzero
columns. This includes modular false positives. Testing only the singleton
would be unsound: a rational two-row cocircuit can reduce to a modular
singleton. The concrete rows I8 plus (101,1,0,...,0) exercise that failure mode.

If deleting D lowers rank over Q, it lowers rank modulo the prime too, since
every 8-by8 minor of the deleted integer matrix vanishes. Hence the modular
candidate list cannot miss an actual rational rank drop. Each candidate is
then checked by exact rational elimination; a modular rank drop alone is
never accepted as a characteristic-zero kernel. Cuts involving roots outside
S_W have the same equations as their intersection with S_W and are covered
by this singleton/pair treatment.

## The exact finite receipt

Only eight of the 43,435 W have any modular candidate cut. All other W have
N_W(P)={0} for EVERY |P|<=2. Across the eight active spaces there are 320
candidate nullspaces after singleton supersets are included. Exact reduction
finds all 320 to be one-dimensional. They collapse to these eight records;
the listed required root is the sole nonzero pairing on S_W:

| Binary annihilator basis | Required root | Normal in predecessor order |
| --- | --- | --- |
|58,67|59|h_3|
|59,67|52|h_2|
|67,148|72|h_6|
|67,149|71|h_7|
|67,296|45|h_0|
|67,297|50|h_5|
|67,390|94|h_1|
|67,391|97|h_4|

RESULT.json gives the actual integer vectors, so this table has no hidden
normalization convention. For every candidate, exact elimination checks its
whole nullspace dimension and basis, not just membership of the proposed h_j.
Its sole nonzero pairing on S_W is r_{t_j} dot h_j. Thus each nonzero kernel
requires t_j in P, and the singleton removal already admits that line. The
finite-union argument proves the stated exact classification. Orthogonality
of the eight h_j makes every eligible subset independent over K. The cut
histogram is choose(104,2), 104*8 and choose(8,2).

## Scope, predecessor credit and open questions

This is a finite certificate with a written reduction to exhaustive linear
algebra. It does not generalize the fixed covers, normalize arbitrary covers,
exclude the historical 2^3,7^7 caller, prove full C5 or price a physical
program. Source authentication is not mathematical admission. No supplier,
restoration, consumer, all-size theorem, selected frontier or kappa changes.
Historical alpha74/capacity censuses, Lean, Docker, the selected cold replay,
and human/proof-kernel review remain unrun and are unnecessary to this exact
fixture theorem.

Credit Nick Petalas/PR3307 for the cover and eight-normal witness and its
quantifier warning; PR3289 for the motivating historical caller seam;
DreamingOfClouds/PR3154 for the alpha74 setting; the canonical PR3161/3162
root-label reconstruction and retained E8/P112 lineage including joaqcoo.
The predecessor's proof and witness are retained verbatim. Its other
conclusions remain its own. New source and proof are Apache-2.0.

Open next question: does the span-at-most-five theorem hold for arbitrary
U7,V4 and common|P|<=2? A useful first step is a cover-orbit reduction that
preserves this exact nullspace contract. This fixture does not supply one.
The family decision is to finish the explicit fixed-cover completeness gap
and stop; no new large census or construction round is justified here.
