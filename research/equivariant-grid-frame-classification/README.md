# Exactly which integer frame groups admit bounded equivariant grid rounding

This contribution is produced by Nick Petalas. Apache-2.0.

**Scoped proof with finite corroboration; no new kappa.** Let `d >= 1`,
`m >= 2` be integers and `G <= GL_d(Z)` be any group. There is a function

    q : (1/m) Z^d -> Z^d

with a finite uniform absolute-error bound and `q(gx)=g q(x)` for every
`g in G` and every input x **if and only if G is finite**. The function may
be coupled, nonlinear and discontinuous. The positive direction actually
constructs such a function on all of `R^d`, fixing every integer vector.

[PR1631](https://github.com/CrocSwap/integer-mult-bounds/pull/1631), by
Sricharan Vagvala, proves the particular infinite-order shear obstruction.
The new result classifies the entire integer frame group and supplies a
compatible positive construction. It does not replay that predecessor's
finite-orbit optima or dirty echoes. In particular, checking that each chosen
generator has finite order is insufficient: two involutions can generate
an infinite group and hence admit no common rounder of this kind.

## Necessity: d seed errors bound the entire group

Assume `||q(x)-x||_infinity <= C < infinity`. Let `e_i` be the standard
coordinate vectors and put

    z_i = q(e_i/m) in Z^d,
    E = [m z_1-e_1 | ... | m z_d-e_d] = m Z-I.

The integer matrix E satisfies `E = -I mod m`, so

    det(E) = (-1)^d mod m.

Consequently `det(E) != 0`, even when m is composite. For every `g in G`,
equivariance at these seed orbits gives

    g E_i = m (q(g e_i/m)-g e_i/m).

Every entry of `g E` therefore has absolute value at most `m C`. Since E
is invertible, `g=(g E)E^-1`. In particular,

    max_ij |g_ij| <= m C ||E^-1||_1,

where the matrix 1-norm is the maximum absolute column sum. A bounded set
of integer matrices is finite. More explicitly, with
`M=floor(m C ||E^-1||_1)`, it contains at most `(2M+1)^(d*d)` matrices.
Thus G is finite.

This proof needs only bounded errors on the G-orbits of the d displayed
seeds. It does not assume a nearest-point rule, linearity, continuity,
translation-equivariance or an identity-on-grid condition. The refinement
condition is essential: on the unrefined domain `Z^d`, the identity function
has zero error and commutes with every integer frame group.

## Sufficiency: a stabilizer-compatible construction

Now assume G is finite. Define the G-invariant norm

    ||v||_G = max_(g in G) ||g v||_infinity.

It dominates the infinity norm because G contains I. For each subgroup H,
let `V_H={v: h v=v for all h in H}`. These are rational linear equations,
so rational row reduction and clearing denominators gives integer vectors
`b_(H,1),...,b_(H,k)` that are a real basis of `V_H`. They need not be a
basis of the whole fixed integer lattice. Set

    R_H = (1/2) sum_i ||b_(H,i)||_G,
    R = max_(H <= G) R_H.

There are finitely many subgroups, so R is finite. Every `y in V_H` is
within G-norm `R_H` of an H-fixed integer vector: expand y in this basis
and round each real coefficient to an integer. The triangle inequality
proves the stated bound. An empty basis has `V_H={0}` and `R_H=0`.

For arbitrary `x in R^d`, define q by the following finite procedure.

1. Choose the lexicographically smallest orbit point `y=min_(g in G) gx`.
   Take any t with `t x=y` and let `H={h in G: h y=y}`.
2. Among integer z fixed by H, minimize `||z-y||_G`; break remaining ties
   lexicographically. A minimizer exists within radius `R_H`. There are
   finitely many candidates there because the G-norm dominates the infinity
   norm. It suffices to enumerate the integer box
   `ceil(y_j-R_H) <= z_j <= floor(y_j+R_H)` and filter by fixedness and radius.
3. Return `q(x)=t^-1 z`.

This is independent of the choice of t. If `t' x=y`, then `t' t^-1 in H`
fixes z, so `t'^-1 z=t^-1 z`. To prove equivariance, for any `a in G`,
the same canonical y and stabilizer H apply to ax, and `t a^-1` is a valid
transport. Hence `q(ax)=a t^-1 z=a q(x)`.

Finally, integrality of `t^-1` gives `q(x) in Z^d`, and norm invariance gives

    ||q(x)-x||_infinity <= ||t^-1(z-y)||_G = ||z-y||_G <= R_H <= R.

If x is integral, y itself is an H-fixed integer candidate of zero error;
the chosen z equals y, so `q(x)=x`. Restricting this construction to any
refined grid proves the positive direction of the theorem.

This is a mathematical finite algorithm using exact comparisons and floor
operations. Its physical bit/tape cost, real-input representation and optimal
error radius are not established.

## Why the compatibility conditions matter

At `x=(1/2,-1/2)`, the frame `A=[[0,-1],[-1,0]]` fixes x. In the ordinary
infinity norm, the lexicographically first unrestricted nearest integer
point is `z=(0,-1)`. It is not fixed by A. Transporting it with either I
or A therefore gives different answers for the very same input. Restricting
to stabilizer-fixed integer points removes this ambiguity.

Nor can one merely check generator orders. The integer reflections

    r = [[1,1],[0,-1]],   s = [[1,0],[0,-1]]

have `r^2=s^2=I`, but `rs=[[1,-1],[0,1]]` has infinite order. The necessity
theorem excludes a single bounded rounder commuting with both r and s.

The construction does not promise translation-equivariance. Adding
`q(x+n)=q(x)+n` changes the problem even for the finite group `{I,-I}` in
dimension one: at `x=1/2`, translation and sign equivariance together would
give `q(1/2)-1=q(-1/2)=-q(1/2)`, impossible for an integer output. The
classification concerns precisely the hypotheses in the opening statement.

## Evidence and reproduction

The written argument is dimension-uniform. [verify.py](verify.py) supplies
finite corroboration using only exact integers and rational numbers. It
implements the positive construction for five explicit finite groups,
including a nonorthogonal conjugate of the order-eight dihedral group and
the three-dimensional permutation group. Every group is checked for closure,
identity, inverses and integral determinant of absolute value one.

For each group it checks all numerator tuples in `{-2,-1,0,1,2}^d`, each
with denominator 1, 2, 3 and 4, and every group translate of each point.
It checks integer output, the written radius, identity on integer inputs,
transport independence and exact equivariance. The seed-matrix census checks
`m Z-I` for all two-dimensional Z with entries -2..2 and m=2..8, and all
three-dimensional Z with entries -1..1 and m=2..4. These are finite tests
of the proof's mechanisms, not a finite proof of the universal theorem.

Controls distinguish the stabilizer tie, coordinatewise nearest-even failure
under a finite reflection, the unrefined-grid exception, shear error growth
and two finite-order generators whose product has infinite order. No
predecessor verifier or receipt is imported.

From the repository root:

```sh
PY=/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12
"$PY" -W error -B research/equivariant-grid-frame-classification/verify.py
"$PY" -W error -I -O -B research/equivariant-grid-frame-classification/verify.py
"$PY" -B scripts/research_package.py --package research/equivariant-grid-frame-classification
"$PY" -B scripts/check_research_commit.py --package research/equivariant-grid-frame-classification --check-source-history
```

Expected markers are `PASS_EQUIVARIANT_GRID_FRAME_CLASSIFICATION no_new_kappa`
and `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`. An equivalent
CPython 3.12 interpreter suffices. Default replay writes no package files.
Optional `--receipt /absolute/external/path.json` exclusively creates a
computed receipt with SHA256 hashes of every package file.

[SOURCES.json](SOURCES.json) pins the unchanged predecessor prose, selected
record and original catalogue. The original `uniform-transfer-audit` card
asks about an actual #4100 caller. [TASK.json](TASK.json) explicitly changes
scope to this carried-frame side theorem; no #4100 obligation is discharged.
[VALIDATION.md](VALIDATION.md) records the executed checks and their limits.

## Limitations

The input domain is the whole refined grid, or at least the specified seed
orbits for necessity. An actual reader can avoid the obstruction by having a
smaller reachable domain. Stateful or frame-dependent rounding, nonuniform
error bounds, noninteger frames and changing output grids are outside the
theorem. The positive construction supplies no optimal radius or efficient
physical implementation. No actual supplier child, rounded dirty echo,
storage recurrence, analytic transfer, selected cold replay, formal proof
kernel or complete multiplication theorem is supplied. The selected frontier
is unchanged.

## Open next questions

1. What is the least possible uniform error radius for one nonorthogonal
   finite frame group? The construction proves finiteness but need not be
   optimal. Start with the displayed order-two reflection and classify its
   stabilizer-fixed nearest lattice points. No such optimization is claimed.
2. Which actual carried reader has reachable outputs containing the d seed
   orbits used here? This determines whether the obstruction applies at a
   physical caller. Start with one concrete reader and its dirty-input image;
   source-bound reachability and arithmetic prices remain missing.

## Credit

Sricharan Vagvala / PR1631 supplies the shear obstruction and its explicit
rounding-interface scope. Woklerx's [PR1892](https://github.com/CrocSwap/integer-mult-bounds/pull/1892)
and `shear-orbit-interval-audit` supply the
separate rational-window oracle and emphasize that per-orbit choices need
not assemble into one rounder. Sagar Thakrar / PR1537 supplies the exact
carried-reader construction; Ross Richardson / PR1287 and the retained
PR1227/889/1203 lineage supply output-frame and dirty-echo context. Their
exact arithmetic constructions are not alleged to be defective. The new
contribution is the finite-group equivalence, its d-seed argument and the
stabilizer-compatible positive construction. Independent human and formal
proof-kernel review are unclaimed.
