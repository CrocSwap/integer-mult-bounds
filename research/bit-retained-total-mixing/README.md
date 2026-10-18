# Late mixing of the nine PR589 totals cannot improve their COPY budget

For the pinned PR589 R439 word, the nine retained helpers reach the scatter at
nine distinct rational hyperplanes of dimension seven. Any in-place XOR network
among these helpers, inserted after their original A preparation and before all
nine COPY calls, has COPY rank sum at least **63**. If it contains any cross-helper
gate, the sum is at least **65**. This excludes a concrete proposed interface
extension before costly synthesis. It does not exclude rebuilding the decoder.

## Contract and proof

There are exactly nine arbitrary dirty helper values h, no extra roles or COPYs,
no frame descents, and one COPY of each helper after the network. Allowed gates
are scalar XORs h_i += h_j at a common frame containing both current frames.
The scalar network U is invertible. Use scatter S U^-1 and restore helpers by
U^-1, so the full boundary is h'=h and y'=y+Sh for every dirty h,y. Neither
frame changes nor the nine COPYs are free. The retained checker requires every
operand of an ADD to climb to its gate frame and COPY charges the current frame
dimension, not the scalar support after cancellation.

Two distinct dimension-seven subspaces of an eight-dimensional space span the
full space. Thus the first gate touching any pair of the original helpers must
put both at the full frame. More generally, each touched helper is full: if its
partner was touched previously it is already full; otherwise the original two
hyperplanes differ. Monotonicity prevents descent. Untouched helpers keep their
seven-dimensional frames. With t touched registers the COPY profile is exactly
(9-t)H7+tH8, even if the scalar network later cancels to the identity. Any
nonempty network has t>=2. This proves the bound for unbounded network length,
not just the 72 elementary tests. Coincident initial hyperplanes are explicitly
excluded and are a positive countercontrol to strictness.

An optimistic full invoice grants all scalar gates for free and allows all
remaining climbs to merge with existing climbs. A retained helper originally
has only a rank-one final climb after its rank-seven preparation; moving that
climb earlier saves no rank or power charge. All other roles and paid events
are held fixed by this contract. The COPY contribution rises by
t(8^(1-a)-7^(1-a))>0 for 0<=a<1, so even this optimistic completed budget cannot
improve. Additional realization, restoration or scatter work can only add cost.
We do not assert every conjugate scatter meets the original target-frame
interface: granting it legality only strengthens this exclusion.

## Reproduction and evidence

`python -I -O -B research/bit-retained-total-mixing/verify.py` checks exact source
hashes, reconstructs pre-scatter frames, classifies all 511 nonempty support
joins, and independently checks all 36 pair joins using rational elimination.
All 72 directed XORs preserve the formal dirty boundary with conjugate scatter
and restoration; stale scatter and omitted restoration are rejected separately.
The certificate is regenerated in memory and compared in full. The source
checker is pinned as interface specification, not imported by the verifier.
Python 3.12 registered replay, optimized replay and selected integrity pass;
native supplier, hosted/full cold and outer assembly replays are not run.

The earlier copy-path-sharing barrier only screened pairwise overlapping source
reads, finding disjoint totals. This result concerns arbitrary late basis-change
networks and paid frame monotonicity. PR765 concerns abstract tensor decoder
factorizations; PR1194 concerns zero-frame D substitution. Neither is used as a
new theorem here. This is a scoped obstruction, not new kappa or native admission.
OVERLAP.json records cached complete pagination and its offline freshness limits;
root refreshes live overlap before any publication.

## Open next questions

Mixing before individual totals reach their hyperplanes changes this premise.
First identify a shared earlier frame and price all subsequent preparation,
COPY, inverse basis changes and target scatter. A favorable completed budget is
the blocker; increasing late-network length cannot reopen this result.

## Credit

The word is DreamingOfClouds' PR589 on eumemic's PR555 and checker lineage.
The prior copy-path barrier credits Sagar Thakrar's restored sharing mechanism.
Prepared by woklerx with substantial OpenAI Codex assistance. Apache-2.0.
