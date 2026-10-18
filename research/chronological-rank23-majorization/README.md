# Uniform optimum for chronological rank-2/3 blocks

**Independent source-bound audit of Cinna Davis [PR1960](https://github.com/CrocSwap/integer-mult-bounds/pull/1960), with an all-exponent strengthening. No new supplier or kappa.**

For both literal selected gauge44 event traces, the PR1960 block-mass profile
minimizes the entire power bill for **every real exponent `0<q<1`**, uniquely
as a rank histogram. This holds for all disjoint contiguous rank-2/3 blocks
of total rank at most 16, treating phase markers as free and every other
noneligible event as a barrier. Singleton blocks preserve unmerged calls.
All physical interface costs are waived, exactly as in the predecessor's
optimistic model. The optimum per complete local call is

```
{1:2412, 2:362, 3:123, 4:158, 5:87, 6:127,
 8:9, 9:1, 12:4, 15:5, 16:3}
```

The full paid rank mass remains **5,586**. The optimal schedule has 162
nontrivial blocks covering 365 source calls, plus all unchanged calls.
This independently corroborates PR1960's profile. PR1960 numerically optimizes
at its fixed 5% target; here an integer majorization certificate proves the
same profile simultaneously optimal throughout the power interval. This
package does not recompute its numerical ceiling or 5% threshold.

## Exact scope and source binding

Original assigned base `1d201395e037bd3fcb0175007fdcd0154878e613`; integrated
onto `178a293edbd162fe3ce13e81a97af921366bd100` with unchanged scientific inputs.
Predecessor
`df468539cb55e3c90e0dc492394450b162beeb56`. The selected source is
`research/community-frontier1094-audit/selected-replay.tar.gz`, SHA256
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.
Both checkers read the unique member
`candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz`, SHA256
`241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a`.
Each orientation has 24,767 events, 641 eligible runs and 850 eligible calls;
all paid climb and centre events reconstruct the complete original profile.
The trace is consumed in full; stored digests supplement, rather than replace,
that reconstruction. Frozen inputs and the selected record are unchanged.

The [task card](TASK.json) records the accepted selector, changed scope,
predecessor pins and overlap. This is a changed scope from selected moment
arithmetic to a pending packing claim on the selected trace, because the former
already has several independent audits. [PR1960's released claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18926727)
is the immediate predecessor; [our independent claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18929908)
identifies the distinct check. The general majorization technique is standard;
the contribution is its source-bound application and independent evidence.

## Model

A word consists of positive ranks. A legal partition splits it into contiguous,
nonempty blocks, each having total rank at most 16. A singleton is allowed.
Its mass vector is the list of block totals, sorted decreasingly. For any fixed
`0 < q < 1`, its cost is the sum of the q-th powers of its masses. Comparisons
pad vectors with zeroes to the number of ranks in the word. All calls outside
the given runs remain fixed and all physical implementation charges are waived.

For equal-total nonnegative vectors, `c` majorizes `x` when every initial sum
of the decreasingly sorted `c` is at least the corresponding sum of `x`.
The strict concavity of `t -> t^q` on `[0,infinity)` then gives

    sum c_i^q <= sum x_i^q,

with equality exactly when the mass histograms are the same. Thus a feasible
vector majorizing every legal vector is simultaneously optimal for all
`0 < q < 1`, uniquely as a mass histogram. Chronological partitions need not
be unique.

## Complete all-n theorem

1. For the word `3^n`, write `n = 5k+r`, with `0 <= r < 5`.
   The canonical mass vector is `k` copies of 15 followed by `3r`, omitting a
   zero remainder. It majorizes every legal partition. For `n=0`, interpret
   this as the empty word, empty vector and zero cost.

2. For the word `(2,2,3^n)` and `0 <= n < 4`, the canonical vector is the
   single mass `4+3n`, namely 4, 7, 10 or 13. For `n >= 4`, write
   `n-4 = 5k+r`, with `0 <= r < 5`. The canonical vector is

       (16, 15 repeated k times, 3r),

   again omitting a zero remainder. It majorizes every legal partition.

Both statements hold for every nonnegative integer n, and their optimality and
histogram uniqueness hold simultaneously for every real `0 < q < 1`.

### Proof

For `3^n`, every block mass is a multiple of 3 and at most 16, hence at most 15.
If `T=3n`, the sum of the k largest masses of any legal vector is therefore at
most `min(T,15k)`. The proposed vector is feasible, by grouping five consecutive
threes at a time, and its sorted initial sums equal `min(T,15k)` for every k.
It consequently majorizes every legal vector.

For `(2,2,3^n)`, the total is `T=4+3n`. If `n<4`, the whole word has mass at
most 13 and forms one legal block. Its vector `(T)` majorizes every partition
of total T.

Suppose `n>=4`. A block mass of 16 must contain both twos: a block with no two
has mass divisible by 3, while one with exactly one two has mass congruent to 2
modulo 3. Therefore at most one block has mass 16. All other block masses are
integers at most 15. For any sorted legal mass vector x and any `k>=1`,

    x_1 + ... + x_k <= min(T, 16+15(k-1)).

The proposed vector is feasible: its first chronological block contains the
two twos and the first four threes, with mass 16; its remaining blocks contain
five threes each, plus a final remainder of at most four threes. Its decreasing
initial sums equal `min(T,16+15(k-1))` at every k. This proves majorization.
Strict concavity gives the stated power-cost optimality and unique histogram.

### Optional direct concavity certificate

The majorization-to-cost step can also be expressed without a numerical
calculation. For a sorted vector v, write `S_k(v)` for its first-k sum, including
`S_0=0`. For every `t>=0`,

    sum (v_i-t)_+ = max_k(S_k(v)-kt).

Thus majorization and equal total imply
`sum min(c_i,t) <= sum min(x_i,t)` for every t. Since, for `0<q<1`,

    x^q = q(1-q) integral_0^infinity min(x,t) t^(q-2) dt,

integration proves the cost inequality. Different mass histograms have
different piecewise-linear truncated-mass functions, so the nonnegative
difference is positive on an interval. The positive integral weight then
makes the cost inequality strict for every `0<q<1`.

## Supplied twelve run types

Every supplied run of total mass at most 16 is optimally a single block.
The three longer run types follow from the theorem:

| Run | Multiplicity | Canonical sorted masses |
| --- | ---: | --- |
| `(2)` | 362 | `(2)` |
| `(3)` | 123 | `(3)` |
| `(2,2)` | 16 | `(4)` |
| `(3,2)` | 5 | `(5)` |
| `(3,3)` | 124 | `(6)` |
| `(2,2,2)` | 3 | `(6)` |
| `(2,2,2,2)` | 1 | `(8)` |
| `3^4` | 3 | `(12)` |
| `(2,2,3^4)` | 1 | `(16)` |
| `3^8` | 1 | `(15,9)` |
| `(2,2,3^8)` | 1 | `(16,12)` |
| `(2,2,3^24)` | 1 | `(16,15,15,15,15)` |

Their combined canonical histogram is

    {2:362, 3:123, 4:16, 5:5, 6:127, 8:1, 9:1,
     12:4, 15:5, 16:3}.

It contains 647 blocks of total rank 2132, replacing 850 original calls
(`418` of rank 2 and `432` of rank 3) in 641 runs. Add every unchanged outside
call to both profiles. Per-run majorization proves the global power-cost
minimum, uniquely as a combined mass histogram, for the independent-run
relaxation. This statement does not permit blocks to cross run boundaries.

## Independent finite checks

`verify.py` reconstructs the source census and uses only integer arithmetic.
For each run prefix i and mark budget k, it maximizes the total mass of at most
k marked blocks over every complete legal partition of that prefix. The last
block is either unmarked (`F[start,k]`) or marked (`F[start,k-1]+mass`). Every
legal interval ending at i is considered, so induction on i proves exhaustive
coverage. For any fixed partition the best k marks select its k largest masses.
The resulting upper bounds equal every sorted prefix of the feasible candidate.
The checker also counts every chronological partition independently of its
maximization recurrence and reconstructs the complete source-indexed schedule.

`independent.py`, written by a separate exact-verification specialist, imports
neither this checker nor predecessor code. It enumerates reachable sorted mass
vectors by suffix recursion, retaining multiplicities of chronological
partitions. It independently parses the pinned source and checks all 2,753
type/vector pairs (distinct mass vectors summed over the 12 types),
representing 23,499,934 chronological
partitions (sum over types, not over the whole trace). It checks 68,595 sorted
prefix inequalities. The written proof above supplies the all-parameter
statement; the finite checks supply exact coverage of this source instance.
Neither is a formal-kernel proof or independent human review.

Positive controls include reordered candidate masses, harmless phase markers,
and a feasible changed-family optimum. Failure controls include a legal but
inferior partition, omitted mass, an oversized block, missing source positions,
wrong block mass, and the invalid extension of greedy optimality to all rank
strings. In particular `(2,3,3,3,3,3)` has greedy masses `(14,3)`, while the
feasible `(15,2)` strictly dominates it. This prevents extrapolating the
special-family proof to arbitrary rank-2/3 words.

The test harness removes the actual majorization detector and requires the
control suite to fail. It also exercises missing, duplicate and corrupted
receipts, source drift, explicit generation/no-overwrite behavior, and
optimized read-only relocation. Default verification consumes fixed receipts
and never creates or repairs them.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/chronological-rank23-majorization
```

The registered commands run both independent engines and the failure-sensitivity
tests. Expected markers include `PASS_CHRONOLOGICAL_RANK23_MAJORIZATION` and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
`RESULT.json` stores the primary prefix bounds and full source-indexed schedule;
`INDEPENDENT.json` stores the independently enumerated counts and witnesses.
Explicit first-time generation uses `verify.py --write` (refuses overwrite)
and `independent.py --json` (prints only); ordinary replay compares every field.

## Limits

The normalized moment at any fixed `m,W` has the same order, by multiplying
the power bill by the positive constant `m^(-q)/W`, with `q=1-a`.
Unchanged external charges can be added to both bills. This establishes the
optimal profile within the relaxation, not realizability of the merged calls.
It does not establish arbitrary-dirty-input semantics, operand independence,
source gathering, output routing, frame compatibility, hosting, restoration,
precision, an all-size compiler, or the complete multiplication recurrence.
No Lean theorem, selected full cold replay, new kappa or adoption is claimed.
At q=1 all mass-preserving profiles tie; the uniqueness claim is only for
`0<q<1`. Chronological partitions with the same optimal histogram may differ.

## Open next questions

- Can nonconsecutive consolidation improve the fully charged physical bill?
  The first useful step is to identify one actual source-level block with
  operand lifetimes and price gather/scatter, frames, hosting, precision and
  dirty restoration. The event trace alone lacks that caller contract.
- For changed run alphabets or caps, recompute the sorted-prefix maxima before
  assuming any one histogram works for all exponents. The one-initial-2
  counterexample shows why the present greedy proof does not automatically
  generalize. This package does not reopen the unchanged cap-16 family.

Structured next questions and the scoped stop rule are in `TASK.json`.

## Credit

Cinna Davis (1337isnot1337), PR1960, supplied the chronological mixed-rank
relaxation, source census, interval optimizer and target-specific result.
The selected gauge44 word, native compiler and owner placement retain their
original attribution, including Jeremy Kothe and Rohan Arun, through the
selected record/source manifest. Earlier rank-one batching and commutation
work (PR1779/1817) and higher-rank same-ADD pairs (PR1836) have different domains;
we do not claim their mechanisms. No predecessor code is imported or executed.

Prepared by Ross Richardson with substantial OpenAI Codex assistance, including
separate `math-asymptotic-bounds` proof and `math-exact-circuit-verification`
enumeration/review specialists. This is mathematical and implementation
cross-checking by AI agents, not independent human verification. Apache-2.0.
