# Six-source universal dirty-connector boundary

**Recursive-interface finite result: exact six-source value and Θ(2^{n/2}) bounds; no new kappa.**

This extends the merged five-source result,
[PR943](references/PR943-README.md) by Ross Richardson, one step further. In that
query model, call a restored source word `w` *universal* if paired output
readouts on it can realize every binary row mask, i.e. `D(w) = F2^n`. Let `f(n)`
be the minimum length of a universal word. PR943 shows `f(n) = 2n` for `n <= 4`
and `f(5) = 12`. This package adds:

1. **`f(6) = 16`.** Two independently implemented exhaustive censuses cover
   every six-source word of length 12 (10,395 canonical words) and length 14
   (945,945). Their maximum coverage is **49/64** and **59/64** respectively.
   An explicit 16-call word covers all 64.
2. **The all-63-row six-source batch has exact optimum 142 queries.** This is
   `2(6+63)+4`. The support bound is 138, so the surcharge is 4 (the five-source
   surcharge in PR943 is 2).
3. **For every n,** `2^{(n+1)/2} <= f(n) <= 2^{ceil(n/2)} + 2^{floor(n/2)}`.
   So the support value `2n` fails for every `n >= 5`, and any universal paired
   path grows exponentially in the number of sources. For `n = 7` the counting
   bound sharpens to `18 <= f(7) <= 24`. A heuristic search found nothing better
   than 126/128 at length 22. That is a search failure, not an exclusion.

```sh
python3 -I -B research/universal-connector-six-source/verify.py
```

Expected output, after about 35 s with Python 3.10+ and the standard library:
`PASS_SIX_SOURCE_CONNECTOR f(6)=16 max14=59/64 max12=49/64 batch63=142 f(7) in [18,24]`.
The script rebuilds every number and compares the result byte-for-byte with
[EXPECTED.json](EXPECTED.json). Use `--write-expected` to regenerate that file.

## Model

The model is PR943's, unchanged: dirty `F2` arrays `x_j`, `y_i`, `z`; complete
calls `B_j: z += B_j x_j` and `A_i: y_i += A_i z` only; a straight-line query
word that may depend on `M` but not on the data; no copies, extra connectors,
frame changes or combined queries. Write `q_t` for the parity vector of the
source labels in the first `t` B calls. PR943 proves three facts used here:

* every `B_j` count is even and `>= 2`, which restores `z`;
* every active `A_i` count is even and `>= 2`, which cancels the connector dirt;
* an output read at boundaries `t_1..t_{2k}` receives the row `q_{t_1} xor ... xor q_{t_{2k}}`.

Paired readouts therefore realize exactly
`D(w) = {q_s xor q_t}`. A restored word that uses every label is a closed walk
on the hypercube starting at 0.

## Exact six-source exclusion

A length-12 word on six labels uses each label twice. A length-14 word uses one
label four times and the others twice; no other even multiplicity pattern sums
to 14. Renaming labels by first occurrence permutes coordinates and preserves
`|D(w)|`. The two censuses are implemented differently:

* **Census A** emits restricted-growth words directly, pruning on parity
  feasibility, and computes `D(w)` as the set of pairwise prefix XORs.
* **Census B** enumerates perfect matchings of the positions, pairing the least
  unmatched position first. For length 14 it merges each of the 21 pairs of
  pairs into the four-occurrence label, then canonicalizes and deduplicates.
  It computes coverage by the dual test: `m` is covered iff some prefix `p`
  has `p xor m` among the prefixes.

The two censuses agree on the word count, the complete histogram and the SHA256
of the sorted `(word, |D|)` records. As a positive control, both reproduce
PR943's five-source histogram exactly (945 words, maximum 31).

| Length | Canonical words | Max `|D(w)|` | Words at max |
|---:|---:|---:|---:|
| 12 | 10,395 | 49 / 64 | 186 |
| 14 | 945,945 | 59 / 64 | 154 |

Length 16 attains 64 with the complementary-subspace word below. Hence
`f(6) = 16`.

## Construction for every n

Take the reflected Gray cycle on coordinates `0..k-1`, then the Gray cycle on
coordinates `k..n-1`, with `k = ceil(n/2)`. The prefixes contain both coordinate
subspaces `F2^k x 0` and `0 x F2^(n-k)`, so `D(w)` contains their sum, which is
all of `F2^n`. The length is `2^k + 2^(n-k)`, and every label count is even.
For `n = 6` this gives

    B0 B1 B0 B2 B0 B1 B0 B2 B3 B4 B3 B5 B3 B4 B3 B5

which is PR943's four-source idea with two three-bit Gray cycles instead of two
two-bit cycles. The verifier checks this construction for `n = 1..8`. It is optimal for every
`n <= 6`: its lengths 2, 4, 6, 8, 12 and 16 equal the known values of `f(n)`.
Universal six-source words need not be of this form. For example, the
non-subspace word `3 4 5 0 3 2 3 4 5 4 1 2 3 0 4 1` also covers all 64 masks;
`explore_n7.py` found it.

## Lower bound for every n

Let `L = |w|`. The boundary `q_t` has Hamming-weight parity `t mod 2`, and
`q_L = q_0`. So at most `L/2` distinct even-weight values `E` and `L/2` odd-weight
values `O` occur. An odd-weight mask is only reachable as `e xor o`, so
`|E| |O| >= 2^{n-1}`, which forces `L >= 2^{(n+1)/2}`. Even nonzero masks also
need `C(|E|,2) + C(|O|,2) >= 2^{n-1} - 1`. The verifier finds the least even `L`
satisfying both conditions. That value is 18 for `n = 7`: at `L = 16`, equality
`|E| = |O| = 8` leaves only 56 even nonzero differences, and 63 are needed.
For `n = 6` the bound gives only 12; the census closes the gap to 16.

## The all-63-row batch

The batch has six sources and one output for each of the 63 nonzero
masks. Rows with distinct masks need distinct `A_i`. Each needs at least two
readouts, and at least four when its mask is not in `D(w)`. The total is
`|w| + sum_i a_i`, so the census maxima give these floors:

| `|w|` | Uncovered nonzero masks | Query floor |
|---:|---:|---:|
| 12 | 15 | 12 + 126 + 30 = 168 |
| 14 | 5 | 14 + 126 + 10 = 150 |
| >= 16 | 0 | 142 |

`|w| < 12` cannot use every label. The 16-call universal word with one readout
pair per row attains 142. The verifier builds this complete 142-query program
and replays it on dense random `F2` maps of dimension 1, 2 and 3, with 40
arbitrary dirty states per dimension. It checks the exact target update and the
restoration of `z`, and also replays the reversed program. Four mutations are
rejected: an omitted final source call, a moved readout, a dropped readout and
a wrong output destination. The general linear identity remains PR943's prefix
argument; the replay is finite evidence.

Unlike five sources, adding extra readouts to a shorter word does not tie with
the longer path: at six sources the longer path is strictly cheaper (142
against 150 and 168). This optimum is for unit-cost queries. With unequal
complete prices, PR943's priced recurrence and its relabeling freedom apply
unchanged; this package states no weighted optimum.

## Scope and remaining obligations

This is a finite exclusion plus an explicit construction inside PR943's
abstract interface. It does not instantiate that interface inside the selected
supplier and claims no new kappa. Common-label/mutable-source realization,
frames, owner admission, full-row charging, compiler/tape integration, precision
and the outer analytic assumptions remain as PR943 lists them. Other
alphabets, such as extra connectors, copies or combined queries, are out of
scope, and so are specialized operators and restricted inputs. The exact value
of `f(7)` is open: neither 18, 20 nor 22 is excluded, and 24 is attained.

See [CLAIM.md](CLAIM.md) for the task card and [NOTICE.md](NOTICE.md) for
attribution. [SOURCES.json](SOURCES.json) pins the base commit, the selected
record hash and the retained predecessor files.
