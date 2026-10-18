# Two mutable snapshots: an executable record-level bank boundary

**Finite exact record checker and lifecycle substitution lemma; no physical
supplier admission and no new kappa.** This package takes the *unchanged*
PR1704 two-copy scatter and fills its executable-record handoff: it emits two
explicit temporary identities in the real six-int32 record format, checks every
rational frame transition, and compiles a separate C++17 interpreter that checks
snapshot equality at every ERASE and the complete 5/9/11-stage formal bank maps.

The new executable admits restored mutable snapshots rather than silently
turning off the inherited immutable-temporary test. Its positive source control
is the original single-slot PR1062 stream. The main countercontrol omits a
restoration: **all persistent outputs still agree if ERASE is treated as blind
deletion, but both new interpreters reject at the chronological ERASE**.

This is not a second claim to PR1704's 120-ADD saving or matching optimum, nor
an audit of physical address transformations. The inherited
[`columns_k.cpp`](../e8-bit-carrier-skeleton/code/bit/checkers/columns_k.cpp)
also projects MOVEs out of its formal-column replay. Here the rational geometry
is checked separately and exactly; MOVEs are never described as executed address
operators. Physical allocation of two snapshots remains an explicit premise.

## Concrete object and source pins

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
PR1704 head `7f14aa7285cf10a7be350472fab25a25ef898484` supplies the fixed partition
`(0,3), (1), (2,4), (5,7), (6,8)` of retained totals472–480.
The consumed PR1062 payload is
[`candidate.json.gz`](../r439-bsection-stars-seed01/candidate.json.gz), at its
exact Git/SHA256 pin in [SOURCES.json](SOURCES.json). No pending package is imported
as executable code. The retained original exporter emits the full baseline; only
its contiguous scatter region is replaced. Every original MOVE and all records
outside that region are retained literally.

[SELECTION.json](SELECTION.json) preserves the one independently drawn nonce
`221c3644c3349df6239e718172a57529`, track `bit-mechanisms`, both suggested cards,
methods, catalogue/selected-record hashes and exact base. [TASK.json](TASK.json)
records the deliberate change from the saturated semantic-D H2/K question to
PR1704's live temporary boundary. The
[round-two claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1929#discussioncomment-18925928)
and [OVERLAP.json](OVERLAP.json) distinguish this from the original scatter census,
its prior independent scalar audit, and the previous round's PR1913 absorption.

## Replacement record contract

The raw ABI is little-endian six signed int32 fields, exactly as in the pinned
exporter. Persistent registers0–660 retain their original identities; two
explicit slots661,662 replace the hard-coded singleton temporary.

* `MOVE(0,role,old,new,rank,0)`: persistent role only, exact old-frame match,
  rational containment, and exact positive dimension charge. In the reverse
  interpretation labels stand for annihilator complements: reversing an original
  containment gives the required increasing complementary containment.
* `ADD(1,dst,src,c,frame,phase)`: distinct declared operands, `c=+1` or `-1`,
  both in the stated common frame; a temporary must be live. No live snapshot's
  original persistent center may be written. Temporary writes are permitted.
* `COPY(2,center,slot,center_frame,ZERO,rank)`: persistent center, inactive clean
  slot, correct center frame and rank. The slot contains the center's exact row.
  Slots are distinct storage objects in this finite interpreter, not aliases.
* `ERASE(3,center,slot,center_frame,ZERO,0)`: the same live center/slot pair, the
  same frames, and **slot row = its saved COPY row = current center row**.
  This equality is checked before deallocation, not inferred from a final map.

There is no reset of dirty persistent workspace. The only clean storage is the
two declared fresh COPY destinations. All661 persistent inputs, including439
helpers, are arbitrary. In the backward word, ERASE becomes COPY, COPY becomes
ERASE, every ADD coefficient is negated, and the original center binding is
retained. Reverse geometry uses complementary frames, not uncharged descent.

### Why the replacement implies the finite boundary

A live COPY is the injection `(z,empty) -> (z,Lz)`, with its original center
unchanged until the matching ERASE. On the legal subspace `slot=Lz`, ERASE is
its inverse. Let any sequence of invertible common-frame additions act between
these events, possibly mixing several distinct live slots. If each individual
ERASE verifies its own exact snapshot equality, reversing the complete word
recreates the correct slot value at that event; subsequent inverse additions
recover the previous state. This follows by induction backwards over events.
The proof does not require each slot to stay immutable between its endpoints.
Final persistent equality alone is insufficient because it forgets the domain
condition at an intermediate ERASE.

For PR1704's block, let the two arbitrary ZERO-frame snapshot outputs be `a,b`.
The emitted temporary word is `p+=q`, the common-target reads of `p`, then
`p-=q`. It restores `p=a,q=b`; exclusive targets read the original separate
values. Every target therefore receives precisely the old increment. This is
an identity over any module over a commutative ring, with arbitrary target dirt.
The snapshots may be outputs of different original frame operators: they are
not equated with each other or with a frame-free persistent value. They are
mixed only after both are in the common snapshot module.

Thus the complete persistent state **and every frame** at the end of scatter
match the original stream. The unchanged B/C continuation sees the same state.
The same restricted-inverse argument applies to the reversed signed stream.
The exact integer row checker certifies equality of the full local candidate
and baseline signed lifts, not a claim that the full signed lift is itself the
multiplication map. Its F2 reduction has the required local shear in both
orientations. Matrix equality makes this a uniform scalar-module implication;
the finite bank tests below do not prove physical address or all-size compilation.

The physical use of this substitution still assumes that both COPY outputs can
be realized simultaneously in disjoint zero-frame modules, with no collision
with private workspace, and that the inherited interpretation of common-frame
ADDs applies. The checker does **not** prove these premises.

## Complete finite accounting

PR1704's scalar counts and its local profile are retained, not improved again:

| Quantity per local invocation | Original | Two slots |
|---|---:|---:|
| Persistent inputs |661|661|
| Peak fresh snapshot slots |1|2|
| Peak sum of live COPY ranks |7|14|
| COPY / ERASE |9 /9|9 /9|
| COPY rank sum |63|63|
| Persistent MOVEs |2,911|2,911|
| Scatter ADDs, including preparation/restoration |527|407|
| Complete ADDs |11,500|11,380|
| Rank mass |5,129|5,129|

The unchanged local profile is
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`.
No zero-cost temporary, omitted restoration, source-frame change, or reused dirty
helper is hidden. A copied snapshot slot is separately counted even though it
has no independent initial dirty column. Its physical size/hosting cost is not
inferred from its COPY rank or the interpreter's bitset storage.

For `K=2,4,5`, there are `S=2K+1` local stages. Unlike the inherited native
columns checker, which uses one restored helper bank, this interpreter assigns
**S independently dirty helper banks**. It therefore checks
`2K*111 + S*439` formal columns: **2,639 /4,839 /5,939**.
Every stage boundary is checked, not just the final composed endpoint.

The finite scalar invoice is

`S*11380 + 6*(K-1)*111 + 3*K*111` ADDs,

including every bank bridge and an explicitly executed three-ADD terminal
exchange. The signed exchange `a+=b; b-=a; a+=b` has endpoint `(b,-a)`, which is
the inherited signed exchange and a swap overF2. Its cancellation-free
intermediate bound is five times the incoming bound; no free terminal swap is
used in the delivered bank interpreter. Every stage uses nine COPY/ERASE pairs;
slots are closed before the next stage. Bridge-omission controls cover every
one of the6/18/24 bank shears.

If `F,B` are the exact local positive-row bounds measured by the Python engine,
a conservative fully counted scalar-prefix envelope for this finite schedule is

`5 * 2^(6*(K-1)) * F^(K+1) * B^K`.

The factor5 includes terminal exchange intermediates. The five- and nine-stage
integers are checked against the inherited algebraic104/192-bit caps; the
11-stage value is reported without inventing a new cap. These are finite
algebraic envelopes, **not a migrated packed precision/tape or hosted invoice**.
Since the recursive profile is unchanged, even making the additional physical
workspace free would leave the local recursive moment unchanged. No scalar
saving here establishes a kappa improvement.

The exercised receipt gives `F=25,717`, `B=6,248,884`, 14,309 raw6 records,
636 exact rational frames, and 2,386 containment pairs:

| Stages | Dirty formal columns | Checked ERASEs | All scalar ADDs | Prefix bits, including exchange |
|---:|---:|---:|---:|---:|
| 5 | 2,639 | 45 | 58,232 | 98 |
| 9 | 4,839 | 81 | 105,750 | 184 |
| 11 | 5,939 | 99 | 129,509 | 228 |

The direct executable smoke and registered Python 3.12.12 replay both passed
with Apple clang 21.0.0. Ten semantic failure controls and the single-slot
positive control passed. Exact output and the two corrected metadata preflights
are retained in [VALIDATION.json](VALIDATION.json); no hosted result is claimed.

## Reproduce and evidence

Requires Python3.12 and a C++17 compiler, with no third-party Python/native
libraries. `CXX` may specify the compiler; otherwise `c++` is used. The compiled
binary and emitted streams live in a disposable work directory, never in the
frozen input packages.

```sh
uv run --python 3.12 --no-project python -I -B \
  research/bit-two-copy-bank-boundary/verify.py --work /tmp/two-copy-bank-new
uv run --python 3.12 --no-project python -I -B scripts/research_package.py \
  --package research/bit-two-copy-bank-boundary
```

Use a fresh `--work` path. The registered replay compiles with
`-std=c++17 -O2 -Wall -Wextra -Werror`, runs the positive source and candidate,
checks exact source pins and rational geometry, local signed endpoints and
chronological snapshots in both orientations, and runs all negative controls.
The native implementation is separate from Python's sparse integer-row engine;
sharing AI assistance does not make it independent human review.
[RESULT.json](RESULT.json) is compared canonically and contains raw stream hashes,
all bills, prefix integers and controls. Receipt regeneration is explicit via
`--generate-receipt --work NEW_PATH`, never an automatic missing-receipt bypass.
[VALIDATION.json](VALIDATION.json) records the actually exercised environment and
commands. No hosted CI result is inferred from local execution.

The meaningful failure controls include unrestored snapshots hidden by blind
deletion, wrong signed restoration (invisible overF2), aliased slots, wrong
center, noncommon frame, undercharged COPY, self-ADD, undeclared slot, use after
ERASE and a truncated raw6 record. All original single-slot states remain a
positive control. The mandatory catalogue helper-star working example is
orientation evidence only; its11500-ADD result is not claimed as new.

## Open next questions

No full selected cold replay, physical address-transform execution, native
physical two-COPY allocator, owner-window/hosting admission, packed precision,
tape realization, outer assembly, Lean proof or independent human review is
claimed. The separate old immutable-temporary checker remains unchanged and
still does not admit the new stream. A new record-level predicate is not a
replacement physical compiler theorem. Selected sources, frontier and kappa
are unchanged.

**Next useful question:** can the actual COPY implementation bind slots661/662
to disjoint physical workspace, including its private temporary, and what is
the full invoice? Start from the emitted raw6 stream and provide exact physical
buffer/owner identities and lifetime interference checks before rerunning a
hosted supplier. The blocker is precisely physical allocation, routing and
precision—not another scalar endpoint or pair matching search. Structured
scope and blocker information is in[TASK.json](TASK.json).

## Credit and disclosure

Ross Richardson's[PR1704](https://github.com/CrocSwap/integer-mult-bounds/pull/1704)
supplies the two-copy block, optimum, proof and open native handoff. The prior
[independent scalar audit](https://github.com/CrocSwap/integer-mult-bounds/pull/1704#issuecomment-6169499202)
reproduces its restricted optimum and pair identities; those are not new here.
Sagar Thakrar supplied PR1062's11500-ADD word; credit PR967/theon199 helper stars,
Gareth Davidson's PR926 pairs, Aaron Wang's PR1015 and Ross Richardson's PR923
blocks, DreamingOfClouds' PR589, eumemic's PR555 and interface lineage, Dylan
Crow's exporter/native adaptation, DaysSky's bank schedule, and woklerx's
PR1437 chronological COPY audit and semantic-D work. Existing source notices
and packages are untouched.

New implementation and scoped proof prepared for Adam Gall with substantial
OpenAI Codex GPT-6 Astra assistance in research, code, tests and writing.
Apache-2.0. No literature-priority claim is made for elementary matrix algebra
or reversible compute/uncompute.
