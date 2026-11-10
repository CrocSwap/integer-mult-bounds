# Exact optimal multiplicities for heterogeneous tensor cuts

This contribution was produced by Nick Petalas. Apache-2.0.

For two fixed dyadic helper-cut types with disjoint odd-prime defect sets,
the optimal unit-channel density at every positive tensor length has an
exact two-candidate formula. The bounded optimizer uses integer comparisons
and returns every optimal multiplicity, including ties.

This is a scoped written mathematical proof with exact finite corroboration.
It sharpens a switching bound in zxv's
[PR6054](https://github.com/CrocSwap/integer-mult-bounds/pull/6054).
That contribution's full product-module theorem and general vanishing-density
bound are cited premises. They are not audited or replayed here.

Let the two rational ranks be r,s and their unit capacities c,d, with
0<c<r and 0<d<s. Put A=r/c and B=s/d. For the unique integer k satisfying

    A^k <= B^(n-k),       A^(k+1) > B^(n-k-1),

the exact optimal density is

    max((d/s)^(n-k), (c/r)^(k+1)).

Only k and k+1 copies of the first type can be optimal. Retain whichever
of the two displayed terms attains the maximum, or both if they tie.
[PROOF.md](PROOF.md) proves the all-length result and states the exact
disjoint-defect hypothesis. [schedule.py](schedule.py) implements it for
ranks and lengths at most 4096. It does not authenticate a supplied physical
cut or check disjoint defects from the four rank/capacity numbers alone.

For K=diag(1,1,3) and L=diag(1,5), four factors have sharp density 8/27,
attained by three K factors and one L factor. Capacity is 16 at rank 54.
The equal-count choice has density 1/4, capacity 9 and rank 36. The
predecessor's general catalogue upper bound is 4/9 for this instance;
8/27 is a strictly sharper bound with attainment. This is an algebraic
example, not a selected productive native cut or a new kappa.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -S -W error -B research/heterogeneous-tensor-schedules/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -S -O -W error -B research/heterogeneous-tensor-schedules/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/heterogeneous-tensor-schedules
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/heterogeneous-tensor-schedules --check-source-history
```

Other hosts may substitute their CPython 3.12 interpreter. Direct commands
print `PASS_HETEROGENEOUS_TENSOR_SCHEDULES` and a generated JSON receipt
bound to every package file's SHA256. No receipt is handwritten, and no
generated files remain in the checkout. Registered replay runs both modes
and prints `PASS_REGISTERED_RESEARCH_PACKAGE`. The final command checks
the committed publication. The scientific checker needs no Git, network,
third-party dependencies or predecessor executable.

The new finite checks enumerate:

- 14,112 profile/length contracts, with every candidate count observed
  separately, giving 246,960 count observations and 562 two-optimum cases.
  Ranks are 2 through 7, capacities every positive smaller integer, and
  lengths 1 through 32. The oracle does not use the crossing rule.
- All 248 binary words of lengths 1 through 5 in four declared diagonal
  catalogues. Every one of their 18,504 tensor diagonal coefficients is
  materialized. A separate integer gcd/lcm Smith oracle computes capacity
  without prime-rank profiles or the optimizer. All 20 length/catalogue
  optima and their complete attaining count sets agree.
- Eleven invalid-profile rejections and nine semantic controls covering
  ties, exact crossing equality, heterogeneous attainment, length one,
  maximum accepted input sizes, shared-prime failure, strict improvement
  and failure of equal multiplicities.

These are new schedule-domain tests, not a predecessor theorem replay.
They corroborate the written theorem only on their enumerated finite domains.
The registered commands have separate 120-second limits. Timing observations
and hosted results belong in the PR body; runtime speed is not a claim.

## Scope and credit

Credit zxv / PR6054 for the question of switching within a fixed defective
catalogue, the full saturated product-module theorem and general bound.
Nick Petalas / PR5882 supplies the primewise tensor-capacity formula.
Ali Romman / PR5615 supplies the single-cut unit-capacity criterion,
with PR5602/5611/5599 and the retained helper/native/controller lineage.
Smith theory, tensor ranks and monotone crossing optimization are classical;
no global literature-priority claim is made. The new contribution is the
exact heterogeneous finite-length optimum, its bounded optimizer and
standalone schedule certificate. Predecessor files and credit are unchanged.

Scientific base is canonical main
7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8. The selected
binding-only first example passes. [TASK.json](TASK.json) explicitly changes
the coverage-law-change card to this algebraic side result, while
[SOURCES.json](SOURCES.json) pins the cited provenance at the reachable base.
There are no live external source inputs. The
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19376668)
states this scope. Main and merged searches include general catalogue,
prime-defect and scheduling wording; live PRs, Discussions and local claims
were checked. Sparse local notes and unpublished work remain overlap limits.

The objective fixes tensor length and maximizes capacity divided by rational
rank. It does not fix total rank or per-type physical costs. Different
orders are algebraically equivalent; physical routing can have different
costs. Overlapping defects, zero capacities and full-capacity types are
outside the strict two-defective-type theorem. Parallel direct-sum activation
and Smith-axis ADD-precision ordering are different optimization contracts.

Physical basis preparation and inverses, common native charts, chronology,
carriers, delivery, restoration, precision/growth, stock, tape, independent
productive targets, compiler and outer obligations remain unpaid. No
complete signed bill, supplier admission, new kappa or complete multiplication
theorem is claimed. Selected scientific replay, Lean and Docker are unrun.
Independent human and formal proof-kernel review are unclaimed. The selected
frontier and its five framework assumptions are unchanged.

## Open next questions

- What is the exact optimum with three or more heterogeneous types, or with
  overlapping defect sets? Start from a finite prime-rank table and fixed
  length, then derive the integer minimax problem. A complete optimality
  certificate and a source-specific paid/target objective remain missing.
- Can an actual native product-cut pair use the optimal mix profitably?
  First extract two full saturated modules with legal common physical timing
  and complete prime profiles. Physical basis preparation, delivery,
  restoration, native charts and the complete signed invoice block a supplier
  claim. Algebraic density alone does not fund those operations.

Structured first steps and blockers are in TASK.json.

## Executable bounds

The autonomous-local-run playbook stops at this first exact improvement.
Build the Lever led to the reusable rational optimizer. Prove It Works
led to independent exhaustive-count and literal tensor/Smith oracles.
Power of Ten inspection covers both new Python files. There is no recursion,
network, subprocess, generated executable code or callback dispatch. Each
function has fewer than 60 physical lines. The public numeric boundary rejects
nonintegers, booleans, invalid strict capacities and ranks/lengths above 4096.
The binary search has at most 14 iterations and uses integers of at most
98,305 bits before reduction. Verification uses fixed finite domains,
retains at most 33 densities per profile, and materializes at most 243
diagonal entries per tensor. Smith elimination has at most 29,403 pair
updates per tensor. Hashing covers seven files, each limited to 256 KiB.

Python's integer, Fraction, dataclass and collection allocation is a managed
runtime deviation from allocation-free execution. These commands are bounded
offline calculations, with no steady service. Input and enumeration limits
bound live objects; a lower-level port must preallocate before widening them.
Warning-strict normal and optimized execution, in-memory compilation and
whitespace checks provide diagnostics. No separate Python linter is available
on PATH; shared build configuration is unchanged.
