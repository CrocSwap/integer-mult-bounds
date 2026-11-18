# Exact-sum rounding needs forward slack at least sqrt(13)-3

Let G=Z[i]. For x,y in G, put s=x+y, d=x-y and
`C_+(x,y)=((s+i*d)/2,(s-i*d)/2)`. Use the Euclidean norm on G^2.
Let F:G^2 -> G^2 be injective, preserve s exactly, and satisfy
||F(z)-C_+(z)|| <= 1 at every input. Define its forward slack as
sup_z max(0,||F(z)||-||z||).

**Theorem.** The forward slack is at least beta=sqrt(13)-3.
On the finite sum-one domain with squared norm at most 13, beta is the
exact minimum. No period, phase covariance, square identity, inverse
contract or surjectivity is assumed.

This improves the necessary bound alpha=sqrt(5)-sqrt(3) from
[Nick Petalas's PR #7652](https://github.com/CrocSwap/integer-mult-bounds/pull/7652).
That proof supplies the question and the candidate formula. The formula
is derived again below. The new obstruction has 18 inputs and 16 neighbors.
The equality certificate covers all 22 inputs of the larger finite domain.

## Complete candidate sets

In the sum-one fiber write `x=a+i*b` and y=1-x. The squared pair norm is
`N(a,b)=a^2+(1-a)^2+2*b^2`. The first ideal output is
`(1/2-b)+i*(a-1/2)`. Exact sum makes the second output one minus the first.
If the first output is `c+i*e`, the pair error squared is
`((2*c-1+2*b)^2+(2*e-2*a+1)^2)/2`.
Both terms inside the squares are odd integers. Error at most one holds
exactly when both terms have absolute value one. Thus the complete legal
candidate set is {-b,1-b} x {a-1,a}. All four candidates have error one.
This argument excludes every other Gaussian-integer output, not only
outputs in a search box.

## The Hall obstruction

Put B={ (a,b):N(a,b)<=9 } and S=B union {(-2,0),(3,0)}.
The two extra inputs have squared norm 13. The rows below give every
output squared norm for each input of S; repeated output norms do not
mean repeated vertices.

| Input squared norm | Number of inputs in S | Candidate output squared norms | Allowed norms at slack strictly below beta |
| ---: | ---: | --- | --- |
| 1 | 2 | 1,1,3,3 | 1 |
| 3 | 4 | 1,3,5,7 | 1,3,5 |
| 5 | 2 | 3,3,9,9 | 3 |
| 7 | 4 | 3,7,9,13 | 3,7,9 |
| 9 | 4 | 5,7,13,15 | 5,7 |
| 13 | 2 | 9,9,19,19 | 9 |

There are 16 points in B and 18 points in S. Every allowed output in
the last column belongs to B. In fact the union of the strict candidate
sets equals B, as the explicit certificate checks. Therefore a map with
slack below beta sends 18 distinct inputs into at most 16 distinct outputs.
It cannot be injective. This proves the lower bound on the entire domain.

All comparisons in the table are strict except the omitted 9 -> 13 gap,
which equals beta. They can be checked by positive squaring. For a useful
rational separation, 0.60 < beta < 0.61; all other allowed positive gaps
in this table are below 0.51, and all excluded positive gaps are above 0.73.
The verifier uses tighter rational brackets and an integer square test,
with no floating-point comparison.

The conclusion applies even if the map has arbitrary behavior off S.
It does not claim that beta is attained on all of G^2.

## Equality on the complete finite domain

The domain D={ (a,b):N(a,b)<=13 } has 22 inputs. The inequalities in N
imply -2<=a<=3 and -2<=b<=2, so enumeration of this box is complete.
[MATCHING.json](MATCHING.json) gives one output for every point of D.
All outputs are distinct. Each output is one of the four legal candidates,
and each radial gap is at most beta. At least one 9 -> 13 edge is present.
The Hall lower bound and this explicit matching prove the exact finite
optimum. The four inputs in D minus S have not been omitted from this
attainment statement.

For an independent geometric check, write the input as
(a,b,1-a,-b). Twice the ideal output is H times this real vector, where

```text
H = [ 1 -1  1  1 ]
    [ 1  1 -1  1 ]
    [ 1  1  1 -1 ]
    [-1  1  1  1 ].
```

The verifier checks H^T H=4I and computes every error directly with this
matrix. A separate augmenting-path search gives maximum matching sizes
20 below beta and 22 at beta on D. This search does not read the retained
matching as a search guide. The written Hall proof and explicit matching
suffice without trusting a maximum-matching implementation.

## Exact comparison and scope

For integers A,B>=0 and positive p/q, set `r=(B-A)*q^2-p^2`.
Then sqrt(B)-sqrt(A)<=p/q exactly when r<=0 or
`r^2<=4*A*p^2*q^2`. This follows by moving the nonnegative radical term
and squaring only when its other side is positive.
The verifier brackets beta between
605551275463989293/10^18 and 605551275463989294/10^18.
Every non-tied edge is separated from this interval; the ties have
(A,B)=(9,13). Thus the complete edge decisions are exact.

The lower bound alpha from PR #7652 is below 0.51, while beta is above
0.60. This is a stricter necessary global bound, not only a larger
finite census. PR #7570 gives the distinct global upper bound
sqrt(19)-sqrt(13) for a class with a square-to-swap identity. That source
proof was read but its verifier was not run here. Global attainment for
the present weaker class, a physical map, precision/range bounds, inverse
behavior, a caller and all implementation costs remain open. There is
no change to kappa or any of the five selected assumptions.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Credit Nick Petalas for PR #7652, Jerry Chen for the fixed-sum matching
context in PR #7570, and Ali Romman for the ideal pair in PR #6509.
The finite witness, matching and verifier here are new. No source code
was copied. Apache-2.0. Independent human and formal-kernel review are
not claimed.
