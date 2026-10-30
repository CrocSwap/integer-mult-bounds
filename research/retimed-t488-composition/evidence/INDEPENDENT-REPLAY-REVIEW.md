# Independent read-only replay review: PR3653 at 2695d365

Verdict: no blocking defect found in the inspected replay composition. This is a source review and bounded input/hash check, not a completed scientific replay or formal proof. The queued packaged full replay must still finish before its final success status can be reported.

Reviewed snapshot: `primary-integration/public-submission-2695d365/research/retimed-t488-composition`. Entry SHA256: `490a500e5182f04dff744e9a011d597ecef217d7cfd18ae33f7941714159cc80`.

## Executed bounded checks

Imported the committed entrypoint with bytecode disabled and executed its read-only `authenticate()`. All 87 vendored/comparator files passed exact inventory, SHA256, Git blob and declared immutable-head checks. Independently checked all 654 files in the already materialized retimed source against the identical pinned manifest (`fb47533a401d1d13719be8b9aab91fe5313931ca62d40dba336eab6a96275aa0`). Expected total rank mass is 31,762,944 = 488 times 65,088. No owner/native/controller/full admission was duplicated.

## Binding and cost review

- `full-replay/reproduce.py:33-55,93-97`: immutable source closure and PR3642 comparator are authenticated; upstream materialization exports exactly 540 source files from frozen main commit 20ecf2891d80b5acf18d980b2164fb44ea7faa90, then reconstructs the 654-file retimed source. The generated native/admission drivers are supplied by this authenticated materializer chain, rather than fetched at runtime.
- Lines 103-118 reconstruct the complete literal T488 allocation and check identical old/new helper widths before applying each actual canonical local bill difference across 4,392 calls. This is deliberately only an expected invoice. The entrypoint does not declare success here.
- Lines 119-128 require fresh changed-native preparation and complete admission. Inspected the matching materialized `prepare_extension_native.py`: it authenticates retained evidence and both changed complete words; requires all five native stages and all 632 arbitrary columns, both orientations, complete actual paid profiles, 408 helpers, eight centers and 91 private zero buffers. Retained predecessor/parent evidence reuse is explicit, fully hash-bound, and not represented as fresh.
- Inspected matching `admit_extension.py`: binds full source/native inventories, exact words, profiles and parent receipt; reconstructs owners, lifts the parent and rebinds against actual canonical native data. Complete physical stock is explicitly checked as 896*T+408+8+91+2, or 437,757 at T488. The full profile includes idle/chronological charges and is independently regenerated, not accepted merely because SPEC states it.
- The same adapter retains strict replay plus independent owner/core/invoice, controller, geometry and rejection checks. Its existing block-norm refinement checks actual scalar/Horner prefixes for both native orientations, preserves invocation/bridge charges, requires full physical-stock norm and partial-cover reserve, and adds forged/undercharged block-norm controls. I did not independently prove the inherited block-norm theorem; this review establishes the required computational gates remain on the execution path.
- Inspected matching `verify_release.py:47-83`: strict supplier verification and independent outer replay must both succeed. The actual strict ASSEMBLY must have the exact global status, 47 outer constraints, a complex endpoint bracketing B, a complex profile equal to the ledger profile, and the pinned bit endpoint. Thus the modern outer is tied to admitted supplier data, not only expected values.
- Wrapper lines 127-135 additionally require final exact replica count/profile, rational equality kappa=C-10^-46-10^-70, C=0.001730418899766071163804, strict improvement over the authenticated PR3642 modern claim, rational/decimal agreement, release receipt digest and package-manifest agreement. The inherited admission compares PR2969, but the wrapper independently enforces the newer exact PR3642 comparison; it does not mistake the old comparator for the modern target.

## Reproducibility limits and remaining acceptance gate

Python 3.12 and the documented numpy/scipy/sympy/mpmath/psutil/gmpy2 dependencies, Git, the frozen-main object, and an existing writable external output parent are required. This command does not fetch objects or install dependencies. Output must be fresh and outside source/package. Assertion optimization is rejected; inherited witness-discovery overrides and PYTHONPATH are removed from child environments. Failed stages preserve logs and cannot reach the full success status.

The package's independent bounded `owners/run.py` is a separate audit; the full replay uses the inherited complete admission owner path rather than invoking that auxiliary wrapper. Both paths are useful, but their completion should be reported separately. The existing portability receipt explicitly covers input guards and source materialization only. Neither it nor this review proves the queued full replay has completed.

No publication files were edited. No heavy process was launched. All inherited theorem-scope conditions (including all-size realization, compiler/dispatcher, scalar/zero allocation, rounding, bootstrap, tape/recovery and analytic/BIT premises) remain; passing finite checks is not an unconditional integer-multiplication theorem.
