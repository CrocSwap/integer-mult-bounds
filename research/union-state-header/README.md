# Minimum exact state headers for sparse-union records

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written construction and sharp information bound, with
exact finite corroboration. No new kappa is claimed.

For a shared context of g axes, side L>=2 and boundary sets E_i of sizes a_i,
the full legal coordinate/tag header domain of Mihir Srivastava's
[PR4583](https://github.com/CrocSwap/integer-mult-bounds/pull/4583) has exactly

    N = L^(g-1) (L + sum_i a_i)

states. The new mixed-radix codec uses the minimum possible fixed width

    H* = 2 + ceil(log2 N)

including the retained two-bit marker. It recovers every coordinate, flag,
canonical ordinal, count and tag. The minimum covers arbitrary encoders with
individual exact decoding under the same fixed shared context.

For h=ceil(log2 L), b=ceil(log2(g+1)), this saves at least gh+g+b bits against
the predecessor's separate-field format. At L=16, g=4 and E_i={0,15}, all
98,304 legal states fit in 19 bits including framing; that format uses 44.
[PROOF.md](PROOF.md) gives the disjoint-tag count, matching lower bound and
attaining rank/unrank construction. [codec.py](codec.py) implements it.

The source metadata contract is a cited premise. Its codec, schedule and
scientific results are not replayed or audited. The new finite enumeration
checks the new representation directly against the legal-state definition.

## Evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/union-state-header/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/union-state-header/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/union-state-header
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/union-state-header --check-source-history --check-modes
```

Substitute another CPython 3.12 executable on other machines. Direct replay
prints PASS_UNION_STATE_HEADER and a generated JSON receipt bound to every
package file and both declared source inputs. It writes nothing.

The finite domain includes every boundary subset and every legal state for
L=2 with g=1..4, L=3 with g=1..3 and L=4 with g=1..2. It enumerates 1,196
contexts and 57,744 legal states, checks 105,120 retags and their line keys,
and rejects all 22,022 unused codes within those record widths. Sixty larger
rank/serialization round trips reach L=2^4096 and g=32. Twenty-seven explicit
controls reject malformed contexts, coordinates, tags, indices, framing,
rounds and mismatched line keys. A collision control retains the distinction
between active and sentinel tags on the same coordinates. A legal substitution
control makes explicit that this is not an error-detecting code.

Normal and optimized commands execute the same always-enabled contracts.
Registered replays are bounded individually by 120 seconds. The universal
conclusion rests on the written proof, not on a finite census.

## Scope, credit and overlap

The shared boundary sets are decoder context. Rank/select access, arbitrary
precision arithmetic, context storage and temporary space are not free in a
physical implementation. Retagging may rewrite the entire index. The old
format's tag-local update and direct metadata fields are not preserved as
locality guarantees. No faster reader, fixed-tape saving or complete emitter
is supplied. Context boundaries remain necessary, and payloads are untouched.
The result does not implement an arbitrary-dirty reversible retagging map.

Credit Mihir Srivastava / mihir-s-05, PR4583, for the precise metadata contract
and separate-field header. Retain Cinna Davis / PR4100, Jeremy Kothe / PR1731,
Vlado Vojdanovski / PR1673, Ryanson Jonathan / PR4327 and PR4590, unpaidmoon /
PR4376, rtyu193-rgb and LeverRank's schedule, layout and review lineage.
Enumerative coding, mixed-radix indexing and the pigeonhole principle are
classical. This contribution applies them to that interface and supplies the
smaller exact codec; no general literature-priority claim is made.

Canonical base is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8,
selected PR6030. SOURCES.json binds the unmodified contract and field-codec
bytes. The card changes from a selected-assumption audit to this representation
side result for precision_tape. The source-binding orientation passed.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375380)
records the target and stop rule. The cached overlap snapshot covers 572 open
PRs and 6,641 Discussion records with complete reported remote pagination.
Only 141 of 8,917 local note paths were materialized. Separate main-wide
README searches and live merged/general-form searches supplement that sparse
coverage. Historical diffs and unpublished work remain limits.

No selected cold replay, Lean or Docker run is needed for this side result.
All five selected framework assumptions remain. Independent human and formal
proof-kernel review are unclaimed. This is not a physical supplier, selected
frontier change or complete multiplication theorem.

## Open next questions

Can an actual union invocation use this representation with a favorable full
reader, emitter and retagging bill? Start with one carving description, bind
rank/select access, and charge every header rewrite and temporary through one
round. Missing bit-level decoding, context delivery and complete caller costs
block an operational saving. TASK.json records this handoff explicitly.

## Code bounds and diagnostics

The codec has at most 32 axes, 128 entries per boundary and L<=2^4096, giving
at most 131,078 index bits and 131,080 serialized bits. No coordinate box is
materialized by rank/unrank. Each codec loop has at most 32 iterations, and
boundary validation operates on at most 128 entries. The exhaustive verifier
retains at most 108 ranks per context. Its context and fixture domains are
fixed as listed above. Source reads are capped at one MiB and the manifest
at sixteen rows; the package receipt covers seven fixed filenames. Functions
stay below sixty physical lines. Warning-strict normal and optimized replay
provide the available runtime diagnostics; no unavailable static analyzer is
claimed as run.

Power-of-Ten rule 3 has a managed-runtime deviation in codec.py and verify.py.
Python allocates integers, strings, tuples, sets and JSON values during the
run. The enforced dimensions, integer and header lengths, bounded live rank
set, capped input reads and streamed contexts bound their sizes. This is not
a static-pool or byte-exact heap bound. Reassess these bounds before enlarging
the capacities; a fixed-pool backend would be a separate implementation.
Rule 9's verifier callback deviation is confined to explicit negative-test
calls to Layout and its encode, decode, unrank, retag and line_key methods.
No dynamic code or unbounded dispatch is accepted. Normal and optimized
negative controls exercise every listed target. Production codec calls are
direct, and decoded Header values and boundary tuples are immutable.
