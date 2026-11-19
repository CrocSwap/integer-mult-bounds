# Exact support distribution over two freely varying coordinates

Fix a repeated matrix unit in common input and output stabilizer bases. Among the 65,536 ordered pairs of matrix units on the two remaining sites, there are seven possible numbers of nonzero coefficients of the Hilbert adjoint. Every pair appears once, including both choices equal to the repeated coordinate.

| Nonzero Clifford labels | Ordered pairs |
|---:|---:|
| 5,929,571,450,880 | 420 |
| 5,978,984,546,304 | 1,350 |
| 6,028,397,641,728 | 18,900 |
| 6,078,693,113,856 | 44,100 |
| 6,670,767,882,240 | 90 |
| 6,781,947,346,944 | 675 |
| 8,338,459,852,800 | 1 |

At width 13 with **all** sites free, there are exactly 30 support sizes among the $2^{104}$ coordinates. With the first address fixed, the number attaining the minimum of 5,411,658,792,960 is 74,959,609,988,606,102,773,113,260,160 out of $2^{96}$ (94.6123%). The maximum is attained only when every site agrees. With zero through six free sites beyond one common address, there are respectively 1, 3, 7, 13, 22, 27 and 30 sizes. The full histogram stabilizes in its set of sizes by six free sites; the multiplicities continue to change. The census concerns the raw adjoint $A^*$.

## Counting quotient isomorphisms

Work in computational bases by conjugating by the two fixed Clifford basis changes. Write $X,Y$ for the row and column spaces $\mathbb F_2^n$. Subtract the repeated or first coordinate from all sites, and let $D\le X\oplus Y$ be the span of the resulting displacement vectors. Put $a=\dim\mathrm{pr}_X D$, $b=\dim\mathrm{pr}_YD$, and $c=a+b-\dim D$. The pure row and pure column subspaces of $D$ have dimensions $a-c,b-c$. Their two projection quotients are identified by $D$ and have common dimension $c$.

At Hadamard rank $h$, the displacement support of a Clifford lift is a linear relation $R$ given by two $h$-planes $U\le X$, $V\le Y$ and an isomorphism $X/U\to Y/V$. This follows from the column-support derivation in [the coordinate census of #7821](https://github.com/apoursh/integer-mult-bounds/blob/eead545a4ba6c50010fcac0919a9fdc6b14bd673/research/clifford-compact-adjoint-fibres/COORDINATES.md). Every column is one coset of $U$, and the surjection from columns to $X/U$ has kernel $V$. Each such relation occurs for
$$
m_h=2^{h(h+1)/2}|P_Z| / \prod_{i=0}^{n-h-1}(2^n-2^i)
$$
symplectic fibres, where $|P_Z|=2^{n(n+1)/2}|\mathrm{GL}(n,2)|$. The coefficient is nonzero when $D\subseteq R$ and the Pauli translate includes the first address, giving $2^{n+h}$ nonzeros per occupied fibre. The absolute square of each coefficient is $2^{-w(n+h)}$ at width $w$.

For $D\subseteq R$, its pure subspaces must lie in $U,V$. The intersections $U\cap\mathrm{pr}_XD$ and $V\cap\mathrm{pr}_YD$ must induce the **same** subspace of the common quotient. Otherwise a vector equivalent to zero on one side maps to a nonzero class on the other. If this induced subspace has dimension $e$, there are $\genfrac{[}{]}{0pt}{}{c}{e}_2$ choices. Set $k=c-e$. The intersections now have prescribed dimensions $a-k,b-k$. The number of $h$-planes having one prescribed intersection of dimension $s$ with an $a$-plane is
$$
L(a,s)=\genfrac{[}{]}{0pt}{}{n-a}{h-s}_2\,2^{(a-s)(h-s)}.
$$
Indeed choose the projection of the $h$-plane to the ambient quotient of the $a$-plane, then its graph into the $a$-plane modulo the fixed intersection. Infeasible dimensions have count zero. Finally the isomorphism on the two $(n-h)$-dimensional quotients must extend a fixed isomorphism between $k$-planes. There are $2^{k(n-h-k)}|\mathrm{GL}(n-h-k,2)|$ extensions. Choose the isomorphism on the complementary quotient and an arbitrary component in the target $k$-plane. Thus the exact number of relations is
$$
\sum_{e=0}^c \genfrac{[}{]}{0pt}{}{c}{e}_2 L(a,a-k) L(b,b-k)
   2^{k(n-h-k)}|\mathrm{GL}(n-h-k,2)|,\qquad k=c-e,
$$
omitting $k>n-h$. Multiplying by $m_h$ gives occupied fibres. The formula is symmetric in $a,b$ and uses only three ranks. It yields both the support size and the squared adjoint norm by shell summation.

## Counting address lists

With $t$ varying sites and a fixed base address, the number of ordered lists of displacement type $(a,b,c)$ is
$$
\genfrac{[}{]}{0pt}{}{n}{a}_2\genfrac{[}{]}{0pt}{}{n}{b}_2\genfrac{[}{]}{0pt}{}{a}{c}_2\genfrac{[}{]}{0pt}{}{b}{c}_2 |\mathrm{GL}(c,2)|
\prod_{i=0}^{a+b-c-1}(2^t-2^i).
$$
The first factors choose the projected subspaces, their pure kernels and the isomorphism between the $c$-dimensional quotients. These data recover $D$ uniquely as a relation. The final product counts surjections $\mathbb F_2^t\to D$, since they are exactly the ordered $t$-tuples spanning $D$. A varying base contributes an extra factor $2^{2n}$. The formulas have no dependency on the other sites' order or on a chosen coordinate gauge.

The [calculator](address_census.py) produces the table and complete histograms. The [independent checker](check_address_census.py) constructs every quotient plane and surjection directly for $n\le4$. In four qubits this visits all 65,536 distinct support relations and checks all 55 ordered displacement types, a different enumeration from summing subspace intersection counts. It also counts all two-site address pairs, checks normalization, and independently verifies that the sum of squared adjoint norms over all addresses equals the number of unit dictionary columns for widths 1, 2, 6 and 13. The calculation extends apoursh's support criterion, individual-address counts and extrema in #7821.

The same closed formula also checks every support multiplicity in the [two-site normal operator](TWO-SITE-SPECTRUM.md), including its off-diagonal entries. Form $D$ from the two directly matched addresses, the two crossed addresses, or their union. The three shell counts reproduce the independently enumerated direct, crossed and simultaneous support counts on every row and column type.
