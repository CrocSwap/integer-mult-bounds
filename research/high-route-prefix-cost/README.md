# Exact linear wrapper bill for complete high routes

The unchanged pooled `route_packet` wrapper adds at most **265 V physical
read/write/unit-move operations** to the complete cube routines it calls.
Consuming and clearing its returned output raises this to **277 V**.
Both constants are sharp over the stated canonical wrapper domain.
The [proof below](#exact-invoice-and-proof) gives an exact invoice, not an
extrapolation from measured ratios.

This answers the prefix extraction, movement and disposal part of PR2968's
released complete-route handoff. It does **not** finish the uniform single-cube
bill, whole caller, bootstrap-stage reserve or supplier admission. There is no
new kappa and no selected-frontier change.

## Contract and sources

Let `C,H,F` be positive integers, encoded by canonical binary Count tapes with
no leading zero digits. The borrowed source contains `C` complete cubes, each
with `H` high records and `F` Boolean payload bits per record. Put `r=H*F` and
`V=C*r`. All borrowed heads start at the canonical origin. The actual selected
shape is `H=Q^(m*m)`, but the wrapper argument does not require that restriction.

Use the retained `ScratchPool.install` and its factory, with initialized blank
roles and enough free inventory for successful execution. A cube call must
preserve its borrowed local source and context, return a distinct owned dense
`r`-bit output, and return both stream heads to their canonical origins. Let
`U_i` be the **entire actual cube-call traffic** for prefix `i`. This includes
its encoded setup, high-bank initialization/erasure, native B1 calls, scaling,
ADD/sign/carry work, intermediate disposal and returned output allocation.
No uniform bound on `U_i` is assumed by the exact identity.

The scientific sources are Jose Manuel/jmbarrancoml's PR2915, author head
`fecc5a87574df441ddc3dad44f99fca9bd7fdd92`, and its frozen PR2899/PR2809/PR2753
and PR2157 dependencies. This package consumes the exact modules and archives
retained on canonical main `47fa55b3cd8c7cf8879206f33569bc59d637dad8`.
[SOURCES.json](SOURCES.json) pins every declared external input. It neither edits
nor substitutes a frozen implementation.

The wrapper is `routes.route_packet` in PR2899's nested PR2809/PR2753 export.
The reached replacement is `high_route.execute` through `stage.Adapter` and
`StagePool`. The proof also uses the retained `stream.Counter`, `copy_bits`,
`copy_rows`, `Tape.rewind/clear` and the pool's one blank read per acquisition.
PR2877's countdown identity and PR2951/PR2968's scaling/pool work are credited
predecessors, not new results here.

The currency counts physical reads, writes and unit moves, including numerical
Word tapes and the native parking controller. It excludes host bookkeeping,
finite-control allocator selection, compilation and initial marker provisioning.
Thus 265 and 277 are **not complete machine-step constants**. The returned native
session is retained for reuse; its eventual enclosing-caller cleanup is separate.

## Exact invoice and proof

Write `b(n)=bit_length(n)` and `s(n)=popcount(n)`. PR2877's fully drained
canonical Counter bill, before its physical acquisition read, is

```text
D(n) = 15*n + 14*b(n) - 5*s(n) + 36.
```

The retained `one_bit_suffix` probe costs `P(F)=4` for even F, `15` for
`F>1` congruent to one modulo four, and `12` otherwise. This follows by
following its early-return reads and rewinds on canonical binary digits.
A payload bit copy costs five operations. For F>1, `copy_bits` also pays
`D(F)+1` for its pooled countdown. Therefore the exact `copy_rows` invoice is

```text
R(H,F) = D(H)+1 + H*(P(F)+5*F + [F>1]*(D(F)+1)).
```

Here and below each `+1` acquisition is the actual pool's blank-marker read,
not an assumed free constructor. The two calls to `copy_rows` per prefix pay
`2R`. The remaining per-prefix work outside the cube routine is:

| Operation | Traffic |
| --- | ---: |
| Acquire the local stream | 1 |
| Rewind it after extraction | `2r+3` |
| Probe the consumed changed stream | 1 |
| Clear changed at its consumed head | `7r+7` |
| Clear the preserved local source at origin | `5r+7` |

Their sum is `14r+19`. Across the whole packet, source and output final rewinds
add `4Cr+6`. Initial source rewind, final source-extent check, output acquisition
and outer Counter acquisition add six more. The complete outer countdown pays
`D(C)`, including its final disposal. Consequently

```text
T_open   = sum_i U_i + C*(2R(H,F)+18r+19) + D(C)+12,
T_closed = T_open + 5Cr+7.
```

The closed interval clears the returned owned output at its rewound head. It
does not dispose borrowed context or preprovisioned permanent inventories.
No cube or native call is multiplied by the prefix count a second time.

### Uniform bound and sharpness

Since `b(n)<=n` and `s(n)>=1`,

```text
D(n)+1 <= 61n                   for n>=1,
D(n)+1 <= 45n                   for n>=2,
D(C)+12 <= 72C.
```

The second bound follows from `D(n)+1<=29n+32`. Thus:

- For F=1, `R<=78r`.
- For F=2, the exact `P(2)=4` and `D(2)+1=90` give `R<=165r/2`.
- For F>=3, `R<=(50+76/F)r<=226r/3`.

The open wrapper bill per prefix is at most `2R+18r+91`. For F=1 this is
at most `174r+91<=265r`. For F=2 use `r>=2`, giving at most `457r/2`.
For F>=3 use `r>=3`, giving at most `199r`. Hence

```text
T_open   <= sum_i U_i + 265V,
T_closed <= sum_i U_i + 277V.
```

At `C=H=F=1`, the exact wrapper invoices are 265 and 277, respectively.
An actual Q=1 reduced route attains both in the controls. Sharpness concerns
this wrapper/currency/domain, not a minimum implementation cost or a selected
stopped caller's attainable parameters.

If every cube has a proved tariff `U_i<=G*r`, the full packet therefore costs
at most `(G+265)V`, or `(G+277)V` with output disposal. Unknown single-cube
charges have not become zero. For equal complete cube traces, the exact useful
cross-check is `T(C)=C*(T(1)-D(1)-12)+D(C)+12`. Equal traces are checked in the
finite fixtures, not assumed for an arbitrary substitute cube routine.

## Replay and measured evidence

From the repository root, with standard-library CPython 3.12 or newer:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/high-route-prefix-cost
```

The primary command authenticates inputs before loading complete source modules.
It replays 44 complete reduced routes, 125,689 payload bits and 1,314 actual
native B1 calls, with direct q-adic affine-matrix endpoint checks. Cases include
Q=1,3,5,9, forward/inverse noncommuting words, suffixes 1/3, prefix counts through
17, and complementary payloads. Native calls take the **elementary** B1 branch;
no fitted selected GL64 payload execution is claimed.

The observer counts raw physical Tape methods once, and adds the native
controller's non-Tape operations. Each complete interval must also agree with
the sum of unique physical-object meters. Word/Lease alias meters are not added
again. Native and cube interval snapshots are entry-relative, excluding earlier
initialization. The observer attaches to the stable adapter method because
`StagePool` reinstalls the route alias after every native return. The checker
requires exactly C observed cube intervals, not merely C reported outputs.

For q=3, w=2, F=1, the complete one-prefix route costs **438,000** operations.
Its cube costs 431,027, including 154,884 inside six actual native calls. The
wrapper costs exactly **6,973**. Three prefixes cost 1,313,895, or 1,315,117
including output disposal. Full typed records are in [RESULT.json](RESULT.json).

The controls independently exercise 256 pooled countdowns and 121 complete
`copy_rows` calls. They check the sharp bounds on 32,768 triples and the actual
attaining route. An endpoint-preserving mutant adds C redundant reads outside
each cube call. At C=3 it adds nine operations, which the invoice rejects.
A noncanonical extra zero in the prefix count preserves the endpoint but adds
14 operations, demonstrating why the canonical-input premise matters. Semantic,
source, missing-declaration and typed-receipt corruptions also reject.

The registered normal/optimized CPython 3.12.15 replay passed locally on Linux
x86_64, as did the 13 optimized control groups on CPython 3.13.5. The repository
workflow suite passed 158 tests with 11 platform skips. Ruff checks and formatting
passed. These are local results, not hosted CI evidence.

These are finite corroborations of the written wrapper proof. The endpoint
patterns are not a new independent-column census. Complete cold supplier replay,
formal-kernel verification, independent human review and hosted CI are separate.

## Implementation bounds

The new harness has no recursion. Fixture prefixes are at most 17, widths at
most three, and total payload at most 100,000 bits. Source inventories have at
most 64 rows, at most 32 MiB per file and at most 64 MiB total. The managed
Python runtime allocates within those fixture limits; it is not the proposed
fixed-tape multiplication machine. Existing source inventories and routines are
left unchanged. All new functions fit within 60 physical lines.

Dynamic loading and temporary method replacement are confined to the five
explicitly authenticated source modules and finite observer targets. They are
needed to run the exact frozen implementation and observe physical operations,
not to alter its arithmetic or loops. Context managers restore methods, successful
outputs and fixture resources are explicitly released, and both source loaders'
temporary exports are explicitly cleaned. General source failure recovery remains
outside the inherited successful-execution contract.

The registered replay enables Python warnings as errors. Local diagnostics use
`ruff check --select E,F,I,UP,B,SIM` and `ruff format --check`. A whole-repository
static typing migration is not part of this dynamic-source audit.

## Open next questions

1. Prove a uniform **single-cube** invoice for the reached source. Start with
   encoded extent/high-bank setup and ordered high-field ADD, then compose the
   already audited sign/scaling and complete B1 tariff. This matters because
   the wrapper theorem only lifts those costs. The all-width native and source
   contracts remain dependencies.
2. Compose a complete machine-step and storage ledger. Start with fixed pool
   selection, marker provisioning and native inventory reuse at common cuts.
   The exact I/O bill does not price finite-control transitions or establish a
   whole-stage reserve coefficient.

The decision is to finish this independent wrapper audit, not expand the
construction family. [TASK.json](TASK.json) records the changed task scope,
coordination and upstream freshness.

## Credit

Jose Manuel/jmbarrancoml supplied PR2915's route/adapter implementation and
PR2899/PR2809 physical compositions. David Arias supplied PR2753's logical
caller. Arham Tahir supplied PR2877's shared countdown identity. PR2951/PR2968
supply the earlier scaling and pool invoices. The PR2157 factor words and
DreamingOfClouds' selected PR589 work on eumemic's base retain their source
attribution. PR2708's `selected-route-live-volume` proves a separate storage
bound for the older decorated-key cube, not this I/O tariff. No predecessor
implementation, storage bound or countdown identity is claimed as new. This
package adds the exact wrapper invoice, sharp linear constants
and independent complete-route cost partition.

Nick Petalas. Apache-2.0. Substantial automated assistance; no independent
human review is claimed.
