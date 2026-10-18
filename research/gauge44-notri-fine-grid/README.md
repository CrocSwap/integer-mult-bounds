# Final-grid refinement of the pinned PR659 conditional witness

The final κ rounding grid can be refined from 10^-18 to 10^-24 without changing
PR659's construction, suppliers, bootstrap schedule or outer parameters:

| Quantity | Exact value |
|---|---:|
| PR659 κ | 0.001656193765416678 |
| Refined conditional κ | **0.001656193765416678434092** |
| Increase | 0.000000000000000000434092 |
| Refined rational | 414048441354169608523 / 250000000000000000000000 |

This **4.34092 × 10^-19 arithmetic refinement is not a new circuit or supplier**.
It depends on the pending PR659 construction; the repository's selected result
is unchanged. The substantially different local-primitive research from the
same sprint is [the multiway dirty echo](../cyclic-dirty-commutator-audit/ECHO-PROOF.md).
No κ gain is attributed to that primitive.

The pre-submission refresh found stronger concurrent proposals, including
[PR671](https://github.com/CrocSwap/integer-mult-bounds/pull/671) at
`16a27439d4ba1db451b6179c9475793529a485b6`, reporting 0.001658714981837397.
That construction was not audited here. This is a refinement of the pinned
PR659 witness, **not a proposed new frontier**; its independent fresh replay
and exact strict-rounding check remain reviewable evidence.

## Exact change and dependencies

The paid complex profile is
`{1:182448, 2:24912, 3:32976, 4:12816, 5:4032, 8:576, 48:2364}`,
with m=73, live width 7168, physical width 7682 and rank deficit 2560.
The complex lower endpoint is 0.001658941293644404576195; the cited PR589 bit
lower endpoint is 0.001733427039589844234749, including its surcharge.

Set eta=beta=10^-24 and s=min(c,(1-beta)b)-10^-27. Starting at
384599/10^10, perform the same seven iterations a <- (1-s)s + sa as PR659,
checking the same strict gaps and finite cutoffs. With q=a(1-2eta), the binding
margin is (1-eta)q/(1+q). `certify.py` changes only the final strict floor:

    grid = 10**24                     # formerly 10**18
    ticks = margin * grid
    kappa = ((ticks.numerator - 1) // ticks.denominator) / grid

All arithmetic is exact rational arithmetic (the pseudocode's final division
is implemented with Fraction). Subtracting one from the numerator also handles
an integral tick strictly. Both independent rational moment engines verify the
complex lower endpoint and reject the next 10^-24 tick. All 47 assembly
inequalities remain strict: 40 feasibility inequalities are identical and the
seven κ gaps decrease by exactly 4.34092 × 10^-19. The next κ tick, equality
with the margin, eta=0, beta=0 and beta=1 are rejected.

[SOURCES.json](SOURCES.json) pins the main base, PR659, PR635, the cited merged
PR589 source, the paid profile and all three arithmetic engines. The fresh
replay reconstructs the base word, removes K triangles, applies the layered
cold ends, and runs native local, wrapper, phase, independent 728-column linear
and cone, full global owner/admission, and independent pricing checks. It
rebuilds the complex construction. It **reprices the cited PR589 bit supplier;
it does not freshly rebuild that bit circuit**.

## Reproduce

From the repository root (standard Python and Git only):

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 4982f0ca66ffe0960b5a6451deb5b66b1039326b a6895a69f8ad98ab45777b03e9e6f48888c39f6f && python3 -B research/gauge44-notri-fine-grid/verify.py --out /tmp/gauge44-fine-grid-replay
```

Use a new output directory. Do not use `-O`; the inherited engines require
assertions, and this wrapper explicitly refuses optimized execution. The
verifier performs no network access or tracked-file writes. Expected final line:

```text
PASS_FRESH_PR659_AND_FINE_GRID 0.001656193765416678434092
```

The recorded fresh run completed all eight stages in about 186 seconds on
Python 3.14.7/macOS arm64. [evidence/CERTIFICATE.json](evidence/CERTIFICATE.json)
contains exact endpoints, bootstrap cutoffs, all 47 slacks and negative controls;
[evidence/REPLAY.json](evidence/REPLAY.json) records the full run. Log hashes in
that receipt identify that run only; timing and paths may differ on replay.
Regenerated compression bytes are not an equality test for the mathematics.
The source reconstruction's canonical word-content checks are retained.

## Scope and credit

The all-size compiler, common-label and mutable-source realization, whole-call
hosting, precision/tape/exact recovery, analytic transfer and bit H1–H5
assumptions remain inherited and conditional. A certificate is not a formal
proof of the full multiplication theorem or a practical multiplication speedup.
The complex endpoint currently binds this witness; eliminating that bottleneck
alone would still leave the cited bit endpoint near 0.0017334, far short of the
ambitious κ>0.01 target. Both suppliers need structural advances for that goal.

Credit **jeremykothe2** for PR659 and PR635, **icekylinx** for the PR645 gauge44
construction, **jaymosley07** and **jeremydiviney** for PR653/658 owner-packing
methods, **chafreaky** for PR619's prior use of finer outer grids on a different
fixed family, **DreamingOfClouds** for
the PR589 bit supplier, and all authors retained by those packages' NOTICE and
UPSTREAM-NOTICE files. This package does not claim their circuit or proof work.
The outer engine additionally credits **eumemic**, **icekylinx**, **Zhihao Chen**
and **hipotures**; their source notices are preserved by using the pinned engine.

This refinement, fresh replay wrapper and audit were prepared for
**@androolloyd**, with substantial **OpenAI Codex** assistance, under Apache-2.0.
