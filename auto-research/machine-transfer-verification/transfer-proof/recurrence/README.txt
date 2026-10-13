Exact floor recurrence, executable depth, and row-stock closure
=============================================================

This bundle proves the integer-width transfer used in notes/batched-bit-rows.tex.
Every child is literally t*(e/m), with natural-number division. No monotonicity
of the cost function and no ceiling-envelope recurrence are assumed.

FloorDepth.lean
--------------

The executable well-founded definition is

  D(e) = 0                           if e < m,
  D(e) = 1 + D(tmax * (e / m))        otherwise,

under tmax < m. A proved strict width decrease justifies termination.
The depth is nondecreasing in e. Every child with t <= tmax satisfies

  D(t*(e/m)) + 1 <= D(e)             for e >= m.

Consequently, W^D(e) dividing R implies both

  W*(R/W) = R,
  W^D(t*(e/m)) divides R/W          when W > 0.

These are exact integer equalities/divisibilities, so internal row splitting
needs no row-count padding. They do not claim that a physical tape program
implements the split or the child invocation.

FloorRecurrence.lean
-------------------

For a finite list, coefficients c_i >= 0, integers 1 <= t_i < m, and p >= 0,
let gamma = sum c_i*(t_i/m)^p < 1. Assume the named physical cost contract

  F(e) <= C + sum c_i * F(t_i*(e/m))       for every e >= m.

The theorem proves F(e) <= A*e^p for every positive integer e, with the explicit
finite constant

  A = sum_{0 <= n < m} |F(n)| + |C|/(1-gamma).

The extra F(0) term is harmless; no recurrence or base inequality is required
at zero. All actual induction base cases are exactly 1 <= e < m. The proof
uses the floor inequality only on the power potential, never on F itself.
There is no assumed finite-base growth estimate: A absorbs the finitely many
real-valued base costs directly. Nonnegative C is not needed.

Also proved, for 0 < tmax < m and every positive e,

  D(e) <= 1 + log(e)/log(m/tmax).

This is an explicit real logarithmic bound on the executable depth.

SelectedFloorTransfer.lean
--------------------------

The specialization imports the independently formalized actual real moment
bound in outputs/next-proof/analytic. Its literal parameters are m=575,
W=137151806, tmax=529 and

  a = 63787735011827529 / 1250000000000000000000,  p=1-a.

It uses every one of the selected profile's 27 width/multiplicity rows, with
c_t=n_t/W, and proves their upper width bound by ordinary kernel computation.
The main theorem SelectedFloorTransfer.all_width_cost_bound has exactly one
cost hypothesis: the explicit physical_recurrence above. The characteristic
inequality is imported as a proved theorem, not an assumption. The theorem
SelectedFloorTransfer.child_row_stock specializes exact stock closure.

PhysicalCostTransfer.lean
-------------------------

The state-indexed theorem removes the need to justify a normalized worst-case
cost function. A state type S can contain arbitrary volumes, spectators and
machine metadata. Each actual child is indexed by a row r and j:Fin(n_r).
The explicit physical contracts are:

  volume(s) >= 0,
  width(child(s,r,j)) = t_r*(width(s)/m),
  volume(child(s,r,j)) = volume(s)/W,
  cost(s) <= B*volume(s)                    for 1 <= width(s) < m,
  cost(s) <= C*volume(s) + sum_r sum_j cost(child(s,r,j))
                                             for width(s) >= m.

For the actual selected profile, selected_state_cost_bound proves

  cost(s) <= A*volume(s)*width(s)^(1-a)

for every positive-width state, with the uniform constant

  A = max(0,B) + |C|/(1-SelectedProfileReal.powerCharacteristic).

The actual real characteristic inequality is discharged by the analytic
certificate. There is no supremum over states, normalized function, volume
asymptotic, or implied uniformity premise. Uniform base and overhead constants
are explicitly part of the physical contract. Fin multiplicity sums remain
symbolic; the proof never expands billions of calls. The generic
state_all_width_bound also accepts any A >= 0, A >= B with C <= A*(1-gamma).

Scope
-----

There are 35 new audited theorems (9 depth, 9 recurrence, 12 specialization,
5 state-indexed transfer),
plus 17 analytic dependency theorems. All report only the standard propext,
Classical.choice and Quot.sound axioms, or a subset. There is no sorry, custom
axiom, admitted arithmetic, native_decide, or analytic enclosure premise.

This closes the mathematical floor-recurrence, depth, and integer row-stock
steps. The selected profile's physical recurrence is still a named contract.
This bundle does not prove the emitted compiler trace, fixed-tape execution
and costs, one-time outer row padding implementation, multiplication analytic
reduction, precision, or exact recovery. It does not claim a new numerical
frontier beyond the older selected profile.

Reproduce
---------

Use an existing project pinned to Lean4.21.0 and Mathlib commit
308445d7985027f538e281e18df29ca16ede2ba3, with dependencies/cache built and the
matching Lean/Lake on PATH. From the mission directory:

  python3 outputs/transfer-proof/recurrence/check.py \
    --lake-project work/agents/lean-foundations/formal/lean \
    --certificate outputs/selected-certificate.json

The portable script accepts --analytic-dir and --output overrides. It checks
source hashes and the selected-profile binding, then compiles all seven modules
in order into an isolated olean directory, auditing all 52 theorem declarations.
It installs nothing and modifies no project, dependency, or proof source.
--check-sources-only checks the dependency pins, hashes and bindings without
compiling. The saved verification/ directory contains the successful fresh
build, source binding, and axiom audit; declaration-scope-map.json maps all 35
new declarations to their precise mathematical scope.
