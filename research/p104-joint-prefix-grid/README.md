# A smaller sufficient grid for every P104 native prefix

The unchanged 5,398-event physical inverse-transpose of PR2586 admits

**`g(lambda) = ceil(15 lambda / 2) + 2` extra fractional bits**, for every
positive integer payload tensor depth `lambda`. At one layer this is **10 bits**,
in place of PR2772's sufficient 15. All native butterfly divisions and scalar
ADD divisions are exact, including the eight strict-zero private erasures.
This is a smaller sufficient format, **not a minimum** or a supplier result.

This answers the second open question in
[PR2772](https://github.com/CrocSwap/integer-mult-bounds/pull/2772), head
`69ba5a423246a1c9281bdd5c1f51240b454f2aa6`: count the Gaussian divisibility of
relative chart/native prefixes jointly, instead of adding separately rounded
worst cases. The word, native factorizations and physical operator are unchanged.
No changed scalar schedule, owner map, recursive saving or new kappa is claimed.

| Payload tensor depth | PR2772 sufficient guard | This sufficient guard |
| --- | ---: | ---: |
| 1 | 15 | 10 |
| 2 | 28 | 17 |
| 3 | 42 | 25 |

## Contract and source binding

Public physical inputs have real and imaginary components in `2^-f Z`, for an
integer `f >= 0`; all 358 inputs, including 150 dirty helpers, are arbitrary.
The canonical charts are `Delta_W = conjugate(Gamma_W)`. Scalar coefficients
are unchanged under payload tensoring. Each chart/native operator is applied
to each of `lambda` tensor factors, as in the predecessor's payload lift.

The native archive has 1,245 records covering 2,070 transport occurrences.
Every recipe is a Gaussian monomial, `r` coordinate C gates, and another
Gaussian monomial. The public word, archive, integer interpreter and README
are retained byte-for-byte from PR2772. Its word/archive originate in ywz65's
PR2586 `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`, through PR2754
`23d8aa7f11cd6a2e9d44a6ce4f6beebe1016492c`.

The exact canonical constructor is also retained from main. Its
`canonical_frame` is a monomial-conjugated product of `dim(W)` coordinate C
gates, with the zero/full special cases using zero/nine gates. Conjugation
and inversion preserve that number and change only signs/order/monomials.
All retained bytes have Git-blob and SHA256 pins in [SOURCES.json](SOURCES.json).
Native operator correctness, the canonical-chart convention and tensor lifting
remain inherited; this package does not rerun the full native compiler proof.

## Proof

### Joint Gaussian divisibility

Put `pi = 1+i`. Each nonzero entry of a normalized C gate or its inverse is
`pi/2` times a Gaussian unit: `1-i = -i*pi`. A Gaussian monomial has only
Gaussian-unit nonzero entries. Consequently every matrix entry of a product
containing `n` such C gates, with arbitrary intervening Gaussian monomials,
belongs to

```
(pi^n / 2^n) Z[i]  subset  2^-ceil(n/2) Z[i].
```

Indeed every contributing matrix-product path has the common factor
`pi^n/2^n`; adding paths preserves its Gaussian ideal. Since `pi^2 = 2i`,
`pi^n` is divisible by `2^floor(n/2)`. This argument needs neither independent
C directions nor commuting monomials. Tensor products add their factor counts.
The Gaussian parity algebra is standard and credited prior work; the new step
is its joint, source-bound application below.

### Count the actual relative prefixes

At an atomic cut the physical value in role `r`, with current frame `W`, is

```
sum_s c[r,s] (Delta_W Delta_I_s^-1)^(tensor lambda) V_s(0),
```

where `I_s` is source `s`'s initial frame and the `c[r,s]` are exact dyadic
logical-row coefficients. This is the predecessor's common-chart invariant.
Our separately written sparse Fraction interpreter reconstructs every row,
checks every common-chart ADD and nested transport, and checks the zero row
at every private erasure. No dirty public input is assigned zero.

For an atomic term take `n = dim(W) + dim(I_s)` and `d = -v2(c[r,s])`.
For a native transport of rank `r_native` beginning at frame `A`, take
`n = dim(A) + dim(I_s) + r_native` and the entrance coefficient's `d`.
The first case bounds the atomic operator; the second bounds every internal
native prefix. Before the right monomial and after any subset of the coordinate
gates, there are at most `n*lambda` C factors, including the entrance chart
and initial inverse chart. Left monomials add no denominator. Thus

```
ceil(n*lambda/2) + d
```

extra bits suffice for that term, and summing terms preserves the grid.
Using the full native rank only overestimates earlier prefixes; tensor-factor
interleaving and partially written stages cannot increase the factor count.

The complete census has 7,818 observations (5,748 initial/changed-field
boundaries plus 2,070 native-entrance observations) and 143,912 nonzero term
visits. These are the maximum intercepts at each **counting bound**, not
measurements of actual matrix denominators:

| C-factor count `n` | Largest `d` |
| --- | ---: |
| 0 | 1 |
| 1 through 9 | 2 |
| 10 | 0 |
| 15 | 2 |

For every positive integer `lambda`, their maximum is
`ceil(15*lambda/2)+2`. The limiting certificate term is the `Y27/4` coefficient
of private role C at event 2031, with entrance dimension eight, source initial
dimension zero and native rank seven. This term does **not** prove that the
actual relative operator requires ten bits; its factors can cancel further.
The claim is sufficient precision only.

### Exact execution, cleanup and range

Evaluate the ideal program first using the preceding bound. Store Gaussian
integers in units `2^-(f+g(lambda))`. Each native butterfly's ideal outputs lie
on this grid, so its four-term integer numerators are even. Nearest-even
quantization after each division by two is the identity. During an in-place
pair update, read both old complex values before writing either result; each
stored component is then from a previous or next complete stage on that grid.
Gaussian monomials are exact permutations and unit phases.

For ADD, both ideal target-before and target-after lie on the grid, so their
difference, the scaled source, does too. Therefore the scalar divisions are
also exact. Induction proves equality to the ideal word at every stored cut.
The eight ideal private zero rows are actual integer zeros at erasure; this
argument does not assume a generally rounded program is linear or erase a
nonzero residue.

PR2772's range argument applies unchanged: if every initial real/imaginary
component has magnitude at most `H > 0`, stored component magnitude is strictly
below `H*2^(ceil((9*lambda+1)/2)+6)`, with two additional magnitude bits for
four-term scratch. Each internal native prefix is unitary and the logical-row
absolute sum is at most `127/2`, as independently recounted here. Lowering the
fractional guard does not increase those physical magnitudes. A bounded-storage
or recursive implementation still needs its own capacity and access argument.

## Reproduce and evidence

Standard-library Python 3.12, from the repository root:

```sh
python3 -I -O -B research/p104-joint-prefix-grid/verify.py
python3 -I -B research/p104-joint-prefix-grid/test_verify.py
python3 -B scripts/research_package.py --package research/p104-joint-prefix-grid
```

The default replay is read-only, network-free and Git-free. It authenticates
all retained inputs before importing the credited PR2772 integer interpreter.
The new sparse row census imports no predecessor verifier. Native occurrences
are bound to exact frames/ranks and all monomial permutations are checked.

Two complete ten-bit integer executions use the credited `Y2=delta_0` witness
and a dense complex-integer input populating every address of all public roles.
Every one of 366,592 real endpoint coordinates per fixture matches a separate
canonical-chart/final-row oracle. Both runs check all eight erasures. The
retained six-bit fixture rejects an inexact internal halving. These fixtures
check implementation behavior; the written argument supplies the all-input
and all-positive-tensor-depth implication.

The tests add Gaussian Fraction calculations with interleaved noncommuting
monomials, frame/rank/compensation faults, source/executable corruption,
duplicate/typed receipt checks, optimized Git-free replay and output refusal.
[RESULT.json](RESULT.json) is the complete expected receipt. No proof-assistant,
independent-human, hosted-CI or selected-supplier cold replay is claimed.

## Scope and family decision

Narrow and finish this finite precision implication. No further construction
or owner search is justified by this improvement alone. Actual factor
cancellation could give a smaller grid; no minimum is claimed. Recursive-child
bit complexity, efficient tape/storage access, physical owners, the other 102
forward corrections, complete moments and all-size supplier admission remain
open. Full-vector Python execution does not price a recursive child. There is
no new selected frontier, complete supplier or multiplication theorem.

## Open next questions

Can one actual recursive representation meet this exact internal-grid contract
within its already paid child cost? Start with one native rank-seven child,
state the payload and scratch integer layout, and count all bit operations and
accesses. The blocker is an admitted recursive complexity/representation lemma,
not availability of a finite vector interpreter. More format optimization
should wait for evidence that it changes that complete decision.

## Credit and provenance

Nick Petalas supplies PR2772's whole-word precision composition, the retained
integer interpreter and full-vector fixtures, following his PR2754 collector.
Arham Tahir supplies PR2674's atomic physical grid and PR2665's rounding
obstruction. Credit ywz65/PR2586 and PR2730, Alejandro Zarzuelo Urdiales's Gaussian
parity methods, and Nick Petalas's PR2549/2550 precision/frame work. Retained
PR2772 text preserves the native/compiler/P104 lineage, including Rohan Arun,
Chafik Boukhalfa, Ross Richardson, Ali Romman and icekylinx. Existing source
notices remain unchanged. New joint census, proof application, controls and
packaging were prepared for David (`sandersdavid90-droid`) with substantial
OpenAI Codex assistance. Apache-2.0.

Scientific base: current main `d9b24831174325cad2e04e34da2068d7acb02938`,
priority revision 5. [TASK.json](TASK.json) records the picker nonce, changed
scope, live-overlap limits and final freshness. Discussion writes are not
exposed by the connector; an attempted advance claim on PR2772 was denied
with HTTP 403. No public reservation is claimed.
