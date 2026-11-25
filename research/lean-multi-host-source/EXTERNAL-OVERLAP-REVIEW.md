# Bounded upstream overlap refresh

Snapshot: **2026-10-12 00:15:23 UTC**, compared with the previous audit at
2026-10-11 23:26:21 UTC. The selected target remains the one PR442
stage-2, replica-0, forward R747 invocation.

The new PR516 materially overlaps with generic stream realization,
ownership, and completion reasoning. It does **not** supply the concrete
PR442 bit-word, frame, owner-function, and clean-private certificates pursued
here. No newer work resolving that exact obligation was found within this
bounded refresh. This is not a global novelty or priority claim.

## Exact pins and unchanged sources

All seven requested heads are unchanged from the previous review.

| Source | Exact head | Commit time or PR last-update time (UTC) |
| --- | --- | --- |
| main | `12a4934d15006e8c10f9b2264f13f8f341be802b` | 2026-10-10 14:13:23 |
| PR397 | `cb6455fa1e9af68be47c33948d3d1a6f0717a5e4` | 2026-10-11 18:03:59 |
| PR442 | `4e16d001d505d4f21dd2bcfc44591f9be4c279bd` | 2026-10-11 13:18:56 |
| PR448 | `359022bcd71143e45d48def0dd005bf67f339aa7` | 2026-10-11 21:15:56 |
| PR509 | `7b9c720ecc9f483c383e7cd9c2ab81f06ee5df59` | 2026-10-11 22:50:52 |
| PR513 | `005dd3f4e3cba8d1761abc4ab391aaf6d14d6f73` | 2026-10-11 23:10:56 |
| [Jacob Sussman's repository](https://github.com/jacobalansussman/wht-power-saving-lean) | `9c94857bbaee886f8649edee0bc2d3c738f9555e` | 2026-10-11 00:24:08 |

Main's complete, untruncated tree still contains 154 Lean blobs. The
previous statement reviews of PR397's indexed scalar bridge, PR509's
generic conjugation/row interpretation, PR513's sequential completed-bank
bindings, and Sussman's linked Lean work therefore remain applicable.
Their existing generic results should continue to be credited.

PR448 has two issue comments, no submitted reviews, and no review comments
at this snapshot. The latest discussion is still the author's
[comment 6113842081](https://github.com/CrocSwap/integer-mult-bounds/pull/448#issuecomment-6113842081),
updated 2026-10-11 21:15:52 UTC. It explicitly says that the split action
"presupposes that one local register can be read and written across two
streams" and that "The hub never states a multi-stream register interface."
It further acknowledges that a second register requires paying its frame
chain and that the advertised gains are not established. This refresh
found no subsequent interface repair. No claim in this contribution relies
on that split action or gain.

## Recent-PR screen

The API query requested all states, sorted by most recent update, with
100 results on page 1. The oldest returned update was 2026-10-11 11:55:14 UTC,
earlier than the prior audit cutoff. Eight PRs were updated after the cutoff.
Their full recursive trees were inspected; none was truncated.

| PR | Exact current head | Last update on 2026-10-11 UTC | Lean comparison |
| --- | --- | --- | --- |
| 516 | `1c6b6ff9366a94e1f86a6c5d661a7df75c6ff814` | 23:58:28 | Six new Lean files beyond PR509; material generic overlap |
| 520 | `6077fa76950facbce11ec2f04dfbc93493114a44` | 23:57:03 | Same 154 Lean path/blob entries as main |
| 519 | `ffd3c48a80ba8b579dc300e785e387fe8acddfef` | 23:51:04 | Three new automatic-width counting modules |
| 518 | `e0a071dce251eeca96d446f73147048cfebbd5c7` | 23:50:50 | Same 154 Lean path/blob entries as main |
| 475 | `5996e33ecad6a0ccd578aec58831457829d75575` | 23:50:07 | Same 154 Lean path/blob entries as main |
| 511 | `9a20ad04be54b1c0fa26bd4ceb689f9ea220eab5` | 23:47:23 | All 158 Lean entries identical to previously reviewed `79f7c03c7f820ab89955b75ef239cbaccc627e6e` |
| 517 | `65518fcff5a7bd490365273ae5469a82aac14853` | 23:44:12 | Same 154 Lean path/blob entries as main |
| 515 | `6590606e733768f6a7004b3f55ae35f988ba515f` | 23:35:02 | All 203 Lean entries identical to its PR504 predecessor `35057a6d70f23480f4e960327d41ecac31ad5cb0` |

The titles, descriptions and relevant new source files were reviewed.
PR520's allocator and PR515/517/518's constructions do not add a new Lean
instantiation of this obligation. PR515's additional Lean blobs relative
to main are inherited; comparing only its count with main would have
misclassified them as new work.

## PR516: substantial generic overlap, concrete target still distinct

PR516, by DreamingOfClouds with disclosed Claude assistance, proves the
realization part of Lemma A for the PR484 complex construction. It is stacked
on PR509; all six Lemma G Lean blobs are unchanged. All 18 files of its new
`research/e8-lemma-a-lean/` subtree were fetched at the exact head and matched
their Git blob hashes. All 17 entries in its SHA-256 manifest also matched.

The important exposed interfaces are:

- [`realize_run`](https://github.com/CrocSwap/integer-mult-bounds/blob/1c6b6ff9366a94e1f86a6c5d661a7df75c6ff814/research/e8-lemma-a-lean/LemmaA/Realize.lean#L70)
  proves that a complete physical event fold, read through supplied charts,
  equals the local run when the owner function is injective.
  `realize_untouched` also preserves every unit outside that image.
- [`streamOwner_injective_of_disjoint`](https://github.com/CrocSwap/integer-mult-bounds/blob/1c6b6ff9366a94e1f86a6c5d661a7df75c6ff814/research/e8-lemma-a-lean/LemmaA/Streams.lean#L32)
  derives injection of `(family,d*σ⁻¹)` from supplied nonempty, disjoint
  footprints of group elements. `sweep_unique` proves the generic
  right-multiplication bijection.
- [`lemmaA_streams`](https://github.com/CrocSwap/integer-mult-bounds/blob/1c6b6ff9366a94e1f86a6c5d661a7df75c6ff814/research/e8-lemma-a-lean/LemmaA/Streams.lean#L62)
  takes the word, labels, exact recipes, well-labelledness, a unit helper
  endpoint row, and a tensor-factorization equation as arguments. Its
  conclusion identifies that helper's full stream action through its chart.
- [`lemmaA_piece` and `lemmaA_async`](https://github.com/CrocSwap/integer-mult-bounds/blob/1c6b6ff9366a94e1f86a6c5d661a7df75c6ff814/research/e8-lemma-a-lean/LemmaA/Tensor.lean#L115)
  additionally require the off-diagonal helper column to vanish and, for
  deferred completion, intervening actions to commute. These formalize
  meaningful complete-invocation and scheduling principles.

These results overlap with the generic foundations used here. This
contribution must not present physical gather/scatter induction, abstract
owner-group cancellation, helper independence from unit rows, spectator
preservation, or commuting completion as new discoveries.

The instance boundary remains different. PR516's `PROOF.md` explicitly
says that it proves an abstract theorem in PR442's stream model and
inherits the assertion that this model describes the machine. Its instance
tables concern PR484's complex words and a replay of PR505. The owner and
window hypotheses are checked by Python; atomicity is partly checked as a
declared `loop_order`, with the asynchronous structural audit delegated to
PR505. The words, actual scalar endpoints, route functions, and matrices
are not embedded as the concrete PR442 R747 certificates in Lean.

In particular, the new six Lean files contain no literal 19,002-event R747
word, checked 987-row symbolic endpoint, actual nine COPY/nine ERASE
clean-private trajectory, 944-frame table, concrete 747-host address
isometries, original 172-family ownership certificate, or common native
cover connection for the old/new selected call. Those are the additional
obligations of this package. PR516 therefore does not replace them.

This assessment is a source review. PR516 advertises a Lean 4.21/Mathlib
build and standard-axiom reports, but this refresh did not independently
rebuild it or execute its Python instance checks. Its disclosed PR505
template-hash discrepancy is not treated as either a proof of failure of
the abstract theorem or a successful reproduction by this audit.

## PR519 and integration implications

All 16 files in PR519's new package were fetched and Git-hash checked;
its 15 `SHA256SUMS` entries matched. Its
[`count_run`](https://github.com/CrocSwap/integer-mult-bounds/blob/ffd3c48a80ba8b579dc300e785e387fe8acddfef/research/lean-automatic-width-count/BinaryAutomaticWidthCount.lean#L141)
and `counter_value` theorems concern a ten-state machine allocating counter
width and counting an input word. They do not discharge an address-frame,
dirty-helper, stream-owner, or R747 source-invocation obligation. Its build
was not rerun here.

The selected contribution remains useful if its final coherent kernel replay
passes. Integration should cite PR516 alongside PR509 and PR513, describe
the result as discharging concrete source premises, and keep full-cover
scheduling, global allocation/cost, compiler, and κ claims out of scope.
No change of target or import of an external proof package is required by
this refresh.

## Evidence and limits

New evidence is confined to
[`review-receipts/external-overlap/`](review-receipts/external-overlap/).
`summary.json` records the pins and findings; `requests.json` records URLs,
retrieval timestamps and hashes; `tree-screen.json` and
`incremental-comparison.json` record the Lean path/blob comparisons.
Complete tree responses are compressed without changing their decoded
bytes. `files.json` records the 34 exact fetched package files and their
Git/SHA-256 hashes; the source copies under `raw/` are review evidence,
not imports or additions to the proof dependency closure.

Repository contribution instructions and the contribution-review index were
read. The refresh used public HTTPS GET requests only: no publication,
comments, push, PR creation, external verifier execution, or git-ref changes.
Its search boundary is the requested exact heads, PR448's current discussion,
the latest 100 updated PRs, and the changed Lean subtrees described above.
Historical branches, all external repositories, and updates after the stated
snapshot were not exhaustively searched.
