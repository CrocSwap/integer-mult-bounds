# Correct collision budgets and the scope of the word census

This note applies to the PR943 singleton prefix-walk model. It separates the
mathematical necessities from the computational receipts. A corrected complete
zero-hit census at all five length-20 splits proves `f(7) >= 22`; with the
existing verified length-24 construction this gives `f(7) in {22,24}`. The old
bit-0 census receipts do not supply that corrected census.

## 1. Prefix states and the partition that follows time

For a word `w` of length `L`, put `q_0=0` and
`q_i=q_(i-1) XOR (1 << w_i)`. Restoration means every label is used a positive
even number of times, so `q_L=0` and `L` is even. Write `P` for the **set** of
prefix states. Universality is `P+P=F2^n`, with addition given by XOR.

Each step flips weight parity, so `wt(q_i)=i (mod 2)`. Let `E` and `O` be
the distinct even- and odd-weight states, and `s=|E|`, `t=|O|`. At even length
`L`, each size is at most `L/2`: the `L/2+1` even-time positions have the
forced coincidence `q_0=q_L`, and there are `L/2` odd-time positions.

This upper bound uses **weight parity**, not the value of any one state bit.

## 2. Both necessary collision budgets

For a nonzero even-weight mask `x`, let `A_x` and `B_x` count its unordered
representations by distinct points within `E` and within `O`, respectively.
Put

```
a = C(s,2) - |supp A|,
b = C(t,2) - |supp B|,
Q = 2^(n-1).
```

If `P` is universal, `supp A union supp B` is exactly the `Q-1` nonzero
even masks. Consequently

```
a+b <= C(s,2)+C(t,2)-(Q-1).                 (even budget)
```

For an odd mask `y`, let `r_y` count representations by `E x O`. Full odd
coverage means every one of the `Q` masks has `r_y>=1`; therefore

```
cross_excess := s*t - |supp r| = s*t-Q.     (odd budget at a universal leaf)
```

For a partial search state, both excess counts are nonnegative and
nondecreasing when a **new distinct point** is added. A branch may be rejected
once either exceeds the target split's budget. A repeated visit to an existing
prefix state contributes no new point, no new pair, and no collision increment.
Visit multiplicities can support backtracking, but mathematical coverage and
collision counters remain set-based. In particular, the old description
"multiset collision semantics" must not be interpreted as counting repeated
visits as new elements of `E` or `O`.

| Weight split | Even budget `a+b` | Odd excess at a universal leaf |
|---|---:|---:|
| `(10,10)` | 27 | 36 |
| `(10,9)` | 18 | 26 |
| `(10,8)` | 10 | 16 |
| `(9,9)` | 9 | 17 |
| `(10,7)` | 3 | 6 |

These are necessary conditions, not sufficient conditions. Exact leaf coverage
is still required. A budget may skip a universality test or prune branches in a
search for universal words; it must not be used to assert that the survivors
are **all** restored words or all simple cycles.

## 3. The pair identity and the complete split list

Let `S=supp A intersection supp B`. Double-counting two distinct cross pairs
with equal sum gives

```
sum_y C(r_y,2) = 2 * sum_x A_x*B_x.
```

Indeed, each unordered `E`-pair and `O`-pair with the same sum produces exactly
two collisions of cross pairs. Since `C(r,2)>=r-1` for `r>=1`, a universal
set satisfies

```
sum_x A_x*B_x >= ceil((s*t-Q)/2) =: need.
```

On shared support expand `A_x*B_x` as
`1+(A_x-1)+(B_x-1)+(A_x-1)*(B_x-1)`. Summing bounds the same quantity by
`|S|+a+b+a*b`. Full even coverage gives
`|S|=C(s,2)+C(t,2)-a-b-(Q-1)`. Thus the necessary arithmetic rows are

```
B0 = C(s,2)+C(t,2)-(Q-1),
a+b <= B0,
B0+a*b >= need.
```

At `n=7, L=20`, counting first leaves the unordered splits
`{7,10},{8,9},{8,10},{9,9},{9,10},{10,10}`. The `(8,9)` case has `B0=1`
and `need=4`. Its rows have `a*b=0`, so `B0+a*b<=1<4`; the mirror is
identical. No other split is lost to this basic identity.

Cyclic rotation by one label translates the prefix set by `q_1`:
`P'=P+q_1`. Translation preserves `P+P`, restoration, and the number of
distinct points; `q_1` has odd weight, so it swaps `E` and `O`. Relabeling
coordinates by first occurrence restores restricted-growth form and preserves
weight parity and coverage. Rotation commutes with coordinate relabeling, so
it also induces a bijection on canonical word classes. Thus existence at
`(s,t)` is equivalent to existence at `(t,s)`.

It follows that **exactly five** length-20 split representatives require an
exclusion, unless one imports a separate stronger set-level exclusion:

```
(10,10), (10,9), (10,8), (9,9), (10,7).
```

At `(10,10)`, `|P|=20` and all `q_0,...,q_19` are distinct: self-avoidance
is valid there. It is not a valid global restriction on the other four
splits. At `L=18`, the same counting and identity analysis leaves only `(9,9)`;
then `|P|=18`, so the simple-cycle restriction is valid for that specific
length-18 exclusion.

## 4. Why the fixed bit-0 budget is unsound

The algebra in sections 2 and 3 is valid for **any nonzero linear functional**
`ell:F2^n->F2`, with its kernel and other coset replacing even and odd weight.
In particular, bit 0 is a legitimate partition for a set-level cover census
whose parameters `s,t` are the actual cardinalities in those two classes.
`joint_covers` is not invalid merely because it uses bit 0.

The word-level error is substituting `L/2,L/2` into the budget while grouping
the states by bit 0. Time parity does not fix those class sizes. For a
20-point set of bit-0 sizes `10+d,10-d`, its valid even budget is `27+d^2`,
not invariably 27. A coordinate permutation preserves cube adjacency; a
general linear change of coordinates need not. Thus general set-cover
symmetry cannot turn this wrong word-level budget into the correct one.

A counterexample lies inside the **simple balanced** word class itself:

```
n=4, L=8, canonical word 01021323
prefix set {0,1,2,3,4,6,8,12}
coverage = all 16 masks
weight split = (4,4)
bit-0 split = (6,2)
balanced budget C(4,2)+C(4,2)-7 = 5
bit-0 collision excess = 8
correct bit-0 budget C(6,2)+C(2,2)-7 = 9
```

All eight nonclosing states are distinct, and every label occurs twice. The
old word-level prune rejects this universal word because `8>5`. The
counterexample establishes unsoundness of the prune, not the existence of a
seven-label counterexample at length 18 or 20. Reproducing node counts between
the old Python and C implementations proves traversal agreement, not the
necessity of their shared prune.

## 5. Correction to the earlier "zero slack" claim

`session2/agent-c/BUDGETS.md` correctly derives both budgets and the split
list, but its conclusion that any strengthening of `need` would immediately
kill `(9,9)` and `(10,7)` is false. Although `need=B0`, the upper bound is
`B0+a*b`, not simply `B0`.

For `(9,9)`, the arithmetic row `a=b=1` has `upper=10>need=9`; for
`(10,7)` it has `upper=4>need=3`. Even replacing `need` by `need+1` leaves
36 and 3 arithmetic rows, respectively. The maximum upper values under the
basic budget are 29 and 5. Such rows are necessary-condition rows, not
constructed covering sets; they suffice to refute the claimed logical
implication. A stronger bound could prune rows, but must be compared with
their actual upper values before claiming an exclusion.

## 6. What a complete length-20 exclusion proves

Suppose a restored universal word has even length `L<20`. Append `(j,j)`
repeatedly, for any label `j` already in the alphabet, until the length is 20.
Each appended pair takes the current state `0` to `1<<j` and back to `0`.
The old prefix set is a subset of the new one, so full pairwise-XOR coverage
is preserved; all label counts remain positive and even. Canonical first-
occurrence order can also be preserved.

Therefore, excluding **all** restored universal length-20 words also excludes
every shorter even length. Odd lengths are impossible by restoration. Once
all five split representatives above are excluded by a sound complete census,
one obtains `f(7)>=22` without using PR2542's old length-18 computation.
Together with a verified universal length-24 word: `f(7) in {22,24}`.

A separate corrected length-18 `(9,9)` run remains useful for repairing
PR2542's specific numerical evidence. It is not an additional logical premise
of the new length-20 lower-bound proof. A length-20 witness, by contrast,
would establish only `f(7)<=20`; deciding whether 18 is possible would still
matter for the exact minimum.

## 7. Scope of the historical evidence and later work

[PR2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542) correctly
uses weight/time parity and the pair identity to reduce length 18 to simple
`(9,9)` cycles. Its decisive invocation
`cyclic_census(7,18,budget=9,simple=True)` uses bit-0 grouping and needs a
corrected receipt. The counting bound, identity, restoration parity, and
verified Gray constructions are not refuted by this implementation error.
The separate original overstatement about all 17-point sets is addressed by
the later set-level work below.

[PR2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634) vendors
the same engine and replays that length-18 computation. Its partial
length-20 simple-cycle census also applies the fixed bit-0 budget. Its
explicit cover witnesses, template lemmas, and labelled heuristic search
failures have different evidence and are not revoked by this finding.

[PR2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691) reproduces
the wrong-budget traversal in C and completes its 15 shards. The old
`6,305,209,079` nodes / `597,148,314` surviving leaves / zero hits remain
historical outputs of that filter. They do not exhaust the mathematically
claimed `(10,10)` candidate class. Its full-exclusion and sound-prune claims
need the corrected census.

The following merged successors were checked by PR metadata/body at their
recorded heads (see `math/SOURCES.json`):

| PR | Relevant scope | Effect on this correction |
|---|---|---|
| [2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773) | Set-level collision profiles and Sidon census exclude `(10,7)` and its mirror | Independent reason to remove that 17-point word split; no repair of old word traversal |
| [2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870) | Fourier/Parseval excludes `(11,6)` and its mirror, completing the 17-point set-level claim with earlier work | The new Fourier contradiction is separate from repeated old word receipts |
| [2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911) | 18-point set-level necessary conditions and remainder rows | No whole 18-point split excluded |
| [2933](https://github.com/CrocSwap/integer-mult-bounds/pull/2933) | Classifies vanishing-character cases for 18-point sets | No whole 18-point split excluded |
| [2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961) | Excludes three set-level classes, strengthens odd-odd multiplicity conditions | No whole 18-point split excluded; no corrected word census |

These later packages cite or replay the old word census as predecessor state;
that replay does not restore its proof. Their independent set-level lemmas
must be assessed on their own hypotheses. Excluding one set cardinality or
split does not exclude longer words with other admissible prefix sets.

## 8. Implementation proof obligations and affected material

For the corrected census: partition the states by Hamming-weight parity (or
equivalently time parity after proving consistency); maintain **distinct**
prefix sets; increment and undo counters only on first visits; use each
target split's even and odd budgets; check exact restored status, split and
coverage at leaves; enumerate all restricted-growth words or a proven
partition of them; distinguish capped/aborted runs from complete runs; retain
the parity-swap argument if only `s>=t` is run. Self-avoidance is permitted
only when the target split forces `|P|=L`.

Material needing a correction or explicit historical annotation:

- PR2691 package `research/universal-f7-singleton-l20-census-complete-seedfd938f30/`:
  `f7_census.c`, `README.md`, `AUDIT-RESULT.json`, and the old-count expectations
  and pass-message semantics in `verify.py`; associated PR description.
- PR2542 package `research/universal-f7-singleton-seedb859517b/`:
  `engine.py::cyclic_census` and the census-dependent statements/receipts in
  `README.md`, `CERTIFICATE.json`, `CERTIFICATE-PROGRESS.json`, `EXPECTED.json`,
  `verify.py`, `search.py`, and related tests and manifests if that package is
  revised. Preserve frozen predecessor copies and describe the correction
  separately rather than silently changing a pinned source.
- PR2634 package `research/universal-f7-singleton-l20-seed06704c39/`:
  the vendored `engine.py`, `census20.py`, `CENSUS20-PROGRESS.json`,
  `verify.py`, `EXPECTED.json`, and dependent census claims. Its hash pins
  should continue to identify the old bytes if retained as frozen evidence.
- Session-2 `agent-c/BUDGETS.md`: remove the false strengthening conclusion;
  `check_budgets.py` has a stale absolute import through the former playground
  folder. The new independent script below avoids that path and dependency.
- Session-2 `agent-a/f7_census_revisit.c` defaults to bit-0 budgets; a user
  running the default can reproduce the faulty mode. The corrected public
  entry point should select only the proved mode and clearly label any
  historical-replay option.

## Reproduction of the mathematical checks

`python3 math/check_math.py` uses only the standard library and imports no census
engine. It checks all restored words at `(n,L)=(3,6),(3,8),(4,8)`, both
budgets, the exact pair identity, every nonzero linear functional's valid
actual-size budget, rotation symmetry, both length-18/20 split lists, the
simple balanced counterexample, and the false-tightness countercheck.
Observed universal counts: 60, 1092, 624; canonical counts: 10, 182, 26.
The exact output is retained in `math/math-check-output.txt`.

Open next question after a verified zero-hit length-20 census: decide length
22 versus the known length-24 construction. This note makes no length-22
exclusion or multiplication-frontier claim.
