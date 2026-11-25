# Independent tiny-domain audit of the L22 union-support prune

**Result:** the union-support completion bound passes an independent exhaustive
check of every canonical restored word and every prefix at `(n,L)=(4,8)`. The
current PR #3818 C engine's union-only hit set also matches that unpruned
domain exactly. This is finite evidence, not a replay of its seven-label,
length-22 exclusion.

## Exact question and scope

For PR #3818's proposed prefix rule, can a prefix be pruned even though some
completion is universal? The rule under audit is the `fresh`-state check in
`research/f7-l22-union-census/engine/union_census.c` at PR head
`e09a08b5f85e648be373bece1b6ea1265d5ea8fa`, source SHA-256
`d34a322fc6c9fd41bc9dae337d3e84923f9dfb938c1af42de491cf536fe3cabe`:

```c
int future_same = C(S,2) + C(T,2) - C(e,2) - C(o,2);
if (|U| + future_same < 2^(N-1)-1) prune;
```

Here `S,T` are the final distinct even/odd prefix-state counts, `e,o` are
their current counts, and `U` is the union of supports of distinct same-parity
point pairs. The C implementation computes `U` after adding the fresh point.
The initialized root check uses the same condition with `U` empty and
`(e,o)=(1,0)`. Revisited states add no pair and do not change the bound.

## Why the implication is necessary

There are `2^(n-1)-1` nonzero even masks. Every such mask must be represented
by some distinct same-parity point pair if the final point set is universal;
cross-parity pairs have odd XOR and cannot supply one. A partial prefix has
already produced `|U|` masks. Its completion has at most

```text
C(S,2) + C(T,2) - C(e,2) - C(o,2)
```

new same-parity pair incidences. Each incidence can add at most one new mask.
Thus the final union support is at most `|U| + future_same`; if that is below
the required even-mask count, no universal completion exists. This argument
allows repeated path states because only distinct points contribute pairs.

## First working example and exhaustive result

The card's calibration word `01021323` independently reconstructs the path
states `0,1,3,2,6,4,12,8,0`. Its eight distinct nonclosing states cover all 16
masks. Their Hamming-weight split is `(4,4)` with excess `0`; their bit-0 split
is `(6,2)` with excess `8`. The invalid fixed balanced bit-0 budget is `5`,
while the actual-size bit-0 budget is `9`. This reproduces the old false-prune
mechanism without claiming a seven-label counterexample.

The verifier scans all `4^8 = 65,536` raw label words without the proposed
support rule, filters to the canonical restored domain, and checks every
completion/prefix pair:

| Check | Result |
|---|---:|
| Canonical restored words | 105 |
| Universal words in the unpruned domain | 26 |
| Universal words retained by the proposed rule | 26 |
| Prefix/completion checks | 840 |
| Distinct target/prefix pairs rejected by the bound | 227 |
| Rejected pairs with a universal completion | 0 |
| Maximum `actual final |U| - computed upper bound` | 0 |

For each rejected prefix key, the script counts every canonical restored
completion in the complete domain and finds zero universal completions. The
current PR #3818 engine was also compiled from the exact source bytes above for
`N=4,L=8`, split `(4,4)`, with only the union bound enabled. Its complete 22-hit
set exactly equals the independent unpruned set for that split.

## Exact source impact

The faulty predecessor is PR #2542's merged
`research/universal-f7-singleton-seedb859517b/engine.py`, source SHA-256
`82e4c407b58864c74ffd14d47f00b6b1675005ee0e0173909b7bd092491175e4` at merge
commit `ee997d5300167b46619f769c47bea9178a958978`. Its
`cyclic_census` groups with `nq & 1` but applies the fixed `budget=9` from a
balanced length-18 split. PR #2634 vendors that engine; PR #2691 ports the same
false-pruning idea to C. Their census zero-hit receipts do not establish the
corresponding exclusions. The tiny `01021323` example refutes the rule, not
every conclusion in those PRs.

The corrected PR #2973 C engine is pinned in its package at SHA-256
`265ead915d1b490c1923bce9b894ecac60f6195fc3d2ceadd6b25077238f415a`. The
independent PR #3005 implementation and oracle supply a second corrected
L18/L20 route. The new PR #3818 bound passes this additional tiny-domain audit;
the result does not certify its L22 `(9,9)` zero-hit run or its five remaining
node floors. Set-level arguments in #2773 and #2870 use separate evidence and
are not affected by the old word-engine prune.

**Adjacent receipt issue observed in the tested PR #3818 head:** when run with
`--no-even-budget --no-odd-budget` (union-only), the JSON writer fills
`all_restored_leaves` whenever the two old budgets are disabled, even though
the union budget remains active. On `(4,8,4,4)`, it reports `22`; the unpruned
domain has `27` restored words, and the union rule prunes five nonuniversal
leaves. This field is not used for the hit-set comparison above. The writer's
condition should require the union budget to be disabled as well before that
field is presented as an unpruned count. No PR #3818 source was edited here.

## Reproduction

From the repository root:

```sh
python3 -B scripts/research_package.py --package research/f7-l22-union-prune-audit --check-only
python3.12 -I -B research/f7-l22-union-prune-audit/verify.py
python3 -B scripts/research_package.py --package research/f7-l22-union-prune-audit
```

The standard-library verifier is complete in under a second. The separate
source-engine comparison used `cc -O2 -DN=4 -DL=8` on the source bytes pinned
above and `4,4 --no-even-budget --no-odd-budget`; it is recorded in the session
receipt. No seven-label or length-22 replay is registered or claimed.

## Open next questions

Independently replay PR #3818's complete L22 `(9,9)` exclusion with a separately
implemented engine. This would verify the only newly completed length-22 split
at the same finite-model scope; the current audit covers only tiny domains.
First adapt the independent #3005 engine's domain guard and node/cap receipt
for `(7,22,9,9)`. This requires a separate compute budget because the current
PR run records 388,563,293 search nodes. The audit itself does not expand into
that search.

## Credit and limits

The prefix-walk model is due to Ross Richardson; PR #2542/#2634's word model
to Aaron Wang; the parity correction and corrected engine to Nicholas Stone;
the union-support bound and current L22 extension to Nick Petalas. This
independent tiny-domain audit was produced with substantial OpenAI Codex
assistance. No human or formal proof-kernel review is claimed. Apache-2.0.
