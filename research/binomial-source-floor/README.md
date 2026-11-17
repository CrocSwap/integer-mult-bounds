# Sharp binomial source floors for separated inventories

Scoped written proof with exact finite corroboration, produced by Nick Petalas.
No new kappa. Apache-2.0.

The all-height floor `S(c) >= W^(g+1)` from Ali Romman's
[PR #5318](https://github.com/CrocSwap/integer-mult-bounds/pull/5318) now has
a sharp summary-data refinement. Fix the productive minimum L, maximum M,
maximum-rank multiplicity t, productive count W and paid count Q>=W, with
all positive paid ranks below L. The exact minimum source count among those
inventories is a finite binomial-tail expression, attained by productive
ranks `{L:W-t,M:t}` and paid ranks `{1:Q}`.

For `L^g <= c < L^(g+1)`, the new floor is

```text
W^(g+1) + (Q-W) sum_(d=0,...,g-1) Q^d
  * sum_(k=0,...,g-d) binomial(g-d,k) t^k (W-t)^(g-d-k)
      [L^(g-d-k) M^k > c].
```

[PROOF.md](PROOF.md) gives the tokenwise comparison and sharpness proof.
The entire height slab has its sharp uniform floor at `c=L^(g+1)-1`.
This is an exact extremal result for an abstract inventory class, not an
exact count or an attaining implementation for a selected supplier.

For the unchanged historical #4470 rule at product power 1024, the new
first strict uniform correction occurs at height two:

```text
L=21^1024, M=145^1024, W=10928^1024, t=224^1024,
Q >= Q0=64620^1024,

S(c) >= W^3 + (Q0-W)t^2 > W^3      when L^2 <= c < L^3.
```

For every larger height g>=2, a simple uniform correction is

```text
S(c) >= W^(g+1) + (Q0-W)
  * (W^g - (W-t)^g - g*t*(W-t)^(g-1)) > W^(g+1).
```

This quantifies part of #5318's explicitly open top-slab deficit question
at the actual product power. The correction is small. No improved accumulated
K/N coefficient, reduced compiler width or physical saving is claimed.
The selected #7000 frontier remains unchanged.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/binomial-source-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/binomial-source-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/binomial-source-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/binomial-source-floor --check-source-history
```

On another machine, replace the absolute interpreter path with its CPython
3.12 executable. The direct marker is `PASS_BINOMIAL_SOURCE_FLOOR no_new_kappa`.
The checker prints a generated receipt with package and cited-input hashes.
`--receipt /absolute/path/outside/the/checkout/receipt.json` also saves it.
It creates no files by default.

The independent root/nonroot slot enumerator passes 2,250 inventory/cap cases,
including 459 strict comparisons. A product-histogram implementation passes
1,640 attaining cases through height six. Eight semantic checks cover the
strict cutoff, height change, exact first correction and the Q<W reversal;
eight invalid summary inputs are rejected. The power-1024 application checks
the new threshold inequalities and correction directly with exact integers.
The correction has 32,353 bits; its decimal-byte SHA256 is
`cc8d4edeefa3ba49f597543ea6d0c344fa6cbbd630510204757e881b0478f3ae`.

These checks test the new extremal theorem and its application. No predecessor
executable, predecessor receipt or selected supplier replay is run. The
predecessor census, power-1024 invoice and separation contract are cited
premises. [SOURCES.json](SOURCES.json) pins their exact retained source bytes;
[TASK.json](TASK.json) records the scope change and next questions.

## Implementation limits

The theorem permits every finite height and every positive integer inventory
in its stated domain. The reference function in [floor.py](floor.py) is
deliberately bounded to L<=16, M<=32, W<=Q<=8 and heights at most six.
The fixed power-1024 application is checked separately, without expanding
its inventory or the actual compiler's large heights.

The code has no recursion or dynamic dispatch. Managed-runtime allocations
are a Power of Ten deviation; the small reference domains bound every loop
and live product histogram. Functions stay below sixty lines. Validation
uses explicit exceptions and survives `-O`. The registered commands enable
warning-strict normal and optimized Python checks. No native compiler,
formal prover, physical tape implementation, timing speedup or broad replay
is part of the claim.

## Credit and overlap

Ali Romman / aliromman #5318 supplies the exact all-height telescope and
the open quantitative-deficit question. JoyboyBrian #5067 supplies the
source census; zxv #4436 supplies the nested compiler, retaining Jacob Alan
Sussman's multinomial lockstep credit. Cinna Davis and zxv #4470 supply the
historical invoice and product/completion/splitting lineage, whose original
notices remain unchanged. Unpaidmoon #5273 supplies the height-one identity.
Nick Petalas #5109's upper coefficient is related background and is not
used in the proof. The binomial count is classical. Only the sharp five-summary
minimum and its explicit deficit application are claimed here.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19595351)
was posted after checking live claims, open PR bodies and main. The baseline
is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`.
The search covered 826 open PRs, 7,445 Discussion records and 10,178 local
README/TASK records, with complete reported pagination and note inventory.
Separate merged-work and recent-account source searches found no conflicting
target. The closed-PR bulk refresh timed out; targeted live merged searches
and the main inventory supplement it. No search certifies novelty or sees
unpublished work.

## Open next questions

- Can the complete productive histogram yield a quantitatively larger
  accumulated K/N lower coefficient? Start by retaining a second productive
  rank class in the deficit count and proving a finite-height bound for the
  same historical completion rule. The present summary minimum alone does
  not establish a better coefficient.
- Does a current physical compiler expose this exact separated-source model
  with a useful complete stock and routing bill? Start with one source-pinned
  caller and its owned lifetimes. The historical count theorem supplies no
  physical implementation or supplier admission.

Native all-column operators, physical stock/ownership/routing, precision/tape,
uniform caller closure and analytic recovery remain unrun. This is neither
a finite certificate of the current supplier nor a complete multiplication
theorem. Independent human and formal proof-kernel review are unclaimed.
