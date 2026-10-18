# Exact alignment envelopes for the rank-seven scalar reference streams

The frozen PR3042 words need **four fractional bits forward and five backward**
in their emitted free-monomial scalar reference model. The corresponding
maximum coefficient row norms are **302 and 169**. Both providers give the
same streams. For signed P-bit integral component inputs, `P+13` bits suffice
in each orientation with its own binary point. A common five-fractional-bit
layout uses `P+14` bits for both orientations.

This closes a reference-arithmetic part of the producer/consumer handoff in
[PR3081](https://github.com/CrocSwap/integer-mult-bounds/pull/3081) and
[PR3080](https://github.com/CrocSwap/integer-mult-bounds/pull/3080).
It does **not** establish a physical fixed-point caller or improve kappa.
In particular, non-scalar frame adapters, recursive children, acquisition,
rounding errors, bit routing and clean-stock production are not implemented or
assigned zero cost.

## What is certified

| Orientation | Minimum fractional bits in this reference model | Maximum row l1 norm | Sufficient extra integer headroom | Total extra width |
|---|---:|---:|---:|---:|
| Forward | 4 | 302 | 9 | 13 |
| Backward | 5 | 169 | 8 | 13 |
| Common layout | 5 | at most 302 | 9 | 14 |

The minimum fractional-bit claims concern all bounded integral input arrays
under arbitrary free monomial actions, not just the largest denominator in an
individual ADD coefficient. Reserving three fractional bits because each
literal denominator divides eight is insufficient for the complete streams.
Repeated operations reach `3/16` forward and `-3/32` backward.

The exact witnesses, with zero-based indices into the regenerated native
streams, are:

- Forward event 6789, role `L363`, input variable 384, empty warp word,
  coefficient `3/16`.
- Backward event 7034, role `L505`, input variable 249, empty warp word,
  coefficient `-3/32`.

All 17,449 scalar events per orientation are checked, together with 240 formal
warp events and the exact final maps on all 632 ordinary input columns.
All 91 private zero buffers return. The eight private centre rows are empty
at completion. There are 731 distinct ordinary/private role names in the
transcript, not a claim that all 731 are simultaneously live.

Every ADD source is divisible by its required denominator after common
encoding at five fractional bits. Each unit-numerator half/quarter/eighth
therefore supplies the low-zero-bit condition required by PR3081, **if its
physical operand equals this encoded reference operand**. The same condition
supplies PR3080's denominator alignment for its multi-term ADD recipes.
Ownership, temporary source writes, carries and physical boundary conversion
remain separate conditions.

The final ordinary maps are `Y += X` forward and `X -= Y` backward, with all
other ordinary roles restored. Consequently every ordinary output is again
integral: its five low fractional bits are zero. Intermediate fractional
target bits must be retained, but they are not permanently live at the end of
this exact reference invocation. This statement does not justify truncating
an approximate physical output or clearing a nonzero intermediate centre.

## Model and proof

The checked object is the same scalar reference stream used by the retained
`bw_emit.py` free-operator endpoint check. At a fixed coordinate, an ordinary
role is represented by a finite row

```text
sum_(input i, reduced warp word w) a[i,w] * w(X_i).
```

Input arrays have integral real and imaginary components. A monomial warp
permutes coordinates and multiplies by a Gaussian unit, so it preserves the
component grid and component supremum norm. Adjacent inverse formal warp
symbols cancel. Different remaining words are kept distinct. Scalar operations
act by their literal rational coefficients. Zero buffers enter at zero.
`phase`, `climb`, `center`, `adapter` and `residual_adapter` events do not update
these *reference* rows, exactly as in the inherited scalar endpoint checker.
Their physical actions are not being simulated.

Induction on events proves the row identity. `lattice.py` computes every
nonzero coefficient with rational arithmetic, checks that every denominator is
a power of two, and records its maximum exponent. Thus forward rows lie in
`2^-4 Z` and backward rows in `2^-5 Z` for integral inputs. The displayed odd
numerators show that one fewer bit fails in the free model. For example,
specialize input 384 at the component indexed by the empty word and zero all
other finitely queried input components. A free regular monomial action keeps
those components distinct. This gives `3/16` at the stated forward event.
It does not prove the same minimum for a particular finite physical warp
representation, where distinct formal words may coincide.

Independently, `audit.py` starts every formal input coefficient at `2^F` and
uses integer arithmetic only. It stores reduced warp words in the opposite
order and checks divisibility *before every division*. It accepts `F=4/5`
respectively, rejects `F=3/4`, and independently obtains both maximum norms
and complete ordinary/private endpoints. It does not import the primary row
propagator.

For a row with norm `M=sum |a[i,w]|`, componentwise input magnitude at most B
implies output magnitude at most `M*B`. If inputs are signed P-bit integers,
`B <= 2^(P-1)`. Encoding with F fractional bits and h extra integer bits gives
signed width `W=P+F+h`. Since `302 < 2^9` and `169 < 2^8`, the encoded
magnitudes are strictly below `2^(W-1)` for the displayed widths. Therefore
all scalar-reference macro endpoints fit without rounding. This is not a
bound on temporary values inside a particular instruction lowering.

The norm witnesses are also attainable at a chosen coordinate in the free
regular model by assigning signs to its distinct input components. At `P=4`,
choose each such magnitude as seven. With one less total bit, the forward
encoded magnitude is `302*7*16=33824` and the backward one is
`169*7*32=37856`, both exceeding the signed 16-bit maximum 32767. This is a
free-model sharpness control, not a physical circuit lower bound.

For an ADD coefficient `n/2^k` in lowest terms, both the old and new target
rows belong to the global `2^-F` grid. Their difference is that multiple of
the source, and n is odd. It follows that the encoded source is divisible by
`2^k`. The verifier also checks this implication directly at every source;
the largest required source guard is four forward and five backward.

## Source binding and reproduction

The two provider words, transport/emitter scripts and notices are byte-identical
exports from PR3080 head `fd5ff58c6c438c438481bc4bff8c86e2d4fbe865`.
They are the original PR3042 words, not PR3080's later contracted candidate.
`VENDOR.json` records original paths, commits, Git blobs and SHA-256 hashes.
The source pins are checked before running either emitter. `RESULT.json` binds
the generated streams and every primary symbolic row through transcript hashes.
Regenerated gzip container bytes are not used to decide mathematical equality.

Python 3.12 and the standard library suffice. With RUN an existing external
session directory containing a `tmp` subdirectory:

```sh
TMPDIR="$RUN/tmp" python3.12 -B scripts/research_package.py \
  --package research/rank7-scalar-lattice

# Keep regenerated programs and emitter diagnostics if desired.
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-scalar-lattice/verify.py --work "$RUN/native"
python3.12 -W error -B research/rank7-scalar-lattice/audit.py "$RUN/native"
```

`--work` refuses an existing directory. Without it all temporary outputs are
removed after verification. Thirteen behavioral groups cover dirty targets,
missing inverse/clear operations, formal warp aliasing, insufficient fraction
and magnitude bits, actual-word coefficient mutation, source corruption,
invalid alphabets/bounds and occupied-output preservation.

See `CHECKS.json` for exact local checks and `ENGINEERING.md` for implementation
limits. The separate implementations share source streams and a contribution
owner; they are not independent human or formal-kernel review.

## Decision and limits

The contribution narrows the physical arithmetic handoff to a concrete boundary
rather than rerunning moment or frame searches. The scalar layer has an exact
finite alignment and magnitude envelope, and its fractional outputs close at
the complete reference endpoint. No selected result, paid child profile or
production precision charge changes.

## Open next questions

Can the physical producer of A gate 13, `X126 -= X83/2`, preserve these encoded
reference conditions across its preceding warp and frame boundary? Start with
that literal occurrence and prove the conversion grid, component range, owned
bits and exclusive access, then follow its fractional target bits to a completed
consumer. A frame/recursive operation that changes the grid or amplification
must have its own ledger; the numbers above cannot simply be applied to its
physical buffers. Stop before another implementation round if that contract or
its fully paid cost is missing. Approximate child-output defects are outside
the exact integral-input theorem.

The base is canonical main `d8e0f83f00191df62174b641e9fff055c357f641`,
priority revision 6. `TASK.json` records the handoff-first scope change from
`independent-moment`; `SOURCES.json` pins historical catalogue/selected context.
The selected conditional kappa remains 0.001672660197076918.

## Credit and license

Nick Petalas contributed these envelope checks and proof. Credit PR3080/3081
and PR3078/3076/3060/3056 for the arithmetic-caller questions, dcharb78/PR3042
for the frozen six-skip words, Jeremy Kothe/PR3015, Marius-Paul Dumitrean/PR2979,
Cinna Davis/PR2226, icekylinx and the retained native/geometry/owner lineage.
The frozen notices in `vendor/` retain predecessor attribution. No novelty is
claimed for general dyadic-grid induction or coefficient-norm bounds.
Apache-2.0. Development used substantial automated assistance; independent
human review remains open.
