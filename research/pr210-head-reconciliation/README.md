# PR210: reconcile the reviewed source527 checkpoint with its parity/fusion update

**Research consolidation and fresh finite replay; no new κ.** The central
ledger leaves PR210 open with 147 paths lacking byte-identical incorporation.
Those are **19 post-review changes plus 128 paths already present at the
reviewed head**. The latter remain a separate incorporation question. This
contribution identifies the exact transition, reconstructs its source closure,
replays it, and checks the stream rewrite with a separate implementation.

The replay reproduces eumemic's already submitted historical conditional
κ = `710069340338651/1000000000000000000` = **0.000710069340338651**.
The historical imported checkpoint remains **0.000710046193349537**; the
selected result at our base remains **0.001661634653669567**. No selection,
historical source package, central disposition, or `upstream/` file is changed.

## Exact scope and provenance

| Object | Pin |
|---|---|
| Main base | `91a2094f2e022930069e8cfdc810a3ea1b81cd09` |
| PR210 reviewed/imported head | `298f7c112889f799e8e2040099fbc325d0ccd0f6` |
| PR210 current head checked here | `b0c058ba979c748bb3a8604bfb6502e9fac9b84d` |
| Historical package manifest SHA256 | `d51e8cc118ef245e100ae74f4029d80371b8309e3e58daaff9983311c79a8780` |
| Current package manifest SHA256 | `3851372231a7baaa86e1abd8b41407aab7450c2d76d0487f1fea4f806f70c90b` |

The current commit's sole parent is the reviewed head. [PINS.json](PINS.json)
records every changed file's old/new Git blob and SHA256, and the 128 unchanged
unresolved Git identities. The historical package has 121 manifest inputs;
the current one has 127. Their root manifests are additional files.
[source-delta.patch](source-delta.patch) is the unedited 16-file package diff.
Applying it to the retained historical package reconstructs all 127 current
inputs exactly, without fetching a branch or overwriting historical evidence.
The three other changes are the author's certificate and replay/publication
receipts, preserved under [submitted](submitted/). They are predecessor
evidence; our execution receipts are under [evidence](evidence/).

The reconciliation separates two questions that the prior records already
distinguished but had not resolved at this granularity:

| Central comparison at the pinned snapshot | Paths |
|---|---:|
| Whole branch diff | 260 |
| Already matched in main/archive | 113 |
| Unresolved paths | 147 |
| Of those, changed after the reviewed head | 19 |
| Of those, byte-identical at both PR210 heads | 128 |

The 128 comprise 113 `coordinated-crossover-pr200` files, 13
`balanced-nullity-banks-163` files, one earlier frame-semantics note, and one
workflow. **Unchanged does not mean reviewed or incorporated.** Their
remaining integration obligations are not discharged here. This is a
supplement to [the historical review](../../docs/research/community-pr210-review.md)
and [the ledger](../../docs/research/pr-ledger.md), not an authorization to close PR210.

## What the 19 changes do

- `parity_transform.py` removes even-coefficient F₂ payload additions and fuses
  nested same-stream moves between retained uses. It independently recounts
  required frames and checks reflected annihilator inclusions.
- `portable_bit.py` retains the original producer, then checks the emitted word;
  `raw_ledger.py` binds the new profile to the producer ledger.
- `scalar_check.py` checks the new F₂ projection and inverse, retains the
  original signed-integer producer checks, and obtains new signed-lift prefix
  bounds for the emitted word. It does **not** claim their integer endpoints agree.
- `bank_check.py`, `finite_check.py`, and `verify.py` update the affected child
  counts, full finite invoice, prefix bounds, and exact final certificate.
- The manifest and three narrative files bind/explain that change. The new
  parity contract and four primary-source files preserve the scalar/address
  distinction, source provenance, and Apache-2.0 license.
- Three top-level submitted receipts record the author's changed result.

The complete source diff is 19 files: 16 package files and three receipts.
The address geometry implementation, five-stage global lowerer, bank template,
complex supplier, and moment/outer engines are unchanged between these heads.

## New evidence

The cold native replay passed all eight mandatory stages in **503.9 seconds**
on Python 3.14.6, SymPy 1.14.0, macOS arm64. It retained all 127 source inputs,
reproduced the submitted exact certificate, checked all 20,107 formal scalar
columns in both directions, and reran the predecessor's controls. The signed
producer, prime/basis checks, physical banks, complex supplier, finite bill,
two moment engines, and all 47 strict outer constraints were included.

[stream_audit.py](stream_audit.py) imports none of the PR210 implementation.
It reads the fresh producer/emitted instruction arrays, retains the exact
ordered non-MOVE operations after discarding even **payload ADDs**, and
compares each stream's trace with adjacent moves telescoped between retained
uses. It compares 20,108 stream traces, including the temporary COPY stream.
Complete projected traces are compared directly; hashes only summarize the
accepted traces in the receipt.
Thus movement may commute with disjoint streams but cannot cross a retained
read/write or COPY/ERASE boundary. Address frame IDs and COPY ranks are not
reduced modulo two. The native replay separately supplies geometric admission.

| Quantity | Before | After |
|---|---:|---:|
| Local instruction records | 2,668,360 | 885,161 |
| Payload additions | 2,569,817 | 786,621 |
| Copied-center episodes | 24 | 24 |
| Local paid rank mass | 434,502 | 434,502 |
| Five-stage unbanked calls | 494,994 | 494,979 |
| Normalized final calls | 5,912,580 | 5,912,400 |
| Literal final children | 29,562,900 | 29,562,000 |
| Literal final stock | 1,304,935 | 1,304,935 |

Exactly **1,783,196 even payload additions** disappear. Streams 2627, 2628,
and 2631 each fuse one rank-8/rank-12 pair into rank 20. The local histogram
delta is `{8:-3,12:-3,20:+3}`; it becomes `{8:-15,12:-15,20:+15}` over five
stages and `{8:-180,12:-180,20:+180}` in the final normalized profile.
The literal rank mass remains 156,328,200 and normalized rank mass 31,265,640.
The full invoice still pays the same banks, source-access/COPY lifetimes,
restoration, routing and fixed interfaces. The fresh invoice recomputes the
costs affected by the reduced ADD/child counts.

Fourteen small tests cover positive commutation/identity cases, omitted odd
ADDs, changed coefficients or address frames, wrong fusion ranks, disconnected
chains, COPY lifetime corruption, crossing a retained use, malformed records,
the F₂/odd-field distinction, and source inventory corruption. Five additional
receipt mutations are rejected. A separate real-word control omits the first
surviving odd ADD and is rejected by the stream comparison. All checker
conditions remain active under `python -O`; the native verifier itself runs
with assertions enabled.

## Reproduce

Python 3.11+, Git, and `sympy==1.14.0` are needed for the full replay. Use a
**new** output path outside the repository. This command runs the source
checks, controls, all eight native stages, and the independent stream audit:

```sh
python3 -B research/pr210-head-reconciliation/verify.py --output /tmp/pr210-reconciliation-fresh
```

Expected: exit 0 and `PASS_PR210_HEAD_RECONCILIATION`, 19 post-review changes,
128 unchanged ancestral paths, the exact κ above, and the displayed deltas.
Progress is saved in the output's `native.log`; complete receipts and the
reconstructed immutable package are retained beside `RESULT.json`.

For a quick source reconstruction and corruption checks, omit `--output`;
this reports `PASS_SOURCE_RECONCILIATION` and does not claim a fresh replay.
`--audit-existing PATH` explicitly checks an already produced native replay;
it is recorded as evidence reuse. Our full native run preceded the finished
wrapper, so [RESULT.json](RESULT.json) accurately records this latter mode.
To additionally recheck Git provenance, fetch `pull/210/head` and pass
`--git-check`; it checks both exact commits, the 19-file delta, and all 128
ancestral identities. No GitHub or network access is needed for the default
or full reconstruction modes once the repository and Python dependency exist.

The historical and current selection binding checks and the repository's five
selected-record tests also pass. The unrelated repository-wide `make verify`
and selected frontier799 cold replay were not rerun; their inputs are untouched.

## Limits, attribution, and stopping rule

This is finite execution evidence plus a source/provenance reconciliation,
not a formal proof of integer multiplication or a review of the entire PR210
branch. The all-size compiler, common/weighted charts, paid routing/restored
rows, prime supply, precision/recovery, and analytic-transfer hypotheses remain.
The F₂ identity says nothing analogous about even payload coefficients over an
odd field. The original signed producer checks and the emitted word's signed
prefix bound serve different obligations.

Track **research consolidation**, OS-random assignment seed **98**. The
[claim](CLAIM.json) records three considered tasks and the time budget. Work
stopped at this one parent/head transition; there was no supplier search.
At selection, there was no pinned sprint issue. PR867 already covered selected
provenance and PR717 covered the schedule/ρ erratum; PR828 separately reconciles
PR279. This contribution adds distinct PR210 head coverage.

Prepared by **Ross Richardson (RossRichardson), with substantial OpenAI Codex
assistance**. The construction and submitted source delta are **eumemic's**;
the prior review and reconciliation are Douglas Colkitt's maintained community
records. Credit to Henry Grant/hcg890 and Jacob Sussman's five-stage work,
Rohan Arun, Evan McKinney, Chafik Boukhalfa, Avi Eisenberg, Dugongue, and
Romyxen/sennemmi remains in the unmodified source notices. See [NOTICE.md](NOTICE.md).
