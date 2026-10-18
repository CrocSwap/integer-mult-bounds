# Persistent coefficient work in the contracted factory

**Finite complex-supplier circuit result and restricted floor; no new kappa.** Keeping coefficient work across ADD boundaries lowers the contracted PR922/924 factory to 46 primitives per real component in the forward and inverse orientations. The inverse-transpose and transpose minima are 48. The maximum therefore remains **48**, exactly the floor already attained by deferring intermediate work clears without any coefficient reuse.

The added evidence is the complete joint gauge/cache census and its orientation boundary. It does not claim a new global supplier or attribute earlier clear-elision savings to caching.

| Minimum over the fixed six-scale placement class | Forward | Inverse | Inverse transpose | Transpose |
|---|---:|---:|---:|---:|
| PR696, work cleared after every ADD | 73 | 73 | 73 | 73 |
| Known-zero clear elision | 54 | 55 | 54 | 55 |
| Only final work clear; fresh preparation every nonunit ADD | 48 | 48 | 48 | 48 |
| Persistent just-in-time source cache | **46** | **46** | 48 | 48 |

Each entry includes the six SCALEs, all 26 data accumulations, every source COPY and work shift, and required work erasure. Real and imaginary components use the same word, so a complex invocation costs twice an entry. The 2-operation forward/inverse gain over the strongest clearing comparator becomes 4 real-component primitives per such complex invocation. No additional four-orientation-maximum saving follows.

## Reproduce

From repository root, with Python 3.10+ and its standard library:

```sh
python -I -O -B research/factory-persistent-work-seed23/verify.py
```

Expected final line:

```text
PASS_FACTORY_PERSISTENT_WORK placements=39424x4 minima=46,46,48,48 controls=11 no_new_kappa
```

Default replay is read-only. It rebuilds both complete census implementations, compares every histogram, replays all 144 winning mode/placement/sign witnesses, invokes the unchanged PR696 emitter for the exact comparator, and compares every certificate field canonically. --write-certificate deliberately regenerates only this package's certificate. Source hashes, exact consumed inventory and frozen base are checked before predecessor code is loaded.

## Exact class and dirty-work contract

The input is PR924's retained composition of PR922's contractions: 26 ordered ADDs and six nonidentity net SCALEs, all at frame [390,74,44,30], on eight data wires. The only extra wire is the already existing coefficient-work register W. Entry data and W are arbitrary and may be correlated; exit data implement the original eight-wire map and W is zero. The first nonunit preparation uses paid COPY to overwrite arbitrary W before reading it. The final CLEAR is paid. If unit operations precede that preparation, they do not read W.

This overwrite COPY is an inherited unit primitive, not a new cost assumption: pinned research/complex-dyadic-lowering/lower.py documents dirty work on entry and emits a single COPY to replace clear plus the leading binary addition. The verifier calls that emitter and compares its exact primitive stream at every replayed witness. Source/work aliasing is rejected.

The net scales are (2,2,2,1,1,-1,2,-2). At the minimum 32-macro count, each of the six nonidentity wires has exactly one prescribed scale. The five magnitude-scale wires have 8,8,8,7,11 possible slots between their uses, giving 39,424 placements. Sign-only wire5 has eight slots. Its placement changes signs but not any charged primitive count or cache eligibility: both signs of accumulation cost one. The complete class contains 315,392 placements per orientation. Seed23 picks sign slot7 as the cost-census representative; all eight signs of every winner are literally replayed.

At a nonunit update T += c S, c = signed 2^e, the just-in-time policy allows two ways to prepare coefficient work:

- Paid COPY W := S, followed by |e| doublings/halvings.
- If W is a signed 2^f multiple of the current, unchanged S, perform |e-f| shifts and adjust the accumulation sign.

Then one paid target accumulation is emitted. Unit updates remain direct and do not proactively prepare work. An ADD writing the cached source invalidates that cache. A SCALE on it adjusts the cached exponent and sign. Other data operations leave it available. No speculative preloads, target accumulation decomposition, arbitrary linear combination in W, data reordering, extra helper, frame crossing, additional SCALE or new macro topology is allowed.

For fixed macros, the cheaper preparation is optimal in this stated policy. Both choices leave W equal up to sign to the same required coefficient times the same current source. Sign changes do not alter any later cost. The future cost state is therefore the same, so local minimization is exact. This is a policy-class optimum, not unrestricted scratch-register synthesis.

## Gauge proof and independent evidence

Move the original scale products to the end algebraically. If S_r is the old product before an ADD and S'_r the chosen product there, its new coefficient is c (S'_d/S_d)/(S'_s/S_s). This diagonal-conjugation identity preserves every boundary map when the final scale totals agree. It holds for arbitrary correlated inputs. Enumerating all six-scale placements therefore closes exactly the declared minimum-macro gauge class; no timeout, state cap or heuristic pruning is used.

The primary constructor normalizes coefficients, materializes each gauge word and emits the actual primitive stream while tracking source identity, exponent and sign. The separate cost oracle imports none of that code. It scans original gates with old/new exponents and tracks fresh value-version labels on ADD writes, with separate powers on SCALEs. It reproduces all four complete histograms in all four orientations. The full PR949 forward per-ADD-clear histogram, not just its 73 minimum, is also reproduced.

A second arithmetic comparison executes all 144 winning mode/placement/sign streams on a checked exact 2^64 integer grid with nine arbitrary input columns. Every halving must divide exactly. A separate Fraction macro replay supplies the target matrix, including work erasure. Independent Gauss-Jordan inversion and transposition verify the four orientation identities. This proves the advertised finite witness endpoints; the written conjugation and cache invariants cover the entire class. We do not claim to execute all nonwinning streams as matrices.

Cache winners preserve the exact local prefix maxima of their corresponding per-ADD comparator: row-L1 peaks 12,8,10,12 and denominator depths 1,2,2,1 in forward/inverse/inverse-transpose/transpose order. These are scalar prefix facts, not full physical precision admission.

There are two winning magnitude placements each in forward and inverse, and one each in the transposed orientations. The original PR924 placement already attains each cache minimum; no priority for a new gauge witness is claimed. All literal streams, placements, complete cost histograms and prefixes are in CERTIFICATE.json.

Eleven controls reject missing entry COPY, missing exit CLEAR, work/source and work/target aliasing, stale cache after a source ADD, wrong cache sign after source SCALE, a missing source pin, duplicate/nonfinite JSON, Boolean cost metadata and incomplete enumeration. No correctness obligation is implemented with an optimization-removable assert.

## Credit, comparison and remaining work

Ross Richardson's PR949 proves 73 in a fixed per-ADD-clear gauge class and explicitly excludes cross-ADD coefficient work. This package changes that contract and confirms its old histogram. CubeJerry's PR922/924 supplies the contracted topology and scale witness; Sagar Thakrar's PR696 supplies the lowering; earlier PR839 and PR722/751 supply clear-state and shared-coefficient precedents. Caching and clear deferral themselves are not claimed as new principles.

PR984 defers a target scale through a historical JP8 interval and composes fan-in sharing; it neither supplies this contracted-factory census nor the same observation/cost class. PR975, PR981 and PR999 use different words or local mechanisms. PR1000/1010 concern T37 owner support, PR1004/1005 mutable-leaver/frame choices, and PR1012 hosted restoration accounting. The frozen selected record is still PR942, kappa0.001661960547713947; these pending research titles do not replace it.

This is a local scalar construction and exact finite policy floor. Physical COPY admission, production substitution, work availability at actual frame boundaries, complete provider/hosted cost and precision/tape invoices, recursive profile changes, outer assembly and inherited compiler/realization/analytic assumptions remain outside the result. Native tools and full supplier suites were not run. No selected pointer, predecessor package or upstream file changes. Attribution, disclosure and license are in NOTICE.md and LICENSE; executed checks are in VALIDATION.json.
