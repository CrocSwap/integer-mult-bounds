# Controller consequences of the centre-free interface

This note uses base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` and the
centre-free scalar interface in the adjacent circuit-interface lane. It does
not admit a new supplier. It gives a proof for a restricted controller class
and prices a repeated-chart realization of the seven-shear identity.

## 1. The native endpoint that the controller must meet

Let `Q` be the diagonal operator whose port `p`, cover class `d` component is
the native line operator `C_(d q_p)` to tensor power lambda. Let `F_s` be the
full native operator on the first `9+8s` axes, transported by `d`. The exact
stage phase corrections in the pinned `DATA-PHASES.json` give these boundary
frames:

* At entry: `(Q,I)` on the X and Y banks.
* After stage s: `(F_s,F_s Q^-1)` on the active X and Y banks.
* After all idle work: `(F_8,F_8 Q^-1)` on every data pair.

Write `D_s` for the port-dependent cover router from the actual controller.
For s greater than zero, its port component is the involution `rho_s(q_p)`.
This involution fixes `q_p`, exchanges its eight-dimensional orthogonal
complement in the first nine axes with the new external block `E_s`, and
fixes all other external blocks. `D_0=I`.

The abstract local shear therefore uses

    K_s = D_s^-1 J D_s,       J = I - R^T R/4.

This is a statement about the scalar content in the actual moving frames.
It does not replace all the `K_s` by one matrix J.

Let C be the product of the abstract local shears and intermediate bridges,
before the terminal operation. In the physical coordinates its endpoint is

    diag(F_8,F_8 Q^-1) C diag(Q^-1,I).

The prescribed terminal operation first translates Y by `Q^2`, then uses
`W=[[0,I],[-I,0]]`. Since every line operator commutes with `F_8`, the final
physical map, before the fixed full-cover phase correction, is

    F_8 diag(Q,I) W C diag(Q^-1,I).

Thus the required full native transform on every original data family is
equivalent to `C=W^-1`. A free terminal bank exchange alone does not meet this
equation. Its input frames differ, and the factors Q remain in the equation.

## 2. A single-pass obstruction for the retained bridge class

The following hypotheses define the claim.

1. Each stage is used at most once on each path through the controller.
2. Every intermediate bridge preserves each port and cover class and maps
   X banks to X banks and Y banks to Y banks. Its coefficients and its mixing
   among banks on the same side can be arbitrary.
3. The entry frames, final frames, and terminal operation are those in
   Section 1. There is only one stage-zero local call on a path.

The actual nine-stage recipe has these properties. The claim permits changes
to its scalar coefficients and same-side bank bridges. It does not cover
arbitrary physical bank exchanges, port changes, or completed-frame routers.

**Theorem.** Under these hypotheses, no controller made only from the
centre-free local shears can perform the required native transform.

**Proof.** Each column of R has squared norm four. Hence every diagonal entry
of J is zero. Each nonzero entry `J[q,p]` changes the port. Its two ports are
orthogonal in the binary native geometry.

For s greater than zero, let `B_p:F_2^8 -> q_p^perp` be the orthogonal basis
map used by `rho_s(q_p)`. A nonzero entry in `K_s` has cover permutation

    g_s(q,p) = rho_s(q) rho_s(p),       q != p.

This permutation does not fix `E_s` pointwise. If it did, multiplication by
`rho_s(q)` would give `B_p v=B_q v` for all v. The two orthogonal complements
would be equal. Their perpendicular lines, and thus their nonzero binary
vectors p and q, would be equal. This is a contradiction.

Expand a controller matrix entry as a sum over paths. If a path uses a
nonidentity term from stage s greater than zero, all other factors on that
path fix `E_s` pointwise: other stages act on other external blocks, and the
allowed bridges do not change the cover. The pointwise stabilizer of `E_s`
is a group. A product with exactly one factor outside that group cannot be
the identity. Thus this path cannot contribute to the identity cover
permutation.

A path with no positive-stage local term can use only the stage-zero local
term. A single such term changes its port, since J has zero diagonal. A path
with no local term remains on the same X/Y side. It follows that every
same-port, same-cover coefficient from X to Y, or from Y to X, is zero.
`W^-1` has nonzero coefficients there. Therefore `C != W^-1`.

For a physical witness, place a nonzero native vector in one X bank at one
port and cover class, and set the other data to zero. The same X bank, port,
and cover class receives zero after the fixed terminal exchange. The required
full native transform has a nonzero value there because it is invertible.
The diagonal native phase factors do not change the port or cover class.
This proves failure of the full normalized endpoint, not only of a chosen
scalar coefficient. QED.

The finite verifier checks all 12,544 port pairs, all 5,824 nonzero J entries,
the external-block premise, and the actual controller recipe. The group
argument proves the statement for all paths and all tensor powers. Finite
enumeration of the full orthogonal group is not used.

## 3. What a repeated chart makes possible

The previous theorem has a real escape. If a stage is repeated, a port path
`p -> q -> p` can have cover permutation

    rho_s(p) rho_s(q) rho_s(q) rho_s(p) = I.

In fact `J^2+12J-13I=0`. The root lane found a seven-shear word that equals W
at both eigenvalues of J, and the bounds-review lane checked it independently
in an exact cubic quotient ring. The scalar identity can be placed in a
single native chart without treating frame transitions as free.

In that chart let F be the full nine-dimensional native operator, and put

    A=diag(I,Q^-1),    B=diag(Q^-1,I),    M(t)=F A U(tJ) B.

The upper-shear variant `U(tJ)` is obtained from the backward orientation by
scalar conjugation. For this algebraic statement, grant exact arithmetic in
the coefficient field. The current dyadic compiler does not yet implement
those fixed algebraic coefficients.

The native bridge

    V=B^-1 W A^-1=diag(Q^2,I) W

is a signed bank exchange and a port-dependent translation. It has rank zero.
All C line operators commute with F. Thus inserting V between seven calls
gives

    M_7 V M_6 V ... V M_1
      = F^7 A (S_7 W S_6 W ... W S_1) B.

If the verified alternating seven-shear coefficients are
`(a,b,c,d,c,b,a)`, choose all seven S factors to be upper shears, with
coefficients `(a,-b,c,-d,c,-b,a)`. The parenthesized product is `-W`.
Since `F^2` and `Q^2` are translations, one final rank-zero bridge converts
the result into F on both data banks. This is an exact native block identity
for every tensor power, conditional on the local scaled shear interface.
It gives one full nine-dimensional transform, rather than seven fresh
eight-dimensional advances.

## 4. The fixed-chart bill

The pinned provider has local rank mass

    5586 = 1792 data + 3730 helper + 64 centre.

The centre-free provider has rank mass 5522. Seven calls therefore cost
38,654 rank units. They perform a full rank-nine transform on 224 data
families, for data mass 2,016. Even if every helper residual is usefully
hosted, their useful helper mass is at most `7*3730=26110`. The total useful
mass is at most 28,126. The excess is 10,528 rank units.

This count grants coefficient arithmetic, all bridges, and perfect helper
hosting for free. It already rules out a positive rank deficit for this
fixed-chart realization. Additional scalar, precision, storage, or routing
charges cannot fix it. This is not a lower bound for all controllers that
repeat stages.

## 5. Next construction questions

The retained bridge class is smaller than the legal physical router class.
At boundary s, a router that preserves `U_s` is legal on X. A sufficient
condition on a Y router is that it also transports the new port line to the
old one. This condition is not necessary. The actual Y frame is
`H_s(q)=U_s intersect q-perp`. A Y-only router can preserve this hyperplane
while mixing its missing line with unused future directions. The old
controller names that missing line, but this label does not itself prove
that a new controller must preserve it. Such routers invalidate the
pointwise-stabilizer proof above. The cover-algebra lane is checking their
exact phases and their use in a construction.

There is also a legal full-boundary correction. Normalize every final Y bank
by Q, apply the inverse abstract controller at the common full frame, and
normalize every X bank by Q. Orthogonal cover routing at that full frame has
only the known phase correction. This costs one rank-one line transform per
data family: 896 units per replica, versus 576 removed centre units. It loses
the old 320-unit deficit. A lower-dimensional syndrome correction could be
better; the residual-syndrome lane is checking that question.

No claim here excludes those two construction routes.

## Reproduction

From the workspace root, run:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/encoded-controller/verify_controller.py \
  --repo worktrees/k5-centre-sharing \
  --interface work/centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json \
  --out work/centre-encoding-campaign-20261014/lanes/encoded-controller/CONTROLLER-CHECKS.json
```

Expected status: `PASS_SINGLE_PASS_CHART_PREMISES_AND_FIXED_CHART_BILL`.
No full supplier replay, algebraic-coefficient compilation, or exponent
calculation is claimed. Prepared with substantial OpenAI Codex assistance.
