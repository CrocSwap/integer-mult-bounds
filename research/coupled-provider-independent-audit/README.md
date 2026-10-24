# Independent coupled-provider and closure-budget audit

This focused review accepts **#5402 as a partial coupled provider**, supplies a conditional budget for closing it, and records a companion bounded review of #5376's Clifford proof/certificate implementation. It supplies no completed consumer, no autonomous credit for the eight coupled H outputs and no new κ.

The candidate heads are #5402 `3348fccea855082786d5f0fc5558b73d4974e745` and #5376 `848cdce9003262c4b6e02ec4558f302e4fae56ad`. Canonical main at assignment is `1ec1119972c9aefe42525172d07b332fcff81cb4`. Raw commit/tree/blob membership proofs are vendored under `custody/`; the older #5376 base and its missing non-runtime contributor document remain explicit in that provenance. These side-head objects are evidence, not publication-history parents.

## Accepted component and remaining interface

The independent checker derives the actual early cache rows and both basis matrices from the original source, replays 632 arbitrary original inputs and nine arbitrary owned inputs, checks all nine final owned zero rows, and verifies 1,240 phase-sensitive physical identities. It compares complete Pauli action and a full zero-state phase anchor. Its partial block is

```
X = D x - R y + R W h
Y = D y
H = D(h - Z y),     ZW = 14 I8,     WZ = I-C.
```

The eight H outputs retain independent Y terms. Only the other 400 helpers receive autonomous credit. Ordered native words, explicit charts, all original directions and all owned fields remain part of the contract. The exact paid profile is `{1:2193,2:412,3:510,4:127,5:40}`. Unchanged native/helper implementations are inherited from the pinned source; this review does not flatten their entire physical tape realization.

The original semantic controls cover endpoint/basis mutation, ownership, phase, order, false zero retags and false autonomous credit. The cache-source substitution is a frame-contract rejection. An additional legal same-chart `SCALE -1` after the actual cache COPY reaches the native algebra and rejects because a required zero row becomes nonzero. See `reports/algebra/SAME-CHART-CACHE-MUTANT.json` and the raw root run.

## Conditional closure budget

The budget lane reconstructs the complete #5398 eighteen-body comparator and requires exact agreement with the prior independent #5400 invoice. Its local paid/helper profiles already match the comparator. The deleted eight H8 plus eight H1 calls are savings against the original raw source, so they cannot be claimed again against this comparator.

Granting eight **new, unearned autonomous H8 targets per provider** gives 144 hypothetical targets. At `t=1-κ`, the exact comparison is

```
margin_new = margin_reference + 144*8^t - M(K) - M(L) + M(Delta).
```

K is added paid closure work; L is lost productive work; Delta is every other signed main/idle/caller change. All remain unknown until a typed caller is supplied. If K is exactly 144 H8 jobs and L=Delta=0, the signed histogram equals the comparator at every rank and hence at every t. Any further positive paid job without compensating targets makes the incremental moment worse. This is a conditional budget, with no universal controller obstruction or autonomous credit for coupled H.

The literal boundary inventory per provider is 17,917 ADD, 1,204 SCALE, 16 COPY, 40 CLEAR, eight whole-field swaps and 464 monomial maps. The exact inherited scalar tariff is 175,022 units, including 42 exterior boundary units; physical monomial work, closure, routing/storage, precision and compiler/outer funding remain open. The earlier checker failure used the wrong original-source subtotal (158,744 versus the actual 158,168). The failed raw receipt is retained as a diagnostic; final source and successful result are the corrected version. No failed construction claim follows. A later literal-scale audit found that the stored output `cache_scalar` already is the final factor. The earlier checker took its reciprocal again, yielding a conservative 16-unit overcount. `screen_v3.py` uses the emitted factor directly. Recursive profiles, field counts and moment budgets are unchanged; old results remain diagnostics.

The separate local-envelope checker derives exponent **18,996** in the author's maximum-over-fields Euclidean norm and **19,012** in the joint Euclidean norm across fields. The latter includes a factor of two for each of sixteen COPY gates; COPY is nonexpansive in the former norm. It bounds the literal one-provider abstract scalar/unitary transcript, all contiguous subintervals and all suffixes at a fixed width. Local residuals must be measured in the same stated norm. It does not supply coordinate-to-field residual conversion or complete caller precision, storage, movement or compiler funding.

## Companion Clifford review

`reports/clifford-proof/REVIEW.md` reviews the all-n criterion under fixed coefficients, exact phase-bearing dyadic Clifford operators, fixed programs and arbitrary roles. The trace alphabet, exact Gram identity, filter and eight-copy invariant supply the written implication. The finite oracle independently builds Fraction-pair matrices: 25 entries, four traces, seven conditional inners, 24 programs, 64 tiny tensor-width cases, seventeen witnesses and 68 rejected witness mutations. It also constructs the 96 one-axis matrices, modular Gram rank and Reynolds checks.

These finite checks support only their tested implementation cases. The literal witness checker certifies a negative nonzero entry; compact positive equality still relies on trusted exact expansion/trace/merge execution, shares expansion helpers and has no separate small positive proof receipt. We did not replay the complete #5376 provider programs, 7,000 recipe classes, 30,328 fusion census, or its six registered commands. The inherited five framework premises and physical/precision/stock/analytic recovery remain outside this bundle.

## Reproduction

Python 3.10+ and its standard library are sufficient on Linux/POSIX. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/coupled-provider-independent-audit
```

A Git-free, read-only export can run either registered wrapper directly, from any working directory:

```sh
python3 -I -B /absolute/path/coupled-provider-independent-audit/verify.py
python3 -I -O -B /absolute/path/coupled-provider-independent-audit/verify.py
```

Each command freshly authenticates every working input and raw origin proof, then serially executes independent algebra, the same-chart control, the corrected conditional exact budget, the two-norm local envelope and the bounded Clifford oracle. The frozen original root author normal/-O pair (51.350 seconds) is authenticated historical evidence only and is not rerun. `COMMANDS.json` declares the actual fresh schedule. Full stable mathematical result objects are compared with frozen receipts; only named runtime fields are ignored. The original main algebra receipt remains unchanged at `reports/algebra/RESULT.json`. Its derived `REPLAY-EXPECTED.json` adds only the authenticated SHA256 inventory row for the later same-chart control file: the unchanged main checker inventories every adjacent Python file, even this unused helper. `REPLAY-EXPECTED-PROVENANCE.json` records that exact transformation, and the source guard requires full equality to the original object plus that one row. No mathematical or other provenance fields are dropped or replaced from fresh output. Fresh outputs and logs go to a private temporary tree; `--output /outside/package/REPLAY.json` selects a new receipt path. `--bindings-only` performs custody/input checks without scientific execution.

The wrapper re-executes through a built-in-only `sys`/`posix` isolated bootstrap, pins its helper/manifest bytes, rejects symlinks, hardlinks, undeclared files and bytecode, and verifies source bytes again after replay. Local imported Python source is loaded from authenticated private scratch, with a fresh cache path. Mathematical engines remain byte-for-byte frozen. Both wrapper modes deliberately compile scientific source at **optimize=0** so assert-based oracle checks remain active under wrapper `-O`; this does not claim an unprotected direct `-O` run of the assert-based oracle. Standard-library loaders are unchanged. The exported wrapper is the trust anchor; hashes provide integrity and origin binding, not a formal proof kernel.

## Open next questions

1. Emit one portable typed closure: exact A/S or alternative operators, their ordered physical words/charts, helper-tail updates, arbitrary-input/owned endpoints, and all added paid/lost-target terms. The reported private continuation is not a replayable input.
2. Test that closure against the complete signed histogram and ordinary/precision/compiler ledger. The conditional 144-H8 cancellation identifies a useful stopping test before another large search.
3. For compact positive Clifford equality, supply a small independent positive proof receipt and an explicit conversion contract for native versus dense witness schemas. Keep it separate from the bounded negative-witness checks.

Construction and predecessor credit remains with Ali Romman and the source-pinned native, provider, controller, Clifford and compiler contributors. The independent dyadic and exact-price engines retain prior attribution. This independent audit is Chris R/Clear1nsight with substantial OpenAI Codex assistance; it claims no independent human or formal-kernel acceptance. New material is under Apache-2.0. The current acceptance record is indexed by `reports/acceptance/README.md`: the corrected-budget/envelope and same-chart-control addenda supplement the preserved original review and gate map.
