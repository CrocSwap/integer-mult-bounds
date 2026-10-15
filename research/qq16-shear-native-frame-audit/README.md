# Native frame audit of the QQ16 identity shear

Status: independent verification and a scoped correction; no new kappa.
This package audits the native implementation claim in [PR2216](https://github.com/CrocSwap/integer-mult-bounds/pull/2216).
The payload-constant rank certificate remains outside the correction.

## Precise claim and inherited boundary

Fix the retained QQ16 interface and the coordinate pairing below.
Keep the F0 output boundary and B1 input boundary unchanged.
The proposed insertion uses only the sixteen bare scalar updates shown here.

```text
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
X_T[j] += X_A[j]
Y_T[j] -= X_A[j]       (j = 0,...,7)
```

For every listed pair, its Y update fails to implement the stated logical subtraction on arbitrary payloads.
Its X update has equal source and target frames.
The claim concerns this insertion at the retained boundary, with no intervening conversion or changed boundary convention.

Let F=completed(0). The inherited boundary encodes logical values x and y as follows:

```text
physical X_p = F x_p
physical Y_p = F C_(q_p)^-1 y_p
C_q = ((1+i) I + (1-i) T_q)/2,    (T_q f)(z) = f(z XOR q)
```

This boundary is explicit in [CONSERVED-QQ16](../joint-query/evidence/CONSERVED-QQ16.md#cover-action-and-native-phases).
The [native review](../joint-query/evidence/NATIVE-REVIEW.md) states that B1 first converts X_T to the Y type.
The `boundary(stage)` function in [verify_native.py](../joint-query/verify_native.py) gives the same types.
We inherit the retained core's output contract; we do not replay or prove that complete core here.
The packet check confirms that F0's wrappers preserve the selected X types and never write Y_T.
It also checks B1's first eight normalizations against the corresponding Y types.

## Complete counterexample argument

Start with logical Y_T[j]=0 and X_A[j]=x.
A bare physical subtraction writes -F x.
The desired logical subtraction requires -F C_q^-1 x.
Since F is invertible, these outputs agree exactly when C_q x=x.
All translation lines commute here, so interpretation in the Y frame gives -C_q x instead of -x.
The two bare updates change the logical T sum by (I-C_q)x.

Each selected label q is nonzero in the first nine binary coordinates.
Choose w with q dot w=1 over F2, and set chi_w(z)=(-1)^(w dot z).
Then T_q chi_w=-chi_w, hence C_q chi_w=i chi_w and C_q^-1 chi_w=-i chi_w.
Thus the two outputs differ for every selected pair.
The logical sum changes by (1-i)chi_w instead of zero.

The witness sits at the identity-owner fiber with one nonconstant payload layer.
Keep the other payload layers and spectator coordinates constant.
This also gives a counterexample for every positive tensor length under the inherited tensor convention.
We retain the full owner cover.

For port 21, q=289 and w=1. Then F chi_w=i chi_w.
At address zero, the bare and desired outputs are -i and -1, respectively.
[RESULT.json](RESULT.json) records all eight exact witnesses.

PR2216's [cost paragraph](https://github.com/CrocSwap/integer-mult-bounds/blob/b80e9ba43367fb8b20877a97da1cb677c34f9264/research/qq16-f0-b1-shear-seedccce426/PROOF.md#cost-and-remaining-obligations) describes all data frames as common.
Its preceding experiment keeps each payload block constant.
On that restricted subspace every C_q acts as identity, so its test cannot detect the frame mismatch.
Sixteen bare additions do realize the shear on that subspace.
This audit does not replay or refute the reported rank-eight minor on that subspace.

## Independent checks and limits

The verifier authenticates four retained inputs and checks the relevant literal wrapper events.
It evaluates stored Z4 coefficient polynomials on all 512 active characters for each target.
A separate physical implementation applies Gaussian-integer C-line convolutions to eight 512-entry character arrays.
That implementation does not evaluate or generate phase polynomials and imports no predecessor executable.
Its outputs match the polynomial prediction and reject each bare subtraction.

Inverse-line adaptation passes; the positive-line sign fails.
Physical decoding also checks the nonzero logical sum change.
Constant payloads pass both paths and expose the restricted test's blind spot.

The complete argument above proves failure of the unrestricted scalar identity.
The finite checks bind its eight labels and witnesses to the pinned source.
They do not independently validate the full retained traversal, its native core, hosting, or the multiplication theorem.
The X count records eight equal-frame updates, rather than eight separate full-circuit tests.

## Cost boundary and contribution

A native implementation for arbitrary payloads needs an explicit typed adaptation or a fusion proof.
The semantic inverse-line control is not a free primitive or a hosted construction.
This audit proves no lower bound on additional children for a redesigned word.
It does not rule out reusing B1's existing operations.
The correction prevents an unrestricted controller from inheriting the sixteen-addition invoice without a typed implementation.
It changes no selected frontier or supplier certificate.

## Reproduce

From the repository root, run:

```sh
python3 -I -O -B research/qq16-shear-native-frame-audit/verify.py
```

Expected: `PASS_QQ16_SHEAR_NATIVE_FRAME_AUDIT rejected_Y_adds=8 same_frame_X_updates=8 character_phases=4096 physical_vectors=8`.
Research verification uses CPython 3.15.0 through the Math research-python wrapper.
The generic package replay also passes in its required environment, CPython 3.12.12.
That second run is an explicit compatibility exception, not independent mathematical verification.

## Open next questions

Can a typed rewrite fuse the missing conversion into B1's existing native operations?
First emit that complete word and compare every arbitrary input and helper output.
Then price its children, maps, storage, restoration, precision, and hosting.
The current audit does not supply that construction.

## Credit and provenance

Ali Romman and the retained QQ16 lineage supply the maps, native words, and reviews.
Cinna Davis supplies the shear in PR2216, head b80e9ba43367fb8b20877a97da1cb677c34f9264.
The audit uses base 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2.
See [SOURCES.json](SOURCES.json) for exact input hashes and Git blobs.
PR2093's separate surviving A-defect concerns full-controller information, not this frame correction.

Prepared for Charles Bethin with substantial OpenAI Codex assistance. Apache-2.0.
No independent human review or formal-kernel proof occurs here.
