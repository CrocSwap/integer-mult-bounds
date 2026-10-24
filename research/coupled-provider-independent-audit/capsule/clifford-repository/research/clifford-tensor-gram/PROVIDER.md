# Complete selected-provider check and a pair-fusion obstruction

The new verifier passes the complete local provider selected from PR4610.
It also excludes **30,328 fixed pair fusions at every positive tensor width**.
This contribution does not increase kappa. The paid profile does not change.

The provider is the exact word at main commit
`1ec1119972c9aefe42525172d07b332fcff81cb4`. Its author head is
`20bb93cd990d2ff683e4d0fc56b87a42cd5d3296`. The paid catalogue comes from
the independent PR5241 admission at
`13efb5fc5f3b7c14ec2cfa181dd9eb6480972cf2`.
`provider/SOURCES.json` binds each copied input to its source Git object and
SHA-256. Frozen source files are not changed.

## Result and coverage

Each direction has 21,449 source events, 632 independent persistent inputs,
and one independent owned input. Every persistent output is checked. The owned
output must be zero. All 408 helper inputs remain arbitrary. Their outputs
have their specified native frame changes; they are not assumed to be zero.

The new quadratic-sum engine checks 7,000 oriented recipe classes:

| Class | Checks | Coverage |
| --- | ---: | --- |
| Paid transitions | 5,710 | All 6,596 event instances across both directions |
| Native warps | 360 | All 480 signed event instances |
| Helper boundaries | 34 | All 408 roles in each direction |
| Main adapters | 896 | All 448 adapter events in each direction |

These counts refer to labelled classes. They do not count distinct matrices.
For two unitary circuits U,V on D=512 coordinates, the checker requires
`tr(U* V)/D = 1`. Here `*` is the conjugate transpose. This equality proves
U=V, including absolute phase. Each circuit then has the same tensor power at
every positive width. A recipe's stored PASS status is not an input to this
test. The main adapter generator only proposes data. Acceptance does not
import or execute that generator or its native compiler.

The complete physical programs are also passed directly to `compact.certify`.
Their references contain every input and output role. The result is equality
at every positive width, with no nonzero endpoint entry. The complete sparse
expansion gives these measured support counts:

| Direction | Scalar/native instructions | Native symbols | Peak total terms | Peak terms in one row | Final terms |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forward | 24,827 | 1,297 | 22,331 | 156 | 744 |
| Backward | 24,819 | 1,297 | 12,930 | 148 | 744 |

These are counts for this fixed provider. General program support can still
grow exponentially. No dense tensor matrix is made. The separate check of
the displayed failure witnesses uses base-space vectors with 512 entries.

## Exact boundary and translation

Let F_U be the source canonical frame, C_q the source Gaussian gate, and
F_full the full frame. Write E_i for the entrance frame of persistent role i
and H_i for its exit frame. In the forward orientation:

- For 0<=i<112, E_i=C_(q_i) and H_i=F_full.
- For 112<=i<224, E_i=I and H_i=F_full C_(q_(i-112))^-1.
- For 224<=i<632, E_i=F_(start_i) and H_i=F_(final_i).

The backward orientation uses the entrywise conjugate of each native frame
and operator. A negative warp uses the inverse before this conjugation.
Conjugation is not replaced by the adjoint.

In these logical coordinates, the forward endpoint is
`L_(112+j) <- L_(112+j) + L_j` for 0<=j<112. The backward endpoint is
`L_j <- L_j - L_(112+j)`. All other persistent logical coordinates return
unchanged. Thus the persistent physical endpoint is

    diag(H_i^tensor f) T diag((E_i^-1)^tensor f).

This operator is invertible for every positive f. The owned input is erased,
and its output is zero. All scalar coefficients remain outside tensor powers.

The importer expands a paid transition a->b as F_b F_a^-1. A signed warp
becomes F_b K_signed F_a^-1. A scalar ADD retains its literal rational
coefficient. Owned CLEAR becomes scalar multiplication by zero. Owned COPY
becomes CLEAR followed by ADD. Borrowed CLEAR and COPY are rejected.

The 448 main adapter markers are included. An entrance adapter is
F_start E_i^-1. An exit adapter is H_i F_final^-1. There is a source detail
that must not be hidden: some identity exit markers precede the final climb.
The importer permits a marker at a different current frame only when the
adapter circuit is exactly the identity. A nonidentity marker must use its
actual current frame.
Every nonidentity entrance adapter must precede all uses of its role. Every
nonidentity exit adapter must follow all uses. The word audit checks both
conditions. Thus an adapter inside a candidate interval changes its endpoint
frame and has the identity logical map.

The sparse interpreter expands all independent inputs together. The existing
`compact.certify` interpreter expands one input at a time. Both complete
endpoints agree with the same explicit physical reference. The earlier
PR5241 free-group argument already proves this provider's algebraic lift.
The new contribution here is an executable application of the new Gram
engine, complete support measurements, and the obstruction below. It is not
a priority claim for that earlier lift argument.

## Fusion class

For each persistent role, list its paid climbs in chronological order. Take
every pair in this list, at all positive ranks. Paid events on the same role
or on other roles may occur between the two climbs. Native warps, scalar contacts,
adapters and complete owned-center windows may also occur between them.
There are **7,582 pairs per direction**. No adjacency or common middle-frame
condition is imposed. The domain includes all 2,658 adjacent pairs, including
all 1,363 adjacent rank-one pairs, per direction.

Let A and B be the literal physical operators of the first and second climb.
Let T be the complete interval between them. The original local map is BTA.
Two replacements are tested:

- Early fusion: apply BA at the first slot and remove the second slot. The
  local map becomes TBA.
- Late fusion: remove the first slot and apply BA at the second slot. The
  local map becomes BAT.

Every other physical operation is fixed. In particular, no scalar contact
is changed to a new native query. The product BA is used with its exact
phase, even when the middle frames differ. This gives 2*2*7582=30,328 candidate
rewrites. The domain does not include a new intermediate placement, a
changed pair of operators, simultaneous fusions, or a pair on different roles.

The initial invoice opportunity was two H1 jobs replaced by one H2 job.
For a legal replacement in each of 18 local calls, the complete delta would
be -36 H1 +18 H2. This is the physical-pair gap in the PR5243 handoff.
The proof also applies to the other rank pairs. The endpoint obstruction
rejects every candidate before a new complete pricing step.
No such saving is charged to the complete kappa calculation.

## Closed-cut lemma

At every persistent climb in this source, the owned register is either
unused and about to be initialized before any read, or is zero after a
completed lifetime. The word audit checks this property. It also checks
that only the owned register can be overwritten and that all reads occur
after initialization.

Set the unused owned entry to zero. At either end of each candidate interval,
the state is therefore determined by the 632 persistent fields. Each prefix,
interval and suffix defines a square linear map on those fields. This remains
true when the interval contains a whole owned-center window.

For a fixed positive f, write the complete baseline as S(BTA)P on persistent
fields. The complete endpoint above is invertible. A product of square
matrices over Q(i) can be invertible only when every factor is invertible.
Thus P and S are invertible. It follows that

    S(C-BTA)P = 0  if and only if  C-BTA = 0.

A nonzero interval defect therefore survives to the complete provider's
return. This argument does not require the persistent prefix or suffix to
be unitary. It does not carry a numerical norm bound through those maps.
It would fail at a cut with live owned information omitted from the state.

## A quantitative contact obstruction

Use the moving logical frames at the interval boundaries. Let M be the
interval's logical matrix. Frame changes and adapter changes are identity
maps in these coordinates. Scalar instructions remain scalar instructions.
Each native warp is the corresponding phase-bearing K operator.

For each candidate, the saved certificate gives an off-diagonal block of M
that touches the changed role r. That block is exactly

    M_(r,j) = q U^tensor f  or  M_(j,r) = q U^tensor f,  j != r,

where q is a nonzero rational and U is a signed word of native unitary maps.
The coefficient is obtained by exact free-group arithmetic. It is not a
sampled equality and holds for all positive f. The second replay checks every
saved coefficient with the earlier independent-input engine. A separate
role-list census checks that the saved pairs cover the entire declared class.

For early fusion, let G1 and G2 be the diagonal physical frames immediately
after A and immediately before B. Let G3 be the frame immediately after B.
Then the changed logical interval is L M R, where

    L = G3^-1 G2,
    R = G1^-1 B G1.

Both corrections act only on role r. Their r-blocks are conjugates of B^-1
and B. For late fusion the corresponding corrections have r-blocks conjugate
to A and A^-1. These formulas do not require the two middle frames to agree.

On the saved off-diagonal block, only one correction acts. The defect is a
unitary left or right multiple of q(V^tensor f-I), where V is a conjugate of
the relevant paid operator or its inverse. Let

    tau = tr(V)/D,  D=512.

The normalized squared Hilbert-Schmidt defect of this block is exactly

    q^2 (2 - 2 Re(tau^f)).

The new quadratic-sum engine calculates every required trace with exact
Gaussian rational arithmetic. In every case it checks

    Re(tau) <= 1/2,  |tau|^2 <= 1/2.

For f=1, the first inequality gives Re(tau^f)<=1/2. For f>=2, the second
gives |tau|^f<=1/2. The same bounds hold for the inverse, whose trace is the
complex conjugate. Consequently every saved block has normalized squared
defect at least **q^2>0 at every positive width**. The closed-cut lemma lifts
this obstruction to the complete provider.
The smallest saved q^2 is **1/256**, which is a uniform lower bound on the
selected cut-block defects. It is not a lower bound on the full-provider
defect after multiplication by its prefix and suffix.

`provider/FUSIONS.json.gz` contains all 15,164 contact certificates, the exact
event positions, ranks, four frame IDs, native word, scalar coefficient and two
traces. Each certificate excludes the early and late replacement.
`provider/WITNESSES.json` also gives twelve literal width-one basis witnesses
from the complete physical programs. They cover both directions, both
placements, equal and unequal middle frames, and nonadjacent pairs with a
higher-rank climb. The native source
amplitude evaluator checks each value without Gram traces or quadratic sums.

## Verification and limits

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -I -W error -B research/clifford-tensor-gram/verify_provider.py
python3.12 -I -O -W error -B research/clifford-tensor-gram/verify_provider.py
```

Expected final line:

```text
PASS_COMPLETE_PR4610_PROVIDER_AND_30328_FUSION_OBSTRUCTIONS
```

The replay checks source bytes, every recipe class, both complete programs,
the complete pair census, every contact coefficient, exact trace bounds and
the full-program witnesses. Negative controls cover an omitted paid class,
a wrong absolute phase, borrowed erasure, a cut with live owned data and a
missing contact. An identity interval is a positive control: no obstruction
is inferred merely from the presence of two paid operations.

The local paid profile remains `{1:2201,2:412,3:510,4:127,5:40,8:8}`: 3,298 jobs
and rank mass 5,327 per direction. The complete selected kappa remains
0.0030217758. This work does not reprice the controller, run a new outer
admission, or change the selected record. The five selected framework
assumptions remain. The result covers this ideal finite local provider and
its tensor substitution; it does not prove physical tape, precision, stock,
analytic recovery or the complete multiplication theorem.

The obstruction does not exclude changed contacts, joint use of several
fields, simultaneous rewrites, interior placement, owned-center pairs,
new operators or later source providers. In particular, it does not
subsume the separate frozen eight-relation row argument in PR5393.

## Open next questions

1. Can a changed scalar contact supply the missing transformed operand at a
   lower complete cost? Start from a saved contact certificate. Replace that
   actual contact, retain dirty restoration, and price the replacement query.
2. Can several coordinated fusions cancel their endpoint defects? Start with
   a small explicit set of saved pairs. Run the complete native endpoint test;
   individual rejection does not prove joint rejection.
3. Can the eight-width criterion help with a complete program whose endpoint
   cannot first be reduced by free-group identities? This provider gives a
   manageable support example, not a bound for other programs.

## Credit

Cao Yifan / intqwq supplies the selected PR4610 construction. Chris R /
Clear1nsight supplies the PR5241 independent paid catalogue, complete admission
and earlier quantified lift proof. Cinna Davis / 1337isnot1337 supplies the
retained controller, native warp and helper chain. zxv, Jacob Alan Sussman,
Dugongue, Rohan Arun, Jeremy Kothe, icekylinx, DreamingOfClouds and chafreaky
retain credit for the relevant native, frame, helper and adapter sources.
The source notices and `provider/NOTICE.md` give the source links. The scalar
arithmetic and frozen native kernel retain their existing notices.

The new provider importer, Gram application, cut proof, complete pair census
and receipts are by Ali Romman with substantial OpenAI Codex assistance.
The checks are author checks. Independent human review and a proof-kernel
verification are not claimed. Apache-2.0.
