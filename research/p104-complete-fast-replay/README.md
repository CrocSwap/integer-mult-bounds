# Complete P104 verification with explicit fast engines

This package regenerates the complete PR6453 result through the published
native, forward-row and pricing engines. It does not read old native or physical
results as acceptance answers. The full scientific result and progress transcript
match the untouched source verifier. No new kappa or supplier admission.

Three alternating fresh-process pairs reduce median full-command time from
166.780543 seconds to 35.086879 seconds (4.75 times faster).
All six full-output hashes agree. BENCHMARK.json retains every sample and the
environment; BENCHMARK-SOURCES.json binds the executed code. The ranges are
154.06–241.90 seconds and 29.43–39.73 seconds. Other host work was present,
so these measurements are local evidence, not a universal speed guarantee.

The complete path includes source-word construction and regressions, all owned
lifetimes and scratch checks, the current and intermediate scalar words, all
799 transpose columns, 2,941 native maps, 208 main adapters, 7,488 physical
contacts, the caller and independent module, both price engines, compiler,
54 strict and four functional outer predicates, and every original corruption
control. RESULT.json binds the complete output and reports these quantities.

The source is PR6453, head b1a3e525793eca35c56324aa7ffd0b714cf606d4.
Component credit remains with PR6479 (native prefix/Gray evaluation), PR6501
(sparse integer forward rows), PR6505 (checked root certificate) and PR6507
(bounded outward log/exp intervals). They retain their source-specific proofs.
This result checks their full composition and total runtime; it claims no new
arithmetic method or component speedup.

PROOF.md and EDITS.json describe four explicit interface edits. The verifier
requires byte equality after those edits. The untouched source is the baseline.
The service object receives the newly generated word and local/native/physical
receipts. Imported classes and functions are not patched. Source archives and
all original authentication checks remain unchanged.

Run with CPython 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/p104-complete-fast-replay
python3.12 -I -B research/p104-complete-fast-replay/verify.py --compare-baseline
python3.12 -I -B research/p104-complete-fast-replay/benchmark.py
```

The registered modes run the full integrated source and require its exact
retained result and transcript digest. The optional comparison also runs the
untouched full baseline. That comparison is executed locally before publication;
it is not a skipped scientific obligation. The separate benchmark repeats full
baseline/integrated commands in alternating fresh processes. It includes startup,
imports, source authentication, archive extraction, all scientific execution and
serialization. No timing threshold is used in CI.

The five assumptions remain native_all_columns, owned_erasure, compiler,
precision_tape and analytic_recovery. No physical multiplier, independent human
acceptance, Lean or Docker result is claimed. The optional full-history preflight
is not run in this shallow checkout. Input bytes are retained in ancestor commits
and in the exported payload. No known fragile workaround is used.

Ali Romman with substantial OpenAI Codex assistance; Apache-2.0. PR6453 is by
Erwan L. with Claude assistance and builds on Rohan Arun's PR6417. Credit David
Arias, Cinna Davis, Gareth Davidson, Charles Bethin, Wentao Li, zxv, Cao Yifan,
Jacob Alan Sussman and the complete retained lineage. Exact notices and proofs
are in inputs. Current selected PR6030 and all shared code remain unchanged.

## Open next questions

Which remaining full-replay cost has the largest measured share? Profile the
integrated command outside the timing experiment. Any next change must retain
every scientific predicate and pass a new overlap check. See TASK.json.
