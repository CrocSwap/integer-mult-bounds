# Exact audit of a common convolution-frame repair

The existing local word cannot be put in one common Walsh basis merely by
replacing its canonical frame representatives with convolution frames while
retaining the pointwise source-carry and target-read requirements below.
An actual helper has the same nonzero binary vector in both required
eigenspaces. This is a scoped obstruction to that repair, **not** an
obstruction to arbitrary complex circuits or to kappa 0.1.

The positive control matters: degenerate carried spaces do sometimes admit
a symmetric convolution frame. Degeneracy alone is not a rejection rule.

## Frozen inputs and replay

All inputs are Git blobs at
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`, authenticated by SHA256 in the
verifier. The scalar word comes from
`research/involutive-walsh-lift/evidence/WALSH-RETARGET-NATIVE.json.gz`.
Its binary frame bases and 112 port labels come from
`slots/local/CANONICAL-WORD.json.gz` inside
`research/community-frontier1042-audit/selected-replay.tar.gz`.
The exact original frame conjugation is checked with pinned
`research/involutive-walsh-lift/native.py`.

Run from the repository root:

```sh
python3 -I -B research/kappa01-outer-repair/convolution_frames.py
```

The command writes `CONVOLUTION-RESULT.json`. Both normal and optimized
Python must preserve its checks; the script uses explicit exceptions and
compiles the imported checker with `optimize=0`.

## The precise replacement model

Work over `H=F2^9`, with standard dot product. A convolution Clifford has
binary symplectic action

    F_A = [[I,A],[0,I]],       A=A^T,

and preimage of the coordinate Z-Lagrangian

    L(F_A) = {(A z,z): z in H}.

Its exact lift can be taken as a full Walsh conjugate of a quadratic
Gaussian phase. It then commutes with every translation and is diagonal
in one common full Walsh basis. This statement gives an operator lift,
not a cheap physical implementation of the Walsh entry and exit.

At a specified scalar cut, let C be the binary span of source port labels
having **nonzero exact rational coefficients** in the helper's current
scalar value. Let R be the binary span of target port labels whose final
scalar output has nonzero derivative with respect to that helper at that
cut. Coefficients are not reduced modulo two: their supports select the
binary labels, and those labels alone are then spanned over F2.

The replacement scheme under investigation retains the conditions

    (c,c) in L(F_A) for c in C,
    (0,r) in L(F_A) for r in R.                       (1)

They are exactly

    A c=c for c in C,        A r=0 for r in R.        (2)

These are the explicit source-carry and target-read requirements of this
scheme. We do **not** derive (1) as necessary for every complex circuit
with the same final input/output map. A changed representation, scalar
schedule, or global circuit could use different invariants.

For the actual canonical label

    L_U={(u,u+v): u in U, v in Uperp},

(1) is satisfied if and only if `C subset U` and `R subset Uperp`.
The reported negative and positive examples pass both conditions.
This checks that their source/read requirements agree with the original
frame geometry; it does not claim every future scalar dependency always
imposes a frame requirement. Indeed some other probed cuts fail the
canonical reader-containment test and are reported separately.

**Symmetric extension criterion.** There is a symmetric A satisfying
(2) if and only if `C intersect R=0` and `C perpendicular R`.

Necessity follows from applying A to an intersection vector and from
`c dot r=(Ac) dot r=c dot (Ar)=0`. For sufficiency define
`B(c+r)=c` on `W=C directsum R`. This is well defined. Its bilinear form
on W is symmetric because the cross pairings vanish. Extend a basis of
W to a basis of H, with change-of-basis matrix T. The first `dim W`
columns of `S=T^T A T` are prescribed by `T^T B w_j`. Their leading
square block is symmetric. Fill the remaining columns by symmetry and
choose the remaining diagonal block arbitrarily symmetric. Then
`A=T^-T S T^-1` works. No nondegeneracy of C or R is required.

The verifier independently solves the 45-entry symmetric linear system
and checks this criterion at every reported checkpoint. It also tests
all 256 pairs of the 16 subspaces of F2^3, embedded in F2^9.

## An actual incompatible helper

Use the forward program's **zero-based event 13759**, immediately after

    ["climb","B",445,493,451,4]

and before event 13760,

    ["scalar",["add",["L",137],["L",445],1,1],451].

Helper L445's dependence on original source variables is exactly

    +(1/2) x_46 -(1/2) x_20.

The corresponding port labels are `140` and `161`. This describes its
source dependence, not the entire dirty helper value. Its exact suffix
derivatives into final target outputs are `+1` for target port 2, label
`35`, and `-1` for target port 25, label `14`; all other target derivatives
vanish. Therefore

    C=span(140,161),      R=span(14,35),
    140 xor 161 = 14 xor 35 = 45 != 0.

All source/read dot products are zero. The two spaces nevertheless meet
in the line spanned by 45. Equation (2) would require both `A45=45` and
`A45=0`. **No linear A exists**, even without the symmetry condition.

The actual frame 451 has basis

    [256,128,64,33,16,11,7].

It contains C and is orthogonal to R. Its radical, and the radical of C,
both have dimension one. Thus this obstruction is not an artifact of
choosing the original Clifford representative for that frame.

Any repair which keeps (1) must alter this cut's carried/read spaces or
leave the convolution-only frame class. Merely allowing general symmetric
A, instead of an orthogonal projector onto the old U, is insufficient.

## Positive alternative frames

At forward event **15459**, helper L283 has just changed to frame 775 and
is about to be read into L139 with coefficient `-1/2`. Its carried space
has basis

    C=span(81,51,463,237,30,8),       R=span(38).

C has radical dimension two, yet is disjoint from R and orthogonal to it.
The following symmetric matrix, represented by nine binary row masks,
satisfies (2):

    A=[50,23,34,8,35,53,64,128,256].

It is not a projector: its square has row masks
`[1,36,34,8,16,6,64,128,256]`. The receipt gives all sixteen nonzero source
coefficients (each is `+1`) and the single target-read coefficient.

A second control uses event 9466, helper L228, whose original frame 23
has basis `[493,30]` and radical dimension one. Here

    C=span(493),
    R=span(266,30,148,84,45,12),
    A=[460,0,493,493,0,460,493,493,493].

This also satisfies (2). Consequently neither a degenerate canonical
frame nor a degenerate carried space alone proves infeasibility.
These pointwise matrices are **not** a replacement native word: common
gate frames, transition ranks, exact phase choices, endpoint conversion,
restoration, guard precision, and hosting remain unconstructed.

## Why the existing canonical operators cannot share one Walsh basis

The 1004 original subspace labels comprise 234 with zero radical, 726
with radical dimension one, and 44 with radical dimension two.
Of 3486 persistent climbs in the chosen local program, 2982 touch a
degenerate label. For the actual canonical frame of `U=span(30)`, the
source exact checker gives

    T_U X_2 T_U^-1 = X_28 Z_14,

with phase exponent zero. Hence this operator does not commute with all
translations. In particular it is not diagonal in their common Walsh
basis.

This cannot be cured by choosing a different representative with the
same preimage label L_U when U is degenerate. The z-coordinate projection
of a convolution-frame graph is injective, whereas L_U contains `(u,0)`
for every radical vector `u in U intersect Uperp`. A nonzero radical
therefore prevents L_U from being such a graph. The positive examples
above instead allow a **different** preimage label satisfying only (1).

## Replay coverage and limits

The verifier propagates exact Fraction rows forward from all 112 source
inputs, and propagates exact target sensitivities backwards from all 112
final target outputs, through all 19693 scalar events. It verifies the
whole scalar Jacobians: the final source-to-source and source-to-target
blocks are identity, and source material is cleaned out of all helpers;
the suffix map also cancels all arbitrary helper influence on targets.
This prevents a truncated prefix or omitted cleanup from manufacturing
the reported supports.

There are 2886 helper checkpoints: all 480 helper entrances and every
persistent helper climb in the local interior. Their classification is:

| Canonical carry/read conditions | Symmetric A exists | Count |
| --- | --- | ---: |
| Both hold | Yes | 1718 |
| Both hold | No, nonzero intersection | 734 |
| Only carry containment holds | Yes | 168 |
| Only carry containment holds | No | 266 |

The last two rows are not used as canonical-compatible obstructions.
The count is an audit of these fixed checkpoints, not an enumeration of
all scalar cuts or possible frame assignments. The negative witness alone
settles the stated fixed-content replacement attempt. General complex
circuits, changes to the scalar content schedule, auxiliary saved transforms,
mixed convolution/nonconvolution words, and larger geometric candidates
are outside the exclusion.
