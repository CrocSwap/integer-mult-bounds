# Eight-query path-lowered words: readouts 74 and source XORs 4 are attained together

**Scoped exact finite computation, in the PR1898 abstract tariff. No new κ.** In the
path-lowered even-subset class of
[PR2677](https://github.com/CrocSwap/integer-mult-bounds/pull/2677)
(`research/mutable-source-789q-invoice`), every eight-query word needs at least
74 readouts `R` and at least 4 source XORs `X`, and one closed walk attains both.
Both floors are known. The new fact is that they are attained together. The
eight-query row of PR2677's table was a lower bound (`R >= 74`, `X >= 0`, tariff
`>= 452`). It is now exact:

```text
min over eight-query words of  b*Q + a*R + x*X  =  8b + 74a + 4x   for all b, a, x > 0
tariff at (b, a, x) = (38, 2, 2):  38*8 + 2*74 + 2*4 = 460   (24 above the six-query endpoint 436)
```

Witness, a closed prefix walk with 74 readouts and 4 source XORs (replayed on
arbitrary dirty formal rows by the pinned model):

```text
(0, 1, 3, 2, 6, 14, 30, 20, 0)      also (0, 4, 20, 24, 9, 1, 3, 2, 0)
```

| Q | readout floor | XOR floor | attained together | tariff at (38,2,2) | vs 436 |
|--:|--:|--:|---|--:|--:|
| 6 | 96 | 8 | yes (PR1898 word) | **436** exact | 0 |
| 7 | 82 | 6 | yes (PR2677 champion) | **442** exact | +6 |
| 8 | 74 | 4 | **yes (this package)** | **460** exact | +24 |
| 9 | 62 | 2 | open; best found `R=70` at `X=2` | between 470 and 486 | at least +34 |
| >= 10 | 62 | 0 | not claimed | above 460 from `38Q` and `R >= 62` | |

The Q = 6 and Q = 7 rows are the existing values; the census and replays here
reproduce them. New here: the attaining Q = 8 word, which makes that row exact and
price-independent; the exact walk spectra; the attained Q = 9 value 486; and the
sharpness of the XOR floor at eight queries (below). The XOR floor itself is not
claimed: it is the connector consequence recorded in PR5935 (below).

## Model

The model, cost formulas and word builder are those of PR2677's `model.py`, which
the verifier imports as a pinned live input after a SHA256 check. A path-lowered
word is a closed connector walk `0 = w_0, w_1, ..., w_Q = 0` in `F2^5` with every
edge `w_i xor w_(i+1)` nonzero. Values and zero revisits may repeat. Then

- `X = sum over edges of 2*(weight(edge) - 1)`, the path-local compute and uncompute
  source XORs;
- `R` is the total even-subset readout count over the slot values: mask `m` costs
  the least even number of slots whose XOR is `m`;
- the tariff is `38Q + 2R + 2X`, the PR1898 fixture.

A walk covers when every nonzero mask is read, which forces its visited values to
span `F2^5`. Only covering walks are words.

## Source-XOR floor

For arbitrary restored source-XOR words, PR5935
(`research/connected-xor-word-floor`, this author's earlier package) proves
`X >= 2(n - c)` for an interaction graph with `c` components. With the component
inequality `Q >= n + c` of PR2455 this gives `X >= 2(2n - Q)`, so at five sources
`X >= 2(10 - Q)` for `Q <= 10`. PR5935 records this: `X >= 4` at `Q = 8` and
`X >= 2` at `Q = 9`. This package does not re-prove it.

For self-containment, here is a direct proof in the path-local cost model. A
covering closed walk with `Q` edges has `X >= 2*max(0, 10 - Q)`, `X = 2Q mod 4`, and
equality at the floor holds exactly when every coordinate lies in exactly two edges.

*Proof.* The visited values are partial sums of the edges, so the edges span
`F2^5` and every coordinate occurs in some edge. The edges sum to zero, so each
coordinate occurs in an even number of edges, at least two. The weight total is the
sum of these five counts: even and at least 10. Then
`X = 2*(total - Q) >= 2*(10 - Q)`, with equality iff the counts are `2,2,2,2,2`.
For `Q <= 5` no covering walk exists, since six edges are needed to span `F2^5`. ∎

**Sharpness.** Each X-floor layer below contains covering walks for `Q = 6..10`, so
the floor `2(10 - Q)` is attained there by a path-lowered word, which is a restored
word. At `Q = 8` this makes the XOR floor 4 sharp for arbitrary restored words, given
PR5935's lower bound. That is the sharp eight-query XOR floor asked for in Open next
question 2 of `research/seven-query-xor-floor`.

## Eight queries

1. **Readout floor, repeats allowed.** A walk with eight edges visits at most seven
   distinct nonzero values. The census over every set of five, six or seven values
   (3,535,767 sets, 3,097,024 covering) gives the spectra

   | distinct nonzero values | `R` values (number of sets) |
   |--:|---|
   | 5 | 96 (83,328) |
   | 6 | 82 (97,216), 88 (486,080) |
   | 7 | 74 (416,640), 80 (1,180,480), 84 (833,280) |

   So `R >= 74` for every eight-query word. Repeated prefix values or zero revisits
   leave at most six distinct values and force `R >= 82`. This answers Open next
   question 2 of PR2677 inside the class: the exact minimum is 74, attained only
   with seven distinct nonzero values. This is also the readout half of Open next
   question 2 of PR2686, repeats included. Its XOR half is the sharp floor 4 above.
2. **XOR floor.** `X >= 4`, from PR5935 for every restored word and from the parity proof above in this class.
3. **Attainment.** The exhaustive layer of closed eight-edge walks with every
   coordinate in exactly two edges has 730,800 walks, the count given by
   inclusion-exclusion. Of these, 30,240 cover with `R = 74` and `X = 4`. Its full
   spectrum is `74: 30,240`, `80: 172,800`, `82: 8,640`, `84: 161,280`,
   `88: 248,640`, `96: 84,000` and 25,200 non-covering walks.

Both floors hold for every word and one walk attains both. The Pareto frontier at
`Q = 8` is the single point `(R, X) = (74, 4)`, so the optimum does not depend on
the prices. The same argument gives single-point frontiers `(96, 8)` at `Q = 6`
and `(82, 6)` at `Q = 7`.

## Price crossovers among Q = 6, 7, 8

With the three exact rows `f6 = 6b + 96a + 8x`, `f7 = 7b + 82a + 6x` and
`f8 = 8b + 74a + 4x`:

```text
f8 < f7  iff  b < 8a + 2x          f7 < f6  iff  b < 14a + 2x          f8 < f6  iff  b < 11a + 2x
```

At `(38, 2, 2)` all three fail, so the six-query endpoint stays optimal among
`Q <= 8`. The verifier checks the equivalences on a grid of prices.

## Nine and ten queries

At `Q = 9` the XOR floor is 2 and the readout floor is at least 62. The X-floor
layer has 453,600 walks and its least readout count is 70, so tariff 486 is
attained. The exact minimum lies between 470 and 486. The next layer (weight total
12, `X = 6`) is not enumerated.

At `Q = 10` the `X = 0` layer has 113,400 walks and least `R = 64`, with no
`R = 62` walk. That reproduces the read-only ten-query repair with 64 readouts and
no source XOR recorded in `research/mutable-source-connector`, and it agrees with
the four-XOR requirement of `research/mutable-source-shear-cost` for 62 readouts.
No Q = 10 claim is made.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/eight-query-path-lowered-tariff/verify.py
python3.12 -B scripts/research_package.py --package research/eight-query-path-lowered-tariff
```

Expected marker:

```text
PASS_EIGHT_QUERY_PATH_LOWERED_TARIFF Q8=(R74,X4) tariff=460 floors_attained_Q6_Q7_Q8 Q9_in_470_486 no_new_kappa
```

The verifier takes about a minute. It checks:

- the readout census above and its set counts;
- the path-local XOR floor exhaustively on 638,832 covering walks in `F2^2`, `F2^3` and
  `F2^4`, including attainment of the floor at every `Q` from `n + 1` to `2n`;
- every X-floor layer at `Q = 6..10`, with walk counts equal to the closed-form
  count `sum_i (-1)^i C(Q,i) C(Q-i,2)^5` and the spectra quoted here;
- literal dirty-row replays with the pinned model of the two `Q = 8` witnesses,
  the `Q = 7` champion `(0,1,2,6,12,24,16,0)`, the six-query word, the `Q = 9`
  witness `(0,1,3,2,6,14,10,26,16,0)` and the ten-query paths;
- the three crossover equivalences on prices `b` in 1..39 and `a`, `x` in 1..7;
- 6,000 seeded random walks, repeats and zero revisits included, comparing the
  set-based readout and edge-cost formulas with the pinned model.

[SOURCES.json](SOURCES.json) pins the model. The exhaustive search that found the
witnesses was a separate, unpackaged program. Every number above is recomputed by
`verify.py` itself.

## Scope and limits

- The exact row is for path-lowered even-subset words: one closed connector walk,
  path-local compute and uncompute source XORs, and PR2677's tariff. The readout and
  walk-spectrum claims are not checked for arbitrary XOR-interleaved restored words.
  Only the XOR floor, and its sharpness at eight queries, is stated for those, and
  its lower bound is PR5935's, not re-proved here.
- The tariff is the abstract complete-call fixture. No physical supplier, hosting,
  precision or kappa claim is made. Independent human and formal proof-kernel review
  are unclaimed.
- Nine queries are not settled. Ten queries are cross-checked only.

## Open next questions

1. What is the exact tariff at nine queries (between 470 and 486)? Enumerate the
   `X = 6` layer at `Q = 9` and compare its least readout count with 70. The layer is
   larger than the ones here. No obstruction is known.
2. Does the readout floor 74 hold for arbitrary XOR-interleaved restored words at
   eight queries, with non-path source XORs? The census uses only the set of
   connector values, so the first step is to check that a restored word's connector
   values obey the same even-subset readout constraint.

## Credit

This contribution was produced by Nick Petalas. It builds on Wentao Li's PR2677
(`research/mutable-source-789q-invoice`: model, invoice table and the open
question), PR2686 (`research/seven-query-r-floor`) and PR2643
(`research/seven-query-xor-floor`); on Arham Tahir's PR1898 (the alphabet and the
six-query word); and on PR1370 and Ross Richardson's PR943 for the ten-query
cross-check. The XOR floor `2(10 - Q)` is the connector consequence of PR5935
(Nick Petalas) with ywz65's PR2455 component inequality; PR2455 also proves the
six-query XOR bound. Predecessor files and notices are unchanged. Apache-2.0.
