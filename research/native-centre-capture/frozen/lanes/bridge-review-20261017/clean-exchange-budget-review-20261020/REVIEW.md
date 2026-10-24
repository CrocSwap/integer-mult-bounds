# Independent review of the clean-exchange native budget

All eight serialized local words have the stated native and scalar
counts. A third independently written rational engine confirms
every strict budget threshold. No material defect was found.

The result is a conditional three-call native budget. It does not
provide a routed three-call composition, an initial Q entry, a
cleanup word, a recursive host, or a complete supplier. It does
not change the selected exponent.

## Sources and coverage

The budget producer freeze has SHA-256
`c2ee7b116d5b177c06b94fffb167354c3e6b49d759f2df16a4599eefded121d5`.
Its receipt has SHA-256
`30a59c5cda0ff3c6f9e6ad7f9f38ec98fbfe71d34c58ddf768964cda304ba30d`.

The clean local-word freeze has SHA-256
`96048355033e5f5bdd26dadddb869708faae6f8b0d9a61a1ae696e5a5c20c0bc`.
The separate dual-word freeze has SHA-256
`fa8f910fe7f22a696f47513c95e814588723dc8abaaa68061fcba3676c308d43`.
The independent clean local review has SHA-256
`6cd34040ecd7d832f1bae3d44c5a7b97dcc11022d843e48007c5474cc4f3701d`.

This review reads and checks those frozen bytes. It counts both
clean variants and both dual variants for each of the two native
providers. Every serialized event is counted. It does not rerun
the native phase or 640-column local map proofs. In particular,
its invoice check is not a new independent phase review of the
separate dual words.

The numerical engine comes from this lane's earlier independent
review, freeze
`953690464698b38801b4f2ddf0f56035203a9337214595a557c7d3950e2e6f87`.
No budget-producer code or either of its two numerical engines
is imported.

## Literal invoices

Each Q, inverse-adjoint, or selected-swap word has the profile

\[
1392H_1+64H_2+48H_3+16H_8.
\]

Its native rank is 1,792. Each I-entry word replaces the sixteen
H8 children by H9 children, for rank 1,808. Each word has
1,520 children.

The checker verifies the rank of every recipe. All native data
roles are between 0 and 223. In each Q or dual word, every
productive field has total native rank eight. In an I word,
sixteen fields have rank nine and the other 208 have rank eight.
Every individual child satisfies \(2r^2<25^2\).

Every scalar event uses a productive data role. The exact tariff
census for each word is:

| Operation tariff | Count | Subtotal |
| --- | ---: | ---: |
| Unit complex ADD, price 8 | 1,032 | 8,256 |
| SCALE, price 2 | 96 | 192 |
| SCALE, price 4 | 38 | 152 |
| Total | 1,166 | 8,600 |

The Q and dual words have 128 input views, 96 output views, and
at most 3,040 native side maps. Their total map bound is 3,264.
The I word has 112 input views, 96 output views, and at most
3,008 native side maps. Both side records of each direct H9
are literal identities, which the checker verifies. The I map
bound is 3,216.

Three Q calls therefore have 25,800 scalar primitives and a
map bound of 9,792. One I call and two Q calls have the same
scalar count and a map bound of 9,744. These are component
subtotals. They do not price a caller or map lowering.

## Historical exponent and exact arithmetic

The exponent is read directly from the selected certificate
and its bound assembly at commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`:

\[
b=\frac{67018507072324140917}{40000000000000000000000}.
\]

Both source hashes are checked. This is a historical pin,
not a statement about the current frontier.

For dimension 25, productive width 224, and no idle jobs,
the moment of a histogram H is

\[
M_H(b)=\sum_r H_r\frac{r}{5600}
          \left(\frac{25}{r}\right)^b.
\]

The third engine uses exact fractions. It reduces each
logarithm to the series

\[
\log x=2\sum_{j\geq0}\frac{z^{2j+1}}{2j+1},
\qquad z=\frac{x-1}{x+1},
\]

with \(0\leq z\leq1/3\). After 64 terms, its upper tail bound is
\(2z^{129}/(129(1-z^2))\). It bounds the exponential through
degree 20. For \(0\leq x<1/100\), its upper tail is
\(x^{21}/(21!(1-x/22))\). Outward rational rounding preserves
both bounds. No floating-point result determines a claim.

The new intervals lie inside the producer's displayed
intervals. The checker separately proves a strict upper
bound below one at every accepted count and a strict lower
bound above one at the next count.

## Confirmed limits

| Three-call profile | Native rank | Extra H1 limit | Extra H2 limit |
| --- | ---: | ---: | ---: |
| Three Q | 5,376 | 196 | 98 |
| One I and two Q | 5,392 | 180 | 90 |

After a hypothetical H1 cleanup, the limits are:

| Profile | Cleanup H1 | Further H1 limit | Further H2 limit |
| --- | ---: | ---: | ---: |
| Three Q | 112 | 84 | 42 |
| Three Q | 128 | 68 | 34 |
| Three Q | 144 | 52 | 26 |
| One I and two Q | 112 | 68 | 34 |
| One I and two Q | 128 | 52 | 26 |
| One I and two Q | 144 | 36 | 18 |

The cleanup rows are budget hypotheses. Their required queries,
scatter, views, phase correction, and restoration are not
constructed by these numbers.

A full 224-H1 terminal fails. With three Q calls its total
native rank is 5,600. Since each rank is less than 25, every
factor \((25/r)^b\) is greater than one for \(b>0\). Its moment
is therefore greater than one. The one-I case has rank 5,616
and fails already at \(b=0\). At the pinned positive exponent,
the terminal must save at least 28 or 44 H1 children,
respectively, before any other native cost is added.

## Sharp bounds for mixed extra ranks

Let \(c_r=r(25/r)^b/5600\). Since \(0<b<1\), the function
\(r^{1-b}\) is increasing and strictly concave.

For any mixture of H1 and H2 with total added rank m,
the largest possible moment increment is \(mc_1\).
The smallest is

\[
\left\lfloor\frac m2\right\rfloor c_2
 +(m\bmod2)c_1.
\]

The checker proves that the all-H1 bill at m=196 passes
for three Q calls, while the cheapest H1/H2 bill at m=197
fails. These minimum and maximum bills increase with m.
Thus every H1/H2 mixture is classified exactly:

\[
\boxed{n_1+2n_2\leq196.}
\]

For one I call and two Q calls the corresponding necessary
and sufficient condition is

\[
\boxed{n_1+2n_2\leq180.}
\]

These conditions concern only the stated conditional moment.
They do not admit a physical mixture of children.

The largest legal individual child rank is 17. For any fixed
total added rank m, strict concavity shows that the cheapest
histogram consists of \(\lfloor m/17\rfloor\) rank-17 children
and one child of rank \(m\bmod17\), if that remainder is nonzero.
To prove this, take two nonzero ranks below 17. Move rank from
the smaller to the larger until one becomes zero or the larger
becomes 17. Concavity cannot increase the cost. Repeat until
only one partial rank remains.

This packed minimum strictly increases with total rank.
Within a partial child, its increment is \(c_{r+1}-c_r>0\).
At a multiple-of-17 boundary, the increment is
\(c_{17}-c_{16}>0\); the next increment is \(c_1>0\).
Thus failure at the next total rank also excludes every
larger total rank in this fixed histogram.

The exact certificates give:

| Profile | Largest possible added rank | Passing best profile | Failing next best profile |
| --- | ---: | --- | --- |
| Three Q | 197 | \(11H_{17}+H_{10}\) | \(11H_{17}+H_{11}\) |
| One I and two Q | 181 | \(10H_{17}+H_{11}\) | \(10H_{17}+H_{12}\) |

Thus rank fusion in this fixed base histogram can buy at most
one rank beyond the H1/H2 budget. This does not exclude a new
base construction, a different productive width, or a changed
caller. It is not a general lower bound on centre encoding.

## Reproduction and credit

Run from this directory:

```text
python3 -I -B check_review.py --output normal
python3 -I -B -O check_review.py --output optimized
```

Both runs print `PASS_INDEPENDENT_CLEAN_EXCHANGE_BUDGET`.
Their `REVIEW-CHECKS.json` files must be byte equal.

The budget-geometry lane supplied the two-engine budget.
The root and controller lanes supplied the coupled interface.
The native lanes supplied the literal words and clean-word
review. The cover-algebra lane supplied the dual formulation.
This review adds the independent invoice, a third exact engine,
and the sharp mixed-rank consequences. AI agents prepared
these local records.

The budget producer independently checked the mixed-rank
proof and reran all eight extremal witnesses with both of
its exact engines. All strict signs agree. The review
record is in `PEER-REVIEW.md`.

No publication is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
