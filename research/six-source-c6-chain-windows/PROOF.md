# Chain windows on the c=6 diagonal: proofs

Scoped written proofs for a fixed finite model, with an exhaustive finite
certificate in `verify.py`. This is not a statement about the unrestricted
six-source depth-two exclusion at characteristic 6, which remains the solver
verdict of PR6141.

## 0. Setting (cited, not re-proved)

The interface is the one restated in the merged package
`research/six-source-c6-centre-classification` (pinned in `SOURCES.json`),
which credits Nick Petalas's PR4231, PR4248 and PR6107.

A **floor word** is a word `w_0 ... w_35` on the sources `0,...,5` calling each
source exactly six times. `q_t` counts the letters among `w_0 ... w_{t-1}`, so
`q_36 = (6,...,6)`. For `4 <= s <= 18` write

```text
S(s) = q_s + q_{39-s},      0 <= S(s)_j <= 12,      sum_j S(s)_j = 39.
```

`S(s)` is **weight-3** when every coordinate lies in `{0,1,6,7,12}` and exactly
three coordinates lie in `{1,7}`. (An integer in `0..12` is congruent to 0 or 1
modulo 6 exactly for those five values.) A **chain on `[s0,18]`**, for
`4 <= s0 <= 18`, is a floor word whose `S(s)` is weight-3 for every
`s0 <= s <= 18`. Its **family** is the sorted multiset `S(18)`. The weight-3
condition at the pair `(0,9)` is the same condition on `q_0 + q_9 = q_9`.
Only the endpoint family is fixed: intermediate multisets may differ from it.
The longest window of a constant-multiset chain is a separate question.

The step identity (also used in open PR #7099) follows from `q_{s+1} = q_s + e_{w_s}`
and `q_{38-s} = q_{39-s} - e_{w_{38-s}}`:

```text
S(s+1) = S(s) + e_{w_s} - e_{w_{38-s}}.                              (0)
```

Call coordinate `j` **low** at `s` if `S(s)_j <= 1` (base 0), **base 6** if
`S(s)_j in {6,7}`, and **high** if `S(s)_j = 12`. Write `L(s)` for the number
of low coordinates.

## 1. Lemma A: bases are frozen along a chain

*If `S(s)` and `S(s+1)` are both weight-3, every coordinate keeps its base.*

By (0) each coordinate changes by `-1`, `0` or `+1`. Inside `{0,1,6,7,12}` the
only unit steps are `0 <-> 1` and `6 <-> 7`. The values `1,6,7,12` have the
neighbours `2,5,8,11,13` outside the set, so no unit step joins two bases. Hence
the vector of bases `6*floor(S_j/6)` is constant on a chain, and so are the
numbers of low, base-6 and high coordinates. `verify.py` also checks the lemma
on all 644,820 legal steps between weight-3 states with `4 <= s <= 17`.

## 2. Lemma B: as many highs as lows

*A weight-3 `S(s)` has exactly `L(s)` high coordinates.*

The coordinate sum is 39 and exactly three coordinates are `1 mod 6`, so the
bases sum to 36. Let `n0, n6, n12` count the coordinates of each base. Then
`n0 + n6 + n12 = 6` and `6 n6 + 12 n12 = 36`, so `n6 + 2 n12 = 6` and
`n12 = n0`.

## 3. Lemma C: a counting bound

*If `S(s)` is weight-3 with `L` low coordinates, then `5L <= s - 3` and `6L <= s`.*

A low coordinate `j` has `q_{39-s}[j] <= S(s)_j <= 1`, so at most one of the six
copies of `j` lies in the first `39-s` letters. At least five lie in the last
`s-3` letters, positions `39-s,...,35`. Distinct low coordinates are distinct
letters, so `5L <= s - 3`. A high coordinate has `S_j = 12`, hence
`q_s[j] = 6` and all six of its copies lie in the first `s` letters. By
Lemma B there are `L` highs, so `6L <= s`. (The second bound is no stronger than
the first for `L <= 3`, the only possible values since `L + L <= 6`.)

## 4. Theorem 1: the window of each family

*Let `F` be one of the six families at `(18,21)` and let `L` be its number of
low coordinates (entries `0` or `1`). For `4 <= s0 <= 18` a chain on `[s0,18]`
with family `F` exists if and only if `s0 >= max(4, 3 + 5L)`.*

| family `F` | `L` | least `s0` |
| --- | ---: | ---: |
| `(6,6,6,7,7,7)` | 0 | 4 |
| `(0,6,7,7,7,12)`, `(1,6,6,7,7,12)` | 1 | 8 |
| `(0,1,7,7,12,12)`, `(1,1,6,7,12,12)` | 2 | 13 |
| `(1,1,1,12,12,12)` | 3 | 18 |

*Only if.* The family at `s = 18` has `L` lows. By Lemma A, `S(s0)` has `L` lows
as well. Lemma C at `s = s0` gives `s0 >= 3 + 5L`.

*If.* The README lists one floor word per family. Each is a chain on
`[max(4,3+5L), 18]` with the stated family, checked literally by
`verify.py` from the word alone. Restricting a chain to `[s0,18]` with a larger
`s0` leaves a chain.

The finite certificate is independent of the argument above. The 77,220
weight-3 states `(q_s, q_{39-s})`, `4 <= s <= 18`, are enumerated exhaustively
(counts `120, 420, 1060, 2100, 3600, 5520, 7740, 9900, 11220, 11280, 9780,
7240, 4500, 2040, 700` for `s = 4,...,18`). The least `s` at which a state with
`L = 0,1,2,3` lows occurs is `4, 8, 13, 18`. A layered search from the 700 end
states at `s = 18` and a second, forward search from the start states agree on
every count in the next section.

Here is why this state graph captures words exactly. A state at index `s`
is any pair `(q,t)` with coordinatewise `0 <= q <= t <= 6`, sums `s` and
`39-s`, and weight-3 sum `q+t`. It is realizable by concatenating blocks with
letter multiplicities `q`, `t-q` and `6-t`. An edge to index `s+1` adds one
letter to `q` and removes one from `t`, recording the letters at positions
`s` and `38-s`. For a whole path, these positions are disjoint. Fill the
first `s0` positions with its initial `q`, the three positions `18,19,20`
with its final `t-q`, and the last `s0-3` positions with `6-t` from its
initial state. All multiplicities are nonnegative and their sums match the
available positions. This constructs a floor word for every graph path.
Conversely, taking these prefixes of any word gives precisely such a path.
Thus graph reachability is equivalent to existence of a word, rather than
only a necessary relaxation.

## 5. Corollary: the T2 question of PR #7099 has no solution on `s = 4,...,18`

Open PR #7099 asks which endpoint pairs of the multiset `(0,6,7,7,7,12)` are
joined by a monotone chain on `s = 4,...,18`.

*Answer: none, and the same holds for all five families other than
`(6,6,6,7,7,7)`.* A chain on `[4,18]` has `L = 0` by Lemma C at `s = 4`, since
`5L <= 1`. Directly: `S(4) = q_4 + (6,...,6) - e_{w_35}` has every coordinate in
`5..10`, and only 6 and 7 are allowed there. By Lemma A every `S(s)` stays in
`{6,7}^6`, so the family is `(6,6,6,7,7,7)`. The question as posed has the empty
answer, because the multiset cannot occur at `s = 4`.

The nonvacuous version asks about the longest window of the family. Take the
start state `(q_{s0}, q_{39-s0})` and the end state `(q_18, q_21)` as the
endpoint pair, which for `(6,6,6,7,7,7)` and `s0 = 4` is the pair
`(M_4, D, M_18)` of PR #7099. A pair is **joined** if some chain on `[s0,18]`
passes through both. At the least window start of each family:

| family | `s0` | start states | end states | joined pairs |
| --- | ---: | ---: | ---: | ---: |
| `(6,6,6,7,7,7)` | 4 | 120 | 20 | 2400 |
| `(0,6,7,7,7,12)` | 8 | 180 | 120 | 720 |
| `(1,6,6,7,7,12)` | 8 | 180 | 180 | 1080 |
| `(0,1,7,7,12,12)` | 13 | 180 | 180 | 360 |
| `(1,1,6,7,12,12)` | 13 | 180 | 180 | 360 |
| `(1,1,1,12,12,12)` | 18 | 20 | 20 | 20 |

So on its longest window `[8,18]` the T2 relation joins 720 of the 21,600 pairs.
The counts for `(6,6,6,7,7,7)` and the sizes of
the six end families (20, 120, 180, 180, 180, 20; 700 in all) agree with the
numbers reported in open PRs #7099 and #7029. They are by-products of this
computation, not a replay of those packages. The other joined-pair counts have
no closed form here.

## 6. Theorem 2: how far down the (0,9) hypothesis needs the chain

*For `4 <= s0 <= 18` there is a floor word that is weight-3 at `(0,9)` and at
every `s` in `[s0,18]` if and only if `s0 >= 8`.*

A weight-3 `q_9` has entries in `{0,1,6}` (7 exceeds the cap), three entries
equal to 1 and coordinate sum 9, so the other three entries sum to 6 from
`{0,6}`. Hence `q_9` is a permutation of `(1,1,1,6,0,0)`; there are 60 of them.

*Only if.* Let `s0 <= 9`, so that `s = 9` lies in the chain. The coordinate `f`
with `q_9[f] = 6` has `q_30[f] >= q_9[f] = 6`, so `S(9)_f = 12` and `f` is high.
Then `L >= 1` by Lemma B, and Lemma A with Lemma C at `s0` give
`s0 >= 3 + 5 = 8`.

*If.* The word `345555552443322111234111223344000000` is a floor word with
`q_9 = (0,0,1,1,1,6)`, weight-3 at `(0,9)`, and weight-3 at every `s` in
`[8,18]`; its family is `(0,6,7,7,7,12)`. It also serves every larger `s0`.

The consequence is for the conditional exclusion stated in open PR #7029
(no floor word is weight-3 at `(0,9)` and at every `s = 4,...,18`). Its
chain hypothesis is needed only from `s = 7`: the pair of hypotheses
`(0,9)` and `[7,18]` is already contradictory, while `(0,9)` and `[8,18]` are
jointly satisfiable. The exclusion in #7029 is cited and not replayed; this
theorem is proved from the definitions above.

## 7. What is and is not established

Established, in the stated model: Lemmas A to C; Theorem 1; the empty answer of
Section 5 and its joined-pair counts; Theorem 2. The witnesses are checked for
weight-3 at the listed pairs; no claim is made that any of them realizes any other mask
of the depth-two interface. The characteristic-6 six-source depth-two exclusion,
other characteristics and source counts, and every pair other than
`(s,39-s)` for `4 <= s <= 18` and `(0,9)` are outside this result.
