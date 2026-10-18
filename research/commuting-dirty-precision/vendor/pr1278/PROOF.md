# Squarefree interval matrices for the balanced dirty word

Status: all-size lemma with exact local checks; external review remains open.
No multiplication exponent, numerical implementation, or precision minimum follows.

## Statement

Let n >= 1. Use the exact PR628 balanced dispatcher, with distinct source x,
target y, and one distinct connector per depth. Factors A_0,...,A_(n-1)
are free noncommuting indeterminates. Each leaf is the ideal linear shear
`target += sign A_j source`. Every cut is a complete leaf boundary.

For every two cuts s,t, in either direction, every surviving monomial in
`P_t P_s^-1` uses each factor index at most once. The cuts may occur in
any order. Deeper connectors remain shared between siblings, as in PR628.
No allocation of fresh scratch per subtree is assumed.

Consequently, suppose actual factors are bounded linear endomorphisms of one
normed space, commute pairwise, and every subset
product, including the empty product, has operator norm at most G >= 1.
Put h=ceil(log2 n) and C=2*3^h. In the maximum joint-register norm,

```
||P_t P_s^-1|| <= C^2 G.
```

This replaces the generic `C^2 G^2` interval estimate from PR905 under
the additional commuting hypothesis. PR1244's noncommuting obstruction
remains valid. It contains a squarefree product in the wrong order.

## Prefix input

We use PR905 Section 1's free-algebra prefix lemma: every prefix and inverse
prefix has ordered squarefree monomials, with coefficient row sum at most C.
A suffix also has this property: it is the inverse of a prefix of the
inverse word. All statements include both signs.

For completeness, its induction uses four completed-child states and one
active child. Write B for the complete left product and A for the complete
right product. A completed child restores every deeper connector. Its outer
maps only add Bx to z or Az to y. A child never writes its source or reads
its target. Thus a new nontrivial product in a prefix or inverse prefix
only appends B to a right-child term or prepends A to a left-child term.
The supports are disjoint and ordered. The completed outer maps and their
inverses have coefficient row sum at most three. The leaf bound is two.
This gives C=2*3^h. The eight signed cases and their outer states appear
in the retained PR905 proof. We do not assume PR1085's sharper coefficient
claim for the displayed theorem.

## Two-cut induction

Write e_x,e_y,e_z for coordinate injections and their transposes for
coordinate projections. Products below act on column vectors. Chronological
execution is right-to-left matrix multiplication. Put

```
U = I + e_z B e_x^T,
V = I + e_y A e_z^T,
F = V^-1 U^-1 V U = I + e_y AB e_x^T.
```

U and V denote the completed child maps, not their expanded instruction
words. Let P_a denote any prefix of the expanded positive U word. Let Q_b
denote any prefix of the expanded positive V word. These operators act on
the shared deeper connectors too. They fix every external parent coordinate.
The displayed identity for F also proves the completed-map and restoration
claim inductively, starting from the one-leaf shear.

A prefix of the inverse U word equals `P_a U^-1` for a complementary cut a.
Similarly a prefix of the inverse V word equals `Q_b V^-1`.
Therefore the four phases of the positive parent have prefix matrices

```
phase 0: P_a
phase 1: Q_b U
phase 2: P_a U^-1 V U
phase 3: Q_b F.
```

These formulas also include child boundaries and the final boundary.
Changing a cut's boundary representation does not change its matrix.

Induct on n for *all ordered pairs of cuts*, including reverse intervals.
The leaf case consists of I and one signed shear. If both cuts lie in the
same phase, the completed prefix cancels. The resulting two-cut matrix is
inside one child, in either order, so the induction applies.

There are six distinct phase pairs. Adjacent phases give, respectively,

```
0 -> 1: Q_b (U P_a^-1)
1 -> 2: (P_b U^-1) (V Q_a^-1)
2 -> 3: (Q_b V^-1) P_a^-1.
```

Each parenthesized term is a child prefix, inverse prefix, or suffix.
The left and right factor sets are disjoint. The prefix input therefore
makes every monomial squarefree, even when a shared connector joins the
matrix product. Inverses reverse these products; the same argument applies.

For the first repeated family, phases 0 -> 2 give

```
I_02 = P_b (U^-1 V U) P_a^-1
     = P_b P_a^-1 + e_y A [e_z^T U P_a^-1].
```

The first term is a two-cut child matrix. The bracket is a row of a suffix
of U. It contains only squarefree left factors. The extra A contains every
right factor once. Their supports are disjoint. For the inverse interval,
interchange a,b and negate the rank-one term. The bracket becomes
`e_z^T U P_b^-1`, so the same reasoning applies.

For the second repeated family, phases 1 -> 3 give

```
I_13 = Q_b (V^-1 U^-1 V) Q_a^-1
     = Q_b Q_a^-1 - [(Q_b V^-1)e_z] B e_x^T.
```

Here x is external to the right child. The bracket is a column of a prefix
of the inverse V word, so it contains only squarefree right factors.
The extra B contains every left factor once. For the inverse interval,
interchange a,b and change the minus sign to plus. The same proof applies.

Finally, phases 0 -> 3 give

```
I_03     = Q_b F P_a^-1 = Q_b P_a^-1 + e_y AB e_x^T,
I_03^-1  = P_a F^-1 Q_b^-1 = P_a Q_b^-1 - e_y AB e_x^T.
```

P fixes the external y coordinate; Q fixes the external x coordinate.
Their source rows and target columns also remain identities. Each first
term joins disjoint factor sets; the added product AB is squarefree.

Addition and cancellation cannot create a monomial with a repeated index.
This proves the claim for every pair of cuts in the positive word.
Every interval of the negative word is the inverse of an interval in the
positive word. Since the induction includes both cut orders, it proves
both signs. All six phase pairs explicitly retain the shared deeper scratch.

## Norm and sufficient error transport

Before cancellation, the coefficient row sum in `P_t P_s^-1` is at most C^2,
by submultiplicativity of the two prefix bounds. Cancellation cannot increase
this sum. Commutation reorders each squarefree word into a subset product.
Substituting actual operators and applying the triangle inequality gives
`||P_t P_s^-1|| <= C^2 G`. No invertibility of individual factors is needed;
every leaf shear is invertible regardless of its coefficient.

This lemma alone does not certify actual rounded leaves. If one separately
has N ideal leaves, initial norm at most D, and a per-leaf error bound
`a*u*(M_actual+1)`, variation of constants gives

```
M_actual <= C G D + t(M_actual+1),   t=N C^2 G a u.
```

If t <= 1/2, this implies `M_actual <= 2 C G D+1` and final error at most
`2 N C^2 G a u (C G D+1)`. These are conditional sufficient bounds.
Compared with the original generic transport argument, one factor G drops
out. Source admission, internal leaf magnitudes, coefficient preparation,
rounding correlations and the complete implementation bill remain separate.
We do not substitute a new cyclic working precision or claim a new kappa.

## Attribution and limits

PR628 supplies the dispatcher; PR905 supplies the prefix and common-operator
lemmas. Credit Chafik Boukhalfa for both. Hanson Sun's PR1244 poses the
all-size interval question and gives the noncommuting obstruction. PR1085
sharpens the prefix coefficient but is not required by this norm estimate.
Gareth Davidson's PR877 supplies the predecessor error-transport context.

Prepared for Charles Bethin with substantial OpenAI Codex assistance.
The written induction is the all-size argument. Finite tests support it;
they do not constitute a proof-assistant or independent human review.
