# Relative defect rank at a negative identity endpoint

Work over a characteristic-zero field. Set every body variable to one
and evaluate the formal central parameter q at +1 and −1. On each
of the retained 36-role Type A and B ports, the exact target evaluates
to $F_+=I$ and $F_-=-I$. An exact formal endpoint must satisfy
these two evaluations.

## Relative factors and slack

Write chronological factors as $A_i^+$ and $A_i^-$, acting on
columns. Put $P_{i-1}=A_{i-1}^+\cdots A_1^+$ and
$D_i=(A_i^+)^{-1}A_i^-$. Applying the product rule to the two phase
prefixes gives

$$
F_+^{-1}F_-=G_m\cdots G_1,\qquad G_i=P_{i-1}^{-1}D_iP_{i-1}.
$$

A q-even invertible factor evaluates identically at the two phases.
Its own relative factor is identity, though it can change later
conjugating prefixes. Thus arbitrary invertible q-even mixing within
one port is allowed. Conjugacy preserves determinant, defect rank and
the rank of $D_i+I$ restricted to the defect image.

Assume $G_m\cdots G_1=-I$ on an n-dimensional space. Let
$U_i=\operatorname{im}(G_i-I)$ and $W_i=\sum_{j\ne i}U_j$.
Telescoping the product minus identity gives
$V=\sum_jU_j=U_i+W_i$, since the left side is $-2I$.
Centrality of $-I$ permits a cyclic shift placing $G_i$ first.
For $x\in U_i$, the image $G_ix$ lies in $U_i$. All subsequent
factors change it only by vectors in $W_i$. The final value is
$-x$, so $(G_i+I)x\in U_i\cap W_i$. Consequently

$$
\operatorname{rank}\left((G_i+I)|_{U_i}\right)
\leq\dim(U_i\cap W_i)
=\dim U_i+\dim W_i-n
\leq\sum_j\dim U_j-n.
$$

By conjugacy, for every i this gives

$$
\sum_j \operatorname{rank}(D_j-I)
\geq n+\operatorname{rank}\left((D_i+I)|_{\operatorname{im}(D_i-I)}\right).
$$

At equality in the ordinary defect-rank bound, every $D_i$ must
act by negative identity on its own defect image.

## Type A

On four distinct roles a fixed J at body one applies the two signed
shears $y\leftarrow y+q^{-1}x$ and
$u\leftarrow u+\alpha_2qv$, where $\alpha_2=-1$.
With $N=E_{yx}+\alpha_2E_{uv}$, the phases are $I+N$ and
$I-N$. Since $N^2=0$, their relative factor is $I-2N$.
Its defect has dimension two, and it fixes its defect image.
The rank of $D_i+I$ on that image is two. Thus the required
total relative defect rank is at least $36+2=38$.

The 17 J blocks supply 34. Each of the four literal q-odd QUERYs
supplies one through its relative transvection. Every other retained
Type A factor is q-even at the two evaluations. Replacing any
nonempty QUERY subset by q-even ordinary work gives a sum below 38.
Of the 15 subsets, four leave slack one, six leave slack zero,
and five fall below ordinary defect rank 36.

## Type B

A fixed J on its active plane has phase matrix
$\begin{pmatrix}1&-q\\q^{-1}/2&1/2\end{pmatrix}$.
The relative block is $\begin{pmatrix}0&1\\-1&0\end{pmatrix}$.
Both its defect and its plus-identity map are invertible on the
active plane. Its determinant is one and its defect rank is two.
The same inequality gives the minimum sum 38. The 17 J blocks
supply 34. The four IDLE_ODD factors each supply a sign flip,
with determinant −1 and defect rank one. Their demotion to IDLE_ONE
removes that contribution. Other retained Type B factors are
q-even at the two evaluations.

An odd number of demotions changes the relative determinant to −1,
excluding eight subsets. Demoting all four leaves defect rank sum
34, excluding one. Demoting two leaves defect rank sum 36,
but saturation would require every J to act by negative identity
on its defect image. The quarter-turn contradicts this condition,
excluding six subsets.

These are necessary endpoint obstructions under the pinned per-port
hypotheses. Changing a J, introducing a new q-odd factor, coupling
ports or enlarging the endpoint space changes the argument.
