# Sharp tariff after adding a paid UT3 central call

For every finite register count r >= k >= 1, the exact positive uniform tariff for k central targets in the formal F2[UT3(F2)] model with paid labels a, b and c=abab is

`k min(2(alpha+beta), gamma)`.

Here alpha, beta and gamma are positive inclusive per-call prices. Mixing central and noncentral calls cannot beat both direct choices, even with arbitrary free scalar mixing and arbitrarily many restored dirty registers. This is a scoped tariff theorem, not an implemented supplier improvement or new kappa.

## Model and precise delta

Retain PR1573's formal group algebra, rank-one binary idempotents N=uv^T with v^T u=1, arbitrary scalar GL_r(F2) basis changes, and endpoint diag([c] repeated k times, identity on all remaining dirty roles). The changed alphabet admits D_N(c)=I+([c]+1)N as an additional **paid** primitive. Each a, b and c call costs alpha, beta and gamma respectively. No COPY, clean allocation, higher-rank unit-price call or free restoration is added. Prices must include their actual implementation overhead if used in a supplier comparison; this package supplies no such implementation.

The two-letter theorem in PR1573 gives n_a,n_b >= 2k. Its open question observes the two direct bills after adding c, but does not prove that hybrid words cannot undercut both. The new implication is

`n_a,n_b >= 2 max(k-n_c,0)`.

The first assignment's third-register census was abandoned upon overlap with PR1478, PR1573, PR1742 and PR1792. Its pilot is not counted as a result. The present change is one bounded alphabet pivot.

## Proof

Normalize free scalar maps into rank-one projectors by conjugation, as in PR1573; augmentation forces the final free scalar map to be identity. Write P=diag(I_k,0) and S=sum of the n_c central-call projectors. Apply the natural three-dimensional representation of UT3 entrywise to the complete register word. In address-block order, a contributes N at block01, b contributes N at block12, and c contributes N at block02. Products involving a central off-diagonal block and any other strictly upper-triangular block vanish. Thus the endpoint implies

`X_a Y_a=0`, `X_b Y_b=0`, `C_ab + S=P`,

where C_ab=sum over ordered a-before-b pairs of N_i N_j, X_g collects the u columns and Y_g the v rows. The automorphism sigma(x,y,z)=(y,x,z+xy) swaps a,b and fixes c. Its representation likewise gives `C_ba+S=P`.

Put q=rank(P+S). Since rank(S)<=n_c, q>=max(k-n_c,0). The column and row containments of C_ab and C_ba imply rank(X_a), rank(Y_a), rank(X_b), rank(Y_b) >= q. The zero products X_g Y_g=0 imply rank(X_g)+rank(Y_g)<=n_g by rank-nullity. Hence each noncentral count is at least2q, proving the displayed implication for every r and every word length.

Consequently the complete abstract bill is at least `2 max(k-n_c,0)(alpha+beta)+gamma n_c`. For 0<=n_c<=k this is affine in n_c, and above k its positive central term is at least k gamma. The minimum is therefore the claimed k times the cheaper direct tariff. It is attained by c on each target if gamma is smaller, or by abab on each target otherwise. More generally t central targets and k-t commutator targets attain every endpoint of the count tradeoff: `(n_a,n_b,n_c)=(2(k-t),2(k-t),t)`. All unused roles are identity operators on arbitrary inputs. This is an algebraic proof; finite fixtures are corroboration, not its substitute.

## Reproduce and evidence

`python -I -O -B research/ut3-priced-central-calls/verify.py`

`python scripts/research_package.py --package research/ut3-priced-central-calls`

Fourteen mixed words cover k=1..4 and every t=0..k with two extra dirty roles. A separate faithful regular-action engine uses literal binary 3x3 address matrices; it does not use the group-ring multiplication engine. Scalar-conjugated fixtures deliberately mix dirty inputs into targets. Every individual call omission is rejected. Further controls expose the invalid reuse of the two-letter bound after adding c, the need to price a rank-two central operation as two rank-one calls, and a zero-dirt false positive. Exact integer/rational tariff checks corroborate the affine optimization. The written rank proof supplies the arbitrary-register statement.

The selected result, native circuits, hosted supplier, all-size compiler, precision/tape, outer assembly and analytic transfer were not replayed. No new paid rank histogram, physical central implementation or kappa is claimed. The natural representations serve only necessary lower-bound conditions; formal equality of the upper constructions is separately checked.

## Open next questions

Can a real central operation have inclusive price below 2(alpha+beta)? That is now necessary for an improvement through this alphabet. Start with one concrete supplier frame and charge its entire central operation, frame transitions and restoration. The blocker is realization, not the abstract mixture optimization. Structured questions are in TASK.json.

## Sources and credit

The exact PR1573 README is preserved unchanged in PR1573-README.md with full commit, Git blob and SHA256 in PREDECESSOR.json. Credit steph4n-gh for the arbitrary-register two-representation/rank proof, juper997 PR1478 and woklerx PR1443 for finite D8 predecessors, Arham Tahir Discussion1569 for concurrent two-target reasoning, Gareth Davidson/bitplane PR1333 and the register-model lineage retained in the source. The new step allows paid c calls and proves the hybrid count/tariff bound. Prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0; no independent human review claimed.
