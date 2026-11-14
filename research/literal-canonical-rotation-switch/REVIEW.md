# Independent review of the literal direct switch predicate

**Verdict:** the stated point-predicate theorem passes independent mathematical,
instruction, source, and execution review on its declared physical ABI. No
counterexample or unresolved correctness defect was found. This review does
not admit a surrounding caller or establish a multiplication bound.

Prepared for @CubeJerry by a separate OpenAI-assisted review worker. The
implementation and its primary interpreter/oracle were not used to implement
the independent machine semantics or expected-bit algorithm below. Nick
Petalas's arithmetic formulas and child closure remain credited to
[CrocSwap/integer-mult-bounds#7504](https://github.com/CrocSwap/integer-mult-bounds/pull/7504);
Cinna Davis's canonical Beneš construction remains credited to
[CrocSwap/integer-mult-bounds#4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100).

## Exact reviewed objects

- Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
- Arithmetic predecessor head: `4eece58f5cebdb70a92d65447974f1c02383f60b`.
- `switch.py` SHA256:
  `89fe721a2920943dbc58eefe7f855ac1573e653e8af3b029c9c2ef838fdeac40`.
- The 2096-location, 14-tape graph SHA256, under compact sorted JSON:
  `320daab199a5528d1e7c273c719b6787c01629ff6160cb01fb9c959e87c7b1d8`.
- Reviewed `PROOF.md` SHA256:
  `1bd3150bdb075ba259dc9b7932800c8897e9b14d2198e8d001a7b212bad5f7b0`.
- Reviewed `PLAN.md` SHA256:
  `46b4655fa56b90f95aa9c09438641334f2a41987d5c77f7cce064fe2cc27b170`.

All six source-pin bytes were independently compared. The three canonical
objects were read by `git show` at the exact canonical commit, and the three
foreign predecessor objects were separately fetched from their exact GitHub
commit URLs. `SOURCE-CHECK.json` records paths, hashes, sizes and methods.
This is an exact-object check, not a claim that a shallow checkout proves
arbitrary history relationships.

## Universal reasoning checked

The height parser preserves the borrowed height, checks positive canonical
LSB notation and constructs exactly `W=h+1` width cells by a physical binary
countdown. The four other borrowed descriptors have exactly W bits. Initial
validation precedes the identity and height-one shortcuts. The initialization
of `2h-2` fits W bits: `2h <= 2^(h+1)` for every `h>=1`.

Every branch and arithmetic macro was traced in the emitted construction.
The low-to-high comparison correctly lets the highest unequal digit replace
its previous comparison state. Right shifts read a successor before writing
its predecessor; carry and borrow are single control bits. No arithmetic
operation requires a decoded runtime integer or random-access operation.
All emitted reads have five fixed-symbol targets, all moves are unit moves,
all writes are fixed symbols and no graph write addresses borrowed ports0..4.

The loop invariant is the stated smaller padded-rotation instance
`(eta,S,A,J,X)` with `R=2eta-2`. Its first and last row cases match the exact
predecessor formulas, including the first padded wire. Interior selection
reads the *current* low wire bit. It computes

```
S' = floor(S/2) + [S odd and (X mod2)=(A mod2)],
Apre = floor(A/2) + (X mod2)(A mod2),
```

and replaces equality `Apre=S'` by zero. The credited closure theorem gives
`Apre<=S'`; the preceding `A>0` test guarantees `S>=2`, hence `S'>=1`.
There is no implicit division by a zero child modulus. Updating J, R and X
reduces eta by one and preserves all domain inequalities. This proves at
most h loop entrances. It also establishes that x means a current wire
address, not an original input-token label.

All input/output heads are rewound. Each private word is erased through its
END, the head traverses the erased span, and the installed LEFT is erased
before return. The review checked both success and rejection continuations.
The latter does not promise recovery from missing/interior LEFT, aliased
owners, arbitrary bank corruption or an unterminated stream. Those exclusions
are part of the stated physical ABI, not hidden assumptions in the theorem.

## Independently counted complete bill

Direct counting of the literal macro bodies reproduces the bounds below;
these are not fitted to execution times. A rewind starting at relative k
uses exactly `3k+3` instructions. The following W-bit bounds include returns
and their stated branch dispatches.

| Macro | Bound |
| --- | ---: |
| Rewind from position at most W+1 | `3W+6` |
| Zero test with destination jump | `6W+5` |
| Increment or decrement | `7W+5` |
| Zero word | `7W+4` |
| Copy word and return both heads | `11W+7` |
| Right shift | `9W+2` |
| Left shift | `7W+5` |
| Comparison and branch | `11W+10` |

For ell=`bit_length(h)`, the setup decomposes into guard/output checks,
height copy, width countdown, six numeric initializations, four field copies,
last-row construction, temporary high-bit construction and validation. Its
sum is at most `h(13ell+13)+28ell+180W+189`, hence the claimed
`h(13W+13)+208W+189`. The longest interior route is bounded by `109W+77`;
`128(W+1)` safely covers every loop entrance, including its terminal output
write. Cleanup is bounded by `98W+179`. Therefore the full bill is at most

```
141h^2+588h+674 <= 1024(h+3)^2.
```

No input serialization, producer, consumer or transport outside entry/return
is silently included in this point-service statement. Those remain caller
obligations exactly as the package says.

The successful runs also admit the sharper exact span count
`11h+2ell+48`: height contributes `ell+2`, the four fixed fields contribute
`4(W+2)`, output contributes3, countdown contributes `ell+3`, and the width
plus six numeric owners contribute `7(W+3)`. This is below the claimed
`16(h+4)` increment. Historical backing remains charged after erasure.
Reusing the same origins takes the per-owner interval union; moving an
origin requires separately charged transport.

## Independent execution and failure detection

`independent_check.py` uses one sparse dictionary keyed by owner and logical
position. Every owner has a distinct negative origin, permanent/private
guards are distinguished, and opaque exterior sentinels are placed just
outside the legal windows. Every physical move, including moves over erased
cells, updates historical extrema. Whole sparse state and all heads are
compared after return; all five borrowed ports must have zero writes.
The six permanent guards must remain untouched and the eight private guard
write sequences must be exactly `[LEFT,blank]`.

The expected-bit oracle independently solves the canonical input/output-pair
color constraints with parity union-find. It orients each component by its
least wire, derives child permutations and recurses. This differs from the
source compiler's traversal and from the direct-query arithmetic evaluator.
The oracle checks each row is constant across its switched pair and routes
every wire through the entire resulting network to its specified endpoint.
Canonical color uniqueness after fixing each component's least wire explains
why this constructs the required canonical orientation.

Executed coverage:

- All1566 queries of all49 networks through height3.
- All544 queries with `h=5,s=17,j=6`, ranging over every offset and wire.
  The independently computed byte-bit hash is
  `bc0ab563e6d8fdfa24ee89b50dbe3f9a3a6f23681f491e883c6b5aeef07d4104`.
- Half-turns at heights13,37,97 reach exactly h loop entrances. Their
  expected one-bit middle-row answer follows by recursive halving of a
  dyadic half turn, without building an exponential reference network.
- Twelve binary/domain/END faults reject with the full stated cleanup.
- One emitted-table child-parity mutation swaps the 0/1 destinations at
  locations1242,1325,1419,1512. At `(h,s,a,j,x)=(3,5,1,1,5)` it returns0
  instead of the independently required1 while restoring all heads, guards
  and private storage. The test therefore detects a semantic error in a
  successfully returning program.
- Removing the height's permanent LEFT crosses the promised owner window.
  This explicitly records the failure boundary; no clean rejection is
  claimed for this outside-ABI input.

Normal-graph replay uses4,507,530 transitions and dynamically visits1930 of
the2096 locations. Every graph location passes static instruction checks;
the universal macro and induction review covers the claim beyond finite
execution. No assertion of complete dynamic branch coverage is made.

## Scope, next obligation and reproduction

This is an explicit missing physical point-query service under its supplied
ABI. All five foundational assumptions remain, and there is no new kappa.
The source-faithful next lemma is a priced adapter from an actual caller's
physical height/rotation/row/current-wire records into this W-bit ABI,
together with output use/retirement and the caller's actual repeated-query
sequence. It must include current-wire updates and transport; the standalone
predicate does not establish that a retained ROM loses on a whole workload.

Portable, read-only replay from a package containing the frozen `switch.py`:

```
python -B independent_check.py .
python -B -O independent_check.py .
```

The reviewer also ran the normal command against a separately saved emitted
graph and the optimized command against the authenticated constructor. Both
must print the same JSON as `INDEPENDENT-RESULT.json`; no artifact is written
implicitly. The graph fallback is only needed for the reviewer's separate
workspace. The published package can use its already pinned constructor.
