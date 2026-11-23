# An explicit production precision bound for the direct circulant Fourier word

This package derives a smaller sufficient external precision for the exact
source word in [#7849](https://github.com/CrocSwap/integer-mult-bounds/pull/7849).
It connects the retained compiler's physical prefix and inverse-prefix bounds,
the actual sixteen-H lowering and cached diagonal implementation, and the
state-relative rounding bootstrap. The result is a **local analytic interface
theorem under named source contracts**, with exact finite controls. No full
framework assumption is removed, and there is **no new kappa**.

## Result

For public precision `p`, `d` axes, binary widths `ell_i >= 1`, and
`L = sum ell_i`, define

```
E = ceil(1257 L / 2) + 2154 d
A = 104 L + 438 d
J = 20000 (d+1) (max ell_i+2)^6
C = 4 J (d+1)^2 + d+1
P = 4p + A + 2E + bit_length(C).
```

Using `P` fractional bits in the source external grid, and its unchanged
`P+8` coefficient-construction call, gives raw transform error strictly below
`2^(-4p)` on every represented half-disk input. The two signs and the entire
padded tensor are covered. The corollary to the source public-grid theorem
retains its final integer error bound `144/B^2 < 1/2` for `B >= 32`.

The proof supplies three separate interfaces:

1. **Actual source intervals.** The full compiler's explicit constants give
   physical prefixes and inverses at most `2^98 t^52`. The routed sixteen-H
   word raises this to `2^537 t^156` per root, and both roots and diagonals
   to `2^1076 t^314` per axis. Complete-factor norms alone are not used to
   control a partial interval.
2. **Local rounding.** Each diagonal coefficient comes from at most `d`
   current-coordinate factors. An odometer induction prevents rounding error
   from accumulating with the number of tensor records. Its state-relative
   defect is at most `(d+1)^2 2^(-P+A)(1+norm(z))`.
3. **Strict numerical budget.** The displayed selector makes both the
   noncircular bootstrap spend and the final raw-error inequality strict.

The exact stored one-axis word also has synthesis error below `2^(-P)`,
instead of needing a dimension-dependent polynomial envelope for that step.
See [PROOF.md](PROOF.md) for quantifiers, all constants and inherited premises.

The old source selector has leading term `4p+32768(L+6d)`. The new selector
has leading term `4p+1361L+4746d+(L mod 2)`. For example:

| Public bits | Axis widths | Old sufficient fractional bits | New sufficient fractional bits |
| ---: | --- | ---: | ---: |
| 72 | 4, 5 | 688,620 | 22,068 |
| 12,288 | sixteen widths of 128 | 70,304,068 | 2,912,487 |
| 6,000,000 | ten widths of 100,000 | 32,793,966,628 | 1,385,047,587 |

These are exact precision-selector comparisons, not full transform executions,
measured memory or runtime gains, or minimum-precision claims.
The original source selector is larger for every supported input, by an explicit
integer comparison in the proof, so the same theorem also validates its numerical
budget under the named contracts.

## Reproduction and evidence

From the repository root:

```sh
python3 -B scripts/research_package.py --package research/direct-circulant-production-precision
```

For a source export without Git:

```sh
python3 -I -B research/direct-circulant-production-precision/check_precision.py
python3 -I -O -B research/direct-circulant-production-precision/check_precision.py
```

Both direct commands finish with `PASS_DIRECT_CIRCULANT_PRODUCTION_PRECISION`
and produce identical evidence. They check an exact positive-coefficient
polynomial certificate for the full schedule count; 60 bindings to the pinned
allocator; 203 exact two-wire words through a separate rational matrix
interpreter; 120 odometer packets containing 2,448 records against fresh
current-coordinate evaluation; and 53 selector inputs, including address
widths too large to materialize. Negative controls cover corrupted source
bytes, a middle-diagonal phase, omitted inverse-prefix reasoning, a stale
cached suffix, a missing column guard, and undercharged precision envelopes.

The universal theorem uses the written inequalities. The finite packets are
not an exhaustive verification of arbitrary matrices, widths, inputs or the
complete multiplier. `EVIDENCE.json` records executed checks and review status.

## Source pins, scope and novelty

Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`.
The direct-circulant source is frozen at
`3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd` in
`aliromman/integer-mult-bounds`. The six small code copies in `retained/`
are exact scientific inputs, not another copy of the predecessor package.
`ORIGINS.json` lists their repository paths, exact commits, Git blob IDs and
SHA-256 digests. The standalone verifier authenticates those bytes before
extracting named functions. `SOURCES.json` separately preserves the canonical
task and selected-result provenance. The result concerns these frozen words;
later compiler or phase changes need a new applicability check.

The predecessor supplied the construction, its original generous selector,
the public-grid recovery theorem and diagnostic product checks. This package
adds a source-specific independent constant derivation, a sharper local endpoint
bound, the resulting smaller selector, and independent failure-sensitive
checks of the emitted word and coefficient-cache semantics. It does not repeat
the previously reported failure of a low diagnostic precision as a failure of
the production selector.

The scope is historical and source-specific. Later
[#7981](https://github.com/CrocSwap/integer-mult-bounds/pull/7981), pinned at
`9585c1fa2ed5f2316ac09e04b357cb720badfcb8`, changes the chronology by completing
and normalizing each pack, and weakens the intermediate raw target from
`2^(-4p)` to `2^(-p)/8`. Its
[numerical proof](https://github.com/aliromman/integer-mult-bounds/blob/9585c1fa2ed5f2316ac09e04b357cb720badfcb8/research/triangular-native-supplier/NUMERICAL-STORAGE.md)
therefore gives a different and asymptotically smaller precision selector. The
present selector is not an improvement over that successor. That successor still
cites #7849 for local root and interval estimates; the sharper source binding here
is reusable evidence for that inherited interface, subject to a separate check of
the changed pack schedule and caller. Searches of PR bodies for `7849` and
`circulant precision` also inspected #7868, #7914 and #8030. This is a bounded
overlap check, not proof that no unpublished or unindexed duplicate exists.

The retained full compiler estimates, certified phase service, exact native
Hadamard action on widened represented grids, outer CRT geometry and recovery
theorem remain named dependencies. No all-size private-tape storage proof,
native tariff, ownership implementation, selected-certificate edit, full
assumption removal, practical crossover or proof-kernel acceptance is claimed.
`precision.py` provides the candidate replacement selector without modifying
the frozen predecessor.

## Open next questions

1. Obtain external mathematical assessment of the source gate/layout bindings
   and coefficient-cache induction. The included separate task-agent review
   accepts the frozen corrected proof; adoption remains an upstream decision.
2. Join this external grid to a source-specific all-size private-grid and arena
   theorem. That requires the exact native representation and ownership
   contracts; a numerical endpoint estimate alone does not supply them.
3. Independently review or formalize the retained full compiler's physical-cut
   estimates used here. The present proof instantiates those estimates rather
   than re-proving the whole compiler.

The structured first steps and blockers are in `TASK.json`.

## Credit

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Ali Romman supplied [#7849](https://github.com/CrocSwap/integer-mult-bounds/pull/7849)
and its [#7846](https://github.com/CrocSwap/integer-mult-bounds/pull/7846)
native/recovery integration. Jose Manuel (`jmbarrancoml`) supplied the retained
rational full compiler and conditioning estimates; Vlado Vojdanovski supplied
the displacement and tensor matching compiler; Chafik Boukhalfa supplied the
certified phase routine; Cinna Davis and the credited mixed-rank/native
contributors supplied the inherited supplier and recovery chain. Source notices
are preserved. Model-assisted cross-review, when recorded, is distinct from
human peer review and proof-kernel verification. Apache-2.0.

## Completed separate review

[review/CROSS-REVIEW.md](review/CROSS-REVIEW.md) accepts the local conditional
numerical theorem at proof SHA256
`26e4e214f0a5785c1d1414561465bb49a3248f9e6f59f6b514eb95a887bdfe2f`.
The author proof retains its original pre-review label for byte identity;
this later review and ROOT-REVIEW.md record the completed disposition.
A fully expanded lowering contains 23 diagonals and 16 H factors, with 38
non-pivot factors. This corrects two prose counts; the conservative 64^40
envelope and every selector constant were unchanged.

The independent reviewer uses a new Gaussian-rational matrix interpreter for
600 words across all four pivots, and noncommutative expression trees for
1,214 coefficient-cache records. Two mutation controls reject a wrong sign
and a stale carried suffix. The author checker is not reused as independent
evidence. The registered third command runs this separate oracle.

Scientific source copies and frozen proofs are self-contained. Top-level
SOURCES.json pins canonical provenance; ORIGINS.json authenticates the six
executable fixtures. Review source citations, read hashes and receipts are
retained under review/. No complete multiplier or private-tape proof is
claimed by this publication.

## Completed source-ordered complete-gate supplement

[compiler-cuts/INTEGRATION.md](compiler-cuts/INTEGRATION.md) and its separate
[review](compiler-cuts/review/CROSS-REVIEW.md) now establish a scoped fragment
lemma for the exact retained Builder, Triangle, Program and Full factories.
Their same sufficient four-way envelopes cover every cut after a subset of
complete one- or two-wire gates in a matching. For the primitive word, the two
cross-bank shears have the same direction and all bank-local gates are unitary;
this controls every prefix, suffix and inverse without an additional generic
matching-interpolation factor. The Full bound remains `2 L0 B H`, with
`B = 256 N^3 (lambda Q)^12`, and an arbitrary interval is bounded by its square.
Both `lambda >= 1` and `Q >= 1` are required individually, as in the source.

This is an extension of a sufficient source envelope, not a no-loss theorem
relative to the measured norms of neighboring full-layer cuts. It retains the
all-size conditioning, rank, phase-service and atom-error contracts. Intermediate
coordinate assignments, arithmetic temporaries, changed recursive atom services
and physical tape costs remain outside the result. The original precision proof,
selector and selected certificate are unchanged.

The author checker and a separately written rational-realification/downset
checker both passed normally and with Python assertions disabled. The independent
review checked 760 primitive cuts, 3,040 four-way structural certificates,
100 arbitrary primitive intervals and 46 separate LDU downsets. The source's
individual conditioning lower bounds have an explicit failing control when
improperly weakened to their product alone. Source notices, frozen proof bytes,
receipts and the prior-work comparison are retained inside the supplement.

This result builds on #4976 and credits the sharp conditioned interpolation
already proved in [#5940](https://github.com/CrocSwap/integer-mult-bounds/pull/5940).
The singular partial-write swap warning and rounded-event boundary were already
identified in [#5240](https://github.com/CrocSwap/integer-mult-bounds/pull/5240);
the new proof does not claim either precedent as a new result.
