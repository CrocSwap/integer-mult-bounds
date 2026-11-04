# Computing and certifying the price

## Exact algorithms

For the list of $h$ nonzero charges (or the augmented binary list), precompute $\Sigma(S)$ for every labeled subset. Any order of a zero-total list cuts into zero-sum blocks at its zero prefix sums. Conversely, concatenating any zero-sum partition yields at least that many boundaries. Thus the maximum number of zero-sum blocks is given by

~~~text
P(empty) = 0
P(S) = [sum(S)=0] + max_{i in S} P(S without i).
~~~

Store an attaining predecessor, recover the order, then cut at its zero sums. The comparison and reconstruction are independent of the cost of constructing the actual row additions. PROOF.md supplies those additions. For vectors of width $d$, the labeled DP uses $O((h+d)2^h)$ field/index operations and $O((d+1)2^h)$ stored entries, plus the explicit gates. With $t$ fixed charge types of multiplicities $n_i$, use a count vector instead of a subset. This needs at most $\prod_i(n_i+1)$ states and $O((t+d)\prod_i(n_i+1))$ operations. For fixed field and fixed slope dimension this is polynomial in the number of labeled coordinates. A minimizing word is easy to check by actual multiplication once its partition is known.

## Small scalar fields

An inverse pair $x,-x$ can always be placed together in a maximizing partition. If they were in different blocks, extract the pair and unite the two remainders, whose total is zero. If they were together in a larger block, splitting the pair off gives an additional block. Thus canceling all existing inverse pairs is safe. Arbitrary choices of larger zero-sum subsets need not preserve the maximum.

For scalar slope charges of total zero, the following give $Z$, before charging $h-Z$ additions.

* Over $\mathbb F_2$, $Z=h/2$.
* Over $\mathbb F_3$, let $A,B$ be the counts of $+1,-1$. Pair opposite signs and make triples from the remaining equal charges. This gives $Z=\min(A,B)+|A-B|/3$.
* Over $\mathbb F_4$, the three nonzero elements sum to zero, and all three multiplicities have the same parity. Pair identical elements. If the three counts are odd, the remaining three elements form one block. This attains $Z=\lfloor h/2\rfloor$ since every block needs at least two entries.
* Over $\mathbb F_5$, remove inverse pairs and count them separately. At most two types remain. After multiplication by a unit and possibly exchanging them, these are $1,2$ with counts $A,B$ (a single type makes blocks of five). The remaining maximum is
  $\min((A+2B)/5,(3A+B)/5)$. Both terms are integers. For the first upper bound give an entry of type one weight one and an entry of type two weight two. Every zero block has total weight at least five. For the second bound use weights three and one, respectively. These are also related by doubling modulo five. If $B\ge2A$, take $A$ blocks $(1,2,2)$ and split the remaining twos into groups of five. If $B\le2A$, start with $(A+2B)/5$ blocks of weight five. Allocate the $B$ twos to the blocks, at most two per block, and use ones to fill each remaining weight. This attains the respective smaller bound.

For example the charges $(1,1,1,2,4,4,4,3)$ over $\mathbb F_5$ split into four inverse pairs. Greedily taking the first four labels instead leaves two indivisible blocks of four. The resulting six additions exceed the attainable four.

## Complexity with a variable prime field

Consider the anchored full-pencil decision problem, with a supplied prime field, one slope row, and a budget $L$. This problem is strongly NP-complete. Membership in NP follows from the partition theorem (or from a word of at most $h-1$ additions and polynomial-time row operations). This statement concerns variable field order. The fixed-alphabet algorithm above has different parameters.

Use the bounded-integer 3-PARTITION problem. Its $3n$ positive integers $a_i$ satisfy $B/4<a_i<B/2$ and have total $nB$. Choose a prime $p>nB$ of polynomial size. Bertrand's postulate allows a prime at most $2nB$ when $nB>1$. On the strongly NP-hard bounded-integer restriction, trial division across this interval is polynomial. Small trivial inputs can be decided directly. Use $3n$ positive charges $a_i$ and $n$ charges $-B$ in $\mathbb F_p$, plus an additional zero-slope carrier. Set every $u_i=1$, take $b$ to select the carrier, and use those charges as the slope row. The normalized full pencil has exactly the required form. [Garey and Johnson, 1975](https://doi.org/10.1137/0204035)

Each block has integer sum between $-nB$ and $nB$, so modular zero means integer zero. Every nonempty zero block must include a negative entry. Thus $Z\le n$, with equality precisely when each block uses one $-B$ and positive entries summing to $B$. The strict size conditions require exactly three positives. The price $4n-Z$ is at most $3n$ precisely for yes-instances. Even explicitly listing all $p$ guards takes only polynomial space on this restriction. This transfers a classical debt-clearing obstruction to a priced finite-field header. The classical transaction problem and its hardness have earlier literature. [Pătcaș and Bartha, 2019](https://doi.org/10.2478/ausi-2019-0010)
