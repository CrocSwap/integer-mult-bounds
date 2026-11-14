# Adversarial review of the semialgebraic tangent extension

## Result

The reduction is valid under its stated hypotheses and under the separate
all-block funding theorem. Semialgebraicity supplies the missing common
regular stratum; the open image condition supplies a stratum whose retained
projection is a submersion. Exact recovery itself need not be semialgebraic,
continuous, or differentiable.

The cited primary result is Drusvyatskiy, Ioffe, and Lewis, Theorem 3.4. It
states that a semialgebraic map admits compatible finite analytic
stratifications of source and target on which the restriction has constant
rank and maps source strata onto target strata. In applying it, include the
semialgebraic image `π_I(S)` in the target compatibility family. Because that
image contains a nonempty open set, at least one included target stratum is
full dimensional. At least one source stratum maps to it, and constant rank
then forces rank `D|I|` on that entire source stratum.

The follow-on common-point step is also sound: restrict each of the finitely
many linear history maps to this semialgebraic smooth stratum. Its differential
rank level sets are semialgebraic and finite in number. The union of the
relative interiors of the rank level sets is dense, since the omitted
semialgebraic boundaries have smaller dimension. Intersect these finitely
dense open loci, then select one point. This preserves the full retained
projection rank and makes all history maps constant-rank near the same point.

At that point, the constant-rank fiber-curve argument proves tangent-kernel
inclusion from exact deterministic recovery without differentiating a
decoder. Differentiating every promised linear zero row gives its tangent
annihilation. Main inputs stay a full independent factor, so the tangent
contains every main direction. The retained helper projection is surjective;
therefore the annihilator has injective restriction to the fully debited
helper columns. These are precisely the hypotheses needed to transfer the
optimistic funding bound from the tangent back to the original promise.

## Boundary checks

- **Reducible and singular sets:** allowed. The proof selects one source
  stratum mapping to a full-dimensional retained target stratum; it does not
  require irreducibility, a globally smooth promise, or a regular point in
  every component.
- **Varying observation ranks:** allowed for a finite family. Semialgebraic
  rank loci have a common open piece of the chosen stratum. The argument
  would not justify an infinite family of independent cache obligations.
- **Critical points:** a bad singular point need not itself work. For example,
  on `(t,t^3)` the observation `t^3` recovers target `t`; at `t=0` its
  derivative cannot factor the target derivative. The semialgebraic stratum
  argument chooses a regular point with `t≠0` instead.
- **Finite grids:** with `|I|>0`, a finite retained projection has empty
  Euclidean interior, so the hypothesis fails. Surjectivity onto a chosen
  finite grid is not the same as containing an open subset. If `I=∅`, a
  nonempty finite promise does satisfy the vacuous `R^0` open-image
  condition, but then every helper field belongs to the debited set `J`.
- **Nonsemialgebraic digit encodings:** a graph can project onto an open
  square and permit exact nonlinear decoding while admitting no useful
  tangent subspace. Such a graph is outside the semialgebraic hypothesis;
  open projection alone is insufficient.
- **Main dependence:** excluded. If the helper promise couples helpers to
  arbitrary mains, the tangent is not `R^{DM}⊕T_pS`, and the full-main
  derivative argument fails.
- **Complex data:** realification yields a real block tangent, not a
  complex-scalar tangent. The conclusion uses the real block funding theorem
  for the realified fixed maps. The present source has common rational-real scalar coefficients, which
  preserve the exact tensor row-space structure used in the block proof.
  Arbitrary complex coefficient blocks need a separate application argument.
- **Funding dependency:** the tangent construction alone is not a numerical
  exclusion. The joint fine envelope follows only when the independently
  checked block-linear funding bound applies to the resulting real tangent.
  It does not claim an implementable cache, a changed source, or an attained
  exponent.

## Primary theorem checked

The PDF's Theorem 3.4 is the stratification theorem used here (journal pages
517–518). It gives compatible `C^ω` stratifications and constant rank for
the chosen semialgebraic map. The stronger semialgebraic Sard/minimization
results later in the article are not needed. The only further facts used are
standard semialgebraic dimension properties and the constant-rank fiber
theorem.
