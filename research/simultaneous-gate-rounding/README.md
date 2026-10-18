# Simultaneous rounding of the capped Toeplitz circuit

PR1673's `SHALLOW-TOEPLITZ.md` section 6 bounds the effect of one perturbed
gate using exact prefixes and suffixes. This note supplies an explicit bound
when **all** coefficients and arithmetic steps are perturbed at once. It also
bounds the perturbed prefixes and their mathematical inverses. The resulting
fractional-precision guard has the same asymptotic order as the source's claim;
no additional linear-in-dimension precision term is needed.

This is a source-bound interface lemma and audit, not a new Toeplitz compiler,
reversible rounding implementation, supplier or exponent. The exact compiler's
prefix bound remains an input hypothesis. Its proof and all-size circuit
construction are not independently certified here.

## Nonasymptotic statement

Use any induced matrix norm and its compatible vector norm. Let the invertible
exact gates be `A_1,...,A_K`, in execution order, and put
`F_0=I`, `F_j=A_j ... A_1`. Suppose

```
max_j { ||F_j||, ||F_j^-1|| } <= B,    B >= 1.
```

Let rounded gates be `A_j + Delta_j`. Define

```
D_j = F_j^-1 Delta_j F_(j-1),
delta_j = ||D_j||,
rho = sum_j delta_j < 1.
```

Then every rounded prefix `Q_j=(A_j+Delta_j)...(A_1+Delta_1)` is invertible,
and, uniformly in `j`,

```
||Q_j||, ||Q_j^-1|| <= B/(1-rho),
||Q_j-F_j|| <= B rho/(1-rho).
```

For an actual arithmetic trajectory
`y_j=(A_j+Delta_j)y_(j-1)+u_j`, with `||y_0||<=M`,

```
||y_j-F_j y_0|| <= B (rho M + B sum_i ||u_i||)/(1-rho).
```

The sum may stop at `j`; using the full sum is a safe common bound. A directly
usable sufficient budget is `rho <= B^2 sum_j ||Delta_j||`. The sharper
interaction budget above is useful for a completely emitted finite circuit.
Errors may depend on the current data and need not be independent, unbiased,
random or commuting. They need only obey the stated bounds on that trajectory.

## Proof

Write `R_j=F_j^-1 Q_j`. Direct multiplication, with order retained, gives
`R_j=(I+D_j)R_(j-1)`. Expanding this finite product bounds its norm by
`product(1+delta_i)` and its difference from identity by that product minus
one. Nonnegative elementary symmetric sums of degree `r` are at most
`rho^r`; hence `product(1+delta_i)<=1/(1-rho)`.

Each `delta_i<1`, so the Neumann inverse exists and has norm at most
`1/(1-delta_i)`. Induction gives
`product(1-delta_i)>=1-sum(delta_i)>=1-rho`. Thus both the forward product
and its inverse have norm at most `1/(1-rho)`. Multiplication by `F_j` or
`F_j^-1` proves the prefix bounds and the operator-defect bound.

For arithmetic errors put `z_j=F_j^-1 y_j`. The recurrence is
`z_j=(I+D_j)z_(j-1)+F_j^-1 u_j`. Every later interaction product has norm
at most `1/(1-rho)`. Summing the propagated errors gives
`B sum||u_i||/(1-rho)` in interaction coordinates. Returning to physical
coordinates contributes the outer `B`, as in the displayed statement.

This closes the simultaneous-error step without assuming that rounded
prefixes already satisfy the exact circuit's bound. An exact cancellation
between large gates alone does not supply the required prefix/inverse bound.

## Precision consequence for the pinned source

For the source's two-wire gates, take the Euclidean norm. If each complex gate
entry has absolute error at most `eta=2^-P`, the embedded gate perturbation
has norm at most `2 eta` by the Frobenius bound. If the arithmetic result in
each of its two complex coordinates has error at most `eta`, then
`||u_j||<=2 eta`. Real and imaginary components stored to `P+1` fractional
bits suffice even for componentwise truncation. The local arithmetic must
actually deliver that final-coordinate error; this note does not assume it
from an unspecified floating-point format.

For `||y_0||<=1`, `p>=0`, `K>=1`, a sufficient fractional precision is

```
P = p + ceil(log2(8 K B^3)).
```

Indeed `rho<=2KB^2 eta<=1/4`, so the trajectory error is at most
`2B(2KB^2+2KB)eta<=8KB^3 eta<=2^-p`. Every perturbed prefix and inverse
has norm at most `2B`. This is an upper bound, not a minimal guard.

The source at exact PR1673 head
`85ddaa312e463cfaca98d49a2a262994551cec4e` supplies:

| Source claim retained as a hypothesis | Consequence here |
| --- | --- |
| Sections 1 and 6: `K=N polylog(N)` and prefix/inverse bound `B=N^O(1)` for fixed near-identity margin | `P=p+O(log N)`, as claimed; no changed power or new numeric constant for that compiler |
| Section 9: `log B=O(log N * log(2+M+1/mu)+log N)` for the SPD extension | Guard `O(log K+log B)`, retaining its stated spectral dependence |
| Main note's grouped logarithmic range `O(g a B_cap+g polylog(p))`, with polynomial local stage count | The same `O(g a B_cap+g polylog(p))` arithmetic guard; the separately paid inherited `a d` term is unaffected |

The source uses `B` for a cap length in places; `B_cap` above distinguishes
that length from this note's prefix bound. For a parallel layer, serialize
its disjoint gates; this is a proof device, not an extra time charge. Norms
of intermediate subsets of a disjoint layer are bounded by its completed
block norms together with the preceding prefix bound, so the source must
supply the prefix bound for the chosen emitted gate order (or enlarge it by
the already stated polynomial gate factor). The asymptotic guard is unchanged.

The finite verifier does **not** extract a numeric universal `B` from big-O
notation. It independently measures exact prefixes/inverses of its declared
rational controls. A production finite-width admission must compute or prove
its own bound and account for integer bits, coefficient generation, overflow,
and the actual local arithmetic error. Exact inversion of a rounded matrix
does not assert reversibility of a rounded instruction sequence.

## Evidence and reproduction

`verify.py` uses exact Fraction matrix arithmetic with the induced infinity
matrix norm and maximum-entry vector norm. The source-facing two-complex-wire
precision consequence above uses the Euclidean norm; the universal theorem
permits either choice, and the finite controls do not certify Euclidean norms.
Direct rounded products
are checked against an independently formed interaction recurrence, including
noncommuting, cancelling and ill-conditioned intermediate gates. All prefixes,
inverse prefixes and adversarial arithmetic trajectories are checked, and the
explicit bit guard is exercised. The readable proof above is universal; these
finite checks are corroboration, not a proof assistant result.

Controls reject omission of higher-order terms, an endpoint-only norm bound,
omitted arithmetic error, a missing small-budget premise and changed matrix
order. Git-free replay checks source and typed-receipt corruption and default
read-only behavior. Run:

```sh
python3.12 -I -O -B research/simultaneous-gate-rounding/verify.py
python3.12 -B scripts/research_package.py --package research/simultaneous-gate-rounding
```

`--out NEW.json` exclusively writes a freshly computed receipt. Hosted CI,
the original compiler's native/full replay and selected multiplication replay
are not claimed.

## Credit and scope decision

Vlado Vojdanovski and the credited PR1673 predecessors retain the circuit,
prefix estimates and outer-transfer work. PR2044's reused review and PR2578's
rectangular/union review are related evidence; this note isolates simultaneous
gate and trajectory perturbation instead of repeating their numerical ledger.
Neumann-series and product perturbation arguments are standard mathematics.
The contribution is their explicit nonasymptotic integration at this interface.
The independent-moment draw is refined to its formal-interface alternative;
TASK.json records the source, overlap and stopping decision.

## Open next questions

Bind an emitted all-size circuit to a computable prefix/inverse envelope and
an actual bounded-error arithmetic kernel. Start with one exact emitted local
tile and report `K`, the proved or measured `B`, coefficient error and noise
budget. The present theorem does not turn the source's asymptotic constants
into a certified machine precision or finite cutoff.

Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
No independent human review is claimed.
