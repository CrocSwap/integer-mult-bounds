# One more event from Fourier integrality

This proof and its finite corroboration were produced by Nick Petalas.

## Claim and inherited contract

Under Jose Manuel's [PR2070](https://github.com/CrocSwap/integer-mult-bounds/pull/2070)
matched P112 endpoint and commuting-phase program contract, one bank requires
at least **140** nontrivial single-array phase events. Four independent banks,
even with shared role-linear processing and private workspace, require at least
**556**. These are lower bounds, with no attaining constructions claimed.

We use the mathematical conclusions in the pinned predecessor README,
Sections 1 through 3, as premises. We do not audit them or replay its code.
In particular, the new result is conditional on the same causal factorization,
character-sector construction and matched-endpoint rank statements.

The contract permits fixed constant complex linear processing of the role
coordinates, including singular COPY/CLEAR, clean private scratch, finite
restored dirty workspace, and uniform tensor Paulis. A paid event acts on
one role by a commuting directional-phase product with a nonzero binary
symmetric polar. It excludes nonlinear or data-dependent programs,
noncommuting payload adapters, arbitrary payload-coordinate mixing, and
new joint multirole child interfaces. All independent inputs and declared
outputs are retained exactly as in PR2070.

This theorem concerns one direct matched bank or four independent direct
matched banks. It does not claim a stronger normalized bound for nonuniform
coherent-cover programs, a new physical tariff, or a full supplier.

## Cited rank and character premises

Write G for the binary vector space of symmetric polars. Every character
chi of G is simultaneously available in the predecessor's common
Pauli-trivial sector at a sufficiently large tensor length. Each of k
nontrivial events has a fixed nonzero polar p_j in G, and acts by
(-1)^(chi(p_j)). Repetitions among the p_j are allowed.

Let t(chi) count the active events, those with chi(p_j)=1. The predecessor's
causal rank inequality is

    rank Delta_chi >= d_image + d_row - 2k + t(chi).

For b independent matched P112 banks its stated premises are

    d_image = d_row = 112b,
    rank Delta_chi <= 16b   for every chi.

Consequently every character must satisfy

    t(chi) <= 2k - 208b.                                      (1)

Each p_j is nonzero, so averaging t over all characters gives k/2.
Thus k >= ceil(416b/3), the predecessor's 139 and 555 bounds for b=1
and b=4. No computation in this package re-establishes the quoted
source dimensions, endpoint, or tensor-sector realization.

## A finite-group rigidity lemma

Let G be any finite binary vector space. Let p_1,...,p_k be a multiset
of nonzero elements, with k positive and odd. If

    t(chi) <= (k+1)/2   for every character chi,                 (2)

then the multiset is exactly H minus {0}, each element occurring once,
for a nonzero linear subspace H of G. In particular k+1 is a power of two.
Conversely, every such multiset satisfies (2).

Proof. Set f(0)=1, and set f(g) to the multiplicity of g for g nonzero.
Its unnormalized real Fourier transform is

    f_hat(chi) = 1 + sum_j (-1)^(chi(p_j))
               = 1 + k - 2t(chi) >= 0.

Fourier inversion at zero gives sum_chi f_hat(chi)=|G|. Therefore
w_chi=f_hat(chi)/|G| is a probability distribution, and inversion gives

    f(g) = sum_chi w_chi (-1)^(chi(g)).                         (3)

Equation (3) implies |f(g)|<=1. The multiplicities are nonnegative
integers, so f takes only values 0 and 1. Moreover, f(g)=1 exactly when
every character with w_chi>0 vanishes on g. The set H on which f is 1
is therefore the intersection of the kernels of those characters, a
linear subspace. This proves both the support statement and the absence
of repeated polars. Since sum_g f(g)=k+1, we get |H|=k+1.

Conversely, if f is the indicator of H, summing a character over H gives
|H| if the character vanishes on H, and zero otherwise. Hence f_hat>=0,
which is (2). This completes the proof for every finite dimension.

Equivalently, if positive odd k has k+1 not a power of two, some character
activates at least (k+3)/2 events. This is an arithmetic obstruction;
it does not depend on the ambient dimension or on a bound on repetitions.
Finite-group Fourier inversion and positivity are classical ingredients.
No global priority for the abstract lemma is claimed.

## The new matched-endpoint bounds

For b=1, the cited average bound already gives k>=139. If k=139,
(1) requires t(chi)<=70 for every chi. This equals (k+1)/2, so the
lemma would require 140 to be a power of two. It is not. Thus k>=140.

For b=4, the cited average bound gives k>=555. If k=555, (1) requires
t(chi)<=278 for every chi. Again this is (k+1)/2, but 556 is not a
power of two. Thus k>=556.

The argument applies separately at every sufficiently large tensor length
in the cited character-sector construction, even if the program and its
constant coefficients depend on that length. Its polar multiset at that
length is still finite and subject to the same lemma.

## Limits and relevance

This strengthens the historical matched terminal obstruction by one event.
PR2070 already excluded its stated comparison invoice; we do not recompute
that invoice, claim a new exclusion of the selected PR6030 caller, or change
kappa. The result explains one additional reason the averaged event-count
boundary cannot be attained in this alphabet.

A zero-polar event violates the lemma's premise. Uncharged adapters that
move between character sectors violate the common-character premise.
Different terminal endpoints need their own image, row and defect bounds.
Event counts do not by themselves determine a native tariff or a complete
signed target/paid moment. The five selected framework assumptions remain.
Independent human and formal proof-kernel review are unclaimed.

The verifier enumerates only its explicitly reported small multisets. Its
finite checks corroborate the new Fourier argument and its implementation;
they do not enumerate candidate 139-event or 555-event circuits, and they
do not replace this all-dimension proof.
