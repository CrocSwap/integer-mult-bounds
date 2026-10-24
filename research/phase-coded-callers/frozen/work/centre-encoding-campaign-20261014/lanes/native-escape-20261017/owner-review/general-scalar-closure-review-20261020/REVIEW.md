# Proof review of closure through T fresh stages

The general-stage extension is correct under its stated hypotheses.
No material finding remains. It is an induction on the exact route
formula, not an inference from the D25 tests.

For D=9+8T, T at least 1, and invertible constant scalar matrices
C0,...,CT on the actual 112 ports:

- Logical monomial closure holds if and only if every C_t is
  monomial, at every payload width f at least T.
- The physical affine version has the same criterion at every
  f at least T+1.
- At every f at least T+1, Q commutes with the product if and
  only if every C_t is diagonal.

These are sufficient width bounds. They do not assert that the
bounds are optimal.

## Ordered recovery of the path

Fix the output port i_T=p. Put

```text
B_t = rho_(t,i_t) rho_(t,i_(t-1)),
M = B_T ... B_1,
L_(>t) = B_T ... B_(t+1).
```

Suppose i_T,...,i_t have been recovered. The prefix L_(>t) is
then known. Every earlier stage fixes the fresh vector e_t.
The exact identity is

```text
rho_(t,i_t) L_(>t)^-1 M e_t = Omega+q_(i_(t-1)).
```

The operator order in this equation matters. It first removes
the known left prefix, then removes the known stage-t factor.
There is no commutation of different routes. Distinct root
labels recover i_(t-1). Descending induction therefore recovers
all T intermediate ports from the single common input
`(e_T,...,e_1)`.

Its output tuples are distinct, so a linear combination of the
path operators cannot vanish on that input unless all coefficients
vanish. For an affine path, the additional leading zero column
records its translation. Subtraction then gives the same linear
images. This proves the stated logical and physical width bounds,
including the T=1 case.

Products of nonzero Gaussian scalar coefficients are nonzero.
For each input/output block, the common input therefore rules
out cancellation among paths. Two paths in one block violate
the coordinate-column condition for a monomial operator. Two
single-path blocks in one port row violate its coordinate-row
condition. The nonzero-row and invertibility argument then
forces C_T, C_(T-1),...,C0 to be monomial in that order.
The converse follows by composition.

## Pulled lines and the phase witness

Starting at the final stage, cancel every pair whose intermediate
port equals p. At the first mismatch, say stage t, the pulled
line acquires a nonzero component in fresh block t. Every
remaining transpose factor belongs to an earlier stage and
fixes that block. It cannot remove this component. Thus

```text
M^T q_p = q_k
```

holds exactly when every intermediate port and k equal p.

The T fresh-vector character columns separate all path outputs,
since each route is orthogonal. If one nonzero path breaks the
line, append zero when its phase difference on those tags is
already nonzero modulo 4. Otherwise append a unit character
that distinguishes M^T q_p from q_k. The appended difference
is 1 or -1. The selected branch has a unique output tuple and
a nonzero commutator coefficient. Affine translations multiply
both sides by the same nonzero sign.

Consequently Q commutation permits only line-preserving nonzero
paths. Every nonzero last-stage entry has a nonzero continuation.
It must therefore be diagonal. Its diagonal entries are nonzero,
so the argument applies successively to every earlier matrix.
Diagonal scalar matrices commute with each port's routes and Q,
which proves the converse.

## Cover and scope

The covariant lift and equal-fiber-support argument from the
frozen D25 binding apply without change to O(D,2). Their proof
uses only the finite complete cover and the stated owner action.
It does not use the value D=25. Thus the spatial failure also
excludes a monomial full-cover product in this scalar-code class.

This review binds the general-stage view theorem and its freeze,
the corrected D25 closure proof, and the general closure proof.
Their exact paths and hashes are in `SOURCE-MANIFEST.json`.
The companion binding freeze is
`7e572942617d880931f52f47849b23174b903f57a199a99134b96ed5cac21ea6`.

This is a proof-only review. No additional path enumeration,
native replay, recursive host, map-price calculation, or precision
test was run. The theorem does not cover operator-valued
coefficients, extra old-chart controls, or a changed access
interface. It gives no general native lower bound or kappa gain.

No frozen source is changed. Before any future PR description,
read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
No PR, commit, push, or publication is authorized.
