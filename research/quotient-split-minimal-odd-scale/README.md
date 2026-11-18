# Minimal odd scale for the composed physical supplier

The fixed graph from [PR #7717](https://github.com/CrocSwap/integer-mult-bounds/pull/7717)
can use odd scale 11025 in each native call. The source uses 2083725.
Keep the binary coefficient allowance at 20 and all root formats unchanged.
The [proof](PROOF.md) connects the exact coefficient lattice to the physical
Gaussian-dyadic charts and inherited nested-call precision argument.
The [receipt](RESULT.json) contains the sharp physical witnesses and full cost comparison.

The conservative scalar-service rate falls from `2^29` to `2^22` steps per
padded cell. All 124816384 scalar services, storage, resets, copies, guides,
phases and recursive jobs are retained. This is a factor of 128 in one
charged upper-bound coefficient, not a measured runtime improvement.
There is no new kappa, smaller selected format or discharge of all five assumptions.

Use CPython 3.12 and the standard library from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/quotient-split-minimal-odd-scale
```

Both registered commands print:

```text
PASS_MINIMAL_ODD_PHYSICAL_SUBSTITUTION 11025 128
```

The [source pins](SOURCE-PINS.json) authenticate unchanged supplier copies.
The exact operator interpreter is the single declared repository input.
The [credit](CREDITS.md) separates the existing minimum-grid criterion,
common-root method and graph from this physical substitution.
The source's complete phase catalogue and compiler are inherited; they
are not rerun here. Selected cold replay, Lean and Docker were not run.
This is author checking with reused engines, not independent human or
formal-kernel review.

## Open next questions

Can an independently proved physical scalar implementation improve the
retained rate formula further? Start from its literal tape service and
full-view costs. A smaller abstract coefficient alone does not prove a
faster machine. New arithmetic lowering, a different native graph or a
smaller selected root format needs a new source-bound proof. No follow-up
is reserved here.
