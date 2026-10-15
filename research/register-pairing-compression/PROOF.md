# Retain the dirty pairing, not the entire dirty span

A rank-one word with a fully restored dirty complement can be compressed to
its active roles plus the rank of the pairing between its dirty column and row
spans. The construction preserves every ordered contraction over an arbitrary
unital F2-algebra. The proof is uniform in word length and finite role count;
the finite tests corroborate the implementation, not those quantifiers.

For the formal UT4 endpoint `diag([z],[uz],I_rest)`, the credited span bounds
then give at most `2+floor((L-13)/2)` roles for a word of length L. In particular,
the possible cost-25 improvement at prices `(a,b,c)=(1,3,1)` reduces to three
roles. This is a workspace reduction; existence of that improvement is open.

## General compression theorem

Let `E=H direct-sum K` be a finite-dimensional binary role space, with `dim H=h`.
Let R be any unital F2-algebra, possibly noncommutative. Consider an ordered word

```
W = product_(j=1..L) (I + lambda_j x_j y_j^T),
x_j,y_j in F2^r, lambda_j in R.
```

Binary scalars commute with R. Every original outer product is nonzero. Let
`u_j` be the K component of `x_j`, and let `v_j` be the restriction of `y_j^T`
to K. Put

```
U = span{u_j} <= K,  V = span{v_j} <= K*,
t = rank(V x U -> F2), (v,u) |-> v(u).
```

Equivalently, t is the rank of the L-by-L dirty contraction matrix
`M_ij = v_i(u_j)`. Spanning lists or bases give the same rank.

**Theorem.** There is a word W' on `H direct-sum F2^t`, using the same ordered
coefficient list and rank-at-most-one binary couplings, such that

```
W' = Fhat W Ghat,
Fhat = diag(I_H,F), Ghat = diag(I_H,G), FG=I_t.
```

Every scalar contraction `y_i^T x_j` is preserved, including `i=j`. If
`W=diag(T_H,I_K)` as a full matrix over R, then
`W'=diag(T_H,I_t)`. Delete zero outer products: every remaining factor belongs
to the arbitrary nonzero rank-one alphabet, in the original order, and every
label count weakly decreases. A label-dependent nonnegative price cannot rise.
No clean initial state, physical projection, COPY, ERASE, or executed F/G map
is used. The construction defines a different legal word.

**Construction.** Let `U_rad=U intersect ann(V)`. Choose a complement
`U=U_0 direct-sum U_rad`; `dim U_0=t`. Choose an isomorphism
`G:F2^t -> U_0 <= K`. On U define F to take the U_0 component to its G
coordinates, and extend F linearly to K. This is possible because U is a
subspace of K. Then `FG=I_t`. For every `u in U`, `u-GFu` lies in U_rad, so

```
vGFu = vu  for every v in V, u in U.                 (1)
```

The implementation chooses independent evaluation images of a basis of U to
obtain U_0, and solves a consistent binary linear system for each row of F.
It does not assume that an ambient coordinate projection has property (1).

Set `x'_j=Fhat x_j`, `y'_j^T=y_j^T Ghat`. The active components are unchanged,
and (1) gives

```
y'_i^T x'_j = y_i^T x_j  for all i,j.                 (2)
```

Expand any nonempty ordered subsequence `i_1<...<i_s` of factors. Its matrix
term is the ordered coefficient product `lambda_(i_1)...lambda_(i_s)` times

```
x_(i_1) (y_(i_1)^T x_(i_2)) ... (y_(i_(s-1))^T x_(i_s)) y_(i_s)^T.
```

All interior binary contractions agree by (2); the outer column and row are
exactly Fhat and Ghat applied to the original ones. No two coefficients in R
are interchanged. The empty term also agrees because `Fhat Ghat=I`. Summing
proves the full product identity. For a restored block-diagonal endpoint,

```
Fhat diag(T_H,I_K) Ghat = diag(T_H,FG) = diag(T_H,I_t).
```

This proves all target outputs, both off-diagonal blocks, and the identity on
every retained arbitrary dirty input. It is stronger than testing only H inputs
or only the active corner. Zero couplings give identity factors and may be
removed; a surviving outer product is rank one. Self-contraction is unchanged,
so an original idempotent (`y_j^T x_j=1`) stays nonzero and idempotent. An
original nilpotent stays nilpotent or becomes zero. Thus an alphabet restricted
to rank-one idempotents also stays legal, with no deletions. Other support,
geometry or native-operation restrictions need separate closure arguments.

**Scope of minimality.** If another factorwise replacement preserves all active
components and all contractions, its dirty contraction matrix is again M.
On d dirty roles that matrix factors through F2^d, so `d>=rank M=t`. The
construction therefore uses the minimum number of dirty roles for this exact
factorwise preservation requirement. This is not a lower bound for all words
with the same endpoint: changing the factor list can use less workspace.

## Why active-corner projection alone is insufficient

On one active and one dirty role take

```
N_1=e_active e_dirty^T, N_2=e_dirty e_active^T.
```

The active corner of `(I+A N_1)(I+B N_2)` contains `I+AB`, whereas both naively
projected couplings vanish. In `F2[UT4(F2)]`, `A=[a]+1`, `B=[b]+1` have nonzero
ordered product AB. Here t=1, which correctly retains the feedback direction.
The finite census detects every such failure among all 2,401 ordered pairs of
nonzero binary rank-one couplings on three roles with one active role.

Conversely, with two dirty directions, a row supported on the second and a
column supported on the first may both occur, with zero dirty pairing. Their
inverse-paired relator restores all inputs and compresses to no dirty roles.
Neither common block orientation need hold. This separates the new lemma from
the one-orientation hypothesis of PR1680. PR1541 restricts to an image span;
that space may still contain the radical eliminated here.

## UT4 application and inherited premises

Use the same formal alphabet as Nick Petalas's
[PR2175](https://github.com/CrocSwap/integer-mult-bounds/pull/2175):
`G=UT4(F2)`, `R=F2[G]`, `a=I+E12`, `b=I+E23`, `c=I+E34`,
`u=I+E13`, `z=I+E14`. A paid call is `I+([g]+1)xy^T` for `g in {a,b,c}` and
any nonzero binary rank-one coupling, including nilpotents. Every occurrence
is charged. Scalar GL mixing is optimistically free and normalized into the
couplings; augmentation makes any final scalar map identity. There are no free
address maps or initialized roles. All extra roles are arbitrary and restored.

Let H be the two active coordinate roles. For label g let X_g and Y_g denote
the spans of all coupling columns and rows. The PR2027 coefficient-span argument
and PR2175 mixed-middle argument give, uniformly in finite r and L,

```
H <= X_g, H* <= Y_g  (all six containments),
n_a >= dim X_a + dim Y_a,
n_c >= dim X_c + dim Y_c,
n_b >= dim X_b + dim Y_b + 1.                       (3)
```

These are credited inputs. For clarity, their mechanism is as follows. In the
retained degree-three quotient of the free algebra on A,B,C, the target has
coefficient `P=diag(1,1,0,...)` on ABC, ACB, BAC, CBA, and
`S=diag(0,1,0,...)` on AB, BA, ABA, BAB. First and last letters force the six
containments; first-degree coefficients give zero sums and the outer rank
inequalities. For middle calls, the transported-column/row matrices obey
`XY=0, UY=S, XV=0, UV=P`. Delete S's output coordinate by pi. The rank-one map
`pi P` factors through `ker X / im Y`, giving the extra 1 in (3). The quotient
homomorphism and earlier census are predecessor evidence, not newly replayed
by this package. Exact archived proofs retain their attribution and pins.

Define `e_g^x=dim X_g-2`, `e_g^y=dim Y_g-2`. They are nonnegative integers,
and (3) gives

```
sum_g(e_g^x+e_g^y) <= L-13.                         (4)
```

Because each X_g contains H, its projection onto K has dimension e_g^x;
similarly the dirty row projection has dimension e_g^y. Hence the combined
spaces U,V from the general theorem satisfy

```
dim U <= sum_g e_g^x,  dim V <= sum_g e_g^y,
t <= min(dim U,dim V) <= floor((L-13)/2).            (5)
```

The compressed full endpoint therefore uses at most
`2+floor((L-13)/2)` roles, and no larger label counts. This applies to every
length for which a word exists. It recovers two roles at L<=14 and gives three
at L<=16, four at L<=18, and so on. The bound is sufficient, not a claim that
all these role counts are necessary or that a word exists at each length.

## The precise fifteen-call handoff

The pinned [PR2314](https://github.com/CrocSwap/integer-mult-bounds/pull/2314)
result excludes fourteen-call five-b words on arbitrary dirty workspace.
Together with (3), it gives

```
n_a,n_c >= 4, n_b >= 5,
n_b=5 implies n_a+n_c >= 10.                        (6)
```

Its two exhaustive quotient censuses are inherited computer-assisted premises;
this package does not rerun or claim them as new evidence. Their public head
and exact proof are retained in SOURCES.json and sources/weighted-boundary.md.

At positive letter prices `(alpha,beta,gamma)=(1,3,1)`, the credited direct
word `abcbabcb` on z and `acbabc` on uz costs 26. Any cheaper word must have
`n_b=5` (six b calls already cost at least 26). By (6), the only cheaper counts
are `(6,5,4)`, `(5,5,5)`, `(4,5,6)`, all of length 15 and cost 25. Equations
(4)-(5) compress any such word to at most three roles. No factor can disappear:
that would create a cost at most 24 word contradicting (6). Thus each count
split is preserved exactly. A word using fewer than three roles can be padded
with an identity dirty spectator.

Consequently, a cost-25 word exists on any finite dirty workspace if and only
if one exists on exactly three roles in these three count splits. At five b
calls, (3) also forces both b spans to equal H, so every b coupling is supported
on the active 2x2 block. This extra restriction is necessary, not a construction.
A complete three-role exclusion would establish the exact cost 26; a survivor
must pass the full 64-element group-algebra endpoint. A quotient survivor or
finite sampled address test would not establish it.

## Evidence, credit and remaining scope

The general theorem above is elementary linear algebra; no literature-priority,
proof-kernel, independent human or independent-agent review is claimed. New
code constructs F,G, tests their full product identity, and separately evaluates
faithful dirty-input columns using literal 4x4 binary group multiplication.
The exact domains, digests, source bindings and deliberate failures are in
RESULT.json. All checks remain active with Python assertions disabled.

Credit CinnaDavis / 1337isnot1337 PR1541 for image-span restriction;
ToikY PR1662/1680 for UT4 span bounds and common-orientation compression;
Gareth Davidson PR2027 for mixed-root tariffs and PR2314 for the weighted
boundary; Nick Petalas / petalas PR2175 for the mixed-middle inequality;
Aaron Wang / navinor PR1690 for the inherited finite profile-screen method.
The PR2175/2314 proofs retain the earlier steph4n-gh, Arham Tahir and Hanson Sun
lineage. Only two actually used proof documents are archived; no predecessor
implementation or census package is copied.

The new contribution is the uniform pairing reduction and its missing-workspace
implication for the next weighted question. No fifteen-call census, optimum
outside the previously proved price cone, native/compiler realization, physical
supplier, precision/reserve theorem, all-size transfer, or new kappa is claimed.
Prepared by Gareth Davidson / @bitplane with substantial OpenAI Codex assistance.
Apache-2.0.
