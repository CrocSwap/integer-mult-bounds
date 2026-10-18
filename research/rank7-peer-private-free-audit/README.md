# All private frees in the PR2979 native execution

The 91 private buffers in each original PR2979 provider return to zero at
**their actual free events**, in both orientations, for arbitrary original
source, target and dirty-helper inputs. This closes PR3038's first open
question at its conditional macro/native boundary. It is a finite audit;
physical supplier admission and the selected exponent remain separate.

PR3038 checked helper249 and private953 (emitted name `Z249`). A peer's later
free can fall outside those roots. The new audit roots every actual private
free and retains the old helper endpoint. For each provider:

| Orientation | Prior cone events | Expanded events | Prior native classes | Expanded classes | Added classes |
|---|---:|---:|---:|---:|---:|
| Forward | 8,902 | 12,693 | 2,039 | 2,648 | 609 |
| Inverse transpose | 12,357 | 20,956 | 1,790 | 3,167 | 1,377 |

The forward additions comprise 557 child, 46 warp and six residual-wrapper
classes. The inverse-transpose additions comprise 1,245 child, 90 warp,
20 wrapper and 22 endpoint-adapter classes. Each serialized identity is
replayed on all 512 address columns, including global phase. The old classes
are replayed too; a stored PASS is not used as their acceptance test.

## Exact scope and independence

The scientific input is [PR2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979)
at `be191346391661f4d35fc0d1508d0a6029572576`. The immediate handoff is
[PR3038](https://github.com/CrocSwap/integer-mult-bounds/pull/3038) at
`c7d0d7be056ba77fda1c168641b2bcffb10cf43d`. The task and source baseline is main
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6. All live inputs
are pinned in [SOURCES.json](SOURCES.json). The claim is in
[discussion #2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19001873).

The new `lifetimes.py` imports no predecessor replay or dependency code. It
propagates exact rational rows over reduced noncommuting warp words, starting
with a distinct formal variable for each of the 632 original inputs and zero
for each private allocation. It records the row immediately before each free,
rejects a nonzero row, and rejects use outside the allocation/free lifetime.
It separately computes forward provenance bitsets on value, chart and lifetime
channels. These are transitive producer sets, not coefficient supports: no
algebraic cancellation prunes a dependency. COPY/CLEAR overwrite value only;
chart and lifetime obligations survive.

For an ADD, row substitution is exact linearity. A warp left-multiplies every
term; only adjacent inverse symbols cancel. Thus a zero row is an identity for
any realization of the warp generators by invertible operators. In the dual
orientation the emitted ADDs already have swapped operands and negated
coefficients, and scales are reciprocal. Warps use distinct formal generators
for inverse transpose. This argument is about exact arithmetic, without
rounding. Induction over the finite event sequence proves that a row computed
as zero is zero on every original input. Allocation is known-zero; it is not
an arbitrary dirty input or a free source of physical storage.

Every state channel's provenance set is initialized with its own boundary
symbol. Each event unions the old channels it reads and its own event label;
all inputs to a multi-channel update are read before writing. Induction gives
exact syntactic reachability for the declared event semantics. The union at
each free includes that private's value, chart and lifetime. The new forward
algorithm reproduces PR3038's complete old event and boundary sets exactly,
then adds all 91 free obligations. Handwritten fixtures independently specify
COPY overwrite, CLEAR, persistent chart dependencies and a peer-free root
that is invisible from the old pair.

The retained PR3038 source decoder is **reused**, with attribution, to compare
the whole fresh emitted stream with the literal source word and bind ordered
frames, role compaction, scalar positions and private names. Its native
selector and Sagar Thakrar's exact Gaussian kernel are also reused. The new
independent work is the private-free propagation and forward provenance,
coverage extension and controls, not a new compiler or native kernel.
Generated program digests and serialized native artifacts must match the
original PR2979 native receipt. Comparison of generated programs uses their
canonical JSON payload, not gzip container bytes. Frozen inputs remain intact.

## A failure invisible to the original roots

In the forward program, event 17256 is `Z395 -= L5` in FULL frame. Change its
coefficient from -1 to +1 while leaving the rest of the stream fixed. At its
actual free, event 22501, `Z395` then contains

```text
-2 (x64 + x65 + x96 + x97).
```

Here `xr` denotes the original normalized input at role `Lr`; all four
coefficients have empty warp words. Setting only `x64` to a nonzero address
basis vector supplies a concrete nonzero output. The old helper249 endpoint
and `Z249` free still pass. Event 17256 is outside the old dependency cone.
This is a deliberate mutant, not a defect in PR2979.

The inverse-transpose control flips event 17254, `Z395 -= 4 L96`; it likewise
leaves the original roots correct but makes `Z395` nonzero, with coefficient
4 on original `L115`. The complete exact corrupted rows are retained in the
receipts. Premature-free controls fail both value and lifetime checks. A
phase mutation in a newly reached native child preserves rank and geometry
but fails the exact operator check. Eight small behavioral tests also cover
noncommuting order, dual symbols, rational cancellation, source parsing and
removing a charged private family from the invoice.

## Invoice trace and remaining obligations

The source allocates all 91 private buffers before cleanup and frees all 91
after it. The measured peak is 91 in all four streams. This result justifies
their normalized zero-return; it does not reduce the charged buffer stock.
The source-declared physical count remains

```text
66,304 live + 408 helpers + 8 centres + 91 private + 2 other = 66,813.
```

A full event recount retains the per-call paid profile
`2445 H1 + 706 H2 + 232 H3 + 108 H4 + 18 H5 + 8 H8`.
The source has 666 calls, 250 base and 416 extra. Its claimed complete recursive
invoice is

```text
1,645,680 H1 + 470,196 H2 + 159,468 H3 + 71,928 H4
+ 13,716 H5 + 5,328 H8 + 28,190 H48.
```

Subtracting the literal local charges leaves the same conditional remainder
as PR2993: `17,310 H1 + 4,956 H3 + 1,728 H5 + 28,190 H48`.
This subtraction is **not an independent owner replay**. The physical sum and
complete invoice are authenticated source declarations with arithmetic
reconciled; this audit does not certify all their physical costs.

The package also retains PR3014's losing controls under the *parent's fixed
owner assignment*: single249 has delta
`1264 H1 + 6694 H2 + 3996 H3 - 6660 H4`, while joint V45 has
`1038 H1 + 6807 H2 + 3996 H3 - 6660 H4`. Their signed rank mass is zero and
all positive terms have rank below four, so both moment differences are
strictly positive for every saving parameter `a > 0`. Those source-bound
identities are prior results, not new owner coverage. PR2979 uses a different
final allocation; these controls do not reject it.

The conditional composition inherits PR3038's common-chart and residual-wrapper
coordinate contract. Exact native identities and zero normalized rows do not
by themselves implement physical rational scalars, COPY/CLEAR, known-zero
allocation, backing ownership, precision or tape. The actual final fill and
its physical bill, both supplier caps, the complete supplier/outer release,
and inherited all-size/compiler/analytic conditions have not been admitted
here. No new packing, lowering search or selected-frontier change is made.
Apart from the retained helper249 endpoint, this audit does not check the
supplier's 632 original output endpoints. Its roots are the private frees.

## Reproduce

Python 3.12 and `numpy==2.3.5` are required by the unchanged producer. The new
checker and exact native kernel use the standard library. From the repository
root, with that dependency already installed:

```sh
python3 scripts/research_package.py --package research/rank7-peer-private-free-audit --check-only
python3 scripts/research_package.py --package research/rank7-peer-private-free-audit
```

The registered hook runs the eight small tests, then one fresh artifact and
exact native replay per provider, sequentially. Each provider prints
`PASS_ALL_PRIVATE_FREES_AND_EXPANDED_NATIVE_CONE provider=base` (or `extra`),
followed by `private_frees=182 native_classes=5815`.
The whole hook ends with `PASS_REGISTERED_RESEARCH_PACKAGE`.
`RESULT-base.json` and `RESULT-extra.json` contain the deterministic evidence.
The fresh registered replay passed on 2026-10-17 in 508.9 seconds under
CPython 3.12.3, with one numeric thread. This includes all eight behavioral
tests, source regeneration for both providers, exact native checks and full
receipt equality. An earlier attempt exposed a tuple/list serialization
mismatch in a control receipt; normalizing that frame to JSON fixed the
comparison without changing its mathematical evidence.

Direct replay is `python3 -I -O -B research/rank7-peer-private-free-audit/verify.py
--provider base` (repeat with `extra`). `--emit` prints a fresh receipt;
`--artifacts DIR` reuses generated artifacts but still authenticates the full
source/receipt bindings and reruns all checks. That mode does not claim fresh
producer execution. The normal command writes no repository artifacts and
needs no network. Each producer subprocess has a 300-second timeout, and each
registered provider command has a 570-second limit. See [VERIFY.json](VERIFY.json).

## Open next questions

Join these checked private lifetimes to the actual final allocation and the
physical scalar, storage and precision contract. Start by binding the 91
named allocations and reached scalar/COPY/CLEAR events to their backing
families and charged physical implementations. This matters because a zero
logical endpoint alone does not admit a supplier. Ownership, arithmetic,
precision/tape, outer and all-size contracts are the remaining blockers.
No further fixed-word native-cone expansion is proposed for these private
free roots. Structured scope and the handoff are in [TASK.json](TASK.json).

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

ToikY supplied PR3038's source decoder, native event selector and explicit
peer-free handoff. Nick Petalas supplied PR2993/3006/3008/3014's frame,
endpoint, event and fixed-owner invoice audits. Marius-Paul Dumitrean supplied
PR2979 and its PR2942 predecessor. Retain Jeremy Kothe's frame/native/cleanup
and rewrite credit; Mason Hale's PR2917 and Jeremy Diviney's PR2908 extraction
credit; Sagar Thakrar's exact Gaussian kernel; icekylinx's native compiler;
Ross Richardson's algebra and packing audits; and Tekalign, Yiyang Lu,
Dugongue, Cinna Davis, DreamingOfClouds and the retained geometry/owner lineage.
This account's PR2655 concerns pooling an earlier PR2269 word and is not
repeated here. No independent human or proof-kernel review is claimed.
New work is Apache-2.0; predecessor sources and notices are unchanged.
