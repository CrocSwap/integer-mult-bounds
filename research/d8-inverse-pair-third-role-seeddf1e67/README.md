# A third dirty role does not reduce the D8 inverse-pair bill

## Result

In the formal group algebra `F2[D8]`, the three-role endpoint

```text
diag([r], [r^-1], 1)
```

has exact paid-call minimum four when the paid labels are the two reflections
`s,t` and arbitrary free scalar `GL3(F2)` maps are allowed between calls.
The direct four-call word remains optimal after adding a third arbitrary dirty
role. An exact rank bound excludes lengths zero through two; a complete census
of the 56^3 ordered three-call words finds no endpoint hit.

This is a scoped finite-algebra result. It does not improve the selected bit
supplier, price physical hosting of the third role, or change `kappa`.

## Model and complete paid bill

Index `D8=<r,s | r^4=s^2=1, srs=r^-1>` by `r^i s^e`, with `i mod 4` and
`e in {0,1}`. Define `t=r^-1s`; then `s,t` are involutions and `st=r`,
`ts=r^-1`. Work in the full group algebra `F2[D8]`, not a finite address
quotient. A paid factor on three scalar roles is

```text
F_g(N) = I + ([g] + 1)N,  g in {s,t},
```

where `N=u v^T` is any rank-one idempotent over `F2`, so
`u,v in F2^3 \ {0}` and `v^T u=1`. There are 28 such projectors and hence
56 distinct paid generators. All three input roles are arbitrary. The exact
diagonal endpoint restores the third role, and every paid factor is charged
once. No additional role, COPY, discarded output, or address operation is
available. Arbitrary interspersed scalar `GL3(F2)` maps are included: push them
to the right by conjugating each projector, then apply augmentation
`[g] -> 1`; because the target augments to `I`, the residual scalar output map
must be `I`.

The direct word is

```text
F_s(E11) F_t(E11) F_t(E22) F_s(E22)
  = diag([s][t], [t][s], 1)
  = diag([r], [r^-1], 1).
```

Its complete formal bill is four calls. A three-call word would save one
factor (25%) in this block, so the best-case budget justified searching exactly
three calls.

## Lower bound for the first three lengths

Use the left regular representation of `F2[D8]`; each role becomes an
eight-dimensional block, for a total dimension of 24. Write `L_g` for left
multiplication by `g`. Since each reflection is an involution, `L_s+I` and
`L_t+I` have rank four: each is a product of four disjoint transpositions over
`F2`. Thus the difference from identity of one paid factor is

```text
(L_g + I) tensor N
```

and has rank four. Multiplication by `r` or `r^-1` consists of two cycles of
length four on `D8`, so each of `L_r+I` and `L_(r^-1)+I` has rank six. The
endpoint difference is block diagonal with ranks `6,6,0`, hence rank 12.
For any matrices `A,B`, `rank(AB-I) <= rank(A-I)+rank(B-I)`. Therefore at
least three paid factors are necessary.

This makes length three the only unresolved length below the direct word. The
packed search checks every ordered triple from the 56 gates using exact
eight-coefficient group-algebra multiplication. A separate verifier repeats
the entire census with tuple-valued coefficients and direct group-law
convolution. Both report zero hits among 175,616 triples. Together with the
rank lower bound and direct word, this proves minimum four in the stated model.

## Reproduction

```sh
python3 -I -B research/d8-inverse-pair-third-role-seeddf1e67/search.py
# D8 inverse-pair W3 exact search: generators=56 triples=175616 matches=0 direct_calls=4

python3 -I -B research/d8-inverse-pair-third-role-seeddf1e67/verify.py
# PASS_D8_INVERSE_PAIR_W3 rank_floor=12/4 generators=56 triples=175616 matches=0 minimum=4 direct_control=pass omission_control=pass altered_rank_control=pass

python3 scripts/research_package.py --package research/d8-inverse-pair-third-role-seeddf1e67 --check-only
```

The registered replay requests Python 3.12. Local direct runs used CPython
3.14.7; the registered 3.12 replay is not claimed unless available in the
submission environment.

## Relation to prior work and limits

- PR #1881 (`5a51deaaab2746d42eddb454bbb968bda3af02cc`) establishes the
  two-role `diag([r],[r^-1])` minimum of four. This result adds a third
  arbitrary restored role and keeps the same noncentral endpoint.
- Discussion #1738 / PR #1742 establish an eight-call minimum for the
  three-role central endpoint `diag([z],[z],[1])` with `z=r^2`. The target,
  paid labels and word-length question here differ.
- PR #1443 concerns a two-role central endpoint `diag([r^2],[r^2])`.

The exact minimum concerns only the finite named formal alphabet. It does not
include native implementation/hosting of the third role or its recursive
charges, so it is not a bit-supplier construction or a new `kappa`. The task
record pins the selected frontier, current task catalogue and predecessors.
Prepared with substantial OpenAI Codex assistance; no independent human
review is claimed.

## Open next questions

Can a fourth arbitrary dirty role lower the four-call minimum for the same
inverse-pair endpoint and reflection alphabet? The dimension-five projector
count grows sharply; first apply the regular-representation rank floor and
estimate the complete length-three search. Any formal saving would still need
an added-role hosting and recursive-cost invoice.
