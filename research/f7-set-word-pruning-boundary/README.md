# Separate set-cover pruning from word-census exclusions

**Scoped source audit and finite certificate; no new f(7) bound or kappa.**

The retained PR2542 `joint_covers` has two interface traps. Its split sizes
refer to **coordinate bit 0**, despite a docstring saying weight parity.
Its optional degree-two filter is exact as a set predicate, but the stated
justification that every minimum-length universal word is Hamiltonian is false:
the minimum-length three-label word `010122` has a degree-one prefix vertex.

The actual-size set enumerator agrees with a separate unpruned subset oracle
in all 200 split/filter domains over dimensions 1–4. This checks, on the
actual function, the scope that Nicholas Stone's
[PR2973 parity correction](../f7-weight-parity-census-correction/README.md)
states in its MATH.md section 4:
the old **word** exclusions need replacement evidence, while this set-level
enumerator is not refuted merely for using bit 0. Four pinned set-search
call sites leave the optional degree filter disabled. No additional false
seven-label exclusion is inferred from the new degree counterexample.

This is an independent audit of an adjacent contract. PR2973 already gives
`01021323`, corrected budgets and source-impact prose; James Reed's
[PR3096 audit](../f7-bit0-false-prune/README.md) already checks small words;
[Nick Petalas's PR3005](../f7-union-support-audit/README.md) already supplies a
separate complete seven-label word implementation. None is rerun at full
seven-label scale here. The contribution is the actual set-interface check,
the degree-filter counterexample, and the precise separation of dependencies.

## The counterexamples and their scope

### Minimum length does not justify minimum degree two

In the singleton prefix-walk model, `010122` traces

```
0, 1, 3, 2, 0, 4, 0.
```

Each of three labels occurs twice, so it restores. Its distinct prefix set
`P={0,1,2,3,4}` covers all eight masks: `{0,1,2,3}` covers the lower two
coordinates, and its XORs with `4` give `{4,5,6,7}`. Every restored word
using all three labels has length at least six, because every label must
occur a positive even number of times. Thus this length-six word is minimal.
Vertex `4` has only neighbor `0` in the induced cube graph. The actual call
`joint_covers(3, [(3,2)])` returns 18 covers including `P`; enabling
`require_min_degree=True` returns none.

This refutes the general minimum-length justification in the retained
`joint_covers` docstring. It does **not** refute the predicate itself, or its
use after proving a simple cycle of length at least four is required. If a
closed word has `|P|=L>=4`, all its nonclosing prefix states are distinct,
and every vertex has two distinct cycle neighbors. The hypothesis `|P|=L`
cannot be replaced by minimum word length. The two-vertex closed walk is
also excluded from that simple-cycle implication.

`010122` is the predecessor's reflected-Gray construction at three labels;
the construction and minimum-length observation are not claimed as new.
The finding is its use against this particular retained interface claim.

### Weight parity is not the actual `joint_covers` partition

Reconstructing PR2973's `01021323` gives

```
0, 1, 3, 2, 6, 4, 12, 8, 0.
```

Its eight distinct states cover all 16 masks. Weight parity gives sizes
`(4,4)` and within-side collision excess zero; bit 0 gives `(6,2)` and
excess eight. The balanced budget is five, whereas the actual-size bit-0
budget is nine. Calling the pinned old `cyclic_census` on this forced word
returns one hit with no budget or budget nine, and zero with budget five.
This directly corroborates the known false prune, without a seven-label
counterexample. The actual `joint_covers(4,[(6,2)])` contains its prefix
set; `joint_covers(4,[(4,4)])` does not. The latter call describes a different
set domain, rather than a failed enumeration of the former domain.

A linear coordinate change cannot silently repair the word interface, as
PR2973's MATH.md section 4 also notes; here is an explicit witness. Define
`T(x)` by replacing bit 0 by the weight parity of `x` and retaining
all other bits. It is an invertible linear map, so it preserves XOR coverage
and takes the original weight split to an actual bit-0 split. But it maps
`e_i` to `e_i+e_0` for `i>0`, changing the singleton-step alphabet.
For the eight-state witness it gives
`T(P)={0,1,2,3,5,6,9,12}`, whose vertex `12` is isolated in the *original*
cube graph. The source filter accordingly rejects it. A transported word
must use the transported adjacency relation; testing the original relation
after this map is unjustified.

## Why the actual-size set pruning survives this objection

Fix a nonzero linear functional, here `ell(x)=x&1`, and actual final sizes
`s,t` in its two classes. Put `Q=2^(n-1)`. If the set covers the whole group,
the union of its two within-class pair supports has size `Q-1`. Hence the
sum of the separate collision excesses satisfies

```
coll <= C(s,2) + C(t,2) - (Q-1).
```

This is the budget used by `joint_covers`. When a new distinct point is
added to one class, its XORs with the existing points in that class are
distinct. The number already in the old support is exactly the increment
in collision excess. Thus `coll` is monotone, and exceeding the final
actual-size budget cannot discard a covering completion.

At current sizes `e,o`, at most `s*t-e*o` new cross pairs and
`C(s,2)+C(t,2)-C(e,2)-C(o,2)` new within-class pairs remain. Each pair can
cover at most one previously missing mask, which justifies the two remaining
capacity prunes. The state saves and restores the affected support, collision
count and both coverage unions at each branch.

Every zero-containing set with the stated actual sizes has one increasing
ordering of its nonzero points. At each step exactly the branch for that
point's bit-0 class can choose it. Conversely each finished branch is one
such set. Exact union coverage is checked at leaves. This gives the written
completeness argument for valid integer inputs `n>=1`, `1<=s<=Q`, `0<=t<=Q`,
with an uncapped run and no degree filter. With the filter, completeness is
for covers additionally satisfying the degree predicate, not for arbitrary
minimal words. A reached node cap raises `OverflowError`, which this audit
requires to remain a failure rather than a zero-hit result.

The argument does not substitute `s=t=L/2`. Time parity bounds the sizes of
the **weight** classes of a closed singleton word, not its bit-0 classes.
That substitution is the separate error in the old word engine.

## Executed finite check and dependency boundary

The direct oracle visits every subset containing zero and computes all
pairwise XORs without a collision or capacity prune. For each actual bit-0
split it compares the complete returned set collection, including duplicates
and partition labels, with `joint_covers`, with the degree filter both off
and on. It also checks that the separate `set_level_splits` selector retains
every observed covering split. Empty splits and zero-hit domains are included.

| Dimension | All zero-containing sets | Covers | Covers with minimum degree two |
|---:|---:|---:|---:|
| 1 | 2 | 1 | 0 |
| 2 | 8 | 4 | 1 |
| 3 | 128 | 64 | 20 |
| 4 | 32,768 | 23,552 | 5,074 |

The total is **32,906 sets and 200 exact domain comparisons**. Every domain
has a count and canonical returned-set SHA256 in [RESULT.json](RESULT.json).
During this enumeration the subject's `cyclic_census` is replaced in memory
by a function that raises immediately, making accidental use a failure.
The PR2542 engine, PR2634 copy and PR2773 vendor copy are byte-identical,
SHA256 `82e4c407b58864c74ffd14d47f00b6b1675005ee0e0173909b7bd092491175e4`.
One execution therefore audits those shared bytes, rather than claiming
three independent implementations.

The source-bound call-site inventory covers six named Python files, plus
PR2691's native rule. It is not a whole-repository dependency proof.

| Predecessor evidence | Consequence of the audited premise |
|---|---|
| PR2542 `search.py` and `verify.py`, L18, `budget=9`, `simple=True` | Two word calls apply the invalid bit-0/balanced budget. Their old zero-hit receipts cannot justify exclusion; use separate corrected exclusion evidence. |
| PR2634 `verify.py`, full and sharded L18 replay | Two calls repeat the same invalid premise. Reproducing the historical counters does not repair it. |
| PR2634 `census20.py`, L20, `budget=27`, `simple=True` | Its partial simple-cycle traversal is not a complete exclusion of the claimed word class. |
| PR2691 `f7_census.c`, `BUDGET=27`, grouping by `nq&1` | Its 15-shard completion inherits the same unsound rule; the old 6,305,209,079-node receipt remains historical filter evidence. No new native replay is performed here. |
| PR2773 `verify.py`, sharded L18 replay | One more call repeats the invalid historical word evidence. That invocation is separate from the set-level computations below. |
| Four PR2542 set-search calls in `search.py`, `verify.py`, `test_engine.py` | All use the default degree flag `False`; their n=5 size-10 controls use the set-level split selector. Neither the bit-0 choice nor the new degree counterexample refutes these calls. The full n=5 controls were not rerun. |
| PR2773 `cover17.py` and `search17.py` | Both import only standard-library modules and use their own set routines. Fresh calculations reproduce empty rows for `(9,8)/(8,9)` and, conditional on the separately recorded excess floors, `(10,7)/(7,10)`. They leave two rows for each `(11,6)/(6,11)` orientation. This reproduces the retained arithmetic without the word engine; the large Sidon floor censuses were not rerun or newly validated. |

PR2973 and PR3005 provide **replacement** word-exclusion evidence in their
own packages. They do not make the old prune valid. Their complete n=7
receipts and resulting `22<=f(7)<=24` claim are not revalidated by this
small-domain check. Later Fourier/set-level results must retain their own
hypotheses; this audit neither revokes nor independently certifies them.
No selected-result file or frozen predecessor is changed.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B research/f7-set-word-pruning-boundary/verify.py
python3 -I -B research/f7-set-word-pruning-boundary/test_verify.py -v
python3 scripts/research_package.py --package research/f7-set-word-pruning-boundary --check-only
python3 scripts/research_package.py --package research/f7-set-word-pruning-boundary
```

Expected marker:
`PASS_F7_SET_WORD_BOUNDARY sets=32906 comparisons=200 degree_counterexample=010122 no_new_kappa`.
The tests exercise the actual counterexamples, a balanced-size budget mutant,
node-cap failure, changed source bytes, wrong partition labels, duplicate
results, a newly enabled degree-filter caller, and missing/changed receipt
fields. The verifier uses explicit checks under `-O`; `--emit` prints a
fresh receipt and does not overwrite files. Loaded source is authenticated
and compiled from bytes, without importing a predecessor bytecode cache.

[SOURCES.json](SOURCES.json) pins the base and all live inputs.
[TASK.json](TASK.json) records the refined revision-6 `census-pruning-audit`
scope, predecessor heads, overlap and remaining obligations. The base is
`463113d675af7410ac91d53a4fed51ec6494eb9a`. The claim is in
[discussion #1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19001818).
This is author-checked executable
and written evidence with a separately implemented oracle; no independent
human review, proof-assistant verification, hosted CI success, full supplier
replay or theorem admission is claimed.

## Open next questions

1. **Should a maintained successor expose separate set-cover and simple-cycle
   APIs?** The new counterexample shows why a minimum-length description is
   insufficient. First define a `simple cycle, |P|=L>=4` contract, preserve
   the actual bit-0 split meaning, and carry these witnesses into its tests.
   This is an interface decision; frozen predecessor files must stay pinned.
2. **Which historical entry points should point to replacement evidence?**
   The six Python calls and one native rule above identify a bounded target
   for an annotation or successor entry point. First decide whether a caller
   intends historical counter reproduction or a mathematical exclusion.
   Independent scientific review of the corrected n=7 receipts remains a
   separate obligation; this package does not reopen the completed independent
   implementation task or launch a length-22 search.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Ross Richardson supplied the PR943 singleton prefix-walk model. Aaron Wang
supplied PR2542/PR2634's word and set engines, reflected-Gray construction,
and PR2773's set-level audit. Nicholas Stone supplied PR2691's C traversal
and PR2973's parity correction and `01021323` counterexample. Nick Petalas
supplied PR3005's independent union-support word census, and James Reed
(@jwr404) supplied PR3096's earlier tiny false-prune audit. Douglas Colkitt
supplied the retained project and contribution framework. This package adds
the particular degree-contract counterexample, set-interface oracle and
dependency audit; it claims no priority over those constructions or the
corrected f(7) bound. OpenAI Codex assisted substantially with derivation,
implementation, checking and writing. No independent human review is
claimed. Apache-2.0.
