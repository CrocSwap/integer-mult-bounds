# Delimited continuation for sixteen local payload roles

This supplies a concrete delimited push/pop primitive for the missing control
stack in [PR5329](https://github.com/CrocSwap/integer-mult-bounds/pull/5329).
It restores sixteen parent payload heads, all parent bytes, role occupancy and
an opaque binary descriptor by sequential tape operations. No saved absolute
origin, frame length, numeric return offset or parent object is supplied to
the controller. Nineteen physical tapes suffice at every finite nesting depth.

The header records each head-to-end distance in unary while moving that head.
For parent descriptor length d, total return distance H, and current child
payload-plus-descriptor length W, one matched push/pop costs at most

```
24d + 12H + 576 + 8W
```

symbol reads, symbol writes and unit moves, including all child cleanup.
Its live control frame has exactly `d + H + 35` symbols. The written induction
and sharper exact action formulas are in [PROOF.md](PROOF.md); finite checks
corroborate them. This is a completed **primitive** result, with source caller
integration still partial. It establishes no supplier admission or new kappa.

## Scope and evidence

PR5329's `Arena.child` keeps `(origins, parents, descriptor)` in a Python list;
its `6D` descriptor tariff assumes already known frame boundaries. This package
answers a narrowed portion of its released [physical-continuation handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/5012#discussioncomment-19151249).
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5012#discussioncomment-19152934)
states that source sizes/handles and child-output delivery remain separate.

The new result is local delimiter construction and restoration for that
sixteen-role binary contract. Unary storage is bounded by the parked payload
size because H <= sum s_i. Given separate caller bounds d+sum s_i+W=O(V),
the primitive's complete action bill is O(V), independent of ancestor lengths.
This provides the requested local-cost implication; it does not prove those
size bounds for every production packet or supply the whole node's tariff.

[RESULT.json](RESULT.json) records the deterministic normal replay:

* 1,935 cases exhaust binary words of length 0 through 4, every legal head,
  and binary descriptors of length 0 through 3 on one varying role. Twenty
  further cases distinguish occupied-empty and absent-empty role masks.
* Seven nested unequal frames restore complete snapshots at every return,
  for dirty ancestor lengths 16, 257 and 4096. Action counts are identical
  across those lengths; no ancestor payload or prior control-frame is scanned.
* Six actual-source calibrations execute unchanged PR2250 `compact.execute`
  twice at nested levels, on complete reduced 128-record f=2 rectangles in
  both field orders. All sixteen enclosing payload roles restore. The source
  work peaks at ten live roles. Each inner matched boundary costs exactly
  16,672 actions, including cleanup, for all three ancestor lengths.
* The exact retained BOUNDARY.json and RIGHT-RECIPE.json bytes also round-trip
  as one long opaque descriptor with all sixteen roles active. This tests
  byte preservation, not production dispatch or recipe semantics.
* Nine failure controls reject malformed top/row/descriptor delimiters,
  excessive return distance, an absent nonempty parent, a nonbinary descriptor,
  omitted head return, wrong descriptor data and uncharged moves. Mutant
  detection is not an authenticated or transactional corruption contract.

The controller uses only current-symbol read/write/unit-move methods. Python
absolute addresses, snapshot lists and expected permutation outputs belong to
the simulator and test oracle. The source-calibration facade still uses
Python logical size/head counters and weak-reference handle allocation. It
does **not** claim to replace those with physical source metadata or compile
the source's entire call stack. In particular, returned output is discarded
by pop unless the caller delivers it first; output delivery has a separate
cost and is not implemented here.

The immutable event8814/family65689 descriptor and offset426/phase1 recipe
are authenticated as predecessor inputs. The actual production phase/affine
recipe, e147 packet, recursive C, complete source role compiler and outer
admission are not replayed. PR5329's separate phase-fibre evidence is not
claimed as new coverage. No Lean, Docker, selected cold replay or complete
multiplication-theorem verification ran.

The base is canonical main `7c472563474e60185e6ca101a17622133d047e56`, priority
revision 7. PR5329's scientific head is
`08456995d5e520a4f9e0501c9b2ea9b03dbae87a`; its retained bytes are unchanged.
[SOURCES.json](SOURCES.json) pins every imported source and scope reference;
the verifier checks the ten live hashes before importing predecessor code.
It executes those captured source bytes directly, bypassing bytecode caches.
The catalogue and selected record are historical provenance. The selected
baseline helper reported 497 omitted inputs in the sparse checkout; no
selected-source closure pass or selected cold replay is claimed or needed
for this isolated primitive.

Entry overlap covered 305 open PR bodies and 4,633 Discussion records with
reported complete remote pagination (19:03/19:05 UTC, 2026-10-23), plus 4,519
local notes. The sparse checkout omitted 2,748 tracked notes; relevant retained
predecessors were read explicitly. No code-diff census or unpublished-work
coverage is claimed. The existing fixed-bank recursive-row caller uses a
one-bit dyadic continuation; the PR3385 parent-return audit covers dense
parking. Both are credited precedents, not the same descriptor/head contract.

The submission refresh retained the same canonical main and unchanged
guidance/inputs. Its remote snapshot covered 310 open PRs at 19:20 UTC and
4,641 Discussion records at 19:21 UTC. A supplementary Git-tree search across
all top-level package READMEs checked continuation/physical-stack/unary-distance
terms, including sparse omissions; the additional hits concern different BIT
coefficient stacks or scoped logical lifetimes. This supplements the stated
search coverage without claiming novelty or arbitrary-diff coverage.

## Reproduce

From the repository root with CPython 3.12 and only the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/segment-continuation-stack --check-only
python3.12 -B scripts/research_package.py --package research/segment-continuation-stack
```

The registered manifest runs normal and optimized verifiers, each capped at
60 seconds. Direct replay is `python3.12 -B research/segment-continuation-stack/verify.py`.
It prints fresh JSON and never rewrites its inputs or receipt. An official
package export retains the repository-relative declared inputs and supports
the same direct command without Git. The stored receipt is evidence of one
run, not an input to the proof decision. All new files remain in this package;
no source archive, shared verifier or selected record is changed.

Validation on CPython 3.12.0, 64-bit Windows 11: metadata/source pins and both
registered modes passed. The committed-byte preflight passed after normalizing
three working JSON files to their committed LF bytes. The official 18-file
export and integrity check passed. Normal and optimized Git-free replays with
an empty PATH reproduced RESULT.json and left all exported file bytes unchanged
(6.30/6.22 seconds on this machine). A byte-corrupted exported predecessor was
rejected by source authentication before predecessor execution; the frozen
repository source was never edited. Full source-history preflight was not run
in this shallow checkout. These local checks are not hosted CI or scientific
acceptance.

## Open next questions

1. **Bind the source's logical counters and lexical handles.** To replace the
   whole Python oracle rather than its physical segment state, construct the
   exact finite metadata/slot schedule through `repair`/`stable_radix` and one
   nested call. First audit the maximum live cut against the sixteen-slot
   contract. No external dependency blocks this; it is unimplemented here.
2. **Deliver one actual child output before pop.** Bind its source role and
   parent packet destination, then give an explicit sequential transfer and
   ownership bill. This matters because cleanup deliberately erases all child
   work. The finalized production packet/recursive-child return ABI is needed.
3. **Compose the complete caller invoice.** Establish descriptor, payload and
   child-retirement size bounds at that concrete caller, including source
   metadata and the output-transfer bill. Only then substitute the local O(V)
   bound into a full node/stock/recurrence argument. No new construction search
   is justified by this primitive alone.

## Credit

JoyboyBrian supplied PR5329's segment refinement, the released continuation
question, PR5041's locality invoice and the fixed-bank recursive-row precedent.
Jose Manuel (`jmbarrancoml`) supplied PR2250's compact/monomial implementation;
Douglas Colkitt supplied the compact identity, guard and repair construction.
Cinna Davis supplied the #4100/#4088 framework, Matarener the cover/stock work,
and Sagar Thakrar the PR3385 parent-return audit. The fixed-bank precedent
credits commdata2338's recursive parking and retained Lean push/pop authors.
Full source notices, including the carry/guard and selected native lineage,
remain in the pinned [predecessor NOTICE](../complex-segment-boundary/source/NOTICE.md).

The new controller, proof and checker were prepared for `mihir-s-05` with
substantial OpenAI Codex assistance, under Apache-2.0. No novelty claim is made
for stacks or unary counters. The contribution is the specified contract,
complete local invoice and source-bound calibration. This is author-checked
AI-assisted evidence; independent human review and formal-kernel acceptance
are unclaimed.
