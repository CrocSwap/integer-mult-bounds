# Increasing precision lowers the Horner oracle volume

For every integer p>=102, the fixed-source inverse evaluator can request
strictly fewer total oracle precision bits while retaining p-1 oracle calls,
a p-bit disk-grid output and error less than p*2^-p. This is a scoped written
proof with exact finite corroboration.

This contribution was produced by Nick Petalas. Apache-2.0.

Let ||E||<=21/50 in the maximum complex-coordinate norm. Assume access to
the rounded-E oracle of Hanson Sun's
[PR1430](https://github.com/CrocSwap/integer-mult-bounds/pull/1430) at every
integer precision q>=101, with error less than (q/3)2^-q on the whole disk
grid. This family is an explicit additional premise compared with a single
fixed-precision oracle. No consistency between its errors is needed.

At iteration j=0,...,p-1 use q_j=max(101,j+3). Round the unchanged source
u/2 inward to each working grid and perform the fixed-source Horner update.
The last oracle uses precision p+2. A final charged inward rounding returns
the output to the original p-bit disk grid. [PROOF.md](PROOF.md) proves every
grid/disk invariant, source-rounding charge and inverse-tail bound.

The exact sum over the p-1 oracle calls is

```text
fixed precision:       p(p-1)
increasing precision: (p^2+5p)/2 + 4750
strict saving:        (p^2-7p-9500)/2 > 0, for every p>=102
```

The ratio approaches one half. At p=128 the counts are 16256 and 13262;
at p=256 they are 65280 and 38158. These are enumerated sums of requested
precision parameters, not runtime measurements, memory bounds, paid recursive
histograms or a complete supplier invoice. The work of repeatedly preparing
the source is explicitly additional. There is no new kappa or selected-frontier
change, and no optimality claim.

## Evidence and reproduction

The standalone verifier uses integer dyadic execution and a separate rational
real-block executor. Every reached prefix agrees. Exact rational elimination
of I+E supplies an independent final inverse. Its five rational complex
matrices have dimensions one through three and include a nonnormal case.
Six requested precisions are 102, 103, 128, 192, 256 and 512. Three oracle
modes include input-dependent signed local errors and ordinary inward rounding.

The generated output reports 684 complete executions and 146718 oracle calls.
It checks the disk and grid conditions and the proved final error bound at
every applicable point. All 1947 integer precisions p=102,...,2048 have their
literal precision sums compared with the closed form and strict-saving test.
Eleven rejecting controls cover bad precision arguments, a frozen coarse
schedule, wrong update sign, missing source halving, decreasing grids, excess
oracle error and an invalid operator bound. All checks use explicit exceptions
and remain enabled under optimization.

From the worktree root, standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/horner-increasing-precision/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/horner-increasing-precision/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/horner-increasing-precision
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/horner-increasing-precision --check-source-history
```

Other machines may substitute their CPython 3.12 path. Direct execution prints
a generated receipt with all six package-file SHA256 hashes and the exact
interpreter version, then PASS_HORNER_INCREASING_PRECISION. It writes no files
and needs neither Git nor external inputs. The registered commands run normal
and optimized checks. Source documents in SOURCES.json are provenance only;
no predecessor executable, scientific verifier or receipt is imported or replayed.
The universal conclusion rests on the written proof, not a finite census.

## Scope, coordination and credit

The original formal-interface-lemma card is explicitly changed to a written
precision-interface result. No proof-assistant formalization is claimed.
The selected-source orientation passed at canonical main
7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8, selected PR6030.
The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363411)
records the target before substantive work. Live claims and reservations,
recent account PR bodies, open/merged searches and main README searches were
checked. Cached sparse local notes and unpublished work remain coverage limits.

Hanson Sun / bbMisk's PR1430 supplies the fixed-source evaluator, its oracle
interface and the disk-invariant proof method. Its first Open next question
asks for a corrected actual Gaussian implementation. This is a new precision
schedule for that interface, not the missing backend or an audit of its result.
eumemic / PR5, icekylinx, the Harvey-van der Hoeven resampling lineage,
Artus Krohn-Grimberghe / PR371, Effy Elden / PR684 and Alan Grillo / PR902
retain their source/interface/analytic credit. Ordinary Horner evaluation,
variable-precision iteration and contraction bounds are classical; global
literature priority is unclaimed. All predecessor files and credit are unchanged.

The actual multi-precision Gaussian oracle, its preparation, source reads,
head returns, grid conversion, workspace cleanup, dirty restoration, native
legality, stock and complete physical cost remain obligations. The proof
does not discharge any of the five selected framework assumptions. No selected
cold replay, Lean, Docker, physical backend, independent human review or formal
proof-kernel review is claimed.

## Open next questions

Can a corrected actual Gaussian E family supply the requested oracles with a
favorable complete invoice? Begin with one implemented family, prove the same
disk/error contract at every q, and price its preparation together with all
repeated source roundings and the final p-bit projection. An actual backend
and source-compatible physical caller are the blockers. TASK.json records
the same question. No further precision optimization is undertaken here.

## Verifier bounds

The verifier has no external numeric input. Every matrix has at most three
complex coordinates, each registered execution has a fixed set of 684 cases,
and the independent arithmetic sweep has 1947 iterations with at most 2048
precision entries each. Functions have at most 44 physical lines. The call
graph is nonrecursive, state is local, file reads are capped at 256 KiB, and
no subprocess, dynamic code generation or callback dispatch is used.

Python's managed allocation is a deviation from fixed storage. Its scope is
this terminating bounded verifier: at most six scalar coordinates per state,
2048 precision entries, six bounded file reads and fixed-size elimination
matrices. Checks validate input/domain bounds and every disk/grid transition.
A fixed-storage implementation is required before using the verifier in a
runtime that forbids managed allocation. Warning-strict normal/optimized
execution and in-memory source compilation provide the local diagnostics.
External Python linters were unavailable locally; no broader static-analysis
or repository-wide analyzer configuration change is claimed.
