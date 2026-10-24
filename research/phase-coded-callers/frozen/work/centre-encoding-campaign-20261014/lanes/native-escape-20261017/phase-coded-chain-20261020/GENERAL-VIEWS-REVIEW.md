# Peer review of the general stage views

The proof in
`bridge-access-20261017/general-stage-views-20261020/GENERAL-VIEWS.md`
has no material error for the adjacent-stage and access-cone
identities used by the phase-coded caller.

The reviewed proof SHA256 is
`5da866eb2802e8a30ea77d2f88877b5005a2eb04632514c897a426e76277db2e`.
Its source freeze SHA256 is
`b6539737b3144d73c0ca313984573fe1493f9736205ab0d885ebd69d88d27c4d`.
This review checks the mathematical proof. It does not rerun the
producer's arbitrary-dimension generator.

Let B be the actual root orthonormal basis. The function

```text
f(z) = sum_(v in B) (v dot z) - |z|  mod 4
```

has no quadratic term: its coefficient at a pair of distinct
standard coordinates is minus two times their scalar product
under the orthogonal basis matrix. Every linear coefficient is
even. Thus f is twice a binary linear form.

For a basis vector v, orthonormality gives
`f(v)=1-|v|=2 beta(v) mod 4`. It follows that this form is
`delta0=sum_(v in B) beta(v) v`. The actual q has weight three
or seven, so its coefficient is one. This proves the source
formula `delta0=q+sum_j beta(b_j)b_j`, including the phase sign.

The route exchanges each b_j with its fresh unit vector e_j.
The eight vectors b_j+e_j are isotropic and pairwise orthogonal.
The displayed matrix for rho therefore acts as the claimed
exchange, fixes q, and is an orthogonal involution.

Conjugating the root phase identity by rho gives

```text
P_rho Froot = X_(rho delta0) Q Ffresh P_rho.
```

The entry translation cancels this phase. The old completed
fresh blocks are spectators. This gives the first adjacent
identity; multiplication by q gives the ordinary-hole identity
because rho fixes q.

When both the root and the current fresh block are FULL, their
exchange has phase `X_(delta0+rho delta0)`. The source exit
translation is exactly that phase. It is fixed by rho, so the
affine exit map is an involution. Old or future spectator blocks
do not change the calculation. This proves the claimed access
cones for every finite number of fresh blocks.

The owner map is right multiplication by a fixed orthogonal
element on the regular cover. It is a bijection. This permits
the complete-cover view used in the proof; it does not identify
different stages without their owner and payload maps.

The separate `check_chain.py` in this folder binds the literal
selected D73 archive and verifies all eight natural boundaries
and all nine FULL shears used by the repeated phase-coded caller.
Its phase primitive is inherited from the earlier pinned bridge
checker. The reviewed D25 caller uses a separate phase-ring
implementation. These are source and finite-consistency checks;
the arbitrary-dimension conclusion follows from the proof above.

The general theorem supports the repeated-triple type lemma
whenever the same local words are available. It does not make
the matrices G_s C G_s independent of s. It does not close a
recursive gathered-axis interface or supply a global helper
host, map-stream invoice, or precision proof.

No PR, commit, push, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
