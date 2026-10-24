# Independent review of the outer-route results

The reviewer used the source archive at main commit
`12a4934d15006e8c10f9b2264f13f8f341be802b`. All ten source SHA-256 values in
`SOURCE-MANIFEST.json`, which pins proposal head
`a900f98be8ff2c09d3292b5112d4731dbd0c8438`, match that archive. The Gaussian
manuscript source pin is `adc7f1241b42e322a6451854ab7e4b4c146bf78a`.
This review makes no live-frontier or literature-novelty claim.

## Polylogarithmic spectator fields

The written routing argument is valid under the same full binary-box,
equal-width field-swap, fixed-tape, and complete scalar-record interfaces
as the retained arbitrary routing theorem. The source is
`references/semantic-bulk/rad20/reports/compact-arbitrary-source-routing.md`,
SHA-256 `3df36853a181fd5d331811b5c4859a1980116c69f447eb78c40a551ff28cde79`.
The reviewer read that source and the complete 177-line proposed verifier.

Let `h=ceil(log2 p)` and `s=h^2`. If `n<=3s`, the two-involution matching
construction costs `O(V log^2 p)`. If `n>3s`, the first, next, and last
fields of width `s` are disjoint. Each routing edge leaves at least one
of those fields untouched. Partition the edges by that choice. Move the
chosen field to the suffix with one permitted equal-width swap, rename
each endpoint under the swap, run its routing class, and restore the
field. This restores all address names and payload bits.

The suffix has reservoir size `R0*2^s`. It exceeds each fixed polynomial
descriptor bound for sufficiently large `p`. The threshold is finite
and can depend on the fixed descriptor degree. A prefix below `64G`
needs only the elementary matching construction. The finite range
below the reservoir threshold has a fixed polynomial setup bound.
Thus the proposed bound retains `O(V p^tau polylog p + poly p)` for
`n=O(p)`. No new scalar precision or address coordinates are required.

The saved verifier receipts cover complete tiny boxes, larger position
probes, actual packed gate counts, and layout negative controls. The
reviewer checked those receipts and source code but did not perform a
third full routing replay. The author reports two equal fresh receipts.
Finite cases support the implementation checks; the written argument
establishes the all-size statement under the inherited interfaces.

This removes the old short-width condition `epsilon>a`. It gives no
certified improvement to the currently admitted multiplication kappa.
It removes neither the Gaussian precision condition nor the numeric
guards on `b` and `r`.

## Gaussian inverse normalization

The reviewer independently reconstructed the unit-column argument from
`upstream/build/sections/07-resampling.tex`, SHA-256
`8a6b91670f9163afb54892489fa2210c77fe1b058f0325ec7d18b44b94be6e2c`.
The source defines the periodic sampler with `u=alpha^2`, proves
`(D N^-1 C) T=I`, and uses tensor scale `gamma=2d alpha^2`. The retained
phase-cell report defines `N=C T D` and retains the same sampler and
complete contraction interface. Its rounded matrix `H` is a numerical
implementation of `N`; it is not a replacement sampling map.

For odd `s>=3` coprime to `t`, choose `j` with
`tj mod s=(s-1)/2`. Put `beta=(s-1)/(2s)>=1/3`. Every periodic image
at an integer output has nearest distance at least `beta`. The remaining
images have distance at least `t(ell-1/2)`. Since `t>=3`, `beta^2<=1/4`,
and `v=ell-1>=0`, the difference of squared distances is at least
`9v^2+9v+2>=2+v`. With `u>=1`, `pi>3`, and `exp(1)>2`, the relative
tail is less than `1/28`. Hence

    ||T e_j||_infinity < 2 exp(-pi u beta^2).

Every complete left inverse `L` then has
`||L||_infinity > 2^(u/3-1)`. Apply the same argument to a tensor unit
column to obtain `||L_tensor||_infinity > 2^(d(u/3-1))` for any complete
left inverse, including one that does not factor by axis. This step
does not assume that the inverse norm is a product of factor norms.
It uses the product norm of one sampled column.

For `u>=12`, dyadic contraction normalization requires at least `du/4`
bits. For a complete approximate inverse with residual norm at most
`1/2`, the loss is one bit; `u>=24` gives the same stated lower bound.
The residual must be a norm bound for the complete inverse. A bound
only for an internal rounded factor would not be sufficient.

The reviewer ran a copied, byte-identical exact verifier in a separate
output directory. It passed 227 coprime size cases and 118992 periodic
distance checks with exit code 0. Its receipt is byte-identical to the
author receipt. The command and all ten source hashes are saved in
`../framework/gaussian-independent-replay.json`. The universal polynomial
and norm argument establish the infinite bound; the finite cases alone
do not establish it.

The lower bound forces `epsilon+r<=1` for `O(p)` normalization and
`epsilon+r<1` for the retained `gamma=o(p)` proof. It does not exclude
the equality case under a new constant and recovery analysis. It does
not exclude a different sampler, a different representation, or a
proved restriction on input and error directions. It is not a lower
bound for unrestricted integer multiplication.

Oddness is not required for the obstruction. For every coprime pair
`2<=s<t`, choose `tj mod s=floor(s/2)` and put
`beta=floor(s/2)/s`. Then `1/3<=beta<=1/2`. For even `s`, take the
absolute nearest-integer phase because the upward tie rule gives a signed
phase of `-1/2`. Every tail step above already permits `beta^2<=1/4`.
The same complete-inverse bound therefore holds for all these axis sizes.
Independent rational controls for this extension are saved in
`../framework/gaussian-all-size-phase-extension.json`. They passed 354
coprime pairs. The all-size proof is the modular-inverse choice and the
same nonnegative tail polynomial, not that finite count.

The source also has `u=alpha^2>=4`. Thus
`u/3-1>=u/12`, and exact contraction normalization needs more than
`du/12` bits throughout the admitted source range. The stronger `du/4`
constant above applies for `u>=12`. No positive-power growth assumption
on `u` is required for the `Omega(du)` statement itself.

## Remaining ceiling

After the routing refinement, the retained full-stream local supplier
has `q<=1`, the compact margin gives `kappa<epsilon*q<=epsilon`, and the
Gaussian phase-cell boundary margin gives `kappa<r`. Combined with
`r<=1-epsilon`, these imply `kappa<1/2`. The current numeric guards
give smaller ceilings. Thus parameter changes and tighter complete
inverse norm estimates alone cannot give `kappa=1` in this route.

Prepared with OpenAI Codex assistance. Apache-2.0.
