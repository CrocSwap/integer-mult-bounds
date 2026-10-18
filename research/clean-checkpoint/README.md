# Research note: a paid clean root checkpoint

One genuinely clean array removes the last right-subtree cancellation from
PR628's dirty product-shear recursion. An exact root-split formula then uses
**25–40% fewer primitive leaf calls**, while retaining the same total number
of scratch arrays: one clean array replaces one arbitrary dirty array.
Both child subtrees keep the existing balanced dirty implementation.

For the seed-selected **54-factor** example, the split is **22 + 32**:
**2,112 calls instead of 3,136**, with one clean and five dirty arrays instead
of six dirty arrays. This generic example is not a prime-power radix-55 kernel.
The neighboring 63-factor case is also checked algebraically, without claiming
that its kernel preparation or full transform has been implemented here.

This is a **research note and scoped interface construction; no new κ**.
Clean storage must be provided and paid for. The adapter cannot erase borrowed
dirt; a counterexample demonstrates why. Physical allocation, phase preparation,
source access, routing, repeated validation scans and precision remain charged
in [PROOF.md](PROOF.md). The selected construction is unchanged.

## Reproduce

Python 3.9+; standard library only; no downloads or optimizer needed:

```sh
python3 -B research/clean-checkpoint/verify.py
```

Expected output:

```text
PASS_CLEAN_CHECKPOINT: 32640 splits; 498 noncommutative cases; n=54: 3136 -> 2112 leaves, 1 clean + 5 dirty arrays
```

The command checks immutable predecessor bytes, recomputes the entire receipt
and compares it with [EXPECTED.json](EXPECTED.json). `--write /path/result.json`
instead writes a fresh receipt. Checks stay active under `python3 -I -O -B`.
The package can be copied elsewhere and run without the repository or Git.

## What is proved and what is checked

For the inherited balanced dirty count `D`, a clean root at split `k` costs
`2 D(k) + D(n-k)`. The first child is computed and uncomputed; the second child
is used once. If `n >= 3` and `q` is the power of two with `3q <= n < 6q`,
every cost-optimal split lies in

```text
max(q, n-4q) <= k <= min(2q, n-2q),
N(n) = 6q(n-2q).
```

Choose the largest such `k` to minimize the largest child and avoid an extra
scratch array. The proof covers every factor count; the finite checks corroborate
it. The optimum is only over **one clean root and balanced all-dirty subtrees**,
with unit leaf prices. Weighted leaf prices have their own complete recurrence;
neither a globally optimal reversible schedule nor a runtime speedup is claimed.

The bounded evidence consists of:

- All 32,640 root splits for `n=2..256`, checking the optimal interval, exact
  counts, space equality and relative count bounds.
- 498 exact free noncommutative linear-operator cases: every split for `n=2..32`,
  plus the selected splits at 54 and 63. All initial source, target and dirty
  columns are tracked. Pinned dispatcher traces match an independent compiler;
  restoration, factor order, inversion and weighted leaf bills are checked.
- 216 executions using PR628's actual rounded leaf definitions, with 2–8
  factors, lengths 1/2/5, both directions and two dirty initializations. Independent
  dense rational solves check the target against the inherited actual-call-count
  error bound. All 216 have nonzero rounding error. Exact restoration, standalone
  negative execution, target independence, same-split four-call equality and
  `3L` arithmetic-pass steps per leaf are checked.
- Fourteen algebraic/interface controls plus two rounded controls: dirty checkpoint,
  source/target aliasing, insufficient scratch, omitted restoration, wrong factor
  order, incorrect inverse chronology, dirt leakage, unpriced uncomputation and
  five phase-array aliases (source, target, clean checkpoint, each dirty level).
  Package/source corruption controls are recorded in [VALIDATION.md](VALIDATION.md).

The shorter word and the four-call word have identical rounded output **at the
same root split**. Changing the split need not preserve rounded bits; the ideal
ordered product and the conditional accuracy bound are the common comparison.
Finite replay is not formal verification of the full multiplication theorem.

## Provenance and coordination

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected record at that base is #626/#543 with
`κ = 51110230636731/31250000000000000` (0.001635527380375392).
Its record, actual assembly, source manifest, construction and maintainer review
were followed before choosing this distinct interface task.

Direct dependencies:

- Chafik Boukhalfa / chafreaky's [PR628](https://github.com/CrocSwap/integer-mult-bounds/pull/628)
  at `0768f97d06c623b8211e651543c66135796b62bf`: dirty rounded leaves,
  balanced dispatcher and conditional error/cost interface.
- @0xkilgore's concurrent [PR663](https://github.com/CrocSwap/integer-mult-bounds/pull/663)
  at `e0e546fd01b396478c68b6b6c5a16d87515983ba`: exact all-dirty call count
  and restoration audit. This contribution changes the storage interface and
  instruction word; it does not repeat that unchanged-dispatcher audit.
- @androolloyd's concurrent [PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673)
  at `0e35f56cab3cae1eb0a99447135569d687c5695a` was discovered during the final
  overlap refresh. Its multiway dirty echo changes a different schedule and can
  use more dirty arrays; no superiority over that interface is claimed here.
  Its phase-alias finding motivated an explicit root admission guard, credited
  and tested here; the original repair patch is pinned in `vendor/` as a reference.
  Its broader echo and arithmetic evidence were not re-audited in this package.

[SOURCE.json](SOURCE.json) records Git commits, paths, blob IDs and SHA-256
for every vendored predecessor file. [NOTICE.md](NOTICE.md) retains attribution
and substantial AI-assistance disclosure. No upstream or selected-result file
is edited. [CLAIM.txt](CLAIM.txt) records track, OS-random seed 54, three candidate
tasks, selection, bounded coverage and the local coordination claim. No pinned
sprint issue was available. [VALIDATION.md](VALIDATION.md) separates completed
checks from unverified repository-wide and platform obligations.
