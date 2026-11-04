# The first possible field order is four

Over the fields of orders two and three, **every** normalized common-image family of at least two guards satisfies $J>p^k$ in every allowed dimension. Over every field of order at least four there is a three-direction pencil with $J<p^3$ for all sufficiently large dimensions. Thus the field-size boundary is sharp for this shared-image model.

The binary result follows from the last-coordinate and pair bounds in PROOF.md. For $q\ge4$ the pencil result follows from SIGN.md. It remains to establish the ternary assertion. Repeated rows can be discarded: the intersection is unchanged, and a higher power of $0<p<1$ is smaller. A single distinct row has probability $p$. For two or three distinct rows, the pair law and TRIPLES.md give strict positivity, including the ternary three-direction pencil. For $k\ge5$, the last-coordinate condition applies since $3(7/9)^5<1$. Only four distinct rows remain.

## Four ternary rows

Four distinct normalized rows cannot lie on a ternary affine line. Their rank $r$ is three or four. At rank three the image $S$ is cut out by one nonzero relation on the four row evaluations, whose coefficients sum to zero. Its support has size at least three, since the rows are distinct and normalized. At support size three the coefficients there are equal up to overall sign. Exactly two nonzero-coordinate triples have sum zero (all signs equal), and the fourth coordinate is free to take either nonzero value. Thus $h(S)=4$. At support size four the coefficients consist of two plus and two minus signs. Among the four nonzero evaluation coordinates, absorbing each coefficient into its coordinate gives six assignments with sum zero. Thus $h(S)=6$. Up to permuting rows these are the two ternary rank-three dependency spaces.

At rank four $S=\mathbb F_3^4$, so $h(S)=16$. In either rank, any space $L$ of dimension $\ell$ has $h(L)\le2^\ell$: select $\ell$ independent coordinate projections, all of which must be nonzero. This bounds each negative contribution in the lattice sum.

For $r=3$, the four codimension-one spaces through $t$ have $\lambda(L)\le17$, and the codimension-two contribution is positive. At $r=4$, the thirteen codimension-one spaces have $\lambda(L)\le43$; the codimension-three line has coefficient $-27$ and $\lambda=7$. Dropping positive lower terms, using $D_r<3(3^{r+1})^d$ and $p<(7/9)^d$, gives the following lower bounds on $J/p^4$ wherever the last bracket is positive:

~~~text
r=3: (2/3) [(35/81)/(7/9)^4]^d [1-4(17/35)^d].
r=4: (2/3) [(113/243)/(7/9)^4]^d [1-13(43/113)^d-27(7/113)^d].
~~~

Both exponential bases exceed one and the final brackets are increasing. At $d=4$ the lower bounds exceed one in both ranks, so they do for all $d\ge4$. The remaining five joint probabilities in the table come directly from the lattice formula. Each exceeds its dimension's $p^4$; the exact ratios, cutoff bounds, and separate raw-prefix counts are retained in TERNARY-FOUR.json.

| Rank and relation support | $m=3$ | $m=4$ |
| --- | ---: | ---: |
| 3, support 3 | $4/39$ | $5/104$ |
| 3, support 4 | $47/351$ | $961/14040$ |
| 4, independent | — | $7811/126360$ |

This exhausts the ternary cases. The four-element example in SIGN.md therefore occurs over the smallest possible field order. This comparison concerns the all-pass probability of normalized common-image **corank-one complement guards**.
