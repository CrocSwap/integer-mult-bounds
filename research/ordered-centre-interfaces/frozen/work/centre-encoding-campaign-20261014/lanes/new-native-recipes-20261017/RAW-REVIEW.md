# Independent review of the raw selected local maps

The five local maps pass this review. No material error was found in their
formulas, physical exchanges, new line recipes, or stated local invoices.
The accepted scope is a local map on the declared input and output arrays.
There is no accepted global controller, decoder, owner allocation, or new
complete kappa value in this result.

| Variant | Added rank-one children | Native mass | Real scalar bound |
| --- | ---: | ---: | ---: |
| B0: no input line correction | 0 | 5522 | 206506 |
| B8: input line correction | 8 | 5530 | 210714 |
| B16: input and ordinary-output corrections | 16 | 5538 | 214922 |
| F0: raw forward exchange | 0 | 5522 | 202554 |
| F8: coded forward exchange | 8 | 5530 | 206762 |

These bounds count the literal non-child scalar operations and the native
rank profile. They are not a complete recursive cost calculation. Child
hosting, actual inter-call views, final code removal, storage, and precision
remain separate obligations.

## Independent method

`check_raw_selected.py` does not import a producer checker or emitter. It
reads the frozen event packets and checks that each retained core is the
byte-exact old centre-free core. It reconstructs that core by a reverse
transpose calculation. Starting with every output covector, it passes
through the scalar events in reverse order. An event `t += c s` changes
the source covector by `w_s += c w_t`. An owned clear deletes the target
covector. This method computes every input column of the local linear map.

The result on all 712 input columns is exactly

    F_core: (x,y,h) -> (x,y+Jx,h),
    B_core: (x,y,h) -> (x-Jy,y,h),

with all eight owned private outputs zero. The checker derives
`J=I-R^T R/4` directly from the pinned source matrix. It verifies the block
identities `J_AA=0`, `J_AU=-B`, `J_UA=-D`, `J_UU=I-DB`, and `BD=13I`.

The checker then composes the physical boundary tapes with the reconstructed
matrix over a free group algebra. Each Q_p and Q_p inverse is a distinct
formal operator. Reduction cancels only adjacent inverse letters. It does
not commute two Q operators or move a Q operator through B or D. Equality
in this algebra proves the displayed local formulas for every substitution
of invertible operators. In particular, it applies to the actual native Q
operators once their physical recipes are checked.

Every variant is checked on all 712 input columns. Its data inverse is
also checked on all 224 data columns. All 480 logical helper values are
unchanged under the inherited native endpoint and wrapper contract. The
new boundaries never touch a helper. The retained physical residual child
progress on helpers is not an identity on unframed arrays; the review does
not make that different claim.

## Actual physical coordinates

The input convention is `X_p=Q_p x_p`, `Y_p=y_p`. The output convention is
`X_p=F x'_p`, `Y_p=F Q_p^-1 y'_p`. The review checks all 448 data endpoint
frame declarations in the canonical word. It also checks every retained
scalar frame, every native nested-subspace transition, and every ordinary
and residual adapter endpoint.

A physical selected exchange therefore sends

    (x_A,y_A) -> (Q_A^-1 y_A,Q_A x_A).

The literal three ADDs and one negative SCALE implement the exchange on
arbitrary arrays. They do not equate the two logical frame labels. The
checker rejects a replacement by a logical swap. At the final boundary,
the same physical exchange has the same two cross operators after the
common F factor is removed.

Each Q_p is a linear combination of the identity and the translation X_qp.
The full F is a product of such coordinate translation operators. Thus F
commutes with every Q_p and its inverse. The separate native interpreter
also verifies this equality, including global phase, for all 16 signed
selected line classes. This is the only commutation needed to remove the
common F factor. No proof step moves Q through a port mixing matrix.

The boundary ADDs act at common physical addresses of the local arrays.
Their resulting operator code is retained in the formulas. This establishes
a physical local array operation with an encoded interface. It does not
establish that a proposed outer controller supplies or consumes these
views at its actual call sites.

## Accepted formulas

Write `x=(a,u)`, `y=(b,v)`, and `r=Q_A^-1 b`. The B0 map is

    X_A = r+Bv,
    X_U = u-v-Dr+DQ_A a,
    Y_A = Q_A a,
    Y_U = v.

For B8 the map is

    X_A = Bv-12r,
    X_U = u-v+DQ_A a,
    Y_A = Q_A a,
    Y_U = v-Dr.

B16 has the same selected and Y outputs as B8, with `X_U=u-v`. In all
three backward variants, physical selected Y is exactly `F a`.

Both forward variants have

    X_A = a-Q_A^-1 Bu,
    X_U = u,
    Y_A = b.

F0 has `Y_U=v+(I-DB)u-DQ_A^-1 b`. F8 has `Y_U=v+(I-DB)u`.

The inverse checks do not divide by 12 or 13. For B8 and B16,
`r=X_A-BY_U` and `v=Y_U+Dr`. For B0, `r=X_A-BY_U` and `v=Y_U`.
The other data follow by the stated signed Q and scalar operations.
These are content inverses. In particular, the `B Y_U` query may span
different physical hole frames. The algebraic inverse is not a free
native decoder.

## New line kernels and verification boundary

The review pins the 16 signed line recipes from the earlier uniform-signed
packet. A separate Pauli and exact Gaussian state interpreter checks each
recipe against the intrinsic signed C_q operator. A second decoder applies
both serialized monomial wrappers, their affine addresses, translations,
quadratic terms, linear phases, and global phases to every basis input.
It compares all 8192 signed basis columns exactly. A wrong global phase
is rejected.

The retained core's full native phase proof is inherited from the pinned
`NATIVE-LIFT-REVIEW.json`, with SHA256
`61b3990c983b96b8bff01feab8c83a612ea41612b948b1059186ce9ffa9692ea`.
That receipt binds the exact core payload used here. This review repeats
the full scalar map and frame ledger. It does not repeat the old Clifford
recipe sweep or construct a dense physical operator on 712 arrays.

The controls also reject an omitted input code, an omitted lower shear,
an omitted physical swap, a wrong inverse-line sign, an omitted output
swap, and movement of Q through B. The last control has an actual native
counterexample: the selected and ordinary line directions give different
translated support on spatial basis input zero. The receipt records the
ports and the nonzero B entry.

## Inputs and reproduction

The reviewed producer files are the frozen raw-selected backward, forward,
and zero-line backward packets in `../native-escape-20261017`. Their source
proofs and checkers are pinned in `RAW-REVIEW-INPUTS.json`. The retained
core, canonical word, source matrix, prior native review, signed-line
packet, and independent spatial decoder are also pinned there.

Run from the workspace root:

    python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/check_raw_selected.py

Expected final status:

    PASS_INDEPENDENT_RAW_SELECTED_LOCAL_REVIEW

The result is in `RAW-REVIEW.json`. `RAW-REVIEW-FREEZE.json` pins this proof,
the checker, the input manifest, and the result. The native-escape lane,
the coordinating lane, and the prior centre-free and uniform-signed lanes
supplied the constructions. This lane supplied the separate review.
Research and review used OpenAI Codex under the user's direction. No human
or maintainer review is claimed. No PR, push, or publication commit was made.
