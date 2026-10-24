# Centre codes with unitary, signed, and rational metrics

This package proves a sharp 24-coordinate bound for the original sixteen
readers in the Gaussian-dyadic unitary model. It gives an actual code and
complete local native words that attain 24. A different reciprocal reader
has a signed-metric code with sixteen coordinates. Thirty complete local
native words implement this code, its paid pair companion, and a separate
transpose interface. A general dyadic scalar construction and a rational-unitary
sixteen-coordinate comparison explain the representation limits.

These results do not improve the complete kappa calculation. No complete
routed caller, terminal decoder, recursive host, finite map cost, or full
precision bound is supplied. Native rank mass is a local invoice. It is not
a multiplication exponent.

Read the [proof and review index](PROOFS.md), the [source record](PROVENANCE.md),
and the [fresh replay receipt](evidence/REPLAY.json).

## The two reader families

| Reader | Euclidean Gram | Representation result |
| --- | --- | --- |
| Original sixteen rows V | diag(12 I8, 8 I8) | A Gaussian-dyadic unitary code needs at least 24 complex coordinates. The actual C24 attains 24. |
| Reciprocal sixteen rows L | diag(10 I8, 7 I8) | A Euclidean-unitary code also needs at least 24 coordinates, by reduction modulo five or seven. A signed-metric code uses sixteen. |

For L, the signed Gram is diag(4 I8, 2 I8). The signed code stores the
rank-sixteen difference E-P. The difference E-I has rank thirty-two.
The physical P is a code on 32 ports, with 160 nonzero entries. It costs
728 real scalar primitives before address-view costs.

The original-reader bound also covers arbitrary borrowed inputs,
nonlinear recovery, and unitary mixing of spatial and owner coordinates.
For arrays of N complex entries, the bound is 24N complex coordinates.
It counts capacity, not names of registers with unrestricted size.
A dyadic-unit output frame and a dyadic orthogonal input frame preserve
the bound. Promised zero inputs, approximate recovery, and general
nonunitary encodings are outside this theorem.

## Exact local words and costs

The standalone C24 code and its adjoint each cost 8052 real scalar
primitives. All eight complete native C24 services cost 16020. A complete
real-component block is treated as one complex-linear frame operation.
An individual component ADD need not preserve that frame.

For the reciprocal readers, C K C^T=G and C^-T=G^-1 C K. The complete
dual conversion includes metric scales on both arbitrary input banks.
The original C transpose violates 32 ordinary support rows. A paid
80-scalar suffix gives the companion Cbar and repairs that support.
Cbar changes the selected coordinates. Recovery of the individual L rows
requires the paid selected-pair code. Only C and Cbar carry L in the sixteen
selected coordinates. Cbar transpose supplies a companion native interface;
its sixteen selected outputs do not decode L.
The raw selected dual of the Cbar-transpose service uses Cbar inverse.
Its metric-converted dual uses Cbar transpose.

| Code | Forward or raw dual scalar cost | Metric-selected dual scalar cost |
| --- | ---: | ---: |
| C24 | 16020 | Not needed |
| Signed C | 9988 | 11252 |
| Signed Cbar | 10068 | 11284 |
| Cbar transpose interface | 10324 | 11156 |

| Service | Q-entry profile | Q-entry mass | I-entry change | I-entry mass |
| --- | --- | ---: | --- | ---: |
| C24 | 1328 H1 + 64 H2 + 48 H3 + 24 H8 | 1792 | Replace 24 H8 by 24 H9 | 1816 |
| Signed code or transpose interface | 1392 H1 + 64 H2 + 48 H3 + 16 H8 | 1792 | Replace 16 H8 by 16 H9 | 1808 |

All duals use the Q-entry profile. Each word acts on 640 arbitrary complex
inputs and preserves the 416 auxiliary roles. The words add no field,
private buffer, CLEAR, or odd division. The signed words have no new
spatial operator; every inherited phase and adapter is bound to its source.
The C24 check also replays eight distinct fresh H8 operators on all 512
spatial columns. Neither result supplies a recursive helper host.

## General signed family

For every k=2^r and n=k+4, the scalar construction gives one centre output
and its metric-orthogonal complement. Its metric and inverse are dyadic.
The exact price in either direction is 86 for r=0, 96 for r=1, and
10kr+76+4r for r at least two. The instruction count is 3kr/2+12.

The proof applies to all r. The checks for k=1,2,4,8,16,32,64 are exact
finite controls. The basis was supplied by the bridge-review lane and
checked by the root lane. The later bridge review checks the root's
word and cost. It is not a second independent proof of its own basis.
No general native row placement is claimed.

## Rational sixteen-coordinate comparison

The first rational unitary C16 packs the original V into sixteen
coordinates. Each complete scalar direction costs 5702 dyadic scalar
primitives, plus sixteen real multiplication-by-three scans and sixteen
real division-by-three scans. Odd scans remain separately priced.
One direction needs ternary height one and local binary height two.
Its complete word must remain contiguous at a common complex frame.

For every positive integer m, h3(C16^m)=h3((C16*)^m)=m. This is a proved
all-power result. The nonzero trace of 3C16 modulo three prevents its
residue matrix from being nilpotent. A fixed dyadic-unit change of basis
or tensoring with an identity preserves the growth. A matched C16 then
C16* pair has prefix odd height one because the inverse word retraces
the first word. This does not give a uniform guard for unmatched calls.

The exact quartet division domain is a congruence modulo three. The
check enumerates all 6561 residue inputs in each direction and accepts
729. The retained root-grid theorem requires a dyadic endpoint on every
role for each completed recursive child. C16 itself has no such endpoint.
All 96 ordinary diagonals of this C16 are nonzero, so this scalar packing
does not have the native realization used by C24. The later supported
packing extension is outside this package.

## Reproduction

Use Python 3.11 or later. No third-party library or network access is needed.
Run from this directory with a new output directory:

```sh
python3 -I -B replay.py --output /tmp/centre-metric-encoders-replay
```

Expected final output:

```text
PASS_CENTRE_METRIC_ENCODERS
```

The runner executes seven checks in normal and optimized Python, in
sequence. It compares each result with the frozen receipt and compares
both Python modes. It checks every immutable source hash before and
after the run. For compressed inputs it checks the decompressed payload
as well as the retained source bytes. It confines each check's file
access to this package, its output directory, and the Python runtime.
The command does not run the archived producer emitters or regenerate
their compressed containers.

The negative controls reject damaged scalar words, wrong metric signs,
omitted target-bank metric scales, wrong dual chronology, wrong global
phases, and an insufficient rational division domain. The review files
state which controls belong to each result. No selected-frontier replay,
Lean formalization, or full recursive supplier check was run.

## Open next questions

A complete signed-code caller must supply route access, saved-record
restoration, and a paid terminal. Start with the explicit local input and
output maps in the signed native review. A count of selected coordinates
does not provide those operations.

A recursive rational boundary type must control whole-state prefixes and
prove decoded child-entry types. Start with the matched C16/C16* case.
The all-power theorem blocks a constant ternary guard for unmatched
repetitions of this fixed C16. It makes no claim about products of
different stage codes.

A general signed-family native construction needs physical row placement
and admissible support for every n=4+2^r. Start with the actual n=6 and n=8
codes. The scalar theorem does not imply those native conditions.
