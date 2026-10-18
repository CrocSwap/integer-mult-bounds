# A Lean transcript theorem for P104 transport cuts

Lean 4.21.0 checks the chronological factorization behind the P104 transport
floor: after `n` counted inward transports, every target-side value factors
through a transcript of `n` whole arrays. If each array has dimension `d`,
the source-to-target block has rank at most `n*d`, even with arbitrary
same-side linear work, storage, copies and feedback. Recovering `m`
independent arrays therefore requires `n >= m` when `d > 0`.

The claim is in [discussion #2164](https://github.com/CrocSwap/integer-mult-bounds/discussions/2164#discussioncomment-18934656).

This formalizes a written argument by **Ross Richardson (PR2127)** and
**Nick Petalas (PR2148)**, following the explicit machine-checking handoff in
[Discussion2164](https://github.com/CrocSwap/integer-mult-bounds/discussions/2164)
and Michael Yee's **PR2163**. The mathematical cut bounds are theirs. The
new contribution is a precise inductive program model, a kernel-checked
factorization and dimension argument, a source binding for the unsplit
cut, and tests of the formal assumptions. No new supplier or exponent is
claimed.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0. No independent human review is claimed.

## Formal statement and model

[TransportCut.lean](TransportCut.lean) defines `Runs n s t`, where `s` and
`t` are the source-dependent linear blocks of the current source-side and
target-side states. A finite program has fixed finite storage capacity;
unused slots can represent later allocations. The theorem itself does not
require finite-dimensional storage, only a finite-dimensional message space.

The grammar has four constructors:

| Constructor | Operation | Count |
| --- | --- | --- |
| `init` | Arbitrary source-side input map; zero target-side source dependence | 0 |
| `source` | Any linear update of source-side state from both sides | unchanged |
| `target` | Any linear endomorphism of target-side state | unchanged |
| `receive` | Read one element of `D` from both sides; update target state by `A t + B z`, and source state by any linear map | +1 |

The `source` constructor grants all return traffic for free. Each incoming
message may depend on earlier messages, so feedback, cycles in the static
frame graph and later retransmissions are included. Copying, discarding,
changing a basis, or storing a received value is a target-side linear
endomorphism and cannot create another independent record.

`Factors n t` means that there are linear maps

```
encode : X -> (Fin n -> D)
decode : (Fin n -> D) -> R
```

with `t = decode ∘ encode`. `factors_receive` appends the new message to
this transcript in the correct order. `runs_factor` proves factorization by
induction on every finite `Runs` derivation. `runs_rank` uses Mathlib's
finite-dimensional range inequalities. `recovery_requires_receives`
allows any final linear readout of all target-side storage and derives
`m <= n` from exact recovery of `Fin m -> D`.

The code is valid over any field. In the characteristic-zero application,
`d` is the dimension of a complete array, including whatever finite cover
and payload coordinates the model retains. **Native child rank and message
dimension are different quantities.** An original rank-seven descent sends
one `d`-dimensional value in this model, not seven independent arrays.

`one_receive_attains` is a formal positive constructor fixture: one
whole-array message attains the identity on arbitrary input.

The exact corollaries are:

- `p104_unsplit_floor`: exact recovery of 104 arrays with at most `8+k` inward
  transmissions implies `k >= 96`.
- `p104_refined_floor`: exact recovery of 56 arrays with at most `8+B`
  inward transmissions implies `B >= 48`.

These are conditional corollaries of the respective authors' cut models.
The second does not formalize the refined subspace separator or prove that
its added paid rank bounds the crossing count.

## How the P104 model enters the grammar

For PR2127, assign every original frame reachable from a source without
using the eight C descents to the source side; all other frames, including
newly introduced frames, are outside. Reserve enough slots on each side
for the entire finite execution. Grant free mixing between *all* slots on
a side; this is more permissive than common-frame mixing.

A same-frame operation stays on one side and is `source` or `target`.
An outside-to-source transport is a `source` update. An inward whole-array
transport is `receive`: its linear read includes its array operator,
`B` writes the destination slot, and `A` retains or clears other outside
slots. Its source slot can be cleared by the `keep` map. Transporting or
copying within a side is free in this relaxation. An arbitrary finite
number of source-independent storage lifetimes fits by preallocating
slots and clearing/reusing them with linear maps.

To isolate source dependence, fix the independently arbitrary target,
helper and fresh-storage inputs to zero. This is a slice of the claimed
all-input endpoint identity; it does not assume that the native program
may use clean dirty helpers. On this slice outside initialization has
zero source dependence. Identity transfer, after any specified invertible
endpoint adapters, gives the `correct` readout hypothesis. Source and
helper restoration are relaxed, so imposing them cannot defeat the bound.

This paragraph is the **written model translation**. Lean checks every
trace admitted by the displayed grammar. It does not parse or formalize a
native program language, or show that every proposed extension meets the
model. Informative initialization, an uncounted inward read, a wider
message, data-dependent nonlinear coefficients, or an adaptive operation
schedule must not be silently placed inside this grammar.

## Source-bound finite premise

[verify.py](verify.py) reads the unchanged PR1972 witness retained by
PR1991, SHA256
`0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e`.
It reconstructs all binary frame spans and all 4,058 events, checks the
common frame of every ADD/COPY and the chronology/rank of every transport,
and reproduces the PR2127 static partition. There are 444 original frames,
222 on each side, 104 source entrances, 104 target exits and 1,410 original
transports. Exactly the eight C descents enter the outside:

```
2463, 2472, 2479, 2487, 2495, 2503, 2510, 2518
```

The canonical receipt is [EXPECTED.json](EXPECTED.json). The checker also
regenerates every Boolean entry of [SourceCut.lean](SourceCut.lean), which
proves the source/target side predicates, array counts, transport count and
eight-crossing count by kernel reduction (`decide`, not `native_decide`).
The JSON-to-frame interpretation remains in Python, outside the Lean
kernel. This is an explicit source binding, not another claim of a new
separator or an independent native-channel replay.

Exact finite controls include a two-message feedback decoder, copying a
single received value without increasing rank, and two-coordinate
noncommuting block recovery. Removing source independence, allowing an
oversized message, or omitting the charge for an extra source read gives
explicit counterexamples to the corresponding weakened statements. Four
mutated original witnesses are rejected. Artifact controls reject source,
receipt-type and generated-Lean changes and missing evidence; relocated,
read-only, normal and optimized Python replay agree.

## Reproduce

The standard-library source and finite checks use Python 3.12:

```sh
python3 -I -B scripts/research_package.py --package research/lean-transport-cut
```

Expected lines include:

```
PASS_TRANSPORT_CUT_BINDING sources=104 crossings=8 transports=1410 controls=12 formal_not_run
PASS_TRANSPORT_CUT_ARTIFACT_CONTROLS groups=8
```

The registered Python hook explicitly **does not compile Lean**. For the
formal proof use the pinned Lean `4.21.0` toolchain and the committed
[lake-manifest.json](lake-manifest.json), whose Mathlib head is
`308445d7985027f538e281e18df29ca16ede2ba3`. From this package directory:

```sh
lake exe cache get Mathlib.LinearAlgebra.Dimension.Constructions Mathlib.LinearAlgebra.FiniteDimensional.Basic
python3 -I -B check_lean.py --lake lake
```

The cache command provisions dependencies and may use the network. The
checker then validates every dependency head, compiles both files afresh
with warnings as errors and at most four Lean worker threads, and audits
all thirteen theorem roots. Only `propext`, `Classical.choice`, and
`Quot.sound` are allowed. No `sorry`, custom axiom or native-decision axiom
is accepted. SourceCut's six finite facts use no axioms.

Eight formal controls must fail: uncharged receive, informative outside
initialization, the false floors 97 and 49, a `sorry`, a custom-axiom proof,
a missing recovery probe, and an undercounted original cut. The custom-axiom and missing-probe controls are required to compile
successfully and fail the axiom/probe audit, so a syntax error is not
mistaken for audit coverage.

Expected final line:

```
PASS_LEAN_TRANSPORT_CUT theorems=13 rejected_controls=8 no_sorry_or_custom_axioms
```

[FORMAL-RECEIPT.json](FORMAL-RECEIPT.json) records the observed local run,
compiler, dependency heads, proof hashes, theorem axioms and rejecting
controls. `--out NEW_PATH` emits a fresh receipt exclusively. It is not a
substitute for rerunning the compiler. The dedicated
[workflow](../../.github/workflows/lean-transport-cut.yml) provisions the
checksum-pinned official Lean release and runs these same commands; hosted
CI has not been observed for this contribution.

## Limits and credit

The source binder checks the **unsplit original** cut. The graph partition,
written all-program bound and retiming/storage extension belong to Ross
Richardson / [PR2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127)
(`befebf0f4ae7a3f69fe9c5e136262559dcac125f`). The refined 48-rank argument
belongs to Nick Petalas / [PR2148](https://github.com/CrocSwap/integer-mult-bounds/pull/2148)
(`937b132f3f143ce0f2621b3b12e1ebc413e66730`), using Tairitsu-Aya / PR2136's
separator. Michael Yee / [PR2163](https://github.com/CrocSwap/integer-mult-bounds/pull/2163)
(`9f6e1f2783aef0c52bb3f26f587a918a8be32fa9`) independently checked graph
premises and requested this formal implication. Earlier cut work by David
Arias, Adam Gall and Jeremy Diviney is retained. The channel is Rohan Arun's
PR1972, natively realized by Chafik Boukhalfa in PR1991 using Adam Gall's
schedule; geometry and decoder attribution continues through their notices.
Lean and Mathlib authors supply the proof system and dimension library.

No new chronological owner realization, source-to-native semantics,
refined-separator formalization, physical transport pricing, coverage
credit, precision/tape, all-size lift or selected cold replay is supplied.
The selected record and every frozen predecessor remain unchanged. The
underlying transcript and rank method is standard; this contribution is
its scoped formalization and source binding.

## Open next questions

1. **Formalize the native-event-to-`Runs` translation.** This would remove
   the written bridge for arbitrary retained-occurrence programs. Start
   with a typed register/frame semantics and prove each primitive has one
   of the four constructor forms. The blocker is agreeing on the precise
   allowed initialization, array width and cross-chart access rules.
2. **Formalize PR2136/2148's refined crossing count.** The generic rank
   theorem already accepts `n <= 8+B`; a useful next step is a kernel proof
   of that premise from the survivor separator and nested paths. The
   blocker is the finite-subspace/interval model, not the 56/8 arithmetic.

The structured forms and bounded first steps are in [TASK.json](TASK.json).
