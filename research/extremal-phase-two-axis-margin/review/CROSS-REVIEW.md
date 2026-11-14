# Complementary review of the extremal two-axis margin

**Verdict: PASS for the stated fixed two-axis source theorem.**
Reviewed proof SHA256:
`03da374ebde2644b883b2398e80112989719c2a0edb7394cc43b2abd26fa447c`.
Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Prepared independently for Jerry Chen / @CubeJerry with substantial OpenAI
assistance. This review complements the lead's separate polynomial and
continuous Bernstein certificate; it does not duplicate or rebrand that
computation as a second independently executed certificate.

## Source geometry and normalization

I compared all three canonical source notes byte-for-byte against the exact
base objects; `SOURCE-CHECK.json` records their SHA256 and Git blobs. The
retained A11 proof also matches the previously independently reviewed
`ce72eb55...` proof. Its publication pin is separately checked by the lead.

The narrow source is precisely
`G_jk=exp(-a[(rho*k-q_j)^2-beta_k^2])`, with half-up nearest integer
`q_j=floor(rho*j+1/2)`. For an odd source prime, no half-integer tie occurs,
and `s*beta_j` realizes every balanced integer residue once over `0<=j<s`.
Dyadic t is coprime to odd s, so delta=t-s has a modular inverse. The chosen
smallest centered numerator is therefore a unique actual source index.

The fine-prime interval gives `0<delta/s<=p^-2`. Starting from
`n=-(s-1)/2`, the next centered numerator is `n+delta` without wrapping,
and the nearest-target increment is one. The forbidden final source index
`s-1` would instead have centered numerator `-delta`; it cannot be the
selected extremum because `2delta+1<s`. Moreover rho<3/2 implies
`q_(s-1)=t-1`, so both selected target indices are inside `[0,t)`.
The square pair therefore uses identical row/column source index sets and
does not cross the physical period cut.

Direct substitution gives the actual off-diagonal exponents
`A=2delta+1` and `B=2s-1`. No diagonal similarity or removal of phase/chirp
is used to transfer ordinary Stein rank. The degree-four A11 compatibility
also checks: `A>4`, `4A+4<s`, and `B=-1 mod s` make the complete `[0,4]^2`
exponent box injective. This compatibility is not needed by the new
quantitative determinant proof.

## Margin and perturbation accounting

I independently checked the logical inequalities of the complete 24-order
classification. The four translated representative classes exhaust 16
orders, and their displayed determinant expressions are invariant under
the required factor-entry swaps. The other eight are exactly the orders
whose first two vertices are opposite. Their reference determinants and
the lead's independent polynomial computation provide the finite algebraic
input; the proof then applies uniformly over a continuous parameter box.

The determinant change bound for those eight orders is
`24*4*4eta=3/8`: each displacement entry changes by at most `4eta`, and
all original/reference displacement entries have magnitude at most one.
The lex/Gray inequalities use only the displayed uniform bounds and leave
the claimed `w^2/16` margin. The norm bound 4 and determinant product give
the forward minimum singular value `2^-10 w^2`.

For nonsymmetric A, the two Schur complements give
`det E(A^-1)=det E_rev(A)/(det A)^2`; reversal is an allowed simultaneous
order. This identity does not assume SPD or persymmetry. Each factor's
inverse norm is at most 4, so the tensor inverse and its displacement have
norm at most 16 and 32. These imply `2^-19 w^2` as stated.

Every norm conversion is paid: maximum entry error delta gives matrix
error at most `4delta`, forward displacement error `8delta`, inverse error
`2048delta`, and inverse displacement error `4096delta`. At
`delta<=2^-32 w^2`, both claimed half-margin conclusions follow. Per-factor
error `zeta` yields tensor error at most `2zeta+zeta^2<=3zeta`, so
`2^-34 w^2` is sufficient. The separate approximate-inverse error premise
does not silently supply inverse construction or its cost.

The source constants also check without asymptotic handwaving at the named
cutoff: for p>=4096, `4ln(16p)<=a<=9ln(16p)<=9p/8` places U in
`[1-2^-10,1]`, V in `[w,2w]`, and w below `2^-11`.
`w^2>=(16p)^-36` gives the stated absolute-entry bit budgets. At p=4096,
the two thresholds before ceiling are 610 bits and 612 bits; their gap
below p increases thereafter. Thus b=p is sufficient for these mathematical
error contracts, without claiming that p-bit intermediate computation
actually produces the coefficients or inverse.

## Periodic aliases and the production boundary

The canonical bilateral note defines exactly `N_source=Pi(G)` with column
sum over `k+ms`. This is the normalization used by section 6, rather than
an arbitrary matrix having a similar Gaussian name. For the selected pair,
`|rho*k-q_j|<=3/2` and `|beta_k|<=1/2`; beta is s-periodic. Each nonzero
alias is therefore at most `exp(-a*m^2*t^2/8)`. The factor four in the two
geometric tails and the conversion to `2^-36*w^2` are valid under t>=32,
a>=1, which this source range easily satisfies. Adding another factor
error `2^-36*w^2` stays strictly within the tensor perturbation budget.

This proves a statement about selected principal sections of the matched
periodic source and the inverse of their selected tensor. It does not
identify a section of the full inverse. Nor does it identify the retained
band N_w from #6099 with Pi(G). The source guard exclusion is exact:
`4d theta>1` and `theta<=p^-2` force `d>p^2/4`, while `u>=1` and `ud<=p`
force `d<=p`; these are incompatible for p>=4. Consequently that particular
production theorem cannot be used to discharge this new coefficient-error
premise. A different producer may work, but needs its own matrix identity,
error proof, setup precision and full cost.

## Limits and conclusion

The modular selector uses extended Euclid and a constant number of O(log s)
integer registers. Its polynomial bit work and two output indices are
explicit, while coefficient pages, inverse tables and source traversal are
not constructed. The broader source chooses many axes and scheduled capped
sections; the proof does not claim those sections contain the selected pair
or inherit its margin automatically.

I also checked the stated three-axis obstruction directly: for the listed
order and `B=[[1,1],[w,1]]`, both displacement columns 2 and 5 equal
`(1,w-1,0,0,0,0,0,0)^T`. This rules out extending the whole continuous-box
lemma unchanged. Its U=1 boundary is not an actual distinct-prime source
counterexample. The exclusions of higher dimension, arbitrary good phases,
larger inverse sections and general runtime lower bounds are necessary and
correct. All five foundational assumptions and the selected kappa remain.

No correction is requested. This is a source/proof review; no additional
finite polynomial or source-page replay was run, because the lead already
provides a genuinely separate exact certificate for that obligation.
