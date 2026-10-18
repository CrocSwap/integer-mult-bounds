# Executed checks and scope

The complete mathematical replay passed on Linux under CPython **3.14.4**
and isolated optimized CPython **3.12.3**. The final 3.12 replay used a
relocated package with write permission removed from every source file and
directory; its receipt was written outside that tree. The complete receipts
are byte-identical, SHA-256:

`789e1b6ae36d56de38010c0824f320682f4246125417bcf71f4243d8bea3a27a`

The main case's full canonical decoded SHA-256 is
`ed3ff7af1243172307a86648324cff314c95a7ef7cd58c9b40186d2e6909653c`.
The complete primitive program's is
`eb88663379c1412a915af9b545b9f8934aa2d9d20a4f89be2f89ec6c73b632ca`.
Generated gzip artifacts are compared by every decoded field, while copied
source files retain exact Git-blob and SHA-256 pins.

## Mathematical coverage

- **5,280 matrix cases**, each with all ten independent data columns:
  861 ordered binary/ternary trees through seven factors at widths 1, 2, 5
  and both signs, plus each parent's chosen plan at sizes 8–64, both signs.
  A separate explicit control stack agrees with the pinned emitter's full
  word. Every leaf prefix agrees with an integer matrix lift modulo `2^w`;
  every recursive return agrees with the direct child-product shear.
  Coverage: **528,302 leaf prefixes and 667,416 recursive returns**.
- **33,280 exhaustive scalar cases**: binary echoes over Z/4Z for every
  coefficient tuple and every five-row input, and ternary echoes over Z/2Z
  under the same complete domain, in both directions. The actual primitive
  backend executes **2,160,640 commands** in these checks.
- **144 dense cases** with dimensions 1, 2, 3 and sizes 1, 2, 3, 5, 8, 13;
  four seeded coefficient fixtures and both signs, including zero factors.
  Independent endpoints, unique signed recovery, operation counts, private
  widths and data-head invoices all agree.
- Four 52-factor fixtures: bounded-seven or arbitrary 56-bit dirty inputs,
  each sign. Every literal leaf is compared with the separately executed
  integer lift. The literal inverse restores every bit pattern. The stress
  integer lift reaches **90 signed bits**, while data storage remains 56.
- The primary bill is independently counted from scalar execution and from
  a closed operation formula and separate address itinerary. This includes
  13,760 reductions, all private clears, 16,512 data/coefficient accesses,
  1,332,416 intercell steps, 924,672 bit actions and 76,431,616 data-head
  moves. Setup, program/control and adapter obligations are stated separately
  in PROOF.md, rather than assumed free.

**19 mathematical/admission controls** reject insufficient endpoint width,
strict signed-cap equality, a zero product hiding an unrepresentable external
input, unjustified source bounds, noncanonical dirt, fractional or boolean
coefficients, aliased ports, writes to the protected source, missing helper
restoration, wrong inverse signs/order, omitted product or accumulator
reductions, uncleared private work, undercharged reductions, decoding an
out-of-range integer, saturation and an overflowing unreduced integer lift.
The separate floor-by-two example shows why quotient arithmetic does not
validate rounded rational factors.

## Artifact and repository checks

All **12 package tests** pass in normal and optimized Python. They exercise
offline relocation; level-1/level-9 recompression of both generated gzip
files; source/context mutation; changed width or removed reduction with
rebound digests; undercharged reductions or product storage; omitted
directions/coverage; boolean receipt fields; and duplicate/nonfinite JSON.
A modified parent containing an executable exception is rejected by its pin
before the parent module can execute. All rejection predicates use explicit
checks and remain active under `-O`.

All **25 existing selected-record, inventory-link and proof-binding tests**
passed at the experimental base. The final working-tree scope and whitespace
were checked. No existing generator, selected record or `upstream/` file is
changed.

Review after the first complete replay identified the zero-factor case:
the width must also represent the unchanged input if the product norm is
zero. The guard now uses `max(X, Y + X product(K_i))`; a specific rejection
control checks that boundary. Both final mathematical replays include it.
Source admission was additionally moved before importing the copied emitter,
and the final portable replay and executable-source corruption test passed.

## Overlap and remaining obligations

The initial pinned-issue query returned none. The final queue was checked
through **PR1152**, including Ali Romman's **PR1135** and its exact-lift proof
at `4c35687d7c0da8e6cf33f17e418ecf31c95ff3ad`. That proof prices a
common-denominator rational embedding and rounded-interface obstructions;
it does not supply this integer modular backend or invoice. This package
does not solve those rounded obligations. PR1144's bounded modular recovery
accelerates a separate determinant audit. No code from either is imported.

The experiment remains based on **ba82555c64e1879e4b7decce28186f208fcb8262**.
At publication upstream is **ce7ad1b6ab09452c3478723a2e96ed5ff212dc08**,
selecting PR1094's conditional kappa **0.001672660197076918**. PR1057 remains
open at the exact pinned head. This self-contained package does not consume
the moving selected pointer or any newly changed root source.

No physical fixed-tape compiler, rounded/dyadic/irrational supplier adapter,
whole hosted supplier, outer assembly, selected cold replay, full repository
suite, measured runtime gain, unrestricted optimum, formal theorem proof or
independent human peer review is claimed. Hosted CI remains separate from
local validation. The all-size/compiler, common-label realization, hosting,
source routing, exact recovery for any different coefficient domain, and
analytic-transfer obligations remain inherited or open. The unchanged leaf
multiplicities give no new multiplication exponent.
