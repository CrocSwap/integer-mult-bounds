# The two-factor-seven obligation on the fixed chart-595 word

This is an independent scalar audit of PR #7697 at
`f55fc1434436ffa1c6d064a29fc56812044b3157`. The normalized graph has decoded
SHA-256 `d5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b`.
The result confirms its reported grid values. It also identifies every input
column that needs two factors of seven in a literal scalar product.

## Contract and result

Each of the 1502 entrances is an independent scalar. For a row v, use the
literal donor order in the graph and compute each product q times donor value
before its addition. Paid chart operations preserve the normalized coefficient
vector; their physical Clifford factors are outside this audit. Use one integer
scale G for entrance coefficients, products, addition prefixes and stored rows.

The least positive scale is `G = 45158400 = 2^12 * 3^2 * 5^2 * 7^2`.
The least scale for complete stored rows alone is
`S = 161280 = 2^9 * 3^2 * 5 * 7`. These are prior figures from the source.
There are 8738317 nonzero products in the independent-input expansion.
Exactly 630 products have a reduced denominator divisible by 49. They occur
in 40 rows: 60 in input column 281, and 570 in input column 1501. No other
input column needs 49. RESULT.json lists all 40 rows and their counts.

Thus both split owners are necessary to test the new two-factor obligation.
A check that uses only other basis inputs cannot see it. This is a scalar
support statement; it is not an assertion about a physical rank or a new
paid/target invoice.

## Sufficiency and minimality

Let a(v,i) be the rational coefficient of entrance i in row v. The graph is
acyclic in its literal schedule. Entrance donor `~i` has coefficient one in
column i and zero elsewhere. At each next row, the checker forms every
`q * a(donor,i)`, then adds the products in the stated order. It executes
integer multiplication and exact division at G. Every division has zero
remainder. Therefore every product and every addition prefix is on the grid.
The complete vector is retained for the next row.

For any finite rational coefficient set A and an integer G that clears A,
the least common denominator is
`G / gcd(G, {G*a : a in A})`. Apply this once to all products and once to all
complete stored coefficients. Integer addition introduces no new denominator.
The two gcds give G and S as stated. Necessity follows by setting one entrance
to one and all others to zero. Arbitrary integer entrance values are covered
by linearity. Multiplication by an external common dyadic input grid preserves
this scalar conclusion.

Separate Fraction replays compute one input column at a time. They do not
consume the integer replay vectors or its gcd state. These replays give the
following product witnesses for each maximal prime exponent:

| Prime power | Row | Donor | Input | Scalar | Donor value | Product |
| --- | ---: | ---: | ---: | --- | --- | --- |
| 4096 | 103161 | 88788 | 265 | 1/8 | 3/512 | 3/4096 |
| 9 | 99762 | 92704 | 1296 | 94/3 | 41/384 | 1927/576 |
| 25 | 96681 | 90728 | 1226 | -4/5 | 1/5 | -4/25 |
| 49 | 93859 | 87424 | 281 | -2/7 | -40/21 | 80/147 |

The last product explains why a row grid with only one factor of seven fails.
It is an actual pair of literal operations, not an estimate from path
length. The receipt also gives a separate first witness for fresh input 1501.
The checker rejects G divided by each of 2, 3, 5 and 7, using the respective
basis inputs. It also rejects S on each of the two split-owner inputs.
All six controls stop at their first nonzero division remainder.

## Interpretation and limits

This confirms the scalar precision sub-obligation requested in the chart-595
handoff. It does not establish the physical chart maps, root divisibility at
all column multiplicities, arbitrary dirty state, the early public return,
complete tape work, compiler funding or outer inequalities. It does not
reduce the source's conservative path grid or replace a provider. The complete
kappa is unchanged. All five selected assumptions remain.

The source's reported minimum values and its gcd method are credited. This
checker is separately written and imports no source verifier. The graph is
copied without change. Independent human review and formal-kernel acceptance
are not claimed.

## Open next questions

Can one accumulate integer row numerators and divide only after the complete
row? That contract can avoid off-grid temporary products, but it needs a
numerator-width bound, an exact division proof and a complete physical bill.
The present literal-product result does not prove that changed implementation.
