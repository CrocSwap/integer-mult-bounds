# One-target CRT scanner-mask consumption and disposal bridge

**Claim type: a narrow scanner-owned-mask interface, exercised in ten repaired-layer
invocations of the #4100/#4169 fixture. Partial: unpaid host key arithmetic and host
macro/inter-layer streams remain. No new algorithm, endpoint, tariff, κ or full closure.**

## Question

`research/pr4100-crt-repair-tariff` (#4328) requests composition of the hole mask, key evaluator
and repair ownership/erasure contracts. #4208/#4201 produce a mask on tapes; #4169 supplies
current-state reverse keys and the ten-layer caller fixture; #4328 already supplies the CRT
repair algorithm/tariff, but builds its `MASK` from a host `good` list and keys from
`T[inv_S[x]]`. #4377 supplies a counting proof, not a tape evaluator plugged into this bridge.

## What is joined (and run)

The replay makes **ten separate repaired-layer invocations** using the existing #4169 fixture
(#4100 `check_compact_crt.py`: five Beneš layers for padded moduli 3 and 5 over all 4096 labeled
payloads, then the five reversed). Within each invocation:

1. the **unchanged** #4208 `producer.py` builds the stencil from six unary geometry words
   `G,H,K,Y,J,B = 2,2,6,8,j,0` (exact `33H+25K+38Y-6G-J+12B+335` invoice asserted);
2. the **unchanged** #4201 `machine.transduce` scans it into the owned BAD mask
   (exact `8ML+15M+13L+18` invoice asserted; mask equals the source `good` predicate);
3. `bridge.py` consumes **that mask tape in place** — never a host good list: split by mask,
   key evaluated at marked addresses only, `L = 12` stable full-key radix passes over
   (payload, key) blocks, mask-driven reinsertion comparing the sorted key to the counter,
   physical erasure of mask, stencil, counter, good/bad streams and both buckets, head return;
4. recycled physical tapes must be blank with head at `LEFT` before the next layer
   (producer private roles are reused as good/bad/bucket roles).

Label 780 reaches address 777 after layer 5 and returns to 780 after the inverse five.
Every layer is also checked equal to the pinned table-based `check_compact_crt.layer`.

The macro/raw stream for each invocation and the payload handoff between invocations are
host-built Python adapters. Blank private-role reuse is checked, but the payload is extracted
and a new data tape is populated for the next invocation. This is **not an uninterrupted
all-tape caller**. The 4096-payload / 29,440-hole fixture and its forward/inverse endpoint
already occur in #4169; the added boundary is consumption of the scanner's actual mask,
marker-driven repair actions, and disposal/head-return gates.

## Exact-head comparison and retained credit

- **#2250 / #4328:** retain extraction, full `T(S^-1(q))` keys, stable two-bucket radix
  reinsertion and erasure as existing algorithms. #4328 supplies the CRT tariff; this
  package does not improve it or claim its asymptotic bound for this implementation.
- **#3055, `9dc841c9a101435fdd15e0f7623bf16b6d0363e9`:** Jose Manuel's
  [physical Compact proof §§4–6](https://github.com/CrocSwap/integer-mult-bounds/blob/9dc841c9a101435fdd15e0f7623bf16b6d0363e9/research/physical-complex-compact/PROOF.md)
  and [`compact_streams.py`](https://github.com/CrocSwap/integer-mult-bounds/blob/9dc841c9a101435fdd15e0f7623bf16b6d0363e9/research/physical-complex-compact/compact_streams.py)
  already implement encoded current-inverse keys, hole flags, physical two-bucket stable
  radix repair, destination checks and disposal. Its guard/key arithmetic is encoded;
  its fast bound uses superpolynomially long records, unlike CRT's `R = Θ(p)` regime.
- **#3608, `c6020096322012f7cc41236c3ac15a6b6cd3f8b9`:** Jose Manuel's
  [sparse XOR proof](https://github.com/CrocSwap/integer-mult-bounds/blob/c6020096322012f7cc41236c3ac15a6b6cd3f8b9/research/physical-sparse-xor-batch/PROOF.md)
  and [`sparse_engine.py`](https://github.com/CrocSwap/integer-mult-bounds/blob/c6020096322012f7cc41236c3ac15a6b6cd3f8b9/research/physical-sparse-xor-batch/sparse_engine.py)
  lower encoded variable source/target pairs and reuse #3055's physical repair, with
  complete owned-work return and a long-record resource argument. Neither cited interface
  consumes the #4208/#4201 CRT scanner-owned mask: that consumption/disposal boundary,
  not first physical repair or a new endpoint, is the narrow addition here.
- **#4169:** retain both current-state inverse-word keys and the exact ten-layer
  4096-payload / 29,440-hole caller credit, not merely inverse-key attribution.

## The unpaid point

`bridge.evaluate_key` pays the tape actions that read the address cells and write the 12 key
bits. The mapping address -> `T(S^-1(q))` is `key_subroutine.ReverseWordKey`: the ten compact
shears run in reverse at the current `y` (kumagi's #4169), then the ideal switch. It is plain
Python integer arithmetic, called once per marked address, with no inverse table, no address loop
and no good-set test; the verifier compares it with #4169's `Word.run(inverse=True)` on every
address of every layer. **It is not a literal tape evaluator and its cost is not charged.**
CRT.md §4's `E(p,ell)` remains a conditional allowance; #4377's counting proof does not
pay for or realize the host callback executed here. Within the repair, the remaining actions
are reads/writes/one-cell moves with finite-control branching; the macro and layer adapters
remain host code. An AST guardrail (review aid only) rejects host arithmetic, indexing,
length primitives and observer reads outside `evaluate_key` in the repair module.

## Evidence

`PROOF.md` instantiates the inherited repair argument for every geometry satisfying the
predecessors' facts and the key premise. `verify.py --part caller` replays the 10 layers (also receipts
`RESULT-caller.json`); `--part controls` runs the negative controls (`RESULT-controls.json`):
wrong keys (`ideal_of_current`, `inverse_only`, `stale_source`, `guarded_identity`) fed
through the real program on the actual layer and on a callable-source fixture; a mode whose key
equals the correct key at every hole of a fixture is reported as equivalent there, not as detected,
and each mode must be discriminated on at least one fixture; zeroed mask (zero key calls, wrong records); one hole unmarked;
truncated mask; over-marked good address (output right, one good key evaluation counted);
key evaluation on every good address; skipped sort; skipped clear of each of mask, stencil,
good, bad, counter, buckets; omitted head return; producer geometry mutants through the real
scanner; damaged source bytes rejected before execution. A skipped clear does not change that
layer's payloads (marker-driven reads) and is caught by the physical-blank gate; the README
and PROOF say so rather than claim the payload check catches it.

Exact per-phase action counts and the 12-bit-record weighted meter are in the receipts.

The existing author record reports execution in Python 3.12.14 passing the ten repaired-layer
invocations and all semantic controls. Across those invocations: 29,440 marked-key calls, zero good-address
key evaluations, 133,110,830 repair actions and 226,260,150 record-bit-weighted repair
actions. The producer uses 8,422 actions and the scanner 4,548,300. The 2,266,880 key-interface
actions are included in the repair total, not added twice. Key arithmetic is excluded.

The control receipt contains 24 detected violations and two distinct non-rejection outcomes:
the key-identical stale-source case and the correctly repaired but overcharged extra mark.
The callable parity source makes the stale-source mutant fail the actual hole-key check.

An independent OpenAI-family verifier reviewed the Anthropic implementation and ran both
isolated optimized replay commands, comparing the existing receipts. The parent then ran
the complete registered package, which reported `PASS_REGISTERED_RESEARCH_PACKAGE` with
`outcome=partial`. Partial refers to the unpaid tape evaluator and host macro/layer handoff,
not to an incomplete execution of this package's two commands. These are retained execution
records, not a new replay of this documentation/attribution change.

## Not covered

The macro `S`, raw post-macro stream and inter-layer payload handoff are host-built.
One target per layer, unary one-target geometry only; no many-target ordering, binary or transported geometry; no
`E(p,ell)` tape evaluator; no asymptotic `O(V)` claim here (the key premise and `L = Θ(p)`
calibration are CRT.md's).

## Live positioning and historical provenance

At the inspected canonical main `fbc9ea0249746acca4f504d4fda2b84e0e36cf0d`, the selected result
is the conditional #4470 construction, `κ = 0.00302015`, with priority revision 7 retained.
This side contribution changes none of that selection or its transfer obligations. The
package's historical base remains `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc` in `TASK.json`
and `SOURCES.json`; pinned predecessor bytes and receipts retain their original provenance.

## Reproduce

```sh
python3 scripts/research_package.py --package research/crt-mask-repair-bridge --check-only
python3.12 -I -B research/crt-mask-repair-bridge/verify.py --part caller
python3.12 -I -B research/crt-mask-repair-bridge/verify.py --part controls
python3.12 -I -B research/crt-mask-repair-bridge/verify.py --probe   # one layer, quick
```

Write receipts with `--write` (once). Standard library only.

## Open next questions

1. **Replace the key premise by a literal tape program.** *Why:* it is the only unpaid
   arithmetic inside the repair. *First step:* the ten reversed shears on the counter role for this geometry,
   plugged into `evaluate_key` and metered. *Blocked by:* a literal CRT-data evaluator (#4192 follow-up).
2. **Macro, many targets and transported geometry.** *Why:* the raw stream and layer hand-off
   are host-built. *First step:* the literal macro on the same data role. *Blocked by:* no pinned
   tape macro or many-target producer.

## Credit and AI disclosure

Cinna Davis (#4100/#4088, CRT.md and original caller); Hiroki KUMAZAKI (@kumagi, #4169/#4174,
current-state reverse keys and the exact ten-layer fixture); ToikY (#4195/#4201/#4208,
scanner, producer); Jose Manuel (@jmbarrancoml, PR2250 repair and #3055/#3608 encoded physical
repair); Ryanson Jonathan (@pinterbanget, #4311/#4328/#4329, CRT tariff and handoff);
unpaidmoon (#4377, evaluator counting bound); Douglas Colkitt/OpenAI and the NOTICE lineage.
This package adds the scanner-mask consumption/disposal interface to their contracts.
Prepared for codyw912 with substantial Anthropic Claude implementation and OpenAI
coordination/verification assistance, including this OpenAI-family scope/attribution edit;
no human or formal-kernel review. Apache-2.0.
