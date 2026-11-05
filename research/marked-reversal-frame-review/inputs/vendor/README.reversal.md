# Reverse the literal paired DDG without a visited-state log

For the fixed `(1,1)` denominator13 pair in [zxv's PR6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072),
the actual312-state DDG has a unique inverse edge when the consumed coin and
predecessor phase are retained. This package supplies that inverse and a
pathwise output-copy/cleanup protocol: retain the two-bit output in a disjoint
XOR accumulator, restore the original tape cursor, clear the controller and
stopping counter, and leave the resident input tape unchanged. **No per-step
node history is required; the stopping counter and transcript are required.**

The source-bound result is logical reversibility on every terminating path,
not a physical sampler, fixed worst-case storage, freshness after output
retention, or a speedup. The input pair must be fixed before sampling. The
selected frontier and its five framework assumptions remain unchanged.

## What changed

PR6072 proves the exact product law and optimal expected fair-bit count while
leaving reversal and stopping records open. Its source leaf overwrite loses
phase: literal states0 and1 both return leaf0 on coin0. Keeping phase (or
deriving it from the stopping count) resolves that collision. The inverse
formula uses `q=next_node+sum(digits)` for an internal child, or the leaf's
unique digit slot for a leaf, and recovers old node `(q-bit)/2`.
[PROOF.md](PROOF.md) gives the full arbitrary-path induction, counter/phase
wrap, output retention and conditional physical bill. This is a refined
`formal-interface-lemma` task, proved in prose with exact executable source
bindings, without a formal proof assistant.

The protocol performs T forward and T reverse transitions, using the same T
resident transcript bits. It uses O(log(T+1)) controller/counter storage beyond
fixed table/scratch and the transcript; T remains unbounded. For this source
pair, expected traversed transitions are exactly twice
`9960277917013927549978/4649714690825496825793`.
An explicit scan implementation charges2496T fixed-record visits plus counter,
phase, addressing and tape costs. The source's702-byte table is not claimed
to include that implementation's extra phase records or machinery.

## Exact retained sources and credit

`vendor/paired_sampler.py` and `vendor/README.source.md` retain byte-for-byte
PR6072 head`9011bf83e85ecd0443c789cf03259442f750877d`, by zxv with substantial
OpenAI Codex assistance, Apache-2.0. [vendor/ORIGIN.json](vendor/ORIGIN.json)
records their original paths and hashes. Only `make(1,1)` is invoked; its
144-pair `main` is never called. These retained files have their own commit in
this branch and source pins refer to that reachable retention commit, so cold
replay does not depend on an unmerged external Git object. No synthetic history
merge or predecessor modification is used.

The classical DDG method, predecessor proof and their credits remain in the
retained README. JoyboyBrian, with substantial OpenAI Codex assistance,
prepared this scoped inverse/protocol and verifier. Apache-2.0. Nick Petalas's
stochastic-prefix context and the JoyboyBrian#5069/#5037 inverse lineage retain
credit; their scientific replays are not imported or repeated here.

## Evidence and reproduction

```sh
python3 -I -W error -B research/paired-ddg-reversal/verify.py
python3 -I -W error -O -B research/paired-ddg-reversal/verify.py
python3 -B scripts/research_package.py --package research/paired-ddg-reversal
python3 -B scripts/check_research_commit.py --package research/paired-ddg-reversal --check-source-history
```

The standard-library verifier checks all624 inverse edges and624 wrong-bit
rejections,1022 terminating literal ten-bit tapes at a nonzero cursor with all
four accumulator values, and315 terminating paths through one/two phase wraps
up to T=314. It also rejects wrong counter, cursor, phase and output labels,
a finite surviving tape, and records the concrete phase-free collision.
The bounded paths validate implementation and failure controls; the arbitrary
terminating-path claim follows from the written edge-inverse induction.
No Monte Carlo or full historical catalogue replay is used. Direct verification
is read-only and Git-free once this package is exported. Registered commands
exercise normal and optimized modes; explicit checks remain active in both.

Canonical base is`721c03822c421b7f7fcbb2598993b947c4d88419`, priority8.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/6073#discussioncomment-19234412)
sets this exact task. Root coordination searched355 open PRs,5737 Discussions
and8348 local records on2026-10-28 UTC; coverage is not proof of novelty.
The public PR6072 head was rechecked before implementation. Later pair selection
belongs to another task; this package does not search for an actual caller.

## Open next questions

Can one physical tape/table service implement the explicit scans, counter
allocation and cursor restoration with a complete uniform tariff? Begin with
one fixed `(1,1)` service and the2496T record-visit bill in the proof, retaining
address movement and unbounded stopping. The physical service is the blocker.

Can an actual caller supply a nonadaptive pair and independent input tape
conditional on its retained outputs? Bind one stage and its randomness lifetime
before reusing the cleaned transcript. This proof restores bits but does not
restore their independence from the retained sampled decision.
Structured questions are in TASK.json. No new kappa or full multiplication
theorem, independent human approval, Lean or Docker result is claimed.
