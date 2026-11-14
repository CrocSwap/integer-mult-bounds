# Sharp radial optimum for exact-sum Gaussian square-to-swap rounding

Exact sum, Euclidean error at most one and fourth power alone do not settle
the additional native square identity. For Gaussian pairs satisfying
`F^2(u,v)=(v,u)`, prove the sharp radial slack
`sqrt(19)-sqrt(13)` and construct an all-input bijection attaining it.
The construction also preserves global Gaussian-unit covariance.

The lower bound applies to every map in the stated class: on the sum-one
fiber the square identity forces a quarter-equivariant unit matching, and
the 36-vertex half-grid square forces a crossing edge of cost at least beta.
An explicit pairing of adjacent square rings attains the bound. A finite
four-cycle alternates squared norms 13 and 19. The square identity makes
forward outward, inverse outward and absolute radial slack coincide in
this class; no unrestricted forward-only lower bound is asserted.

Pin and credit #6509/#6619, nearby larger-block work and the existing n=4
exact-square construction #6776. Apply #6778 as the known obstruction to
same-map row/column commutation. The actual inverse is `swap o F`;
inverse-by-conjugation is universally incompatible with exact sum and the
square identity. This is an alternative pair-level rounding contract,
with no selected-caller, tensor supplier, physical tariff or kappa claim.

Validation: standard-library exact checker, normal and optimized Python;
seven complete ring pairs, the 36-vertex/24-edge boundary, 625 Gaussian
inputs, finite sharp attainment, and four premise/interface controls.
The universal theorem rests on the written all-input proof. The checker
is deliberately bounded and is not a production graph. Root supplied
the sharp candidate; reference-code exposure and separate review evidence
are disclosed in the package.
