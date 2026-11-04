# Exclusive fields reduce the complete selected scalar bill

Keep two fields in the existing staging buffers across adjacent ADD/COPY
events. Their owner slots stay zero until eviction. This removes repeated
physical acquisition while preserving a complete owner tape at every SCALE,
native, INIT/CLEAR and final boundary.

At W=64 the complete scalar bill falls from
`1236161936D - 5196390` to **`800847760D - 5118198`** for every positive payload
dimension D. The saving is **`435314176D - 78192`** operations, about 35 percent,
with the same four tapes, 256D staging bits, one carry bit and two payload
control bits. All transfer, local-circuit, rewind and flush costs are included.
The 7936D physical bit-reset requests remain explicit and unimplemented.

[PROOF.md](PROOF.md) gives the exclusive-owner invariant and exact policy
class. [POLICY.json.gz](POLICY.json.gz) contains the complete affine potential
certificate and attaining route. [RESULT.json](RESULT.json) records the cost,
cache statistics and literal physical checks. The minimum is for this stated
no-prefetch policy; it is not a minimum over all physical scalar compilers.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/p104-exclusive-field-cache
```

Both registered modes are read-only. `verify.py --write` explicitly regenerates
the policy and receipt. Main-source and exact predecessor bytes are checked
before import. ORIGINS.json retains original commits, paths, blobs and hashes;
no side-branch checkout is needed. Normal/optimized registered replay,
committed bytes/modes, official export and read-only Git-free replay are checked
before publication. Full-history preflight is not run in this shallow checkout.

The independent ownership checker covers every selected event. The complete
scalar trace checks exact arithmetic and all prefix records using explicit
native-grid and reset stubs. Literal windows cover all 43 templates at D=1,2,
all cache hit counts and each external boundary type. Physical windows check
bit-circuit equality; the full scalar trace separately checks arithmetic
preconditions. Five controls reject incorrect potentials/totals, a missing
acquisition, an incomplete boundary flush and aliased tapes.

## Limitations

The native and reset bodies are not implemented. Initial layout construction,
uniform encoded-D control, complete numerical/native admission, supplier
funding and outer transfer remain open. The all-D result is a family of
compiled W=64 schedules. It is not a uniform multiplication theorem, practical
runtime measurement, independent acceptance, new kappa or frontier change.
SCALE currently flushes the whole cache; the policy does not hide this cost.

## Open next questions

Can a resident SCALE field use a same-ribbon paired circuit without a complete
flush? Emit that physical circuit and compare the full transition with this
certificate. Its real and imaginary records share one ribbon, while the
inherited circuit uses separate ribbons. Native/reset implementations and
uniform control remain separate obligations. Recheck overlap before taking
any next scope; this contribution reserves none of them.

## Coordination and credit

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19365209).
Canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8
and current handoffs/PRs were checked before work and submission. Cached local,
PR and Discussion searches found the released predecessor's next question;
the older closed-PR snapshot and unpublished work remain coverage limits.
TASK.json preserves the original card and changed physical return contract.

Credit PR6527 for the complete owner-staging interface and baseline; PR6513 for
physical control caching; PR6511 and Nick Petalas for the scalar circuits;
Sagar Thakrar / PR3241 for metered tapes; DreamingOfClouds / PR6030 and all
retained native/compiler work. Classical caching, exclusive ownership and
dynamic programming retain their credit. The predecessor notices remain in
inputs. Ali Romman with substantial OpenAI Codex assistance; no subagents.
Apache-2.0.
