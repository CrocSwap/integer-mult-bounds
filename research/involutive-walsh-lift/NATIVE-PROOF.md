# Exact native frame and helper contracts

This result changes the local representation of the selected word. It
does not remove its centre children or supply a new centre decoder. The
source commit and archive members are pinned by `sources.py` and the
package source manifest. The global frame proof and the invoice are
separate parts of this package.

The local statement holds on arbitrary arrays and arbitrary borrowed
helper values. Every scalar phase is retained. The twofold construction
uses Gaussian dyadic coefficients and works for every positive tensor
parameter. It does not need a pair of physical replicas.

## A frame change that preserves every native child rank

Write `S(x)=i^wt(x)`. Let F_r be the original coordinate native
transform, and define `H_[r]=S_[r] F_r S_[r]`. On one coordinate,

    H_1=(1+i)/2 [[1,1],[1,-1]],   H_1^2=i I.

Thus `H_[r]^2=i^r I`. For a binary subspace V, choose the invertible
chart B that extends the recorded basis and put

    H_V=P_B (H_[r] tensor I) P_B^-1,   r=dim(V).

This is an invertible operator even when V is degenerate. It squares
to `i^r I`. It is not a product of the formulas `(1+i)(X_v+Z_v)/2`
along the vectors of an arbitrary basis. For example, the latter
formula at the even vector 30 kills `|0>-|30>`. The chart-defined
operator for that line is invertible. The independent review checks
both facts directly.

Let O_V be the original canonical frame. Its preimage of the diagonal
Pauli space is

    {(v,v+w): v in V, w in V-perp}.

The preimage under H_V is `{(v,w): v in V, w in V-perp}`. The common
right factor S gives this second preimage to O_V S. Consequently

    A_V=H_V S^-1 O_V^-1

is monomial, and `H_V=A_V O_V S`. A monomial here is an affine address
permutation with a quadratic phase over Z/4. Its complete coefficients
are in the emitted records. The review checks all 1,004 identities as
full operators, their squares, and both Pauli preimages. It does not
assume that the source bases are orthogonal.

For an edge from V to W,

    H_W H_V^-1=A_W (O_W O_V^-1) A_V^-1.

Therefore the new edge has the same native rank as the old edge. Its
two new monomial factors fuse with the old child factors. Every one of
the 2,896 emitted recipes receives a complete independent operator
check. Pauli action determines each Clifford up to a scalar; an exact
Gaussian dyadic state image fixes that scalar. No producer compiler is
used by the review.

## The scalar word and its physical endpoints

Every scalar gate in the original word acts on operands in one common
frame. Replacing that frame by H_V therefore leaves its logical scalar
map unchanged. A private CLEAR gives zero for any initial private
value. Induction through the complete stream proves the result on all
inputs. The review also checks both scalar maps by a separate
transpose replay on all 712 input columns. They are

    forward: (x,y,h,c) -> (x,y+x,h,0),
    backward: (x,y,h,c) -> (x-y,y,h,0).

Here h includes all 480 ordinary helper values, and c contains the
eight private centre inputs. Their native transformations are accounted
for by the frame and helper adapters.

At an odd data label q, the intrinsic source is

    H_q=(1+i)(X_q+Z_q)/2,   H_q^2=i I.

The full operator is H_full, and the target is `H_full H_q^-1`.
The 224 emitted endpoint adapters are checked against these exact
operators and against the canonical chart frames. Both orientations
use entrance `(H_q,I)` and exit `(H_full,H_full H_q^-1)`. One must not
retain an old backward-relative frame convention in a new global
schedule without a new derivation.

## A complete helper job

Let the new residual from helper entrance to exit have recipe

    H_exit H_entry^-1=L F_r R.

Its complete H_r job uses the literal external maps

    pre=R^-1 S_[r],   post=S_[r] L^-1.

The resulting product is `S_[r] F_r S_[r]=H_[r]`. The old inverse
factors alone would give F_r instead. All 36 normalizer pairs are
emitted separately and checked as complete operators. The equality
holds for every helper input and in either orientation.

If an owner still requires the original F_r job, put S_[r]^-1 before
the complete H_r job and S_[r]^-1 after it. These maps have native rank
zero. Their finite phase and address costs remain part of the supplier
invoice; a productive helper is not treated as an identity wire.

## Two coordinate copies give exact involutions

For every old frame V of rank r and every tensor parameter lambda, set

    Gamma_V=i^(-r lambda) (H_V tensor H_V)^tensor(lambda).

Then `Gamma_V^2=I`. The correcting factor is a Gaussian unit. At one
tensor copy the coefficients have absolute value `2^-r` on their
support, with real signs. The chart address maps are permutations.
Thus the full Gamma_V is real and orthogonal, and it is symmetric
because it is an involution.

For an odd source label q,

    Q_q=(X_q+Z_q) tensor (X_q+Z_q) / 2

at lambda one. Its tensor powers also square to I. This is a rank-two
source plane; it is not a rank-one formula for the even vector `(q,q)`.
The doubled full and hole ranks are 18 and 16, and

    Gamma_hole=Gamma_full Q_q^-1.

The phases agree: the full and source normalizations both contribute
`i^-lambda`, while the hole normalization is one. The endpoint adapters
are the literal tensor products of the reviewed old adapters.

Suppose an old new-frame edge has recipe `L F_r R`. Let P send the
first 2r coordinate axes to the first r axes in each old copy. Then

    F_r tensor F_r=P F_(2r) P^-1.

The doubled edge from V to W is therefore

    i^((dim(V)-dim(W))*lambda)
      (L tensor L) P F_(2r) P^-1 (R tensor R).

This is one child of rank 2r. The rank phase and both gathered factors
are emitted explicitly. The review compares every affine address and
quadratic phase on zero, all single bits, and all bit pairs. Those
values determine each factor in full. It also checks every coordinate
gather. No dense 18-bit operator matrix is needed.

The source event streams keep their source frame IDs. Their old rank
tokens are reference data; the emitted child record supplies the
doubled native rank. The review records both the complete source-word
profile and the persistent-climb profile. In particular, persistent
climbs have rank 11,044, while the original word with its private
centre children has rank 11,172.

## Doubled helper and output normalization

For a doubled residual `L2 F_(2r) R2`, use

    pre=R2^-1 S_[2r],
    post=i^(-r lambda) S_[2r] L2^-1.

Here S_[2r] acts on the contiguous first 2r coordinates after the
emitted gather. It does not act on two scattered sets of r coordinates.
The complete job is the real normalized Walsh job on the first 2r
coordinates in each tensor block. The review checks all 36 emitted
pre and post maps, including the phase in the post map.
To recover the original F_(2r) owner job, add S_[2r]^-1 before it and
`i^(r lambda) S_[2r]^-1` after it.

That conversion is an optional interface identity. The global package
uses Gamma owner histories throughout. It does not convert each
complete owner job back to F. The literal recursive child inside each
emitted recipe remains F_(2r).

At global dimension 146, the same formula is

    Gamma_73=i^(-73lambda) S_(146lambda) F_(146lambda) S_(146lambda).

Pre S_(146lambda)^-1 and post `i^(73lambda) S_(146lambda)^-1` give
the required F_(146lambda) on every input. This endpoint formula does not replace the separate
global proof of all intervening data charts and owner jobs.

Every identity above is an exact base operator identity. Tensoring it
gives the identity for every positive lambda. General arrays follow by
linearity; inputs need not be separable tensors. Scalar coefficients in
the word act once per array entry and are not squared by this lift.

## Verification scope

Run `review_native.py` and then `review_doubled.py` after the package
generator, with the same `--repo` and `--out` paths. Both checks use
explicit requirements and have deterministic receipts. The first
prints `PASS_INDEPENDENT_WALSH_RETARGET_FRAMES_AND_ACTUAL_WORD_LEDGER`.
The second prints `PASS_EXACT_DOUBLED_WALSH_NATIVE_LOWERING`.

This proves the local representation change, full phases, arbitrary
helper contracts, and explicit doubled lowering. It does not supply a
cheaper complete centre controller. The remaining source access, mode
restoration, and changed-word finite costs are not removed by the
involution identity. Source attribution is retained in the package
README and manifest. Research and independent agent review used
OpenAI Codex assistance. No independent human review is claimed.
