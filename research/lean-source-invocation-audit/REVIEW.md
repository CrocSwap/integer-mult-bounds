# Independent review of the source-invocation diagnostic

Reviewed 2026-10-11. Reviewer: a separate Codex agent that did not write the
three new Lean modules or their generator/checker. This is an internal review,
not external peer review. No upstream writes or publication were made.

**Verdict:** the new statements are sound at their stated scope. They add a
kernel-checked execution of an actual emitted source word on two specific
inputs, and a conditional, precisely scoped explanation of why the direct
single-host comparison is too strong. They do **not** establish an actual
physical invocation provider, arbitrary-dirt correctness in Lean, or a failure
of PR442's algorithm. Those distinctions must remain in the final description.

## What was checked independently

I built `CoordinateSwap`, `Hosting`, `PhysicalHosting`, `SourceWord`,
`ContractScope`, and `SourceWitness` in a fresh temporary directory with Lean
4.33.0, commit `d8b18978322de05a8f3dba51ef03cf5461676c17`. All compiled. The
initial complete build took 43.9 seconds; I also rebuilt `SourceWitness` after
its clarification about the common unmodified physical projection.
The build output and exact hashes are in `independent-build.json`.

The printed principal source-word theorems use only `propext`; the two
contract-scope theorems use no axioms; the geometric witness and final
conditional contradiction use `propext` and `Quot.sound`. I found no `sorry`,
new axiom, or `native_decide` in these modules. This independent build checked
the printed principal results, not a separately generated inventory of every
checkpoint theorem; the package replay should maintain that inventory.

I separately parsed all 19,002 literal Lean events, including all 4,291 scalar
no-op frame events, and compared their four-field projection with the actual
PR442 forward template. All 96 chunks matched. I also independently replayed
the source forward events on all 987 independent normalized columns with a
Python integer-bitset interpreter. Copy/erase equality, the final blank
temporary, and the expected complete scalar endpoint passed. That last
all-column check is Python evidence, not a Lean theorem.

The source checkout is PR442 commit
`4e16d001d505d4f21dd2bcfc44591f9be4c279bd`. At stage 2, replica 0, pair 0:

| Local helper/register | Parent owner | Hosted owner |
| --- | --- | --- |
| 0 / 240 | bank family 9142, offset 56, width 8 | family 507, child 2, offset 16, width 8 |
| 3 / 243 | bank family 9145, offset 56, width 8 | family 508, child 2, offset 16, width 8 |

Both helpers enter at frame 0 and exit at frame 1. The parent call has no
owner in family 508. The hosted call has three helpers in that family,
at pending-chart intervals `[0,8)`, `[8,16)`, and `[16,24)`. Parent and hosted
templates contain identical local programs. These facts agree with
`SOURCE-INSPECTION.md` and the checked source files.

## Source model and theorem assessment

`SourceWord.lean:19–42` accurately gives the normalized Boolean semantics:
odd-coefficient ADD is XOR, MOVE is a scalar no-op, COPY writes the fresh
temporary, and ERASE clears it. The accumulated Boolean checks include clean
temporary preconditions and equality at erase. The two terminal theorems at
lines 19924–19928 check the *entire* word from zero and from basis vector 243;
they are not a projection to just the few gates involving helper 3. The
checkpoints are computed by Python but accepted only after ordinary Lean
`decide` proves each concrete transition. Incorrect checkpoints cannot make
the final theorem pass.

The Lean model intentionally erases frame IDs, nested-subspace geometry,
owner selectors, and physical address maps. Its guards also do not establish
the full center lifetime/frame discipline. `check_source.py` also checks the pinned source-file hashes and authoritative
decompressed JSON hashes, then checks those literal frame annotations and
center lifetimes separately. It does not prove
projector nesting, finite-field admission, or physical realization of MOVE.
Calling this a physical invocation proof would therefore be incorrect.

`ContractScope.lean:19–40` correctly extracts a necessary consequence of the
existing `PhysicalContract`: the entire second retained component must agree
for the two layouts. Its proof does not require bank cleanliness.

`SourceWitness.lean:34–42` uses the actual two trajectories to establish the
selected helper's Boolean response. Lines 51–69 then use an explicitly
*declared* coordinate residual to distinguish family 508. The interval is in
the pending-child chart; its index 16 is not claimed to be raw ambient
coordinate 16 before constructing that chart. An arbitrary coefficient type
with two distinct elements avoids an unsupported claim that a specific small
address prime is admitted.

The final theorem, lines 78–94, correctly takes both physical-observation
refinement equations as hypotheses. It proves that these observations cannot
coexist with the proposed single-host contract under the **same unmodified
family-508 projection**. It does not derive those observations from physical
execution, or prove that any implementation satisfies them. There is no
logical vacuity hidden by the theorem: its purpose is exactly to expose this
incompatible conjunction. Its usefulness depends on retaining that explicit
conditional scope.

## Adequacy and next boundary

The unconditional contribution is a concrete source-bound normalized
execution certificate for two inputs. The physical result is a failed direct
instantiation under the source's declared residual semantics. This is useful
progress beyond a generic wrapper-only lemma, but the stronger goal of one
actual physical provider satisfying the whole-hosting conditions remains
open.

This diagnosis does not refute whole-residual hosting. A per-family hybrid
comparison that holds the other relocations fixed, a multi-host theorem, or
an explicitly justified layout-dependent decoding could repair the mismatch.
Simply dropping other final data from `R` would not certify those data's
endpoint behavior. A successful physical provider still needs source-event
lowering, owner injectivity, and the coordinate-chart/reflection interfaces.

Reviewed source hashes:

| File | SHA256 |
| --- | --- |
| SourceWord.lean | `1b0ece2792e8afc180263817fdfa751cf0b9f30be2071dbd1302c641226403ef` |
| ContractScope.lean | `06856752515bcb3dbcbe5286198037fa7941acc83bf6aa15dd77024d929b38a7` |
| SourceWitness.lean | `4032af4cf1d69c2de97fb5abc1ad201936227d0fc4e961f21a4df84414214a5f` |
| check_source.py | `c848990686adb7309479127515eb7a24d7e204ed90b79a92edd0b14d1a0087f1` |
| generate_source_word.py | `d0560650e969e770670916c0b7089f80012c5c208b01a2381711d3983b526144` |

Packaging note: the implementing agent subsequently added a checked equality between
the original binary COPY charge and its emitted rank in check_source.py. The source
binding was rerun successfully. The reviewed Lean source snapshots are unchanged.
