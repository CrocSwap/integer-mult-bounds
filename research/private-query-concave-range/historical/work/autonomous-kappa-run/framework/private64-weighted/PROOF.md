# Weighted optimum for private scalar queries

Result: PASS in the stated private scalar interface. For every
`0<b<=1/32`, the minimum query bill is

`8*8^(1-b)=64*8^(-b)`.

This is a cost statement about the fixed retained E8 Gram correction and
binary source labels. It supplies no new circuit or exponent saving. It
does not apply to a shared carrier, native block, productive source owner,
changed encoding or changed controller.

## Model and retained proof inputs

Write the fixed correction as `G=sum_j u_j f_j`, over Q, R or C. Each
scalar query row `f_j` is delivered privately from a SOURCE frame `F_j`
that contains its support. Let `r_j=dim(F_j)`, with `1<=r_j<=9`. Its bill
is `r_j^(1-b)`. A common factor from the outer dimension is immaterial:
the recurrence term for these children is
`m^(b-1)*sum_j r_j^(1-b)`.

Drop zero rows and retain an independent basis of the query rows. Absorb
the removed row coefficients into the decoder columns. This operation
does not change G and removes positive private query charges. The retained
query space contains the eight-dimensional Gram code W. Any lower bill
would therefore have an independent-row factorization with a lower bill.

The saved sharp rank theorem excludes `sum_j r_j<64`. Its proof and final
bindings are in `../PRIVATE64-INDEPENDENT-REVIEW.md` and
`../PRIVATE64-FINAL-BINDING.json`. That theorem includes the two final
algebraic profile closures; the new check does not replace them.

The necessary conditions for total 64 use the same independently checked
frame capacities
`[0,1,2,4,8,12,20,36,64,112]` and generalized code supports
`[53,76,92,100,106,109,111,112]`.
For N independent queries, any k-subset meets W in dimension at least
`k+8-N`. Its support union must meet the relevant code support bound.
Total query incidence is at least `224-N`. Discrete concavity of subset
coverage gives the saved balanced-incidence average-union bound.
For N=9, a rank-six/rank-seven pair cannot cover a code root: their root
intersections contain at most `20+32=52` ports, fewer than 53.

## Total rank 64

The new nondecreasing-rank recursion covers all 195,666 rank partitions
of exactly 64 with parts in 1 through 9. A separate coefficient dynamic
program gives the same partition count. The exact necessary tests reject
84,690 profiles by incidence, 110,944 by generalized support, 24 by the
average-union bound and two by the short-root-pair argument.

Exactly six profiles remain:

| Necessary-condition survivor | Rank sum |
| --- | ---: |
| `1,1,6,7^8` | 64 |
| `1,6,7^7,8` | 64 |
| `1,7^9` | 64 |
| `2,6,7^8` | 64 |
| `7^8,8` | 64 |
| `8^8` | 64 |

These are necessary-condition survivors, not six constructed
factorizations. Every part is at most eight. Thus, for every `b>0`,

`sum_j r_j^(1-b)=sum_j r_j*r_j^(-b)>=sum_j r_j*8^(-b)=64*8^(-b)`.

Equality requires every part to equal eight. The literal eight coordinate
gathers and decoder `R/4` attain that profile. Their eight SOURCE support
ranks were reconstructed in the saved geometry check. No other total-64
profile can reduce the weighted bill.

## Every larger rank total

Put `q=sum_j r_j`. Since every `r_j<=9`,

`sum_j r_j^(1-b)>=q*9^(-b)`.

Relative to the eight-gather bill, the ratio is at least
`(q/64)*(8/9)^b`. The elementary strict bound `log(9/8)<1/8` and
`exp(-x)>=1-x` imply, for `q>=65` and `0<b<=1/32`,

`bill/reference > (65/64)*(1-1/256)=16575/16384 >1`.

This handles every finite larger profile at once. No increasing-cost
enumeration is needed. At the requested generous ceiling
`B=0.00396314`, the sharper uniform lower ratio is
`5197423959/5120000000 >1`.

The rank theorem, the exact-total screen and this larger-total bound
prove the stated weighted optimum throughout the current construction's
admitted complex-saving range. They do not prove optimality of the whole
controller or multiplication algorithm.

## Certified prices and controls

The independent rational series engine uses 60 logarithm terms,
30 exponential terms and outward rounding to a `10^-60` grid. It imports
no producer price engine. It compares each surviving profile at the
fresh PR569 complex saving
`400657953443603669637/250000000000000000000000` and at B.
All non-reference differences are strictly positive. Equality for `8^8`
is exact. The analytic inequalities above cover the whole interval,
including arbitrarily small positive b; two endpoint samples alone would
not establish that interval statement.

The controls show why rank sum by itself was insufficient. The unbuilt
profile `1,9^7` also totals 64 and has a strictly lower weighted bill at
the current b. Its singleton row violates the one-dimensional Gram code
support bound. It is not a factorization. Likewise, the unbuilt block
profile `16^4` has a lower bill, but violates the private SOURCE rank-nine
interface. It supplies no block circuit or paid implementation. Both
strict numerical comparisons use exact certified bounds.

An optimized-Python control rejects before reading inputs. The initial
successful screen is retained. All original private64, frontier and
proposal files remain unchanged.

Reproduce from the autonomous run directory with a new result path:

```sh
venv/bin/python -B framework/private64-weighted/check_weighted.py . \
  /tmp/private64-weighted-result.json
```

The final run passed, exit zero, in 0.859 seconds. The finite result is
`RESULT.json`; exact command, log hashes and exit status are in
`COMMAND.json`. The proof is not a Lean formalization or an all-size
compiler theorem.

Prepared with OpenAI Codex assistance.
