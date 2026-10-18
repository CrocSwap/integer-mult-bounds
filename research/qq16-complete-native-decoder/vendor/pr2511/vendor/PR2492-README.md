# A paid native reconstruction of QQ16's L2 old-cut record

PR2470's L2 record can be reconstructed by an explicit local native word with
all 200 source arrays unchanged at its boundary. The word produces 96 owned
outputs in the old F0 completed-X frame. It costs 400 rank-one children,
96 rank-eight children, 208 full-cover maps and 6,624 real scalar primitives
under the retained QQ16 allowance. Its native rank mass is 1,168.

The useful distinction is between the logical L2 identity and a legal native
read across two cuts. Directly applying the current-chart alignment fails:
it also moves the frame accumulated by B1. This construction explicitly removes
that frame on its owned sums before the selected correction. The verifier
rejects the cheap alignment on all 96 ordinary ports.

This is one paid local reconstruction, not a complete 224-input decoder or a
storage saving. Its 96 output arrays are owned, allocated and charged as a
separate requirement. Delivery of the eight earlier T records is assumed.
Their capture, retention and retirement are not supplied here. The remainder
of the decoder, global hosting, physical movement costs, precision and supplier
invoice remain open. No new supplier or kappa is claimed.

## Exact source and field contract

Canonical main is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The retained joint-query packet and selected-replay archive supply the actual
centre matrix R, port labels, native phases and all current-chart owner maps.
[SOURCES.json](SOURCES.json) pins canonical inputs; [PREDECESSORS.json](PREDECESSORS.json)
binds the retained pending proof/code bytes and their Git blobs.

PR2470 (`1b2eee3bf1ec67e68c0b0fa7f47c7b2a66febe56`) supplies the L2 lead.
PR2468 (`baa90ee8176931e697d91a9024114ee2e9a189ea`) supplies the source
reconstruction, phase-polynomial and line-kernel methods adapted in
`native_support.py`. That predecessor implements a different query, B2 C,
using future chart 2. This package uses current chart 1 and adds the necessary
cross-cut frame removal. The adaptation is credited, not presented as a
second independent implementation of PR2468.

Let L be axes 0..8, E1 axes 9..16, and U1=L+E1. At owner d write
`F_V = product_(v in the specified orthonormal axes of V) C_(d v)` and
`C_q = ((1+i)I+(1-i)T_q)/2`. The three input families are:

| Inputs | Count | Native frame | Meaning |
| --- | ---: | --- | --- |
| X_p, p in U | 96 | F_U1 | live post-B1 X2_U |
| Y_p, p in U | 96 | F_U1 C_qp^-1 | live post-B1 Y2_U |
| T_t, t in T | 8 | F_L | retained post-F0 x1_T |

All 200 arrays may vary independently in the local operator contract. Their
source content and frame are restored; X is read-only. No arbitrary dirty
helper is cleared. There are 96 exclusively owned output arrays Z_p whose
initial values are discarded, and one exclusively owned local scratch C,
cleared before and after each query at each owner. The scratch is not a
cover-wide bank. Other source/helper fields are untouched.

The output, in frame F_L, is

```
Z_p = X_p + Y_p - sum_(t in T) (R_U^T R_T)[p,t]/4 D_1(p)^-1 D_1(t) T_t.
```

The logical route `D_1(p)` changes the owner by the actual involution rho1(p).
It is distinct from its physical translated native alignment. All route
products retain their order. Applied at the specified cuts, this gives x1_U:
the retained backward contract says `X2_U=x1_U-y1_U` and
`Y2_U=y1_U+K_(1,U) ell_(1,T) x1_T`. Their sum minus the correction is x1_U.
This algebraic identity is credited to the QQ16 contract and PR2470; the new
result is its paid native realization with exact restoration and scope.

## Construction and proof

For each port use the pinned map

```
A_p = M(rho1(p), delta_p),
M(g,a) f(d,z1,...,zlambda) = f(dg,z1+d a,...,zlambda+d a).
```

Its inverse is `(g^-1,g^-1 a)`, not merely `(g^-1,a)`. The retained bridge
identity at the old cut is

```
A_p [F_L C_qp^-1] = F_E1 D_1(p).
```

The bracket denotes the physical representation of logical data, so this
identity includes owner change, payload translation and the resulting native
phase. The verifier reconstructs every relevant actual rho/delta and checks
the entire Z/4 phase polynomial in all 73 character bits. Equality per tensor
layer extends to every number of layers; spectators remain unchanged.

Execute the following literal sweeps, recorded in [WORD.json](WORD.json):

1. Apply positive C_qp to each Y_p, so its frame matches X_p. Clear Z_p in
   that common frame and add X_p and Y_p. Apply inverse C_qp to restore Y_p.
   Now Z represents X+Y in F_U1 and both source families are restored.
2. Apply `F_E1^-1` to each owned Z_p. Since the axis factors commute,
   `F_E1^-1 F_U1 = F_L`. The logical content is unchanged. No source is
   subjected to this additional rank-eight child.
3. Apply inverse C_q followed by A_p to all Z_U and retained T_T fields.
   Both families now have the common frame F_E1. Their logical rows are
   `D_1(p)(X_p+Y_p)` and `D_1(t)T_t`.
4. Complete one private sweep. At each owner, for k=0..7, clear C, form
   `C=sum_t R[k,t] D_1(t)T_t`, add `-R[k,p] C/4` to each nonzero U row,
   and clear C. Every ADD has exactly the same native frame. Complete the
   entire body at that owner before reusing C at another owner.
5. Undo each T and Z alignment with its actual inverse, then apply positive
   C_q. T returns to its input frame and content; Z has the displayed ordered
   operator in frame F_L. The private scratch returns to zero/identity.

Every cover-map sweep finishes before the next sweep or scalar body begins.
The proof never reads a partially permuted bank. In step 4 only the owned
outputs change; retained T sources stay fixed throughout all eight queries.

### Why the tempting cheap alignment fails

Applying A_p directly to `F_U1 C_qp^-1` does not produce the old common
F_E1 frame. The current rho1 swaps the port's eight orthogonal chart vectors
with E1, so the *already accumulated* F_E1 factor moves back to a port-dependent
frame. PR2468's future chart 2 leaves E1 alone; that proof cannot be transferred
by simply changing its chart index. A complete phase comparison rejects the
shortcut for all 96 ports. Omitting stage removal from this word also fails
an actual scalar ADD phase check. This is a boundary of the attempted shortcut,
not a defect attributed to either predecessor.

## Native lowering and local invoice

For a nonzero q, an invertible binary wrapper P sending e0 to q gives
`C_q=P C_e0 P^-1`; the negative line uses `C_q^-1=T_q C_q`, with T_q fused
into the left wrapper. These are exactly one inherited positive rank-one child
and two monomial wrappers. The checker verifies both signs on all 512 basis
columns for each of the 104 distinct source/target port lines.

Let P exchange axes 0..7 with 9..16 and fix every other axis. Then

```
F_E1^-1 = T_(e9+...+e16) P F_8 P^-1.
```

This uses one positive rank-eight child and two monomial wrappers. At another
owner the complete recipe is conjugated by that owner's coordinate embedding.
The formula holds on arbitrary arrays and spectators, and tensorizes over
layers. The exact Gaussian checker compares all 65,536 coefficients of its
256-by-256 active kernel against the product of eight inverse line kernels;
all have common denominator 256. The full 73-axis wrapper and its inverse are
also checked. This proves the local inherited child identity; it does not
place 96 new children in the global supplier schedule.

| Operation | Count |
| --- | ---: |
| rank-one children: Y normalization/restoration | 192 |
| rank-one children: Z normalization/restoration | 192 |
| rank-one children: retained T normalization/restoration | 16 |
| rank-eight children: owned Z stage removal | 96 |
| native rank mass | 1,168 |
| native monomial wrapper maps | 992 |
| full-cover maps, both directions | 208 |
| unit ADD macros | 224 |
| quarter-coefficient ADD macros | 384 |
| CLEAR macros | 112 |
| real scalar primitive allowance | 6,624 |
| owned output arrays / local private scratch | 96 / 1 |

The real scalar allowance is bound to `joint-query/verify_scalar.py`:
224 unit ADDs cost 8 each, 384 quarter ADDs cost 12 each, and 112 CLEARs cost 2
each. The source function is hash-checked and evaluated in isolation. Counting
quarter ADDs like unit ADDs would understate this allowance by 1,536.
Native wrapper and cover-map counts are operations, not physical tape or
stream time. These counts are a constructive upper invoice, with no optimality
claim. Capture/retention of the earlier eight source records and subsequent
use/retirement of the 96 outputs are additional obligations.

## Reproduce and validation

Python 3.12, standard library only, from the repository root:

```
python3 -I -B research/qq16-l2-native-reconstruction/verify.py
python3 -I -O -B research/qq16-l2-native-reconstruction/test_verify.py
python3 scripts/research_package.py --package research/qq16-l2-native-reconstruction
```

Expected main marker:
`PASS_QQ16_L2_NATIVE_RECONSTRUCTION sources=200 outputs=96 rank_mass=1168 controls=9 no_new_kappa`.

The default replay is read-only and compares the complete literal word and
receipt, not just a digest or operation counts. It checks 200 independent
source-array symbols with exact noncommuting owner products, all 96 output
rows and source restoration, full 73-bit native phase identities, 106,496
rank-one basis columns and 65,536 rank-eight coefficients. The written operator
proof supplies the arbitrary-owner/array implication; the finite checks are
reported separately. Nine semantic controls reject missing Y normalization,
missing T restoration, missing or wrongly signed accumulated-stage removal,
missing or wrong inverse payload translation, uncleared output dirt, wrong
correction sign and a payload-only owner map. No proof assistant or selected
supplier cold replay is claimed.

## Open next questions

Can the complete immediate-cut decoder consume these outputs without storing
all 96 simultaneously? First specify the decoder's ordered reads, output
lifetimes and reconstruction schedule, then count capture, retention and
retirement. The present owned-output contract does not settle that question.

Can a lower-cost native representation avoid 96 rank-eight stage removals?
First exhibit an exact common physical frame for the live sums and old T
records, including accumulated E1 and all owner translations. The rejected
direct current alignment cannot be used as that premise. No lower bound on
all possible native reconstructions is claimed.

Can the full controller and supplier admit the new children and outputs?
Bind each child/output to actual owners, include physical maps, recursive
precision, all four bank repairs and the final retained boundary. Those
global contracts are absent here.

## Credit and overlap

Credit thakrarsagar / PR2470 for L2 and the retention census; starship-s /
PR2443 for the original cut decoder; Ali Romman / PR1969 for the complete
QQ16 maps, native word and bridge convention; ywz65 / PR2456 and PR2468 for
the operator audit and native read methods; and the retained selected geometry,
local-core and native interpretation lineage. Source notices remain in the
unchanged retained files. New work is Apache-2.0.

Ross Richardson's active discussion 2424 claim at 12:06 UTC minimizes a different
part of the contract: 24 retained arrays and an information lower bound with
reads granted. This package neither minimizes the record nor proves that
decoder. Its narrow advance claim is
https://github.com/CrocSwap/integer-mult-bounds/pull/2470#issuecomment-6191762591.
The initial complete overlap refresh covered 677 open PRs and 1194 discussion
records; exact source pins, freshness and the task-card refinement are recorded
in TASK. No text search is a novelty guarantee.

Prepared for **ywz65** with substantial OpenAI Codex assistance in derivation,
source review, implementation, verification and writing. Agent review is
distinct from independent human or maintainer acceptance.
