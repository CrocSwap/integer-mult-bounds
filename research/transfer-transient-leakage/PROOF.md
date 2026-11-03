# Uniform error from one transient virtual block

This is a scoped written proof. The finite executable corroborates the stated
identities; it does not supply their unbounded quantifiers.

## Complete physical endpoint

Use zxv's PR5441 fixed-transfer contract over the complex field. There are
`d` physical input and output letters, a fixed virtual space `V=U direct-sum W`,
and a fixed transfer matrix for each physical pair:

```text
T[y,x] = [ A[y,x]  C[y,x] ]
         [    0     D[y,x] ].
F = [L 0],       B = [0; R].

E_f[i,y_1...y_f ; j,x_1...x_f]
    = (F T[y_1,x_1] ... T[y_f,x_f] B)[i,j].
```

`L:U->C^p` and `R:C^q->W` include every output and input role required by
the endpoint. If this is an error certificate, `E_f` must represent the
complete implementation-minus-target operator, including required dirty
returns. The theorem does not license removal of a return block. The virtual
states are representation coordinates, not free physical workspace.

All matrices, the splitting, and both boundaries are fixed across widths.
The lower-left zero is an exact hypothesis. Width-dependent tables require
their own explicitly represented controller.

Let `P_U,P_W` be positive-definite Hermitian matrices. Give the virtual spaces
their induced Hilbert norms and physical spaces their ordinary Euclidean norms.
Put `P_dU=I_d tensor P_U` and `P_dW=I_d tensor P_W`.
Use physical-major ordering to assemble the full local operators
`Ahat=[A[y,x]]`, `Chat=[C[y,x]]`, `Dhat=[D[y,x]]`.
These are coherent operators on a physical column and its virtual state.

## Theorem

Suppose `alpha,beta,delta>=0`, `0<=rho<1`, and

```text
Ahat* P_dU Ahat <= P_dU,
Dhat* P_dW Dhat <= rho^2 P_dW,
Chat* P_dU Chat <= delta^2 P_dW,
L* L <= alpha P_U,
R* P_W R <= beta I_q.
```

Then, at every positive integer width,

```text
||E_f||_op <= sqrt(alpha beta) delta (1-rho^f)/(1-rho)
           <= sqrt(alpha beta) delta/(1-rho).
```

The norm is on the full `p*d^f` by `q*d^f` operator. There is no physical
dimension factor. The inequalities include every off-diagonal physical-input
block. Bounds on individual columns or individual `T[y,x]` do not suffice.

### Proof

Lift each local block to its column in the full physical tensor product,
tensoring identities on the other columns. Its weighted operator norm is
unchanged. Apply the right boundary first, then columns `f,f-1,...,1`,
then the left boundary. The coefficient product is exactly the displayed
`T[y_1,x_1]...T[y_f,x_f]`, as in PR5451's physical contraction proof.

Because the lower-left block is zero, every path from `W` at the right
boundary to `U` at the left boundary crosses `C` exactly once. The complete
upper-right block of the product is

```text
sum_(k=1)^f A_1 ... A_(k-1) C_k D_(k+1) ... D_f.
```

The subscripts identify lifted columns; no commutation of virtual matrices
is assumed. Each summand has weighted norm at most `delta rho^(f-k)`.
The triangle inequality and geometric sum bound the complete upper-right
block by `delta(1-rho^f)/(1-rho)`. The two boundary inequalities multiply
this by `sqrt(alpha beta)`. This proves both assertions. For `rho=0`,
the sum consists only of its final nonzero term, with empty products
interpreted as identities. For `delta=0`, the endpoint is zero. QED.

This is a different sufficient certificate from requiring a contraction
metric for the entire local `T` operator. It does not supersede that test
on arbitrary endpoints or characterize every uniformly bounded family.

## A sharp family outside the whole-table metric test

Let `d=2`, `dim U=dim W=p=q=1`, `delta>0`, and `0<=rho<1`. Take

```text
T[0,0] = T_plus  = [1  delta],
                         [0    rho],
T[1,1] = T_minus = [1 -delta],
                         [0    rho],
T[0,1] = T[1,0] = 0,
F=(1,0),       B=(0,1)^T.
```

The scalar block metrics are both one, and `alpha=beta=1`. The full local
blocks are `Ahat=I_2`, `Dhat=rho I_2`, `Chat=delta diag(1,-1)`, so every
theorem inequality holds with equality.

`E_f` is diagonal in the physical bit basis. On the word `x_1...x_f` its
diagonal entry is

```text
delta sum_(k=1)^f (-1)^(x_k) rho^(f-k).
```

The absolute value is at most the geometric sum, and the all-zero input
attains it. Consequently

```text
||E_f||_op = delta (1-rho^f)/(1-rho).
sup_(f>=1) ||E_f||_op = delta/(1-rho).
```

Thus the theorem's width bound and uniform constant are sharp. For
`rho=1/2, delta=1/1024`, the error is strictly below `1/512` at every finite
positive width, with supremum exactly `1/512`.

### No common positive contraction metric in this representation

Suppose a positive-definite Hermitian `G=[[a,z],[conjugate(z),b]]` and
`0<=c<=1` satisfy the full local PR5451 inequality. Since the physical
table is diagonal, this requires both `T_plus* G T_plus<=cG` and
`T_minus* G T_minus<=cG`.

Both matrices fix `e_1`. Evaluation on that vector gives `a<=ca`, and
`a>0` forces `c=1`. The two positive-semidefinite matrices
`K_plus=G-T_plus*G T_plus` and `K_minus=G-T_minus*G T_minus` have zero
top-left entry. A zero diagonal entry of a positive-semidefinite Hermitian
matrix forces its row and column to vanish. One can see this from its
two-by-two principal minors, which would otherwise be negative.

Their upper-right entries must therefore both vanish:

```text
(1-rho) z - a delta = 0,
(1-rho) z + a delta = 0.
```

Subtracting yields `2 a delta=0`, contradicting positivity. No such metric
exists, including a metric with complex off-diagonal entries. QED.

This impossibility concerns the exact two-state representation above and
the full-table contraction test with `c<=1`. It does not exclude another
representation, a different sufficient certificate, or the bounded endpoint
itself. In particular, it is no criticism of PR5451's correctly stated
sufficient test and no re-audit of that work.

## What remains open

No actual selected native word or physical caller is bound to this triangular
contract. Exact source/version extraction, physical realization and return,
coefficient access, movement, storage, precision, stock, recursive compilation
and a separately justified recovery tolerance remain obligations. The result
does not improve kappa or discharge a selected framework assumption.

The block-product expansion, Hilbert norms and geometric-series estimates
are classical. The contribution is this sufficient physical endpoint
certificate, its sharp two-state separation from the whole-table metric
test, and its exact executable corroboration. No global literature-priority
claim is made. Credit zxv/PR5441 for the interface and approximation question,
and Ali Romman/PR5451 for the coherent local-metric certificate and retained
physical contraction argument. Their automata, matrix-product, native,
phase and compiler lineage retains its credit.

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.
