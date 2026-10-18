# Mixed GL3 bit targets: the direct word is optimal for all 916 open pairs

**Scoped negative result; no new kappa.** This closes open question 1 of
[`bit-gl3-mixed-targets-seed18`](../bit-gl3-mixed-targets-seed18/README.md)
(Hanson Sun). In that package's two-register formal model, the 916 ordered
target pairs with direct cost 10 to 12 were known only to need at least nine
paid calls. Each of them needs exactly its direct cost:

| direct cost d(a)+d(b) | pairs | exact minimum | new evidence |
|---:|---:|---:|---|
| 10 | 816 | 10 | no word of length 9 |
| 11 | 96 | 11 | no word of length 9 or 10 |
| 12 | 4 | 12 | no word of length 9, 10 or 11 |

With seed18's table, **every one of the 28,224 ordered pairs diag([a],[b]) costs
exactly d(a)+d(b)**. Free GL_2(F2) scalar mixing never lets two different
coordinate-CNOT targets share paid work in this alphabet. The four cost-12
pairs are the ones whose entries are the two 3-cycle permutation matrices,
the only elements at coordinate-CNOT distance six.

## Model (unchanged from seed18)

Work in M_2(R), R = F2[GL_3(F2)]. A paid call is `I + N([g]+[e])`, with g one of
the six coordinate CNOTs `I + E_ij` and `N = u v^T` one of the six binary
rank-one idempotents (`v^T u = 1`). This gives 36 paid generators. Both
registers start dirty, and free scalar GL_2(F2) mixing is pushed through the
paid calls and removed by augmentation, exactly as in seed18. The target is
`diag([a],[b])`, with formal equality of every coefficient. The direct word
costs `d(a)+d(b)`, where d is the coordinate-CNOT word length in GL_3(F2)
(Cayley layers 1, 6, 24, 51, 60, 24, 2). The bill counts paid calls only,
which is seed18's deliberately optimistic relaxation.

## Coverage argument

Every generator is an involution, so a word of length at most 10 equals
`A B^-1` with A and B in the radius-5 ball. Seed18's row-orbit lemma applies
unchanged: `A B^-1 = diag([a],[b])` exactly when each row of A is the left
G-translate of the same row of B. Rows are reduced to a canonical
left-translation representative. The minimizing anchor is unique because an
invertible matrix's row has trivial stabilizer; a tie aborts the engine.
States with equal keys (the four canonical coefficients) are grouped, and
every ordered pair in a group gives a target `(x_A x_B^-1, y_A y_B^-1)` at
cost `d(A)+d(B)`.

`engine.cpp` builds the radius-4 ball by breadth-first search with exact state
deduplication. It then applies all 36 generators to every distance-4 state.
Images that are not in the radius-4 ball are exactly the distance-5 states,
possibly repeated, and they are deduplicated exactly by key and anchors. All
keys are compared in full; no digest decides equality. The join over all
16,292,362 states of the radius-5 ball examines 1,119,282,418 ordered pairs.
This covers every word of length at most 10.

Length 11 is needed only for the four cost-12 pairs. Such a word is
`(h C) B^-1` with C at distance exactly 5, h a generator and B in the radius-5
ball. If C is shorter, the word has length at most 10 and is already covered.
The engine streams all 562,639,176 images `h C`. It looks up their key among the
radius-5 groups and searches each group for the anchors this target requires.
Of the 1,169,568 anchor hits, none is for a cost-12 target. All of them are
for the 96 cost-11 control targets described below.

## Bounded probe: one extra dirty register (lengths at most 7)

`engine3.cpp` takes a first step on the next question. It adds one third
scalar register with arbitrary input. That register must be restored, or in a
second count may end at any monomial `[c]`. On three registers there are 28
binary rank-one idempotents, so there are 168 paid involutions, and free
GL_3(F2) mixing is normalized as before. The radius-3 ball has layers
1, 168, 21,882 and 2,683,740 (2,705,791 states). A ball-3 x ball-3 key join plus
450,868,320 streamed distance-4 images covers every word of length at most 7.
**No ordered pair (a,b) gets a word shorter than d(a)+d(b), restored or not.**
Every direct word of length at most 7 is found, which is the positive control.
So the extra dirty register gives no saving for the 24,224 pairs with direct
cost at most 8, and every pair with direct cost at least 9 still needs at least
8 calls. Lengths 8 to 12 with a third register are not covered: a stored
radius-4 layer would be hundreds of millions of 216-byte states.

## Evidence and controls

- **Reproduces seed18.** Radius-4 layers 1, 36, 996, 25,518, 636,945 (663,496
  states) and 133,207 cosets match seed18's pinned certificate. The radius-4
  join alone reproduces seed18's table `min(9, d(a)+d(b))` at all 28,224 pairs.
- **The join finds words when they exist.** For each of the 27,308 pairs with
  direct cost at most 9, the radius-5 join returns exactly the direct cost, so
  5+4 splits are found. For all 816 cost-10 pairs it returns 10, so 5+5 splits
  are found. Each returned length-10 word is checked in the full formal algebra.
- **The length-11 stage finds words when they exist.** The same stage runs on all
  96 cost-11 pairs as positive controls and finds a length-11 word for each one.
  The 96 words are checked formally.
- **Upper bounds.** The four direct twelve-call words are checked formally.
- **Tamper controls.** Dropping any one call of a witness, transposing one label,
  or swapping the claimed target all fail the formal check.
- **Determinism.** Engine runs with 4 and 10 threads give identical receipts
  and pair tables. The length-11 witness choice was made thread-independent
  before RESULT.json was recorded.

`verify.py` is standard-library Python. It rebuilds GL_3(F2) and the
distances, re-derives the 916 pairs from scratch, and checks every recorded
word (816 + 96 + 4) in its own formal-algebra implementation, written
separately from seed18's `algebra.py` and from `engine.cpp`. It also binds the
receipt to seed18's pinned certificate. The lower bounds themselves rest on
the C++ engine run (`--full`). Quick mode checks only the engine's recorded
output.

## Reproduce

```sh
python3 -I -B research/bit-gl3-mixed-targets-length10/verify.py          # quick, < 1 s
python3 -I -B research/bit-gl3-mixed-targets-length10/verify.py --full   # compiles engine.cpp
python3 -I -B research/bit-gl3-mixed-targets-length10/verify.py --three  # third-register probe, ~35 s, 2.3 GB
python3 scripts/research_package.py --package research/bit-gl3-mixed-targets-length10 --check-only
```

Full mode needs a C++17 compiler and about 3 GB of RAM. It took 65 s on
10 cores and 116 s with 4 threads (Apple clang, macOS, 2026-10-14). The engine's
complete parsed output must equal `RESULT.json`. Expected:
`PASS_GL3_MIXED_TARGETS_LENGTH10 mode=full open_pairs=916 exact=916 ...`.

## Limits

This is a finite certificate for exactly two scalar registers, this 36-call
alphabet and these targets. Apart from the length-at-most-7 probe above, it
covers no extra or dirty auxiliary registers,
other address labels, physical source/compiler/hosting/precision admission, or
transfer to the rational-frame bit supplier. No kappa or selected-record change
is claimed. The lower bounds are computer searches by one engine each. Seed18's
independent replay corroborates only its radius-4 part, and no second
implementation of the radius-5 join exists yet. No dedicated CI workflow is
added; the registered quick command does not compile C++.

## Open next questions

1. **Does one dirty third register save anything at length 8 or more?** The
   probe above excludes savings through length 7, which settles all pairs with
   direct cost at most 8. Length 8 needs a 4+4 join. The first step is to store
   only 64-bit key digests and anchors of the distance-4 layer as a candidate
   filter and recheck any match exactly. Memory is the blocker: the layer is
   hundreds of millions of states.
2. **Is there a written invariant that proves `min = d(a)+d(b)` for all pairs?**
   This would replace the search and might extend to GL_n(F2). A first step is
   to test whether some quotient of R separates the two rows' label counts.
   Seed18's natural representation has aliases, so it does not work, and none is
   known.
3. **A second, independent implementation of the radius-5 join**, for example a
   faithful-regular-representation join, would make the lower bound
   independently replicated. The blocker is memory: 16.3 million states.

## Credit

Model, row-orbit coverage lemma, radius-4 table and question: Hanson Sun's
[`bit-gl3-mixed-targets-seed18`](../bit-gl3-mixed-targets-seed18/README.md),
with its retained lineage (eumemic PR288, Ali Romman PR468, Gareth Davidson
PR1333). PR1804 (1337isnot1337) treats one cost-6 pair, which is already
inside seed18's table. Prepared for Josie Elliston (session 32 of a donated
overnight run) with substantial AI assistance from Claude (Anthropic) via Claude
Code. Apache-2.0. No independent human review is claimed.
