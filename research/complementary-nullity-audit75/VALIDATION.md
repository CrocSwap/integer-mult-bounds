# Executed validation

Windows, CPython 3.14.5, Python standard library only, 2026-10-13. Exact base:
`2921874911956718fcaaaf9396fe8267b3cfa9f0`.

| Command | Executed result |
|---|---|
| `python -I -B research/complementary-nullity-audit75/verify.py --write` | PASS; generated full finite receipt |
| `python -I -B research/complementary-nullity-audit75/independent.py --write` | PASS; generated exact source kernel receipt |
| `python -I -O -B research/complementary-nullity-audit75/verify.py` | PASS; 11,232 matrices, 404,352 block pairs |
| `python -I -O -B research/complementary-nullity-audit75/independent.py` | PASS; 4,096 source subblocks, 10,240 transported basis vectors, source ranks 2,4,2,4 |
| `python -I -O -B research/complementary-nullity-audit75/test_package.py` | PASS; eight mathematical and five immutable-package controls |
| `python -I -B scripts/verify_selected_result.py` | PASS; selected kappa 1661960547713947/1000000000000000000 unchanged |
| `git diff --cached --check` | PASS before commit |

The two checkers use different arithmetic methods: explicit F3 cofactor
inversion/direct minor rank versus rational RREF and kernel transport. They
share only source-pin/literal helpers; no predecessor arithmetic is executed.
The source receipt's literal A, rational B, block ranks and regular rank-one
restrictions are corroborated. The finite and rational domains are separate
evidence and are not conflated with an exhaustive all-field computation.

Negative controls reject unswapped inverse complements, a missing rank
offset, singular whole matrices, a corrupted source inverse, duplicate
subset indices, an omitted kernel basis vector, dropping the second
complementary-invertibility hypothesis, and a float-for-integer receipt.
Package controls reject missing/extra source pins, a wrong base, wrong
source hash, and wrong frozen selected-snapshot hash. Controls use explicit
exceptions and remain enabled under Python optimization.

No NumPy, solver, compiler or proof assistant was required or installed.
Native/full supplier, cold ancestry, hosted CI and Lean were not run.
The source's valid written proof is corroborated, not corrected; no Fano
support/color hypothesis or additional branch exclusion is claimed.
All certificate writers completed before commit.
