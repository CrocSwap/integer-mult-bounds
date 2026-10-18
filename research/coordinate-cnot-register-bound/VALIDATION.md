# Local validation

At base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, using CPython **3.12.3**
and only the standard library:

```sh
python3 -B scripts/research_baseline.py
python3 scripts/research_package.py --package research/coordinate-cnot-register-bound --check-only
python3 scripts/research_package.py --package research/coordinate-cnot-register-bound
```

The baseline returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it checked
selected source bindings and arithmetic, not the selected supplier's cold
replay. The metadata check returned `PASS_PACKAGE_METADATA_AND_PINS`.

The complete registered replay passed in approximately **8.1 seconds** in
this environment (timing is not an acceptance condition). Its direct command
returned:

```text
PASS_COORDINATE_CNOT_REGISTER_BOUND minimum=6 dirty_registers=arbitrary census_r=2,3 symbolic_patterns=31 controls=14 no_new_kappa
```

The registered focused file ran **six tests**, all passing. Those tests cover
the exact noncommuting symbolic identity and a wrong-functional control;
fourteen boundary/scope controls; five receipt corruptions including an
integer-to-Boolean substitution; duplicate JSON fields; external receipt and
source corruption; and a byte-unchanged read-only minimal export under
`python3 -I -O -B`. The optimized replay performs the complete census and
symbolic checks, not a reduced smoke test. Temporary test exports are removed
after each test.

The direct replay compares complete formal and faithful-regular state sets
for `r=2,3`, checks their exact distance layers, the empty target intersection,
positive identity/one-swap controls, and the six-call formal witnesses. It also
checks 31 symbolic label patterns, 36 sign products and 4,704 scalar projector
conjugations. All deterministic results are in `EXPECTED.json`.

Not run: Lean, a selected-supplier cold replay, physical compilation, hosting,
common-label realization, precision/tape or analytic transfer. No independent
human proof review or hosted CI result is claimed. The all-register claim
rests on the written proof in `PROOF.md`, with these checks as corroboration.
