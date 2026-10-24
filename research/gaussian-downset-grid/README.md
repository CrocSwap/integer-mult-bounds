# Use the smaller Full allocation in the actual Gaussian callers

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.

## Result and source boundary

This closes the actual normalized/raw caller question left by [PR4977](https://github.com/CrocSwap/integer-mult-bounds/pull/4977). Its smaller completed-downset allocation now reaches the unchanged `Gaussian.compile_root` and both the provisional and child allocations of `RawGaussian.__init__`. Source method bodies, all admission/rejection checks, the immutable shared `Reference`, and diagonal/gauge arithmetic are retained. The allocator of PR4977 and its uniform Full/downset proof are dependencies, not results re-proved here.

`bridge.py` makes two private subclasses. It reuses each source method's exact code object with a private globals dictionary: only `allocation` changes in normalized `compile_root`; only `allocation` and the bound `Gaussian` class change in raw `__init__`. Every other inherited method is unchanged. No frozen source file, original module globals or original class is modified. This explicit bridge is an opt-in construction, not a repository-wide replacement or an assertion that unmodified callers already use the new allocator.

The actual factory has the original public finite domain: dyadic positive dimensions, valid normalized kernel/shift, positive radius/accuracy and admitted raw cell/period geometry. Exact coefficients, reciprocal setup and original conditioning and fragment contracts remain inherited. The result is conditional on those written contracts. No new selected κ or complete multiplication theorem is claimed.

## Quantified caller and grid implication

For every admitted normalized caller let its radius be R, target t and incoming grid F0. Its prepared rational kernel and exact coefficient/tail receipt do not depend on the Full allocator. `compile_root` still invokes Full with `(n,n,2 qbar,R,t+1,F0)`. The certified allocator supplies the same requested Full error target `2^(-t-1)` with the new child precision; hence its unchanged forward and inverse inequalities against the ideal Gaussian still hold. The norm/inverse admission and stored gate reversal are unchanged. The exact normalized kernel itself and its source hash are identical to the original caller, although the new Full plan's gate coefficients may differ.

For every admitted raw caller the original source computes g,H, its diagonal coefficient error, middle radius `R*=2g(R+1)`, middle target `t*=t+ceil(log2(16g))` and the same immutable reference comparison. None uses the changed allocator. Let A(F0) denote the new allocation's data precision at `(n,n,2 qbar,R*,t*+1,F0)`. Its exact source formula is `A(F0)=max(F0,F_required)`, where F_required does not depend on F0. The raw caller declares

```
F = max(F0, t+ceil(log2(24 n g H)), A(F0)).
```

The bound child then requests the same normalized instance with incoming precision F. Consequently `A(F)=max(F,F_required)=F`. This proves the actual raw/normalized common-grid check at every declared parameter, rather than only at the finite fixtures. Redirecting the raw provisional site but leaving the normalized child on the old allocator can break that equality; the verifier executes this missing-site control. Redirecting only the child can retain the old larger provisional floor and therefore fails to realize the advertised width saving.

The original raw proof now applies literally on that one grid. With `r=n 2^-F`, the rounded first diagonal obeys `(g+delta) R+r <= R*`. The middle error is at most `2^-t/(16g)`. Source telescoping retains

```
E_raw = 2g E_middle + 3gH delta R + 3gH r < 3*2^-t/8.
E_forward = E_raw + R E_ref,
E_inverse = E_raw + 2 Q_raw^2 R E_ref < 2^-t.
```

The reference admission still demands `E_ref <= 2^-t/(8(R+1)Q_raw^2)`. The stored inverse still reverses and inverts the very same prepared forward gates, with no independently rounded inverse table. The caller recomputes its actual intermediate amplitude, integer and temporary-bit allowance from the changed child receipt and unchanged gauges. This is not a claim that all these quantities decrease monotonically: only child precision strictly decreases and the selected data grid never increases. Incoming precision can dominate and leave data width unchanged.

All original asymptotic online-width bounds therefore remain valid. The bridge adds no arithmetic operation to the generated data plan. It supplies no physical price for offline exact admission, coefficient preparation, reference pages or address delivery.

## Evidence and decision

The verifier authenticates all declared source bytes before imports. Five actual source callers execute: shifted normalized n=2; normalized n=2 with 512-bit incoming data; raw narrow n=2; raw broad n=2; and raw narrow n=4 with 512-bit incoming data. The three raw calls share one exact rational reference. Both the original and changed factories compile, with identical normalized kernels, raw reference hashes/descriptions and raw gauge tables. Twenty actual rounded forward/stored-inverse trajectories are compared against direct matrix multiplication and a separately implemented exact inverse. The actual source execution statistics check intermediate signed-grid and temporary widths. A 512-bit nonzero input is retained.

Observed child/data-bit changes are respectively `240/134 -> 55/72` for the normalized shifted fixture, `174/111 -> 53/71` for raw narrow n=2 and `539/261 -> 114/119` for raw broad n=2. The two incoming-512 fixtures preserve 512 data bits. These are fixture measurements, not universal constant savings. All actual finite coefficients and typed statistics are in generated `RESULT.json`.

Five controls reject an altered source allocation premise, a changed common-reference page after preparation, an illegal original-cell crossing, discarded incoming grid and a missing normalized-child binding. Receipt corruption is rejected by exact typed canonical comparison, including bool/int distinctions. Normal and optimized checks are registered; claims of universal validity come from the argument above, not from extrapolating these executions.

Research decision: stop at this caller edge. Completed Full/downset/conditioning contracts are retained dependencies; the allocator binding and grid implication are established here; complete core/tensor callers, physical costs and selected-frontier admission remain separate. This closes the immediate width-substitution uncertainty without treating unknown costs as zero.

## Reproduce and provenance

```
python3.12 -B scripts/research_package.py --package research/gaussian-downset-grid
python3 -B scripts/check_research_commit.py --package research/gaussian-downset-grid --check-source-history
```

Both registered commands need CPython3.12 and the standard library. An official committed export can execute `verify.py` directly with `-I -W error -B`, and separately `-O`, without Git or network. `--emit NEW_PATH` writes a fresh receipt and refuses overwrite; ordinary replay compares the committed typed receipt.

Canonical base `bee95ce88f9f19802f0613f92838895cd0e14a1f`, priority7, selected conditional κ0.00302015 unchanged. Entry overlap covered310openPRs at06:05:59UTC,4096Discussion records at06:06:48UTC and all6690base notes on October23. Scope, source pins and later claim/PR links are in TASK/SOURCES and the canonical record. Coverage is advisory and excludes arbitrary diffs and unpublished work. Hosted CI is unverified at publication.

Credit Nick Petalas for the downset block-solve theorem; Jose Manuel/jmbarrancoml for rational Full, normalized/raw Gaussian and their conditioning, immutable-reference and grid/error contracts; Vlado/PR1673 for the compiler, Jeremy Kothe for shifted identities, Chafik/PR628 for phases, Mason Hale for interval arithmetic, Brian/JoyboyBrian's PR4977 for the one-expression adapter, and all retained predecessor notices. Source bytes are imported in place, not redistributed as a second archive. No independent human or proof-kernel acceptance is claimed.

## Open next questions

Can one actual finite-core caller use the bridge for every raw/normalized child while preserving its prepared boundary-page and stage-input budgets? Start with one complete fixed-reference invocation of core.py, enumerate its allocation sites and audit every actual stage-input radius. Those additional page/precision and physical delivery obligations are outside this package; another scalar allocator sample would not resolve them. Structured question: TASK.json.
