# Preserve inherited limits in the primary baseline launcher

The baseline launcher previously tried to install `(1 GiB, 1 GiB)` even when its unprivileged parent had a lower hard address-space limit. That fails before the runner starts. This source successor keeps the original requested 1 GiB ceiling, selects a legal installed tuple using the existing inherited-limit calculation, and passes that tuple to the real child-limit callback. It records requested, inherited and installed limits separately and rejects parent-limit drift at terminal validation.

The [original investigation is PR #6321](https://github.com/CrocSwap/integer-mult-bounds/pull/6321). The immediate source is [the readable baseline in PR #6837](https://github.com/CrocSwap/integer-mult-bounds/pull/6837); the calculation is reused from [the candidate supervisor in PR #6830](https://github.com/CrocSwap/integer-mult-bounds/pull/6830). It is retained locally in the baseline closure so the baseline does not import candidate bootstrap code.

## Delivered change

`implementation/baseline/baseline_owner_v1.py` is a new source successor, with a complete byte-reversible diff in `patches/baseline-owner.patch`. Its logical module name remains unchanged. Original launch bounds, driver/stage pins, error ordering, custody and admission gates are retained. The protocol digest changes to the separately selected amended protocol; that full execution policy is an external prerequisite and is not supplied or granted by this package. The explicit amendment scope is documented in `PROTOCOL-AMENDMENT-DELTA.md`.

The original requested upper bound is still 1 GiB. For example, inherited `(128 MiB, 256 MiB)` now installs `(128 MiB, 256 MiB)`, rather than attempting a forbidden hard-limit raise. A lower inherited limit is not evidence that the full workload fits it.

## Verification and reproduction

From this directory, run:

```sh
python3 -B verify_source.py
python3 -S -s -P -B validation/test_baseline_as_successor.py
python3 -O -S -s -P -B validation/test_baseline_as_successor.py
```

The two control commands passed against these exact source bytes under a bounded local guard: 7 tests in each mode, including 440 finite feasible-set oracle cases per mode. Raw unittest results are retained in `evidence/`. The tests execute selected production definitions and the actual child callback, launch-field and drift-predicate source projections. They use the original pure schema predicate and an inert `setrlimit` recorder. They do not import or execute the baseline/candidate modules, launch a scientific child or mutate native limits through that callback.

The independent small-domain oracle enumerates feasible tuples and chooses the maximum hard/soft pair. Additional cases cover real-scale lower limits, zero soft bounds, invalid types/order, distinct requested and installed metadata, actual callback forwarding, protocol binding and parent-limit drift. Passing under `-O` confirms that these checks do not rely on Python assertions.

`MANIFEST.json` binds the complete package bytes other than itself. The source integrity check is separate from these finite controls and from production qualification. Git stores these inert source files as ordinary regular text; production freezing and the full source closure remain separate runtime prerequisites.

## Scope and open next questions

This repairs the baseline source's inherited-limit behavior and supplies changed-boundary controls. It does not establish workload fit, complete source/caller qualification, a performance gain, execution permission or a complete cost account. No scientific source, original oracle, sample order or selected bound changes.

The connected common-supervisor work remains necessary: real post-launch parent qualification, protected waiting-runner/query ownership, coherent deadline/retirement handling, authentic common-runner refusal reception, complete comparison and actual settlement. The [existing complete-outcome CLOSE source in PR #6762](https://github.com/CrocSwap/integer-mult-bounds/pull/6762) is the reuse candidate for settlement. A real source-associated environment, full resource/funding bill and original prerequisite outcomes are still required before execution. Do not substitute these projection controls for those obligations.

The smallest next check is to adopt this source successor into the fully pinned baseline owner/receiver closure and independently review its real caller together with the common-supervisor changes. The old baseline and all failed evidence remain unchanged.
