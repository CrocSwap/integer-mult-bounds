# Two odd prime blocks and capacity under prime powers

For distinct odd primes p<q and positive a,b, the maximum number of orthogonal
columns with p+q entries is the same over `mu_(p^a q^b)` as over `mu_(pq)`.
Higher prime powers do not increase this exact capacity.
[Proof](PROOF.md) · [Certificates](RESULT.json) · [Checker](verify.py) ·
[Source pins](SOURCE-PINS.json) · [Credit](CREDITS.md).

A stronger structural statement gives the reason. Every matrix that cannot
descend to the smaller alphabet has a phase and row-permutation form
`[A D; B]`, where A is an orthogonal p-row block over mu_p, B is an orthogonal
q-row block over mu_q, and D contains the relative column phases. It therefore
has at most p columns. Explicit p-column examples show that this threshold is
sharp. The product of two prime-cycle permutations replaces the special
three-root argument in [PR #7775](https://github.com/CrocSwap/integer-mult-bounds/pull/7775).

The result does not compute every squarefree capacity. The existing eight-row
capacity remains four. No physical supplier or new kappa follows, and all
five framework assumptions remain.

From the repository root, with Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/odd-prime-phase-blocks
```

Both modes must report `PASS_ODD_PRIME_PHASE_BLOCKS`. The replay reads only
retained files. It does not need Git or network access. Exact checks cover
82,728 canonical quotient cases, 1,252,944 full subset cases, all 5,166 relative
permutations for p=3,5,7, all 82,906 cycle pairs in twelve stated alphabets,
124,766 product submultisets, 3,448 recorded Gram entries and 24 single-entry
mutants. A p=2 control shows the limit of the product lemma. All 37 retained
files are authenticated; the complete p=3 and nested eight-row source checks
run without changes.

These are finite controls for the written universal proof, not enumeration of
all matrices or a replacement for Lam and Leung's classical two-prime theorem.
No Lean, Docker, selected cold replay, independent human or formal-kernel
acceptance is claimed.

## Open next questions

Determine a new squarefree capacity, or study a changed zero-sum type with an
even prime, third prime or different row count. The theorem does not classify
the smaller blocks A and B. Native realization and complete caller costs also
remain outside scope. See [TASK.json](TASK.json).
