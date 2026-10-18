# Two dirty roots attain twelve signed connector queries

**Research construction with a sharp child-query count; no new kappa.**
A second dirty root changes the one-root signed connector barrier.
The word below attains the universal twelve-query lower bound with six paid root passes.
The extra root is an explicit space cost; no selected-supplier admission is claimed.

## Exact interface and claim

Let `x0,x1,x2,y0,y1,y2,z,w` be distinct length-L arrays with arbitrary initial contents, for every integer `L>=1`.
Choose fixed linear maps `A0,A1,A2,B0,B1,B2` over Q or C.
They need not commute or be invertible.
Each complete child query preserves its source, other arrays, private scratch, and required head positions.
Its increment is independent of its target's old contents.
The data arrays and both roots stay outside child scratch.
Sources and coefficients are immutable, and outputs are observed only at completion.
An ordinary B query adds or subtracts B_j x_j into one root.
An ordinary A query adds or subtracts A_i of one root into its designated output.
No combined query, direct product query, output read, overwrite, source mutation, or other data operation is allowed.

The required map fixes the sources and roots and adds the following to the outputs:

```text
M = [[1,1,1], [1,1,-1], [1,-1,0]],
y_i += sum_j M_ij A_i B_j x_j.
```

Permit signed child queries into or from either root, and paid shears `z += a*w` for `a=-1,2`.
The following chronological word uses twelve child queries and six root passes:

```text
z += B0 x0
 y2 += A2 z
z += B1 x1
z -= w
 y0 += A0 z
z += 2w
 y1 += A1 z
z -= w
z -= B0 x0
 y2 -= A2 z
z -= B1 x1
w += B2 x2
z -= w
 y0 -= A0 z
z += 2w
 y1 -= A1 z
z -= w
w -= B2 x2
```

All roots and child scratch restore exactly.
This changes PR944's one-root alphabet; it does not contradict its fourteen-query minimum.
It also changes PR1526's one-root scaling alphabet, whose minimum remains thirteen queries.

## All-input argument

Write `u=B0 x0`, `v=B1 x1`, and `t=B2 x2`.
The first A2 read sees `z0+u`; the second sees `z0+v`.
Their difference gives `A2(u-v)`.

At the first pair of A0/A1 reads, the arguments are `z0+u+v-w0` and `z0+u+v+w0`.
At the later negative reads, the arguments are `z0-w0-t` and `z0+w0+t`.
Their differences give `A0(u+v+t)` and `A1(u+v-t)`.
Each three-pass root block has coefficients `-1,2,-1`, whose sum is zero.
The B queries also cancel in pairs, so both arbitrary root inputs restore.
Linearity proves the map without commuting any operators.

The inverse reverses every event and negates each shear coefficient.

Twelve child queries are minimal for a word that works uniformly for every permitted operator and input.
The lower bound even permits arbitrary invertible scalar changes of basis on the two roots.
These scalar changes do not depend on input values.
Fix any L. Specialize all six operators to L-by-L identities and restrict each input to one common coordinate.
The resulting scalar calculation suffices for the lower bound.
Every column of M is nonzero, so every B_j must occur.
If B_j occurs once, it injects a nonzero multiple of x_j into the two-root vector.
Later root changes multiply this vector by invertible matrices; no other source query contains x_j.
An A query never changes a root.
Thus a single B_j occurrence cannot restore both roots for arbitrary x_j.

Every row of M is nonzero, so every A_i must occur.
The dependence of the current roots on their two initial dirty values is an invertible 2-by-2 matrix.
Source queries do not change that dependence.
If A_i occurs once, its read selects a nonzero row of that matrix and leaves dirty input in y_i.
Other A operators write different outputs and cannot cancel it.
Thus each of three B and three A operators needs at least two occurrences.
The twelve-query word attains this universal lower bound.
A special zero operator or algebraic relation can have a cheaper instance-specific implementation.
This argument does not minimize root passes or complete cost.

## Complete tariff and recursive lowering

Let `c_F` include source/coefficient access, arithmetic, restoration, routing, frame work, head return, and query dispatch.
Assume these complete prices agree between signs and the relevant root ports when using the simplified comparison.
Otherwise sum the actual port-specific prices of the literal word.
Let `t_-` and `t_2` be the complete root-pass prices, including both root reads and writes.
Let `I`, `P`, and `D` charge admission, coefficient preparation, and any remaining program work.

Then

```text
C_two = I_two + P_two + D_two + 2 sum_F c_F + 4 t_- + 2 t_2.
C_14  = I_14  + P_14  + D_14  + 2 sum_F c_F + 2 c_min.
C_13  = I_13  + P_13  + D_13  + 2 sum_F c_F + c_min + d + h.
```

The last comparator uses PR1526's paid doubling and halving prices `d,h`.
Every difference in admission, layout, preparation, and program work must enter the comparison.
The new word needs one additional dirty root.
It is not an unconditional cost improvement at arbitrary tariffs.

Balanced product lowering uses `C(F)=2C(R)+2C(S)+dispatch`, with disjoint dirty child scratch.
For factor lengths `B=[2,3,4]` and `A=[5,6,7]`, complete factor-call counts are `4,10,16,28,40,52`.
The expanded programs contain 308, 304, and 300 factor calls for the fourteen-, thirteen-, and twelve-query words.
The thirteen-query word has two scaling passes; the new word has six root passes.
The new word reserves two root rows and three child rows, versus one root and three child rows.
The expanded formal interpreter verifies all eleven independent dirty input rows and all 27 noncommuting factors.

## Declared dense tape invoice

This is an exact word-cell model, not a measured runtime or a selected-supplier tape implementation.
Use integer coefficient matrices, exact arithmetic, and a data head that starts and ends each primitive at cell zero.
Place the mutable rows first, then the 27 row-major coefficient matrices.
For every dense factor term, visit its coefficient, source cell, and target cell; update the target directly.
A root pass visits each source-root cell and corresponding target-root cell.
A scaling pass scans the affected root.

All reads, writes, additions, multiplications, dyadic operations, and literal instruction counts appear in the receipt.

The candidate uses eleven mutable rows.
The compact predecessors use ten; their child scratch indices shift down by one.
Common eleven-row comparisons also appear in the receipt, but do not replace the stronger compact baselines.
The candidate therefore pays the extra row in both layout and admission reads.


For a factor with matrix index f, source row p, target row q, and R mutable rows, its head moves equal

```text
(2f+1)L^4 + (2R-2min(p,q)-1)L^3 + 2(q+1)L - 2.
```

This formula follows by summing the literal coefficient/source/target visits and the final head return.
A candidate root pass from row seven to row six costs `2L^2+14L-2` head moves.
A predecessor root scaling costs `14L-2`.
These formulas independently match the simulated aggregate bills at lengths 1,2,3,4,8,16,32,64.

The candidate's operational head-move difference against the compact thirteen-query word is

```text
delta(L) = -8L^4 + 148L^3 + 12L^2 + 476L.
```

It is positive for integers 1 through 18 and negative for every integer at least 19.
For `L<=18`, the cubic factor is `L^2(148-8L)+12L+476 > 0`.
At 19 it equals -740; its forward difference is `-24L^2+272L+152`, negative and decreasing thereafter.
An initial full admission scan and return adds two further head moves per extra cell, hence `2L` to the difference.
That addition preserves the same threshold, by the same argument with constant 478.

This head-move result alone does not compare arbitrary weighted physical costs.
The extra row increases space.
[COST.md](COST.md) gives the exact integer-width bound, owned scalar registers, program encoding, admission, controller tariff, and host costs.
A separate bounded-integer machine checks the expanded words against direct product evaluation.
The receipt preserves every charged component instead of treating fewer queries as a complete runtime gain.

## Verification, provenance, and next step

The short word passes a free noncommutative symbolic interpreter and a separate elementary-matrix product checker.
The latter checks 20 dense fixtures, 480 independent basis columns, both orientations, and 16 noncommuting cases.
Twenty short-word controls and three expanded-word omission controls reject broken maps.
The bounded-integer machine checks 36 expanded fixtures and their inverses, with five additional failure controls.
An independent summation formula checks the tape tracer's polynomial.
These checks are not a proof assistant or external human review.

`SOURCES.json` pins the main-base inputs and the PR1526 README containing its proof.
Credit Ross Richardson's PR944, martinxxx9's PR1088, and Hanson Sun's PR1526 and PR1556.
PR1438, PR1498, and the concurrent PR1615 concern a different characteristic-two five-source universal target with two connectors.
Credit woklerx, Gareth Davidson, Hanson Sun, and Cinna Davis for that mechanism lineage.
They receive mechanism credit; this package makes no broad priority claim for adding a second connector.

The small witness search stops after finding this construction.
It establishes no excluded search domain or optimal root-pass count.
The selected PR1094 certificate and `upstream/` remain unchanged.
Prepared for Charles Bethin with substantial OpenAI Codex assistance; Apache-2.0.

## Open next questions

- Can fewer paid root passes attain twelve queries for this signed target? Derive a transfer lower bound before searching. The current proof bounds queries only.
- Does a selected supplier expose the required immutable source and exact additive child ports? Identify one actual interval and price both root rows, hosting, precision, and assembly. No such interval is supplied here.
- Can the complete invoice improve at an actual fixed space budget? Implement the required adapters with common widths. The extra root and arbitrary Q/C precision remain blockers.

These questions concern different proof obligations. The finite fixture does not close them.

## Replay

Use Python 3.10 or later with the standard library, from the repository root.
Local verification uses stable CPython 3.15.0 through the research wrapper.
The output directory must not already exist.

~~~sh
python3 -I -B research/two-root-signed-connector/replay.py --out /tmp/two-root-new-output
~~~

Expected: `PASS_TWO_ROOT_LOCAL_REPLAY queries=12 roots=2 root_passes=6 factor_calls=300 controls=28 machine_fixtures=36; no supplier admission`.

The command checks source pins, runs optimized checkers in the output directory, and compares semantic receipts.
It also works after copying the package to a read-only location.
See TASK.json for exact source heads, scope, and local validation.

For read-only relocation and four on-disk corruption controls:

~~~sh
python3 -I -O -B research/two-root-signed-connector/test_package.py
~~~

Expected: `PASS_TWO_ROOT_PACKAGE relocation=1 corruptions=4`.
The expected receipts serve as regression records; they are not independent proof evidence.
