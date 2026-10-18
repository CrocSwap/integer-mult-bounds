# R439 B509: the unchanged source still must reach rank four

**Independent certificate of a scoped negative result; no new κ.** Source register 22 in the fixed R439
phase-B block at frame 509 cannot remain in any proper subspace of that
rank-four frame. This holds for arbitrary finite exact resyntheses on the
original 11 wires, with monotone rational frames inside F509. It is not
limited to the existing frame catalogue or a bounded circuit length.

[PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368), by Arham
Tahir, left this case open: forward dependencies force ten wires to rank four,
but register 22 ends unchanged and only forces rank two by that test.
The missing constraint is its **inverse column**, whose support is

`[17, 22, 33, 38, 77, 87, 468]`.

Registers **17 and 468 already enter on F509**. Either one forces register 22
to reach F509 as well. Every original wire therefore exits on F509, and the
current frame bill of **7 rank-two children + 2 rank-three children** is minimal
in the stated class, for every supplier exponent `0 < a < 1`. Fewer scalar
XORs can still be useful; this result excludes a cheaper frame itinerary at
this fixed interface and fixed external charges.

## Exact object and evidence

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
The selected result at that base is conditional κ = **0.001672660197076918**,
PR1094; its bit supplier is PR589 on PR555. The complex side binds. The selected
record and every predecessor package are unchanged.

The wire order is `[17,22,33,38,50,60,67,77,87,92,468]`. Entry frame IDs are
`[509,182,185,188,52,62,192,186,189,184,509]`, with dimensions
`[4,2,2,2,1,1,2,2,2,2,4]`. The block-entry variables are arbitrary: the complete
scalar prefix is invertible, so the argument assumes no clean sources/helpers.

| Pinned fixture | B509 slice (zero-based, end excluded) | B509 XORs | Whole-word ADDs |
|---|---|---:|---:|
| Selected PR589 word | `B[283:314]` | 31 | 24,305 |
| PR1062 block composition | `B[224:245]` | 21 | 11,515 |
| PR1062 composition plus admitted stars | `B[224:245]` | 21 | 11,500 |

All three have the same block matrix, inverse, entry frames and 661 ordered
register frame paths. The separate Boolean implementation evaluates all
**2,048 inputs per block**, including arbitrary helper dirt. Rational row
reduction and a separate integer Gram-minor calculation agree on every
footprint. Roots `[17,22,33,60]` give a rank-four witness with **integer
Gram determinant 64**. The full matrix and footprints are in
[CERTIFICATE.json](CERTIFICATE.json).

The primary replay also checks all **661 scalar columns in both directions**,
literal cleanup, every nested frame climb, and nine rank-seven COPY charges
for each complete word. It recovers the inherited profile
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`, rank mass **5,129**.
Scatter is replayed as its exact additive map; this is not a native COPY/ERASE
or physical-address replay. The independent implementation checks the block
maps, entry labels and rank/cost witnesses, not that complete word replay.
Both implementations were written by the same assistant session.

## Proof: inverse columns constrain frames

Let the block-entry data be a column vector `u`. At an intermediate point the
values are `z = P u`, with P invertible over F2. Let S_j be wire j's entry
frame and F_i its current frame. Two invariants hold:

1. If `P[i,j] = 1`, then `S_j ⊆ F_i` (forward row dependence).
2. If `P⁻¹[j,i] = 1`, then `S_j ⊆ F_i` (inverse column dependence).

Initially P is the identity and both hold. Monotone frame moves preserve
them. For an invertible scalar operation T on wires J at common frame F,
the new matrix is `T P`. Its affected rows combine old rows indexed by J.
The new inverse is `P⁻¹ T⁻¹`: its affected columns combine old columns
indexed by J. Every such old row and column has its required entry frames
inside F, because all operands have reached the common frame. Cancellation
can remove support but cannot introduce a donor outside F. Other rows and
columns are unchanged. This proves both invariants for every finite length.

Any exact implementation of the prescribed block matrix M consequently has
the necessary exit condition

`S_i + Σ_{j:M[i,j]=1} S_j + Σ_{j:M⁻¹[j,i]=1} S_j ⊆ F_i(exit)`.

The S_i term records monotonicity even if that coordinate cancels. The inverse
index order matters: **column i**, not row i. For source 22, the forward row
and inverse row are both identity and miss the obstruction. The inverse
column includes 17 and 468, whose entry frames equal F509. Since every
permitted operation frame lies inside F509, source 22 must end exactly there.
The certificate supplies rank-four forward footprints for the other ten
wires and checks the combined footprints for all eleven.

This invariant adapts the two-sided monotone-frame idea in Ali Romman's
[PR1128 proof](https://github.com/CrocSwap/integer-mult-bounds/blob/df29b159239b79d7e451d6ddda826a73e0e50a67/research/bit-width-seven-boundary/PROOF.md).
That method and PR1368's forward-dependency/concavity argument are predecessor
work. The final overlap refresh also found Andrey Mas's
[PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511), which gives
the same general inverse-column invariant and applies it to B508/source19,
followed by [Discussion1515](https://github.com/CrocSwap/integer-mult-bounds/discussions/1515)
claiming its B509/source22 corollary. This package adds a source-bound B509
certificate across three words, a separate Boolean/integer-minor implementation,
full scalar/frame recounts and package-corruption controls. It claims neither
priority for the invariant/corollary nor a different mathematical method.

## Complete frame bill and outside boundary

A wire entering at dimension e and forced to exit at dimension four makes
positive dimension increments d_j summing to `4-e`. For `q=1-a ∈ (0,1)`,

`Σ d_j^q ≥ (Σ d_j)^q = (4-e)^q`.

Divide by the positive total and use `t^q ≥ t` for `0 ≤ t ≤ 1`; the inequality
is strict when two increments are positive. The old program already makes
one climb per wire needing one. All eleven wires, including the two rank-one
entrants and two already-full entrants, are counted: **7H2 + 2H3**, rank mass
**20**, nine nonzero children. The common positive normalization factor
preserves the inequality. Splitting cannot reduce the number of children or
a fixed nonnegative per-child surcharge either.

Every wire is essential to M (a nonidentity row or column), so an exact
same-wire replacement touches every wire. With all exit frames fixed at
F509, the untouched continuation starts in the same scalar and frame state.
Regenerating the replacement's literal inverse at the full rank-eight cleanup
frame still touches every wire there; repetition at that frame adds no climb.
The scalar cleanup work remains payable. Retained copies, other source access,
helper inventory, hosting, precision charges and the rest of the invoice are
held fixed. This does not exclude changing those contracts or crossing blocks.

The conclusion concerns the **frame part of the completed bill**. It does not
claim 21 is the shortest scalar circuit or that all replacements have the same
histogram: split climbs can change the histogram and worsen its moment.
There is no synthesis search or search-exhaustion claim.

## Reproduce and controls

Python 3.12, standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/r439-b509-inverse-footprint-seed19
```

Expected output includes:

```text
PASS_R439_B509_INVERSE_FOOTPRINT fixtures=3 exits=11 source22=2->4 block_climbs=7H2+2H3 controls=8 no_new_kappa
PASS_INDEPENDENT_B509 Boolean_inputs=2048 fixtures=3 Gram_determinant=64 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/r439-b509-inverse-footprint-seed19 outcome=negative-result
```

The registered replay runs both engines and seven tests under optimized Python.
Eight direct controls reject rank-two and rank-three source exits, an omitted
gate, reversed gate directions, a missing inverse donor, frame descent, source
dirt leakage and a dependent rank witness. The rank-three control uses the
**unlisted** rational span of roots `[17,22,33]`. Both smaller-exit controls
pass the weaker forward-row test; the inverse-column condition rejects them.
An identity and a genuine rank-one XOR are positive controls against blindly
rejecting smaller frames.

Tests run both scripts in a relocated temporary checkout and reject four real
package corruptions in both engines: a missing inverse term, understated
carrier bill, false rank-three receipt and changed source bytes. Actual-word
controls also reject a lower-frame gate and a cancelling cleanup pair that
preserves the binary endpoint but violates literal cleanup. No predecessor
check is disabled. Default replay is read-only; `verify.py --write` regenerates
only this package's certificate.

## Sources, coordination and limitations

[SOURCES.json](SOURCES.json) records Git blobs and SHA256s for all three live
inputs and historical selected/catalogue provenance. Separate context entries
pin PR1368 at `6ae784908c57f3aa5a2165d382b21a40accdf7a6`, PR1128 at
`df29b159239b79d7e451d6ddda826a73e0e50a67`, and concurrent PR1511 at
`f247c4e17b19e55c0db0ec8a1b660fd118adf014`. These context documents are credited
references, not imported implementations or newly accepted upstream results.
No pending-PR file is required for execution.

OS assignment seed **19**, bit-supplier track. [TASK.json](TASK.json) records
three candidate tasks, the scope, stop rule and overlap coverage.
`19 mod 2 = 1` selects B509 from the two exceptional blocks. Semantic-D and
one-relation-register suggestions already had work in PR1194/1311 and
PR1454/1456. This package uses the `scalar-to-moment` card within the user's
bit-track assignment. The adjacent B508/source19 investigation in
[Discussion1470](https://github.com/CrocSwap/integer-mult-bounds/discussions/1470)
is credited; B508 is not replayed or separately certified here. The final
02:08 UTC refresh discovered its published PR1511 and the same-object claim
1515, begun while this locally claimed package was in verification. A final
02:17 UTC check found the cited PR heads and upstream main unchanged; Discussion
1515 still contained the claim, with no posted result. This package's added
evidence and absence of a priority claim are recorded above. PR1221/1344/1359
concern a different smaller scalar endpoint, not this 11-wire boundary.

Live overlap checks use public HTML PR bodies/searches and discussion pages,
plus the offline repository helper and ledger. Coverage is partial: API/posting
access is unavailable, there is no complete remote cache, and no match is not
proof of novelty. The claim and result are recorded locally.

The mathematical domain excludes extra wires, COPY/ERASE inside the replacement,
noninvertible operations, frame descent, frames outside F509, changed entry
states and cross-block rewrites. This is a written scoped proof with finite
corroboration, not proof-assistant verification. Native multistage replay,
full hosted emission/invoice, all-size/common-label/mutable-source realization,
precision/tape and analytic transfer are not established here. PR1062's known
semantic-D H2/K adoption gap remains. The selected cold replay was not rerun:
no supplier or selected artifact is changed.

## Open next questions

Can a larger seam change donors 17 or 468's entry frames so that the combined
inverse footprint no longer spans F509? This matters because fixed entry
frames are now the obstruction. First locate both donors' last pre-B509 writes
and frame climbs, include those events in an explicit seam, and recompute its
exact map and two-sided footprints before synthesis. Any candidate must price
all source, carrier, restoration and later climbs. The blocker is that this
result supplies no favorable complete seam budget or changed contract.
TASK.json records the same question. A longer search inside the fixed block
is not a next step.

## Credit and disclosure

Prepared for **@CubeJerry**, with substantial **OpenAI Codex** assistance in
research, proof, implementation, verification and writing. No subagents or
independent human review were used. New work is Apache-2.0.

Credit **Arham Tahir / PR1368** for the open exception and forward-span proof;
**Ali Romman / PR1128** for two-sided boundary reasoning; **Aaron Wang / PR1015**,
**Ross Richardson / PR923**, and **Sagar Thakrar / PR1062** for the block programs
and composition; **Sricharan Vagvala / PR967** and **Gareth Davidson / PR915/926**
for helper/target transformations; and **DreamingOfClouds / PR589**, **eumemic /
PR555/543**, and their retained compiler/frame/hosting/checker lineage.
Credit **Andrey Mas / an664 / PR1511 and Discussion1515** for the concurrent
inverse-column invariant, B508 result and B509 corollary investigation. Their
work is not presented as this package's discovery.
