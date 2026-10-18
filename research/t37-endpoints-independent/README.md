# Code-disjoint check of the selected T37 endpoints and κ reduction

**Status: independent verification. No new κ; the selected result is unchanged.**
Track 75–84 (independent verification), assignment seed 76 (OS CSPRNG via Python `secrets`).
Base commit `2921874911956718fcaaaf9396fe8267b3cfa9f0`.

## What is checked

The selected record (PR942, κ = 0.001661960547713947) rests on three certified moment endpoints.
Each one is accepted on the 10⁻²⁴ grid and rejected at the next grid point:

| Model | Profile | Endpoint | G − 1 at endpoint | G − 1 at endpoint + 10⁻²⁴ |
|---|---|---|---|---|
| native complex | T37 complex, m = 73, W = 33,152 | 0.001664727258740678855772 | ≤ −3.362e−25 | ≥ +2.612e−24 |
| conservative complex (with the inherited surcharge) | same | 0.001664727255848707292019 | ≤ −1.533e−24 | ≥ +1.414e−24 |
| bit (PR589, with surcharge) | m = 64, W = 28,416 | 0.001733427039589844234749 | ≤ −1.599e−24 | ≥ +1.669e−24 |

From these, the selected outer reduction gives κ = 1661960547713947/10¹⁸ (complex-bound) and
the conservative κ = 83098027241579/(5·10¹⁶). PR991 replayed the selected T37 with both retained
engines but says that this replay is not code-disjoint. This package rechecks the arithmetic
chain from the hosted payload to κ **without importing or reading** `moment.py`,
`base_two_moment.py` or `outer.py`.

1. **The profile comes from the payload.** It is recomputed from the hosted T37 template as 333
   calls times the local paid profile (equal in both orientations), plus the idle children. The
   result equals the record's `complex_profile`, and its deficit 73·W − mass is 11,840.
2. **All three endpoints certify.** Logarithms come from prime decompositions:
   - ln 2 = 2 atanh(1/3)
   - ln 3 = ln 2 + 2 atanh(1/5)
   - ln 5 = 2 ln 2 + 2 atanh(1/9)
   - ln 7 = 3 ln 2 − 2 atanh(1/15)
   - ln 73 = 3 ln 2 + 2 ln 3 + 2 atanh(1/145)

   Each atanh tail carries an explicit geometric bound. Exponentials use Taylor polynomials with a
   Lagrange remainder, and intervals are exact rationals rounded outward to 2⁻³²⁰. Both retained
   engines reduce to a fixed range instead.
3. **The recorded engine intervals agree.** `ASSEMBLY.json` records six rows (an endpoint and a
   next point for each of the three models) with two engine intervals each. All 12 intervals
   intersect these enclosures. They are read as data only.
4. **κ follows exactly.** The reduction is s = min(c, (1−β)b) − 10⁻²⁷, then seven bootstrap steps
   from 384599/10¹⁰, then q = a₇(1−2η) and margin (1−η)q/(1+q), with η = β = 10⁻²⁴. It gives
   exactly the selected κ and the conservative κ. Each value is the largest 10⁻¹⁸ grid point
   strictly below its margin, and the complex side binds.

## Negative controls

| Control | Rejected because |
|---|---|
| C1 native endpoint + 10⁻²⁴ claimed as accepted | moment not below one |
| C2 one extra rank-one child | moment not below one |
| C3 dimension 72 instead of 73 | moment not below one |
| C4 bit model without the inherited surcharge | the next grid point is no longer rejected |
| C5 κ + 10⁻¹⁸ | not admissible under the margin |
| C6 exponential truncated at degree 2 | the enclosure is too wide, so the check fails closed |
| C7 corrupted assembly pin | digest mismatch |

C4 shows that the bit endpoint is exactly the surcharged value, as the selected assembly's model
control states.

## Reproduce

```sh
make t37-endpoints-independent-verify
```

The same check without make:

```sh
python3 -B research/t37-endpoints-independent/verify.py --work /new/empty/dir
python3 -B -m unittest discover -s research/t37-endpoints-independent -p test_package.py -v
```

The expected last line is `PASS_T37_ENDPOINTS_INDEPENDENT_REPLAY`, followed by 5 tests OK. It
takes about 2 s on standard-library Python 3.10+ with no network. `RESULT.json` is regenerated and
compared with the committed copy.

## Scope

This verifies one precise chain, from profile through endpoint certification to κ, with
independent code. Some things it does not do:

- It does not check the 47 outer inequalities beyond the binding margin; PR813 certified those
  for an earlier assembly.
- It does not check the bootstrap cutoffs, the owner map, the local word, the hosting, or any
  inherited all-size, realization, precision/tape, analytic or bit H1–H5 assumption.
- The surcharge term and the reduction formula are the selected assembly's model. They are
  re-implemented here, not re-derived.

This is not a formal proof of the multiplication theorem.

## Sources and pins

[`PINS.json`](PINS.json) pins the selected `ASSEMBLY.json` and `selected-result.json`.

- The bit record digest is the assembly's `PR589-EXPECTED.json` input.
- The T37 archive's hosted template payload is the assembly's `template_sha256`.

## Credit

- Jonathan Capalbo: the selected record (PR942).
- Chafik Boukhalfa, Jeremy Kothe, NewBArch and Hao Yan: its lineage.
- DreamingOfClouds and eumemic: the bit supplier (PR589, PR555).
- The two retained engines' authors: the recorded intervals cross-checked here.
- Earlier independent endpoint work on older checkpoints: PR960 (binomial enclosures), PR706
  (integer root bounds) and PR678.
- PR991: the scoping statement that motivated this check.
- Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude
  (Anthropic) via Claude Code. New material is Apache-2.0.
