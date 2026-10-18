# Boundary-preserving sign substitution

This argument applies Ross Richardson's PR919 method to the frozen PR1042
scalar programs. It establishes a local circuit substitution and its complete
primitive price. It does not establish a new recursive supplier or exponent.

## State invariant

Let `x_r` be the baseline value of register `r`.
Let `y_r` be its physical value in the replacement circuit.
Maintain a compile-time sign `s_r` in `{+1,-1}` with

```text
x_r = s_r * y_r.
```

Every sign initially equals `+1` at a run boundary.
The construction applies the following exact rules.

| Baseline primitive | Replacement primitive | Sign update |
| --- | --- | --- |
| `negate r` | none | `s_r <- -s_r` |
| `r <- r + e*q`, `e` in `{+1,-1}` | `r <- r + (e*s_q*s_r)*q` | none |
| `r <- q` | the same copy | `s_r <- s_q` |
| `clear r` | the same clear | `s_r <- +1` |
| `double r` or `halve r` | the same shift | none |

The table proves the invariant by induction on baseline primitives.
For example, the replacement addition gives

```text
s_r * (y_r + e*s_q*s_r*y_q) = x_r + e*x_q,
```

because `s_r^2 = 1`. The copy rule overwrites the target sign and value.
It therefore handles arbitrary incoming target and private-work contents.
The clear rule removes both value and sign.

At the final boundary, negate every register whose sign equals `-1`.
Each such negation costs one primitive. After this flush, all signs equal `+1`
and every physical register equals its baseline value.
No sign state survives a non-scalar event or a literal frame change.

## Full substitution and precision

Each run replacement has the same complete boundary map on arbitrary inputs.
Any surrounding computation therefore receives the same register values.
This conclusion does not require an interpretation of the intervening opaque events.
The events retain their exact positions, frames, operands and order.
The finite package does not itself execute their physical semantics.

At each corresponding prefix, `y_r` differs from `x_r` only by its sign.
Every coefficient's absolute value and denominator therefore agree.
Deferred and final negations introduce no larger magnitude or fractional grid.
This argument applies to arbitrary register values, not only to the sampled
or scalar-only input values used for diagnostic measurements.

The primitive sequence retains every non-negation instruction in order.
An addition can switch between add and subtract, with the same source and target.
No source access, copy, shift, clear, helper or recursive call becomes free.
No workspace lifetime crosses a new physical boundary.
All required final sign restorations receive a charge.

The first implementation checks a fresh sparse rational basis at every run.
The second implementation independently repeats those checks with integer-dyadic rows.
Each touched register has its own arbitrary input column.
Untouched registers retain identity and cannot affect the touched map.
The ambient inventory has 713 registers: 704 logical and nine private.
Both complete scalar projections also check all 713 initial columns.
Endpoint comparison includes every register, including dirty helpers and work.

## Exact cost

For run `j`, let `N_j` count baseline negations.
Let `F_j` count negative signs that survive to its final boundary.
All other primitive counts remain unchanged. Its real-component cost is

```text
C'_j = C_j - N_j + F_j.
```

The complex circuit applies the same real-coefficient word to both components.
Its complete saving is therefore `2 * (N_j - F_j)`.
No assumption that this quantity is nonnegative is valid in general.
For example, negate `a`, then copy it to `b` and `c`.
The baseline has one negation. The replacement must restore three registers.
The complete replacement costs two more primitives.
The package includes this positive cost-growth control.

For each pinned orientation, the full census gives

```text
sum N_j = 560
sum F_j = 356
complex saving = 2 * (560 - 356) = 408.
```

All 2,166 runs receive an exact price, including the 2,137 zero-gain runs.
The 29 changed runs save `128 + 14*4 + 14*16 = 408`.
Neither orientation contains a cost-increasing run in this census.
The complete forward and backward counts are 148,594 and 148,610 respectively.

The paid child profile, frames and non-scalar event word remain unchanged.
The bit supplier remains unchanged. This scalar constant reduction does not
change either supplier's paid recursive moment or justify a new kappa.
No fresh global invoice, hosting admission or analytic transfer is claimed.

## Negative controls and scope

Each changed run has two independently executed mutations.
The first removes a required boundary negation or final logical target update.
The second flips an addition sign. All 116 actual-run mutants fail endpoint equality.
Other controls separate endpoint equality from prefix growth, dirty-work erasure
and the required frame/event boundaries.

The result covers exactly the two pinned programs and the declared substitution.
It proves no circuit minimum and no impossibility outside that class.
It does not combine the sign method with other pending scalar rewrites.
The compiler, source realization, precision/tape and analytic assumptions of the
conditional multiplication framework remain open.
Finite replay is not a formal proof of the all-size multiplication theorem.

New argument and evidence: @Scratch-net, with substantial OpenAI Codex assistance.
Method and compiler: Ross Richardson, PR919.
Primitive lowering: Sagar Thakrar, PR696, on the retained icekylinx circuit lineage.
Apache-2.0. No independent human review is claimed.
