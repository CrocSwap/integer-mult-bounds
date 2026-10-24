# Principal demand ideals characterize single-insertion dirty fanout

**Scoped written proof with exact finite corroboration; no new κ.**
For every finite commutative ring with identity and every nonzero two-row
demand, one source insertion is possible **if and only if the ideal generated
by the two demands is principal**. When possible, either row can receive the
insertion, with at most four row additions. Combining this criterion with
Krzysztof Wójt's [#5045](https://github.com/CrocSwap/integer-mult-bounds/pull/5045)
lower-bound classification gives the exact optimum at every positive price.
This answers Open next question 1 of
[#5089](https://github.com/CrocSwap/integer-mult-bounds/pull/5089).

The eight-element ring below supplies an obstruction absent from residue rings:
its demand `(epsilon,eta)` requires at least two source insertions. Its exact
price envelope has three terms, whereas blindly extending the residue-ring
five-term formula can underprice it by almost a factor two.

## Model and exact price formula

Let R be a finite commutative ring, with `1 != 0`. For arbitrary independent
`a_0,a_1,p in R^w`, `w >= 1`, start with `A_i=a_i` and require

    A_0 = a_0 + lambda_0 p,     A_1 = a_1 + lambda_1 p,

while preserving the disjoint source p. Use only a fixed finite straight-line
word in the gates

    P_i(beta):  A_i <- A_i + beta p,          price mu_i > 0;
    E_i(alpha): A_i <- A_i + alpha A_(1-i),   price c_i > 0.

The four prices are finite, arbitrary positive real numbers, stationary and
independent of coefficients. In particular, `c_i` prices the direction **into
row i**. These are the predecessor's complete abstract gate prices. Both original
dirt columns must return exactly; there are no extra rows, free basis changes,
clearing, intermediate observations or input-dependent choices. An inverse
execution, if required, is paid separately. Zero-coefficient calls may be deleted.

Write `I=(lambda_0,lambda_1)` for the generated ideal and `j=1-i`. Define

    D   = [lambda_0 != 0] mu_0 + [lambda_1 != 0] mu_1,
    T_i = 2 mu_i + 2 c_j.

If I is not principal, set `S_0=S_1=+infinity`. Otherwise set

          { mu_i                       if lambda_j = 0,
    S_i = { mu_i + 2 c_j               if lambda_j != 0 and lambda_j in R lambda_i,
          { mu_i + 2 c_i + 2 c_j       otherwise.

**Theorem.** In this contract,

    OPT = min(D, T_0, T_1, S_0, S_1).

For nonzero demand, S_i is exactly the least price among words with one
nonzero source insertion at row i, whenever I is principal. If I is not
principal, such words do not exist. At zero demand the empty word costs zero;
no word with exactly one **nonzero** insertion reaches zero. Equivalently,
including zero: **at most one insertion suffices if and only if I is principal**.
The finite S values at zero are harmless upper bounds, not costs of nonzero
single-insertion words.

## The eight-element obstruction and sharp construction

Take

    R = F_2[epsilon,eta] / (epsilon^2, epsilon eta, eta^2).

Its elements are `a+b epsilon+c eta`, with a,b,c binary. Its four units have
`a=1`. Its radical `m={0,epsilon,eta,epsilon+eta}` squares to zero. A nonzero
radical element u generates exactly `{0,u}`: multiplication by a unit leaves
u unchanged and multiplication by a radical element kills it. A unit generates
all of R. Consequently m has four elements and is **not principal**.

For demand `(epsilon,eta)`, the theorem gives

    OPT = min(mu_0+mu_1, 2 mu_0+2 c_1, 2 mu_1+2 c_0).

The following chronological words attain the three terms exactly. Characteristic
two makes each negative coefficient equal its positive counterpart.

| Word | Gates | Counts `(P_0,P_1,E_0,E_1)` |
|---|---|---|
| D | `P_0(epsilon), P_1(eta)` | `(1,1,0,0)` |
| T_0 | `E_1(1), P_0(eta), E_1(1), P_0(epsilon+eta)` | `(2,0,0,2)` |
| T_1 | `E_0(1), P_1(epsilon), E_0(1), P_1(epsilon+eta)` | `(0,2,2,0)` |

Every legal word dominates one of these three count vectors, by the proof
below, so they form the exact Pareto frontier. In price order
`(mu_0,mu_1,c_0,c_1)`, they are uniquely cheapest at `(1,1,1,1)`, `(1,9,1,1)`
and `(9,1,1,1)`, respectively. For `(100,1000,1,1)`, the true optimum is
**202**. Including the unavailable single-insertion term incorrectly predicts
**104**. This refutes that extension of #5089's formula, not its residue-ring
theorem.

## Proof of the single-insertion criterion

### Necessity: invertible changes preserve the generated ideal

Suppose a word has exactly one nonzero source insertion `P_i(beta)`. Before
that insertion the source column is zero. Let M be the product of all row
gates after it. The final column is `lambda=M(beta e_i)`. Each row gate is
invertible, with inverse obtained by negating its coefficient. Every coordinate
of lambda is a multiple of beta, so `I subseteq (beta)`. Conversely,
`beta e_i=M^(-1) lambda`, so beta is a linear combination of the demands and
`(beta) subseteq I`. Thus `I=(beta)` is principal.

This implication works over every commutative unital ring; finiteness is not
used. Invertibility also implies that nonzero beta cannot give zero demand.
Restoration of dirt adds a constraint to legal words, but is not needed for
this necessary condition.

### Finite-ring coefficient-selection lemma

**Lemma.** If `(x,y)` is principal in a finite commutative ring R, there
exist a,beta,r in R with

    beta = x-a y,     y = r beta,     x = (1+a r) beta.

For x=y=0 take all three coefficients zero. Otherwise choose a generator
gamma of `(x,y)` and write `x=u gamma`, `y=v gamma`. Since gamma belongs
to `(x,y)`, there are s,t with `gamma=sx+ty`. Hence

    (su+tv-1) gamma = 0.

The annihilator `J=Ann(gamma)={z:z gamma=0}` is a proper ideal. In the
nonzero finite commutative quotient `B=R/J`, the images of u,v satisfy
`s_bar u_bar+t_bar v_bar=1`. They cannot both belong to any maximal ideal.

B has finitely many maximal ideals. Distinct maximal ideals are comaximal:
their sum strictly contains either unless they are equal. Prescribe a_bar
modulo each maximal ideal q by

    a_bar = 0 mod q    if u_bar is not in q;
    a_bar = 1 mod q    if u_bar is in q.

The Chinese remainder theorem supplies a simultaneous a_bar. In the second
case v_bar is not in q, so `u_bar-a_bar v_bar=-v_bar mod q` is nonzero;
in the first case it is `u_bar mod q`, also nonzero. Thus
`b=u_bar-a_bar v_bar` lies outside every maximal ideal. It is a unit: if
its principal ideal were proper, that ideal would be contained in a maximal
ideal (existence follows from finiteness), a contradiction.

Lift a_bar to a in R and set `beta=x-a y`. Choose r lifting `v_bar b^(-1)`.
Then `v-r(u-av)` belongs to J; multiplying by gamma gives `y=r beta`.
The identity `x=beta+a y` gives the third formula. These equations also show
`(beta)=(x,y)`. Only b is inverted **in the quotient**; gamma and beta need
not be units in R. This is the elementary finite-ring stable-range-one
argument, applied to the annihilator quotient. CRT and that classical
algebraic mechanism are not new claims.

### Sufficiency with full dirt restoration

For a prescribed insertion row i, apply the lemma with
`x=lambda_i,y=lambda_j` and execute

    E_i(-a), E_j(-r), P_i(beta), E_j(r), E_i(a).

On the original dirt columns, the first two gates are the inverse word of
the last two, so their product is identity. The source column, zero before
the insertion, subsequently evolves as

    beta e_i -> beta e_i + r beta e_j
             -> (1+a r) beta e_i + r beta e_j.

This is the desired demand. For nonzero I, beta is nonzero because it
generates I. The word uses one insertion and at most four row gates, at
either choice of insertion row, proving the criterion.

Given finite operation tables, one can enumerate a until `(x-a y)=(x,y)`,
then enumerate r until `r(x-a y)=y`. The proof ensures termination. This
is the verifier's witness-selection algorithm; no efficiency claim in a
compressed presentation of R is made.

## Arbitrary-word lower bound and all attaining words

We credit and restate #5045's lower-bound classification and standard words.
Setting p=0 leaves the dirt matrix, which must return to identity. A nonzero
row-addition direction cannot occur exactly once. With just one upper shear
U(alpha), all other dirt gates are lower shears. Combining those before and
after it gives `L(b) U(alpha) L(c)`, whose upper-right entry is alpha.
It cannot be identity. Exchange the rows for the other direction. Thus every
used direction occurs at least twice.

Nonzero demand needs an insertion. Every word falls into one of these cases:

1. Both rows receive an insertion. Its price is at least `mu_0+mu_1 >= D`.
2. Only row i receives insertions, at least twice. If `lambda_j != 0`,
   some `E_j` must occur, hence at least two: the price is at least T_i.
   If `lambda_j=0`, I is principal and the price is at least `mu_i=S_i`.
3. Exactly one insertion occurs at i. Necessity excludes nonprincipal I.
   If `lambda_j=0`, its price is at least `mu_i=S_i`. Otherwise at least
   two `E_j` occur. Without `E_i`, row i's final source coefficient equals
   beta, and row j's is a sum of multiples of beta. Thus
   `lambda_j in R lambda_i`. When this divisibility fails, at least two
   `E_i` also occur, giving precisely the third S_i lower bound.

Zero demand has optimum zero. The cases bound every other word below by
the claimed minimum, without a length bound, field assumption, ideal
comparability or restriction on interleavings and cancellations.

For upper bounds, direct insertions attain D. For either i, the word

    E_j(-1), P_i(lambda_j), E_j(1), P_i(lambda_i-lambda_j)

restores dirt and gives the demand at cost at most T_i. For principal I
and `lambda_j=0`, use `P_i(lambda_i)`. If `lambda_j=r lambda_i != 0`, use

    E_j(-r), P_i(lambda_i), E_j(r).

This attains the second S_i case. In the remaining principal case use the
five-gate word from the lemma. Its a,r,beta are nonzero: a=0 would imply
`lambda_j in R lambda_i`, while r=0 or beta=0 would imply `lambda_j=0`.
It attains the third S_i price exactly. Delete any zero gates in the other
words; each finite candidate is attained at no greater price. Combining
these constructions with the lower bound proves equality for all positive
prices. Literal inversion reverses a word and negates every coefficient,
with the same tariff.

For nonprincipal I, both demands are nonzero and neither generates the
other. Cases 1 and 2 therefore give exactly the three Pareto vectors in
the eight-element table, for **every** nonprincipal two-generated demand
ideal. This three-term case even holds over any commutative unital ring:
necessity and its constructions do not use finiteness. The full theorem,
including its principal case, is only claimed for finite rings.

## Verification, provenance and limits

`verify.py` uses standard-library Python and exact integer/Fraction arithmetic.
It checks finite operation-table ring axioms, all demand ideals, lemma
witnesses, candidate words and inverses. An independent column-orbit search
uses only row-gate transitions to check single-insertion reachability from
each row. Any orbit path M gives a restoring word by applying its inverse
before the insertion and M afterwards. A separate full affine-state graph
and Dijkstra searches compare
the tariff with exact shortest paths; the oracle does not call the ideal
criterion, tariff or constructors.

Fixtures include residue rings, F4, dual numbers, F2^3, the eight-element
obstruction, its product with F2, a sixteen-element ring with nonzero
epsilon-eta product, and the characteristic-three square-zero analogue.
The replay prints precise finite coverage and control counts. It reads no
external scientific input and writes no files. Both warning-strict normal
and optimized runs are registered.

The nine fixtures cover 1,761 demand pairs, including 102 nonprincipal ones,
with 3,522 row-specific orbit comparisons, 3,318 witness checks, 8,601 words,
51,606 forward/inverse basis checks and 3,072 literal scalar checks. The
four complete graphs have 24,576, 5,184, 13,824 and 960 states, respectively;
45 exact Dijkstra runs compare 2,348 target optima. Every run also checks
all Bellman inequalities and a tight descending parent path for each state.
Eleven controls check missing terms, the 202-versus-104 obstruction, wrong
source coefficients, lost dirt, nonunit generators and the zero exception.
Three disposable optimized-script mutations also fail: removing the
nonprincipal-ideal guard, dropping a dirt-return gate, and replacing
heterogeneous graph prices with unit prices.

```sh
python3.12 -B scripts/research_package.py --package research/finite-commutative-fanout --check-only
python3.12 -B scripts/research_package.py --package research/finite-commutative-fanout
python3.12 -I -W error -B research/finite-commutative-fanout/verify.py
```

The all-ring and all-price claims rest on the written proof; enumeration
corroborates bounded instances. Independent human review and proof-kernel
verification are unclaimed. Infinite principal cases, noncommutative rings,
more than two dirty rows, coefficient-dependent prices and physical caller
admission are outside the full theorem's scope. No new supplier, native
cost claim or multiplication exponent follows.

Scientific base is canonical main `20a1e31bc6009b9b3f4d084bbaadc6350e34fcba`,
priority revision 7. The donor requested this follow-up; the historical
`bit-helper-contract` card is marked changed in [TASK.json](TASK.json).
[SOURCES.json](SOURCES.json) pins #5089's README and #5045's proof as historical
provenance, not executable dependencies. Initial overlap checks covered 315
open PRs at 10:23 UTC and a complete 4,278-record Discussion snapshot at 10:06
UTC on 2026-10-23, plus all-state nonprincipal/finite-commutative/fanout searches
and a live read of #5030. No resolving successor was found in that coverage.
Sparse local notes, arbitrary diffs and unpublished work were not exhaustively
searched. Publication-time refresh is recorded in the PR.

## Open next questions

1. **Which nonsemilocal commutative rings fail the same criterion, or need
   more than four row additions?** This separates principality from
   elementary-column reachability beyond stable reduction. Start with a
   unimodular pair over a polynomial ring with two variables and test its
   elementary orbit. The relevant annihilator quotient need not have stable
   range one; the present proof supplies no such orbit classification.
2. **What is the exact tariff for three dirty rows?** Start with #5045's
   `(2,1,1)` over Z/4, retaining all dirt columns and classifying source
   supports. This addresses larger shared demands; the two-direction return
   lemma does not apply unchanged when a third row carries dirt.
3. **Can a physical caller realize these tariffs?** Specify its complete
   source and row-ADD prices, including preparation, routing, precision and
   restoration, and compare its completed bill. That caller and cost
   contract are missing here.

## Credit

Prepared by lee-phys with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. Apache-2.0. #5089 supplies the
residue-ring theorem and explicit finite-ring question. Credit Krzysztof Wójt
#5045 for the source-count classification, directional return lemma,
comparable-demand theorem and repeated-insertion words; Nick Petalas #4916
for the ring-valued contract and unit-demand theorem; Ross Richardson
#3121/#3063; Cinna Davis #1944/#1968; Anthony #774; Oscar Fennell #759;
Tekalign #3130; and the predecessors' retained lineage. CRT and finite-ring
stable reduction are classical. The addition is their application to the exact
principal-ideal reachability criterion, the nonprincipal obstruction and
the complete finite-commutative-ring tariff.
