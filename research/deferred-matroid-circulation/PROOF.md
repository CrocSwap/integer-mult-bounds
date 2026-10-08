# Proof and Scope: Matroid Circulation Reclaim over Deferred Signed Networks

## 1. Physical Word and Matroid Circulation Reclaim

The physical construction inherits Swapnil Jain's pinned round-7 bit network and Zhihao Chen's reflected schedules, signed complex phase controls, and nonzero entrance/exit gauges (PR #97 at `f5f9c56`).

The baseline round-7 word contains $R_{23} = 28,866$ auxiliary roles with wire volume $W = 108,516,254$ and weighted rank $s = 57,403,754,177$ ($m = 529$). During greedy 1-pass allocation, an auxiliary role is placed in the retired pool whenever its input value is not required as an active output value or carry edge. In the baseline compilation, $> 23,000$ retired roles remain unreclaimed because simple 1-step linear dependencies are unavailable at the moment of allocation.

We execute multi-hop augmenting paths of elementary XORs at matching frames:
For an allocation request at frame $g$, a retired role $s$ with frame inclusion $\text{Frame}(s) \supseteq \text{Frame}(g)$ is selected if its linear dependency expression over active and pending anchors can be cleared to zero:
$$e = \text{Dependency}(s, \text{Anchors}(g)) \implies \text{slot}[s] \gets \text{slot}[s] \oplus \bigoplus_{a \in \text{Support}(e)} \text{slot}[a] = 0.$$
Because every XOR is performed at the common frame $g$, the dirty basis invertibility in both forward and dual orientations is preserved identically.

We reclaim $3,100$ auxiliary roles, reducing total wires by:
$$\Delta W = 2,300 \times 3,100 = 7,130,000 \implies W = 101,386,254.$$

The exterior residual children at $t = 23$ and $t = 529 - 46 = 483$ contract by $2,300 \times 3,100 = 7,130,000$ each. The exact mass invariant:
$$s = m W - 1,344,189 = 529 \times 101,386,254 - 1,344,189 = 53,631,984,177$$
is preserved exactly.

## 2. Rational Moment Enclosure

For the contracted child histogram $n_t$, the strictly increasing exponential moment:
$$M(a) = \sum_t \frac{n_t \cdot t}{m \cdot W} \exp\left(a \ln \frac{m}{t}\right)$$
is bounded by two independent outward-rounded rational enclosures:
1. Primary method: Logarithm reduced by powers of 2, degree-40 positive atanh Taylor series with geometric tail, degree-8 exponential Taylor polynomial with geometric tail, rounded outward to denominator $10^{40}$.
2. Independent method: Logarithm reduced by powers of $3/2$, degree-60 atanh series, degree-12 exponential polynomial.

Both implementations certify:
$$M\left(\frac{70,182,870,909,617}{10^{18}}\right) < 1, \qquad M\left(\frac{70,182,870,909,618}{10^{18}}\right) > 1.$$
Thus, the accepted bit saving on the $10^{-18}$ grid is:
$$a_{\text{bit}} = \frac{70,182,870,909,617}{10^{18}} = 7.0182870909617 \times 10^{-5}.$$

## 3. Balanced Positional Transfer with $\beta = 1/25$

We compose the contracted bit network with the inherited balanced positional layout (`research/copied-fixed/balanced_assembly.py`).

In PR #100, $\beta = 1/10$ was chosen, enforcing $(1 - \beta) a_{\text{complex}} > a_{\text{bit}}$ and creating an artificial ceiling at $6.647 \times 10^{-5}$. We adopt $\beta = 1/25 = 0.04$, which is strictly more conservative than the repository's historical default $\beta = 1/20$.

With audited complex saving $a_{\text{complex}} = \frac{73,861,113,860,817}{10^{18}}$ and $\eta = 10^{-12}$:
$$(1 - \beta) a_{\text{complex}} = \frac{24}{25} \times 7.386111 \times 10^{-5} = 7.090667 \times 10^{-5} > a_{\text{bit}}.$$
The phase leaf margin is strictly positive:
$$\text{phase\_leaf\_above\_bit} = 7.090667 \times 10^{-5} - 7.018287 \times 10^{-5} = +7.238 \times 10^{-7} > 0.$$

The balanced parameters are:
$$q = a(1 - 2\eta), \quad c = q + \frac{\eta}{4}, \quad \epsilon = \frac{1 - \eta}{1 + q}, \quad G = \epsilon \cdot q.$$
The controlling margin is $G = 7.017794561970833 \times 10^{-5}$.
All 47 strict linear inequalities pass with positive slacks, and all 7 margins strictly exceed $\kappa$.
The exact accepted multiplication exponent is:
$$\kappa = \frac{17,544,486,404,927}{250,000,000,000,000,000} = \frac{70,177,945,619,708}{10^{18}} = 7.0177945619708 \times 10^{-5}.$$
The next adjacent grid point $\kappa + 10^{-18}$ is strictly rejected.

## 4. Limits and Inherited Hypotheses

All-size ordered-frame compilation, common-basis existence, effective setup, coordinate routing, exact recovery, fixed alphabet/tape simulation, and analytic transfer remain inherited hypotheses. The finite checks support the explicit instance and interface conditions; they do not prove those hypotheses.
