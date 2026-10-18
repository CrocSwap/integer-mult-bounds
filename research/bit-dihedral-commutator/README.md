# Two central commutators require eight paid calls in a dihedral alphabet

In the explicit two-register formal F2[D8] model below, free scalar mixing
cannot shorten two central commutator targets. The exact minimum is **eight**
paid calls, attained by four direct calls on each register. This is a complete
finite alphabet result, not a claim about the original rational-frame model or
the multiplication exponent.

## Changed model and full price

Let G=UT3(F2), write g=(a,b,c) for [[1,a,c],[0,1,b],[0,0,1]], and multiply by
(a,b,c)(a',b',c')=(a+a',b+b',c+c'+ab'). This nonabelian group has eight elements.
Only x=(1,0,0) and y=(0,1,0) are legal paid labels. Each call is
D_N(g)=I+([g]+1)N, where N=u v^T is a binary rank-one idempotent on two scalar
registers. There are six N and twelve generators. All scalar GL2(F2) basis
changes are free, but no other address operation, extra role, COPY or clean
state is available. Both register inputs are arbitrary. Target is
diag([z],[z]), z=xyxy=(0,0,1).

Conjugating by a free scalar map merely conjugates N within these six projectors.
Move every free map through the paid factors; augmentation [g]->1 makes every
paid factor I and forces the remaining scalar map to equal the identity.
Thus the twelve-generator search covers arbitrary interleaved free scalar mixing.
Every generator is an involution because g^2=1 and N^2=N. The price is its
complete count of paid x/y calls; direct construction costs4+4=8. No central
label z may be declared a free or unit-price primitive.

The proposed nonabelian extension changes the original abelian rational-address
hypothesis explicitly. It is stricter than PR1333's unrestricted binary affine
rank-one alphabet, where z itself costs one call. The current coordinate-CNOT
follow-up in Discussion1317 uses GL2(F2), two SWAP targets, and a third dirty
register. Here the group, central target, allowed labels and role count differ.
The scope comparison is not a claim that either prior result is incorrect.

## Exact finite proof and independent witness

Matrices over F2[G] have four eight-bit coefficient cells. The verifier enumerates
the complete Cayley balls of radius4 around I and the target using all twelve
involutions. Both layer counts are1,12,80,472,2459. The balls intersect in398
states; every meeting has sum of minimum distances8. Any word of length<=7
splits into two portions of length<=4, producing a meeting of total length<=7.
There is none. The known eight-call direct word provides the upper bound.

This is exact formal group-algebra equality: all coefficients are stored, not a
test on one chosen address representation. A separate engine multiplies sets of
literal3x3 group matrices and verifies the shortest witness and direct word.
Each single-call omission of the shortest witness is rejected. Associativity
and the noncommuting central commutator are separately checked across the finite
group. Ball hashes and the complete witness are in CERTIFICATE.json. The search
establishes the bounded metric; the split argument establishes the minimum.

## Reproduce and limits

`python -I -O -B research/bit-dihedral-commutator/verify.py`

Python3.12 registered replay, source metadata and selected-integrity checks pass.
The native supplier and all-size physical compiler, frame, precision, hosting
and analytic obligations are not invoked or discharged. This is a deliberately
optimistic scalar-cost relaxation; it fails to save even before physical costs.
No larger register count or different address group is excluded.

## Open next questions

Does a restored third dirty register help for the same D8 central target?
First build exact balls using the28 rank-one scalar idempotents; use an explicit
memory cap and meet-in-the-middle counts. The two-register result gives a
comparison, not a proof for that expanded role model. Construction needs a
uniform formal identity and a full physical invoice if a saving is found.

## Credit

The scalar-idempotent normalization follows the retained three-register note
and eumemic PR288; the nonabelian affine direction is related to Gareth Davidson
PR1333 (head7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2) and its open follow-up.
Prepared by woklerx with substantial OpenAI Codex assistance. Apache-2.0.
No independent human review claimed. Cached overlap limits are in OVERLAP.json.
