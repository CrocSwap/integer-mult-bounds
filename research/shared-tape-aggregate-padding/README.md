# Aggregate padding on eight tapes

A shared-head counter layout reduces the twelve-tape interface of
[PR6151](https://github.com/CrocSwap/integer-mult-bounds/pull/6151) to eight
tapes, while retaining D mutable counter bits and a uniform complete action
bound of `256N+32D+256`. This is a scoped constructive proof with finite
corroboration, produced by Nick Petalas. No new kappa is claimed.

Five immutable descriptor tapes, one shared counter tape and two payload
tapes implement both lexicographic zero padding and restriction. Work, input,
descriptors and all eight head positions are restored as specified; output
is retained. Canonical descriptors, owned delimited zero work and fresh output
are entry premises. [PROOF.md](PROOF.md) gives the exact contract and proof.

Counter blocks lie in carry order, fastest first. A forward/back crossing
beside an L-bit counter costs exactly `4L+8`. Each such traversal follows a
complete inner cycle. Since `4L+8 <= 8*2^L`, all four adjacency edges cost at
most `32N` actions over a full scan, including empty blocks. This resolves
the predecessor's second open next question about serialized counters.
The contribution is tape reduction with linear movement. Its sufficient
action bound is larger than the predecessor's `192N+16D+80` bound.

## Reproduce

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/shared-tape-aggregate-padding/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/shared-tape-aggregate-padding
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/shared-tape-aggregate-padding --check-source-history
```

Another CPython 3.12 path may replace the local interpreter. The direct verifier
also runs without Git or repository inputs. Its expected marker is
`PASS_SHARED_TAPE_AGGREGATE_PADDING`. Normal and optimized warning-strict
commands are registered. Each prints a generated receipt bound to package
file hashes and writes nothing.

The checker covers 700 full scan cases, 348 exhaustive payload scans, 1032
adjacent-block navigation pairs and fifteen rejection/mutation controls.
Some full scan cases immediately reuse the same restored work and descriptors.
Every successful scan checks the separate rectangle oracle, eight distinct
tapes, one actual work head, immutable inputs, protected cells, D zero work
bits, unchanged delimiters, every head return and the complete action bound.
These finite tests corroborate the written uniform proof.

## Scope and provenance

The original `uniform-transfer-audit` card is changed to this local physical
resource construction, relevant to `precision_tape` and `owned_erasure`.
It does not discharge either selected assumption. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. The selected
metadata orientation passed; no selected scientific replay is claimed.
[TASK.json](TASK.json) records the change and structured next questions;
[SOURCES.json](SOURCES.json) pins exact historical provenance. No external
live or executable input is required by the new standalone checker.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19441197)
preceded implementation. Live open PRs, this account's recent work, handoffs,
local locks, main README text and merged searches were checked. Distinctive
terms included shared physical work tapes, serialized counters, aggregate
padding and eight tapes. The cached card scan has incomplete sparse-note
coverage. Empty searches do not establish novelty. The older source question
was reserved before work; no recent result from this account is extended.

## Limitations

Allocation, descriptor construction, ancestor parking, the completed fast
callee, selected caller integration and the complete supplier invoice remain
external. Successful well-formed calls are covered; hostile parsing and
failure restoration are outside scope. No minimum-tape or optimal-action
claim, wall-clock speedup, compiled transition table, formal kernel, new
supplier, selected frontier change or complete multiplication theorem is given.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Can an actual completed exchange integrate the eight-tape scan within its
  simultaneous tape and parking inventory? Bind the literal callee's entry,
  output and cleanup contracts first. That physical callee remains external.
- Can the five immutable descriptors also share a tape without losing the
  complete linear bound? First price simultaneous descriptor/work navigation
  at every phase change and carry. This construction shares only counter heads.

## Credit

This contribution is produced by Nick Petalas. His PR6151 supplies the
local two-phase coordinate countdown and the explicit shared-tape question.
ywz65's PR2636 supplies the seventeen-tape aggregate scan, and PR2457 the
aggregate-before-padding reduction. commdata2338/PR2399, Jose Manuel/PR2234
and Adam Gall/PR2087 retain the earlier descriptor, parking and supplier
credit. Binary countdown amortization is classical. The new step is the
serialized physical head, its travel proof and the eight-tape implementation.
All predecessor files and credit lines are unchanged. Apache-2.0.
