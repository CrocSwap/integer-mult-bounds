# Shortest words for the braid endpoint 3214

Produced by Nick Petalas. Apache-2.0. A written argument plus an exact finite
census re-executed by [verify.py](verify.py). It is not a proof-kernel
certificate or a physical caller invoice.

## Setting

The setting is the one of unpaidmoon's PR6642. K is a field, A=K^2, U is the
12-dimensional space of ordered pairs e_(i,j), i≠j in {1,2,3,4}, with
σ·e_(i,j)=e_(σ(i),σ(j)), and [σ] acts on A⊗U as I⊗σ. Composition is
(ab)(i)=a(b(i)), and products of operators act rightmost first, so
[a][b]=[ab]. With s=(1 2), t=(2 3), u=(3 4), the target is T=[w] with
w=sts=tst, one-line notation 3214. For a transposition r and an idempotent N
on A,

    D_r(N) = I + ([r] - I) N.

A paid factor is D_r(N) with r ∈ {s,t,u} and N of rank one. Write X'=I-X.
PR6642 proves that every word equal to T has at least six factors. Over F_q
there are n=q(q+1) rank-one projectors.

## Three identities, valid over every field

**(C) Conjugation.** [σ] D_r(N) [σ]^{-1} = D_{σrσ^{-1}}(N) for every
permutation σ, since I⊗σ commutes with N⊗I.

**(L) Line lemma.** Let Z be a rank-one projector and let every factor of a
product be D_{r_k}(N_k) with N_k ∈ {Z, Z'} and r_k an arbitrary transposition.
Each factor preserves (im Z)⊗U and (ker Z)⊗U. On (im N_k)⊗U it acts as [r_k]
and on the other summand as the identity. Hence the product equals
Z⊗π_L + Z'⊗π_M, where π_L is the ordered product of the labels of the factors
with projector Z and π_M that of the factors with projector Z'. If π_L=π_M=π
the product is the pure permutation [π].

The complement identity D_r(Z)D_r(Z')=[r] of PR6642 is the case of two
factors.

## Theorem

**(a) Every field.** Each of the following sixteen words equals [w] for all
rank-one projectors P, X, Y.

| pattern | word | free projectors |
|---|---|---|
| ssttss | s(P) s(P') t(X) t(X') s(Y) s(Y') | 3 |
| ttsstt | t(P) t(P') s(X) s(X') t(Y) t(Y') | 3 |
| sttsst | s(P) t(X) t(X') s(Y) s(Y') t(P') | 3 |
| tsstts | t(P) s(X) s(X') t(Y) t(Y') s(P') | 3 |
| sststs | s(P) s(P') t(X) s(X) t(X') s(X') | 2 |
| ttstst | t(P) t(P') s(X) t(X) s(X') t(X') | 2 |
| stssts | s(P) t(P) s(X) s(X') t(P') s(P') | 2 |
| tsttst | t(P) s(P) t(X) t(X') s(P') t(P') | 2 |
| ststss | s(P) t(P) s(P') t(P') s(X) s(X') | 2 |
| tststt | t(P) s(P) t(P') s(P') t(X) t(X') | 2 |
| ststst | s(P) t(X) s(X) t(X') s(X') t(P') | 2 |
| tststs | t(P) s(X) t(X) s(X') t(X') s(P') | 2 |
| ststts | s(P) t(P') s(P') t(X) t(X') s(P) | 2 |
| tstsst | t(P) s(P') t(P') s(X) s(X') t(P) | 2 |
| sttsts | s(P) t(X) t(X') s(P') t(P') s(P) | 2 |
| tsstst | t(P) s(X) s(X') t(P') s(P') t(P) | 2 |

Here r(Z) abbreviates D_r(Z). Each free projector occurs literally at a fixed
position, so each parametrization is injective, and distinct label patterns
give disjoint families. Over F_q the families contain exactly
4n^3+12n^2 distinct words, n=q(q+1).

**(b) Finite fields F2 and F3.** Every six-factor word equal to
[w] lies in one of the sixteen families. So the number of shortest words is
1296 over F2 and 8640 over F3, in both cases 4n^3+12n^2. The verifier
accepts other primes as an opt-in run; no such run is claimed here.

**Corollary (every field).** Every tight two-factor suffix allowed by the
PR6642 peel table extends to a shortest word. The suffix r(P') r(P) occurs in
the family ssttss or ttsstt, and r'(N) r(P) with r≠r' in {s,t} occurs in
tsstts or sttsst, whose last two projectors Y' and P' are independent.

Part (b) is an exhaustive computation, not an all-field theorem. Whether the
families are complete over every field is the first open question in the
README.

## Proof of (a)

Each word is rewritten to [w] by two moves. A contiguous block whose
projectors all lie in one pair {Z,Z'} and whose two line products agree is
replaced by the pure permutation [π] given by (L). The pure permutation is then
moved to the right end through the remaining factors by (C), which changes
their labels to other transpositions but keeps their projectors. Repeat until
no factor remains and compare the accumulated permutation with w.
`reduce_certificate` in verify.py performs exactly these moves on the symbolic
words and checks the final permutation. Every move is a field-independent
identity, so the check proves (a) for every field.

Two hand evaluations show the pattern.

* s(P) t(X) s(X) t(X') s(X') t(P'). The middle block lies in {X,X'} with
  π_L=π_M=ts, so it is [ts]. By (C), [ts] D_t(P') = D_{(ts)t(ts)^{-1}}(P')[ts]
  and (ts)t(ts)^{-1}=tstst=s by the braid relation. The word becomes
  D_s(P)D_s(P')[ts]=[s][ts]=[sts]=[w].
* s(P) t(X) t(X') s(Y) s(Y') t(P'). The two inner pairs give [t][s]=[ts]; the
  same conjugation turns the last factor into D_s(P'), and the word is again
  [s][ts]=[w].

## Proof of (b)

Two independent engines enumerate words over F_p. Operators are stored as
elements Σ_σ M_σ⊗σ of M_2(F_p)[S_4], and every equality test uses the exact
24×24 operator on A⊗U, the equality notion of PR6642.

1. **Tight-peel search.** With φ(M)=dim H-dim(H∩M^{-1}H), H=A⊗U+, PR6642
   shows φ is subadditive and φ(D_r(N))=1. The verifier recomputes φ(T)=6 and
   φ=1 for every factor of the field. If a word f1⋯f6 equals T, then for each
   k the right prefix W_k=f_{7-k}⋯f6 satisfies φ(T W_k^{-1}) = 6-k, since
   otherwise the remaining factors could not supply the missing defect. The
   search therefore keeps only tight peels, and a word is accepted only when
   the final remainder is the identity operator.
2. **Unpruned join (F2, F3).** All three-factor products are tabulated. Every
   factor is an involution, so f1⋯f6=T exactly when f1f2f3 = T f6 f5 f4. This
   join uses no defect argument.

Both engines return the same word set, and it equals the union of the
families. Its size is checked against 4n^3+12n^2.

## Limits

Completeness is proved only over F2 and F3. Spectator
elimination (JoyboyBrian PR4765), the length bound and the defect (PR6642,
PR6449) are inherited and not replayed. Scalar conjugation is algebraic, not a
physical basis change. No caller, tape, precision, stock or compiler cost is
priced. The selected conditional value 781451/250000000 is unchanged and all
five framework assumptions remain.
