# Extension to any number of fresh stages

The D25 closure proof extends to every dimension D=9+8T with T at
least one. It uses the actual general-stage routes. It does not
require an enumeration of all paths.

Let C0,...,CT be invertible constant scalar matrices on the same 112
ports. Put

```text
K = (Gamma_T C_T Gamma_T) ... (Gamma_1 C_1 Gamma_1) C_0,
Gamma_t = diag(P_(rho_(t,p))).
```

The root labels q_p are distinct and remain the same at every stage.
Each rho_(t,p) exchanges the root complement of q_p with fresh block
t, fixes q_p, and fixes all other fresh blocks. This is the exact
route from the general-stage view theorem.

For logical payload width f at least T, K is monomial if and only if
every C_t is monomial. For literal physical affine paths the same
criterion holds at f at least T+1. At f at least T+1, K commutes with
the intrinsic line Q if and only if every C_t is diagonal.

These width bounds are sufficient. No smaller-width optimum is
claimed. The matrices C_t may differ at every stage.

## One input separates every path

Let e_t be the sum of the eight unit vectors in fresh block t.
Let Omega be the sum of the nine root unit vectors. As in D25,

```text
rho_(t,p) e_t = Omega+q_p.
```

Fix output port p and write i_T=p. A path has intermediate ports
i_(T-1),...,i_0 and ordered route

```text
M = (rho_(T,i_T) rho_(T,i_(T-1)))
    ...
    (rho_(1,i_1) rho_(1,i_0)).
```

Apply every path to the same T-column position input

```text
(e_T,e_(T-1),...,e_1).
```

The first image is
`rho_(T,p)(Omega+q_(i_(T-1)))`, because all earlier stages fix e_T.
It gives i_(T-1).

Suppose i_T,...,i_t are known. Remove the corresponding known left
route pairs from M e_t. Then remove rho_(t,i_t). Earlier stages fix
e_t, so the result is `Omega+q_(i_(t-1))`. The distinct root labels
give i_(t-1). Descending induction recovers the complete path.

Thus all intermediate-port paths have distinct outputs on this
one input. Their operators are linearly independent at f=T. Zero
columns extend the test to larger f.

For a physical affine path `x -> Mx+b`, use the single input

```text
(0,e_T,e_(T-1),...,e_1).
```

Its first output gives b. Subtract it from the others to obtain all
linear images. Thus the same separation holds at f=T+1 for arbitrary
literal path translations. Nonzero scalar phases do not affect it.

## Monomial product

For fixed input and output ports, different paths cannot cancel.
Products of nonzero scalar edge coefficients are nonzero. A block
with two paths sends the common basis input to two output coordinates.
If a port row has two blocks with one path each, each output coordinate
has two input coordinates. Either case excludes a monomial operator.

Every row of each C_t is nonzero. One path per output row therefore
forces C_T to have one entry in each row. Invertibility makes it a
monomial matrix and makes its port permutation reach every row of
C_(T-1). Repeat this argument through C0. The converse follows by
composition.

The covariant lift and equal-support argument in `CLOSURE.md` carry
this spatial criterion to the declared full regular owner cover.

## Q commutation

The pulled output line is M^T q_p. If i_(T-1) differs from p, its
stage-T factor gives a nonzero component in fresh block T. All
remaining transpose factors are from earlier stages and preserve
that component. It cannot equal any root input line q_k.

If i_(T-1)=p, the stage-T pair cancels. Apply the same argument at
stage T-1. This gives

```text
M^T q_p = q_k  if and only if
i_(T-1)=...=i_0=k=p.
```

Use `(e_T,...,e_1)` as the first T Fourier-character columns. They
separate all path outputs, because the routes are orthogonal. For a
path that breaks the line, calculate the Q exponent difference on
these tags modulo four. If it is nonzero, append a zero character.
Otherwise, append a unit vector on which M^T q_p and q_k differ.
The resulting exponent difference is nonzero.

This branch has a unique output tuple. No other path can cancel it.
A literal affine translation only supplies the same nonzero sign
on both sides of the commutator. Thus a nonzero line-breaking path
makes `QK-KQ` nonzero at f=T+1.

Every nonzero entry of C_T has a nonzero continuation. Q commutation
therefore forces C_T diagonal. Its diagonal entries are nonzero.
Induction then forces all earlier C_t diagonal. Conversely, diagonal
scalar matrices commute with the portwise routes and with Q.

## Sources and limits

The exact general-stage view theorem is
`bridge-access-20261017/general-stage-views-20261020/GENERAL-VIEWS.md`,
SHA256
`5da866eb2802e8a30ea77d2f88877b5005a2eb04632514c897a426e76277db2e`.
Its freeze is
`b6539737b3144d73c0ca313984573fe1493f9736205ab0d885ebd69d88d27c4d`.
The literal D25 instance and all eight C/C* products are checked in
the companion packet. The arbitrary-T result is the induction above,
not an inference from a finite sample.

This theorem concerns constant scalar codes in their current fresh
charts. It does not include additional old-chart controls, general
operator coefficients, a changed gathered-axis interface, or a paid
decoder. It gives no native cost lower bound and no complete kappa
gain. The complete caller and recursive owner host remain separate.

This work used AI assistance. No PR, commit, push, or publication is
authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
