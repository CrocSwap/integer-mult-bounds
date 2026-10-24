# Sharp factor two for mixed quadratic cyclic inverses

This scoped proof is produced by Nick Petalas. For

    P(z)=c(z-a)(1-bz),  c!=0,  |a|<1,  0<|b|<1,
    delta=min_{|z|=1}|P(z)|,  m=min(|a|,|b|),

the [written proof](PROOF.md) establishes

    delta ||1/P||_W <= (1+m)^2/(1+m^2) < 2.

The Wiener norm sums the absolute values of the Laurent coefficients. The
radius-sensitive factor is optimal at each fixed m, and two is the least
uniform factor. Both statements also hold for the induced infinity norm of
`P(tau Z_L^w)^(-1)`, uniformly over positive cyclic lengths, integer strides
and unit phases. Sharpness there is a limit over cyclic lengths.

Rafael Guevara's [#803](https://github.com/CrocSwap/integer-mult-bounds/pull/803)
proves the general degree bound `(1+4n)^2/delta` and leaves its degree factor
nonoptimal. On this mixed-root degree-two subclass, the sufficient multiplier
therefore falls from 81 to two. The new step is the exact two-sided Laurent
norm and a sharp endpoint bound. The antipodal family `a=r,b=-r` attains
`(1+r)^2/(1+r^2)` and approaches two. No predecessor result is replayed or audited.

## Evidence and reproduction

Standard-library CPython 3.12 is sufficient. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/mixed-quadratic-circle-bound
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/mixed-quadratic-circle-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/mixed-quadratic-circle-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/mixed-quadratic-circle-bound --check-source-history
```

A reviewer can substitute their CPython 3.12 executable. Direct verification
also works from a Git-free export. Ordinary verification writes no files.
`--emit-to NEW_EXTERNAL_FILE` exclusively creates a generated receipt with all
six package source hashes; `--check-receipt FILE` recomputes every result and
compares it with the receipt, including integer/Boolean types. No receipt is
hand-written or required as an external replay input.

The executed finite coverage is:

- 192 exact endpoint inequalities across four interior radii, three reciprocal
  exterior radii and every pair of phases in `{1,-1,i,-i}`.
- 768 cyclic inverse comparisons between dense elimination and a finite
  geometric resolvent construction, with 2,688 inverse entries. Eight root
  pairs, lengths 1 through 6, strides `-1,0,1,2` and all four unit phases are
  crossed. Both inverse identities and rational upper enclosures of the norms
  are checked. The 192 antipodal cases also use their exact circle gap.
- 63 rational sharpness identities at `r=(d-1)/d`, `d=2,...,64`. The final
  normalized Wiener norm is `16129/8065`, with exact deficit `1/8065` from two.
- Eight controls cover three invalid root domains, wrong factor sign, wrong
  inverse direction, wrong gauge, omitted negative Fourier frequencies, and a
  finite cyclic counterexample to replacing the factor by one.

The enumerations corroborate the universal proof. They do not exhaust complex
roots or establish the universal theorem by sampling. Receipt mutation,
exclusive-create and source-hash controls are separate publication checks.

## Scope and implementation limits

This is a scoped proof with finite corroboration, not a finite supplier
certificate or complete multiplication theorem. No new kappa is claimed.
The theorem concerns exact operators with one interior and one exterior root.
It gives no coefficient preparation, rounded execution, dirty restoration,
fixed-tape schedule, complete caller invoice or supplier admission. The selected
frontier remains unchanged. Independent human and formal proof-kernel review
are unclaimed. No Lean, Docker or selected cold replay is required or run.

The verifier has no recursive calls. Its finite mathematical loops are bounded
by the displayed corpus, matrix size six and exponent 64; functions remain
below 60 lines. Explicit exceptions retain the checks under optimization.
Python's managed allocation is a deviation from fixed storage: all matrix
storage is bounded by six rows of seven Gaussian rationals, and external
receipt size is bounded by one MiB. Library arithmetic and JSON parsing use
runtime allocation. A lower-level implementation would require its own storage
proof. Warning-strict normal and optimized execution provide available
diagnostics; no separate linter or type checker is installed in this environment.

Source pins in [SOURCES.json](SOURCES.json) are historical provenance at canonical
main `624de9dc66858af0945e5f8a0942488d62280d43`. There are no imported predecessor
executables or live mathematical dependencies. [TASK.json](TASK.json) records
the changed card scope and structured next questions.

## Open next questions

1. Determine the best multiplier when both quadratic roots are outside the
   unit circle. Start with separated two-pole phases and exact coefficient
   sums. Coefficient cancellation blocks the disjoint-series argument here.
2. Apply the bound to one actual source-bound mixed quadratic caller's complete
   rounding recurrence. First identify the factor, then charge preparation,
   every prefix and restoration. A complete physical invoice remains missing.

## Credit

Credit Rafael Guevara #803 for the general degree-controlled bound and its
nonoptimality question, Ali Romman #621 for the cyclic kernel setting, and
Thiago Costa #802 for the related Fourier-transfer work. Geometric-series
resolvents and Fourier substitution are classical; Ryan Pinto #692 retains
credit for the retained finite-geometric cyclic implementation lineage. No
literature-priority claim is made for those methods. This result is produced
by Nick Petalas. New files are under Apache-2.0.
