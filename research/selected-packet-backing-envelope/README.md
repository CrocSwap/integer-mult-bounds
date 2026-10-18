# A complete named-array envelope for the selected packet loop

This closes the **packet-loop cut** portion of [Ross Richardson's PR2874
handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18965395).
For Jose Manuel/jmbarrancoml's unchanged PR2697 caller, the exact maximum
of its explicitly named packet/prefix backing arrays, over an entire successful
loop with at least two primitive passes, is

```
M = K + (2N+1)F + 4 + D + 2Q + max(Q,F).
```

Here N is the positive number of prefixes, F their positive payload size,
K the actual borrowed packet backing, D the actual directory backing, and
Q the uniform fresh prefix backing. Backing lengths include LEFT and erased
retained entries. The [proof](PROOF.md) specifies the successful-source,
freshness, alias, native factory and throughout-action retained-length premises.
This is a named-array component, **not total caller memory or a physical tape
allocator theorem**. The selected frontier is unchanged; no new kappa is claimed.

PR2874's prefix-return maximum is recovered exactly. Output-copy completion
contributes a second maximum, larger by F-Q when F>Q. This extends PR2874's
explicitly restricted result; it does not identify an error in that result.
For example, N=2,F=9,Q=4,K=19,D=7 gives prefix peak 87 and copy peak 92. The factory right-hand-side transient is also covered. Unlike the credited
PR2731/PR2743 bounds, this metric retains blank backing and prefix records.

If all action-private arrays, including the pending returned result and
excluding every caller array, have simultaneous backing at most A, a
source-bound composition is

```
caller + action <= max(M, K + 2NF + 3 + D + 2Q + A).
```

It is generally an upper bound, not an attained maximum. In particular,
`A <= F+1+max(F,Q)` suffices to stay within M. Adding A to M would combine
peaks from different phases. Endpoint restoration alone is insufficient:
the borrowed arrays' backing identities and lengths must remain fixed
throughout the action. The checker includes a counterexample to dropping
that premise.

## Evidence and replay

```sh
python3.12 -B scripts/research_package.py --package research/selected-packet-backing-envelope
# Portable, no Git/network/third-party modules needed:
python3.12 -I -B research/selected-packet-backing-envelope/verify.py
python3.12 -I -B research/selected-packet-backing-envelope/independent.py
python3.12 -I -B research/selected-packet-backing-envelope/test_verify.py
```

[RESULT.json](RESULT.json) records 99 finite cases and 693 each of the
prefix-return and output-copy cuts. The primary checker executes unchanged
packet-engine, reader, copying and clearing source, sampling their line,
constructor-return and write-return transitions. Ninety synthetic copy-action
cases cover N=1,2,4, F<Q/F=Q/F>Q, padded borrowed backing, and explicit private
scratch; nine real sign-action cases cover Z/3 fibres. The sign cases check
caller backing and output permutation, **not native action-private storage**.
The layouts and record bodies are synthetic; this is not selected GL64 or
catalogue admission. The separate arithmetic census corroborates the written
lifetime proof but does not replace it. See [VALIDATION.md](VALIDATION.md)
for exact commands, environments, negative controls and review coverage.

The loader authenticates exported bytes and rejects preloaded source modules;
it compiles authenticated bytes directly, avoiding stale bytecode. All 23
PR2697 source exports and the manifest are retained unchanged from PR2874.
[runtime.py](runtime.py) is reused from that predecessor with an attribution
header update. [SNAPSHOTS.json](SNAPSHOTS.json) records original Git blobs,
SHA256 hashes and paths. Source integrity is distinct from mathematical proof.

## Open next questions

1. **Instantiate A for native ADD/swap/sign.** Bound simultaneous retained
   private arrays, including cleared buckets and pending results, at actual
   action cuts. Start with `bitstream.sign_address` and its nested digit and
   translation passes; preserve the caller identity exclusions above. This
   determines whether the new interface fits without increasing M. Existing
   nonblank-content or traffic bounds do not by themselves supply A.
2. **Join the remaining caller owners at these same cuts.** Add Program,
   arenas, count/control and continuation tapes, closed preflight internals,
   event/layout metadata and outer payload owners by backing identity.
   Then prove last-borrower erasure, placement and reuse. These components and
   physical obligations remain separate; repeated Python allocations do not
   establish fixed physical tape reuse.

No failure cleanup, recursive-caller transfer, full selected cold replay,
physical compiler, formal proof kernel or independent human review is claimed.
The native private-array bound is intentionally an uninstantiated parameter.
This session stops at the component; it does not expand the mechanism family.

## Sources, overlap and credit

- Jose Manuel/jmbarrancoml, [PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697),
  `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`: unchanged first-range caller and
  retained framework/source lineage; original [NOTICE](sources/pr2697/NOTICE.md).
- Ross Richardson, [PR2874](https://github.com/CrocSwap/integer-mult-bounds/pull/2874),
  `08dd02bd8d8b1fadc5fe8589c2d2875d21fe5fce`: exact prefix-return cohort,
  authenticated portable exports and loader, field-producer / Program-acceptance
  predecessor handoffs. Its result is corroborated, not claimed anew.
- starship-s [PR2731](https://github.com/CrocSwap/integer-mult-bounds/pull/2731)
  and Nick Petalas [PR2743](https://github.com/CrocSwap/integer-mult-bounds/pull/2743):
  distinct nonblank payload and complete-node data-content bounds.

New work: kumagi, with substantial OpenAI Codex assistance, including two
separately delegated AI lifetime derivations and a separate checker review.
Apache-2.0; predecessor notices and license retained.
[Canonical claim and handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18965863).
Task selection, exact base, overlap coverage and limitations are in
[TASK.json](TASK.json). Other agents' sign-traffic and physical-wrapper
investigations are separate from this backing-array interface.
