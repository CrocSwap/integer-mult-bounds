# Independent review of the controller residual theorem

The finite algebra in `../PROOF.md` passes this review. No error was found in
the factorization, kernel description, kernel form, or residual rank formula.
The source bytes at review time are recorded in `REVIEW-STATUS.json`.

The review does not prove the native global normal form or the bound from the
routed-projection theorem. These are separate dependencies. In particular,
the scalar interface receipt alone does not establish the native global
normal form. The final note must state that distinction.

## Algebra checked

For a forward local step, the removed term adds `-R_s^* R_s/4` to the Y
update. For a backward step, it adds `R_s^* R_s/4` to the X update. The old
step commutes with this error shear. Each old prefix P is symplectic, so
`P^-1 Omega = Omega P^*`. Conjugation by that prefix therefore gives the
same factor `I + Omega V_s^* V_s/4` for both orientations. The order is
`B_8 ... B_0`. No two routed matrices must commute.

The stacked triangular recurrence gives the stated inverse `4I-L`, with a
minus sign. Its inverse exists without an assumption on the ranks of the
routed matrices. The kernel argument then uses the separate assumption
`R_s R_s^*=56I`.

The nine bank source rows have a unique relation c. Direct reconstruction
from the source recipe gives

    c = (1,-1,-1,1,1,-1,-1,1,1).

Every maximal proper minor is 1 or -1. Thus every proper subset is
independent. The relation of the bank rows implies that any vector in
`ker(V^*)` has `R_s^* z_s = c_s w` for one common vector w. Injectivity of
each `R_s^*` gives `z_s = c_s R_s w/56`. This proves the claimed bijection
with the common routed centre image.

The direct bank calculation gives area 4. Under the above identification,
the identity contribution is `9/14` and the lower triangular contribution
is 4. The compressed form is therefore `-47/14` times the inner product
on the common image. This is not the scalar of the compression in an
orthonormal basis of `ker(V^*)`; the note correctly specifies the common
image inner product. Its nonsingularity suffices.

To finish the rank proof, let `n=(4I-L)^-1 u` lie in `ker(V^*)`, with
`u in im(V)`. Then `(4I-L)n` is orthogonal to `ker(V^*)`. The nonsingular
compressed form forces n to be zero. This proves that the decoder loses no
further rank. For a proper stage subset, `V^*` is injective, so no kernel
compression argument is needed.

## Separate exact execution

`independent_residual.py` does not import `verify_residual.py`. It builds
elementary matrices from the pinned archive recipe and uses exact SymPy
matrix products. It checks the following facts:

* Every source step is symplectic and the old terminal endpoint is the
  identity.
* The nine source rows, their unique relation, all nine maximal proper
  minors, area 4, and the form `-47/14` agree with the proof.
* The 16 replicas have disjoint data namespaces, each with 896 families.
* Three exact models with two centre directions have common-image
  dimensions 0, 1, and 2. Their residual ranks are 18, 17, and 16.
* In another model, all nine maximal proper stage subsets have residual
  rank 16. The full matrix products agree with the triangular formula.
* An incorrect triangular sign fails in every exact model.

The models include noncommuting centre projections. They test the general
algebra; they do not enumerate the full orthogonal cover group. The proof,
not these small examples, establishes the result for the actual full cover.

The source checker was also rerun with Python isolation and optimization.
It passed, and its new receipt equals the supplied `RESIDUAL.json`.

## Whole arrays and limits

Given the separate bound `d <= 8|G|/183`, the rank is at least
`13168|G|/183 > 71|G|`. Across 16 independent replicas it is at least
`210688|G|/183 > 1151|G|`. The ceilings are therefore 72 and 1152 complete
cover arrays. The full 72-array syndrome per replica gives the matching
information capacity. A joint encoder across the 16 replicas does not
change the second ceiling.

This counts the dimension of a declared residual channel. It does not
count peak workspace, native child rank, or temporal reads. Borrowed state
does not evade a stated linear channel factorization if it is restored.
A circuit that later reads the original data has additional channels and
is outside that argument. The proof states these exclusions correctly.

Two wording changes are requested before publication:

1. Name the local native lift, the global endpoint normal form, and the
   routed-projection bound as separate dependencies.
2. Replace `nine independent centre cohorts` with `nine separate centre
   cohorts`. The theorem permits the dependence measured by d.

No code or proof file under review was changed. No native corrector,
supplier admission, full recursive price, or kappa improvement was checked.

## Commands

From the workspace root:

```sh
work/autonomous-kappa-run/venv/bin/python -I -O -B work/centre-encoding-campaign-20261014/lanes/residual-syndrome/review/independent_residual.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/residual-syndrome/verify_residual.py --repo worktrees/k5-centre-sharing --interface work/centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json --out work/centre-encoding-campaign-20261014/lanes/residual-syndrome/review/REPRODUCED-RESIDUAL.json
```

Expected status lines:

```text
PASS_INDEPENDENT_RESIDUAL_ALGEBRA_REVIEW
PASS_SELECTED_CONTROLLER_RESIDUAL_FACTORIZATION
```

This review and its code used AI assistance.
