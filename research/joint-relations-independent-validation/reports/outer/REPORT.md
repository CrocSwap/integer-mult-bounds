# Independent BIT, outer and finite compiler arithmetic review

**PASS for the scoped rational arithmetic of both pinned endpoints.** This lane checks Ali Romman's #5383 at `4bd6efa51a495a7c7b7754915cf0244e7e60969e`, κ `.00302666`, and Dugongue's #5387 at `b1ab650d36f59e5be682a813145b7c67e219e341`, κ `.003026674765`. It establishes 54 strict outer inequalities, four additional stock/semantic predicates, retained ordinary BIT arithmetic and the sufficient finite compiler's integer threshold. This is a component of same-premise conditional admission. It does not establish native/ownership/physical applicability, promote selection, or prove an unconditional multiplication theorem.

The new standard-library checker is `check_outer.py`; exact values and observed resources are in `RESULT.json`. `SOURCES.json` pins every directly used source. Candidate Python code was read for contracts but never imported or executed. The separate independently transcribed #5241 ledger preserved in #5384 supplies explicit equation provenance; this checker implements those equations afresh and evaluates its own rational parameter family. The resulting rows are compared with the author receipts only after independent computation. Author receipt equality is an error check, not the decisive oracle.

## Derivation and exact coverage

Write `K` for outer κ, `C` for the tested complex saving and `g=(C-K)/7`. Allocate

```
uniform = K+6g, b = K+5g, a = K+4g, q = K+3g,
epsilon = 1-g, beta = 1-3g, r0 = g/10, stop = layout = g.
```

The complex compiler must furnish `C > uniform > b > a > q > K`. The outer exponent definitions are `sigma=1-b`, `tau=1-a`, `internal=tau+(1-stop)max(sigma-tau,0)`, `leaf=sigma+stop(1-sigma)`, `lambda=1-(q+a)/2`, `xi=epsilon(1+q)-3/32+layout`, and record-key exponent `beta+1-epsilon`. The checker derives the nine work savings from these exponents, computes every named comparison independently, and checks all are strictly positive. The 54-row inventory includes the nine work savings minus `K`; the other 45 rows cover supplier savings, stopping/leaf recursion, lambda separations, cap/group bounds, logarithm absorption, layout, source geometry and semantic guards. Four additional predicates bind group semantics and inherited/current BIT stock.

The binding work saving is always `main_transform=epsilon*q`; its headroom is

```
epsilon*q-K = g(3-K-3g).
```

| Quantity | #5383 | #5387 |
| --- | --- | --- |
| Tested saving C | .00302667 | .003026674766 |
| g | 1/700000000 | 1/7000000000000 |
| Uniform saving | 529667/175000000 | 21186723361/7000000000000 |
| Effective BIT saving a | 1059333/350000000 | 21186723359/7000000000000 |
| BIT .0034 minus a | 130667/350000000 | 2613276641/7000000000000 |
| Main-transform headroom | 419576267/98000000000000000 | 10489406638321/24500000000000000000000000 |
| Approximate main headroom | 4.2813904796e-9 | 4.2813904646e-13 |
| Minimum of all 54 strict slacks | 1/7000000000 | 1/70000000000000 |
| Strict/functional counts | 54 / 4 | 54 / 4 |

The smallest strict slack is the assigned logarithm-absorption margin `r0`; it is not the binding work saving. Exact full row values are preserved in `RESULT.json`.

## BIT compatibility

Both candidate records must equal the unchanged BIT record from `research/query-thinned-controllers/RESULT.json` byte-for-value at the JSON object level. The checker recalculates

```
atom = 1/250,
ordinary = (1-atom)(69/20000)+atom(.0000384599)
         = 8590884599/2500000000000,
admitted = 17/5000 = .0034.
```

It verifies `atom > ordinary > admitted > C`, `admitted > a`, `atom < 1-ordinary`, and `0 < beta(1-atom) < 1`. All 54 strict/four functional rows use the retained compatible supplier. This lane inherits that supplier's native/interface/precision admission; it does not re-prove the BIT native construction or replace it with a cross-field operation. Under this outer contract, the supplier requires strict `a>K`; hence `.0053` and `.0073` outer targets cannot be funded by the unchanged `.0034` BIT supplier.

## Compiler threshold and reserve

For power 1000, tensor exponent `v=1024`, and integer `step=1/g`, the sufficient inequality is

```
H = step*j,          (H+1)^1000 < 2^j.
```

An independent exponential search and binary search computes the winning integer; arbitrary-size integer comparisons evaluate the strict winner and the immediately preceding index. The function `1000 log(step*j+1)-j log(2)` is strictly concave, equals zero at `j=0`, is positive at `j=1`, and eventually negative. Therefore these two exact comparisons establish the least winning positive integer on this specified `H=step*j` grid. They do not establish the least arbitrary height or an optimal compiler.

| Compiler quantity | #5383 | #5387 |
| --- | --- | --- |
| j | 44836 | 58507 |
| H | 31385200000000 | 409549000000000000 |
| N encoding | 2^31385200000000 | 2^409549000000000000 |
| Winning strict integer comparison | pass | pass |
| Comparison at preceding j | fails | fails |
| H > 8v | pass | pass |
| Completion reserve rho | 1e-9 | 1e-12 |
| Remaining normalized rounding margin | 2145530521/2097154147483648 | 97179323/1048576001073741824 |
| Approximate margin | 1.02306762885e-6 | 9.26774243359e-11 |

No enormous expanded word or `N` is materialized. All counts are encoded in integers, and the largest comparisons involve only tens of thousands of bits.

The fixed rounding debit is `R=4/2^32`. Its funding condition is

```
1/(1+v*rho) + R < 1
iff rho > R/[v(1-R)] = 1/1099511626752
                           approximately 9.0949470262e-13.
```

Both reserves strictly pass. A `1e-13` reserve strictly fails. Thus moving near the raw crossing cannot treat reserve as freely shrinkable under this fixed rounding construction. Exact decay checks `(.97)^128 < 1/16`, `4(.97)^1024 < 4/2^32`, target splitting `20^64 < 21^63`, and shifted-exit capacity `2*20^(1024*64) <= 145^(1024*63)` also pass. Independent interval checks for alpha, both completion tails, eta/complement capacity and initial range belong to the pricing lane and are separate dependencies of complete compiler admission.

## Rejections and endpoint scope

For **each endpoint**, the independently recomputed rows reject insufficient BIT `.0027`, closed BIT saving `bit=a`, closed complex saving `uniform=b`, unfunded outer endpoint `K=C` with the other funded parameters held fixed, closed epsilon `epsilon=1`, and absent layout `layout=0`. Separate exact checks reject `rho=1e-13`, a closed compiler gap `K=C`, and the preceding compiler grid integer.

These controls test the actual mathematical margins, not file hashes. A rejected mutant does not imply all conceivable constructions under its altered parameters are impossible.

The preceding **compiler j-grid** failure is distinct from a κ **next-grid** claim. Neither original author endpoint is certified optimal by this lane. The common raw profile crossing `(0.00302667476807, 0.00302667476808)`, independently reconstructed moments and tests at `.003026674767/.768` are assigned to the pricing lane. Any next-grid failure there applies to that named profile, tested saving, reserve and completion prescription. A raw crossing is not an outer theorem or a circuit ceiling.

## Executed command and resources

Executed from the project root, with no external writes, commits, PRs, solver, Lean or subagents:

```bash
timeout 15s bash -c 'ulimit -v 131072; ulimit -t 15; python3 -B swarm-execution-sol-high-20261024/agents/outer/check_outer.py --candidate PR5383 swarm-execution-sol-high-20261024/repository/research/kappa-joint-relations-20261023/RESULT.json --candidate PR5387 swarm-execution-sol-high-20261024/agents/sources/pr5387/research/eight-owned-relations/RESULT.json --bit-source swarm-execution-sol-high-20261024/repository/research/query-thinned-controllers/RESULT.json --out swarm-execution-sol-high-20261024/agents/outer/RESULT.json'
```

Final execution: Python 3.12.3, 0.120 seconds, 18,696 KiB maximum process RSS, exit 0. Hard address-space/CPU limits and a wall timeout were applied. This small arithmetic screen required no root-serialized heavy run. Only this lane's owned files were created or edited; all referenced packages remain read-only.

Invalidation: changed candidate receipt bytes, C/K/rho, supplier/domain, compiler power/tensor/cutoff/tail/rounding constants, outer exponent contract, physical input class or precision/stock applicability invalidate the corresponding checks. This report's PASS remains scoped until the independent invoice, moment/tails and physical applicability dependencies are accepted by the integrator.
