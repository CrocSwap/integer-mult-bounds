# JP8 unit additions with already-zero coefficient work

**Finite complex-supplier circuit improvement; no new κ.** A conservative
state analysis removes 4,614 redundant coefficient-work clears from each real
orientation of the historical #626 JP8 program. Both real components together
save **9,228 primitives per orientation beyond #696**. The addition boundary
still leaves coefficient work zero; no macro boundary is fused or relaxed.

| Complete JP8 scalar program | Original | PR696 | This composition |
| --- | ---: | ---: | ---: |
| Forward real-component primitives | 257,232 | 200,380 | **191,152** |
| Backward real-component primitives | 257,280 | 200,396 | **191,168** |

These are exact instruction counts, not runtime measurements. This package
specializes Sagar Thakrar's incorporated #696 lowering; it does not claim his
copy/unit savings as new. The additional savings are 400 in the zero-frame
precondition, 2,596 in A, 186 in B, 5,968 in full-frame cleanup and 78 in the
cleanup tail, identically in both orientations.

## Reproduce

From the repository root, using Python 3.11+ and its standard library:

```sh
python3 -I -B research/jp8-clean-work/verify.py
```

Expected final line:

```text
PASS_JP8_CLEAN_WORK orientations=2 columns=716+9 extra_saved=9228,9228 controls=15
```

The command is offline, writes nothing and also works via an absolute path from
another directory. `--json` prints the exact checked [receipt](EXPECTED.json).
All source pins are checked before importing the predecessor lowerer. Compressed
inputs are bound by decompressed payload, so gzip headers are not proof data.
The constructor is [lower.py](lower.py); [verify.py](verify.py) synthesizes and
replays its entire emitted stream, including a digest of every primitive and
unchanged non-scalar event.

## The state condition and proof

Let W be the existing private coefficient register. PR696 lowers a unit addition
to `T += S; clear W` (or `T -= S; clear W`). Its nonunit additions prepare a
coefficient in W, accumulate it and clear W. Every addition therefore guarantees
W = 0 on exit, even for arbitrary incoming W.

At the start of each uninterrupted scalar run in one frame, the new lowerer
knows nothing about W. It emits the first addition exactly as #696 does. From
that boundary onward W is known zero. Intervening scale/copy/clear macros only
address logical or center registers, so they preserve this fact. A subsequent
unit addition does not read or write W, and its trailing clear acts on zero.
Deleting that clear preserves the complete boundary map. Nonunit additions
remain literal #696 circuits, reestablishing the same postcondition.

Induction over the run proves the equality for arbitrary, possibly correlated
logical, center and helper inputs. Every phase, climb, center call, adapter,
residual adapter and frame change discards the knowledge. The argument needs no
claim that an opaque operation preserves private scratch. The lowerer rejects
scalar operands outside the logical/center register classes, including aliases
of W. It never assumes W is initially clean.

Deletion of a clear on an already-zero register also preserves every intermediate
register value, up to repeated states. This is a stronger local justification
than an endpoint check: no new prefix growth, source access or intermediate
support appears. The retained positive bounds remain 64 bits forward and 101
bits backward, within the inherited charged 192-bit allowance. Exact arithmetic
does not discharge the inherited uniform rounding/tape implementation.

## Complete cost and recurrence scope

For an orientation with U certified omissions, its new real-component bill is
`P_new = P_PR696 - 2 U`. Here U = 4,614 in both orientations. No logical scalar
macro changes: all 22,693 macros, source reads, copies, center operations,
restorations, frame events and residual wrappers remain in their original
positions. Nonunit coefficient work remains fully paid. The work register and
eight private centers already exist; no helper or temporary register is added.

The local invoice uses the pinned `invoice_allcold.py` formula, including its
entire generic adapter reserve. With m = 73, n = 716, c = 8, M = 22,693 and
K = 3,606 paid children:

```text
compiler = 64 (m+1)^3                         = 25,934,336
adapters = 16 (M+K+n+c) + 64m                 = 437,040
adapter primitive reserve = adapters*compiler = 11,334,342,205,440
local bound = max(P_forward, P_backward) + adapter primitive reserve
```

The complete local bound is **11,334,342,396,608**, versus
11,334,342,405,836 with #696 and 11,334,342,462,720 originally. Thus the generic
adapter accounting does not erase the 9,228 additional saving. It also makes
clear why the scalar percentage is not a percentage improvement to the full
invoice or a practical speedup.

The paid-child profile remains exactly
`{1:2512, 2:400, 3:448, 4:160, 5:70, 6:8, 8:8}`. The same recursive children,
helpers, owner widths and wrappers occur, so the recurrence's child terms and
moment equation are unchanged. There is no new exponent and no opportunity for
a different supplier to become binding through this scalar-only change. The
local bound is recomputed here; production global invoice/artifact bindings
have not been regenerated or admitted.

## Evidence and limits

The verifier covers all 27,909 events in each orientation. Its integer dyadic
interpreter executes every primitive on all **716 native plus nine arbitrary
private input columns** (eight centers and W). It checks the forward shear,
inverse-transpose shear, restoration of all 492 dirty helpers, private clearing
and zero W at every addition boundary. It compares the original and #696 bills
with their pinned receipts and recounts every paid child.

An independent backward scan reconstructs the exact omission witnesses without
using the optimizer's forward state. Both orientations have the same witness
digest; the primitive stream digests differ. A separate Fraction interpreter
checks all 574 encountered coefficients through 13,728 intermediate primitive
states, including unequal input denominators, and checks their full macro maps.

The 15 [negative controls](controls.py) cover dirty initial work, every opaque
boundary kind, frame changes, private aliases, unknown instructions, wrong sign,
omitted nonunit cleanup and endpoint-preserving excess prefix growth. In the
barrier controls an adversary actually replaces W by fresh independent dirt;
forgetting the state is therefore tested, rather than inferred from a run in
which every barrier happened to leave W zero.

This is exhaustive finite coverage of the two frozen programs and their
coefficients, together with the run-level algebraic proof above. It is not a
formal proof of the multiplication theorem. Native scalar macros and geometry
are unchanged, so geometric admission is inherited from the pinned #626 review;
this package does not repeat or extend that admission. All-size realization,
common labels/mutable bases, whole-call hosting, precision/tape and analytic
transfer remain inherited obligations. No composition with other pending
coefficient or basis optimizations is asserted by adding their reported savings.

## Provenance, diversification and credit

Exact base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
At that base the accepted record is #741 at
`e516b1463606840a15f80aac1995d64ce0092e89`, with conditional
κ = `1661202643272239/10^18`. Its [construction and review](../../docs/research/community-frontier741-review.md)
were consulted; this experiment deliberately chooses the historical JP8 object,
not a proposed current-frontier change. The live selected record and `upstream/`
are untouched.

[SOURCE-PINS.json](SOURCE-PINS.json) binds the #626 provider at
`660de893d27bb7abd1d5b01b1640207528a5c851`, its #622 ancestor at
`f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`, #696's actual lowerer and receipts,
the original emitter/invoice and the frozen #626 checkpoint. The historical
selected-record check inside #696's standalone driver is not bypassed or edited;
this package directly consumes its pinned lowerer and comparison data.
The retained #696 source head is
`5a3f983715027c4fd83f50bc9001d4b18463bed1`.
The [validation record](VALIDATION.md) also records the later upstream advance
to #799 and confirms that all nine historical dependencies remained unchanged.

The OS-random assignment seed is **33** (complex supplier). Its odd parity selects
JP8 over CK and it indexes a reproducible omission example. The
[local claim](CLAIM.json) records three candidates, the finite domain, stopping
rule and time budget. No pinned sprint issue existed. The PR overlap record
is [OVERLAP.json](OVERLAP.json). In particular, #755's pinned implementation
excludes unit coefficients from its shared-work runs and retains their work
clear; it does not implement this state specialization. #722/#739/#755/#787,
#793/#811/#830 study sharing/rescaling/batching coefficient values. Here W stays
zero at every original addition boundary, and there is no reordering or fusion.
This does not reopen the fixed-order frame searches of #776/#815 or the packet
delivery restrictions recorded in #651 and the experiment archive.

Credit: **Sagar Thakrar** for #696's copy/unit lowering; **icekylinx** for the
scalar/coefficient-work lineage through #425/#433/#531; **Jeremy Kothe** for
the #622 construction and JP8 schedules; **Chafik Boukhalfa** for #626's
owner repair and replay; **DreamingOfClouds**, **Rohan Arun** and the other
contributors preserved by the [#626 review](../../docs/research/community-k492-review.md)
for cold ends, recurrence correction and the inherited framework. Concurrent
coefficient work retains its distinct attribution in OVERLAP.json.

Contribution by **faw01**, with substantial **OpenAI Codex** assistance in
research selection, implementation, proof, checks and writing. New files are
under the repository's **Apache-2.0** license; predecessor notices are unchanged.
