# A sharp envelope for simultaneous block-local quotients

## The comparison

Fix either the forward PR7001 BIT word or its transpose. The first 222 public coordinates are the 111 main pairs. The other 437 coordinates are helpers. The scalar endpoint on these helpers is the identity. Group them by their ordered pair of entrance and exit charts. Write $H_g$ for the span over $\mathbf F_2$ of the entrance coordinate **functionals** of group $g$, and $H=\bigoplus_g H_g$. The nine dimensions are 410, 7, 6, 5, 3, 2, 2, 1, 1. The replay checks full row rank and orthogonality in all 636 rational eight-axis charts, and nesting on all 2,374 directed paid pairs and nine helper boundaries. This certifies the dimension-difference tariffs used below. [Pinned word and caller](SOURCES.json)

Choose a subspace $U_g\le H_g$ independently for each group. Restrict the inputs to the common zero set of $U=\bigoplus_g U_g$. An invertible change of basis at that group's two boundaries realizes its kernel as arbitrary surviving helper coordinates. The main inputs stay independent. The group surrenders $\dim U_g$ identity targets, each of rank $d_g$, the absolute difference in its two chart dimensions. Keeping all original paid forms, ranks, charts, and chronological order, permit omission of an arrival whenever its value can be synthesized by scalar XOR from the free entrances and strictly earlier arrivals at that receiver. Grant the storage and ordinary XOR work for free. This is the causal-bank relaxation introduced for the selected word. [Bank model and single-relation proof](https://github.com/aliromman/integer-mult-bounds/blob/3e56de8c160f259612f9766e06bf6990c7b5a3ef/research/bit-single-relation-bank-obstruction/PROOF.md)

Write $G_t(U)$ for the saved paid price minus $\sum_g d_g^t\dim U_g$, for $0\le t\le1$. Let $q=\log_2(5/3)$. We prove

$$
\max_U G_t(U)=\max(0,1+4^t-6^t)\qquad(q\le t\le1).
$$

The proof also determines the sign of the optimal complete invoice over the entire interval $0\le t\le1$. Section 5 gives the resulting global raw BIT ceiling.

## 1. Chronological rank loss

At chart $C$ put all initial local fields first and then all arriving paid forms in their literal order. Let $V_j$ be the span of the first $j$ rows in this list. The raw-word replay verifies that every whole list is independent in each orientation. On inputs annihilated by $U$, the rank of the first $j$ rows is

$$
\dim V_j-\dim(U\cap V_j).
$$

Consequently a paid row at position $j$ can be omitted exactly when $D_j=\dim(U\cap V_j)$ increases by one. The earlier-bank equality supplies a reconstruction. Induction in the word order permits all such omissions together, because an earlier reconstructed value can itself be retained. This is optimal for the declared fixed arrival and deadline contract.

Put $F_j=V_j\cap H$ and $F_{g,j}=V_j\cap H_g$. A *birth* at $j$ means the dimension of the stated space increases at that row. If $j_0$ is the end of the free entrances and $m$ the final position, the saved paid price at this receiver is

$$
D_m-D_{j_0}+\sum_{\substack{j>j_0\\r_j>1}} (r_j^t-1)(D_j-D_{j-1}).
$$

Only births of $F_j$ can contribute to the sum. Whenever $\dim F_j=\sum_g\dim F_{g,j}$, inclusion and disjoint coordinate supports give $F_j=\bigoplus_g F_{g,j}$. At such a prefix $D_j=\sum_g\dim(U_g\cap F_{g,j})$ for every simultaneous choice of $U$.

## 2. Where the groups interact

The following finite facts are checked from the word, at every free and paid prefix in each receiver. The counts include free rows. The maximum dimension excess in the table is $\max_{C,j}(\dim F_j-\sum_g\dim F_{g,j})$.

| Quantity | Forward | Transpose |
|---|---:|---:|
| Receiver charts | 636 | 636 |
| Nonempty bank prefixes | 3,530 | 3,530 |
| Charts with a mixed prefix | 5 | 31 |
| Maximum dimension excess | 7 | 2 |
| Charts still mixed at the final prefix | 3 | 26 |
| Potential paid births of rank greater than one | 254 | 235 |

At each free prefix the full flag decomposes. Immediately before **and** after every possible paid birth of rank greater than one it decomposes as well. Thus the higher-price terms in section 1 add across the groups. At a receiver whose final flag decomposes, the entire saved price adds across the groups, even if an intermediate rank-one prefix was mixed.

Write $B=H_{\rm large}$, the 410-dimensional group, and $S=\bigoplus_{g\ne{\rm large}}H_g$. The replay checks $V_j\cap S=\bigoplus_{g\ne{\rm large}}F_{g,j}$ at *every* prefix. At all mixed-final receivers, every possible full-helper birth has price one and occurs at a paid row. The kernel of the projection $\pi_B:F_m\cap U\longrightarrow B$ is $(V_m\cap S)\cap U$. Its image is contained in $(\pi_BF_m)\cap U_{\rm large}$. Hence

$$
D_m\ \le\
\sum_{g\ne{\rm large}}\dim(F_{g,m}\cap U_g)
+\dim(\pi_B F_m\cap U_{\rm large}).
$$

On just these receivers we charge the projected space to the large group at unit price. This grants the large group every possible small-group cancellation. The final flag at every group boundary decomposes. Setting $U_{\rm large}=0$ gives exact additivity among all the small groups. The forward arrival at chart 50, clock 19881, checks that a mixed term can be essential in an actual prefix. [All mixed charts and witness](RESULT.json)

## 3. Charging the large space and the other groups

Fix an ordered coordinate basis in a group. For a subspace $W$, let $P(W)$ be all possible leading positions of its nonzero vectors, with the largest nonzero coordinate leading. Elimination gives $|P(W)|=\dim W$. At the entrance chart the entire group's relation space already lies in the free prefix, so it saves zero paid rows there. At every other chart the original independent bank list gives each clean signal a unique representation. Its latest bank determines its chronological price.

At a nonterminal receiver enumerate its clean signals for this group. Denote by $b_C(i)$ the maximum possible price at coordinate pivot $i$, or zero if absent. The chronological prices removed by $U_g$ at this receiver sum to at most $\sum_{i\in P(U_g)} b_C(i)$. To prove it, take a basis of $W=U_g\cap F_{g,m}$ with distinct, increasing latest-bank positions. These are precisely the removed positions. Process this basis in that order, eliminating previous **coordinate** pivots. Each modified vector keeps its own latest bank, since every eliminator uses earlier banks, and acquires a distinct coordinate pivot in $P(U_g)$. Its price is bounded by $b_C(i)$. The same bound for a mixed projected receiver follows by counting distinct coordinate pivots at unit price. Every enumerated nonterminal space after projection has dimension at most four.

At its terminal the clean flag spans the full group. Use the basis vectors introduced at its successive births. A combination whose last nonzero coordinate is $i$ has the price of the $i$th terminal birth. A permutation within one consecutive equal-price run preserves this statement. For the large forward group the original role basis with a uniform terminal bound of rank two suffices. For the large transpose group the terminal prices in order have run lengths 2, 153 and 255, with ranks 4, 2 and 1. In the final run apply the following six swaps of zero-based positions, in order.

~~~
(365,156)  (401,237)  (380,200)  (409,329)  (296,251)  (376,162)
~~~

These are choices of proof coordinates. Independently, the initial 410 chronological basis vectors can be recovered by taking all original unit roles except 332 and 340, adding $e_{332}+e_{333}$ and $e_{340}+e_{375}$, and sorting by each vector's latest terminal bank. All 410 latest banks are distinct. [Primary charge computation](flags.py) Ã‚Â· [Independent terminal reconstruction](crosscheck.py)

At $t=q$, multiply prices by 27. The integer prices of ranks 1, 2, 4 and 8 become 27, 45, 75 and 125. Add each terminal charge to the nonterminal maxima on the same coordinate. The table gives the maximum resulting numerator per coordinate. Boundary pairs are named in the forward direction on both sides.

| Forward group | Helpers | Target rank | Forward maximum | Transpose maximum |
|---|---:|---:|---:|---:|
| $0\to1$ | 410 | 8 | 120 | 117 |
| $506\to1$ | 7 | 4 | 75 | 75 |
| $507\to1$ | 6 | 4 | 27 | 72 |
| $508\to1$ | 5 | 4 | 27 | 72 |
| $509\to1$ | 3 | 4 | 27 | 72 |
| $0\to506$ | 2 | 4 | 72 | 72 |
| $520\to1$ | 2 | 4 | 27 | 72 |
| $374\to1$ | 1 | 2 | 45 | 45 |
| $0\to374$ | 1 | 6 | Ranks 1 and 4 | Ranks 1 and 4 |

For example the four forward profiles on the 410-dimensional group are $(1,2)$ on 252 coordinates, $(2,2)$ on 153, $(1,2,2)$ on three, and $(2,4)$ on two. They account for every coordinate. The highest price is $45+75=120<125$. The cross-check independently recovers the profile counts in both orientations. [Group receipts](RESULT.json)

Every charged rank $r$ is at most its group's $d_g$. The normalized price $(r/d_g)^t$ decreases or stays constant as $t$ increases. All inequalities verified at $q$ thus hold through 1. Every nonzero large-group restriction incurs a strict loss. On a small group other than the rank-six group, every coordinate either loses strictly at $q$ or has the solitary charge $(d_g)$.

## 4. Attainment, threshold and maximizers

The unique rank-six group consists of role 341. Choosing its full one-dimensional relation space sets $x_{341}=0$. Direct chronological elimination gives the complete list of paid omissions below. A blank donor list means the restricted arrival is zero. Clocks start at zero in the indicated orientation.

| Orientation | Chart | Omitted clock | Rank | Earlier donor clock |
|---|---:|---:|---:|---:|
| Forward | 53 | 19929 | 1 | 19928 |
| Forward | 374 | 21559 | 4 | 21547 |
| Transpose | 0 | 14207 | 1 | 13967 |
| Transpose | 177 | 12577 | 4 | empty |

In each row the arrival XOR its listed donor equals $x_{341}$ on every original input. The joint upper bound permits exactly the gain $1+4^t-6^t$ for this group. Taking this restriction alone attains it. Taking the zero relation in every group attains zero. This proves the envelope.

Dividing by $6^t$ gives $(1/6)^t+(2/3)^t-1$, which strictly decreases, is positive at zero, and is negative at one. Its unique zero $t_*$ exceeds $q$. Indeed $2^{37}3^{50}>5^{50}$ and $6^{37}9^{50}<34^{50}$ give $q<37/50$ and $6^{37/50}<34/9<1+4^{37/50}$. Below $q$ the same single helper already yields a positive gain. Thus the first profitable price saving over the whole unit interval occurs strictly beyond $\eta_*=1-t_*$. Rational logarithm and exponential series with outward tails certify

$$
0.2517782975220009 < \eta_* < 0.2517782975220010.
$$

For the logarithm the checker bounds the tail after $N$ terms of $2\sum_{j\ge0}z^{2j+1}/(2j+1)$ by $2z^{2N+1}/((2N+1)(1-z^2))$, with $z=(b-1)/(b+1)$. For $0\le y<2$ the exponential tail after degree 44 is less than $2^{46}/45!$. [Exact interval arithmetic](sharp.py)

For $q\le t\le1$, every maximizing tuple has zero large-group component. On the eight small groups the flags split, so every coordinate with a strict deficit excludes that subspace from equality. Conversely, when all selected pivots have the solitary terminal charge $(d_g)$, the terminal attains that charge and the allowed nonterminal contribution is zero. The rank-six line is forced on for $t<t_*$, forced off for $t>t_*$ and optional at equality. The rank-two line is always optional. The only remaining choices lie in the seven-dimensional block $506\to1$.

* In the forward flag the allowed pivots are 5 and 6. Each neutral space is the graph of a linear map from a subspace of the terminal two-dimensional quotient to the first five coordinates. There are $1+3\cdot2^5+2^{10}=1121$ choices.
* In the transposed flag the allowed pivots are 0 and 1. Its neutral spaces are precisely the five subspaces of that initial two-dimensional plane.

Thus, away from the switch in the envelope's range, **2,242 forward tuples and 10 transposed tuples** attain the maximum. At the switch these counts double. Direct enumeration checks every small-block subspace and its actual removed banks. These counts distinguish subspaces of relations. Different generating bases for the same subspace are identified.

The paired caller uses two invocations at each of 18 stages. Each occurrence has fresh helper coordinates. The unchanged root, QUERY and idle terms cancel in the signed difference, so multiplication by 36 gives the complete caller envelope. The source recount has 107,352 paid calls, 19,950 productive targets and integer rank surplus 1,506. Whole-call implementation, tape costs and the other framework obligations keep their original scope. [Caller and group counts](RESULT.json) Ã‚Â· [Selected application review](../../docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)

## 5. Global optimum for the signed BIT invoice

Let $M(t)=\sum_r(T_r-P_r)r^t$ be the original signed margin. The **supremum of feasible raw BIT price savings over the entire quotient family**, for $0\le\eta\le1$, is exactly the original PR7001 crossing

$$
0.0038525393934 < \eta_0 < 0.0038525393935 .
$$

More precisely, some allowed tuple gives strictly positive complete margin if and only if $0\le\eta<\eta_0$. This interval was previously reported for the original BIT caller. The new assertion is optimality over all the simultaneous quotients. [PR7001 source proof](../paired-query-only-bit/PROOF.md)

For $t\ge3/4$ the envelope gives zero maximum gain, since $t_*<3/4$. For $0\le t\le3/4$, grant all original productive credits and omit *every* paid arrival that could disappear under any restrictions. Dependence at a fixed deadline is monotone under enlarging $U$. Taking $U=H$ therefore gives every potentially removable paid position. The forward count by ranks $(1,2,4)$ is $(599,249,5)$, and the transpose count is $(355,230,5)$. Other ranks have zero possible omissions. The coordinatewise maximum across orientations gives the following upper bound even if each invocation chooses its own orientation and subspaces.

$$
M_{\rm generous}(t)=M(t)+36\bigl(599+249\cdot2^t+5\cdot4^t\bigr).
$$

Both $M(t)/8^t$ and $M_{\rm generous}(t)/8^t$ are strictly increasing on $[0,1]$. To see this, inspect the two signed profiles. Every coefficient below rank 8 is nonpositive, and the rank-one coefficient is strictly negative. Each normalized term there is increasing. At ranks $h=14,21,\ldots,56$, pair a negative coefficient with the matching positive coefficient at $h+1$. The function $((h+1)/8)^t-(h/8)^t$ increases for $t\ge0$, since $y^t\log y$ increases for $y>1$. All remaining terms have nonnegative coefficients at ranks at least 8. The checker verifies these sign and pairing conditions on both actual profiles.

Exact outward bounds give $-23329<M_{\rm generous}(3/4)<-23328$. By normalized monotonicity every allowed margin is negative throughout $0\le t\le3/4$. On the rest of the unit interval, $M(t)$ is attained and is the maximum. Its normalized monotonicity and the certified opposite signs at the two displayed $\eta_0$ endpoints prove the claim.

At the project's price parameter $\eta=0.01$, the **best possible** complete margin satisfies

$$
-2355.302 < \max_U \bigl(M(0.99)+\text{complete gain}\bigr) < -2355.301.
$$

The strict gate requires a positive margin. The 0.251778… sign change of an individual edit thus occurs where even the generous complete invoice already fails. The conditional multiplication exponent recorded by the project is a separate quantity.

The numerical sign checks use only integer arithmetic. Bracket the rational exponent on the grid $2^{-80}$, then enclose each repeated square root of the integer rank on the grid $2^{-128}$ by integer square roots rounded outward. Multiply the selected factors with outward rounding and choose the appropriate endpoints for each signed coefficient. The monotonicity proof covers the intervals between tested exponents. [Whole-caller certificate](invoice_bound.py) · [Receipt](RESULT.json)
