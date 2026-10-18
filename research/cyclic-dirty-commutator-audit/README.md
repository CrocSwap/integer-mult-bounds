# Multiway dirty echo and phase-alias repair for PR628

**A subquadratic composition schedule and a concrete executable admission fix.**
The new [echo construction](ECHO-PROOF.md) replaces binary dirty commutators
with a forward/undo ladder and a second ladder omitting the first link. For
fixed fanout k it uses O(n^log_k(4k-4)) factor calls and O(log n) borrowed arrays.
At k=8, the exponent is about 1.602452 instead of 2. For 512 factors it uses
21 borrowed arrays and 21,952 calls, versus 9 arrays and 262,144 calls for the
binary schedule. The flat variant uses n-1 arrays and 4n-4 calls.

The written proof includes the exact noncommutative identity, rounded exact
restoration, all recursive calls and the inherited complete-word error budget.
Under PR628's separation bound the precision power falls from r^5 to roughly
r^4.602452 for fixed fanout 8. This is a **classical local primitive**, not a
paid common-label supplier or a new multiplication κ. The one-line admission
repair below is independently useful even without adopting the new schedule.

The [full-transform and bit integration experiment](../dirty-echo-integration/README.md)
now implements complete synthetic Fourier transforms and Boolean address
interchanges with this echo. The functional checks pass, but the complete
all-role recursive bill rejects this direct adapter as a route to larger κ.
Its proof and exact counterexamples identify the remaining interface and
cost obligations without changing the local echo result.

The [bit role-sharing cost screen](../bit-role-sharing-budget/README.md)
then prices arbitrary XOR role pooling, ideal local consolidation, and
cross-stage rank/repair targets before attempting a replacement supplier.
It rejects the first two routes to κ=0.01 and records exact requirements
for a genuinely changed paid profile. No new κ is claimed.

## Executable admission defect

At PR628 head `0768f97d06c623b8211e651543c66135796b62bf`, `dirty.py::compose`
checks that the mutable source, target and scratch arrays are distinct, but
allows its supposedly read-only `phases` list to alias any of them. Its entry
unit-modulus check does not make that list immutable during execution.

With `x = phases = [1, 1]`, `y = [0, 0]`, one outer factor with `b = 1/4`,
scale 1, β = 1/2, direction +1 and eight fractional bits, the call returns
normally with **x = [1, 15/16]**. Exact restoration fails. All entry checks pass.
This is not a counterexample to the written lemma under genuinely read-only
phases: it is a missing executable admission check for that hypothesis.

## Why it fails, independently of numerical precision

The outer coefficient at site i is `b * phases[i]`. The first causal lift makes
`x[1] = 1+b`. Because phases aliases x, the undo now reads the changed phase and
subtracts `b*(1+b)`, instead of the original b. Thus

    x[1] after undo = (1+b) - b(1+b) = 1-b².

For dyadic b in (0, 1/2] and a grid representing b and b², this calculation is
exact. Increasing precision cannot fix it. The replay checks b = 1/8, 1/4,
3/8 and 1/2 at 8, 16 and 64 bits. Aliasing the target also returns normally
with damaged data. Aliasing scratch can instead fail only after mutations;
that is not rejection before execution.

The proof's undo argument requires the same coefficient on the forward and
reverse lifts. The recursive cancellation also requires phases to remain
unchanged between paired calls. The mutable-array identity exclusion already
present in `compose` does not enforce either requirement for phases.

## Repair and replay

[phase-alias-guard.patch](phase-alias-guard.patch) inserts this check immediately
after the existing mutable-array identity check, before any writes:

```python
c.need(all(phases is not v for v in arrays), 'phase array aliases mutable data')
```

It is a patch against the pinned pending PR628 package, which is not on this
main base. Applying it to that package fixes the ordinary-list identity alias
case without copying the length-L phase array or adding array passes. It takes
O(h) identity checks per invocation for h borrowed arrays; those same arrays
are already enumerated by the existing admission checks. Distinct lists with
equal values remain valid. General mutable views, concurrent mutation and
stateful coefficient callbacks are outside this list-based guard; the generic
`lift` API still requires fixed coefficient/multiplier/destination callbacks.

From the repository root, the reproducible command is:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 0768f97d06c623b8211e651543c66135796b62bf && python3 -I -B research/cyclic-dirty-commutator-audit/verify.py
```

Expected final line:

```text
PASS_PHASE_ALIAS_REPAIR_AND_INTEGER_GRID_AUDIT 300 differential cases; 19 pre-mutation alias rejections
```

The verifier reads Git blobs at the exact pin, checks every consumed source
hash in [SOURCE.json](SOURCE.json), and applies the submitted patch in a
throwaway directory. It performs no network access or tracked-file writes.
`--out /absolute/new/report.json` optionally saves evidence. `-O` is also
supported by this audit; its checks do not rely on Python assertions.

The 300 valid cases compare the original, patched, and separately implemented
integer-grid execution paths bit for bit: 1/2/3/5/8 factors, lengths 1/2/3/5/8,
precisions 4/8/16, both directions and signs, nonzero dirty data, inner/outer
factors and varying rational unit phases. The PR628 producer uses Gaussian
rational pairs throughout; [integer_model.py](integer_model.py) stores data as
integer grid coordinates and compiles a flat instruction word before reversing
it. No producer arithmetic or schedule helper is imported by that model.
Seed 67 fixes the generated values. The finite domain is completed in full;
there is no random early stopping and no impossibility claim.

The source and every scratch array must be restored exactly; positive then
negative execution must return all arrays exactly. The repaired path rejects
19 source/target/scratch aliases before any mutation. Distinct equal-valued
phase lists are accepted. Removing the guard must reproduce source damage.
All eight inherited instruction mutations must still fail. Explicit positive
and negative half-grid tie controls check rounding toward positive infinity.
This is finite differential evidence, not a formal proof of the all-length
rounded inverse, its precision bound, or integer multiplication.

## Reproduce the complete contribution

From the repository root, use this single compound command and a new output
directory (Python standard library and Git only):

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 0768f97d06c623b8211e651543c66135796b62bf 4982f0ca66ffe0960b5a6451deb5b66b1039326b a6895a69f8ad98ab45777b03e9e6f48888c39f6f && sh research/cyclic-dirty-commutator-audit/replay.sh /tmp/dirty-echo-sprint-replay
```

Expected final line: `PASS_DIRTY_ECHO_ALIAS_REPAIR_AND_FINE_GRID`.
The script checks the repair, echo, same-input Fraction benchmark and the
separately scoped [PR659 final-grid refinement](../gauge44-notri-fine-grid/README.md).
It also runs the full-transform/bit integration and its scoped cost rejection.
The bit role-sharing budget screen is included as the final check.
The final-grid component reconstructs the pinned complex supplier afresh and takes
roughly three minutes on the recorded machine. It requires assertions in
inherited engines. The alias and echo checkers separately support `-I -O`.

`verify_echo.py` completes 72 exact noncommuting matrix cases, 744 rounded
integer-grid comparisons, 120 dense inverse/error-budget cases and 62
pre-mutation phase-alias rejections. Three instruction mutations fail. Factor
counts, fanouts, directions, precision grids and dirty values are explicit in
the checker; the seed is 67 and every listed case is completed. The independent
matrix oracle checks the schedule; the integer interpreter checks arithmetic
on that schedule; the inherited dense oracle checks the target/error bound.
These are distinct forms of evidence, not independent human or formal review.

The same-input benchmark uses 16 factors, length 8, 1024 fractional bits and
three repetitions. Source, target, factors, phases and the common scratch-pool
prefix are identical; scratch counts are explicitly different. The binary,
fanout-8 and flat methods use 256/112/60 calls and 4/8/15 arrays respectively.
All three restore exactly and meet the same 32-bit dense accuracy check.
See [evidence/BENCHMARK.json](evidence/BENCHMARK.json) for timings. These measure
the Fraction prototype only, not a practical integer multiplication algorithm.

## Pins, overlap, scope and attribution

Main base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. OS assignment seed: 67,
adversarial mathematical audit. [CLAIM.json](CLAIM.json) records the candidates,
selection and local claim; no pinned coordination issue existed. The selected
main certificate was κ = 0.001635527380375392 (#626/#543), which is unchanged.

The final queue refresh found concurrent
[PR663](https://github.com/CrocSwap/integer-mult-bounds/pull/663), by @0xkilgore,
at `e0e546fd01b396478c68b6b6c5a16d87515983ba`. It independently audits nonlinear
restoration and proves the exact **binary** leaf count, retaining quadratic
asymptotics. Our comparison uses actual binary calls, not the loose 4n²
allowance. The **changed multiway schedule**, phase-alias counterexample/guard,
and independent rounded integer-grid arithmetic are distinct additions.
PR665 concerns a spectral residual encoder's unfavorable boundary bill;
PR666 concerns composite-radix nonvanishing. Neither is used as a dependency.

PR628's dirty inverse and its proof are by **Chafik Boukhalfa / chafreaky**, with
substantial OpenAI Codex assistance. Its PR621 kernel, by **Ali Romman**, and
OpenAI, Pan, Mehlhorn–Sagraloff–Wang, Brent and filtering sources retain their
original attribution; see the source-pinned NOTICE.md and SOURCE.json. This
audit does not claim their algorithms as new work. The unrelated final-grid
refinement requested during the sprint is in
[../gauge44-notri-fine-grid](../gauge44-notri-fine-grid/README.md).

New audit, integer interpreter and repair prepared for **@androolloyd** with
substantial **OpenAI Codex** assistance. Apache-2.0, under the repository license.
