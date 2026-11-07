# Displacement rank for all aligned pure hub idles

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This accompanies the shortest-root proof in the same research package. **No new κ.**

## 1. Exact model and result

Work over any field of characteristic other than two, including Q and C.
The exact executable fixtures use Q. There are k>=3 nonempty arms with disjoint private chain
coordinates and a shared two-dimensional hub H. Select one native query
per arm in chronological order. Its rank-one matrix x_i y_i^T is square
zero. Its hub factors u_i,v_i satisfy v_i u_i=σ_i in {+1,-1}; cross-arm
pairings come only from H.

Assume ACTUAL ordinary hub-only transport aligns ALL complete complementary
hub-idle projectors in one common gauge. Thus for one rank-one idempotent P,

    u_i v_i=σ_i P       for every selected arm.

This is stronger than alignment of only some pairs or image-only matching. Actual
ordinary maps have total endpoint identity and do not mix private chains.
When deriving this premise from a uniform bridge, evaluate S=1 AND all
stage variables D_i=1; abstract conjugacy alone is insufficient.

Let the full word have N rank-one factors I-2x_j y_j^T and equal -I on
all n inputs. Selected natives are square zero; the rank identity below
does not require the other factors' self-pairings to vanish.

**Theorem.** Let r count + to - transitions in the CYCLIC chronological
sign sequence, including the last-to-first edge (r=0 for constant signs).
Then

    N-n >= k-r >= ceil(k/2).

For n=G+2+e, where G counts full root query sites and e additional empty
spectators, N=G+h implies

    h >= e+2+k-r >= e+2+ceil(k/2).

For binary children, G counts root child groups, not the native
leaf count denoted by m in the price notes.

Subtracting e rank-one productive spectator credits leaves at least
2+k-r uncompensated thin charges under this target model. This counts
queries; it is not a complete price or κ result.

## 2. Universal displacement identity

Write X=[x_1 ... x_N], Y=[y_1;...;y_N], G=YX and
A=I+2 lower(G), using the strictly lower triangular part. Column actions
are chronological: factor N is on the left. Ordered multiplication gives

    product = I-2 X A^-1 Y.

Endpoint -I yields X A^-1 Y=I_n. The matrix Q=A^-1 YX is idempotent of
rank n: Q^2=Q by substitution; X is surjective and A^-1 Y injective. Hence

    rank(A-G)=rank(A(I-Q))=N-n.                 (1)

This is the displacement mechanism of the companion shortest-root proof.
The shared characteristic-zero framework is credited to
CrocSwap/integer-mult-bounds#6836.
The present application extracts an all-k principal rank bound.

## 3. Orientation of the selected block

Write P=a b with b a=1. There are nonzero α_i with
u_i=α_i a, v_i=(σ_i/α_i)b. Thus, for distinct selected arms,

    G_ij=v_i u_j=σ_i α_j/α_i.

Rescale x_i to x_i/α_i and y_i to α_i y_i. Queries are unchanged, and
G is conjugated by diag(α). Its selected off-diagonal entries become
σ_i, while selected diagonal entries remain zero. Chronological index
comparisons are unchanged by interleaved unselected queries.

The selected principal block B of normalized A-G is therefore

    B_ii=1,    B_ij=sgn(i-j)σ_i for i!=j.       (2)

The sign belongs to the ROW. Principal restriction and diagonal similarity
give rank B<=N-n. Set C=diag(σ)B. Its off-diagonal entries are sgn(i-j)
and its diagonal is σ_i, so

    C+C^T=2 diag(σ).

The right side has rank k; rank(C+C^T)<=2 rank C proves
rank B>=ceil(k/2). This basic inequality also holds for arbitrary nonzero
σ_i, by taking C=diag(1/σ_i)B. The exact formula below uses signs ±1.

## 4. Exact cyclic-sign rank

For z put p_0=0, p_i=sum_(j<=i)z_j and S=p_k. This is an invertible
change from z to p_1,...,p_k. Row i of C z becomes

    2p_i-S       if σ_i=+1,
    2p_(i-1)-S   if σ_i=-1.

Let t_i=i in the first case and t_i=i-1 in the second. Two t_i coincide
exactly for consecutive signs +,-. If l counts those transitions among
positions 1 through k-1, there are k-l distinct t values.

The forms 2p_t-p_k for 1<=t<=k-1 are independent in their own p_t
coordinates. The endpoint forms are -p_k for t=0 and +p_k for t=k;
these are dependent only when both endpoints occur, namely when
σ_1=-1 and σ_k=+1. Therefore

    rank C=k-l-1_{σ_1=-1,σ_k=+1}=k-r.

Since r<=floor(k/2), the previous bound follows. Alternating signs attain
ceil(k/2), proving sharpness of the PRINCIPAL-MATRIX bound, not existence
of a complete root attaining the query bound. Constant signs give rank k;
one nonempty + block and one nonempty - block give rank k-1.

## 5. Scope and evidence

Thin queries can be anywhere, and spectators do not change the selected
block. The theorem requires the stated actual ALL-alignment gauge and
all-column scalar endpoint. Alignment of only some pairs, coupling/chain mixing,
restricted-input ancillas, different spectator target credit, or an
unproved S-dependent carrier substitution are outside it.

The standard-library verifier checks every sign word of lengths 3 through
10, literal coupling factors and diagonal similarity, finite exact roots
for (1), sharp alternating examples, and hypothesis/overclaim controls.
The all-k statement rests on the proof, not a finite failed search.

Scientific base: 7c49fe32c55de02c2c873655c804b16e4c3fef0a.
The common-gauge argument follows the companion shortest-root proof in
this same package. Credit CrocSwap/integer-mult-bounds#6836 for the shared
characteristic-zero displacement framework; the companion proof records
CrocSwap/integer-mult-bounds#4666 and CrocSwap/integer-mult-bounds#5617
as earlier precursors. The present application extends the characteristic-zero
chain-root setting of DreamingOfClouds in
CrocSwap/integer-mult-bounds#6833. The new result is the exact cyclic-sign
principal rank and the all-aligned multi-arm query consequence.
No supplier realization, frontier change, independent human acceptance,
or proof-kernel formalization is claimed.
