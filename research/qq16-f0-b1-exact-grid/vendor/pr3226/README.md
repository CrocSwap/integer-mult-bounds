# A sufficient finite grid for the complete native F0 reference

**Scoped sufficient-format proof and source-bound audit; no new supplier or κ.**
The literal one-layer QQ16 F0 reference can execute exactly with bounded dirty
inputs. If every real and imaginary input component is an integer multiple of
`h = 2^-b` with absolute value **strictly less than `2^P h`**, then the following
common format suffices:

```
working quantum q = h * 2^-35
signed two's-complement width W = P + 102,  P >= 1.
```

All 224 data fields and all 480 dirty helper fields may vary independently;
the eight owned private fields start at zero. Each field has 512 complex
coordinates. The bound covers the complete **26,099-event** F0 word, including
native butterfly interiors, residual and endpoint monomials, constant-product
partials, and every intermediate cancellation. It guarantees exact agreement
with the ideal finite reference, hence zero arithmetic defect relative to that
reference. It is a conservative sufficient format, **not a minimum**.

This closes one part of the finite-producer handoff after
[Ross Richardson's PR3067](https://github.com/CrocSwap/integer-mult-bounds/pull/3067)
and [Sricharan Vagvala's native component audit](../qq16-native-rounded-components/README.md).
Those predecessors exhibit deterministic loss for a particular binary64 input.
They do not give this uniform bounded-input contract. The separate
[PR3189 noise-lattice audit](../qq16-noise-lattice-audit/README.md) permits
independent child errors; here every native primitive is executed exactly on
the finer grid. No noisy-child closure implication is assumed.

The claim is in discussion [#2727](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-19001870).
Base and predecessor heads, Git blobs, and immutable input hashes are in
[SOURCES.json](SOURCES.json); the refined task is in [TASK.json](TASK.json).
Evidence is author-checked and independently reviewable, with a separately
implemented arithmetic recurrence. No independent human review is claimed.

## Arithmetic reference and exact scope

We use `programs.F_0` and its retained forward core from the unchanged
[joint-query certificate](../joint-query/certificate.json.gz). Native recipes
come from the pinned selected replay archive. A rank-r recipe applies its
serialized right monomial, r Gaussian coordinate lines, and its left monomial.
The monomials are signed permutations of real and imaginary components;
adjoints have the same range and lattice effects. The source F0 has no added
cover-map events. Phase events are control labels in this retained reference.
The inherited local chart/access interpretation is not proved again.

The pair-first Gaussian lowering is the one in the native component audit.
For a pair `(a+ib,c+id)`, compute these sums and differences, then halve:

```
rp=a+c; ip=b+d; rd=a-c; di=b-d
out0=((rp-di)/2, (ip+rd)/2)
out1=((rp+di)/2, (ip-rd)/2)
```

A scalar coefficient is normalized to `n / 2^d`. Compute the signed integer
product first, using binary shifts and additions, then divide exactly by
`2^d`. An ADD then adds that result to its target. The product is not silently
fused with its target, and native halves are not rounded. Only owned private
fields may be cleared. This is a finite direct arithmetic realization; its
cost is not the source's recursive child tariff.

The exact arithmetic guarantee holds for **arbitrary input components in the
stated box**, including nonconstant vectors and independent dirty helpers.
It is a proof by induction through the bound rules below, not an extrapolation
from the single literal test fixture. Exact helper restoration or data-map
identities transfer only insofar as they hold for the inherited ideal native
reference. We do not reprove that reference's complete symbolic endpoint.

## Bound invariant and proof

Let `M` be the maximum absolute integer entry coefficient, so `M < 2^P`.
The verifier assigns each field a pair `(R,g)` meaning that every component x
satisfies

```
|x| <= R M h,       x belongs to h * 2^-g Z.
```

`R` is a nonnegative dyadic rational and `g` is an integer, possibly negative.
A zero field has `(0,0)`. Ordinary inputs have `(1,0)`; private inputs have
`(0,0)`. The case `M=0` is immediate.

1. A signed permutation preserves `(R,g)`. Each used monomial's binary matrix
   is checked invertible; its coefficients and phases are checked to describe
   component permutations and sign changes.
2. Adding or subtracting two nonzero fields gives
   `(R1+R2, max(g1,g2))`. Zero operands retain the other bound.
3. Scaling by a nonzero dyadic c gives
   `(|c| R, g - v2(c))`. For a coefficient numerator n, every binary shifted
   term and every partial sum has magnitude at most `|n| R M h` and grid no
   finer than the source grid. All terms have the same sign before the one
   final coefficient sign change. These temporary bounds are recorded before
   the exact denominator division.
4. For a Gaussian line, the first sums have bound `(2R,g)`, the crossed
   numerators `(4R,g)`, and the halved outputs `(2R,g+1)`. The pre-halving
   numerator cannot be omitted from the range bill.
5. A private CLEAR replaces only its destination bound by zero. Earlier
   maximum range and grid obligations remain in the receipt.

Each rule follows from an integer linear combination or an exact dyadic
scaling. Thus it holds simultaneously for every allowed input, without
assuming cancellation, statistical independence, or a particular native
error pattern. Applying the rules to every source event yields:

| Quantity | Certified upper bound | First attaining bound location |
| --- | ---: | --- |
| Required fractional guard G | 35 | event 26033, native half in `inverse_0` on C0 |
| Component/temporary magnitude multiplier R | 42,822,849,617,116,776,290 < 2^66 | event 26051, native cross in `inverse_20` on C0 |
| Signed width | P + 102 | combines the two uniform upper bounds |

These are maxima of the conservative bound recurrence, not demonstrated
maxima of reachable values or necessary precision lower bounds.

Every recorded lattice contains only multiples of `q=h*2^-35`. In particular,
whenever an operation divides by `2^d`, its output lattice has been included
in G; its encoded numerator is therefore divisible by `2^d`. Induction proves
that integer execution on q performs every division exactly. Moreover,

```
|x/q| <= R M 2^35 < 2^(66+P+35) = 2^(W-1).
```

The strict input bound makes both signs fit W-bit two's-complement storage,
including sign changes. Binary-product partials and butterfly numerators
were included, so this argument also rules out intermediate overflow.
No floating exponent or significand approximation is used.

## Direct finite payload bill

The receipt retains the source inventory: 3,494 native recipes, rank mass
5,530, 7,692 applied monomials, 866 identity adapter labels, and ten phase
labels. The following is a constructive upper bound for one execution on
512-coordinate fields, in operations on **W-bit payload words**:

| Operation | Count or upper bound |
| --- | ---: |
| Additions/subtractions, including constant products | 33,161,216 |
| Constant left shifts and exact right shifts/halvings | 21,299,200 |
| Negations | at most 18,526,208 |
| Component copies | 49,646,592 |
| Private and final scratch zero writes | 33,804 |
| Sum of these payload operations | at most 122,667,020 |

A constant with k nonzero binary digits uses k component copies, k−1
additions, one left shift for each nonzero digit position, at most one sign
change, and at most one exact right shift. For in-place SCALE, save the input
once and reuse it for the later shifted terms. The source ADD leaves its
source intact until the final target update. Native pairs use four input and
four output copies plus eight sums and four halvings. Each monomial writes a
full permutation buffer and then copies it back, so no free pointer relocation
is assumed. Monomial negations are bounded by one per component; this is not
an exact sign census or a circuit minimum.

Logical payload storage is `712*1024 = 729,088` W-bit words. One 1,024-word
permutation buffer and twelve arithmetic temporary words suffice; they are
written before read and cleared at completion. Thus a sufficient payload
allowance is **730,124 W-bit words**, including that scratch. At P=66, W=168,
this is 122,660,832 payload bits. This is a logical payload bound, not measured
Python memory. Fixed code, addresses, counters, routing and ownership records
are outside this payload subtotal. A fixed-tape/physical implementation must
charge them, and must implement the listed wide-word operations.

No claim of affordability follows. The arithmetic and payload storage are
constructively bounded; recursive cost, physical placement/movement, all-size
compilation, B1, F17 consumption and the complete supplier invoice remain
unknown. The family decision is **narrow and stop** at this numerical contract.

## Evidence and reproduction

From the repository root with standard-library Python 3.12:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-native-grid-envelope
```

Expected markers:

```
PASS_QQ16_NATIVE_GRID_ENVELOPE events=26099 grid_guard=35 range_bits=66 signed_width=P+102
PASS_QQ16_NATIVE_GRID_INTEGER_RECURRENCE observations=133628
PASS_QQ16_NATIVE_GRID_CONTROLS literal_events=26099 fixed_grid_exact binary64_control_loses_data
PASS_REGISTERED_RESEARCH_PACKAGE research/qq16-native-grid-envelope outcome=completed
```

[verify.py](verify.py) uses rational magnitudes and explicit dyadic valuations.
[independent.py](independent.py) imports neither that implementation nor a
predecessor checker: it uses integer magnitudes at each local lattice and
reconstructs the complete trace. Both agree on **all 133,628 bound
observations**, every completed event, final bounds, and the direct operation
counts. This is a separate arithmetic implementation by the same contributor,
not independent human review of native semantics.

[controls.py](controls.py) checks 4,637 rational scalar containment cases and
all 625 Gaussian pairs in `[-2,2]^4`. A further 3,859 literal binary
constant-product cases cover every source coefficient, including large signed
operands. Rejecting controls cover an off-grid
native half, overflow at a crossed numerator whose final outputs fit, a
nondyadic coefficient, a singular monomial and an attempted borrowed CLEAR.
A later CLEAR is checked not to erase an earlier guard obligation.

It also actually executes the complete native dirty-helper fixture
`L112=1`, `L224=2^65`, other fields zero, on the uniform grid G=35 with W=168.
Every division and intermediate range is checked. All 26,089 changed-field
cuts are hashed; all 480 chosen helpers return and all private outputs are
zero. The exact data survive. Running the retained binary64 engine on the
same source and input loses data in fields 112,114,137,190,211, as its authors
reported. [CONTROLS.json](CONTROLS.json) records both the escape and its control.
The reused dispatcher and monomial evaluator retain their attribution; this
fixture is not a new discovery of the rounding failure.

Default replay is read-only. `--write PATH` exclusively creates a new receipt.
The two scientific archives and two reused implementation files are authenticated
and declared in [VERIFY.json](VERIFY.json). The generic package runner, selected
cold replay, source theorem and physical implementation have different scopes;
a passing local replay is not supplier admission or a multiplication theorem.

## Open next questions

Can a recursively admitted caller supply this input/dirty bound and grid at an
affordable complete cost? Pin one actual child layout and consumer, then price
its wide-word arithmetic, routing, ownership, storage and F17 consumption
against a complete allowance before optimizing this envelope. This matters
because PR2965 assumes producer accuracy; it does not pay for an exact direct
reference. B1 and arbitrary tensor depth need their own numerical realization. Input
preparation and any error from placing an original real input on the entry
lattice also remain separate.
Those unresolved physical/recursive costs are the blocker. The structured
question and stop rule are in TASK.json; no larger search is proposed.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New derivation, bound interpreters, fixed-grid control and prose are Apache-2.0.
No independent human review or formal-kernel proof is claimed.

Credit Sricharan Vagvala for the actual pair-first native component lowering
and binary64 corroboration (`946a399d6ae1667236bb395d21c33c749e000877`),
Ross Richardson / PR3067 for the physical-rounding witness and finite-producer
handoff, Tekalign / PR3017 for the native vector evaluator and / PR3189 for
the separate noise-lattice warning, Arham Tahir / PR3036 and PR2995 for the
scalar rounding/fault witnesses, and Nick Petalas / PR2965 for completed-output
error transfer. The runtime control reuses the unchanged native-rounded-components
code and its unchanged Tekalign evaluator, without claiming their implementation
as new. Ali Romman, Sagar Thakrar, DLamdata, ywz65, starship-s, Douglas Colkitt
and the full retained QQ16/native lineage retain the attribution and notices in
[joint-query/NOTICE.md](../joint-query/NOTICE.md).
