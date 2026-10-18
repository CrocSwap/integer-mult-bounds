# An exact internal grid for the whole physical P104 word

All 5,398 events of the unchanged PR2586 physical inverse-transpose admit
one sufficient fixed grid, including every internal native butterfly and
all eight strict-zero private erasures. At payload tensor depth `lambda >= 1`,
with public physical inputs on `2^-f Z[i]`, use

```
extra fractional bits: g(lambda) = max(14 lambda, 13 lambda + 2)
stored component magnitude: < H * 2^(ceil((9 lambda + 1)/2) + 6)
scratch component magnitude: < H * 2^(ceil((9 lambda + 1)/2) + 8).
```

Here `f >= 0` is an integer and `H > 0`. Every initial real and imaginary
component has magnitude at most `H`; zero input is included.
For one 512-coordinate layer, fifteen extra fractional bits suffice.
These are sufficient bounds, not optimal precision or a cost improvement.

This closes the whole-prefix exact-grid implication left outside
[Arham Tahir's PR2674](https://github.com/CrocSwap/integer-mult-bounds/pull/2674)
and the local collector implementation in
[PR2754](https://github.com/CrocSwap/integer-mult-bounds/pull/2754).
PR2674 proves atomic instruction boundaries. PR2754 proves the two native
recipes of the first collector under an assumed entrance grid. This successor
connects the entire actual producer, all collectors and subsequent readers
through a conservative common grid. It does not construct an admitted
recursive child or establish its promised cost.

## Contract and exact sources

The word is ywz65's PR2586
`7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`. Its native archive contains
1,245 recipes covering 2,070 occurrences, including all endpoint conversions.
Each recipe is `M_left C_0 ... C_(r-1) M_right`, with `1 <= r <= 8` and
Gaussian monomials on either side. A monomial permutes addresses and
multiplies by powers of `i`, including its global phase.

The word and native bytes come through PR2754 head
`23d8aa7f11cd6a2e9d44a6ce4f6beebe1016492c`. The atomic-bound source is
PR2674 head `aeb5551b162b78e33c0b42681abaff92eb608d70`. Both original
READMEs, with attribution and limitations, are retained in `inputs/`.
[SOURCES.json](SOURCES.json) gives exact source paths, Git blobs and SHA256s.
The canonical chart definition is separately pinned to main.

Native correctness remains the predecessor's physical operator premise.
The replay binds every occurrence to its literal old/new frames and rank,
validates its monomial permutations, and independently executes two whole-word
physical fixtures. It does not rerun the compiler or prove every native
operator on all columns. The chart is
`Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)`.

At depth `lambda`, each chart and native map is tensor-powered across
`lambda` factors. Scalar ADD coefficients remain the original word's scalars.
This is the source's payload lift, not the tensor power of the entire scalar
program. The proof covers that lift; direct array execution covers `lambda=1`.

## Proof

### Atomic certificate, reproduced with predecessor credit

At an instruction boundary, a field with current frame `F` has physical value

```
sum_s c_s [Delta_F Delta_I_s^-1]^(tensor lambda) V_s(0).
```

Transport changes the outer frame, common-chart ADD changes the exact rational
row, and signs negate it. A private allocation has the zero row. The interpreter
checks each of its eight erasures has a zero row. All 358 public inputs are
independent, including arbitrary dirty workspace.

Canonical chart entries have Gaussian denominator dividing `2^dim(F)`.
For nonzero dyadic `c_s`, a sufficient termwise grid has extra bits
`(dim(F)+dim(I_s))*lambda-v2(c_s)`. The replay reproduces PR2674's complete
table over 5,748 changed-field boundaries and 103,145 nonzero term visits:

| Slope | Largest intercept |
| --- | --- |
| 0 | 1 |
| 1 through 9 | 2 |
| 10 | 0 |

Thus `B(lambda)=max(10 lambda,9 lambda+2)` suffices at every ideal atomic
boundary. The largest logical row absolute sum is `127/2`. These are retained
results, not new atomic-grid or logical-norm claims.

### Internal prefixes and the common grid

For `k` distinct coordinate C gates, a nonzero matrix entry is

```
(1+i)^(k-j) (1-i)^j / 2^k,  0 <= j <= k.
```

Its numerator is a Gaussian unit times `(1+i)^k`. Since `(1+i)^2=2i`,
both integer components are divisible by `2^floor(k/2)`. Every entry lies
on `2^-ceil(k/2) Z[i]`. Gaussian monomials preserve this grid.
At depth `lambda`, execute the tensor-factor right monomials, then the
`r*lambda` distinct coordinate gates, then the left monomials. Every prefix
needs at most `ceil(r*lambda/2) <= 4*lambda` additional fractional bits
relative to its atomic entrance.

Combining with the independently established ideal atomic bound gives
`B(lambda)+4*lambda = g(lambda)` for every internal prefix of every transport.
This evaluates the ideal program before reasoning about quantization.

Now implement all fields as Gaussian integers in units `2^-(f+g(lambda))`.
A C pair update divides each four-term signed integer numerator by two.
Its ideal value is on the grid, so the numerator is even. Nearest-even
quantization after the update is the identity. During a partially written
stage, each coordinate belongs to either the previous or the next complete
prefix; the same grid holds. Monomials are exact permutations and signs.

For ADD, the ideal before and after target are both on the common grid.
Their difference, the scalar multiple of the source, is therefore on it too.
Integer scalar division is exact. Induction through every instruction proves
equality to the ideal word. Each ideal private zero is consequently an actual
integer zero at erasure. This does not assume that a general rounded program
is linear, or dispose of a nonzero residual.

### Range and representation

Each internal native prefix, canonical chart and initial inverse chart is
unitary. A row of their product has complex absolute sum at most
`sqrt(512^lambda)`. An initial complex component has modulus at most
`sqrt(2)*H`. The unchanged logical row bound gives component magnitude at
most `(127/2)*2^((9 lambda+1)/2)*H`, strictly below the stated stored bound.
This also bounds partially written stages coordinate by coordinate.

Four-term butterfly numerators need at most four times this range.
The scalar alphabet is `+/-1/4,+/-1/2,+/-1,+/-2`; its product and addition
temporaries need at most three times the same range. The fourfold scratch
allowance covers both. Numerators need no extra fractional precision.
For a physical magnitude bound `M`, a sufficient signed integer width is
`1+ceil(log2(M*2^(f+g(lambda))+1))` bits.

The finite scalar expansion has unchanged rank mass 3,542 and therefore
`3542*lambda*2*512^lambda` scheduled real halvings. Each numerator uses three
real additions/subtractions. Monomials, scalar ADDs, reads/writes, representation
conversion and movement are additional. Payload size is exponential in
`lambda`; this expansion does not establish an efficient recursive
implementation or admit the supplier's recursive invoice.

## Evidence and reproduction

Standard-library Python 3.12 or later:

```sh
python3.12 -I -O -B research/p104-whole-word-internal-grid/verify.py
python3.12 -I -B research/p104-whole-word-internal-grid/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-whole-word-internal-grid
```

The read-only default authenticates inputs, reconstructs every logical row
and frame boundary, binds every native occurrence, and checks the literal
rank-zero through rank-eight prefix formula. Two internally quantized physical
executions use the fifteen-bit grid: the credited `Y2=delta_0` witness and a
dense complex integer fixture populating every address of all 358 public
fields. All 716 final fields match a separate canonical-chart/final-row
oracle. Both executions check all eight strict-zero erasures. These finite
fixtures support the implementation; the all-input and tensor-depth claims
follow from the proof above.

Five semantic controls reject a wrong native occurrence, missing private
compensation, a non-dyadic ADD, a native phase that corrupts private erasure,
and an insufficient six-bit execution. The last rejects inexact internal
halving; it does not show fifteen bits are necessary. Tests also check exact
Fraction prefixes, signed nearest-even ties, typed receipts, duplicate keys,
Git-free optimized export, real source corruption and output overwrite refusal.
`--out NEW.json` writes only a new receipt. [RESULT.json](RESULT.json) records
the full expected output.

The Power of Ten inspection bounds dimensions by 512 addresses, nine chart
bits, eight native stages, 358 public fields, 5,398 events and authenticated
source sizes. There is no recursion; every function is under 60 physical
lines. The interpreter uses full-vector temporaries, not an in-place storage
bill. Python integers, containers and JSON decoding allocate dynamically,
a runtime deviation bounded here by those dimensions and fixture integer
lengths. A capacity-controlled implementation must replace them before
claiming physical storage admission. Warning-enabled compilation, optimized
replay and behavioral failure tests are the available local diagnostics.
Ruff checks E/F/B and warning-as-error compilation pass locally. The registered
CPython 3.12.15 replay and four package test groups pass. The repository's
74 research-workflow tests pass with seven skips. A separate internal reviewer
checked the proof and ran the isolated optimized replay. Hosted CI is separate.

## Family decision and limits

Narrow and finish this precision implication. No next owner or construction
search is justified by it. The word, rank profile, ownership obligations and
selected frontier remain unchanged. This is exact scalar arithmetic with a
conservative format, not an approximate-child error theorem. Native operator
correctness and the tensor-lift convention remain inherited. Physical
tape/hosting, total runtime/storage, recursive cost, other corrections,
all-size algorithm admission and a favorable complete supplier remain open.
No new kappa or full multiplication theorem follows.

## Open next questions

- Can an admitted recursive representation realize this grid within its child
  cost allowance? Bind one actual child to the integer payload, scratch and
  native-prefix contract, then count bit operations and accesses. The finite
  scalar expansion does not provide that complexity bound.
- Can correlated chart/source rows reduce the sufficient format? Evaluate
  relative prefixes attaining the termwise bound, rather than adding independent
  worst cases. This may reduce storage, but further construction work needs
  a viable complete cost ledger.

## Credit and provenance

Credit Arham Tahir for PR2674's atomic bounds and PR2665's rounding obstruction;
ywz65 for PR2586's physical dual and PR2730's changed-grid collector;
Nick Petalas for PR2754's internal collector and PR2549/2550 precision/frame
questions; and Alejandro Zarzuelo Urdiales for Gaussian parity methods.
The elementary Gaussian prefix formula is retained mathematics. The new result
is its whole-word source-bound composition, range argument and expanded
caller replay. The retained READMEs preserve the full native/compiler/P104
lineage and notices. Apache-2.0.

Base main `31452ecd309f32a97e2e84214719b21297a59018`, priority revision 5.
[TASK.json](TASK.json) records scope, freshness, overlap and assistance.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18958803).
Evidence is author-checked with a separate internal review. Independent human,
proof-assistant, native-compiler cold replay and hosted-CI success are not claimed.
