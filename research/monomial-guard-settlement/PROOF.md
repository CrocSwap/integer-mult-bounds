# Paying to separate the coordinates of a guard family

Work over a finite field $K$ of order $q$. A nonzero column $u$ and a row $v$ satisfy $vu=1$. Its guard tests all leading principal minors of orders $1$ through $m-1$ of the corank-one complement $G(I-uv)G^{-1}$. The full determinant is always zero. PR6710 treats a complete uniform header $G$ and asks what remains under monomial headers. We count free permutations and nonzero coordinate scalings, and charge one unit for each elementary addition $R_i\gets R_i+aR_j$, $i\ne j$, $a\ne0$. Choices may depend on the known input. This is a finite-field operation metric. Data movement, precision, inverses, selection and restoration in a physical caller are unpriced. [PR #6710](https://github.com/CrocSwap/integer-mult-bounds/pull/6710)

## What can a permutation alone accomplish?

The state transforms by $u\mapsto Gu,\ v\mapsto vG^{-1}$. On positions $S$ in a prefix, the principal determinant is $1-\sum_{i\in S}u_iv_i$, by the rank-one determinant identity. A diagonal change cancels in every product $u_i v_i$. Thus a uniform monomial header induces exactly a uniform permutation of the labeled coordinates. For any named subfamily, mark a proper subset $S$ allowed when none of its row sums is one. Set $F(\varnothing)=1$ and compute

~~~text
F(S) = [S is allowed] sum_{i in S} F(S without i).
~~~

The full set is always allowed in this recurrence because its minor is not tested. Each term fixes the last coordinate of an order. The exact joint probability is $F([m])/m!$. An empty named subfamily has probability one. In particular the identities and the coordinate order matter here, even when the complete general-linear orbits agree.

For example take $m=2,\ u=(1,1)^T,\ v_a=(1-a,a)$ for all $a\in K$. Guards $a=0,1$ pass on opposite orders. Each has marginal $1/2$ and their joint probability is zero. All other directions pass both orders. Conjugate this same family by the matrix with rows $(1,-1),(0,1)$. The new image vector is $(0,1)^T$ and the rows become $(1-a,1)$. Every guard now passes on the very same one of the two orders. The joint probability for the full pencil is $1/2$, above the product $2^{-q}$. This disagreement already occurs over the binary field, despite the positive complete-header theorem.

## The separation distance

For the full affine family take $v_\lambda=b+\lambda W$ for all $\lambda\in K^d$, with $bu=1,\ Wu=0$. The $d$ rows of $W$ may be chosen independent. The case $d=1$ is the full pencil. Write $x_i=u_i b_i$ and $y_i=u_i W_{:i}\in K^d$. The slope charges $y_i$ sum to zero and the scalar charges $x_i$ sum to one. At a proper prefix, if its vector slope sum $Y$ is nonzero, the parameter $\lambda$ can make $X+\lambda Y$ equal one. If $Y=0$, every direction passes exactly when $X\ne1$. Therefore all the guards can pass only if every proper slope prefix vanishes. The final slope sum vanishes too, so subtracting successive prefixes forces **every individual $y_i$ to vanish**. Conversely, when all $y_i$ vanish, what remains is precisely the single-row scalar prefix test. This necessity uses the full parameter family.

Discard initially zero slope charges. Write $h$ for the number left, and $Z$ for the largest number of nonempty disjoint zero-sum blocks partitioning those $h$ labeled charges. Set $Z=0$ for the empty list. The **exact minimum number of paid row additions making all slope charges zero** is

~~~text
distance to separation = h - Z .
~~~

The proof works for vectors in arbitrary dimension. Under $R_i\gets R_i+aR_j$, the column component $u_i$ increases by $a u_j$ and column $W_{:j}$ decreases by $aW_{:i}$. Consequently the only charge changes are
$y_i\gets y_i+a u_j W_{:i}$ and $y_j\gets y_j-a u_j W_{:i}$. A monomial conjugates an elementary addition into another such addition, with relabeled indices and a nonzero scalar. Thus free operations may all be moved to the end, where they only permute the charges.

For any successful word, connect the two labels involved in each paid addition. The initial charge sum on each connected component is conserved and must be zero. The components containing initially nonzero charges partition those charges into at most $Z$ blocks. A component containing $k$ active labels needs at least $k-1$ edges, including when initially zero labels are used as helpers. Repeated edges are still charged operations. Summing yields the lower bound $h-Z$.

For the reverse bound, choose a maximizing partition. In each block keep one initially active coordinate $j$ and visit the other labels $i$ in any order. Add row $j$ to row $i$ with coefficient $-u_i/u_j$. This sets $u_i$ to zero and transfers its whole charge to $j$ in the dual rows. The accumulator's $u_j$ never changes. Its final charge is the block sum, zero. Each block of size $k$ costs $k-1$. These legal elementary matrices supply the missing realization step in transferring the classical zero-sum partition idea to constrained row operations. [Csaba Pătcaș, *The debts’ clearing problem: a new approach*](https://acta.sapientia.ro/content/docs/the-debts-clearing-problem-a-new-approac.pdf)

## When the separation price is the full guard price

Call a scalar carrier **anchored** if $b$ is supported at a single coordinate $c$, $u_c b_c=1$ and $W_{:c}=0$. The construction above never touches $c$ since $y_c=0$. It preserves $b$, and a free permutation puts $c$ last. Every proper scalar prefix is then zero. Thus for an anchored full flat, $h-Z$ is also the exact minimum price of a header passing **all the original minors**. A full guard requires separation regardless of whether the carrier is anchored.

For instance over $K=\mathbb F_5$ take $u=(1,1,1,1,1)^T,\ b=(0,0,0,0,1)$ and a single slope. For $(1,4,2,3,0)$ two opposite pairs settle in two additions. For $(1,1,1,2,0)$ only the whole active block sums to zero, so three additions are necessary and sufficient. Both lists have four active labels, yet their optimal costs differ. WITNESSES.json supplies every coefficient and EXAMPLES.json checks all raw states at every smaller cost plus an actual attaining word.

## Arbitrary binary families

Now take any nonempty ordered list of normalized rows $V$, possibly repeated or dependent. Set $z_i=u_i V_{:i}$ and $t=(1,\ldots,1)$. In the binary field a proper prefix passes every guard if and only if its sum is **the zero vector**. Thus success after a free permutation means the charges vanish off one coordinate, whose charge is $t$. Write $h$ for the number of nonzero $z_i$, and append a single labeled dummy charge $-t$ to those $h$ charges. If $Z_*$ is the maximum zero-sum block count of this augmented list, then

~~~text
minimum paid additions passing an arbitrary binary family = h - Z_* .
~~~

In a successful word, append the dummy to the component of the final carrier. This component has initial total $t$. All other components have initial total zero. This gives the same edge lower bound. Conversely, settle every block as above, consolidating only the real charges of the dummy's block onto one accumulator. That block contains at least one real charge. Its final value is $t$, and a free permutation puts it last. The dummy is a bookkeeping device and never a row or usable workspace. The same formula computes the distance to a single charge in any field, which suffices for guarding but need not be necessary outside the binary case.

Even when slope separation is free, the remaining price can grow without bound. Over the binary field choose $2n+1$ coordinates with $u_i=b_i=1$, and a separate zero-$u$ coordinate supporting $W$. Every active charge for the full pencil is the same all-ones vector. After adjoining the dummy there are $2n+2$ identical charges, so $Z_*=n+1$ and the exact full guard price is $n$. All slope charges were already zero. A prior separation test alone cannot price this input.

## Ternary flats whose slopes are already separated

Suppose $q=3$ and every $y_i=0$. Write $A$ for the number of scalar charges $+1$ and $B$ for those equal to $-1$. Thus $D=A-B\equiv1\pmod3$ and $n=A+B>0$. In reverse order the guard passes if and only if every nonempty scalar prefix in that reverse order has nonzero sum (the full sum is one). Starting with zero, the first charge must be nonzero. After zeros are removed the prefix states alternate between $+1$ and $-1$, finishing at $+1$. For odd $n$ this requires $D=1$, and for even $n$ it requires $D=-2$. Each allowed case has exactly one sign pattern. It starts with $+1$ for odd $n$ and $-1$ for even $n$, after which the next nonzero step is forced. Conditional on the first coordinate being nonzero, the relative order of the nonzero labels is uniform. The passing probability under a uniform monomial header is therefore

~~~text
n/[m binom(n,A)]  if D is 1 or -2;   otherwise 0 .
~~~

More strongly, with row additions allowed the exact full guard price here is
$\min(|D-1|,|D+2|)/3$. One paid addition changes at most two scalar charges, preserving their total in the field. Their signed integer sum can change only by zero or by three in absolute value. This gives the lower bound even when the intermediate slope charges are unrestricted. When $D>1$, merge two $+1$ charges into one $-1$ and one zero. The previously separated slopes on those active coordinates remain zero. Each such merge decreases $D$ by three. When $D<-2$, pair two negative charges instead. In either direction there are enough same-sign pairs, and the resulting scalar list has the required ordering. In particular $s$ active coordinates alone do not determine either the probability or the minimum price.

For arbitrary odd fields with an unanchored carrier we supply an exact order-counting algorithm and a separation lower bound. The anchored and already-separated hypotheses identify the statements that give a full paid distance here.
