# Sharp contraction under a reserve-imbalance cap

This scoped written proof was produced by Nick Petalas. Apache-2.0.

## Contract

Let R1 and R2 be finite nonempty menus of nonnegative real rows of length
two. Write a first-type row as (a,b) and a second-type row as (c,d).
As in Ali Romman's [PR6472](https://github.com/CrocSwap/integer-mult-bounds/pull/6472),
each row choice is independently legal, and each row must already include
the complete costs of its declared children, adapters and restoration.
That interpretation is a premise, not proved for a physical supplier here.

For B >= 1, define

```text
q_B = min max { a + b*w2/w1, d + c*w1/w2 : (a,b) in R1, (c,d) in R2 },
```

where the minimum is over w1,w2 > 0 with
max(w1,w2)/min(w1,w2) <= B. Only their ratio matters. Setting x=w2/w1
reduces the domain to the compact interval [1/B,B], so the minimum exists.

## Closed form

For one row pair put

```text
lambda(a,b,c,d) = (a+d + sqrt((a-d)^2 + 4*b*c))/2.
```

Then the exact answer for all finite menus is

```text
q_B = max {
    max_(a,b) [a+b/B],
    max_(c,d) [d+c/B],
    max_(a,b),(c,d) lambda(a,b,c,d)
}.
```

In particular, different row pairs may bind at different parameters. Checking
only a designated whole matrix would omit independently legal combinations.
Zero rows, zero off-diagonal entries, ties and q_B=0 are allowed.

### Necessity

If x in [1/B,B] is feasible at rate q, then
q >= a+b*x >= a+b/B and q >= d+c/x >= d+c/B.
Also q-a >= b*x and q-d >= c/x. Both left sides are nonnegative, so
(q-a)(q-d) >= b*c for every pair.

For q >= max(a,d), this last inequality is equivalent to q >= lambda.
Indeed the quadratic (q-a)(q-d)-bc is nondecreasing on that half-line,
and lambda is its larger root. Thus every feasible rate is at least the
displayed maximum.

### Sufficiency and the complete weight interval

Suppose q is at least every term in the displayed maximum. Define

```text
L(q) = max { 1/B, c/(q-d) for rows (c,d) with c>0 },
U(q) = min { B, (q-a)/b for rows (a,b) with b>0 }.
```

The reserve-boundary terms ensure q>d whenever c>0 and q>a whenever b>0.
Thus all displayed quotients are well-defined and positive. They also give
c/(q-d) <= B and 1/B <= (q-a)/b. Finally the row-pair term gives
c/(q-d) <= (q-a)/b whenever both quotients occur. Every lower candidate
is therefore at most every upper candidate, and L(q) <= U(q).

For any x in [L(q),U(q)], rows with positive b or c obey the required
inequalities by construction. A row with b=0 requires only q>=a; a row
with c=0 requires only q>=d. The boundary terms already ensure both.
Conversely every feasible x must belong to this interval. Hence [L(q),U(q)]
is exactly the entire feasible ratio set. At q=q_B it is the entire
minimizer set. This proves the formula and supplies explicit weights (1,x).

## Exact rational certificates

Suppose the rows and B are rational. For any rational proposed q>=0,
feasibility is decidable without square roots. Check the two boundary
families and all row-pair determinant inequalities. The boundaries imply
q>=max(a,d), so no extraneous lower quadratic branch is admitted. If they
pass, the endpoints L(q),U(q) are rational and give rational witnesses.

Positive rational weights attain q_B if and only if q_B is rational.
If q_B is rational, the interval just constructed has rational endpoints.
Conversely every row ratio evaluated at rational weights is rational;
the maximum of finitely many rational values is rational. Density and
continuity on [1/B,B] imply that the rational infimum is always q_B, even
when it is not attained. The case B=1 has the single rational ratio x=1.

This is a certificate statement, not a polynomial bit-complexity claim for
arbitrary algebraic inputs. The verifier implements only rational thresholds.

## A literal reserve transition

Consider the new synthetic menu

```text
R1 = {(0,1/2), (1/8,1/4)},
R2 = {(1/4,0), (1/16,1/8)}.
```

Its four pair roots are sqrt(2)/4, (1+sqrt(17))/16, 1/4 and 1/4.
The second is smaller than the first. To see this, 4*sqrt(2)-1 is
positive, and its square exceeds 17 because 16>8*sqrt(2).
The remaining roots are smaller as well. The boundary terms other than
1/(2B) are

```text
1/8 + 1/(4B), 1/(4B), 1/8 + 1/(16B).
```

For 1<=B<=sqrt(2), each is at most 1/(2B): the first comparison uses
B<=2, and the last uses B<=7/2. For B>=sqrt(2), these decreasing terms
are at most their values at sqrt(2), each below sqrt(2)/4. Therefore

```text
q_B = max { 1/(2B), sqrt(2)/4 }.
```

For B<sqrt(2), the first row forces the unique optimum x=1/B. For
B>=sqrt(2), the first rows of the two menus force x=1/sqrt(2).
Thus rational B<sqrt(2) admits rational optimal weights, while rational
B>sqrt(2) does not. For instance B=7/5 gives the exact certificate
x=5/7 and q=5/14. The menus and this reserve law are introduced here;
they are not PR6472's or PR6555's synthetic menu.

## All-depth consequence of the same cap

Let T(v)_i be the largest allowed row product at type i. Suppose q<1
and w is a feasible positive weight. For the adaptive unit-toll recurrence
x_0=0 and x_(k+1)=1+T(x_k), the weighted maximum norm is contracted by
q. This follows from

```text
|T(v)_i-T(z)_i| <= max_(r in Ri) r*|v-z| <= q*w_i*||v-z||_w.
```

Consequently 1+T has a unique fixed point u, its finite-depth iteration
converges to u, and 0<=u-x_k componentwise. Its error obeys

```text
||u-x_k||_infinity / ||u||_infinity <= B*q^k
```

for every integer k>=0. Indeed weighted contraction bounds the error by
q^k*w_i*max_j(u_j/w_j), and converting to the ordinary maximum norm
costs at most max(w)/min(w)<=B. For the literal menu above, substitution
checks the fixed point u=(12/7,10/7). This is an abstract accounting tail,
not physical retained stock or a source-bound compiler cutoff.

## Credit, originality and limits

Ali Romman's PR6472 supplies the independent-row accounting interface,
its unit-toll semantics and the explicit common-ratio optimization question.
Classical two-by-two Perron roots, positive diagonal scaling, weighted
norms and contraction arguments are credited as established mathematics.
Global theorem priority for these classical methods is unclaimed.

Nick Petalas's older PR6555 treats exactly one unbounded synthetic menu,
including its rational approximation and a cutoff. Those results are cited
as background; their menu, identity, construction and cutoff are not used
as the main step here. The contribution is the explicit arbitrary-menu
reserve-cap law, complete minimizer interval and rational-attainment criterion
at the repository's adaptive-row interface, with the new transition fixture.

No actual supplier row menu is bound. Independent physical legality,
complete native charges, compiler closure, ownership, stock, precision/tape
and analytic recovery remain separate obligations. No selected-frontier
change, new kappa or complete multiplication theorem follows. The universal
claim rests on this written proof; finite checks corroborate it.
Independent human and formal proof-kernel review are unclaimed.
