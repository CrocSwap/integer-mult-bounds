# Task card (autoresearch.md section 3)

Task ID / proposed scope key: bit-new-register-model / scope key 7f5f4426ef796683c485,
refined: `q8-central-commutator-pair` (F2[Q8], r=2 and r=3, central commutator pair).
Base commit; exact predecessor and dependency heads: base 0b1cccf86e2f5132ed286a26ef0a681a495740ea;
selected-record SHA-256 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32.
Predecessor package research/bit-dihedral-commutator (woklerx, PR 1443) at the base commit.

Concrete object and question: formal F2[Q8], Q8 = {±1, ±i, ±j, ±k}; paid labels x = i, y = j
only; paid factors D_N(g) = I + ([g]+1)N with N = uv^T, v^T u = 1, in M_r(F2); free scalar
GL_r(F2) mixing normalized by augmentation (predecessor's normalization); arbitrary dirty
register inputs. Target diag([z],[z]) with z = xyxy = x^2 = y^2 = −1 (the commutator, central
of order two). Question: exact minimum paid-call count; direct bill is four; can rank-one
idempotent sharing compress below four? Secondary endpoint: r = 3, target diag([z],[z],[e])
with one restored dirty register.

Scope status: refined. Reason: the card's allowed variation "a specified nonabelian operation
family" is instantiated as the quaternion group; the predecessor fixes address group
UT3(F2) ≅ D8 and states "No larger register count or different address group is excluded".

Existing restriction being changed: the address group of the formal register model
(D8 → Q8). Note the arithmetic difference: in Q8 the central commutator is a paid-label
square (z = x^2 = y^2), so the direct bill is 4 rather than the dihedral 8.

Method; explicit parameter ranges/candidate alphabet: complete BFS over the formal matrix
monoid M_r(F2[Q8]) with all generators; r = 2 has 6 rank-one idempotents x 2 labels = 12
generators, r = 3 has 28 x 2 = 56. Exact formal group-algebra equality in every coefficient
(no finite-address tests). BFS depth ≤ direct bill − 1 decides compression; a found word of
length d plus complete depth-(d−1) coverage certifies the minimum.

Nearest overlapping PRs and why this adds something: PR 1443 (D8 central pair min 8,
different group and different commutator arithmetic); PR 1742 (D8 third dirty register,
negative); PR 1478/1573 (UT3 commutator closed at 4k for all registers); the F2[GL2(F2)]
coordinate-CNOT/SWAP line (PR 1333/1414/1491/1495/1496; order-six group ≅ S3); S4/S5 target
PRs (1716/1720/1734/1749); AGL2/GL3 claims of 1337isnot1337. No Q8 object found in the
overlap survey (find_overlap.py, refreshed 2026-10-14T10:17Z).

Optimistic full cost budget; required observable improvement: no kappa claim is possible
(bit side does not bind). Observable: exact minimum versus the direct bill of 4 in the
optimistic scalar-cost relaxation, with all interface hypotheses named.

Success evidence; falsification test; time/compute cap: BFS layer counts + literal witness
word re-multiplied by an independent engine; controls: mutated targets rejected, each
single-call omission of a witness rejected, group-law checks for Q8. Compute cap 20 minutes.

Predecessor authors; intended artifact and reproduction command: woklerx (PR 1443);
eumemic PR 288 section 1.2 (scalar-idempotent model); Ali Romman PR 468; Gareth Davidson
PR 1333 (augmentation normalization). Artifact: research/q8-central-commutator-pair/ with
`python -I -O -B research/q8-central-commutator-pair/verify.py`. Contributor: Aaron Wang,
with help from opencode.
