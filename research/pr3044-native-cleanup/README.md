# PR3044 R2: native cleanup and all private zero returns

The complete R2 cleanup realizes its literal source operator, and all **91
clean private arrays return to zero before their actual frees**, for arbitrary
live entrance arrays, in both orientations. This is a source-bound finite audit
of Nick Petalas's [PR3044](https://github.com/CrocSwap/integer-mult-bounds/pull/3044),
head `1f922b25abff2d7fd87fa5b29619160862a06b59`. It adds no construction,
storage saving, supplier admission or kappa improvement.

The native identity covers the 5,208-gate cleanup body. The later residual post
adapters are bound to their positions but their semantics are not rechecked
here. The clean-return proof does not depend on the earlier prefix establishing
a special reachable state. Restoring the invocation's original live inputs,
physical ownership and complete supplier admission remain separate obligations.

## Result

Both authenticated providers give these counts, per orientation:

| Check | Forward | Inverse transpose |
| --- | ---: | ---: |
| Source-bound cleanup scalar gates | 5,136 | 5,136 |
| Native FULL-frame warp occurrences/classes | 72 | 72 |
| Complex basis columns per native identity | 512 | 512 |
| Arbitrary live entrance arrays in the zero-return proof | 632 | 632 |
| Private allocations / verified zero frees | 91 / 91 | 91 / 91 |
| Unchanged target rows | 112 | 112 |
| Changed live rows at the end of the cleanup body | 429 | 397 |
| Residual post adapters, bound after all frees | 195 | 195 |

All 5,585 cleanup-phase events are bound, including allocations, body, frees
and post adapters. The leading 204 source gates are independently checked as
the reversed inverse of R2's restore after private-role substitution. The
new checker separately checks all 72 used native recipes per provider and
their conjugates; exact cross-provider reuse leaves **76 distinct source-bound
recipes**, so the four differing records are not silently shared.

[RESULT.json](RESULT.json) contains the exact classes, whole-live-boundary
digests, counts and **52 named semantic rejections**. Faults are applied after
authentication and must reach their named semantic check, rather than merely
fail a file hash. [PROOF.md](PROOF.md) gives the composition and zero-return
argument and makes its interface assumptions explicit.

## What is independently checked

The new `verify.py` derives compact/private namespaces, matches every cleanup
event, checks private lifetimes, and propagates exact rational rows over a free
noncommutative operator algebra. For native arithmetic it reuses Sagar Thakrar's
pinned [`clifford.py`](../frontier1094-recipes-exact-seed76/clifford.py), the
separate standard-library Gaussian-integer audit kernel also credited by the
earlier native audits. The producer, compiler and original cleanup evaluator
are never imported or executed. Independence is from that producer, not from
the reused audit kernel or from the source's operator convention.

For each source G, finite enumeration derives its inverse and quadratic phase.
The actual serialized monomial is checked against `F9 K_G^sign F9^-1`, including
global phase. Componentwise rational scalar gates commute with the common
FULL change of coordinates, so these identities compose through the complete
cleanup body. A separate exact row calculation proves every private free is
zero for all 632 independent live entrance vectors. Substituting the verified
native operators preserves those zero identities.

The mathematical methods have predecessors. This package's delta is the
complete R2 native cleanup binding and its combination with prefix-independent
clean return, not a new free-group method or a new Clifford kernel.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/pr3044-native-cleanup
python3 -I -O -B research/pr3044-native-cleanup/verify.py
```

Expected marker: `PASS_PR3044_NATIVE_CLEANUP`, followed by the registered
package PASS when using the first command. Normal replay is read-only and
requires no network, native generation, NumPy or solver. `verify.py --emit`
prints a freshly recomputed deterministic receipt without comparing it with
the saved result. The default command recomputes and compares all fields.
Execution evidence is recorded in [VALIDATION.json](VALIDATION.json).

Five compressed files in `data/` retain the six relevant native artifacts
(the identical LOCAL-PROGRAMS is shared). These are reused from the fresh
PR3202 generation, **not regenerated in this session**. Every source word and
original native payload is authenticated against PR3044's published native
receipt on main. For newly compressed JSON the check uses original uncompressed
bytes; immutable original gzip inputs retain their raw hashes. The complete
original archives are preserved even though only cleanup-related native
recipes are interpreted.

The optional original producer regeneration is documented in
[PR3202's reproducible package](https://github.com/24kHandsome1201/integer-mult-bounds/tree/259043321323717b7e816d6be38ad5e1f0b69b4c/research/pr3044-r2-native-slice).
Its generation is distinct from this independent verification. No complete
13-stage native/supplier/outer release was repeated here.

## Scope and overlap

This answers [PR3202's released cleanup handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3202),
following Hiroki Kumazaki's PR3146 external cold replay. PR3202 checked the R2
tail children, four source adapters and residual wrappers; it explicitly left
full cleanup semantics open. PR3146's full replay retained the original native
implementation.

ToikY's PR3038 V45 cone audit is overlapping predecessor work. Its retained
PR2979 receipts list 30 FULL cleanup warp classes forward and 8 backward per
provider. [OVERLAP.json](OVERLAP.json) records that observed receipt inventory;
it is not a fresh replay or a proof that classes from different source heads
are interchangeable. This package checks all 72 classes each way on R2.

commdata2338's active
[PR2979 peer-private-free investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19001873)
was read before claiming this scope. It concerns the earlier V45 dependency
cone; the present module concerns complete R2 cleanup and its actual native
operators. Their [earlier PR2269 buffer-pooling package](../t74-cleanup-buffer-pooling/README.md)
already uses a prefix-independent free-group cleanup argument and retains that
credit. No exclusivity or priority for general private-free auditing is claimed.

Canonical main was refreshed to `463113d675af7410ac91d53a4fed51ec6494eb9a`,
priority revision 6. The selected result remains unchanged. The bounded PR,
local-note and Discussion coverage, original card and exact next steps are in
[TASK.json](TASK.json). Unpublished work and complete historical diffs are not
covered. [Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19001947).

## Open next questions

1. Complete the actual R2 native prefix and compose its live endpoint with
   this cleanup. Start with the remaining source-bound native classes and
   PR3202's existing slice. Private clean return is now independent of this
   premise; original source/helper restoration still needs it.
2. Bind one real executor Z allocation/free interval to its physical owner,
   scalar/warp accesses and complete movement/precision bill. Clean algebraic
   return alone does not supply owned storage, routing or a stock saving.

Other child/center/adapter semantics, physical executor/ownership, precision
and tape, uniform all-size compilation, caller/analytic contracts and complete
supplier/outer admission remain open. The contribution does not validate a
newest candidate or update the selected frontier.

## Credit

24kHandsome1201 with substantial OpenAI Codex assistance for analysis, code,
execution and writing. Solo agent; no independent human or proof-kernel review
is claimed. The result is author-checked independent code relative to the
producer. Apache-2.0.

Credit Nick Petalas (R2 and release), Jeremy Kothe (R1 and cleanup lineage),
Marius-Paul Dumitrean (joint rank-7 construction), Hiroki Kumazaki (cold replay
and handoff), Sagar Thakrar (reused exact kernel), ToikY (V45 native cone),
commdata2338 (prefix-independent cleanup/pooling method and concurrent private
free audit), and Cinna Davis (native warp convention). Retain Mason Hale,
Jeremy Diviney, Yiyang Lu, Tekalign, Ross Richardson, DreamingOfClouds,
icekylinx, chafreaky and the native/geometry/owner lineage credited by the source.
Original [credits](../rank7-shared-restore-fanin/vendor/PR3015-CREDITS.md) and
[notice](../rank7-shared-restore-fanin/vendor/PR3015-NOTICE) remain unchanged.
