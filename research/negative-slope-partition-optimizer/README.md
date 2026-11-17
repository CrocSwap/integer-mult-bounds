# Exact negative-slope partition optimizer

This contribution was produced by Nick Petalas. Apache-2.0.

For the negative-slope Reading B contract of unpaidmoon's
[#7449](https://github.com/CrocSwap/integer-mult-bounds/pull/7449), this package
finds a maximizing partition, answering its Open next question 1. The claim is
a **scoped written proof with exhaustive finite corroboration**. No new kappa
or selected-frontier change is claimed.

At fixed piece count k, choose the shortest free rank s. The charged pieces
can be balanced. If R-s=(k-1)q+r, their multiplicities are k-1-r at q and r
at q+1. The resulting objective F_k is discretely concave in s, with

```text
F_k(s+1)-F_k(s)
  = delta(s+1) - (1-d) delta(ceil((R-s)/(k-1))).
```

The first nonpositive difference locates the first maximizing s. Comparing
these values over k and the unsplit target gives an exact optimizer in
O(R log R) arithmetic operations and comparisons. This is an oracle-model
bound, not a bit-complexity or tape-runtime claim. The proof covers all ranks
and real nondecreasing discretely concave tariffs with phi(0)=0, d<0, c>=0.
The supplied rational implementation accepts ranks 1 through 4096.

At zero fee every tariff has an all-singleton optimum. For the strictly
concave harmonic tariff that maximizing multiset is unique, settling #7449's
proposed zero-fee first example at every rank. Nonzero fees use the same
optimizer. For the harmonic tariff at R=12, d=-1, c=0, the first fixed-length
optima include (4,8), scoring 122407/27720, and (2,5,5), scoring 41747/5544.
The latter strictly beats both the balanced and extreme three-piece splits.

[PROOF.md](PROOF.md) contains the theorem, proof and scope counterexample.
[verify.py](verify.py) contains the optimizer and a separate literal partition
census that enumerates every possible free-piece choice.

## Verification

The exact finite checks cover:

- All 1,000 tariff tables at ranks 1 through 10 whose nonincreasing first
  differences lie in {0,1,2,3}, at slopes -3, -1, -1/3.
- Harmonic tariffs at ranks 1 through 20, at those slopes and -1/20.
- Every positive integer partition in each domain and every free-piece
  choice at zero fee. For fees 0, 1/3, 1, 3, 7, subtract the exact length fee
  from these exhaustive fixed-length maxima before comparing the global
  optimizer. Counts include repeated partitions across tariff and slope cases.
- The first-difference identity, the first maximizing free-rank tie rule,
  the binary comparison bound, global maximum, and an attaining partition.
- Explicit interior-free-rank examples, flat and linear tariffs, invalid
  input rejection, and a nonconcave example where balancing charged pieces
  strictly loses credit.

A full run reports zero errors, 3,080 tariff/slope cases, 87,703 partition
scores, 396,388 free-piece choices, 21,784 fixed-length comparisons,
16,208 difference identities, 15,400 global comparisons, six witness checks
and thirteen failure controls. These are exact counts, not runtime estimates.
The finite census corroborates the written theorem; it is not an all-rank
exhaustive certificate.

## Reproduce

From the repository root, using CPython 3.12.15 and the standard library:

```sh
IMB_PYTHON=/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12
"$IMB_PYTHON" -I -W error -B research/negative-slope-partition-optimizer/verify.py
"$IMB_PYTHON" -I -O -W error -B research/negative-slope-partition-optimizer/verify.py
"$IMB_PYTHON" -B scripts/research_package.py --package research/negative-slope-partition-optimizer
"$IMB_PYTHON" -B scripts/check_research_commit.py --package research/negative-slope-partition-optimizer --check-source-history --check-modes
```

The direct marker is `PASS_NEGATIVE_SLOPE_PARTITION_OPTIMIZER`; the registered
runner also prints `PASS_REGISTERED_RESEARCH_PACKAGE`. The commit check must
run after committing. Both registered commands have a 240-second limit.
Local warning-strict normal and optimized executions took 2.56 and 2.43
seconds, respectively. These are single-run wall times for the timeout check,
not performance benchmarks. The registered two-command replay took 5.22 seconds.
For an optional generated receipt, append `--receipt /absolute/scratch/receipt.json`
to a direct command. The receipt records the actual interpreter, counts and
SHA256 of every package file. No receipt is hand-written or committed.

## Scope, sources and overlap

Card `coverage-law-change`, priority revision 8, base
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status is changed from a
completed physical call to this explicit accounting optimization. The selected
record is #7000 with kappa 363005817/100000000000. The catalogue's #5599
assessment is historical. The source-binding orientation passed; no selected
scientific replay was run. Source pins for the catalogue and selected record
are provenance only, and there are no imported scientific inputs.

Question source and direct predecessor: unpaidmoon #7449 at
`180fac9c9797fee6ec44df8d9540f71612d07e1a`. Its existence theorem is cited,
not replayed. Unpaidmoon #7299 at `bfcb85c0b7298392607092f751df4a7b1afb60c6`
supplies the Reading B definition and earlier fee analysis. The proof restates
the definition and is self-contained. These unmerged heads are citations,
not Git-history dependencies. No predecessor program is imported or executed.

Live open-PR and Discussion intake was checked on November 12, 2026, including
#1166 and active threads. The overlap helper covered 768 open PRs and 7,360
Discussion records. Its local sparse inventory omitted 9,973 historical note
paths; direct `git grep origin/main` searches covered the complete committed
README inventory for Reading B, negative slope, shortest/free pieces and
weighted balancing. Merged-PR searches also included rank-dependent fees and
the general partition model. The account-filtered #7449 reference search found
no recent source reuse among open PRs, but its closed-PR scan timed out; the
separate live all-state own-PR list and merged searches supply additional
coverage. None of these searches proves novelty.

Related open work:

- [#7449](https://github.com/CrocSwap/integer-mult-bounds/pull/7449) decides
  existence for the same negative-slope fee. This package determines a
  maximizing partition and does not replay its existence proof.
- [#7299](https://github.com/CrocSwap/integer-mult-bounds/pull/7299) studies
  both fee readings, proves Reading A optima and nonnegative Reading B
  existence, and leaves negative Reading B existence open. The present
  optimizer concerns the negative Reading B maximum.
- [#7445](https://github.com/CrocSwap/integer-mult-bounds/pull/7445) identifies
  a physical helper adapter and distinguishes it from the abstract fee
  readings. This package makes no claim that its fee is physically realized.
- [#7303](https://github.com/CrocSwap/integer-mult-bounds/pull/7303) bounds
  actual fixed-word singleton splits and a charged two-way moment. This
  package optimizes the declared abstract fee without asserting physical
  feasibility or comparing those different quantities.

## Limitations and unrun obligations

A profitable accounting partition does not provide a legal physical split or
adapter. Native implementation, chronological delivery, arbitrary dirty-state
restoration, complete paid and productive invoices, and supplier admission
remain unproved here. The five selected framework assumptions remain. No
complete multiplication theorem, independent human review or formal proof-kernel
acceptance is claimed. Lean, Docker, selected cold replays and predecessor
scientific suites were not run. Hosted CI is separate from the local evidence.

## Open next questions

1. Can one find the best piece count without comparing every k? The current
   theorem searches the free rank efficiently at each k. First study the
   discrete curvature of the optimized fixed-length values on exact tariff
   tables. Maximization over s does not itself preserve concavity in k.
2. Does a real helper adapter have this negative-slope fee with independent
   delivery? First name one producer, consumer, per-piece charge and complete
   restoration contract. No such adapter is supplied here, and accounting
   gains alone do not justify construction expansion.

## Implementation bounds

The optimizer validates rational input, rank 1 through 4096, negative slope,
nonnegative fee and the tariff hypotheses. Its binary search has an explicit
bit-length iteration cap. Census ranks are capped at 20; the larger integer
family stops at 10 and enumerates bounded combinations of four increments.
All functions are under 60 lines, and the code uses no recursion or dynamic
code loading. Contract rejection and all mathematical acceptance checks remain
active under optimized Python; assertions only check internal invariants.

Python allocates integers, fractions and collections during execution. This is
a managed-runtime deviation from fixed post-initialization allocation. Live
storage is bounded by the supplied tariff and the fixed census domains;
arithmetic storage depends on input numerator and denominator lengths. The
census retains only one rank's partitions and one tariff case at a time.
A packed fixed-capacity implementation would require a separate numeric-range
contract before use in a constrained runtime. Warning-strict normal and
optimized commands are registered for every package replay.

## Credit

The new normal form, difference test, optimizer, zero-fee consequence and
corroborating verifier were produced by Nick Petalas. Unpaidmoon #7449 supplies
the maximizing-partition question and #7299 the fee definition. Retain their
Ali Romman #5769 fee-contract lineage and Nick Petalas #6651 uniform-fee
background; #5909 supplies earlier unit-fee context. Those optimization and
existence theorems are not steps in this proof. Balancing by discrete concavity
and monotone binary search are classical; no literature-priority claim is made.
