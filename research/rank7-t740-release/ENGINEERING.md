# Engineering bounds and retained-source exceptions

Build the Lever shaped the contribution into an executable streaming
materializer and source-bound release wrapper. Prove It Works requires the
actual literal-owner recount and a fresh source/native/admission/outer chain,
rather than a moment comparison alone.

New code has structured control flow and no recursion. Explicit domains are
740 replicas, 6,660 calls, 408 helpers per call, 2,717,280 streamed rows,
550 journal records, 36 group factors, 2 providers, 13 source stages and at
most 100 pinned inputs. Retained native subprocess stages have 1,800-second
timeouts; source export has a 60-second timeout. Process groups are terminated
on every stage exit. Files use scoped context managers. Workspaces must be
fresh and external to the package. Source and output failures propagate.

Rule 3, fixed memory: Python and the retained numerical libraries allocate
managed objects during execution. Materialization streams rows and gzip output;
the finite owner engine has bounded dictionaries for 1,491,840 bins, plus
6,660 helper/family masks. Input decoding is limited to 150 MB in the new
finite checker. Full admission retains its existing resource model and finite
input domains. The package does not claim allocation-free execution or a
measured peak-memory bound. Follow-up is a bounded streaming replacement only
if actual replay memory becomes a blocker.

Rule 8, source compilation: one explicit `exec(compile(...))` executes an
exactly SHA256-authenticated Python source from PINS.json. This avoids stale
bytecode replacing the pinned source. Only fixed call sites select the retained
lift, R1 checker, owner, cap and interval modules. The narrowly annotated S102
diagnostic records that required exception. Source drift controls reject before
execution. Follow-up is a source-loading API that preserves the same bytecode
isolation if the project supplies one.

Rules 2, 4 and 10 for retained engines: the original files are frozen and
byte-identical, including their existing loop/function conventions and
assertions. They are not refactored as part of this isolated mathematical
composition. The full wrapper refuses optimization because inherited native
validators use assertions; new finite invariants use explicit exceptions and
remain enabled under optimization. Functions changed here remain below the
rough 60-line review limit. Ruff, warnings-as-errors, optimized finite replay,
behavioral controls and registered source-pin checks cover the new files.
No TypeScript or JavaScript is changed.

The original PR3021 process-group runner and exact-tree export are adapted
with attribution. Their retained source is included for line-by-line review.
Read-only internal review is distinguished from independent human review.
