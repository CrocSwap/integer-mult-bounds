# Derive idle phase translations instead of storing them

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Result

An opt-in metadata emitter and consumer remove all 2,240 stored
`idle_children[*].translation_after` fields from the pinned DATA-PHASES
document. The consumer reconstructs the complete legacy document and every
ordered idle-child record exactly. Using the same canonical JSON encoding,
the source occupies 814,140 bytes and the new envelope occupies 763,803
bytes, including its schema and original-document digest. The saving is
**50,337 bytes**. This counts uncompressed canonical metadata, not compressed
archive size, runtime, physical storage or a recursive invoice.

Claim type: **finite representation construction with a scoped correctness
proof**. The result answers the representation part of Open next question 1
in Ryanson Jonathan / pinterbanget's [PR4466](https://github.com/CrocSwap/integer-mult-bounds/pull/4466).
The phase formula is that predecessor's result. The new contribution is its
two-bit-plane implementation, compact producer, legacy-record consumer and
complete source-instance reduction. No phase identity or predecessor result
is re-audited as a deliverable.

The source is historical QQ16/P112 data. This package does not install the
adapter in a physical native caller or change selected PR6030. It removes
stored values, not the required physical translations. No new kappa follows.

## Construction and proof

The input is a JSON object with dimension `m`, a declared port count and
ordered recipes. Each recipe contains its port normal `q` and ordered idle
children. Every child contains its rank, ordered binary row masks and a
translation. Other metadata is carried through unchanged. The admitted
schema is bounded in `codec.py`; invalid ranks, duplicate ports, noninteger
rows, incomplete supported frames and nonorthogonal frames fail explicitly.

Retain PR4466's frame convention. Prepend `q` exactly when the child axes
meet the first nine port bits. The resulting rows form an orthonormal basis
on their coordinate support. For each column let `c_i` be its integer count.
The cited formula is `t_i = [c_i = 3 modulo 4]`. Empty children have tag zero.

The following accumulator evaluates that formula without column counters:

```text
low = high = 0
for row in rows:
    high = high XOR (low AND row)
    low = low XOR row
return high
```

After every prefix, bit `i` of `low` is `c_i modulo 2`; bit `i` of `high`
is `floor(c_i/2) modulo 2`. Initially this holds for zero counts. Adding a
row toggles the low bit in its active columns and carries to the high bit
exactly when the OLD low bit was one. This proves the invariant by induction,
including wraparound from three to zero. An orthogonal square matrix has
odd column weights, so its final high bit is precisely the cited tag. This
is a standard binary counter specialization, not a new phase identity.

For `r` rows of width `m`, synthesis uses exactly `r` ANDs and `2r` XORs on
two `m`-bit state integers. Input rows, frame validation and document parsing
are additional work. This operation count is not a physical machine tariff.

`encode` copies the document, verifies that every supplied translation equals
the derived value, and removes just those fields. It encloses the payload
with a versioned schema and the SHA256 of the original canonical document.
`decode` rejects stored translation fields in its compact input, reconstructs
them from the frames, and checks that digest. For every admitted encoder
input, every deleted value is therefore restored to the same value; all
other keys and array orders are preserved. Hence `decode(encode(D)) = D` as
JSON values. This equality follows from construction, not a hash-collision
assumption. The digest is a corruption check, not independent authentication.

`events` first validates the complete decoded envelope, then yields
`(port, child_index, legacy_child)` in original order. No record is released
before validation finishes. The JSON input and restored document are held
in memory. "Stream" means the ordered consumer records; this is not an
incremental constant-memory JSON parser. Object-key ordering and the source
file's final newline are normalized; byte-exact original whitespace is not
part of the round-trip contract.

## Evidence and reproduction

CPython 3.12 and its standard library suffice. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/derived-phase-stream/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/derived-phase-stream/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/derived-phase-stream
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/derived-phase-stream --check-source-history
```

Any CPython 3.12 interpreter can replace the local path. Direct checks accept
`--scratch EXISTING_DIRECTORY` to contain temporary CLI fixtures. The replay
prints `PASS_DERIVED_PHASE_STREAM` and a freshly computed receipt bound to
every package file and live input. It stores no receipt in the checkout.

The exact new-construction checks are:

- The full source document and all 2,240 ordered consumer records round-trip;
  encoding is stable and the encoder does not mutate its input.
- A separate column-sum oracle covers every row sequence of length zero
  through five in widths one through three: 38,877 cases. Four further
  cases exercise 129 rows at widths 9, 73, 128 and 256.
- Eighteen API rejection controls cover wrong supplied translations, schema,
  digest, retained compact fields, invalid or incomplete frames, rank,
  port normal, unrelated metadata, record order, duplicate JSON keys,
  input capacity, row capacity, negative masks, overflow and booleans.
- The real optimized CLI executes encode, decode and ordered events, with
  byte-for-byte expected canonical output. A malformed envelope exits two
  with empty stdout before releasing a record.

The full source reconstruction is verification of this new codec, not a
claim of fresh scientific coverage of the inherited phase identities. No
predecessor scientific executable is imported or run. [SOURCES.json](SOURCES.json)
authenticates the live source and the cited question; catalogue and selected
record pins are historical provenance.

## Limits and code bounds

The universal statement is the scoped encoder/decoder proof above. The byte
reduction is a finite certificate for this one source document. A new frame
convention or a partial frame outside the declared coordinate support needs
a different derivation. The adapter does not infer native admissibility from
its structural frame checks. It preserves all other source claims as opaque
metadata and does not certify them.

The CLI accepts at most 2 MiB, 256 ports, 64 children per recipe, 128 supplied
axes per child and width 256. The port block remains exactly nine bits.
All explicit loops have these bounds or fixed finite verification domains.
Functions fit within 60 lines, use no recursion or dynamic code generation,
and keep checks active under optimization. The CLI reports parse and
validation errors before writing output. Verification subprocesses have
30-second timeouts and run only the fixed local codec with the current Python.

Power of Ten rule 3 deviation: Python, JSON and arbitrary-precision integers
allocate dynamically. Bounded byte sizes, dimensions and fixture counts
bound live objects; a fixed-allocation implementation is not supplied.
The JSON decoder's fixed duplicate-key hook and the verifier's fixed
negative-control callbacks are rule 9 deviations. Warning-strict normal
and optimized execution provide runtime diagnostics. Ruff is unavailable
in the local interpreter; no static-analyzer result is claimed.

Physical metadata access, validation, coefficient preparation, routing,
rounding, restoration, stock/tapes, compiler, full supplier and outer costs
remain unpriced. All five selected framework assumptions remain. Selected
cold replay, native replay, Lean and Docker were not run.

## Open next questions

Can one actual native consumer read these reconstructed records without
recreating the full document? Start with one caller's literal idle-child
access and count parsing, validation, tag synthesis, data movement and
restoration. A complete physical caller and its access contract are the
blockers. This package supplies a legacy-record adapter, not that integration.

## Credit and coordination

Credit Ryanson Jonathan / pinterbanget #4466 for the forced-translation
formula and explicit construction question; Mihir Srivastava / mihir-s-05
#4464 and Mark / Matarener #4457 for stage-zero context; ToikY #4002 and
Chris R / Clear1nsight #3987 for distinct native phase-tag conventions; and
the retained QQ16/P112, Cinna Davis, zxv, native and compiler lineage.
Those formulas and their original notices are unchanged. No global
literature-priority claim is made for counters, derived metadata or JSON.

The `formal-interface-lemma` card changes to this representation side result,
rather than formalizing a selected assumption. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. Selected
baseline binding orientation passed. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371077).
The overlap helper covered 521 open PRs and 6,525 Discussion records with
complete remote pagination. Main/merged object and general-form searches,
recent account work and local reservations supplemented its sparse local
notes. Unpublished work and arbitrary diffs remain outside that coverage.
The first verified representation improvement ends the construction work.
