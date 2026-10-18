# Validation receipt

2026-10-12, Windows, CPython 3.11; standard library only.
Base: 66849e1475c930fd7732b1a0067ffee7e1e95f60.

Passed ordinary and isolated optimized execution. Output:

```
PASS_REUSABLE_CLEAN_CHECKPOINT 516 census cases; 1016 basis cases; weighted 20 -> 16; uniform54 2112; no new kappa
```

Coverage: 516 exhaustive price/cap cases through six factors; all 109 admissible
decorated trees through five factors; 1016 complete noncommutative basis cases,
including every independent source, target and dirty coefficient in the two
larger fixtures. Every case checks endpoint and exact signed-word inversion.
Small trees also check nonlinear zero-preserving leaves with arbitrary dirt.
Eight instruction/admission controls reject the stated failure modes.

A relocated standalone copy passes under isolated optimized Python. Altered
certificate cost and changed vendored source bytes both fail. Actual pinned
PR714 code freshly reproduces 2112 in the uniform54 control. Vendored proof,
notice and code match the committed SHA-256 pins.

The initially isolated run failed to import the local module because isolated
Python removes the script directory from its path. The verifier now inserts
its own resolved directory explicitly; the final isolated replay succeeds.

The repository selected-record checker passes on the complete clean checkout
of this same base: exact kappa, original source inventory and proof supplement.
The changed sparse checkout's selected record is byte-identical to its HEAD:
SHA-256 b3bf402f31a69bde0629936a9b569bed48281568d7b16d5fba120b5311ea1f53.
The selected source manifest, actual ASSEMBLY and maintainer review were read.
No selected-supplier cold replay, root-wide suite, PR628 rounded leaf replay,
remote CI, Linux execution or formal proof-assistant pass is claimed.

Publication overlap refreshed through PR787. PR714,730,744,758 remain distinct:
one clean root versus all-dirty scheduling versus the present sequential reuse
of one clean array. No pinned sprint issue was found. Posting permission for
the upstream repository was not established by the connected integration.
The credential-manager route successfully published PR788. PR784's newly
arrived scratch-dependent theorem concerns an all-dirty class and is credited
as concurrent context; its result is not imported or independently verified.
