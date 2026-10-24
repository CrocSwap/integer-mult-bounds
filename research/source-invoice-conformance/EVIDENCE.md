# Source and validation record

Canonical base `1ec1119972c9aefe42525172d07b332fcff81cb4`, priority revision 7.
The selected record, source manifest and review were resolved before this work:
κ=.0030217758 under five inherited framework assumptions; reproduce through
`make frontier4610-verify`. This opt-in package changes no selected data,
predecessor source or shared implementation.

Inputs are package-local data exports, authenticated before verification by
EXPORTS.json. Original-word/caller bytes came from `git show BASE:path`.
Pending word bytes came from the GitHub contents API with explicit pinned `ref`.
No producer evaluator, price engine or receipt is imported or executed.

* [#5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383):
  `4bd6efa51a495a7c7b7754915cf0244e7e60969e`.
* [#5387](https://github.com/CrocSwap/integer-mult-bounds/pull/5387):
  `b1ab650d36f59e5be682a813145b7c67e219e341`.

CALIBRATIONS.json records the separately inspected producer-claim paths,
heads and raw receipt hashes from which its expected paid/target fields were
retained. Those fields are comparison fixtures, not evidence substituted for
the independent source interpretation. Native/caller profile annotations are
deliberately ignored. Source/checker hashes identify the actual execution;
they confer no physical or scientific acceptance by themselves.

## Reproduction and coverage

macOS 26.5.1 arm64, CPython 3.12.8, standard library only. Isolated branch
`codex/source-invoice-conformance`. Execute from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/source-invoice-conformance --check-only
python3.12 -B scripts/research_package.py --package research/source-invoice-conformance
```

The manifest runs complete isolated, warning-strict normal and optimized
verification serially, with 120 seconds per command. The external run guard
also limits the complete pair to 300 seconds and samples descendant RSS every
0.5 seconds with a 1-GiB stop. RESOURCE.json records the final command and result.
The final pair passed in 24.793 seconds with sampled peak 290704 KiB. These resource measurements are not a mathematical storage guarantee.

Coverage consists of the original selected word and two actual owned-relation
successors, both orientations and all independent entry columns, all native
frame transports, all paid events and helper endpoints, and the complete literal
p16/a7 caller with both boundary programs. The factored ledger accounts for
every recursive contribution at actual caller IDs. Its independent reconstruction
matches all three separately retained claim profiles. The CLI round trip writes
and rereads the full source audit and preflight invoice, checks its expected
claim, and rejects overwrite. The 24 controls cover source mutations, ownership,
rank/frame changes, false zero retags, target debits, queries/idles, caller
semantics, stale same-invoice bindings, malformed inputs and growth limits.

The original and changed invoices exported from the checked result were also
accepted by the published signed preflight interface of
[#5397](https://github.com/CrocSwap/integer-mult-bounds/pull/5397), reporting
`uniformly_better` with paid delta−128H1−128H8 and target delta−128H9.
That is a format/arithmetic integration check, not new funding or a rerun of
the predecessor research package.

Separate assisted reviews checked native interpretation, caller composition,
source binding and claim scope. Review led to explicit main port/endpoint
subspace gates, symbolic growth guards, bounded rational syntax and a hash of
the complete recursive ledger. Registered receipt checking also exposed an
unstable first-failing-role diagnostic from set iteration; sorted role order
fixes it. Golden data were updated only after confirming all positive invoices
and native semantic-audit hashes remained unchanged. The final normal/optimized
replays use the corrected code. Reviews share context; no independent human
or formal-kernel acceptance is claimed.

## Freshness and limits

The overlap helper at 2026-10-23 22:56 UTC reported complete pagination for 353
open PR bodies and 4689 Discussion records. Sparse local-note coverage was
zero of 7267 tracked top-level notes; no missing local match establishes novelty.
Start-here, handoff and relevant current [Discussion #4930](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930) / [#5125](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125) activity were read
separately. Exact related code/claims distinguish the signed histogram preflight,
price compatibility oracle and this independent extractor. Arbitrary diffs and
unpublished work remain outside coverage. No public Discussion post was made
during the donor's local-draft checkpoint.

Final targeted refresh retained the canonical base and both scientific word
heads. [#5391](https://github.com/CrocSwap/integer-mult-bounds/pull/5391) was
re-read at `96f193143a7a2ff8a4e6b9d574d7f551d68a7da3`: it remains a compatibility
oracle consuming trusted evidence, distinct from this source extractor. Recent
native-provider/normalization/controller-ceiling work changes constructions
rather than supplying this extractor; it is not imported or replayed here.

No native absolute-phase engine, physical fresh-stage/coordinate embedding,
precision/tape implementation, complete ordinary-cost funding, compiler,
analytic recovery, selected cold replay, Lean or Docker was run or inferred.
The source-port guard binds the supported symbolic ABI; it does not prove the
all-size physical embedding. Unsupported schemas or growth reject as outside
this tool's domain, not as mathematical impossibility results.

The checkout is shallow. Optional full source-history checking is unavailable;
metadata/source pins, direct base ancestry, committed bytes and portable export
verification are separate checks and do not imply full publication history.

Final transport checks passed at scientific-code commit
`1d9608a86ac1f0b6ea51475874021fc49d5338dd`: committed-byte verification,
the official nineteen-file export and its integrity check, and a complete
optimized isolated replay from that Git-free export with empty PATH. Every
exported file remained byte-identical after replay. Direct base ancestry passes;
the optional history command reports `source-history check requires full Git
history`. A final static assisted review confirmed the native boundary and
symbolic-growth issues resolved, with no residual blocking issue. Subsequent
changes only record these validation results.
