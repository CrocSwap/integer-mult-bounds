# An elementary certificate for the existing short-axis search

Put $w=20\lceil\log_2 k\rceil$, $X=2^w$, $Y=\lfloor X/k^2\rfloor$ and $m=\lfloor k/w\rfloor$. For every $k\ge 2^{2^{100}}$ and every integer $1\le A\le 2^{k+1}$, the $Y$ integers $X-Y+1,\ldots,X$ include an integer coprime to $A$. This loose numerical cutoff applies only to the axis-search lemma. The descending gcd search in the published Lean source therefore succeeds at each of its $m$ calls with the prescribed width and window.

The tape manuscript finds short axes using a theorem of Baker, Harman and Pintz about primes. The released Lean implementation already searches for odd coprime integers and certifies them through a quadratic Jacobsthal theorem. The argument below supplies the interval estimate required by that implementation. The program and its bounds on time and space stay the same. The counting technique is a classical Brun-type combinatorial sieve. Its contribution here is a source-matched proof with elementary dependencies and an explicit cutoff.

## Counting integers without small prime factors

Put $z=k^{6/5}$ and let $I$ be any interval of $Y$ consecutive integers. Starting at $u=z$, take the primes in $(\sqrt u,u]$ as one band and replace $u$ by $\sqrt u$. Stop before a band whose lower endpoint would be below $2^{32}$. The residual primes are at most $2^{64}$. Index the $J$ large bands from the top by $j=0,\ldots,J-1$. Then $J\le\log_2\log_2 z$. The product $D_0$ of the residual primes is at most $(2^{64})^{2^{64}}=2^{2^{70}}$. Their independent survival probability is at least $2^{-64}$, since $\prod_{n=2}^{U}(1-1/n)=1/U$.

Every large band has reciprocal prime mass at most $3/2$. All primes in $(2^v,2^{v+1}]$ divide $\binom{2^{v+1}}{2^v}<2^{2^{v+1}}$. Their number is at most $2^{v+1}/v$ and their reciprocal sum at most $2/v$. For $a=\lfloor\log_2\sqrt u\rfloor\ge32$, summing shells $a,\ldots,2a+1$ bounds the band by $2\ln2+3/a<3/2$. Here $\sum_{v=a}^{2a+1}1/v\le 1/a+\ln((2a+1)/a)$. Consequently the independent band survival probability $V_j=\prod_{p\in j}(1-1/p)$ exceeds $1/5$, since $-\ln(1-1/p)\le (32/31)/p$ throughout the band.

For each integer in $I$, let $h_j$ indicate that none of the band primes divides it. With $t_j=4+2j$, let $U_j$ be inclusion–exclusion truncated after even degree $t_j$, and let $E_j$ be the elementary symmetric sum of degree $t_j+1$ in the divisibility indicators. Bonferroni gives $0\le h_j\le U_j$ and $U_j-h_j\le E_j$ by the alternating partial binomial sums for the number of prime divisors in the band. Telescoping the difference of two products of nonnegative factors gives
\[
 \prod_j h_j\ \ge\ \prod_j U_j-\sum_j E_j\prod_{i\ne j}U_i .
\]
Multiply by the exact indicator of avoiding the residual primes.

Evaluate the right-hand expression first in the independent Bernoulli model with each prime present with probability $1/p$. For the band expectations, $\overline U_j\ge V_j>1/5$ and $\overline E_j\le(3/2)^{t_j+1}/(t_j+1)!$. Disjoint bands are independent. Relative to the product of the upper expectations, the sum subtracted is at most
\[
 5\sum_{j\ge0}\frac{(3/2)^{5+2j}}{(5+2j)!}<0.34 .
\]
The first term before multiplication by five is $(3/2)^5/120$ and consecutive ratios are at most $(3/2)^2/(6\cdot7)$. Including the residual primes, the expected lower polynomial is at least $2^{-65}(\log_2 z)^{-3}$, using $5^{-J}\ge(\log_2 z)^{-3}$.

For an actual interval, each squarefree monomial indexed by $d$ counts multiples of $d$. Its count differs from $Y/d$ by at most one, at every left endpoint. Within each of the $J+1$ product expressions, $d$ uniquely identifies its prime subsets, so each coefficient has magnitude at most one. Every possible divisor satisfies
\[
 d\le D_0\prod_{j\ge0}(z^{1/2^j})^{5+2j}=D_0 z^{14}.
\]
This includes the additional degree in each possible subtracted term. Hence the number of distinct positive divisors in each expression is at most $D_0 z^{14}$. A lower bound for the number in the actual interval surviving all primes through $z$ is
\[
 2^{-65}Y/(\log_2 z)^3-(J+1)D_0 z^{14}.                 \tag{1}
\]
The sieve is used only for existence. The machine tests gcd.

## Larger prime factors and an explicit cutoff

At most $k+1$ distinct primes divide $A\le 2^{k+1}$. Each factor above $z$ removes at most $Y/z+1$ integers of $I$. Subtract $(k+1)(Y/z+1)$ from (1). To check the constants, put $t=\log_2 k\ge 2^{100}$. Then $Y\ge k^{18}/2$, $\log_2 z\le 2t$, $J+1\le 2t$ and $z^{14}=k^{84/5}$. Dividing by $Y$, the two error bounds sum to at most
\[
 4tD_0\,2^{-6t/5}+2\,2^{-t/5}+4\,2^{-17t}.
\]
Each summand is less than one quarter of $2^{-65}(2t)^{-3}$. For example $2^{70}\le t/1000$ and $\log_2(2t)+100\le t/1000$ throughout this range. The latter inequality holds at the left endpoint and its right side has greater derivative thereafter. Taking binary logarithms gives all three comparisons. The surviving count is positive.

## Attachment to the integer caller

Run the same descending search at each step with $A=2\prod_{\rm previous}a_i$. Before step $i\le m$, $A\le 2X^{i-1}\le2^{k+1}$. The returned axis is odd and coprime to every earlier one. It is at least $X-Y$. Append the fully occupied power-of-two axis of width $k\bmod w$ when that width is positive. The occupied product is at least
\[
 2^k(1-k^{-2})^m\ \ge\ 2^k(1-m/k^2)\ \ge\ 2^{k-1}.
\]
The widths sum to $k$, their maximum is $w=O(\log k)$, and their count is at most $k/w+1$. For the paper's digit choice $2^k\ge4\lceil n/\lceil\log_2 n\rceil\rceil$, the occupied product is at least twice the number of input digits.

There are at most $m(Y+1)$ trials, and $X\le(2k)^{20}$. A fixed set of heads can scan the previous short axes, testing pairwise gcd by the Euclidean algorithm and checking oddness. Each pass, rewind and update takes polynomial time in $k$. The stored axes occupy $O(k)$ binary bits. Even the source's unary short-axis implementation visits only polynomially many setup cells in $k$ in a reusable marked region. This setup fits $2^k k=\Theta(n)$ for large $k$, for both time and cells ever visited. Explicit shape tests and schoolbook fallback handle smaller lengths. The numerical and interchange thresholds elsewhere in the full theorem remain separate.

In the pinned source this replaces the use of the general Jacobsthal bound in the proof of the witness in each descent. The window, test, axis list, density lemma and physical pairwise-gcd implementation can all be retained. See the [source's integer box](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/The-logarithmic-exponent-of-integer-multiplication-on-tapes-November-24-2026/build/integers.tex), [width and window scale](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/lean/OAI/Computability/NearSquareRoot/BoxScale.lean), [descending search and its success proof](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/lean/OAI/Computability/NearSquareRoot/CoprimeBox.lean), and [compiled pairwise gcd tests](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/lean/OAI/Computability/NearSquareRoot/BoxCoprimeTest.lean).

For the classical combinatorial sieve background, see D. Koukoulopoulos, *The Distribution of Prime Numbers*, chapter 19. The released source uses the stronger quadratic theorem for its own proof. This application of a coarse polynomial interval estimate supplies independent evidence for one step of the adaptive multiplier. [Sieve reference](https://dms.umontreal.ca/~koukoulo/documents/publications/primes.pdf)
