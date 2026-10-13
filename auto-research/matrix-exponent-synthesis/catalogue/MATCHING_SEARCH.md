# Exact fixed-DAG assignment benchmarks

`assignment_certificate.py` adds exact integer dual certificates to the community's numerical weighted-matching discovery. It uses the actual admissible-carrier edge dumps and rigorous rational logarithm/exponential enclosures. The numerical solver proposes an assignment; its result is accepted only after every exact dual inequality, selected-edge tightness, column injectivity, nonpositive column price, zero unused-column price and primal/dual equality is checked.

The four self-contained inputs and lossless integer cost dumps are under `inputs/matching/` and `*-integer-costs.tsv`. `assignment-audit-receipt.json` records standard-library replay of every certificate and twenty corrupted-cost/dual/matching/source controls. Run the replay without SciPy:

```
python -S assignment_certificate.py --edges inputs/matching/h25-selected-edges.txt --verify fixed-dag-h25-selected-dual.json
```

The fixed parameter in these examples is PR48's bit saving `82375901/2000000000000`; it is an explicitly dated search benchmark, not the current global best parameter. The h23 selected hillclimb is a discarded search example. The h25 physical matching is retained unchanged and has quantized primal gap 92 units above the benchmark optimum; its true-cost gap is still rigorously bounded. None of the discovered assignments replaces a complete physical witness automatically.

## Objective and units

Write `F_t=t*exp(a*ln(m/t))=m^a*t^(1-a)`. The signed internal-profile edge objective is `sum delta[t] F_t`. The normalized axis-profile expression `sum delta[t]*(t/m)^(1-a)` is this objective divided by `m`. A complete normalized internal moment multiplies by `axis_repeat/(m*W)` instead. The reported regret bounds use the first units; a bound for the unscaled raw power sum is conservatively the same, since `m^a>=1`.

For the selected h25 search instance there are 14,314 real admissible edges, 9,227 donor rows and 23,541 inequalities including private dummies. The integer primal equals the dual at `23004227857985789`; its true unrounded internal-profile objective regret is at most `3.98473e-9`, or `6.92996e-12` before the axis repetition and division by W in normalized profile units. This proves the **quantized objective optimum**, plus a rigorous near-optimality bound for the unrounded objective over the fixed maximum-cardinality family. It does not prove zero unrounded gap, global graph optimality or optimal kappa.

The matrix/circuit source and the fixed edge/profile assumptions remain separate. Arbitrary changes to scalar graphs, projector bases, dirty endpoints or physical schedules require their own replay and proofs. The discovery idea is credited to Rohan Arun's community work; inherited PR48 projector profiles and rational enclosure methods retain their attribution. Assignment duality is established mathematics; the contribution is its exact certificate integration into this concrete search.

## All-cardinality feasibility correction

Maximum-cardinality matching alone need not optimize a complete characteristic because role count changes both external child costs and W. For a fixed graph with K matches,

```
W = W0-axis_repeat*K,
A = A0+axis_repeat*(sum deltaF-K*(F_h+F_(m-2h))),
A-mW = A0-mW0+axis_repeat*sum[deltaF+m-F_h-F_(m-2h)].
```

`all_cardinality_certificate.py` directly minimizes this fixed-a feasibility slack over **all** matching cardinalities. Every private dummy has raw cost zero. One constant is added to every row edge, real or dummy, solely to keep sparse discovery weights positive; it does not force cardinality.

The actual h25 instance at `a=5155151733/125000000000000` has a certified integer primal/dual equality `22172308087581`, with all 23,541 inequalities checked. It selects 7,894 real edges without a cardinality penalty and encloses its true slack-objective regret by `4.16105e-9`. Its complete-profile baseline slack must be added before deciding feasibility. This optimizes an additive fixed-a feasibility test, not the ratio Phi itself. The candidate still needs full profile and physical replay before becoming a new multiplication witness.

Replay the all-cardinality certificate using only the standard library:

```
python -S all_cardinality_certificate.py --verify all-cardinality-h25-certificate.json
```

The conditional weak-duality companion is in the package's `MatchingDual.lean`. Its integer cost theorem is separate from the written logarithm/profile/slack connection and the Python binding of this concrete instance.
