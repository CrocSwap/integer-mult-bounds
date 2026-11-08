# Physical first narrow inverse window on union records

**No new κ.** This package connects prepared union records to a literal
fixed-tape first narrow inverse-window transaction: the original coupling
subtraction, the Schur solve, and the return of unchanged headers and
complementary values. Its coefficient pages come from the **same current
rational Gaussian Reference** as the target. Actual physical page preparation
runs before any payload, and one page context serves multiple prefixes.

The complete multiplication bound and all five global assumptions remain
unchanged. Whole-union routing, broad forward stages and outer recovery are
outside this contribution.

## Exact result

Partition the original source matrix into interiors I and retained coordinates
J, with original coupling C₀ and Schur matrix F. E contains J and every needed
interior endpoint. On the actual current post-dense input the target is

\[
 v_J\mapsto F^{-1}(v_J-C_0v_I),\qquad
 v_{E\setminus J}\mapsto v_{E\setminus J}.
\]

`UnionInverseWindow` streams b/2 complex E-lines into b real columns, carrying
a batch across prefix changes inside one source context. Encoded lockstep
transposes expose row-major operands. The retained exact seven-product caller
applies the original coupling shear on E, then solves on J. One inverse
transpose returns the original record order and every header bit. All hot-path
dimensions, addresses and loop counts remain encoded; fixed roles replace a
host recursive stack. Borrowed bodies/origins are restored, scratch is erased,
and a pending flag protects the full return until `consume()`.

The source shear is included, not replaced by an external post-shear promise.
Its J-row/complement-column support makes all products of its block masks
zero. Thus the existing page solver can implement its inverse through two
block factors, preserving the actual several rounding sites. `NUMERICS.md`
funds all four passes, actual rounded radii and exact Reference error.

The generic movement results of #4376/#4645, header ABI of #4583, and
algebra/page protocol of #4186/#5059 are inherited. The new result is their
literal serialized caller, current-source composition and complete return.

## Complete accounting

For m complex lines, a=|E|, n=|J|, dyadic b≥2, put K_E=ceil(a/b),
K_J=ceil(n/b), Z=ceil(2m/b). The exact scalar-child count is

\[
 [2(2K_E-1)+2(2K_J-1)]Z\,7^{\log_2 b}.
\]

`PROOF.md` prices parsing, encoded control, all transposes, page scans, copies,
padding, children, rewinds and erasure in addition to these scalar calls.
`NUMERICS.md` adds exact source generation, rational serialization, physical
page preparation and retained caches. Small-dimension ceilings remain.
The complete return occupies `ma(H+2w)` additional owned bits; active batch
space does not replace that term. Every role retains its historical maximum
backing. The production-density specialization additionally needs the retained
carve bound and separately funded setup/ceiling remainder.

## Executed source and schedule

The primary fixture is `Reference(61,3,2,1,3,32)`, window `[16,20)`, explicit
interior I=(1,2), J=(0,3), E=(0,1,2,3), b4/P24/w32. Its local band1 is checked
exactly. This is an admitted partition, not the conservative production carve
output, whose global bandwidth guard would make the small window all boundary.
The fixture supplies admissible values at the post-dense boundary; it does
not execute the preceding dense interior inverse.

Unchanged physical `prepare_pages` creates eight banks totaling 64 scalar
words. An independent original-matrix oracle checks their exact bits. The
retained #4327 step4, inverse layout and LIFO continuation execute around the
new physical step5 callback. A 4×4 grid gives32 record visits, eight complex
lines, four batches and 784 actual scalar products. Later lines consume values
changed by earlier work. The independent complete-grid hash is
`bf3f728125d578ee31d22da16491c3324877c2e56a606ebd164133c09cb9dff9`.

The schedule proof uses invariant flag classes, each executing its active
axes in ascending order. It does not assume rounded maps commute; a separate
control disproves that assumption. The outer schedule and #4583 encoder stay
host models. Only the stated step5 transaction is claimed literal.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/physical-union-inverse-window
```

Both registered normal and optimized (`-I -O -B`) commands execute the full
source/preparation/schedule/controls and compare stable fields to `RESULT.json`.
Expected marker: `PASS_PHYSICAL_UNION_INVERSE_WINDOW`. Physical rational page
preparation dominates this finite replay; each command has the repository's
maximum 600-second registered allowance. Direct normal reproduction is:

```sh
python3 -I -B research/physical-union-inverse-window/verify.py
```

`SOURCES.json` authenticates canonical inputs; `DEPENDENCIES.json` authenticates
the exact retained files, including published predecessor commit
`f821cba68f44048e70e78afb75603ed4dde99f11`. Exported execution needs no Git,
network or installation. The optional `--extended` development fixture is not
registered or counted as completed physical evidence.

## Independent checks and limitations

The separate source-aware AI verifier derives F by inverting the J-principal
block of original Q's inverse, checks both original equations, and independently
computes page words, completed integer dots and whole-grid chronology.
Raw-bit transport checks cover prefix changes, signed minimum values, aliases,
bad ordinals, truncated words, moved origins and moved pending output.
All 2796 owned roles and all borrowed bodies/heads are checked.

An actual-preparation E6/J1,b2 control exercises lower, diagonal and upper
coupling blocks and distinguishes staged from one-shot rounding (84 leaves).
An E3/J1,b4 control carries three complex lines in two batches with padding
(392 leaves). Truncating its final payload fails after one completed batch
(196 leaves), then erases partial output and restores every borrowed port.
Wrong source origin, transposed Schur matrix and omitted coupling are detected.

Finite-alphabet action counts mean reads/writes/unit moves, with a fixed
binary simulation factor; they are not Python VM instruction counts. No finite
speedup is claimed. The exact rational Reference is the numerical target.
Incoming dense error, other-axis header truth, global context selection and
outer recovery remain explicit premises. Independent review is not human or
proof-kernel acceptance. `PROOF.md`, `NUMERICS.md` and `INDEPENDENT-REVIEW.md`
contain the complete arguments and boundaries.

## Open next questions

1. Bind a literal global header/catalogue emitter and union router to this
   prepared-record contract, with full context and return storage charged.
2. Compose source-bound broad forward work and incoming dense error with the
   narrow substage's actual-grid chronology.
3. Fund exact page/catalogue preparation across a production parameter family,
   preserving every source key, setup lifetime and retained cache extent.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Separate AI
researchers supplied the exact source/numerical contract and independent
original-matrix/physical checks. See `NOTICE.md` for predecessor credit.
Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Apache-2.0.
