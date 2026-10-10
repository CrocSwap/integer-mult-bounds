# Gen4 circuit and common-delivery frame integration

Douglas Colkitt, with OpenAI Codex assistance; 2026-10-10.

## Pinned construction

The candidate is Rohan Arun's PR279 at
`4d8c31eec7ae618645cb058101cb4e72a97268d3`, stacked on DreamingOfClouds'
PR276 at `cf6cb4ebb55f0ee5f03918033e96a29209ff6798`. The exact conditional
witness is `90446448750933/125000000000000000` = **0.000723571590007464**.
Review completion and execution evidence are recorded in
[the integration receipt](community-pr279-integration.json).

The full local replay passes all nine mandatory stages with all 112 package
inputs unchanged. All five producer artifacts regenerate exactly. The
dedicated [Linux run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/38025424194)
passes both replay and regeneration on Python 3.11 and 3.13 at the same pinned
head. The local run used Python 3.14.6 and SymPy 1.14.0 without a portability
adapter. Publication metadata passes the selected-record corruption controls.

While integration was finishing, PR279 advanced to `913ccc4` with an additional
target-prefix transform and a larger claim. That later revision is outside
this review and is not included in this selected witness. The PR remains open
for review of that increment; this checkpoint preserves the four original
commits through `4d8c31e`.

This is 1.90486% above the independently reviewed PR210 snapshot
`298f7c112889f799e8e2040099fbc325d0ccd0f6` (0.000710046193349537),
and 56.98526% above the earlier published 0.0004609169 checkpoint.
These compare exponent savings, not practical runtime. The immediately
preceding main selection was 0.000661885549259598; the stronger PR210 review
had not yet changed that selection.

## What changed

DreamingOfClouds supplies a new paired-cube bit word. Different local addition
trees create more usable carrier arcs; a pair module shares its total with
the copied center; the all-but-one module is also redesigned. The virtual
auxiliary count falls from PR200's 18,908 to 17,904. After 1,494 compensated
reuse pairs, 16,410 independent dirty registers remain. The retained checkers
admit the pinned circuit itself; no search optimality claim is needed.

Rohan reassigns 880 source-pair mixing gates to their existing rank-22 common
delivery frames. For each pair the paid children 1,1,20,22 become 21,21,2,
with the other unchanged child retained. The rank mass stays fixed while
the recursive moment improves. This reuses eumemic's PR244 common-frame
technique on the new gen4 word. No source, target or dirty endpoint, scalar
instruction, copied-center lifetime, entrance or bank chart changes.

The full physical replay checks source-value containment, nesting in both
orientations, every formal scalar column, inverse restoration and the
complete paid histogram. The independently written
[local check](../../research/community-pr279-audit/check_retiming.py)
imports no contributor code: it checks all 880 selected subspaces against
their existing delivery annihilators over the rationals, proves full rank
and nondegeneracy using a two-dimensional dual Gram test, and rejects a
rank-deficient mutation. This local check does not replace the full word replay.
An additional [standalone scalar checker](../../research/community-pr279-audit/check_literal_word.py)
imports no contributor code and executes all 19,930 formal columns of the
emitted word in both directions. It compares the complete scalar/COPY sequence
against the original producer after removing even F2 identities, reproduces
both prefix majorants, restores 16,410 dirty registers and rejects an omitted
addition. It checks the scalar projection; address geometry remains separate.

## Prime coverage correction

The initial PR279 head `2e2a38ba3f48edbda2152ed86691c75ff326b254`
failed both dedicated Linux jobs at `base and added transform coverage`.
Its coverage assertion incorrectly required every original producer frame
to remain among the frames physically consumed after retiming. Rohan's
`4d8c31e` correction evaluates the union of original obligations and actual
current frames. All current frames remain covered and their determinants
are freshly evaluated; no determinant or nondegeneracy check is disabled.

## Dependency and proof audit

Seventy package files match the audited PR210 tree byte for byte, including
the virtual checker, PR200 physical-word classes, scalar program, complex
supplier, both moment engines and the outer assembly code. The
[source comparison](../../research/community-pr279-audit/source-comparison.json)
lists all matching paths and every changed/new file.
The earlier [independent complex scalar replay](../../research/community-pr279-audit/pr210-complex-scalar.json)
is reused only after checking both its recorded schedule-source and certificate
hashes against this package. It covers all 12,052 scalar columns and arbitrary
dirty restoration in both directions. The package's own complex stage is run
fresh; the reused scalar receipt is not described as a new execution or a
proof of address geometry.

The changed geometry adds the rank-21 entrance family to the existing
rank-20 checks. Every actual entrance chart is separately reconstructed by
the bank checker. The unchanged projector identities apply for either rank:
five disjoint windows carry the residuals, and each bank's coordinate blocks
partition the complete 120-dimensional address space. Sixty literal replicas
fill the stage-private families with blocks of widths 3,4,24. The proof's
distinct normalizers and fixed stage/replica order preserve the inherited
conflict-free completed-bank argument. All 4,923,000 assignments and all
370 actual entrance charts are checked. Physical stock is 1,283,035; the
smaller moment normalization is not substituted into physical routing costs.

Even payload additions are identities over F2. Removing them leaves odd-prime
address arithmetic unchanged. Retiming retains common frames at surviving
gates and all endpoints, so the common-frame conjugation identity preserves
the complete operator. The new emitted word has its own forward and inverse
prefix majorants. Its defining integer lift is not assumed to equal the
older producer's integer decoder.

The final accounting retains all 502,915,820,400 extra bank selector calls,
the full rare-class fallback, three finite ordinary-leaf levels, the complex
supplier and all 47 strict outer constraints and seven margins. The adjacent
headline grid point must fail. The general finite overcharges and inherited
interfaces are unchanged; their constants remain enormous.

## Scope

Acceptance is conditional on the retained all-size weighted compiler,
common-ancestor/weighted charts, complete-stream movement, restored rows,
selectors, routing, prime supply, precision/recovery, complex symbolic
correctness and analytic reduction. This is finite construction verification
and a written compatibility audit, not a new complete Lean multiplication
proof, independent human peer review or a practical multiplication benchmark.
Historical source comments and contributor-described independent runs are
not represented as additional maintainer executions.

## Attribution

- **DreamingOfClouds (#276):** gen4 circuit, physical producers and five-stage
  completed-bank integration; this supplies most of the new numerical gain.
- **Rohan Arun (#279):** descent selection, exact retiming stage, rebinding,
  final composition and prime-coverage fix.
- **eumemic (#244/#210/#168):** common-delivery retiming principle, package
  machinery, scalar implementation, checkers and preceding circuit framework.
- **Henry Grant / hcg890 (#234) and Jacob Sussman:** five-stage construction
  and complex baseline.
- **Evan McKinney (#197) and Rohan Arun (#237):** completed entrance banks.
- **Chafik Boukhalfa (#200):** physical-word classes and exact checkers.
- **Avi Eisenberg (#193):** retained complex supplier.
- **icekylinx (#144), an664, DaysSky, James Chang, Zhihao Chen, Swapnil Jain,
  RaD and other predecessor contributors:** preserved in the source notices.

Original commits, licenses and assistance disclosures are retained. This
integration does not assign exclusive priority or approve unrelated claims.
