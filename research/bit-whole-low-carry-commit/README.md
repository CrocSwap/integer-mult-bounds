# Complete low-domain carries followed by physical low commit

This package constructs a literal fixed-tape program that applies **every
coordinate carry to every complete low-type fiber**, then runs the existing
physical low permutation and retires the old cache after its final consumer.
It binds that construction to the actual frame506 matrix in #4989, in both
source directions. For fixed dimension N and fixed odd prime q, the complete
transition and visited-cell bills are linear in the supplied full payload
volume. **No new κ.**

The result is one complete **supplied-ABI component** of the BIT route. It
does not execute the separate homogeneous high-coordinate action, construct
the literal selected caller's required tape order, or admit its physical
dispatcher at the selected tariff. The accepted frontier and all predecessor
files remain unchanged. Canonical base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Exact result and scope

Fix s>=1, N=8s, D=N² and q before runtime. From the pinned frame506 form
`S8 = transpose(frame['B'] + frame['A'])`, with the source's exact right-action
convention. Choose `M=S8 tensor I_s` or its rational inverse. Let
`T=|GL_N(F_q)|`. Runtime Q is any positive odd integer and Z is any positive
integer, supplied as canonical binary descriptors. The complete owner has
V=TQ^D Z arbitrary bits in the exact order

```text
(lexicographic low matrix G0, row-major high[0], ..., high[D-1], trailing z).
```

This is the full-array ABI of #5487, not a sparse list of occupied records.
Every high coordinate independently ranges over [Q] and the complete trailing
coordinate ranges over [Z]. The source specialization is Q=q^(w−1).

Define `pi_M(G0)=G0 M mod q`, using canonical low digits, and
`C_M(G0)=(G0 M_mod(qQ)−pi_M(G0))/q mod Q`. The program executes the push
permutation

```text
B_M: (G0,H,z) -> (pi_M(G0), H+C_M(G0) mod Q, z).
```

It returns the original physical owner, preserves every supplied descriptor
and unrelated spectator tape/head, and erases every private tape back to its
entry origin. Wholly blank, distinct private tapes are an entry precondition;
the program does not certify an infinite blank tape by reading one cell.

The negative source-direction flag computes **B_(M^-1)**. This is generally
different from **(B_M)^-1**. To implement the complete source right action
`G -> GM`, first execute the separate homogeneous action `H -> HM` and then
B_M. Both source directions use the positive physical carry rotation; a
negative carry has already been reduced modulo Q.

N, q, s and T are compile-time constants. A growing runtime column width
cannot be hidden in them. Additional runtime columns or spectator tuples may
be flattened into Z only when that complete contiguous layout is already
supplied. The literal selected caller's layout conversion and source access
remain open. The program is finite but may be enormous when N=8s; practical
compilation of the full GL8 domain is not claimed.

## Construction and complete accounting

The unchanged #5487 initializer writes the full old-low cache in the same
order as the source fibers. At Q=1 the program runs the actual low commit and
cache retirement directly. Otherwise it produces unary Q and Z loop controls,
the full fiber extent H=Q^D Z, and a T-type loop from the supplied descriptors.

For each low type it stages the entire H-bit fiber, copies that type's old
low digits, and retains them through all D coordinate consumers. For each
coordinate a it physically produces binary `P=Q^a` and
`S=Q^(D-a-1)Z`, executes the unchanged #5332 cache-to-carry frontend, and
rotates the complete `[P] × [Q] × [S]` stream using #5849. Coordinate zero
uses this same genuine complete-stream operation: there is no dummy Q axis,
free callback or OLD interchange. Every leaf's descriptor and scratch output
is erased. The transformed fiber is installed into its original parent
location and its staging tape is consumed and cleared.

Only after all T fibers have completed does the program call #5487's actual
full-array low commit. The global old cache survives that program's input
validation and is retired after the completed output is installed. The proof
therefore closes the full last-consumer sequence, rather than inferring it
from one successful leaf.

`PROOF.md` derives every added loop, copy, rewind and cleanup cost. Its
positive complete invoice is evaluated in `bounds.py`, including the retained
decoder, rotation and low-commit bills. For K=TDb, b=ceil(log2 q), it bounds
visited cells by

```text
64(D+1)V + 8K + 512(D+1).
```

Both transitions and visited cells are O_(N,q)(V). In particular, binary
products are produced by literal increments: at most 7r+10 transitions for
r trailing ones, including the physical rewind. Summing r over P increments
gives less than P. Nested unary-loop rewinds are also charged, giving at most
10kP loop transitions for k counters with product P. The bound hides neither
a logarithmic increment cost nor a free arithmetic operation.

All emitted instructions are scanned-symbol branches, single-symbol writes,
unit head moves, fixed jumps, halt and reject. The finite program has D+26
tapes. Compilation accepts no runtime Q, Z, payload or host-selected carry.
The generic reduced-fixture compiler additionally requires the retained
decoder to accept every reachable aggregate; support and a coefficient norm
bound alone do not suffice. The actual source's exact positive/negative
column envelopes prove that admission for all odd q.

## What is new, and predecessor relationships

| Contribution | Established mechanism and relationship |
|---|---|
| #4989, `research/bit-row-route-generator/` | Exact frame506 addressed source, right-action factor word and cache/carry/commit order. Its primitive callbacks remain inherited contracts. The present package physically implements the complete supplied-ABI carry/commit suffix. |
| #5332, `research/bit-low-carry-lowering/` | Physical old-low decoder and quarter-offset descriptor producer. Imported unchanged; not claimed anew. |
| #5487, `research/bit-full-fiber-low-commit/` | Complete low-domain payload permutation, original-owner installation and cache retirement. Imported unchanged. This package supplies its preceding whole carry stage and proves the cache join. |
| #5849, `research/runtime-quarter-carry/` | Literal in-place quarter carry for every coordinate, including coordinate zero. Its 393H generic transition and 43H visited-cell bounds are retained. |
| #5985 | Q=1 is a low-only branch. That observation is credited, not a new lemma. |
| #6241 | One physical port-nine cache-to-carry consumer and explicit source-PC/tape translation. The present compiler credits that translation and applies it to all D coordinates of all T fibers. |
| #6296 | New-low output and cache-boundary gate. The current complete loop establishes when the last local and global consumers actually finish. |
| #6467 | Shorter factorization of the identical S8 matrix. It changes the separate homogeneous word; the present source-bound carry matrix is unchanged. |
| #6474 | Logical interleaved G20 producer for a distinct source family. It is neither imported nor treated as a physical frame506 producer. |

The novelty is the **executed whole-domain join**, including generated
runtime extents, staging and reinstallation, exact old-cache lifetimes,
direction-sensitive source binding, and a complete all-parameter bill.
It is not a new scalar tensor identity, another width-one adapter, or a
conditional wrapper that accepts the missing operation as a callback.
The broad supplier framework in #4760/#4814 and #4957 remains conditional;
#4359's finite compiler closure does not itself supply this physical stage.

At the scope checkpoint, #6467 and #6474 were open at
`8c7a406f60de96ef51af13ecf01ff4e4dce7fa35` and
`63c65d845d84ae47fa8264c48c289e55c44cdc76`, respectively. They are credited
comparisons, not imported dependencies. Every input used by this package
comes from the pinned canonical base and is listed in `SOURCES.json` and
`VERIFY.json`.

## Reproduction and executed evidence

From the repository root, Python standard library only:

```sh
python3 -I -B research/bit-whole-low-carry-commit/verify.py
```

Expected final marker:

```text
PASS_BIT_WHOLE_LOW_CARRY_COMMIT {"complete_low_types": 48, "controls": 10, "kappa_changed": false, "literal_tables": 2, "positive_cases": 18}
```

Run the registered normal and optimized replays with:

```sh
python3 -B scripts/research_package.py --package research/bit-whole-low-carry-commit
```

`RESULT.json` is deterministic. `--write` regenerates only that new receipt.
Normal replay requires its exact equality, including regenerated literal
program digests, complete endpoint digests, transition/space observations and
every control. The package authenticates source Git blobs and SHA256 hashes
before execution. Retained modules are compiled from authenticated bytes;
predecessor source files are neither copied into this package nor modified.

| Check | Completed scope |
|---|---|
| Literal complete low domain | All 48 GL2(F3) types; four high coordinates |
| Runtime shapes | Q=1 and 3; complete trailing Z=1 and 2 |
| Source orientations | Both M and M^-1, with the precise B_M meaning |
| Payloads | Seed 12 arbitrary complete bits; additional all-zero and all-one extremes |
| Complete local executions | 18 cases, including both independent sparse/dense instruction engines |
| Literal instruction tables | 73,054 forward and 73,702 source-inverse instructions; 30 tapes each |
| Largest payload | 7,776 bits, with every returned cell and head checked |
| Largest observed cost | 4,390,766 transitions and 16,789 visited cells |
| Lifetime boundaries | Every one of 48 fiber entries and local-cache last-use points, plus the full cache before commit |
| Actual source binding | Fixed s=1,2,3; q=3/5; w=2/4; 1,920 carry occurrences in the original addressed schedules |

The dense engine is a separate retained implementation. Only its fixed-tape
schema count is set to the new program's tape count; its opcode semantics
remain unchanged. Its exact transition counts and visited spans agree with
the sparse engine on each common fixture. The payload oracle independently
enumerates GL2 using the determinant and computes the whole push permutation
directly modulo qQ, without calling the emitted decoder or type compiler.

Source checks bind transpose(B+A), tensor lane order, the exact inverse,
all original row-major carry events, their order before commit/clear, and
the complete homogeneous-plus-carry algebra. The old source interpreter is
an operational-contract check, not a physical implementation of its remaining
callbacks. **The full GL8 payload is not executed.** The all-size component
claim follows from the written invariant and cost proof, with finite replay
corroborating the implementation.

Ten controls detect changed source bytes, a wrong old-cache block, premature
low commit, reversed carry rotation, early local-cache erasure, omission of
coordinate zero, aliasing the carry owner with its parent, omitted payload
installation, and the wrong low permutation direction. The tenth is an
endpoint-preserving extra-work mutation: it adds exactly two observed
transitions and changes the literal table. This detects count drift; it is
not falsely described as violating the deliberately loose upper bound.
Semantic mutants run modified literal programs, so their rejection is not
merely a source-hash mismatch.

## Open next questions

Structured versions and stopping rules are recorded in `TASK.json`.

1. Supply this complete low/high/trailing layout from one literal selected
   caller occurrence, with source access, conversion and reverse conversion
   fully charged. Runtime trailing flattening is useful only after this
   physical presentation obligation is established.
2. Lower the whole homogeneous high-coordinate action onto the same ABI,
   including earlier-target ordinary interchanges and complete returns.
   Then compose it with B_M and the opposite complete source route. The
   carry map alone does not furnish that inverse pair.
3. Bind a finite compiler's fixed blocks to these machines while keeping
   N,q and any varying column width distinct. Price the finite construction
   threshold and every inter-block layout transfer before claiming a
   selected-rate dispatcher or stronger multiplication bound.

## Attribution and license

Prepared for **@CubeJerry**, with substantial **OpenAI Codex** assistance in
research, construction, proof, implementation and adversarial review. The
lead reviewer checked the loop/rewind costs, full source-direction algebra
and ownership composition. A separate research worker used independent
rational/modular calculations and reviewed the all-size proof. These are
AI-assisted reviews, not independent human or proof-kernel acceptance.

Credit JoyboyBrian for #4989/#5332/#5487, Ali Romman for #5849, David Arias
for the literal machine and #2776 lineage, AAAmirinu for #6241's explicit
translation, unpaidmoon for #6296, and Nick Petalas for #5985/#6467. Credit
the #6474 authors for the distinct G20 arithmetic and all earlier supplier,
ordinary, ROW and native constructions rather than claiming their mechanisms
again. Apache-2.0, following the repository license.
