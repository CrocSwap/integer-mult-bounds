# Positive-frame third profile: impossible for every power-of-two m

**Scoped written proof with exact finite corroboration. No κ change.**

This answers part of Open next question 2 of apoursh's PR6089
(`research/bit-positive-frame-use`). The question asks whether the third necessary
multiplicity profile $(0,1,3,3,m)$ occurs for any $m\ge2$. The model is PR6089's
formal PR2085/2112 four-target model: rank-one binary idempotent calls over
$\mathbb F_2[\Lambda]$, free $\operatorname{GL}_w(\mathbb F_2)$ mixing, exactly
restored dirty workspace and any finite width $w\ge4$. The profile is ordered as
$(F,F^\perp,G,H,R)$, with added frame $R=F/m$.

## Result

**Theorem.** If $m=2^k$ for some $k\ge0$, no exact word has the profile
$(0,1,3,3,m)$, at any finite width.

For $m=1$ this is PR6089's exclusion. For $m=2,4,8,\ldots$ it is new. Combined with
PR6089, the attained count profiles for these $m$ are exactly the two subdivision
profiles $(1,2,2,2,m)$ and $(0,2,2,2,2m)$.

**The idea.** Write $E_1,\ldots,E_m$ for the projectors of the $R$ calls, in word
order. Send $[R]\mapsto1+s$ and $[B],[P]\mapsto1$. Then $[A],[Q]\mapsto(1+s)^m=1+s^m$
over $\mathbb F_2$. The $s^m$ coefficient of the word is the single ordered product
$E_1\cdots E_m$ plus the three $Q$ projectors. PR6089's first-order $B$ character
gives a second equation. Together they give

$$N_B+E_1E_2\cdots E_m=\operatorname{diag}(1,1,1,1,0,\ldots,0).$$

The left side has rank at most 2, and the right side has rank 4.

[PROOF.md](PROOF.md) has the complete argument and scope. It also shows why the
argument stops when $m$ has an odd factor $o\ge3$: the $s^{2^k}$ coefficient becomes
an elementary sum of $R$ projector products, and its rank is not bounded by one.

## Evidence

[verify.py](verify.py) uses exact F2 and group-algebra arithmetic and needs only the
standard library. It checks:

- the pinned PR6089 proof bytes;
- the lattice identities, the determinant balance of the profile and both character
  value tables for $m=2^k$, $k=0,\ldots,10$;
- on 1,600 random profile words at $w=4,5$ and $m=1,2,4,8$, that the $[R]\mapsto1+s$
  image has $e_j(E)$ at every order $j<m$ and $E_1\cdots E_m+\sum N_Q$ at order $m$,
  and that the $B$ character has $N_B+\sum N_Q$ at first order;
- 72 checks that specializing the exact $\mathbb F_2[\Lambda]$ product equals
  specializing call by call;
- that both of PR6089's attained subdivision words equal $T_w$ exactly at $w=4,5$ and
  $m=1,2,4$ and satisfy the same coefficient equations. A mutated word is rejected;
- exhaustively at $w=4,5$, that $D_w$ plus any matrix of rank at most one has rank at
  least 3, which is the finite form of the rank step.

The random words corroborate the coefficient lemma but do not prove it. The proof
covers every $k$ and every $w$, and no bounded search is part of it.

## Reproduce

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/bit-positive-frame-third-profile/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/bit-positive-frame-third-profile/verify.py
python3.12 -B scripts/research_package.py --package research/bit-positive-frame-third-profile
```

Each verifier run prints `PASS_POSITIVE_FRAME_THIRD_PROFILE_POWERS_OF_TWO` in under
a second.

## Limitations

Only powers of two are settled. For $m=3,5,6,7,\ldots$ the profile is neither
constructed nor excluded. Nothing here changes PR6089's minimum $m+7$, its length
spectrum, the selected frontier or κ. No native implementation, independent human
review or formal-kernel check is supplied.

## Open next questions

1. **Is $(0,1,3,3,m)$ realizable when $m$ has an odd factor $o\ge3$?** Start at
   $m=3$. The two characters reduce the problem to $E_1+E_2+E_3+N_B=D_w$, which
   coordinate projectors satisfy, so a second-order character is needed. One example
   is $[R]\mapsto1+s$ with $[P]\mapsto(1+s)^c$ modulo $s^3$, or a map that sends
   $[R]$ to an $o$-th root of unity times $1+s$. Alternatively, search for an exact
   10-call word at $w=4$ under the three first-order constraints.
2. **Does a uniform obstruction exist?** A full exclusion would complete PR6089's
   profile classification. The blocker is the rank of the elementary sum
   $e_{2^k}(E)$ once $o\ge3$.

## Credit

This package was produced by Nick Petalas. apoursh's PR6089 supplies the model
reduction, the symmetries, the necessary profile list, the $B$ character and the
subdivision words, and poses the question. Cinna Davis's PR2085/2112 supply the
model and endpoint. Nick Petalas's PR2910 supplies the determinant method, and
PR6032 the support and first-order approach. The retained BIT predecessor lineage
carries over. New work is Apache-2.0.
