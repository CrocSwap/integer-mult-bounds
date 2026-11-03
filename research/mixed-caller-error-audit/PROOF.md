# What the exact replay establishes

## Source and abstract domain

The word and the author contract are frozen by SOURCE-PINS.json. The word has
34 fields and 570 events, with 18 independent commuting unitary stage symbols.
We audit the quantitative argument of PR6473; its theorem and contract remain
Ali Romman's predecessor work. The older mixed caller is not selected 6030.

Let H be a complex Hilbert space, Q unitary with Q^4=I, and D_j commuting
unitaries commuting with Q. Decompose H into the four orthogonal Q eigenspaces.
Every D_j preserves them. For a matrix cell on one eigenspace, combine equal
stage monomials with Gaussian rational coefficients and bound its operator
norm by the sum of |Re c|+|Im c|. Every stage monomial has norm 1. Taking the
maximum over characters bounds the full cell operator. Summing those cell
bounds then bounds a row from the maximum field2-norm to H. Commutativity,
unitarity and the order-four property are explicit hypotheses.

The order matters. For H=C^2 and Q=diag(1,-1), a row consisting of its two
complementary spectral projections has character row sums 1. Yet the unit
inputs (1,0) and (0,1) give output(1,1), of norm sqrt2. Taking a maximum of
character row sums is therefore insufficient for this field norm. Our cell
maximum followed by row sum gives the safe bound 2. This toy diagnoses the
order of operations; it is not an actual caller counterexample.

## Literal error propagation

Each completed ADD/SCALE has one scalar-class defect; LOCAL has two native
output defects; QUERY has one; each updated idle output has one. Normalizer
LAMBDA has the grouped completed-defect premise at most (9/2)e_s in the
abstract all-Q propagation. For a translation-pair-compatible normalizer,
where Q² is the pair swap, the literal four half-field operations justify
that premise. Their error columns have squared
Euclidean norms 1, 2, 1, 1 for either sign, giving (3+sqrt2)e_s < (9/2)e_s. These
are independent error sites, not a free exact normalizer. Arbitrary Q^4=I
alone does not guarantee this equal-half representation: H=C,Q=i already
cannot have a nonzero equal-half split. The abstract theorem therefore
assumes the grouped defect bound, rather than claiming an all-Q four-operation
realization. Exact SWAP/Q_POWER
have no defect in this contract.

For zero-based event t, final defect contribution is the suffix **after** that
event applied to the injected output. Thus accumulate from S_(t+1) before
extending the suffix across event t. The two engines implement this identity
with different representations/constructions and compare every output row
and every boundary envelope. Hashes identify retained cell transcripts; a hash
alone is not a proof. Correctness rests on the explicit exact recurrences and
the elementary norm inequality above, not finite samples of D_j.

The common-error maximum is 943/2<512. For the lower bound, specialize only here
to H=C and Q=D_j=I. Propagate a chosen output functional backwards, selecting
the sign of each permitted non-normalizer defect from its exact rational
suffix coefficient. Execute the literal noisy word forwards from zero and
check the same output, yielding 307. Every injected defect has magnitude at
most1; all normalizer defects are0. Scaling by e gives307e>256e. Together these
bounds show g9 suffices and g8 fails for the stated abstract contract. They do
not assert943/2 is the exact real optimum or that actual rounding realizes
those signs. If a pair-compatible model is required, the scalar lower witness
embeds in the constant Q=1 sector of a four-cycle on C^4, with all D_j=I and
zero normalizer errors. This is a linear embedding of the existing witness,
not a new numerical experiment.

## Intermediate and physical obligations

The prefix envelope18 bounds ideal boundary signals. The source argument uses
the exact diagonal unitary endpoint U and invertibility: S_t=U P_t^-1, so
P_t U^-1 maps the final error to the intermediate error with norm at most18.
Applying the final budget to only the errors before t gives the source bound
18M+8487e. Partial normalizers give the conservative36M+16982e bound. Native
interiors remain outside these premises. We do not infer their ranges, widths,
coordinate errors, memory access, precision tariff or cleanup.

Formal polynomial equality and exact error arithmetic bind this word and
contract. No physical supplier, selected-frontier admission or multiplication
theorem is claimed; all five inherited framework assumptions retain status.
