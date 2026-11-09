# A source-specific three-query minimum

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.

## 1. Claim, sources and exact boundary

The original #6937 caller is pinned at
`a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`, file
`research/p104-two-chain-findings/data/caller_efree.json`, Git blob
`5a71ca9f80ced1aeb8a68e97516cab52eb72a52a`. Consider exactly its zero-based
events 457 through 575, inclusive. They contain 119 operations, begin with
`QSELF(0,-1)`, end with `QSELF(19,-1)`, and contain one QUERY between them.
The complete state has 76 independent formal input registers. Only the
38 A registers are touched; the 38 B registers are unchanged.

The public package `p104-query-only-interval`, commit
`617903497387a98f7ca929ad0b6928dd32abffec`, replaces that same interval by
223 events using exactly three QUERYs and no QSELF. It preserves the
entire boundary map, with all independent inputs and formal D variables.
We retain and authenticate its proof rather than claim its construction
again. The original and replacement words are included byte-for-byte.

**Theorem.** In the fixed linear/affine rewrite model in Section 2, every
replacement of this exact interval's full independent-input map uses at
least three charged QUERY operations. The cited three-query construction
attains this bound in the model. Extra finite linear helpers, copies,
erasures and affine constants do not reduce the minimum.

This is a local formal-operator result. It does not prove optimality of
the complete caller, a paid native-rank lower bound, a bit-complexity lower
bound, or a limit on multiplication kappa.

## 2. Rewrite model and legal evaluations

The required identity is over

    R = Q(i)[q,D1,...,D18]/(q^4-1),

with no additional q/D relations or D idempotence. In particular q is a
formal operator parameter, not an input register. Both evaluations
`q=+1,D9=1` and `q=-1,D9=1` are lawful; other D variables may also be set
to 1, since none occurs in this interval. We take matrix ranks only over
the field Q(i) after evaluation, not over the quotient ring R.

A candidate has a fixed finite instruction stream and finite register
state. It may add any finite number of helper registers. Free steps are
linear or affine maps whose coefficients, constants, initialization and
final output extraction evaluate identically at the two chosen points.
Arbitrary q-even coefficients are allowed when defined at both points;
any allowed rational denominator must be regular there. Free maps may be
singular or rectangular. Copying, erasure and arbitrary q-independent
initial helper values are allowed without cost for this lower bound.

A charged query must have full-state matrix difference of rank at most
one between the two evaluations, after homogenizing affine state. The
retained instruction `dest += q^k source`, for odd k and distinct roles,
has difference `2 E_dest,source`, hence meets this condition. Surrounding
it by any permitted free maps still has difference rank at most one.
Even powers have zero response and cannot improve the bound by themselves.
The original QSELF steps also have rank-one difference, although QSELF
is not an allowed uncharged operation in the replacement alphabet.

All query-dependent side information must be accounted for. In particular
a prequeried helper bank cannot enter this interval for free, and odd-q
linear coefficients are not free. Every independent boundary input is
preserved as specified by the source map; restricting to a reachable
subspace or discarding selected outputs changes this task. Data-dependent
branches, nonlinear coefficient synthesis and a wider payload query whose
full-state difference has rank greater than one are outside the model.

These restrictions are essential. For example, freely applying q to three
independent registers has response 2 I_3 and would supply the rank-three
witness with no charged queries. Restricting the input to two dimensions
also makes any response rank at most two. Neither is an admissible rewrite
of the problem stated here.

## 3. Classical product-difference bound, including helpers

Append one constant coordinate to homogenize affine maps. At the two
evaluations let the chronological step matrices be A_j^+ and A_j^-.
Initialization E and final extraction P are the same at both evaluations.
Variable register dimensions can be kept in the following compatible
rectangular products, or padded into the finite union of all registers.

The difference of whole maps is

    M^+ - M^- = P sum_j [ A_m^+ ... A_(j+1)^+
                         (A_j^+ - A_j^-)
                         A_(j-1)^- ... A_1^- ] E.             (1)

This is the usual telescoping identity, with no inversion. A free step
contributes zero. A charged query contributes a term of rank at most one,
because multiplication on either side cannot increase rank. Rank
subadditivity therefore gives

    rank(M^+ - M^-) <= number of charged queries.              (2)

For affine maps, restrict the columns to independent original inputs to
obtain the same bound on the linear response. Extra initial constants do
not invalidate (2). Noninvertible helpers, copies, rectangular maps and
erasures cause no problem. Correlated q-independent initial helpers are
already part of E. The rank and telescoping facts are classical; no
novelty is claimed for this general argument.

## 4. Exact source witness

Evaluate the original 119-event word at the two points in Section 2.
LAMBDA_s is the actual even polynomial

    ((1+s i) + (1-s i)q^2)/2,

so it evaluates to 1 at either sign. The single IDLE_ONE in the interval
is D9 and evaluates to 1. All ADD/SCALE coefficients remain their exact
rationals; SWAP is unchanged. Thus direct rational arithmetic suffices.

Let Delta=M^+-M^-. Its rows and columns numbered 0,1,19 give

| | input 0 | input 1 | input 19 |
| --- | ---: | ---: | ---: |
| output 0 | -2 | -4 | 0 |
| output 1 | 0 | -2 | 0 |
| output 19 | 0 | 0 | 2 |

The determinant is 8. Hence rank(Delta)>=3 over Q(i). The supplied forward
evaluator also computes the complete 76 by 76 response and finds rank
exactly 3, with 55 nonzero entries. Rank at least 3 is all the lower bound
needs. Applying (2) proves that two or fewer queries are impossible in
the stated model.

There are two independently coded source checks. `verify.py` propagates
all original input columns forward and performs exact rational elimination.
`review/check_covectors.py` propagates three output covectors backwards
through literal transposed instructions, retaining all 76 input coordinates.
The latter was written by a separate shared-context AI worker without
importing the lead evaluator or the predecessor arithmetic. It recovers
the same minor and determinant. Its proof review is retained separately;
this is not human or proof-kernel acceptance.

Both checks authenticate source bytes and fixed interval endpoints. Each
also checks the corresponding response of the public replacement. Deleting
any one of the three charged source sites or any one of the three replacement
queries destroys this rank-three witness; all six controls are included.
These are exact certificates for a finite, explicitly given matrix. The
universal claim over all candidate straight-line rewrites comes from
Sections 2 and 3, not from enumeration of candidate circuits.

## 5. Attainment, budget and limits

The pinned predecessor proves the full R-valued identity for its 223-event
replacement, including the untouched independent inputs, the formal D9
service, the correct unit-valued LAMBDA factors and their conjugations.
It uses only three odd-power QUERYs and permitted even/constant free maps.
Its entire formal proof is retained as `retained/ATTAINMENT-PROOF.md`.
The two sign checks in this package alone would not establish that full
identity at q=+i,-i or all D9; they are supplementary source checks only.

The exact three-query minimum prevents a one-query reduction of this
particular interval while preserving the model and boundary. It does not
reprice the predecessor. That package's additional free-operation costs,
helper access, width, copying, restoration, finite compiler and physical
supplier obligations remain in force. In particular no uncharged wider
payload query or queried initialization is being hidden in this result.
We do not multiply the formal rank by the number of physical ports and
call it a new native or whole-caller lower bound.

No runtime algorithm, selected certificate or accepted kappa changes here.
The selected kappa remains 781451/250000000, conditional on all five
retained framework assumptions. The proposed QUERY-only caller still has
its separate precision, complete native admission and compiler obligations.
Global reordering, changing the interval boundaries, exploiting a proved
reachable-input subspace, or exploiting extra relations of a particular
native operator remain possible research directions and are not excluded.

## 6. Relation to prior work

The #6937 two-chain source and the public three-query construction are
the indispensable predecessors. The latter supplied the upper bound;
this package supplies a matching source-specific lower bound.

The bounded overlap review read the canonical actual-query information
and affine-tag minimum packages, and #6825's characteristic-two rank
factorization result with #6800 antecedent. Their source targets, operation
models and coefficient fields differ from this order-four characteristic-zero
interval. We credit their rank/query perspective and make no claim to
inventing the rank method or exhaustively surveying all circuit complexity.
`OVERLAP.md` records the distinctions and exact scope.
