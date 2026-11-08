# Actual Full programs on a complete global tensor field

**Source-bound compiler, numerical and physical-service composition. No new κ.**
The package connects actual Full programs to one complete tensor field,
including encoded coefficient pages, exact scalar arithmetic, the physical
H boundary, input admission and owned scratch restoration.

The actual `FullRoot.lower()` programs in #4253 have coefficient-dependent
depths. A fast complete-array H service cannot be inserted independently into
each small Full field: its global address/precision domain must also hold.
This package prepares the actual forward or stored-inverse programs across
all axes and coarse labels, adds complete compiler-generated identity layers,
and emits one synchronous word of whole-field H masks and product diagonals.
It separately funds a new global rounded execution of that word. The physical
consumer executes the emitted events from encoded tapes, preserving the
same global rounding semantics.

## Exact result

For K complete coarse labels, g axes and common Full side N=2^m>=2, let L be
the largest actual logical depth. The emitted word contains exactly
`L(8m+2)` global H requests and `L(8m+3)` global diagonal requests. It acts on
all K N^g records, including arbitrary correlated input vectors. Its exact
reference is the direct sum of tensor products of the original stored Full
plans. Stored inverses use their source gates and exact reciprocals.

[PROOF.md](PROOF.md) gives explicit preparation targets, raw-prefix bounds,
factor/data precision, internal word widths and a complete symbolic service
invoice. For an admitted input with whole-field radius R and target 2^-t,
the source error is at most 2^-t/8 and the new arithmetic error at most
2^-t/4. Every padded diagonal rounding is included. Exact raw-H returns stay
on the common grid; their internal widths and physical costs remain charged.
[PHYSICAL-PROOF.md](PHYSICAL-PROOF.md) binds those events to the unchanged
exact word service and the source-owned #3627 H boundary. Input radius
admission uses actual physical magnitude squares; intermediate payloads are
not decoded into host lists between stages.

This statement does not tensor nonlinear local rounded trajectories. The
source preparation, exact tensor reference and globally rounded arithmetic
are distinct objects, compared by separate checks.

## What is new and what is inherited

#4178, `research/gaussian-height-contract/CALLER.md`, already establishes
cached tensor coefficients, a generic exact C/H caller, a global error
allocation and O(p) word bounds. Its examples use hand-built matching layers;
they do not consume actual Full roots or synchronize coefficient-dependent
Full depths. Those generic cache and height lemmas are credited premises.

#4205/#4253 supply the actual Full plans, stored inverse, exact prefix
accounting and fixed H lowering. The new binding verifies their raw pages,
generates genuine complete empty layers through their unchanged compiler,
and connects source endpoint defects to the common global precision. The
separate direct semantic oracle is not a physical tape implementation.

The physical diagonal uses #3709's exact all-width Karatsuba
word engine. Its complete scalar cost, including recursion-frame movement,
fits within the global H bill when
`beta*.99827101>log2(3)-1`; for example beta=.975 has a strict margin.
[PROOF.md](PROOF.md), Section 6.1, gives the full conditions and retains
source preparation and H-service premises. This avoids adding a scalar FFT
approximation or scalar recovery hypothesis to this particular composition.
The full diagonal term remains explicit generally. In particular this
Karatsuba choice does not supply a fast diagonal tariff for an outer caller
whose grouping exponent is below the stated threshold; the example is not
an outer parameter retuning.

The complete physical bill includes source preparation, all-stage control
encoding, native-owner construction, radius admission, four exact real word
products per complex product, truncation, page movement, return consumption
and cleanup. Its control storage and historical blank backing remain explicit.
The physical suffix producer expands one axis at a time in the correct digit
order, using fewer than two coefficient products per final record, without
assuming random access or one tape per axis.

The canonical source base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Every retained source and proof
dependency is listed with Git blob and SHA256 in [SOURCES.json](SOURCES.json).
The selected record and task catalogue are historical provenance only;
later priority changes do not substitute source bytes.
[PHYSICAL-SOURCES.json](PHYSICAL-SOURCES.json) also pins the two byte-identical
boundary files from the public source-owned H contribution at
`271f1d4c3128a89d49694e7508c1c88bba8cc981`. One authenticated Count/Tape cohort
serves both physical children; preloaded scalar aliases are rejected.

## Reproduce

From the repository root, with Python 3.12 and `sympy==1.13.3`:

```sh
python3.12 -B scripts/research_package.py --package research/full-global-tensor-caller
```

The registered commands execute the source check, physical controls and
complete physical Full fixture in both ordinary and optimized modes. Expected
markers are `PASS_FULL_GLOBAL_SOURCE`, `PASS_PHYSICAL_FULL_CONTROLS`,
`PASS_PHYSICAL_FULL`, and the runner's `PASS_REGISTERED_RESEARCH_PACKAGE`.
Each individual source and physical command was executed successfully in
both modes before integration. The physical code and its companion Full
source bytes were authenticated against the frozen handoff before copying.
The integrated manifest adds only six already-authenticated physical input
pins; [PHYSICAL-RECEIPT.json](PHYSICAL-RECEIPT.json) retains the exact earlier
manifest hash rather than relabelling that inventory as already replayed.

The fast source-only command is
`python3.12 -W error -B research/full-global-tensor-caller/verify_source.py`.
It returns deterministic receipt SHA256
`87b1b2c58ef8d64f5b18492abde9d68c86d6456dbb6fafbf156a40bc2b0c4944`.
[SOURCE-RESULT.json](SOURCE-RESULT.json) records three actual source families,
11 input trajectories, 1,918 H requests, 2,109 diagonal requests and 1,351
observed nonzero roundings. These are finite witnesses, not substitutes for
the all-size argument.

The heterogeneous family has two labels, two axes and local depths 21, 21,
1 and 21; all eight global basis vectors and one correlated complex input
are checked. Its complete schedule has 441 stages at the conservatively
allocated 1,007 fractional bits. Separate cases preserve a 16,384-bit incoming
grid and exercise the global masks `(0,2)` and `(1,3)` at side four.

Each trajectory compares four independently organized calculations: the
emitted rounded word, the exact emitted primitive word, the original stored
logical plans, and an exact rational root/inverse calculation. The latter
uses a separate Gaussian elimination implementation. Twelve controls include
wrong coarse routing, missing H normalization restoration, wrong label
pages, fake all-one identity padding, an underfunded grid, a changed source
page or direction, a violated input radius, lost incoming precision, and
changed retained source bytes. Trusted exact preparation temporarily permits
arbitrary-size integer serialization for the inherited hashes; it restores
the prior process-wide CPython digit guard on both success and failure.
This addresses a concrete 16,384-bit input-grid preparation edge without
changing arithmetic, event formats or existing hash formats. The source and arithmetic error bounds are
checked separately before the combined root target.

## Actual physical evidence

The complete actual Full fixture is the stored inverse of `(2+i) I_2`, with
target 8, incoming grid 0 and whole-field radius 2. The source allocation
remains F407/W608. All 21 emitted stages execute physically: ten H calls and
eleven complex diagonals, with 92 exact real word products including input
admission. The output agrees with the separate source oracle, satisfies the
root-error target, preserves borrowed tapes and restores owned scratch.
Normal and optimized executions took approximately 202 and 257 seconds in
the recorded environment. These timings are feasibility evidence, not an
asymptotic bound.

This actual Full fixture has nonzero source approximation error but zero
nonzero stage truncations, because its prepared coefficients are dyadic on
the allocated grid. A separate physical service fixture supplies the missing
rounding/ordering evidence: three axes, two labels, two successive nonconstant
complex diagonals, zero factors and 40 nonzero fresh-reference roundings.
Those pages are explicitly service fixtures, not relabelled Full output.

Six physical endpoint/radius mutants reject, including wrong label, wrong
axis, stale stage pages and premature coefficient/data truncation. Fourteen
private-port alias guards, protected-output reuse, successful owner reuse,
scratch restoration, observer erasure and three preloaded-module controls
are checked. The actual scalar child is WordProduct at every width; it never
calls FftWord, RingProduct or a scalar FFT. Its full integer return is consumed
before component truncation.

[PHYSICAL-RESULTS.json](PHYSICAL-RESULTS.json) contains the complete results;
the ordinary and optimized outputs agree after removing only measured elapsed
times. The source-only checker still accurately reports
`physical_service_executed: false`; the separate physical check establishes
the physical evidence. The H fixture uses the declared reduced q2 source
binding and a certified finite specialization of two metadata floor helpers.
Unlisted helper arguments delegate to the unchanged routine. This does not
execute a production native or prove a long-field rate.

## Scope

The accelerated H tariff applies only under its own
global `n=Theta(P)` and `g<=P^.997` conditions. A small finite source witness
does not establish those asymptotic conditions. The full outer Gaussian,
core/halo and exact integer recovery interfaces remain separate. Neither
the selected certificate nor any global multiplication exponent changes.
The universal claim is the written source-relative proof, with the inherited
exact-integer, H-native, stock and ownership premises explicit. The finite
checks are corroboration, not an all-size proof or formal-kernel acceptance.

## Open next questions

The concrete next questions, also recorded in [TASK.json](TASK.json), are:

- Bind one admitted outer Gaussian/Toeplitz cohort and its actual source
  preparation cost to the global service. A favorable grouping exponent is
  not an outer admission proof.
- Supply an exact faster scalar option where small grouped dimension makes
  the explicit Karatsuba term binding, preserving the same encoded lifecycle.
- Replace all-stage controls with a priced stage producer if constant-axis
  space matters, while preserving coefficient-page provenance and rounding.

## Credit

Prepared by @CubeJerry with substantial OpenAI Codex assistance in source
analysis, mathematics, implementation, verification and writing. Credit
Jose Manuel/jmbarrancoml for #4205/#4253/#4178 and the Full numerical compiler;
the retained Chafik Boukhalfa/#628 and Vlado Vojdanovski/#1673 lineage remains
credited in the source notices. Credit #3709 for the exact word engine,
#3627 for H/support composition,
and the source-owned H boundary linked in [PHYSICAL-PROOF.md](PHYSICAL-PROOF.md).
Coordinated AI cross-review and independently organized arithmetic checks
are part of the author process, not independent human acceptance. New work
is Apache-2.0; inherited notices remain unchanged.
