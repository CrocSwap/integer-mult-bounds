# Live copied values require operator intertwining under simultaneous rebasing

At a live COPY/ERASE cut, synchronizing the same scalar helper and temporary gates is not sufficient when their snapshot operators differ. For arbitrary nonzero linear snapshot maps over F2, a simultaneous invertible helper map U and copied-slot map V is legal exactly when

`diag(C_i) U = V diag(C_i)`.

This admits precisely common invertible block maps U=V within classes of **equal complete operators C_i**. If the C_i are pairwise distinct, only U=V=I is possible. Equality of ranks is insufficient. This is a scoped interface obstruction, not a physical supplier result or new kappa.

## Exact changed contract and proof

Let each arbitrary dirty helper h_i belong to a common F2 module M, and each snapshot t_i=C_i h_i to a common F2 module N. The C_i:M->N are fixed nonzero linear maps. Mixing helpers uses scalar U in GL_q(F2); copied-slot mixing uses scalar V in GL_q(F2). The copy validator at the cut requires t_i=C_i h'_i for every i, with the original snapshot operator for that role. No alias, reset, source mutation, hidden allocation, or change of C_i is admitted.

After the two changes, h'=U h and t'=V C h. Equality on every arbitrary input is equivalent to C U=V C. Its i,j entry is U_ij C_i=V_ij C_j. Since both maps are nonzero and the scalar field is F2, this equation forces U_ij=V_ij; a common value1 further forces C_i=C_j. Consequently U=V has zero entries between unequal-operator classes, and every diagonal class block must be invertible. Conversely every such common block map satisfies the equation. The number of legal pairs is therefore the product over class sizes s of |GL_s(F2)| = product over s and 0<=j<s of (2^s-2^j). This holds for arbitrary modules and arbitrary q; no finite test is substituted for the proof.

For two distinct snapshot maps the six possible synchronized GL2 changes collapse to identity. For two equal maps all six are legal. Allowing the zero operator would invalidate the entrywise argument; nonzero is a named hypothesis. Changing C itself requires a separate physical contract.

## Relation to actual predecessor interfaces

PR1437 freezes the copied value and permits changing helper values only when the copied functional is pointwise fixed. Here both sides may change before their ERASE comparison. PR1704 instead keeps original centers immutable, changes two ZERO-frame copied outputs temporarily, and restores those outputs to their original snapshots before ERASE. Its proof explicitly warns that outputs of different snapshot operators must not be equated. This result classifies the distinct proposal of maintaining equality by synchronizing changes on both sides. It does not reject PR1704 or identify any selected-supplier bug.

This package deliberately does **not** equate distinct frame labels with distinct complete C_i, nor infer operator equality from equal COPY rank. Actual physical maps must be reconstructed before applying the classification to R439 or another supplier. No native checker is changed, disabled or claimed to accept the changed contract.

## Complete local price and smallest falsification

For equal operators C, the schedule COPY both; h0+=h1; t0+=t1; ERASE both; h0+=h1 restores arbitrary helpers and passes both cut equalities. It uses two COPY/ERASE pairs, peak two live copied slots, and three scalar ADDs, including the final helper restoration. No original helper or temporary is free. The two copy ranks, frame changes and physical workspace costs remain those of the supplied COPY implementation; no reduction is asserted. Any target readers during the changed basis need their own fully priced compensation, which is outside this no-reader pilot.

For unequal nonzero maps C0=I and C1=SWAP on F2^2, doing the same two synchronized ADDs can violate t0=C0 h0'. For example h0=0,h1=(1,0) gives t0=(0,1) but C0 h0'=(1,0). Both maps have rank2, all helpers eventually restore, and the scalar coefficient U=V matches. These weaker facts do not discharge the live operator equality.

## Reproduce and limits

`python -I -O -B research/bit-live-copy-operator-intertwiner/verify.py`

`python3.12 scripts/research_package.py --package research/bit-live-copy-operator-intertwiner`

The complete two-role census uses every ordered pair of nonzero 2x2 binary operators (225), every GL2 U,V pair (36), and every dirty input (16). Exactly300 of8100 pairs pass. A separate coefficient calculation and literal input execution agree throughout. Five three-role equality partitions exhaust all168^2 U,V pairs each, obtaining168,6,6,6,1. The verifier checks the exact paid equal-operator schedule, rejects the unequal same-rank counterexample, and rejects moving restoration past an ERASE. Controls remain active under -O.

Not run: physical COPY-map identification, frames/admission, native implementation, actual R439 scatter replay, hosted invoice, precision/tape, all-size compiler, supplier adoption and outer assembly. The theorem proves a boundary classification in its explicit module model; it does not improve a recursive profile.

## Open next questions

Which equal complete snapshot maps occur at an actual simultaneous-copy cut? Reconstruct those maps before optimizing scalar rebasing. Rank equality alone cannot screen this question. The blocker is physical COPY semantics and workspace admission. Structured question: TASK.json.

## Credit

Credit woklerx PR1437 for the fixed-snapshot live stabilizer; Ross Richardson PR1704 for two-copy scatter and its explicit snapshot noninterference contract; Sagar Thakrar PR1062, the PR967 helper-star lineage, DreamingOfClouds PR589 and eumemic PR555 for the underlying context. PR1704's README is unchanged with exact head, blob and SHA256 in PREDECESSOR.json. The new result is the simultaneous operator-valued classification. Prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0; no independent human review claimed.
