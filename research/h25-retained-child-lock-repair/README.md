# Retain child identity until group retirement and preserve the working error

The actual common runner in [PR #6864](https://github.com/CrocSwap/integer-mult-bounds/pull/6864) can consume its direct child before its final numeric process-group signal. The group number can then identify an unrelated owner. [PR #6866](https://github.com/CrocSwap/integer-mult-bounds/pull/6866) supplies the counterexample, public construction and conditional ownership argument. This contribution installs that construction into the connected source and both immutable stage recipes.

A consequential Pro review also found that the actual enclosing `science.lock` context could replace the working exception with a close exception. The corrected actual `main` preallocates separate error slots, closes a known lock handle once, retains the first working exception and its traceback, and raises the close exception only when there is no earlier working exception. An expected administrative exit code 1 is issued only after known successful lock retirement. A lock-close failure therefore remains visible on stderr instead of looking like an accepted quiet refusal.

Original investigation: [#6321](https://github.com/CrocSwap/integer-mult-bounds/pull/6321). [End-goal specification, PR map and contributor tasks](https://github.com/CrocSwap/integer-mult-bounds/pull/6321#issuecomment-6713710045).

## Exact source and changes

The source predecessor is #6864 at `c8f7bd582ffc1301b851dde2364c60f1636aac8b`; the adopted construction is #6866 at `fcba647106f3e2f08de1b39ebed04a13c0a6ef8b`. The repository base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

- The existing owner observes its direct child with `waitid(..., WNOWAIT)`, keeps a strong child reference, sends the final group signal while that identity remains owned, and makes one consuming wait afterward. It never sends another group signal after that wait.
- Fixed, preallocated custody slots retain working, signal, wait and capture-close failures without allowing cleanup to replace the first working failure. Entered operations with unknown completion stay unknown.
- The outer lock correction follows the same error-ordering rule and explicitly defers the original administrative `SystemExit(1)`.
- Both complete stage declarations, the actual supervisor's immutable runner SHA, queue pins, selected source packet, effect/command profiles and detached source manifest are rebuilt. Original factory/cwd/timer repairs are retained.
- Literal byte inverses relate the group correction to #6864 and the lock correction to the first tested successor. Other changes are selected-root relocation and dependent pins. Original scientific/native/compiler bodies, independent validators and all unchanged stage members are preserved.

`SOURCE-MAP.json` maps 61 source roles and seven profiles onto 66 distinct readable selected leaves. Role aliases share file identity. The detached manifest is supplied separately. Both stage declarations retain their 197-member inventories; unchanged scientific members and 44 historical control references remain at their exact predecessor locations rather than being duplicated. `.txt` suffixes make source bodies inert. The absolute paths identify the inspected subject, not a portable installation.

## Validation actually executed

Two distinct bounded control operations ran once each using Python 3.12, a clean environment, a 20-second outer timeout, two-second kill tail, 256 MiB address-space cap and fixed output limits.

1. Fifteen methods passed in normal mode (0.327 seconds) and optimized mode (0.306 seconds). Actual predecessor and successor source run against explicit inert process/wait/signal/clock/capture ports. Consuming wait releases the fixture identity; an unrelated next owner then exposes the predecessor's unsafe signal. The successor signals while owned and waits once afterward. Controls also cover bounded error/capture ordering, partial acquisition, uncertainty, observation failure, cap precedence and source/binding inverses.
2. Eight new methods passed in normal mode (0.547 seconds) and optimized mode (0.525 seconds). They reproduce actual outer-context error masking and exercise the corrected actual lock-owner/finalizer statements with one inert working-body port. They check all six retained errors, unknown acquisition, cancellation, expected-exit ordering, later wait-observation failure, actual queue stderr rejection, actual stale-runner/stage predicates and actual scientific/independent-validator inventory rejection. They verify the full changed graph and literal lock inverse.

The unchanged 15-method suite was not rerun after the lock-only correction. Its group function is byte-identical in the second successor; that identity is checked in the second operation. Recorded timings are fixture durations, not performance gains. Return-code fixtures are not execution of the original full optimized refusal.

Raw argv, output and outer resource records are under `evidence/`; exact tests and two-mode drivers are under `validation/`. They require the exact local source/predecessor graph named in their bodies. This archive does not promise a portable executable fixture replay. It registers no scientific replay hook.

Passive archive reproduction, from this directory:

```sh
sha256sum -c SHA256SUMS
```

This checks exported bytes only. It neither imports candidate code nor runs the scientific comparison. No actual `Popen`, group signal, file lock, guardian, compiler, native target, financial context or scientific workload was exercised by these new controls. The policy debit was 26 seconds per operation. Remaining recorded policy time is 23.109466521 seconds of the unchanged 2400-second cap; preparation, Pro, review, reporting, publication, final metadata and historical physical gaps remain `OPEN_NOT_ZERO`.

## Review and remaining obligations

`PRO-REVIEW.md` records the public-source consultation, its consequential premises and the enclosing correction. Pro did not inspect the unpublished complete successor graph. Codex inspected the actual correction, literal inverse, pins and executed controls. There is no independent complete-graph acceptance, human approval, proof-kernel result, authentic caller qualification, current host/native/configuration association or full baseline/candidate equality here.

The identity argument assumes the exact fresh-exec SIGCHLD/default-wait path, no automatic reaping, exclusive consuming wait ownership and strong child references. An integer returned by `Popen.wait()` alone is not an identity certificate. If signaling fails, the local blocking wait has no proved local completion bound; the existing outer deadline/owned-domain/guardian remains necessary. In-process error objects are not durable cross-process evidence if the runner dies. Complete descendant emptiness remains unknown, not established.

The complete source/helper/driver/native closure obligation, 52-helper/65-context acceptance, genuine primary baseline/comparison adoption, successful complete-outcome CLOSE, resource/funding admission and original complete normal/optimized outcomes remain open. This source prerequisite changes neither original acceptance criteria nor original completion credit.

## Open next questions

Independently review this exact changed runner, actual enclosing lock and both stage bindings against the public predecessor and #6866 identity premises. Carry the changed-binding and predecessor failure controls. Then reconcile the genuine primary baseline/full comparison from #6837/#6847 and the complete-outcome CLOSE owner from #6762 through the actual caller. Do not substitute fixture successes for genuine inputs or issue grants/receipts to make missing prerequisites appear satisfied.
