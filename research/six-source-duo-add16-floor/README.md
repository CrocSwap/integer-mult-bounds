# The six-source DUO batch optimum is 140 queries and 142 adds

In the inherited six-source dirty-connector model, Aaron Wang/Navinor's
[PR2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128) construction
simultaneously minimizes the all-63-output batch's **queries (140)** and
**source/readout adds (142)**. Thus `(140,142)` is its only Pareto point for
these two charges. A paired-universal source word needs at least **14 calls
at every source-add budget**; the predecessor attains `(14,16)`.

The unrestricted group-theoretic value is already reported by Volodymyr
Gavrylkiv, *Bases in Dihedral and Boolean Groups*, JIS 20 (2017),
[Table 3](https://cs.uwaterloo.ca/journals/JIS/VOL20/Gavrylkiv/gav4.pdf):
`r[(C2)^6]=14`. We credit that result. This contribution independently
rebuilds its finite lower bound, applies it to the connector's complete bill,
and supplies a separate exact 16-add word census. It does not introduce a
physical supplier or improve the selected kappa.

## Model and inherited reduction

Keep [Navinor's DUO model](../duo-toggle-connector/README.md), extending
Ross Richardson's [dirty connector](../universal-connector-boundary/README.md):
six read-only sources, arbitrary dirty targets, one arbitrary dirty connector
z, and complete F2-linear calls with fixed generic maps:

```
B_j:       z += B_j x_j
DUO_{j,l}: z += B_j x_j + B_l x_l       (j != l)
A_i:       y_i += A_i z.
```

No extra connectors, source mutations, combined readouts or reads inside a
DUO are allowed. Restore z and all scratch. A source word has k calls and W
source-map applications: a singleton contributes one to W, a DUO two. The
inherited price is one overhead o per call and one marginal p per add.

Write q_t for the source-parity prefix. Restoration forces q_k=q_0=0,
with every used source occurring a positive even number of times. Two
readouts give q_s XOR q_t. Paired universality is exactly
`D={q_s XOR q_t}=F2^6`. Necessity follows from independent scalar dirty
inputs; sufficiency holds for arbitrary A_i and B_j without commutativity.
This reduction and the attaining word are inherited, not new here.

## Unrestricted 13-point exclusion

For a restored k-call source word, the distinct prefixes form a set S of
size at most k: the last prefix repeats the first. Suppose a set of at most
13 points covers every difference. Enlarge it to exactly 13 distinct points,
translate one point to zero, and choose six independent translated points.
Such a basis exists because full difference coverage forces affine span 6.
An invertible linear map sends those six points to the coordinate basis.

The normalized set therefore contains `0,1,2,4,8,16,32`; its other six
points are any six of the remaining 57. Every possible cover has a
representative in these **C(57,6)=36,288,252** combinations. Multiple
representatives of one affine orbit are allowed. This is an existence
reduction, not an orbit count. The transformation is used only in the
impossibility proof; it does not change or subsidize the physical alphabet.

Two code-disjoint C++ implementations exhaust this complete domain:

- `basis13_recursive.cpp` chooses points recursively and incrementally adds
  literal pair differences.
- `basis13_bitset.cpp` enumerates six-bit selections in colexicographic order
  using Gosper's rule, rebuilds each point set, and computes its differences
  by XOR translations of a 64-bit incidence vector. All 4,096 singleton
  translation identities are checked first.

They agree on the entire coverage histogram, with maximum **63/64** and
4,200 attaining normalized sets. Neither has a full cover. Both check the
14-point positive fixture through their actual coverage computation and a
sharp 13-point near cover. Deadlines produce a rejected `TIMEOUT` receipt.
The native histogram is independently reconstructed, not accepted by hash.

`basis.py` checks the receipts, literal attaining witnesses, invertible
normalization and 256 affine-image controls, and rejects a proper-subspace
fixture. These finite controls support the written normalization argument;
they are not a formal proof of all possible changes of basis. Since every
hypothetical cover is represented in the exhaustive domain, **k>=14** for
paired universality, independently of W. This lower bound even allows
arbitrary source-step masks, while retaining a single connector and the
same paired-readout rule. The known DUO word shows sharpness.

## Complete batch lower bounds

The batch contains one separate dirty output for every nonzero six-source
mask. Each output needs at least two readouts to cancel the unknown initial
connector. If its mask is absent from D, it needs at least four. Write M for
the number of missing nonzero masks. Then readouts `R>=126+2M` and total
queries `Q=k+R`.

- If `k>=14`, then `Q>=140`.
- If `k=12` or `13`, the unrestricted exclusion gives `M>=1`, hence
  `Q>=140` or `141` respectively.
- If `k<=11`, at most `C(k,2)` nonzero differences are present. Thus
  `Q>=k+126+2(63-C(k,2))>=153` for `1<=k<=11`.

Therefore **Q>=140 even when more than two readouts are permitted**. The
bound at k=12 is only an optimistic lower bound; no such attaining word is
claimed. The predecessor attains Q=140 at k=14 and R=126.

Source restoration and dependence on all six inputs require positive even
W>=12. Expanding DUOs exposes more prefixes and preserves W. The retained
singleton census therefore gives the following add floors:

| Source adds W | Required output readouts | Total adds W+R |
|---|---:|---:|
| 12 | at least 156 (15 missing masks) | at least 168 |
| 14 | at least 136 (5 missing masks) | at least 150 |
| 16 | at least 126 | at least 142 |
| even W>=18 | at least 126 | at least 144 |

The old singleton maxima are 49/64 at W=12 and 59/64 at W=14, and are
fully replayed. Thus **W+R>=142**. Both minima are attained simultaneously
by PR2128's source word

```
2,16,8,16,1,4,48,4,3,4,32,8,4,16.
```

It has 14 calls, 16 adds, restoration and full coverage. Its complete bill
is `140o+142p`, optimal for every nonnegative o,p in this inherited tariff.
For strictly positive prices, a different query/add pair is more expensive.
This is a statement about a declared abstract interface, not practical
runtime, free physical composition, or a multiplication supplier invoice.

## Independent restricted 16-add census

The investigation first resolved the named `(k,W)=(13,16)` handoff. That
evidence is retained as an independent restricted cross-check, even though
the unrestricted basis result already excludes all k<=13 paired universals.

A `(13,16)` word contains ten singletons and three DUOs. Expanding each
DUO gives a restored 16-step singleton word. Positive even source
multiplicities have exactly the profiles `(6,2,2,2,2,2)` or
`(4,4,2,2,2,2)`. The original prefixes hide precisely the three internal
midpoints: pairwise nonadjacent cyclic vertices, each merging distinct
labels. Conversely every such deletion makes a legal `(13,16)` word.
Repeated prefixes are allowed. Expanded internal boundaries are only proof
bookkeeping; the actual DUO offers no readout there.

An expanded word must cover all differences if its visible subset does.
First-occurrence source relabeling leaves exactly

```
16! / (6! * (2!)^5 * 5!)                 =  7,567,560
16! / ((4!)^2 * (2!)^4 * 2! * 4!)       = 47,297,250
total                                   = 54,864,810.
```

`enumerate_rgs.cpp` uses restricted-growth words, parity feasibility and
incremental pair differences. `enumerate_partitions.cpp` independently
partitions positions into even blocks and uses bitset translations. They
agree byte-for-byte on **7,480 full-cover words**, all with the second
profile. [FULL-COVERS.bin](FULL-COVERS.bin) stores sorted little-endian
uint64 codes, sixteen 3-bit labels each, earliest in the least significant
bits: 59,840 bytes, SHA256

```
251100fa9f200ddb24cefac8a6b8255cfa43d1f3bd7e4bc3f45120d4f3aa7262
```

The literal Python audit partitions the table into 251 complete
rotation/reversal/relabeling orbits: sizes 8:1, 16:33, 32:217. These
symmetries preserve legal hidden midpoints and retained coverage. It checks
all 352 cyclic nonadjacent triples per representative, retaining the 86,900
cases that merge distinct labels. It does not use the primary native
individual-removability prune. The maximum is 63/64. Non-full expanded
words cannot gain coverage by deletion. No timeout is used as an exclusion.

The sharp near miss

```
2,1,4,1,2,9,20,8,32,8,16,8,33
```

misses only mask 12. Four readouts at boundaries 0,1,2,6 repair it, at a
dominated batch bill of 141 queries and 144 adds. Splitting DUOs also
excludes `(12,16)`; the inherited 14-step bound excludes `(12,14)` and
`(13,14)`. The unrestricted result additionally closes `(12,18)`,
`(13,18)` and every higher-add paired-universal k<=13 cell.

## Reproduce and limits

Full replay needs Python 3.12 and a C++17 compiler (g++ or clang++).
Tested: Ubuntu 24.04, CPython 3.12.3, g++ 13.3.0. Set CXX to its executable
if c++ is unavailable. No compiler or dependency is downloaded. Default
replay builds in temporary storage and leaves the source package unchanged:

```sh
python3 -I -O -B research/six-source-duo-add16-floor/verify.py
python3.12 scripts/research_package.py --package research/six-source-duo-add16-floor
```

Expected: `PASS_SIX_SOURCE_DUO_GLOBAL_OPTIMUM`. The complete receipt binds
four censuses, both histograms, the restricted word table, literal audits,
positive fixtures, mutations and exact batch floors. The first complete
four-census replay including compilation took 13.31 seconds and 120,300 KiB
peak RSS on one CPU. `--out NEW_PATH` creates a receipt exclusively.

The optimized portable audit runs on Windows without a compiler:

```sh
python3 -I -O -B research/six-source-duo-add16-floor/audit.py
```

It checks the saved **restricted** table, all orbits/deletions, the near
miss and full dirty-input positive replay. It does not re-establish either
native census's completeness or the unrestricted basis result. The full
native replay was not run on Windows. Positive replay covers all 70, 140
and 210 independent columns at dimensions 1,2,3, with noncommuting maps at
dimensions 2 and 3. Dropped/moved readouts, a shrunk DUO and a dropped
source call reject. Both native basis enumerations also pass full-domain
UBSan runs. Missing source/compiler, drifted inputs, changed table/results,
deadline truncation and output overwrite are rejected.

All implementations have the same author/assistant. Algorithmic agreement
is not independent human or formal-kernel review. No frame/owner admission,
physical compiler, chronological hosting, precision/tape proof, global
supplier moment, all-size theorem or outer exponent is supplied.

## Open next questions

The six-source abstract DUO query/add frontier is closed under the stated
rules. The relevant remaining question is physical admission: can one
pinned supplier implement a complete DUO call after all owner/frame, access,
restoration and precision costs? Start with one small arbitrary-input,
noncommuting fixture and a fully charged invoice. This package supplies no
such instance. Structured scope, source pins and handoff are in [TASK.json](TASK.json).

## Credit

Volodymyr Gavrylkiv / JIS 2017 Table 3: the known unrestricted 14-point
Boolean-group basis value. Ross Richardson / PR943 and PR934: interface
and prefix reduction. Navinor / PR1531: DUO model, five-source result and
prices. Aaron Wang/Navinor / PR2128 at
`697369a971eed02c0fbcd75ebefec9f59945f08e`: the attaining six-source word
and open-cell handoff. Douglas Colkitt / PR1185 and Hanson Sun / PR1215:
singleton result. PR2134/PR2146 retain credit for their distinct TRIO
censuses; their witnesses are not reproduced or attributed to this package.

Prepared for Tairitsu-Aya with substantial OpenAI Codex assistance in
mathematics, code, source reading, verification and prose. Apache-2.0.
Frozen predecessors and the selected result are unchanged. This continues
a released handoff, not a new operation family or a fresh random draw.
