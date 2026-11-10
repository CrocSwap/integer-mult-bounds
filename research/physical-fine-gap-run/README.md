# Physical fine-gap run inverse with certified source pages

This package implements the complete ordinary-run inverse left as an
indexed-memory algorithm in CrocSwap/integer-mult-bounds#5571. It joins
certified bounded coefficient pages to the actual encoded signed convolution
of #3851 and word multiplier of #3787. Both orientations, stable recurrences,
local recentering, all finite-F maps, record reversals, overlap access,
discarded returns and erasure are included.

For the admitted ordinary source interval and input radius, the returned
vector approximates the inverse of the **fixed rational Reference principal
block**, with the explicit error in the prepared plan. The complete online
bill is `O(n W log^2(LW+2))`, hence `O(n p log^2 p)` in the stated fine-gap
regime. Input-independent interval work and physical page emission are
charged separately. See [PROOF.md](PROOF.md) and
[COEFFICIENTS.md](COEFFICIENTS.md) for the all-size hypotheses and argument.

**No new κ.** The periodic Schur correction and complete Gaussian/CRT/outer
caller remain unfinished. None of the selected construction's five global
framework assumptions is removed. The selected conditional frontier at
the frozen base remains `781451/250000000 = 0.003125804`.

## New result and inherited results

The q-LDU inverse, stable bidiagonal factorization and local recentering are
already proved in #5571. Generic physical signed convolution and its exact
word backend are already #3851/#3787. The common rational Reference and
local perturbation mechanisms are already #5216/#5326 and their pinned
`RAW-GAUSSIAN-PROOF.md`. None is presented as a new lemma here.

The new result is their source-bound **full run execution**: six certified
streams, a finite tape interface, both orientations with the original F
indices, local overlapping windows, common precision/range, complete cost,
retained-space accounting and an independent check against the original
matrix. The old #3851 production wrapper's coarse-gap admission is not
invoked; its standalone convolution has the needed window ABI. The result
covers ordinary nonwrapping constant-phase intervals, not joined cyclic
runs or a whole transform.

Before selecting this scope, the lead surveyed the canonical research
archive and later handoffs. Earlier caller/serialization questions were
stopped as duplicates. The #5571 factor identities, generic convolution,
hole insertion and generic resolvent comparison were likewise excluded.
A bounded later-work search located no completed source-bound physical
full-run implementation; this is not a claim of exhaustive coverage.

## Sources and interface

The exact canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
`SOURCES.json` pins every live source and both existing runtime archives by
Git blob and SHA256. The unchanged Gaussian loader authenticates the full
nested actual-word export, including embedded receipts. The scientific
verifier needs no remote fetch, Git query or shell child.

| Source | Exact head | Role |
|---|---|---|
| #5571 | `7e1ddb459728f4f2998e0b75c6a6a6aee7687481` | Run factors and recentering |
| #3851 | `7ab67b4a84d28cd562b9711aa315ca5b47822b37` | Actual signed convolution |
| #3787 | `9b5474f47b0ea9a3c76bb5b1b577fb36704815e0` | Acyclic exact word implementation |
| #5216 | `1ea9efdc1d1d36757a5491bf7fdaa93597dcea67` | Shared rational Gaussian weights |
| #5326 | `234142af90b5e7afe0b33c4b78c3c0bd622d5fc3` | Fixed Reference/geometry contract |

`coefficients.prepare(reference, start, length, radius, accuracy_bits)`
returns an admitted plan and six integer-numerator streams. Its interval
code never queries a global Reference entry or global similarity weight.
`run_pages.EncodedPages` emits them with the unchanged Signed ABI and four
distinct canonical Count descriptors. The physical consumer then borrows
the arbitrary input, those coefficient tapes and the descriptors:

```python
returned = owner.run(source, *encoded.streams, *encoded.counts)
```

The caller pays for loading its arbitrary input and consuming the output.
Every coefficient, data and descriptor port must be distinct and external
to all owned roles. Borrowed ports enter and return at their origins.
Output protection is the ownership contract: the caller consumes, clears
and erases the returned body before reentry. This is not a promise of
clean rejection of arbitrary private-output manipulation.
[ABI.md](ABI.md) gives the exact record/page order.

Preparation uses a separately priced interval/integer workspace. A fresh
preparation's bound does not erase source `pi_interval` cache entries from
earlier different-precision preparations. Retain and charge those cached
values, or explicitly clear them with paid cleanup. The online tape bound
does not silently include or deallocate historical preparation caches.

## Reproduction

From a checkout with the package and declared inputs:

```sh
python3 -B scripts/research_package.py --package research/physical-fine-gap-run
```

Both registered commands finish with `PASS_PHYSICAL_FINE_GAP_RUN`; one uses
normal Python and one disables assertions. A clean Git-free source export
can run directly:

```sh
python3 -I -B research/physical-fine-gap-run/verify.py
```

## Verified evidence and controls

The default fixture uses the exact original `Reference(61,3,1,4,8,80)`,
source start 11, and successively lengths 8, 2, 1 on one reused owner. Length 8
has `L=6,W=95,f=57`: overlapping windows, a short final block, unequal
forward/reverse coefficients and mixed-sign input. The program has 2,640
fixed tape roles, with observed outer pool peak 21. Its length 8 trace uses
exactly 84 scalar and 16 packed word products; the singleton uses none.

The physical return is checked bit for bit against an external integer
rounded-schedule oracle. Separately, `original_matrix_oracle.py` constructs
the original rational Reference block from source/target coordinates and
inverts it by exact rational elimination, checking every entry of
`H*H^-1=I`. Its expectation does not use factor pages. The observed
length 8 inverse error was approximately `5.861990775735749e-16`, below
the explicit allowance approximately `0.001953125`. Short-run reuse and
the exact singleton pass; all eleven borrowed tapes and every owned role
are checked.

The extended fixture covers length 20, `L=6,W=95,f=57`, including two full
overlap windows and a short final window in each orientation:

```sh
python3 -I -B research/physical-fine-gap-run/verify.py --long
```

It invokes 216 scalar and 32 packed word products. Its observed original
Reference inverse error was approximately `6.409736255753634e-16`, and
equation residual `6.074680426261895e-16`. The initial complete 20-row
physical calibration took about 288 seconds here; wall time is descriptive,
not a mathematical bound. The current alias guards were added after that
initial calibration without changing its valid-path arithmetic, and the
registered replay checks those guards. The default replay is smaller.
These finite fixtures exercise the inherited exact base branch at the
fixed 4096 crossover, not new finite coverage of its FFT branch.

Executed controls reject an underfunded Reference, phase-crossing and
wrapping intervals, inadequate gauge precision, excessive interval width,
aliased streams/descriptors, an alias into an inactive descendant pool,
and a truncated physical page. The original-matrix oracle rejects
transposition, reversed returns and a changed unit. An F-index mutation
changes the exact rounded result. A literal product-first rounding mutation
is executed and returns the wrong two-row answer. A separate 16-case
exact-source check confirms live cleanup costs are independent of old
blank backing tails.

These are finite observations. The universal result rests on the
source-specific proof and explicitly inherited dependencies, not on finite
tests or a claim of human/proof-kernel acceptance.

## Open next questions

1. Join the ordinary-run consumer to the cyclic low-rank/Schur correction
   with explicit boundary pages, source coupling and precision. The old
   coarse-gap wrapper has different admission hypotheses.
2. Build the complete caller that selects and scatters these runs,
   handles original holes and normalizers, and pays for both complex
   components. Generic interfaces alone do not prove this composition.
3. Check the aggregate preparation and online bill at the actual selected
   Gaussian/outer parameters. This supplies one precision/tape component,
   not admission of the complete supplier.

## Attribution

Prepared for **@CubeJerry** with substantial OpenAI Codex assistance.
The physical consumer, coefficient/precision producer and independent
original-matrix/ownership reviewer were separate concurrent AI workers;
the lead independently reviewed their composition. No human or formal
kernel review is implied. The Reference adapter follows the separately
reviewed halo contribution's source-only import rebinding, preserving
every executed numerical source body.

Credit Dugongue for #5571; Jose Manuel for #3851/#3787 and the rational
Reference; Mason Hale for outward interval arithmetic; Chafik Boukhalfa
and the earlier Gaussian-inverse lineage for inherited factorizations;
and the source packages' geometry, tape and arithmetic contributors.
Predecessor notices/licenses remain in the unchanged inputs and archives.
This contribution is Apache-2.0.
