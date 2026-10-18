# Signed Hadamard batching with one dirty connector

**Recursive-interface research construction; no new kappa.** This supplies a
literal 22-query word for four sources and four outputs with Sylvester Hadamard
coefficients, replacing 40 queries for either separate-star orientation. It
retains a shared dirty connector between readouts and restores all sources,
the connector and every recursive child's scratch exactly.

For factor lengths `|B|=[1,2,3,4]`, `|A|=[2,3,4,5]`, complete balanced child
lowering uses **238 primitive calls**, versus **364** for output stars and
**526** for source stars. All three use **four borrowed dirty arrays** in
addition to the eight source/output arrays. Every child and inverse operates
on the full length-L row and is counted. No clean row is assumed.

| Exact quantity | Candidate | Output stars | Source stars |
|---|---:|---:|---:|
| Complete queries | 22 | 40 | 40 |
| B query counts | 2,2,2,2 | 8,8,8,8 | 2,2,2,2 |
| A query counts | 4,4,4,2 | 2,2,2,2 | 8,8,8,8 |
| Complete primitive calls | 238 | 364 | 526 |
| Borrowed dirty rows | 4 | 4 | 4 |
| L=2 literal tape travel, word slots | 130,596 | 152,288 | 329,732 |
| L=2 observed signed word bits | 47 | 47 | 47 |

The tape counts are for the fully specified dense integer reference trace,
including returning home after every leaf; they are not timing measurements
or an implementation of the paper's native supplier. Work with nonuniform
operator prices is given explicitly below, without inferring a generic bit
complexity gain from the unit-price fixture.

## Reproduce

From the repository root, standard-library Python 3.11+ suffices:

```sh
python3 -I -B research/signed-hadamard-batch-seed55/verify.py --replay-search
python3 -I -B research/signed-hadamard-batch-seed55/test_package.py
```

Expected final markers:

```text
PASS_SIGNED_HADAMARD_BATCH queries=22_vs_40 leaf_calls=238_vs_364_vs_526 dirty_arrays=4 controls=8 no_new_kappa
PASS_SIGNED_HADAMARD_PACKAGE standalone_optimized_replay=PASS controls=8
```

The first command regenerates the completed search and compares every
construction field, checks the signed query identity, emits balanced recursive
products, replays all twelve arbitrary dirty input columns as free
noncommutative polynomials, checks literal inverses, and executes dense integer
fixtures of dimensions two and three. The receipt includes all leaf
multiplicities, primitive-word digests, coefficient/source access, arithmetic,
storage, preflight checks, instruction bits and exact head travel.

Use `--output /absolute/new/directory` to retain all three literal primitive
programs. Existing destinations are refused. The standalone test uses an
optimized Python process and a path with spaces, and rejects eight source,
construction, invoice, receipt and output-preservation faults. The verifier
has eight further obligation-specific controls. It imports neither the
constructor nor a predecessor implementation.

## Contract and literal construction

There are distinct arbitrary dirty rows `x_0,...,x_3`, `y_0,...,y_3` and `z`.
A_i and B_j are exact additive linear maps and need not commute or be
invertible. A complete restored query is either

```text
B_j^s: z += s B_j x_j
A_i^s: y_i += s A_i z,        s = -1 or +1.
```

It preserves its source, other data, private scratch and prescribed head
positions. The sources and operator coefficients are fixed, and intermediate
outputs are exclusively owned. The demanded endpoint is

```text
y_i += sum_j H_ij A_i B_j x_j,
H = [[1,1,1,1],[1,-1,1,-1],[1,1,-1,-1],[1,-1,-1,1]].
```

`CONSTRUCTION.json` contains the literal word and every readout pair. Its B
path is

```text
B0- B1+ B3- B2+ B3+ B0+ B2- B1-.
```

Each B_j is applied and unapplied once. Outputs 0,1,2 each take four signed
readouts, and output 3 takes two. For each output the readout signs sum to
zero, cancelling its contribution from arbitrary initial z, while their
signed connector coefficients equal the corresponding Hadamard row. This
proves the full identity at every row length with noncommuting operators;
the program also restores z. [PROOF.md](PROOF.md) details the identity and
child lowering. No optimum is claimed.

## Complete cost and storage recurrence

Let C(F;L,w) price a restored additive child for the ordered factor list F,
using the maximum price of its two signs. Leaf prices include coefficients,
source access, target update, routing, head returns and arithmetic. The
inherited binary dirty commutator gives

```text
C([f]) = c_f + d_leaf,
C(F) = 2 C(F_first) + 2 C(F_second) + d_node(F).
```

Both halves execute on full length-L rows. The node borrows a distinct dirty
row; its four complete child calls restore that row. Negative children are
literal inverses, with the same call multiplicities. In the unit-price fixture,
L(1)=1 and L(n)=2L(floor(n/2))+2L(ceil(n/2)).

Write B=sum_j C(B_j), and let R price the additional batch coefficient/sign
preparation, dispatch, program storage, source/port bindings, any required
frame adapters, parking and tape returns not already in child prices. Then

```text
C_candidate = 2 B + 4(C(A0)+C(A1)+C(A2)) + 2 C(A3) + R_candidate,
C_source_stars = 2 B + 8 sum_i C(A_i) + R_source_stars,
C_output_stars = 8 B + 2 sum_i C(A_i) + R_output_stars.
```

Against source stars the child saving is
`4(C(A0)+C(A1)+C(A2))+6C(A3)`; against output stars it is
`6B-2(C(A0)+C(A1)+C(A2))`. R differences must still be paid. Thus the
candidate need not beat output stars under every positive price assignment.
At the stated unit-leaf lengths the child saving against the better star
comparator is exactly **126**, with the full counts 238/364/526.
The receipt also checks a positive-price counterexample:
`C(B_j)=1`, `C(A_0)=C(A_1)=C(A_2)=1000`, `C(A_3)=1` gives candidate
cost 12,010 and output-star cost 6,034, before additional R. This prevents
interpreting the fixture's benefit as universal domination of both comparators.

Child scratch is reused only after return, and the eight data rows and z are
excluded from it. The peak is
`1+max(max_i ceil(log2 |A_i|), max_j ceil(log2 |B_j|))` borrowed dirty rows, here four.
Read-only coefficient storage, the emitted program, descriptors and loop state
are additional. The dense reference uses 12L dirty data words and 24L²
coefficient words, one scalar dot-product accumulator, and paid index/control
state. Every matrix row, coefficient/data alias and pair of data roles is
checked before the trace. The certificate prices each leaf instruction with
both role IDs, factor ID and sign. At word size w the literal travel costs
travel*w bit movement, plus listed loads/stores, multiplications, additions,
negations and pointer/control work. This is a reference invoice, not an
all-size precision or fixed-tape implementation theorem.

## Search, provenance and limits

OS seed **55**, exact base **`bbc600db2fc15007b7c914f4f2b2ed55fa909c87`**.
The selected certificate there is PR942's conditional
`1661960547713947/10^18`; it is unchanged. Three alternatives and the local
claim are in `CLAIM.json`. No pinned coordination issue existed.

The final domain is exactly 4,000 shuffled eight-step signed source paths,
one positive and one negative query per B_j. Each output is expressed by
one or two signed differences of visited states. All trials complete:
3,814 distinct paths, 491 admitted trials, with 237 22-query and 254 24-query
nominees. Select minimum complete unit-leaf cost, then query count and
lexicographic word. No rescan or additional seeds are used. This is not an
exhaustion of the full query alphabet or an optimality theorem.

The earlier 16,000 ten-source-step and 20,000 twelve-source-step screenings
found no path supplying all four rows with two readouts each. These are failed
bounded searches, not exclusions. The single mechanism revision allows more
output readouts while retaining the minimum source-call profile; the completed
construction is the positive result packaged here.

The signed query contract and product lowering build on @CubeJerry's PR889
and Ross Richardson's PR934/944. PR943 covers binary four-source batching;
this signed Hadamard object differs. Source heads and retained notices are
in `SOURCES.json` and `vendor/`. PR982's new output-borrowed fanout changes
the common-factor scratch contract; it is distinct from this multi-source
signed batch with a dedicated connector. Full open-PR scans and targeted
all-state searches were refreshed repeatedly through that arrival.

This is a completed exact recursive-interface construction, not a selected
supplier. No physical owner/frame compiler, hosted invoice, assembly change,
new moment/kappa, measured speedup or multiplication theorem is supplied.
Finite dense traces do not discharge inherited tape, precision, rounding,
all-size compiler, mutable-source or analytic transfer assumptions.
Original sources, `upstream/` and the selected frontier remain untouched.
See `NOTICE.md` for attribution and substantial AI-assistance disclosure.
