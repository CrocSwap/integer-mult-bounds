# H2-sem pricing of the PR848 copy-path helper-sharing wraps

## Contract (imported, not re-derived)

Use the replacement scalar contract H2-sem of
`research/r439-semantic-d-contract-seed10/PROOF.md` (PR1194):

1. Every D gate is at the common zero frame and is source-free.
2. No target feeds a source or helper (retained H1 inside D).
3. The complete D operator is exactly `(x,y,h) -> (x, y + N h, h)` for a
   specified binary matrix N.

The old gate-local H2 requires every D gate to write a target. Helper
preparation/restoration writes therefore fail syntactic H2. Under H2-sem they
are legal when the boundary equation holds. Semantic N must equal the raw
helper-response K of A/scatter/B for the interleaved substitution theorem.

## Objects

Let W be the selected PR589 R439 word
(`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`). Its D section
has 18,085 helper reads and already satisfies syntactic H2/K.

PR848's wrap for an oriented helper pair `(a,b)` prepends `a ^= b`, rewrites
every D row that contains `a` by symmetric difference with `b`, and appends the
reverse restoration `a ^= b`. The arithmetic source-read saving of one pair is

`sum_{rows containing a} (1_{b in row} - 1_{b not in row}) - 2`.

The seed-42 greedy disjoint matching of PR848 selects 205 positive pairs with
total arithmetic saving 6,231; the best single pair is `(277,434)` with saving
65. Both figures are recomputed here.

## Boundary lemma (dirty inputs)

Write H for the involution that XORs each selected center by its leaf. The wrap
is chronologically `H; D0; H` where D0 is the rewritten body. Because H = H^{-1}
over F2 and the body applies the conjugated coefficient matrix, the composite
equals the original D map on every F2 input column. Necessity of full helper
restoration is witnessed by deleting a restore gate: some helper basis column
fails to return. Equality of the 661 binary D columns therefore certifies the
H2-sem boundary for every F2-module stream under the common zero-frame reading
(the same coefficient argument as PR1194).

## Paid invoice

Only D changes. Register frame paths, COPY ranks and the climb histogram are
unchanged, so the paid recursive profile remains

`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`

with rank mass 5,129. Literal COPY/ERASE stream peaks give:

| word | ADDs | D ADDs | F | B | local bits | nine-stage bits |
|---|---:|---:|---:|---:|---:|---:|
| baseline W | 24,305 | 18,085 | 49,347 | 1,113,070 | 93 | 177 |
| single pair 277→434 | **24,240** | 18,020 | 50,535 | 1,113,070 | 94 | 177 |
| seed-42 matching (205) | **18,074** | 11,854 | 75,381 | 1,196,402 | 95 | 180 |

Both candidates stay strictly under the inherited 104-bit local and 192-bit
nine-stage guards. Forward/reverse complete-word F2 boundaries equal the
baseline. Inherited H1/H3/H4/H5 and U/J/C remain true; syntactic H2 and
`K_equals_D` are false exactly on the wraps, while semantic N equals the
baseline N (weight 18,085).

## What this does not claim

No new kappa: the bit supplier does not bind, and the paid profile is
unchanged. Native C++/Boost replay, hosted supplier emission, all-size
compiler, rounding/tape and analytic transfer are not executed. Matching
optimality is not claimed. PR1782's interface-admission package is complementary:
it established H2-sem legality without recomputing F/B or the paid profile;
this package supplies that invoice.
