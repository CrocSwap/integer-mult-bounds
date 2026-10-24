# Exact admission for a selected-baseline source code

The selected-block unit condition is necessary for the stated source
interface. It is not only a sufficient construction. This result uses
the same ordered coefficient ring as SELECTED-BLOCK-NORMALIZATION.md.
It does not prove a lower bound for a different source interface.

Split the source and target coordinates into S and U. Let A be a subset
of S. Let E be a supplied unit that writes a systematic query into A
and fixes every other row. In particular, E_U=selector_U. Its selected
rows E_S specify both the new query in A and the unchanged baselines
in S minus A.

Suppose a source unit F satisfies

    F_S=E_S,       (JF)_U=selector_U.

Put C=F E^-1. Then C_S=selector_S. Thus C has the block form

    C = [[C_UU,C_US],[0,I_S]].

Since C is a unit, C_UU is a unit. Also E^-1 fixes the U rows, so

    J_U C=selector_U E^-1=selector_U.

The U columns of this equation give J_UU C_UU=I_U. Therefore
J_UU=C_UU^-1 is a unit. The S columns then fix

    C_UU=J_UU^-1,       C_US=-J_UU^-1 J_US.

These equations determine C and F uniquely. No commutation of
operator coefficients is used.

Conversely, if J_UU is a unit, these blocks define a unit C, and
F=C E has the required selected rows and target response. For
J=I-KR, the standard ordered block identities give the equivalent
condition that

    D=I-R_U K_U

is a unit. The unique source factor is

    C=H=I+bar(K_U)D^-1R,
    H^-1=I-bar(K_U)R,
    F=H E.

Thus the selected-block test is exact for even one supplied systematic
query E. It is not necessary to demand that F work for every future
query before this test applies. The proof does not apply if the source
may also change the selected baseline rows, if the query is stored in
a different representation, or if the target interface is changed.

For the actual R and K=R^T/4, suppose S is a union of k disjoint
eight-column minors, each with Gram4I. Then R_S K_S=kI and

    D=(k-13)I.

Over the dyadic or Gaussian-dyadic scalar ring, and for 1<=k<=14,
this is a unit exactly for k in {5,9,11,12,14}. The first such union
therefore has forty selected fields. This also holds in the group
algebra of cover permutations: augmentation makes a scalar inverse
necessary, and a dyadic scalar inverse is sufficient. It does not
prove that forty is minimal among arbitrary selected subsets.

The five actual minors and their dyadic inverse are checked in
SELECTED-BLOCK-NORMALIZATION.json. This note adds an ordered proof;
it adds no native frame, scalar invoice, owner, or controller claim.
The source E and H still need the native implementation at the stated
input boundary. The current five-minor component supplies one such
implementation, subject to its literal-word and global obligations.

The parent supplied the selected-block construction. The controller
lane supplied the common five-minor instance. This lane derived the
necessity and uniqueness statement. Research used substantial OpenAI
Codex assistance under the user's direction. New material uses
Apache-2.0.
