# One-pass packets for all released G20 fused carries

The fused G20 carry now has a source-bound producer for the five-bit packet
used by the physical runtime rotation. It reads interleaved radix and low-digit
bits once. It uses no runtime division or modular inverse at the radix and
at most **78 bits of between-row state**, independent of input width. This
covers both bases, all 111 ports, both directions and all eight columns.

[PROOF.md](PROOF.md) proves the all-width construction. [producer.py](producer.py)
implements its bounded-state transitions. This is a constructive interface
result, not a new kappa or a complete physical caller. The change from the
serialized cut-state model is explicit interleaved input access.

## Evidence

[RESULT.json](RESULT.json) records 53,280 source-column cases, 49,449 exhaustive
active-coordinate inputs at radix three, seven 4097-bit cases and ten rejection
controls. All 729 distinct columns are covered. An independent rational oracle
uses the full modular inverse and does not share the streaming recurrence.
Thirty-eight actual physical-consumer runs check nineteen generated packet
values in both directions, including Q=125. They check the whole payload,
physical owner, private cleanup, descriptors, spectators and returned heads.

From the repository root, use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/g20-interleaved-carry-producer
```

The registered normal and optimized commands check every input hash and the
complete deterministic result. Direct replay is read-only and also works in
the official export without Git. `--write` explicitly regenerates RESULT.json.
No full predecessor scientific suite or selected frontier replay is required.

## Scope and next use

Each fixed column needs 9B input-symbol reads for B radix bits and emits five
bits. This cost is additional to the existing consumer's 468V transition bound.
The logical state bound excludes physical input access and an implementation
of the fixed transition logic. A literal tape producer, cache layout, head
returns, packet erasure and complete route/caller bill remain open. No runtime
speedup, global optimum, independent human review or formal proof is claimed.

AAAmirinu's [PR6241](https://github.com/CrocSwap/integer-mult-bounds/pull/6241)
already joins a supplied q=5 cache to the physical leaf for port9 inverse
column1. This result covers every source column with a different, interleaved
access contract; it does not replace that literal one-column implementation.
unpaidmoon's PR6296 keeps cache-tail retirement separate from that leaf.
Their physical work and the inherited PR5332 frontend retain their credit.

Family decision: continue only to a named physical interleaving/erasure binding.
This result resolves packet arithmetic. More random packet cases would not
resolve that remaining obligation. The selected result and its five framework
assumptions stay unchanged.

## Open next questions

Bind one actual low-cache row to the nine interleaved channels and include the
packet's final erasure. Start with the generated nonintegral Q=125 fixture and
emit the literal head movements before composing the high route and low commit.
The missing physical cache/ROW contract blocks a full supplier result.

## Credit and coordination

Base: canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8.
[Claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4945#discussioncomment-19362973).
The full overlap snapshot covered 409 open PRs, 5528 closed PRs, 6360 Discussion
records and all 8917 in-scope local notes. Arbitrary diffs and unpublished work
remain outside that search. All executable inputs are pinned to this base.

Credit Ali Romman PR5820, PR5841 and PR5849 for the released words, fused carry
identity and packet consumer; Nick Petalas for the q-adic identity and serialized
cut theorem; JoyboyBrian, Tekalign, David Arias, Charles Bethin, Jose Manuel,
ToikY and the retained G20/native/ROW authors. Binary carry comparison and
modular arithmetic are classical. New source binding, interleaved producer,
proof and checks: Ali Romman with substantial OpenAI Codex assistance; no
subagents. Apache-2.0. Original source files and credit lines are unchanged.
