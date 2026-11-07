# A global ceiling for the declared two-chain invoice

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The caller, native profile and chain idea are due to DreamingOfClouds in
CrocSwap/integer-mult-bounds#6833, frozen at
`ad24ad966b857dbfed50d9121624db84b2eccc92`. This proof adds an infinite-family
optimization result; it does not reprove that predecessor's supplier contract.

## 1. Exact statement and applicability

Let each of two chains have a positive integer length, denoted by `l` and `r`,
and write `M=l+r`. Freeze the 104-port native profile in the retained source.
Its signed helper-minus-paid multiplicities, in ranks 1 through 9, are

\[
d=(-2220,-446,-485,-1,-135,-4,1,39,359).
\]

The **declared family** charges `M` copies of this native profile, 104 copies of
one target of rank `8M+1`, 104 targets of rank `8j+1` for every `1<=j<=l` and
every `1<=j<=r`, and 104 paid jobs of rank `8j` for every `1<=j<l` and
every `1<=j<r`. For even `M` it includes 104 extra rank-one targets and 312
rank-one thin-query payments; for odd `M` it includes no extra rank-one target
and 208 thin-query payments. In either case the signed constant is -208.

The `(9,9)` member is independently recounted from the literal `CALLER.json`,
without importing the predecessor constructor, pricing engine or interval code.
Its counts are 12,232 productive fields, 64,184 paid jobs, 166,812 paid rank mass,
and surplus 760. The inherited native histogram is authenticated, not rederived
from the native operator circuit in this package. For other lengths, this is an
explicit invoice family. The all-parity extension is a relaxation: no claim that
every even or mixed-parity member is a valid compiled caller is needed below.
In particular, a valid odd/odd caller with exactly the declared accounting lies
inside the family. A new caller or a different native profile requires a new
applicability argument.

**Theorem.** Among all positive integer pairs in this declared family, `(9,9)`
has the unique largest raw moment crossing. That crossing, denoted by `C*`,
satisfies

\[
0.0033718004754<C_*<0.0033718004755.
\]

For every pair and every `C>=0.0033718004755` with `C<1`, the signed moment is
strictly negative. For totals at least 3 the crossing is unique. Total 2 has
no positive favorable interval. These are statements about the frozen signed
invoice, not a new admitted multiplication exponent.

## 2. Complete moment and balancing

Put `t=1-C`, so `0<t<1`, and define

\[
D(t)=\sum_{k=1}^9d_k k^t,\qquad
A_g(t)=\sum_{j=1}^g(8j+1)^t-\sum_{j=1}^{g-1}(8j)^t.
\]

The complete family margin is

\[
F_{l,r}(t)=M D(t)+104\big((8M+1)^t+A_l(t)+A_r(t)-2\big). \tag{1}
\]

No thin query, native payment or merged idle job is dropped in (1). In
particular, it is not the optimistic main-target-only budget.

For `g>=1`,

\[
A_{g+1}(t)-A_g(t)=(8g+9)^t-(8g)^t.
\]

This difference is strictly decreasing in `g`: for any positive width `h`,
the function `(x+h)^t-x^t` has strictly negative derivative in `x` when
`0<t<1`. If `l>=r+2`, replacing `(l,r)` by `(l-1,r+1)` therefore strictly
increases (1). For a fixed total `M`, the largest invoice is attained precisely
by the balanced pair, up to interchange. Write its margin as

\[
B_M(t)=F_{\lfloor M/2\rfloor,\lceil M/2\rceil}(t),\qquad M\ge2.
\]

## 3. Strict discrete concavity in the total

Direct subtraction, including the new native copy, gives

\[
B_{M+1}(t)-B_M(t)=D(t)+104\left[
(8M+9)^t-(8M+1)^t
+(8\lfloor M/2\rfloor+9)^t-(8\lfloor M/2\rfloor)^t
\right]. \tag{2}
\]

The first bracketed difference is strictly decreasing in `M`. The second is
nonincreasing, repeating at most once because of the floor. Thus (2) is strictly
decreasing for every `0<t<1`. Two adjacent signs locate the maximum over the
entire infinite domain; there is no unsearched large-length tail.

The directed-integer certificate evaluates (2) over the **whole** saving interval
`[0.0033718004754,0.0033718004755]`, not just at one guessed root. It proves

\[
B_{18}-B_{17}>0.3232560777>0,
\qquad B_{19}-B_{18}<-0.1714023579<0.
\]

Hence `B18` uniquely maximizes the balanced family throughout that interval.
Balancing then makes `(9,9)` the unique maximizing pair there. At the two exact
rational endpoints its margins have the directed enclosures

| Saving C | Enclosure of F(9,9; 1-C) |
|---|---|
| 0.0033718004754 | [0.000000021652415920367122, 0.000000021652415920367123] |
| 0.0033718004755 | [-0.000000000734152088876529, -0.000000000734152088876528] |

Continuity gives a root between them. The next section rules out a later
favorable interval, for this or any other pair, and proves uniqueness.

## 4. Monotonic normalization excludes later crossings

It is not sufficient merely to exhibit a negative margin at one value of `C`:
a general signed moment could change sign again. Here every `F/9^t` is strictly
increasing in `t` on `0<t<=1`.

First consider `D(t)/9^t`. Its terms of ranks 1 through 6 have negative
coefficients and positive derivatives. Keeping only the rank-one contribution
gives the lower bound

\[
\frac{d}{dt}\frac{D(t)}{9^t}
\ge \frac{2220}{9}\log9-\log(9/7)-39\log(9/8)
\ge \frac{2220\cdot8}{81}-\frac{2}{7}-\frac{39}{8}
=\frac{323717}{1512}>0. \tag{3}
\]

The first inequality uses `9^(-t)>=1/9`, `(7/9)^t<=1`, `(8/9)^t<=1`;
the rank-nine term is constant. The second uses `log x>=1-1/x` and
`log x<=x-1` for `x>0`. Thus (3) is a rational certificate, with no numerical
logarithm premise.

For the remaining terms rewrite

\[
A_g(t)=(8g+1)^t+\sum_{j=1}^{g-1}\big((8j+1)^t-(8j)^t\big).
\]

After division by `9^t`, the terminal term is `( (8g+1)/9 )^t`, nondecreasing.
The `j=1` summand, when present, is `1-(8/9)^t`, strictly increasing. For
`j>=2`, both bases are at least one; the derivative of `a^t-b^t` for
`a>b>=1` is positive because `x^t log x` strictly increases in `x>=1`.
The normalized root term is increasing, and `-2/9^t` is increasing. Combining
these observations with (3) proves strict monotonicity of `F/9^t`.

Consequently, every invoice negative at the upper endpoint stays negative as
`C` increases. At the crossing `C*` of `(9,9)`, Sections 2 and 3 make every
other pair strictly negative; monotonicity places any other crossing strictly
below `C*`. Finally,

\[
F_{l,r}(0)=104-2892M<0,\qquad F_{l,r}(1)=48M-104.
\]

Thus a unique crossing exists for `M>=3`; for `M=2` both the monotonicity and
the negative endpoint exclude a favorable interval. This completes the proof.

## 5. Exact arithmetic and scope of computational evidence

The new interval implementation uses integer endpoints scaled by `2^192`.
Each arithmetic operation rounds outward. For a positive integer `n`, reduction
`n=2^k u`, `1<=u<2`, expresses its logarithm using `log 2` and
`2 atanh((u-1)/(u+1))`, whose argument lies in `[0,1/3]`. The first 80 terms
are enclosed with a positive tail at most
`9/[4(161)3^161]`. Exponentials are scaled to arguments at most `1/2`, summed
through degree 40, and supplied with the geometric upper bound on the remaining
positive terms before outward repeated squaring. Finally
`n^(1-C)=n/exp(C log n)`. No floating-point sign is trusted.

The verifier recounts the literal caller bill, checks both root signs and
the uniform adjacent-increment signs, and checks the rational derivative bound.
Its 961-pair grid (`1<=l,r<=31`, deterministic, exhaust the grid) only
corroborates the formula: the infinite conclusion comes from Sections 2–4.
Algebraic square-root and integer-power controls test the interval mechanism.
Negative controls reject omitted queries, omitted or undercharged idle jobs,
lost target axes, incorrect target exponents, altered native bills, false
maximizers, the favorable lower endpoint as a ceiling, malformed lengths, and
each altered retained source file. The checks do not replace a formal proof
assistant or a full supplier replay.

Changed native profiles, additional coupling fields, different target supports,
different merged-idle lifetimes and different caller topologies are outside
this theorem. Compiler admissibility of the predecessor's merged jobs remains
an inherited obligation, even if investigated independently elsewhere. The five
framework assumptions (`native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape`, `analytic_recovery`) remain outside this invoice theorem.
The selected frontier is unchanged. **No new κ.**

## 6. Extension to arbitrary binary children and ordered partitions

The preceding theorem used one native call per chain site. The source also
permits a chain site to contain a binary child tree; its `(4,4,1|1,4,4)` gate
uses this option. The following extension rules out an improvement by **any**
ordered partition into binary children, even allowing arbitrary full binary
tree shapes instead of the source constructor's balanced children.

The relevant source is retained `chain_root.py`, function `outer_formula`.
An internal binary node with `m>=2` native leaves adds two targets of rank
`8m+1`, two paid jobs of rank `8m`, and one rank-one thin query. With

\[
\delta_j(t)=(8j+1)^t-(8j)^t,
\]

its per-port signed contribution is `2 delta_m-1`. The source node rule and
complete outer bill are inherited; no claim is made that arbitrary new tree
shapes have been operator-replayed. Allowing all their declared invoices is a
relaxation sufficient for an upper bound. The checker also reproduces the
source's gate crossing `(0.00330823456614,0.00330823456615)` from its own tree
invoice implementation.

Consider a side containing `L` native leaves, partitioned into `g` chain children.
Up to reversing the left partition, its chain contribution is the terminal
`(8L+1)^t` plus `delta_j` at each of the `g-1` internal partition boundaries.
There are `L-g` missing boundaries relative to the all-one partition. A forest
of full binary trees on those children has exactly `L-g` internal nodes.

Since `delta_j` decreases strictly with `j`, each internal node contributes at
most

\[
c(t)=2\delta_2(t)-1.
\]

Consequently every side bill is bounded above by

\[
U_L(t)=(8L+1)^t+\sum_{j=1}^{L-1}\max\{\delta_j(t),c(t)\}. \tag{4}
\]

Indeed, each retained boundary contributes its `delta_j`; each missing boundary
can be assigned one of the equally many node contributions, each at most `c`.
Taking the larger alternative at each boundary can only increase the bill.
This is an envelope, and need not be simultaneously attained by a forest.

Its increments satisfy

\[
U_{L+1}-U_L=(8L+9)^t-(8L+1)^t+\max\{\delta_L,c\}. \tag{5}
\]

The width-eight difference decreases strictly and the maximum decreases weakly
in `L`; hence (5) is strictly decreasing. Balancing and total-length concavity
therefore apply to the envelope

\[
\mathcal B_M=M D(t)+104\big((8M+1)^t+
U_{\lfloor M/2\rfloor}+U_{\lceil M/2\rceil}-2\big).
\]

The new exact interval check proves `delta_9-c>0.00783179` throughout the
same raw-root bracket. All earlier `delta_j` exceed `c` too. It follows that
`U9=A9`, and that the envelope's increments from total 17 to 18 and 18 to 19
are exactly the increments in Section 3. Thus its unique maximum is still
`(9,9)`, and its value there is exactly the ungrouped bill. A nontrivial grouping
at `(9,9)` loses strictly, because its omitted boundaries have `j<=8` and
`delta_j>c`.

Finally, the actual grouped invoices retain the monotonic-normalization
argument. Every added binary term divided by `9^t` is

\[
2\left[\left(\frac{8m+1}{9}\right)^t-
\left(\frac{8m}{9}\right)^t\right]-9^{-t},\qquad m\ge2,
\]

which strictly increases in `t`. Each retained chain boundary and endpoint
has the same property established in Section 4. If `I` is the number of
binary internal nodes, the endpoint identities become

\[
F_{\rm grouped}(0)=104-2892M-104I<0,
\qquad F_{\rm grouped}(1)=48M-104.
\]

**Corollary.** Over all positive side lengths, all ordered partitions and all
full binary child-tree invoices with the source accounting rule, the unique
maximum raw crossing is the all-one `(9,9)` member. It has the same bracket as
in Section 1, and no member has a favorable margin above the upper endpoint.
This does not cover a changed root topology, changed native profile, altered
internal-node interface or different idle-sharing rule.

The checker corroborates the accounting on every ordered pair of full binary
forests with total native leaves 2 through 7, and verifies both endpoint
identities. That finite domain is exhausted deterministically. The infinite
conclusion is (4)–(5), not a search extrapolation. A semantic control removes the
internal thin-query charge and correctly fails the envelope certificate; that
charge is essential and cannot be optimized away by assertion.
