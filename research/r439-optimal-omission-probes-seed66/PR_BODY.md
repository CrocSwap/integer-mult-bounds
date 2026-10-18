Two fixed binary inputs detect all 5,563 single elementary ADD omissions in
the frozen PR967 D word under complete 661-output observation. One cannot:
three gate-input forms are x185, x188 and x185 XOR x188. Independent literal
execution checks every complete mutant; reverse-prefix pullback checks the
lower-bound forms.

This adds an optimal compact diagnostic suite to the credited PR1017 syndrome
atlas. It also provides a concrete two-omission error that passes both tests
but changes 27 target outputs on a singleton input. The guarantee is therefore
explicitly limited to exactly one omitted ADD. PR762's optimal ten-test suite
concerns a different radius-three coefficient fault model.

Reproduce with `python3 -I -O -B research/r439-optimal-omission-probes-seed66/verify.py`.
Expected: `PASS_R439_OPTIMAL_OMISSION_PROBES minimum=2 faults=5563 forms=761 controls=12 pair_counterexample=1 no_new_kappa`.

Exact source pins, complete typed certificate comparison and 12 rejection
controls are included. Native/full-word hosting, precision and outer assembly
were not executed. No new kappa or selected supplier; inherited obligations
remain. Prepared for @woklerx with substantial OpenAI Codex assistance,
Apache-2.0; no independent human-review claim.
