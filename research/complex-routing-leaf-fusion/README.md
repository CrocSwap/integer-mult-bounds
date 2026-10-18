# A cheaper completed routing frame for the joint twelve-source word

This composes Marius-Paul Dumitrean's [PR #2733](https://github.com/CrocSwap/integer-mult-bounds/pull/2733)
frame refit with both complete words from Tekalign's
[PR #2751](https://github.com/CrocSwap/integer-mult-bounds/pull/2751).
The latter's generated words retain the earlier, more expensive frame. The
composition replaces **1,332 rank-one recursive transports with 666 rank-two
transports**, at unchanged rank mass, physical stock, helper inventory, source
recoveries, dirty-input endpoint and cleanup.

The certified conditional saving is **κ ≈ 0.001717256973467002308270**,
about **0.00671972% above [PR #2751](https://github.com/CrocSwap/integer-mult-bounds/pull/2751)**. The exact rational is the certified
lower endpoint minus `10^-46 + 10^-70`; see [CLAIM.json](CLAIM.json).
This is an incremental paid-cost improvement. The frame refit itself is
credited predecessor work, and the larger difference from the selected
κ = 0.001672660197076918 includes predecessor constructions and their
changed outer contract. The selected record is unchanged.

**Release status:** complete finite native, supplier and modern outer release
passed. Four native provider chains and retained parent admission were run
fresh; the public wrapper then reused their fully authenticated same-session
cache. [VALIDATION.md](VALIDATION.md) records exact commands, coverage and
receipts. The result retains the predecessor's all-size theorem assumptions;
finite checks do not prove the full multiplication theorem.

## What changes and why it reduces the bill

At zero-based B1151, `393 += 515` can use a rank-five common frame instead
of rank six. The exact adjacent frame paths are:

| Register | Before | After | Recursive bill |
| --- | --- | --- | --- |
| 393 | 4 → 6 → 7 | 4 → 5 → 7 | `H2+H1` → `H1+H2` |
| 515 | 5 → 6 → 7 | 5 → 5 → 7 | `2H1` → `H2` |

For `0<p<1`, `2^p<2`, so the second change strictly lowers the paid child
moment. It saves one child per local invocation, without moving that cost
to an inverse, source recovery or idle remainder. Both actual words are
regenerated and checked; matching register numbers alone would not prove
the composition legal. [PROOF.md](PROOF.md) gives the subspace containments,
full invoice, exact moment and inherited assumptions.

New local profile: `{1:2364,2:647,3:297,4:120,5:26,8:8}`.
Complete profile:
`{1:1591740,2:430902,3:204396,4:79920,5:22532,8:5328,32:1,48:26558}`.
The fixed-word coverage relaxation gives a complex cap below
0.001750493235223; the achieved complex endpoint is 98.10132018% of that
upper cap. This is a generic relaxation, not an attainable packing optimum
or a global limit for different words. See [PACKING-CAP.json](PACKING-CAP.json).

Rank mass remains 4,816,512; all 276,390 owner roles, 415 helpers and 72
private buffers remain charged. Live/physical stock is 66,304/66,801.

## Reproduce

The bounded, standard-library replay runs on Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/complex-routing-leaf-fusion
```

It authenticates every consumed predecessor file before import, regenerates
both complete words, checks both arbitrary-input orientations, every frame
and cleanup operation, all owner reservations, the full moment and meaningful
failure controls. `independent_check.py` implements a separate endpoint/frame
checker. `exact_moment_checker.py` independently certifies the adjacent
24-decimal root bracket using rational logarithm/exponential enclosures.
The public-entrypoint controls include a Git-free export, source corruption,
an omitted refit, a typed receipt fault and output-preservation checks.

For complete native/supplier/outer release, install `requirements.txt`
in a separate environment and run:

```sh
python3 -B research/complex-routing-leaf-fusion/full_replay.py --work /tmp/FRESH-routing-leaf
```

The full replay authenticates its pending predecessor sources, derives the
changed runtime in a fresh external directory, and retains the predecessor's
mathematical rejection controls. The readable runtime/admission patches make
the derivative changes reviewable. Exact commands, environment, execution
coverage and any explicit same-session native-cache reuse are recorded in
[VALIDATION.md](VALIDATION.md).

To regenerate only the two candidate words into a fresh directory:

```sh
python3 -B research/complex-routing-leaf-fusion/generate.py \
  --source research/complex-routing-leaf-fusion/vendor/pr2751 \
  --out /tmp/FRESH-frame-words
```

Generation refuses an existing output directory. Verification is read-only;
mathematical equality compares decompressed JSON, not gzip container bytes.

## Scope, overlap and source history

The task began from canonical main
`6b6b3ab304ca60eab7493e73f264fd23c146be4c`, priority revision 5. Initial
complete pagination covered 705 open PRs and 1,393 Discussion/comment/reply
records without warnings. [TASK.json](TASK.json) records scope, subsequent
freshness and the explicit user assignment. The final refresh covered 711
open PRs and 1,400 Discussion/comment/reply records, with complete pagination
and no warnings; see [OVERLAP.json](OVERLAP.json). Metadata search is not proof
of novelty. No public coordination message or selected-frontier change was made.

The initial target was the BIT caller's `O(wV)` route and leaf routines.
The selected complex supplier already binds, so completing that assumed BIT
contract alone cannot change the selected κ at its current precision.
[PR #2399](https://github.com/CrocSwap/integer-mult-bounds/pull/2399) and
[PR #2457](https://github.com/CrocSwap/integer-mult-bounds/pull/2457) already
provide conditional fast-callee and spectator adapters. The single bounded
pivot here targets actual paid complex transport instead. This package does
**not** discharge BIT H2 or supply a new physical fixed-tape compiler.

PR #2751 is pinned at `4cfbb0cc8314d7fb4e8e754545a49a42eb590a69` and PR #2733
at `a63c55ff56aaa8645d64d1162d1f017b59ded42a`. Their earlier scalar words,
source recoveries, frames and outer hypotheses remain credited and explicit.
Only this scoped directory is added. `PREDECESSOR.json`, `CREDIT-PINS.json`
and the full-replay manifests identify exact source hashes and Git blobs.

The all-size compiler, common-label/source access, physical hosting/routing,
precision/fixed-tape, exact recovery, ordinary recursion, bit supplier and
analytic-transfer obligations remain inherited. No measured multiplication
speedup, unconditional theorem, proof-assistant verification, global frame
optimum or independent human review is claimed.

## Open next questions

- Can a changed source or restoration boundary eliminate more paid transport?
  Start from these complete words and price all new source reads, adapters,
  cleanup and owner lifetimes before searching. A local saving is insufficient
  unless the complete bill improves.
- Can an actual route or leaf implementation discharge an inherited physical
  interface? Start with one named fixed-tape boundary and its uniform cost
  proof. The finite words and the source-level BIT caller do not supply the
  complete multiplication machine.

The corresponding structured questions and blockers are in TASK.json.

## Credit

Marius-Paul Dumitrean supplied the rank-five refit; Tekalign supplied joint
twelve-source recovery. Mason Hale's assignments, Philippe Van Velzen's
pre-life hosting, Jeremy Kothe's owner allocation, and the preserved
source-partner, geometry, native, BIT and outer lineage remain credited in
[the original notice](vendor/pr2751/SOURCE-NOTICE) and the unchanged source
exports. This composition does not claim authorship of those mechanisms.

Prepared for David Arias with substantial OpenAI Codex assistance, including
separate mathematical and implementation-checking agents. New work is
Apache-2.0; retained source licenses and notices remain in place.
