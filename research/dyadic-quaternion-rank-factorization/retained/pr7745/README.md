# An integral quaternion channel gap

A $2\times 2$ response matrix needs **two factorization channels over the
Lipschitz order** and **one over the dyadic quaternion order**. Its rank over
the rational quaternion division ring is one. This scoped proof answers
the integral-versus-dyadic part of RQ10 for one coefficient dictionary.
[Dugongue's RQ10, PR #5803](https://github.com/CrocSwap/integer-mult-bounds/pull/5803)

## Exact channel counts

Let $H=\mathbb Q+\mathbb Q i+\mathbb Q j+\mathbb Q k$, with $i^2=j^2=-1$
and $ij=-ji=k$. Write $L$ for the order with four integer coordinates and
$L[1/2]$ for its dyadic extension. The inner rank of $B$ over a ring $R$
is the least $q$ for which $B=P T$ with $P$ having $q$ columns and $T$
having $q$ rows over $R$. The order of multiplication matters.

Set $h=(1+i+j+k)/2$. Direct expansion gives

$$
B=\begin{pmatrix}
1+i & i+k \\
1+j & i+j
\end{pmatrix}
=\begin{pmatrix}1+i\\1+j\end{pmatrix}\begin{pmatrix}1 & h\end{pmatrix}.
$$

Since $B$ is nonzero, the outer product gives both dyadic inner rank one
and $\operatorname{rank}_H B=1$. The integral factorization $B=B I_2$
uses two channels.

To rule out one integral channel, assume $B=(p_0,p_1)^{\mathsf T}(d,e)$
over $L$. The first column forces $p_0$ and $d$ to be nonzero. The second
column gives $p_0(e-dh)=0$, so $e=dh$ by cancellation in $H$.
If $s=1+i+j+k$, then $is=js=ks=s$ modulo $2L$. Thus all four coordinates
of $2dh=ds$ have the parity of the coordinate sum of $d$. Since $dh$ is
integral, that sum is even. The squared norm $N(d)$, the sum of the four
coordinate squares, has the same parity and is even as well.

The norm is positive on nonzero quaternions and multiplicative because
$u\bar u$ is central. Both $p_0d=1+i$ and $p_1d=1+j$ have norm two.
Hence $N(d)=2$ and $N(p_0)=N(p_1)=1$. Conjugation gives an integral inverse
for $p_0$. This would put
$p_1p_0^{-1}=(1+j)(1+i)^{-1}=(1-i+j+k)/2$ in $L$, which is impossible.
The integral inner rank is exactly two. A nonzero matrix with one row
or one column always factors through one channel, so two rows and two
columns are the smallest dimensions for this gap.

## Ordinary coefficient operations

Use four rational lanes in the basis $1,i,j,k$. Left multiplication by $i$
maps $(a,b,c,d)$ to $(-b,a,-d,c)$, and left multiplication by $j$ maps it
to $(-c,d,a,-b)$. Applying $j$ and then $i$ gives left multiplication by
$k=ij$. The input to the one-channel response is

$$
z=x_0+\tfrac12(x_1+ix_1+jx_1+kx_1).
$$

For a query $Q$ that commutes with these ordinary coefficients, write
$w=Qz$. The two contributions are $w+iw$ and $w+jw$. The coefficient
dictionary uses signed permutations, additions, and one exact halving of
a four-lane field. For a faithful formal example, act identically on two
copies of the four lanes and let $Q$ exchange the copies. The ordinary
operators preserve the copies and their products with $Q$ exchange them,
so the odd response is determined separately.

The integral obstruction applies under the atlas's R03 hypotheses with
ordinary coefficients in $L$. Its odd-row argument forces
the coefficient matrix to factor through as many rows as the word uses
queries, including with feedback. The dyadic operations above specify the
response and channel factors. A physical query, exact halving on its
reached inputs, restoration, tape movement, and a complete caller invoice
remain open. The result establishes no multiplication exponent saving.

## Reproduction

Run from the repository root using CPython 3.12 and the standard library.
The local checks used CPython 3.12.15 on macOS arm64.

```sh
python3.12 -I -W error -B research/lipschitz-channel-gap/verify.py
python3.12 -I -O -W error -B research/lipschitz-channel-gap/verify.py
python3.12 -B scripts/research_package.py --package research/lipschitz-channel-gap
python3.12 -B scripts/check_research_commit.py --package research/lipschitz-channel-gap --check-source-history
```

The checker compares the signed-permutation formula with the literal
matrix on all eight rational basis inputs. It checks the 16 parity classes
and exhausts all 24 integral norm-two right divisors. Eight divide each
first-column entry individually, and zero divide both. The checker also
confirms the two-channel identity and detects the response change when
$ij$ is reversed. The written proof establishes the channel bounds. The
finite checks corroborate its witness and obstruction.

## Open next questions

- Determine when dyadic localization preserves rational quaternion rank
  for a general rectangular response. Start with column reduction over the
  Hurwitz order and track each denominator in the coefficient dictionary.
- Find a live boundary with the signed permutations and a commuting query.
  Start by naming the caller's input grid and pricing the four-lane half,
  source preservation and final scratch restoration together.

## Credit

This scoped proof and checker were produced by Nick Petalas. Dugongue's atlas
supplies the question, the odd-row lower bound and the split dyadic comparison.
The source is pinned at PR #5803 head `0acda5ab421d28b98fdf916968696c8f9453376f`.
[Atlas and predecessor credits](https://github.com/CrocSwap/integer-mult-bounds/blob/0acda5ab421d28b98fdf916968696c8f9453376f/research/frontier-mathematical-atlas/volume-algebra.md)

The Lipschitz and Hurwitz orders and their norm arithmetic are classical.
Machiavelo and Roçadas give the same nonassociate norm-two pair in the
remarks after Theorem 3.2. The contribution here is the response matrix,
its channel obstruction and its dyadic coefficient construction.
[Some connections between the arithmetic and the geometry of Lipschitz integers](https://www.cmup.pt/sites/default/files/2024-09/1201.5817v2.pdf)

Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
