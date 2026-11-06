# Independent review of the sharp bound

Reviewed 2026-11-06 at10:10UTC, worker D. Source: worker-b/p104-n4-coupled-gap/SHARP-BOUND.md, SHA256 f7365ad8eb857327cc63fa28782cb3ef50b4e0cd5237829903b7cc909cbe6529. This review followed sealing D's independent rank21 construction; D had not read B's derivation before construction. AI-assisted mathematical review, not human or proof-kernel review.

**Conclusion:** the universal21q/2 lower bound under the stated inherited normal-form/actual-prefix contract is valid. I found no internal-block commutativity assumption or finite-search extrapolation. The equality inventory follows as claimed.

The coordinate reduction was checked independently, in particular the important order M_X J rather than J M_X. Since the selected query columns form a basis, M=KE has column support from E U_i=0 and row support from V_iE=0. The singleton sectors vanish because the corresponding diagonal block of K inverse is zero. The six remaining sectors and total-rank equation are correct.

For separated AB,CD sectors, J=v t^T−t v^T gives rankM≤rankMv+rankv^TM. Orthogonality passes through a q-dimensional space, so the two cross equations do imply x+z≤2q.

For the low sectors AB,BC,CD, the ordered adjacent forward multiplier is F=J inverse T0, its reverse is F inverse, and the two far multipliers are N and I−N after conjugation. I explicitly recomputed the block products and independently evaluated them on the rank21 fixture. Both controls replacing the far multipliers by I fail, so the fixture does exercise these constraints. The exact check is check_reduction.py; it passes with isolated Python.

Because PQ=QP=QR=RQ=0, P,R act on kerQ and vanish on imQ. Compressing N along imQ gives L with PLR=0 and R(I−L)P=0. If u lies in imP∩imR and phi in rowP∩rowR, then Pu=Ru=u and phiP=phiR=phi. Therefore phiLu=0 and phi(I−L)u=0, so phi u=0. This is the central implication; it does not require L to be idempotent, and the proof correctly does not assume that.

The canonical pairing between imP and rowP is nondegenerate because P is idempotent. Thus two orthogonal subspaces of dimensionsa,b within those spaces satisfy a+b≤rankP. Applying this to both P,R, with each intersection dimension at least x+z−m, yields 3(x+z)≤4m. Combining this with x+z≤2q gives x+y+z≤5q/2 in both cases y≤q/2,y≥q/2. The endpoint common sector w≥q then proves total≥21q/2.

At equality, y=q/2,w=q,x+z=2q, and the two individual rank inequalities force x=z=q. The remaining high sectors have h+j=q/2. Trimming can have lost no rank at an original optimum, so the stated nested endpoints and stage ranks follow. This checks the even-q equality inventory, not a canonical matrix classification or any native/physical implementation.

## Final-draft delta review

At10:19UTC I read the current complete SHARP-BOUND.md, SHA256 4e2c86e4ed33aff63b234a835f8c8e38151b577cb8a5a3095fac0e7c0ce3e06c. The new self-contained endpoint-prefix argument is valid: commutation with Q1 and Q1Q0 yields commutation with R0 because2 is invertible, and support of R1 plus invertible cross Gram forces both column and row support of R0. The analogous right-end implication follows from B3=−I−2R4. The added rank-lemma proof correctly uses row independence after restriction to imP.

The reflection formula B'_i=−B_(j−1), j=4−i, is correct. Original P_j commutes with Q_j and B_j, hence with B_(j−1); this preserves actual prefixes after reflection. Direct sums preserve every hypothesis. The all-placement corollary properly retains the inherited even-interior4q and other-three-stage7q bounds. No new mathematical objection was found.

Exact checked-file pins:

|File|SHA256|
|---|---|
|B SHARP-BOUND.md|4e2c86e4ed33aff63b234a835f8c8e38151b577cb8a5a3095fac0e7c0ce3e06c|
|B check.py|0a8c3dbac43e37920505c9610eea78aac3ebfebd5818b695b882ee7c244dba0e|
|D check_rank21.py|01de985a8137d4ba8a006aecc3eabc2d3cbd251a48dc7680efb1bd3c5d424133|
|D check_reduction.py|a5ded1111afe99ee721515b1a27660ad4285aa9520b6e18ef593add7f2c1539b|
|Shared ROOT-RANK21.json|b22d9085b8b0112b94b80ab807a11564e9a515dc8559c60b1f4a5a08ff04bb43|

The B checker pin identifies the reviewed package context; D's own independent matrix checker and reduction audit supply this review's executed evidence. Pinning B's checker is not a claim that D independently audited every line of that checker.

## Final combined package and no-idle corollary

The final combined package is worker-b/research/p104-four-field-sharp-rank. I checked the full presentation diff: author attribution, spacing and q=2 notation leave the earlier mathematics unchanged. New Section5 was reviewed in full. Final proof SHA256:41aa74357a06eab4bcd0985dbe189b43d07cfcba4f3a091a12d3a5589d15f4e3. Final B checker SHA256:dbc768c3da18cab10825a9177b5ca6b0cdd5902c3ccb6b78ff207e69b3a8f52f. Fixture and D checker/reduction pins above are unchanged.

The no-removable-idle-sector corollary is valid. The mask explicitly contains the trimmed stage. Unit pairing and same-sector support make F=ba an idempotent rank-one subprojector commuting with every stage. Matching eigenvalues give commutation with the actual prefix. Both idle equations give FR_i=R_iF=0. Hence P_i−F preserves idempotence, query support, all commutations and the full query word, while lowering total rank by one. This contradicts the established minimum for every optimal coupling. The exact scope is a rank-one trim within one joint sector, with matching prefix eigenvalues and both query products zero; arbitrary paid internal splits and mixed-mask mechanisms are not excluded.

The local control P=I2,R=E01,F=E00,prefix=−I2 is correct: RF=0 but FR=R, and (P−F)R=0 loses left support. It is appropriately labeled a local implication control rather than a complete root. The final prose-only simplification of the scope paragraph changes no condition. No further objection was found.
