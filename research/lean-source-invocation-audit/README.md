# Actual R747 source trajectory and a single-host contract mismatch

This follow-up attempted to connect one actual PR442 invocation to the
existing whole-hosting `PhysicalContract`. **The direct wholesale comparison
does not fit that contract**, when it retains the same unmodified observations
of all other final data and realizes the source's declared residual semantics.
The missing physical-provider connection is not proved by this package.

The concrete problem is in the scope of our contract: stage 2, replica 0 moves
helpers onto many data families at once. Its helper 0 moves to family 507;
helper 3 moves to family 508. With 507 as the distinguished host and 508
retained in `R`, the old contract requires 508's output to agree in both
layouts. The declared hosted residual on 508 is nontrivial. This diagnoses
the proposed direct instantiation, not a flaw in whole-residual hosting.

The new unconditional Lean result is **execution of the actual 19,002-event
normalized source word on two concrete inputs**, including clean-copy guards
and the complete final bitset. It replaces an invented local word with the
literal source program for this diagnostic. It does not prove the endpoint
for arbitrary dirty inputs or establish physical frame lowering.

## Exact source selection

Source: CrocSwap/integer-mult-bounds PR442,
`4e16d001d505d4f21dd2bcfc44591f9be4c279bd`. The invocation is stage 2,
replica 0, active pair 0, forward, using the inherited R747 word.

| Helper / local register | Parent owner | Hosted owner | Local entrance / exit |
| --- | --- | --- | --- |
| 0 / 240 | Bank 9142, `[56,64)` | Family 507, child 2, `[16,24)` | Frame 0 / frame 1 |
| 3 / 243 | Bank 9145, `[56,64)` | Family 508, child 2, `[16,24)` | Frame 0 / frame 1 |

Frame 0 is the empty local subspace; frame 1 is the full eight-dimensional
subspace. The parent call does not name families 507 or 508. The hosted
call places 747 helpers on 317 idle data families. A physical owner includes
a cover class as well as a family: the witness refers to helper 3's one
stream `(508, d σ₃⁻¹)` in a fixed-cover invocation. It is not an identification
of all streams in family 508 with one register.

[invocation-source.json](invocation-source.json) pins both emitted templates,
the original binary records, frame/state files, generator sources, and exact
owner rows. The compact forward program SHA-256 is
`4ed9ed1f7756ea6ff2c299b61ed1dc3fe0fa5bbbb91b5170133596b452c8085e`.
[SOURCE-INSPECTION.md](SOURCE-INSPECTION.md) gives the source correspondence.

## What Lean checks, and what it does not

- [SourceWord.lean](SourceWord.lean) contains every source event, projected to
  `(opcode, x, y, coefficient parity)`. Frame moves remain in sequence but
  have identity **normalized scalar** action. The two inputs are zero and
  the unit bit at register 243. Both produce exactly the same complete
  988-bit state at exit, with the cumulative index/clean-copy/erase guards
  true. Register 987 is the source's initially zero temporary; it is not an
  arbitrary dirty auxiliary input. Python-generated checkpoints are guesses
  verified by Lean's kernel, then composed into the whole execution theorem.
- [ContractScope.lean](ContractScope.lean) proves that the original and
  relocated outputs in `R` must agree under the existing single-host contract,
  even when their auxiliary banks differ.
- [SourceWitness.lean](SourceWitness.lean) feeds the actual word's verified
  helper response into the source's **declared coordinate residual**. A
  payload distinguishing the two address halves at coordinate 16 is unchanged
  in the parent observation and changed in the hosted observation. The proof
  works over any address-coordinate type with two distinct values; no
  particular small prime is claimed to be admitted.

`direct_single_host_bridge_impossible` proves these two declared observations
cannot both be supplied to the old contract with the same unmodified retained
projection. Its `parent_endpoint` and `hosted_endpoint` hypotheses are explicit
physical-observation refinement obligations. They have **not** been derived
from physical instructions here. The theorem is therefore conditional on that
source interpretation, not a certified physical counterexample.

The independent Python checker binds every Lean event to the binary source
records and separately replays all 987 input columns, frame annotations,
and nine private-center lifetimes. Those broader checks are not Lean theorems.
Frame rank/label checks do not establish projector identities, subspace
nesting, owner injection, or physical route implementation. The emitted
template gives symbolic owner selectors and an isometry rule, not numerical
helper `σ` matrices. [REVIEW.md](REVIEW.md) independently checks these limits.

## Replay and regeneration

From the repository root, with the official Lean 4.33.0 executable installed:

```sh
python3 -B research/lean-source-invocation-audit/replay.py \
  --lean /absolute/path/to/lean-4.33.0-linux/bin/lean \
  --receipt /tmp/source-invocation-replay.json
```

The replay needs no network or Mathlib. It rebuilds the three pinned sibling
dependencies and four new modules in an empty directory with `-t 0`, checks
the transitive axiom closures of all named declarations, and rejects three
false controls. The generated source certificate takes about 40 seconds and
roughly 1.6 GB in this environment. Most of its supporting theorems are
generated checkpoint/composition facts, not separate mathematical discoveries.

For source binding, replay the pinned PR442 package into an output directory
using `python3 -B research/idle-axis-hosting/verify.py OUTPUT` from that source
checkout. Then run the following with the appropriate paths:

```sh
python3 -B research/lean-source-invocation-audit/check_source.py \
  --source-root /path/to/pinned-pr442 \
  --hosted-template OUTPUT/bit/GLOBAL-TEMPLATE.json.gz \
  --parent-template OUTPUT/parent/changed/bit426-source-centres/global/GLOBAL-TEMPLATE.json.gz \
  --states OUTPUT/parent/changed/bit426-source-centres/records/249-states.json \
  --frames OUTPUT/parent/changed/bit426-source-centres/records/frames.json \
  --records OUTPUT/parent/changed/bit426-source-centres/records/249-records.bin
```

The certificate itself can be regenerated independently:

```sh
python3 -B research/lean-source-invocation-audit/generate_source_word.py \
  OUTPUT/bit/GLOBAL-TEMPLATE.json.gz /tmp/SourceWord.lean
cmp /tmp/SourceWord.lean research/lean-source-invocation-audit/SourceWord.lean
```

The source parser and generator are outside the kernel trust claim. Source
hashes, literal-event comparison, review, and mutation checks support that
binding; the kernel separately verifies the resulting execution claims.

## Audit, required repair, and attribution

The overlap check preceded implementation. Main, PR397, PR442, PR448, PR505,
and Jacob Sussman's heads were unchanged; changes to PR473 and PR477 were
inspected without finding a new matching Lean provider. Existing
`DirtyWrapper`, `FramedXor`, PR397/430 interfaces, and OpenAI `WordScheduling`
already provide generic algebra and execution lemmas. This package claims
only the additional concrete source certificate and precise scope diagnostic.
Exact pins and bounded-search limits are in [overlap-audit.json](overlap-audit.json).
PR448's advertised gain remains unestablished and is not used.

A viable next source bridge must compare one family relocation against a
hybrid layout, extend the retained contract to multiple hosts, or prove an
explicit layout-dependent decoding and its composition. It must then prove
the actual frame/owner lowering and the required universal dirty endpoint.
Dropping family 508 from the observations would simply leave its final data
unverified. This audit does not rule out the listed repairs.

See [NOTICE.md](NOTICE.md) for attribution and assistance, and
[VALIDATION.md](VALIDATION.md) for exact replay scope. All work is local;
no source construction, price, or κ claim was changed or published.
