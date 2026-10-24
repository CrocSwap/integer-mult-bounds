# Nine passive macro cuts do not recover the four Gaussian jobs

This is a necessary-condition result for the prospective scope in Discussion #4902, expiry 06:00 UTC. It concerns the single frozen mixed p2 word from the preceding local packet. It does not change that word, inject a saved value into a later paid gate, access native internal prefixes, or emit a physical caller.

## Source and exact observation contract

The source is #4948, `86e474038e05f99a76d41f71d81946ad2327e4a4`, using its actual signed monomial normalizers K_i and involutory scalar matrix F. The native reverse primitive is

`B_s=diag(D_s,D_s) U(−Q C_s)`, `C_s=diag(K_s)^−1 F^T diag(K_s)`.

The source relations are `C_s²=I`, `[C_s,D_s Q]=0`, and `[C_s,D_t]=0` for distinct fresh stages. No own-stage `[C_s,D_s]` or `[C_s,Q]` commutation is assumed. Source-byte hashes are included in `GRADE-GATE.json`, inherited through the authenticated frozen mixed checker.

There are four independent original main input banks, each of 112 owners. The word keeps the source scalar right/left boundaries, initial paid IDLE, all bridges and signed swaps. Its three thins are exactly:

`C1 Q^-1` at stage 0, `Q^-1 C1` at stage 2, and `Q^-1 C3` at stage 4.

Choose these nine macro cuts, saving the four current main banks at each:

1. After the scalar right boundary.
2. After thin 0.
3. After FULL 1.
4. After the paid IDLE on pair 1.
5. After bridge-plus and thin 2.
6. After bridge-minus.
7. After FULL 3.
8. After thin 4.
9. After the final bridge, signed swaps and scalar left boundary.

Also save the three already paid responses in their actual order: `Q^-1 x` before C1 in thin 0; `Q^-1 C1 x` in thin 2; and `Q^-1 C3 x` in thin 4. Thus there are 39 dependent observed bank fields. The initial cut is after an invertible scalar boundary; it includes the original input information without adding a tenth cut.

Copies are passive. The original paid gates continue with precisely the frozen input expressions. New left decoder controls may combine arbitrary owner fields by scalar operations and apply the actual finite C1/C3 words of length at most three. They may be interleaved on decoder fields: every such resulting coefficient is still a finite scalar sum of monomial Clifford maps. No Q is free. Restoring the old autonomous helper jobs cannot change any coefficient of an independent original main input.

## The original-input dependency trace

Track original main bank 0, before the scalar right boundary. For its four current-bank coefficients and its three paid-response coefficients, the entire exact trace contains only signed occurrences of

`I`, `Q^-1`, `C1 Q^-1`, and `Q^-1 C1 D1`.

The checker verifies all 39 observations against precisely this set. In particular, there is no hidden D3 term or later query path for this original input. FULL 1 cancels its X coefficient. The bridge-minus cancels its pair-1 Y coefficient before FULL 3; it therefore never obtains the second transverse factor. This trace uses the original input, not a later field whose owner or frame was silently changed.

The preliminary bank-scalar span contains 273 candidate generators: 39 observations times the seven reduced words `I,C1,C3,C1C3,C3C1,C1C3C1,C3C1C3`. Its dimension is 92. Only the positive first-pair target is attained; its explicit recipe is minus C1 applied to the saved FULL-1 X row. This preliminary calculation alone does not cover arbitrary per-port scalar controls. The following grade argument does.

## Actual port coefficients and their grades

For original source port j in bank 0, the late observation `Q^-1 C1 D1` has output-port-i coefficient

`(F^T)_(i,j) Q^-1 K_i^-1 K_j D1`.

The actual F diagonal is zero at 104 ports and equals 12 at the other eight. For every one of the 104 zero-diagonal ports:

* Its same-port late term vanishes.
* Exactly 52 other output coefficients are nonzero.
* Every one of those 52 literal Clifford words has Fourier grade 7.

The exact signed-tableau census checks all **5,408** such nonzero words. It does not sample pairs. Each source K_i is monomial, and its commutation with the full nine-axis Gaussian is independently checked including absolute phase. The nine-axis grade calculation embeds into the actual 17-axis ambient space by leaving the other fresh eight axes untouched.

The earlier I path has grade 0. The earlier Q^-1 and C1 Q^-1 paths consist of grade-1 words because each K_i^-1 K_j is monomial. Hence every observed coefficient for each of these 104 original source inputs has pure-word support of grades in `{0,1,7}`.

By contrast, the required original first-bank target is `D1 Q^-1`, of grade **9**. The checker confirms this rank and also checks the eight nonzero diagonal ports as controls: their literal same-port late term has grade 9. Replacing the code by the identity likewise exposes the uncoded grade-9 term, and the preliminary uncoded span recovers all four ordinary targets.

## Why finite code controls cannot fill the missing grade

For a Clifford tableau, its Fourier grade is the rank of the X component in its images of the Z generators. Multiplying on the left by a monomial Clifford map applies an invertible address map to that X component and therefore preserves its rank. Scalar coefficients, phases, COPY and owner mixing do not create new pure operator words. Each entry of C1 or C3 is a scalar multiple of a monomial K_i^-1 K_j. Every finite code word expands into a finite scalar sum of monomial words.

Consequently, after any allowed passive left decoder, each of these original-source coefficients remains supported on pure words of grades `{0,1,7}`. Allowing arbitrary port-by-port scalar operations, extra decoder work arrays, or all finite COPY/CLEAR costs for free does not change this support fact. The eight selected ports cannot repair the absent coefficients of the 104 different arbitrary original inputs: those inputs are independent.

This is a pure-word support argument, not a claim that small-width Clifford matrices are linearly independent. The latter claim would be false.

## Sufficiently large width and the phase quotient

At column width f, each literal one-column operator word A is lifted as `A^tensor(f)`. The source scalar owner coefficients occur once, outside that tensor power. Each observed entry and finite code decoder expands as a finite sum of these pure-word tensor lifts. No tensor of a sum is replaced by a sum of tensor powers.

Group the finite one-column words into projective classes. Words differing by a scalar phase have the same grade; their phase to power f is absorbed into their scalar coefficient. Choose one unitary representative A_r from each remaining class. Distinct representatives satisfy

`|tr(A_r^* A_s)/dim(A_r)| < 1` for r≠s.

The normalized Hilbert–Schmidt Gram matrix of their f-fold tensor powers has off-diagonal entries equal to the f-th powers of these overlaps. The finite Gram matrix therefore tends to the identity as f tends to infinity, and is positive definite for all sufficiently large f. The projectively distinct pure-word tensor powers are consequently linearly independent at those widths. This remains true if the reconstruction's scalar coefficients depend on f.

The grade-9 target is projectively distinct from every grade-0, grade-1 or grade-7 word. It cannot lie in their span for sufficiently large f. Therefore no decoder in this passive finite-code grammar can supply an identity valid at every positive width. The proof does not assert failure at every small width, does not infer independence from width-1 arrays, and does not need to enumerate the whole Clifford group.

## Ownership, invoice and stopping decision

All-snapshot storage would add `39*112=4,368` dependent fields, initialized to owned zero, with 4,368 COPY operations and 4,368 final zero-reset obligations. The existing 448 original main inputs remain arbitrary. The 816 independent helper jobs remain unchanged and credited once. There is no fresh input or productive reward for a snapshot.

There is no accepted reset recipe: saved values would need to be erased using a still-available source or a permitted expression in retained outputs. Overwriting an owned snapshot, discarding its information, running the native inverse for free, and treating a dependent copy as a new arbitrary input are all excluded. A span identity alone would not settle those obligations.

The preceding optimistic recursive profile remains

`P={1:4754,2:824,3:1020,4:254,5:80,8:224}`,

`T={4:56,7:14,8:94,9:876,17:224}`,

with unrealized raw margin about 36.14614 at C=.0030217758. Here no new Gaussian is requested, but the required main endpoint already fails even when all added finite operations, code evaluations, storage, initialization, resets and precision are granted for free. Thus no finite bill can turn this specific passive-snapshot proposal into that supplier. No physical emission, compiler strictification, outer reserve, BIT promotion or κ claim follows.

Active use of a saved response as an input to a later paid Gaussian gate changes the original dependency trace and is outside this fixed-word result. So are new Gaussian calls, native internal prefix taps, a different thin placement, a different target profile, and f-dependent non-columnwise payload routing. Those require a new exact physical/cost contract.
