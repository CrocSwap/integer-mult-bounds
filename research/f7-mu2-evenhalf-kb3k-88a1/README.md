# KB3k - the mu2-constant even-half condition for the 18-point cover question of `F2^7`

**Set-level finite result, no words enumerated. Outcome=partial.** The mu2
"constant per split" lead of [PR 3108](https://github.com/CrocSwap/integer-mult-bounds/pull/3108)
is pressed. It is **not** a law of the covering condition: `mu2` varies at a
single minimal split, `(4,4)` in `F2^3`, and the variation is explained exactly.
For the both-odd regime of the target splits `(11,7)`/`(9,9)`, `mu2` is constant
at every scale where covers can be produced, but that constancy is CHECKED, not
PROVEN, and it is not forced by any identity found here. The lead is therefore
**demoted as a proof filter** (it cannot be carried to PR 2911's 501/196 rows and
then to `m=6` as a hard condition). No class is decided; no cover is constructed;
no false kill is made. No new kappa.

## Object and chain of record

In the PR943 prefix-walk model
([PR 943](https://github.com/CrocSwap/integer-mult-bounds/pull/943), Ross
Richardson) a restored seven-source singleton word is universal exactly when its
prefix set `P` covers: `P + P = F2^7`. The 17-point question is closed
([PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542),
[PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634),
[PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773),
[PR 2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870));
[PR 2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911) narrowed
the 18-point question to `(12,6)`, `(11,7)`, `(10,8)`, `(9,9)`;
[PR 2933](https://github.com/CrocSwap/integer-mult-bounds/pull/2933)
classified the vanishing configurations;
[PR 2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961) fully
excluded `(10,8)` and decided three tightest classes;
[PR 3023](https://github.com/CrocSwap/integer-mult-bounds/pull/3023) killed
`(12,6)` A-vanish `(5,1)` and reduced `(4,2)`/`(3,3)` to exact walkable forms;
[PR 3034](https://github.com/CrocSwap/integer-mult-bounds/pull/3034) demoted
the parity shortcut and localized the m=5 obstruction;
[PR 3108](https://github.com/CrocSwap/integer-mult-bounds/pull/3108) walked a
partial of `(4,2)`, classified the even-half self-sum profiles, and recorded the
mu2-constancy lead this package presses.

The reduced covering object (PR 2911 reduction lemma, `cover18.py` docstring):
for `G = F2^m`, a pair `(A, B)` of subsets **covers** iff `A + B = G` (cross) and
`(A+A) u (B+B) = G` (even-half / self sums). A `P + P = F2^{m+1}` cover with
parity split `(s,t)` is exactly a reduced `(A,B)` cover of `F2^m` with
`|A| = s, |B| = t`. The 18-point question is the reduced cover of `F2^6` (64
elements) in splits `(12,6)`, `(11,7)`, `(10,8)`, `(9,9)`. Every cited PR author
was re-verified at writing with `gh pr view NNN --json author,title`: PR
2542/2634/2773/2870/2911/2933/2961/3023/3034/3108 are Aaron Wang (navinor); PR
2691/2973 are Nicholas Stone; PR 3005 is Nick Petalas; PR 1185 is
Mister-Meeseeks. This package is strictly SET-level and enumerates no words
(Nicholas Stone's `22 <= f(7) <= 24` word line is untouched).

## The exact identity (PROVEN)

For any reduced cover `(A,B)` of `G = F2^m` (`|G| = 2^m`), inclusion-exclusion
on `(A+A) u (B+B) = G` gives

```
mu2 = |(A+A) n (B+B)| = |A+A| + |B+B| - |G|.
```

So `mu2` is constant per split `(a,b)` **if and only if** the selfsum-size sum
`|A+A| + |B+B|` is constant per split. The identity holds exactly on all 41,341
`F2^3` covers (`identity_violations = 0`) and all `F2^4` covers checked. The
whole lead reduces to: is `|A+A| + |B+B|` pinned by `(a,b)` among covers?

## Verdict: not forced - the minimal variation split is (4,4) in F2^3

Complete enumeration at `F2^1` (2 elements), `F2^2` (4), `F2^3` (8) shows `mu2`
is constant per split at `F2^1` and `F2^2`, and first **varies** at `F2^3` at
split `(4,4)`. This is the minimal variation split (minimal group, and minimal
within `F2^3`).

| Group | Split | Covers | mu2 values | sum `|A+A|+|B+B|` |
|---|---|---|---|---|
| `F2^3` | (4,4) | 3,360 | 3 and 6 | 11 and 14 |
| `F2^3` | (4,5),(4,6),(4,7),(4,8),(5,4),(6,4),(7,4),(8,4) | 560-3,920 each | 4 and 7 | 12 and 15 |
| `F2^3` | every both-odd split | (see below) | single | single |
| `F2^4` | (2,8) | 15,360 | 1 | 17 |
| `F2^4` | (4,6) | 143,360 | 4 | 20 |

**Mechanism (characterized, exact).** `mu2` varies because `|A+A|` varies with
the additive structure of a half. In `F2^3` a 4-set is either a coset of a
2-dimensional subspace (an affine plane, `|A+A| = 4`) or generic
(`|A+A| = 7`). At `(4,4)` the two halves vary independently:

| half A | half B | `|A+A|` | `|B+B|` | sum | mu2 | covers |
|---|---|---|---|---|---|---|
| generic | generic | 7 | 7 | 14 | 6 | 2,688 |
| plane | generic | 4 | 7 | 11 | 3 | 336 |
| generic | plane | 7 | 4 | 11 | 3 | 336 |
| plane | plane | - | - | - | - | 0 (never covers) |

So `mu2 = 6 - 3 * (number of plane halves)`. A single structured (affine-plane)
half lowers `|A+A|` by 3 and hence `mu2` by 3. The covering condition does not
pin this. At `(4,6)` in `F2^4` the split is constant again (`mu2 = 4`) precisely
because the two halves' selfsum sizes are anti-correlated by the cover
condition: `|A+A| = 4` (plane) forces `|B+B| = 16`, and `|A+A| = 7` (generic)
forces `|B+B| = 13`; the sum stays 20. So the constancy that survives is a
correlation of the specific split, not a covering law.

## The both-odd regime of (11,7)/(9,9)

The target splits `(11,7)` and `(9,9)` are both-odd. At every both-odd split
where covers can be produced, `mu2` has been constant:

| Group | Split | Covers | mu2 | `|A+A|,|B+B|` |
|---|---|---|---|---|
| `F2^3` | (3,5),(5,3),(3,7),(7,3) | 2,688 / 448 each | 4 | 4,8 |
| `F2^3` | (5,5),(5,7),(7,5),(7,7) | 3,136 / 448 / 64 | 8 | 8,8 |
| `F2^5` | (7,7) | 310 (mutation search) | 12 | 22,22 |

So `mu2` is constant at `F2^3` (complete) and at `F2^5` `(7,7)` (310 covers,
both halves pinned `|A+A| = |B+B| = 22`). But this is CHECKED, not forced:

- The `(4,4)` `F2^3` counterexample proves the covering condition does not pin
  `mu2` in general; a structured half is enough to move it.
- Both-odd halves at `F2^6` (`|A| = 11, 9`) can still have varying `|A+A|`
  (an 11-set is a subspace plus points), so the `F2^3`/`F2^5` constancy rests on
  those small scales having rigid odd-set selfsums, not on a covering identity.
- Direct `F2^6` `(9,9)`/`(11,7)` covers were not produced in a bounded
  hill-climbing search (0 covers in 300 restarts each), so `mu2` variation at
  the exact target splits is neither observed nor ruled out.

The planned lift - "mu2 is constant per split, carry it to the 501/196 surviving
rows (PR 2911) as a filter, then lift to m=6" - is therefore **not justified**.
`mu2`-constancy is scale- and split-dependent: false for both-even splits,
empirical for both-odd splits, and unforced everywhere. This is the same shape
as the demoted scale-dependent self-sum lift of PR 3034: a two-scale regularity
with no coupling identity. It is demoted accordingly.

For completeness: PR 2911's 501/196 rows are pair-representation row
configurations (census floors of PR 2773's `(e_ex, b_ex)` rows), not concrete
`(A,B)` covers, so `mu2` cannot be evaluated on them without the row-to-cover
map; that map is the remaining "carry to the rows" step and is still blocked
(PR 3108 recorded the same blocker).

## The (4,2) walk (continuation of PR 3108)

The (12,6) A-vanish (4,2) decision walk is continued as a budget-honest partial,
never an exclusion. PR 3108's sharded walk (its `walk42.py`/`run42.py`, vendored
byte-exact here) is extended by shard 29 with a per-shard receipt that carries
explicit `complete`/`budget_hit` flags and checks the budget after every U slice
(PR 3108's lesson). This session's shard was run from empty receipts and then
re-run from empty receipts again with identical counters, to prove recomputation
(the receipt-validation trap). The inherited 29 shards (PR 3108) plus shard 29
give 30 of 2048 shards complete, 2,490 U slices, 257,845,500 normalized pairs,
with `w_candidates = 0` and `covering_configs = 0` on every walked pair. The
complete walk remains far outside one session (PR 3108 sized it at ~608
core-hours at 7,866 pairs/s), so this is a narrowed remainder and not an
exclusion; the zero counts are facts about walked pairs only.

## Anchors reproduced before any new number

| Anchor | Expected | Status here |
|---|---|---|
| PR 2870 OBSTRUCTION | parseval=696 allowed=504 deficit=192 | recomputed live (PR 3108 verify quick) |
| PR 2933 CLASSIFY | tight=2 cases=6720 | recomputed live |
| PR 2961 FOURIER (7,1) | need=175 lower=239 contradiction=True | recomputed live |
| PR 2961 CLASS82 | checked=28,815,360 covering=0 | read back (PR 3108 receipts) |
| PR 2961 CLASS60 | d_checked=169,911 d_with_transversals=0 | read back |
| PR 3023 AV51 | uv_pairs=3,049,492,320 covering=0 | read back |
| PR 3108 SELFSUM | (5,5)=3,136 and (7,7)=64 all profile (8,8,8) | read back |
| PR 3108 CENSUS33 | (3,3) covers=296,352 | read back |
| mu2 identity | `mu2 = sa+sb-\|G\|`, violations=0 over 41,341 `F2^3` covers | recomputed live |

## Reproduce

Standard library only, CPython 3.12, from the repository root (or this package
directory):

```sh
python3 -I -B research/f7-mu2-evenhalf-kb3k-88a1/verify.py quick
python3 -I -B research/f7-mu2-evenhalf-kb3k-88a1/mu2_search.py m3
python3 -I -B research/f7-mu2-evenhalf-kb3k-88a1/mu2_mechanism.py
```

Expected markers: `PASS_KB3K_QUICK`, `MU2_M3_DONE`, `MU2_MINIMALITY_DONE`. The
heavier receipts re-run with `mu2_search.py m4` (complete `F2^4` census, a few
minutes), `mu2_search.py m5odd`, `mu2_search.py m6`, `mu2_odd_search.py`, and
`verify.py full`. All arithmetic is exact Python integers (int bitmasks); no
floats are used. Vendored predecessor engines (`vendor/parity_census.py`,
`vendor/selfsum_classify_kb3j.py`, and the `walk42`/`tight` family for the walk)
are byte-exact with SHA-256 pins in `SOURCES.json`.

## Scope and limitations

Set-level only inside PR943's abstract interface. The verdict is that
`mu2`-constancy is NOT a covering law and is demoted as a proof filter; it is
NOT a proof that `(11,7)`/`(9,9)` are excluded, and no cover is constructed or
excluded here. The `(4,4)` variation is PROVEN (complete `F2^3`); the both-odd
constancy is CHECKED at `F2^3` (complete) and `F2^5 (7,7)` (310 covers) only;
`F2^6 (9,9)`/`(11,7)` `mu2` is untested (no covers produced). Not checked:
anything word-level (PR 2973/PR 3005 hold `22 <= f(7) <= 24`; untouched), the
row-to-cover map, the `(12,6)` D-vanish classes, the surviving `(10,8)` classes,
the 19-point question, and any kappa, supplier or selected-frontier implication.

## Open next questions

1. **Decide whether both-odd `mu2` is forced at `F2^6`.** Produce a `(9,9)` or
   `(11,7)` reduced cover of `F2^6` and vary `|A+A|` to see whether `mu2` moves.
   Why it matters: a both-odd counterexample closes the lead for good; a pinned
   value would license the row filter. Blocked by: both-odd `F2^6` covers are
   rare (none produced in a bounded search).
2. **Isolate the `(4,6)`-type selfsum correlation.** At `F2^4 (4,6)` the two
   selfsum sizes are anti-correlated by the cover condition. Characterize which
   splits force that correlation (constancy) versus independence (variation).
   Blocked by: the correlation has no proved coupling identity.
3. **Carry any sound both-odd condition to PR 2911's 501/196 rows** via the
   row-to-cover map. Blocked by: the map and both-odd forcing are both open.

## Credit

PR 2542/2634/2773/2870/2911/2933/2961/3023/3034/3108 (Aaron Wang): the 17-point
exclusion chain, the pair-representation rows and odd-coverage Fourier/Parseval
identity, the `(A,D)` reduction and vanishing-character restriction, the class
floors and tight-class decisions, the `(5,1)` decision and walk engine, the KB3i
remainder (parity demotion, m=5 obstruction localization), and the KB3j mu2 lead
and `(4,2)` walk this package presses and continues. PR 943 (Ross Richardson):
the prefix-walk model. PR 1185 (Mister-Meeseeks): the pinned `f(5)=12`,
`f(6)=16` record. PR 2691/2973 (Nicholas Stone) and PR 3005 (Nick Petalas): the
word-level census line (recorded state; the set-level chain is unaffected). The
vendored engines are byte-exact with SHA-256 pins and credited in `SOURCES.json`.
