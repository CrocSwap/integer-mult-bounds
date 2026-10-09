# Community round 8: reviewed suppliers and completed entrance banks

Douglas Colkitt, with OpenAI Codex assistance; 2026-10-09.

The strongest candidate reviewed in this batch is PR186's conditional
**κ = 330942774629799 / 500000000000000000 = 0.000661885549259598**.
This is about 40.184% above the overnight integration candidate and 43.602%
above published main. It is approximately 2^-10.56113, leaving a factor
2.95085 to 2^-9. Neither main nor the selected-result pointer is changed by
this review branch. Linux replay status is in the [validation receipt](../../research/community-round8-audit/validation.json).

## Audited constructions

The frozen refresh contains 133 open PRs: 26 new since the overnight batch,
plus three older submissions whose heads changed only to record verification
evidence (#116/#118/#123). The submission snapshots are evidence of author
claims, not blanket maintainer acceptance of the entire queue.

| PR | Contributor | Review disposition |
|---|---|---|
| #168 | eumemic | Core lineage reviewed through #182's independent full physical replay; local signed modules, output fusion, physical bit word and terminal sinks |
| #181/#182 | Chafik Boukhalfa / chafreaky | Full local finite replay passes: shared-edge complex circuit, regenerated matching, operation frames and terminal sinks; κ=0.000660216552061722 |
| #185 | Rohan Arun | Exact arithmetic and acyclic ordinary-leaf composition reviewed; κ=0.000660627334074291; physical inputs exactly match #182; all 46 public CI checks passed |
| #186 | Dugongue | Full local finite replay passes; strongest candidate, with the bank scheduling supplement below; both branch-specific Linux jobs passed |
| #154 | eumemic | Verification parallelism, frame speedups and removal of irrelevant repository-wide hash pins; useful separate integration task, not merged in this round |
| #183 | Romain Hedouin | 22 focused tests pass; closed-form assembly reduction reviewed as arithmetic-only work, no new κ; separate integration |
| #175 | Chafik Boukhalfa / chafreaky | Ordered retired-register buckets preserve selection order; exact overlay already included in the reviewed #181/#182 prerequisite and its CI; main integration still separate |

PR186 is imported as its original self-contained package, with all file pins,
archive parts, author notices and assistance disclosures intact. An independent
git-blob comparison checks every one of the 1,700 bundled prerequisite files
against its named PR181 commit. The archive contains neither missing nor extra
paths and no changed file bytes. No root source is overwritten to make an old
source manifest accept a new checkout.

## What the review establishes

For #182 and #186, the full aggregates reconstruct complete original and
terminal-modified signed complex words, including both shear signs and inverse
cleanup. The packed formal-column encoding has an independently accumulated
absolute coefficient bound; its radix is strictly larger than twice that bound.
Thus the complete-column check is not random testing. The bit checks use exact
F2 formal vectors and sparse integer coefficients. The integer contract is the
defining decoder, whose reduction is the identity, not an integer identity.

The review covers actual operation frames, conservative value spans,
nondegeneracy/prime witnesses, donor death versus recipient read times,
physical-chain splices, target chronology, exact dirty restoration and the
complete paid ledgers. Terminal deletion is checked on the simultaneous
modified word, including initial target shears, source/dirty responses,
interleaved target reads and literal reverse operations. Copied centers,
the full original scalar reserve and the full finite complex group remain paid.
Exact interval moments, the entire bit rare-class fallback, strict stopping
and row tolls, all 47 inequalities and all seven margins pass. Corruption
controls are retained. A separate high-precision calculation agrees with the
strict moments but is only a sanity check, not the rational certificate.

## Bank scheduling supplement for #186

The submitted coordinate-projector identity establishes a full dirty-bank
endpoint once the completed cores have run. It does not alone specify an
efficient conflict-free schedule for the physical invocations. The maintainer
[supplement](../../research/community-round8-audit/BANK-SCHEDULE.md) makes the
missing scheduling detail explicit using the existing GL low-residue classes.

Within each low class, distinct fixed role embeddings give distinct bank
ports. All high lifts can therefore be batched without two live cores sharing
storage. Complete that class before proceeding to the next one. There are a
fixed number of classes independent of atom width. Each role still visits
every bank exactly once; its transported split residual is one member of the
coordinate partition. The raw endpoint follows from the checked arbitrary-dirty
core, not from an assumed clean scratch register.

The proof also makes explicit a finite extra prime exclusion for the fixed
routing embeddings. This uses the existing choice of a sufficiently large
fixed prime and changes no rank, child count or exponent; it does not assert
that the old Gram exclusions alone certify every new routing matrix. A small
exhaustive local-ring model checks the schedule over GL_2(Z/9), including all
3,888 invocations, 7,776 role visits and 15,552 endpoint basis columns.
The general proof supplement is not a new Lean-checked theorem.

## Compatibility with #185

Rohan's finite bootstrap takes a completed ordinary supplier A_0 and defines
only three further wrapper levels, each calling the preceding level at its
ordinary leaves. Its saving obeys a_(j+1)=(1-c)c+c*a_j. The stopping and
borrowed-row gaps remain strictly positive, and both padding and tape counts
grow only by constants at fixed depth. The old external 252 reserve is retained
as slack; it is not falsely represented as the new internal borrowing bound.

This is a transferable improvement. However, PR186's effective bit saving is
already about 0.000665064158, above its complex saving 0.000662323931899051.
Improving the bit leaves alone therefore leaves PR186's current final κ
unchanged. The gains from #185 and #186 cannot be added. Keep #185's mechanism
and credit for a future complex-side improvement or a different supplier.

## Attribution and boundaries

The current step includes Dugongue's rematching, coordinated frame cuts,
46 complex terminal sinks and bit entrance-bank packing; Chafik's shared-edge
supplier; eumemic's #168 searched modules and physical words; DaysSky's carrier
closure work; and James Chang's terminal substitution and balanced assembly.
icekylinx's paired-cube framework, an664's completed-core sharing, Zhihao Chen's
bit compilation, Swapnil Jain's finite witnesses, geckods's stopping refinements,
RaD's positional layout and all earlier notices remain in the pinned source
chain. Rohan's independent bootstrap is recorded even though the winning
candidate is already complex-limited. The scheduling supplement claims no
priority for the bank construction itself.

These are conditional finite/construction findings. The inherited general
weighted compiler, common-chart and routing interfaces, restored rows,
precision/recovery, prime supply, uniform setup and analytic fixed-tape
multiplier are not established from scratch or fully formalized by this audit.
Main publication and PR closures remain separate maintainer actions.

## Final validation receipt

The new complete package and scheduling diagnostic passed on Linux Python 3.11
and 3.14 at `c799bddbacb0d5bcc6f4938914c041f27780a570`:
[dedicated run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/37928942214).
Both jobs also passed the unchanged-tracked-tree gate. Git initially normalized
two pinned CRLF JSON artifacts; a path-specific `.gitattributes` rule now
preserves all original package bytes. The initial failure and fix are recorded.

The previous full 53-job Linux result is reused for the old implementation:
all existing scripts, tests, certificates, formal sources, notes, references,
Makefile and workflow blobs are identical to that tested baseline. Only earlier
review receipts and the new-package-specific attribute rule differ among existing
paths. The [reuse receipt](../../research/community-round8-audit/baseline-reuse.json)
records this comparison. Redundant automatic baseline reruns were cancelled;
they are not described as new successful runs. A final evidence-only commit
uses `[skip ci]` and preserves all tested candidate and dependency bytes.

For #154, 12,000 deterministic exact comparisons agree for canonical bases,
orthogonal complements and containment, in dimensions 1..32. Its concurrency
runner still needs integration-level checks; in particular `--jobs 0` should
be rejected rather than permitting an idle queue. #175's ordered-bucket change
preserves the old descending-rank/ascending-slot selection: bucket mutations
occur only after a clearing candidate is accepted and that scan then returns.
Both speedups remain separate from the reviewed numerical candidate.
