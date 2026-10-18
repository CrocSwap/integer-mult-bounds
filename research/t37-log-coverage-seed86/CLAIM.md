# T37 execution-log coverage claim

Claimed 2026-10-13 17:24 UTC. OS-random seed 86 selects verification
engineering under the user's 85-94 mapping. Cycle began 17:17:25 UTC;
verification and handoff start by 17:47:25 UTC; finish by 17:57:25 UTC.
Base main: `2921874911956718fcaaaf9396fe8267b3cfa9f0`, fetched and confirmed
fast-forwarded from CrocSwap. Prior checkout and branches are preserved.
Branch: `research/cycle04-seed86-t37-log-coverage`.

Three candidates were considered:

1. Check all T37 stage logs, including the eight native logs whose existence
   is not checked by the frozen final binder. Chosen.
2. Audit receipt scalar types in isolation. Deferred; type checks belong to
   the concrete stage-evidence admission boundary in the chosen scope.
3. Reduce repeated source hashing. Rejected without a demonstrated bottleneck.

Exact object: the four stage indexes and 34 logs in
`research/community-frontier942-audit/t37-replay.tar.gz`, produced by
Jonathan Capalbo's selected PR942 T37 construction and its pinned U8 ancestry.
Hypothesis: a portable supplementary evidence check can reject every omitted
log, including native omissions that the frozen native-stage predicates do
not inspect, while accepting the unchanged archived stage evidence.

Method: inspect the actual producers and final binder; bind their exact source
bytes; verify complete ordered indexes, exact integer success codes, required
log presence and each digest that the producer records. Demonstrate the
native omission boundary using the unmodified source predicates, with a
clearly stated component-level scope. Exhaust all single-log omissions and
run changed-log, sequence, type and source-pin controls. Do not equate a
receipt or a log with authenticated execution or a full theorem proof.

Deliverable: a small standard-library checker, reproducible archive audit and
exact control receipt, source pins, scope/credit/license documentation and
handoff. No mathematical improvement is proposed. The optimistic effect on
the complete selected invoice and kappa is zero. No stronger supplier or
kappa is assumed. No selected record, source package, or upstream file changes.

Coordination: immediately before this claim, checked all 753 open PR bodies
through #1058, recent repository comments and pinned issues. No pinned issue
or matching active claim exists, so this claim is local. Relevant existing
work includes #865's PR799 evidence contract, #851's bridge coverage, #991's
different T37 witness/payload controls and #1006's owner-audit bitmap speedup.
None covers this current T37 log inventory. The review ledger and retained
negative scopes were read; no closed mathematical search is reopened.

Stopping rule: finish the declared archive and control census; if useful
evidence or relevant checks fail, preserve the patch and an honest handoff.
At most one focused PR; refresh metadata and overlap before submission.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
New files are Apache-2.0; predecessor notices and source licenses remain.

## Completed result, 2026-10-13 17:42 UTC

Published one focused PR: https://github.com/CrocSwap/integer-mult-bounds/pull/1073
and attached it to the originating chat. The archive passes at 34 logs,
26 producer-recorded digests and eight native presence-only logs. All 80
declared negative controls reject. The original native-stage source slice
admits all eight native-log omissions; native content changes deliberately
remain accepted by the supplementary checker while changing its observation.
This is scoped evidence-coverage work, not a mathematical counterexample.

Both tested Python runtimes, optimized workers, relocated minimal closure,
public CLI controls, 25 selected-record tests, three replay-coverage tests and
the selected-record check pass. Full receipt SHA-256 is
`e834d7037dee9071f14b0c0a3194c84c8f036d1160ca512f84d2a578992170c0`.
Final overlap checked 739 open PRs through #1072 and recent comments.
Refreshed upstream `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf` retains all
12 consumed/context pins. No pinned sprint issue exists, and neither requested
Codex label is available. This is the claim's single result update.

No full supplier or invoice replay, full make verify, Linux CI result or new
kappa is asserted. Selected sources, prior branches and upstream are unchanged.
Verification and handoff began by 17:30 UTC, before the reserved final interval.
