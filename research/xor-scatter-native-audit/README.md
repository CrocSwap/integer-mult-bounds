# Native composition audit of the XOR scatter boundary

This package independently checks one remaining obligation in [PR #3273](https://github.com/CrocSwap/integer-mult-bounds/pull/3273). Its actual public `xor-scatter-v1` normaliser and authenticated exporter compose successfully with the unchanged native legality and formal-column checkers using genuine upstream Boost 1.85. Four accepted finite fixtures pass, and the targeted cost, lifecycle, and endpoint controls have the expected rejection behaviour. The extra retained alias remains separately charged.

The result is a finite boundary audit. It does not adopt the proposed boundary into a production supplier, complete a multiplication theorem, or change the selected exponent. The source-word invoice is independently calculated with exact rational frame ranks. Separate agents supplied that calculation, reviewed the native harness, and checked source provenance and replay receipts. These are separate automated checks, not independent human peer review.

## Exact scope and sources

The scientific base is canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6. The investigated PR head is `2e0408a03e770c85a7e59b9ade547dcbbaea7e73`. [SOURCES.json](SOURCES.json) binds nine repository input files by exact commit, Git blob, SHA256, and byte count. Seven come from canonical main, and the normaliser and its source manifest come from PR #3273. Every run authenticates these files before copying them into a private source snapshot and checks the snapshot again afterwards. No predecessor source is edited.

The fixed native domain is `HDIM=8`, `VPORTS=111`, and `RHELP=439`, with `NCOPY=9` for the original retained-slot list and `NCOPY=10` for its alias extension. The native staging helper deliberately uses an empty selected kernel and empty source-owner and donor-owner lists. The audit runs both exact COPY-count contracts as positive and negative controls. This is a source-bound finite question, not a search over new suppliers.

The source selection follows the handoff-first procedure and refines the `supplier-boundary-audit` card to PR #3273's explicit unrun native replay. [TASK.json](TASK.json) retains the original catalogue card, its provenance, overlap coverage, checkpoint decisions, and remaining obligations. The relevant investigation is [Discussion #2976](https://github.com/CrocSwap/integer-mult-bounds/discussions/2976). The live initial search covered all 342 open PR records across four API pages, but only 52 visible Discussion records from #1166 and #2976. Hidden and older Discussion pages, arbitrary code diffs, and unpublished work were outside coverage. The normalisation-specific metadata search found PR #3273. That is limited overlap evidence, not a claim of worldwide novelty.

## Established result

The following fixtures pass through the public normaliser CLI, its unchanged authenticated symbolic checker, its unchanged exporter, the original staging helper, and fresh builds of both native C++ checkers.

| Fixture | Exact input change | Passing NCOPY | Native records | COPY/ERASE pairs | Local raw rank charge |
| --- | --- | ---: | ---: | ---: | ---: |
| Selected baseline | None | 9 | 27,234 | 9 | 5,129 |
| Paired absent slot | Append `[0,0]` to scatter row 0 | 9 | 27,234 | 9 | 5,129 |
| Odd existing slot | Append `[4,4]` to row 0, which already contains slot 4 | 9 | 27,234 | 9 | 5,129 |
| Retained alias | Append helper 472 as retained slot 9, then append `[9,9]` to row 0 | 10 | 27,236 | 10 | 5,136 |

Every accepted fixture has 527 scatter ADDs, 24,305 total scalar ADDs, and 2,911 MOVEs. Both duplicate-row fixtures produce all three baseline export artifacts byte for byte. The retained alias changes the record stream by one empty COPY/ERASE block, while retaining the same scalar action. Its extra rank-seven COPY remains in the local bill.

Each accepted fixture passes all 883 native formal columns across the five-stage construction, with 661 local registers and 439 independent dirty helper registers. The five-stage ADD count is 121,525. The baseline has 45 fresh centre copies, including 18 reverse-stage copies; the alias has 50, including 20 in reverse stages. All six built-in omitted-bridge controls are rejected. The signed prefix bounds are 49,347 forward and 1,113,070 reverse. Their combined bound is `9528119495320518471870892800`, with 93 bits, for all four fixtures.

The native build uses GCC 13.3.0, C++17, and unchanged upstream Boost 1.85 headers in the author environment, with CPython 3.12.14 on Linux x86_64. A separate exact 779-bit product verifies unbounded `boost::multiprecision::cpp_int`. The harness rejects the named fixed-width stand-in, records compiler-resolved Boost dependencies, and compares every used Boost header with its exact entry in the authenticated official archive. The author run used 182 distinct Boost headers. Compiler and C++ standard-library headers remain environment dependencies, so this is not a hermetic compiler bootstrap.

## Why the scalar action and the bill agree

Fix the helper values immediately before scatter. Let `z[k]` be the value of helper `ret[k]`, and let `m[t,k]` count slot `k` in row `t`. In characteristic two,

\[
\sum_k m_{t,k}z_k=\sum_k(m_{t,k}\bmod2)z_k.
\]

This equality does not require distinct helper values, so it remains valid when retained slots alias the same helper. The normaliser changes only the scatter rows. During scatter, additions write targets while retained sources are helpers. Each serial COPY therefore sees the same helper value used by the symbolic snapshot, and each COPY block closes before the next opens. On a normalised row, membership equals the desired parity coefficient. This composes the scatter identity with the unchanged surrounding word.

The identity does not erase copied-slot obligations. The additional alias has two occurrences that cancel, but it remains an entry in the retained list. Its empty COPY/ERASE block still incurs the source frame's rank-seven charge. The independent invoice in [independent_invoice.py](independent_invoice.py) computes all 636 frame ranks by rational elimination and derives the MOVE charge by telescoping.

\[
H_{\mathrm{MOVE}}=5177-111=5066,\qquad
H_9=5066+9\cdot7=5129,\qquad
H_{10}=5066+10\cdot7=5136.
\]

It also obtains 23,778 non-scatter ADDs and 527 normalised scatter ADDs directly from the source word. These values are reconciled with an independent packed-event recount and the native receipts. Frame chronology and legal COPY ranks are checked separately by the unchanged native legality executable.

## Rejecting controls and what they establish

| Control | Legality checker | Formal-column checker | Meaning |
| --- | --- | --- | --- |
| Original nine-slot stream under NCOPY 10 | Rejects `unclosed COPY` | Rejects `center boundaries` | A declaration cannot silently add a slot. |
| Ten-slot alias stream under NCOPY 9 | Rejects `unclosed COPY` | Rejects `center boundaries` | Scalar equality does not permit dropping a copied-slot obligation. |
| Final alias COPY charged at rank 6 instead of 7 | Rejects `COPY rank` | Accepts | An output check alone does not certify the invoice. |
| Final ERASE rebound from helper 472 to 473 | Rejects `invalid ERASE lifecycle` | Rejects `discard original-source binding` | The copied source must remain correctly bound through disposal. |
| Genuine scatter ADD removed at zero-based record index 21,817 | Accepts | Rejects `local defining-decoder full formal column` | Legal geometry alone does not certify the operator. |

The omitted ADD changes output register 113 on 98 independent input columns, including dirty helper column 472. The harness calculates this witness separately and records the exact changed event and stream hashes. The cost-only mutation leaves the scalar map unchanged. An additional input fixture appends a single absent slot `[0]` to row 0 and is rejected by the normaliser's authenticated symbolic checker before any export directory is published.

These native control designs retain [PR #3210](https://github.com/CrocSwap/integer-mult-bounds/pull/3210) and [PR #3222](https://github.com/CrocSwap/integer-mult-bounds/pull/3222) credit. The new evidence is their source-bound composition with PR #3273's actual public normalising boundary and genuine upstream Boost, supplemented by the independent source-word invoice. Changing which helper is aliased is not claimed as a new mechanism.

## Reproduction

This is a dedicated native replay. It does not register a Python-only generic replay hook or claim hosted CI. Use Python 3.12 or later and a GNU-compatible C++17 compiler. Every native command is bounded by 120 seconds, and each native execution by 60 seconds. Builds and artifact-regenerating checks run serially in a new scratch directory.

Download [the official Boost 1.85 archive](https://archives.boost.io/release/1.85.0/source/boost_1_85_0.tar.bz2). Its [official checksum metadata](https://archives.boost.io/release/1.85.0/source/boost_1_85_0.tar.bz2.json) gives SHA256 `7009fe1faa1697476bdc7027703a2badb84e849b7b0baad5086b087b971f8617`. Extract its `boost_1_85_0/boost/` headers without editing them. The replay requires the original archive as well as the extracted include root, and authenticates all compiler-observed Boost headers against that archive.

From a repository with the two pinned commits and their input blobs already fetched, run the following command. The source reader is read-only and does not intentionally fetch missing objects.

```sh
python3 -I -B research/xor-scatter-native-audit/verify.py \
  --git-sources \
  --boost-include /path/to/boost_1_85_0 \
  --boost-archive /path/to/boost_1_85_0.tar.bz2 \
  --workdir /tmp/xor-native-replay \
  --output /tmp/xor-native-receipt.json
```

If needed, fetch the pinned canonical commits explicitly before replay.

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git \
  463113d675af7410ac91d53a4fed51ec6494eb9a
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git \
  2e0408a03e770c85a7e59b9ade547dcbbaea7e73
```

For a Git-free source export containing the nine pinned files at their repository-relative paths, replace `--git-sources` with `--source-root /path/to/export`. The scientific input bytes remain the same. The final author replay used the Git-source mode with `-I -O -B`; all existing result fields matched the first source-export replay, and the final receipt adds implementation, canonical-input, and Boost-archive bindings. Both the work directory and receipt must be new. A failed run writes no success receipt; an explicitly retained work directory keeps its partial evidence for inspection. The harness uses fresh receipt paths for every native invocation and restores mutated scratch record streams.

[RECEIPT.json](RECEIPT.json) contains the final checked source version, complete native receipts, environment details, compiler-resolved Boost hashes, and all control outcomes. Exact immutable source hashes remain mandatory. Regenerated gzip input hashes are diagnostic container hashes; compare their canonical JSON hashes when changing Python or compression versions. All mathematical fields and complete exported actions remain part of the comparison.

## Limits and open next questions

The native legality receipt contains a literal field named `nondegeneracy_checked_by_separate_exact_bank_audit`. That inherited field refers to another audit; this replay does not perform it. Similarly, zero owner intersections in the empty-owner fixture do not validate a nonempty ownership construction. This result does not run the complete selected cold ancestry, complete bank admission, physical hosting or routing, precision and tape transfer, all-size compilation, or a complete multiplication theorem.

The first next question is whether a maintainer should adopt the XOR-normalised interface as a separately versioned production boundary. A feasible first step is to review PR #3273 and this exact native receipt, then specify its schema, per-slot COPY contract, and source-manifest updates. The outstanding complete supplier and bank obligations block adoption; a finite PASS does not resolve them.

The second next question is how the boundary behaves in one named nonempty selected kernel, owner, and donor construction. A feasible first step is to pin a concrete consumer fixture and enumerate its live-source, ownership, and completed-bank obligations before replaying it. That fixture and its separate physical budget are not supplied here. Structured versions of both questions are retained in [TASK.json](TASK.json).

## Predecessor credit and licence

Nick Petalas supplied PR #3273's normalising boundary and PR #2977's mismatch discovery and guard work. Arham Tahir supplied PR #2992's simple-support boundary. Hiroki Kumazaki supplied PR #3004's parity and count characterisation, qualified for retained aliases by Sricharan Vagvala (`theon199`) in PR #3128. James Reed (`jwr404`) supplied PR #3099's scalar corroboration. `commdata2338` supplied the native odd-multiplicity and alias audits in PR #3210 and PR #3222, including the credited rejection controls used for calibration here.

The selected word and checker lineage belongs to eumemic and DreamingOfClouds through PR #543, PR #555, and PR #589. Dylan Crow supplied the exporter, staging program, and generalised native interfaces. LJH-217 and DaysSky supplied the earlier native cohort checkers in PR #346 and PR #352. Sagar Thakrar supplied the checked `cpp_int` stand-in used by the predecessor audits; that stand-in is not used here. Douglas Colkitt supplied the selected bindings, review, and contribution framework. Original source notices and the embedded `json.hpp` notice remain intact.

This audit harness and independent invoice were prepared for Clear1nsight with substantial OpenAI assistance from four concurrent agents. New work is Apache-2.0. Boost retains its own licence and is obtained separately from its official archive. The complete selected result and the repository's inherited analytic and compiler obligations remain unchanged.
