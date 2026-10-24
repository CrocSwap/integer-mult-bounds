# Validation and exact scope

Local environment: macOS, CPython 3.12. All scientific commands ran sequentially under the batch's global `serial.py` lock. No original native verifier or controller replay was launched.

| Command | Result |
|---|---|
| `python3.12 -I -B research/coded-reverse-physical-pair-gap/verify.py --write` | PASS; first measured scientific run 0.57 seconds, then a final authoring replay passed below one second |
| `python3.12 -B scripts/research_package.py --package research/coded-reverse-physical-pair-gap` | PASS_REGISTERED_RESEARCH_PACKAGE, including normal and `-O` direct commands |

The first timing wrapper used `/usr/bin/time -l`; the verifier passed, but macOS denied that wrapper's optional `sysctl kern.clockrate` statistic. Its nonzero wrapper exit is not reported as a successful complete command. The later direct and registered commands exit successfully without that statistic.

The exact sparse signed witness, positive scalar-A fixture, phase and noncommutation controls, actual 112-owner modular pair with all eight fresh Gaussian axes, and owned-only cleanup control all pass. The receipt reports the residual's actual nonzero coordinate count. The normal/optimized replay uses explicit exceptions, so none of its correctness checks disappears under `-O`.

The added verifier's authoring gate is: (1) it protects the observable physical pair equality required by PR4940's proposed scalar-code substitution; (2) replacing physical `C` by scalar `A`, omitting the signed normalizer, commuting `C` through `Q`, or clearing an original helper is the credible failure; (3) PR4940's existing binding specializes `Q,D` to scalars and PR4933's normalizer/gauge checks do not test this literal next thin source and its x-only boundary; (4) no production export, test hook, shared-code change, or existing test modification is needed.

The source-head byte and ancestry checks confirm that PR4933 head `d969c458c24278e0fd37e5b4c0ff8a53a496b430` and PR4929 head `361f5d4100640177d6a983dd2f336021c75bfd5e` are ancestors of the canonical base and that the used mathematical source bytes match. The package's declared Git provenance itself resolves through the pinned canonical base, so no pending foreign object is required for replay.

Material limitations: the producer's all-input identity and autonomous helper transforms are inherited source premises; new wrappers use the pinned signed physical ABI. This is a local scalar-substitution gap, not a rejection of every noncommuting caller or the full PR4940 endpoint. Fixed-point odd division, complete native ordinary work, tape routing, compiler, full-controller cancellation, hosted CI and formal-kernel acceptance remain unrun or unresolved. No multiplication exponent or selected record changes.
