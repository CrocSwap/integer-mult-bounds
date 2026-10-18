# Paid phase-local gauge schedules

The varying-gauge identity, clipping lemma and chain DP also occur in Sagar
Thakrar's concurrent PR1259; they were independently derived during this work.
We credit that overlap explicitly. The new proof obligation here is exact identity
at **every** non-scalar boundary, including recursive and residual-wrapper events,
and the exact price of imposing it. No novelty is claimed for the common DP.

Fix a helper h not occurring in any scalar COPY/CLEAR and not a private center.
Partition the emitted program at every non-scalar event, including phase markers,
climbs, adapters, residual wrappers and center events. Each resulting scalar run
begins and ends with gauge exponent zero. All other registers have gauge zero.

## Exact arbitrary-input identity

Let D(k) scale h by 2^k. Immediately before an original scalar gate A, change the
current gauge j to k by the paid scale D(k-j), and replace A by D(k) A D(-k).
For an ADD `t += q*s`, this changes only its coefficient, to
`q*2^(k*([t=h]-[s=h]))`. Original SCALEs commute with D and remain unchanged;
COPY/CLEAR has no incidence with h. Finish the run by D(-k).

Telescoping shows that the new run has exactly the old linear map on every input,
including arbitrary helper and coefficient-work dirt (the latter is separately
handled by the retained literal lowerer). Since the gauge is zero at every
non-scalar boundary, no commutation through a recursive child, wrapper or phase
operation is needed. The entire non-scalar state and paid child stream are
unchanged. The original common frame of an incident ADD is also h's current
frame, so an adjacent scale on h uses exactly that frame. The unchanged emitted
frame/wrapper checker tests these conditions on the materialized winners.

Gauges need change only immediately before incident ADDs, with restoration just
after the last such ADD in a run. They commute with disjoint scalar gates and
existing SCALEs; moving a scale to such an adjacent position changes neither
map nor price. Multiple successive changes collapse at no greater price by the
triangle inequality. Runs without incident ADDs optimally use no new scales.

## Complete cost and finite exact optimization

Write the absolute reduced dyadic ADD coefficient as p*2^e with p positive odd.
The retained PR696 one-component cost is

```
c(p,e) = 2 + floor(log2(p)) + popcount(p) + |e| - [p=1 and e=0].
```

For the i-th incident ADD, set s_i=+1 for h as target and -1 as source,
b_i=-s_i e_i, and u_i=[p_i=1]. Its gauge-dependent cost, up to an unchanged
constant, is `f_i(k)=|k-b_i|-u_i[k=b_i]`. A positive dyadic scale costs the
absolute change of exponent. Thus the complete variable objective is

```
|k_1| + sum_i f_i(k_i) + sum_{i=2}^n |k_i-k_(i-1)| + |k_n|.
```

No entry, interior or exit scale is omitted. The unchanged scalar gates and all
COPY/CLEAR costs are added back by a complete literal invoice. The complex call
executes this one-component word on real and imaginary parts, doubling the count.

**Clipping lemma.** Put L=min(0,b_1,...,b_n), U=max(0,b_1,...,b_n). Project every
integer k_i onto [L,U]. Projection is 1-Lipschitz and fixes zero, so all transition
and boundary costs weakly decrease. Each distance to b_i weakly decreases. A
discount previously attained is retained, and a new one may appear. Therefore
the objective cannot increase. There is an optimal schedule entirely in this
finite integer interval; this is not an empirical exponent cutoff.

The exact DP starts at state 0 with cost zero. For each incident ADD, compute
`V_i(k)=f_i(k)+min_j(V_(i-1)(j)+|k-j|)` and finally minimize `V_n(k)+|k|`.
All costs and states are integers; backtracking supplies a witness. The intervals
include every integer, not merely coefficient breakpoints. The unit discount
makes a naive convex/median shortcut invalid.

Different runs are independent because each boundary state is fixed at zero.
Sum the exact run minima for each helper, then compare all 477 admissible helpers.
This proves the declared one-helper optimum, conditional on the source-bound
finite input and retained primitive cost model. It does not prove an all-circuit
or all-helper bound. The same argument applies after fixing PR1214's fully priced
two-helper word; only one new phase-local helper is optimized in that comparison.
The identity boundary in that composition is relative to the fixed PR1214 word;
its existing two constant gauges and their transfer assumptions are inherited.
The wrapped L652 witness instead applies the zero-boundary rule directly to the
selected original word, including both residual-wrapper boundaries.

## Separate checks and limits

`comparison.py` removes the reset barriers only for pricing, joins each helper's
incident terms, and reproduces every one of PR1259's 32 saved minima. The barrier
objective is a restriction of that chain: it inserts a fixed-zero state at every
non-scalar boundary, so its optimum cannot be lower. Its one-component extra price
is 2 at L276, 2 at L427, and 0 at L359, in each orientation. The unrestricted L427
comparison is scalar pricing only; we do not construct or admit that unrestricted
word. The reset L427 and fixed-PR1214-plus-reset-L359 words are the materialized
and locally admitted constructions in this package. This distinction avoids
assuming any new gauge commutation through the inherited recursive interface.

The main implementation explicitly minimizes over all predecessor states.
`independent.py` instead uses forward/backward distance-transform sweeps,
evaluates costs by the actual PR696 lowerer rather than the formula, and enlarges
every exponent interval by two on each side. Its independently reconstructed
candidate streams match canonical hashes, and its literal primitive interpreter
tracks 713 arbitrary initial columns, including dirty coefficient work.

The finite exact replays support the source-bound construction. The clipping and
telescoping arguments are written proofs, not proof-assistant certificates of
the multiplication theorem. The paid recursive profile is unchanged, so this
does not improve the selected moment root or kappa. Full compiler, native, hosting,
global precision/tape and analytic obligations remain as stated in the README.
