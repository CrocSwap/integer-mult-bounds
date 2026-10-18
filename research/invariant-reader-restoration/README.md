# Reader-compatible restoration deferral

**Research note / exact recursive interface; no new kappa.** Nonzero reads of
borrowed workspace need not prevent deferring its restoration. The precise
condition is that each read annihilates the accumulated drift. A fully expanded
example, including cancellation of incoming dirt and both source calls, reduces
**210 to 150 two-address ADD instructions**, and **5,864 to 4,504 data-tape word
transitions**, for the same fixed borrowing interface. Preparation and control
costs are separately and explicitly charged below; these counts are not a
runtime benchmark or an optimal circuit claim.

This refines Navinor's [PR1155](https://github.com/CrocSwap/integer-mult-bounds/pull/1155)
at `9821c6e9388f3fc097e94b72be9fa7b41a849527`. Its retained
[original note](sources/PR1155-README.md) states that read-freedom is necessary
and sufficient and uses one failing reader as evidence of necessity. That
counterexample shows that **some** readers fail, not that **every** reader fails.
The construction here has compatible readers after actual nonidentity drift.
PR1155's shared-final-target observability also admits a weaker cancellation
condition, distinguished below. No assertion is made about its executable
fixtures beyond the statement inspected in that pinned note.

Concurrent [PR1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199)
by Sagar Thakrar at `85ac2880ea5bda44f28632b71ffa2b4e35ec6b7d` independently
corrects the same necessity claim, supplies a diagonal-sign checkpoint planner,
and states the general summed-defect identity. **No priority is claimed for
that correction or the prefix-defect identity.** This package adds separate
noncommuting-permutation evidence, distinct-output admission, an explicitly
dirt-independent shared-B wrapper, and a separately implemented symbolic
scalar/tape invoice. It does not reproduce or supersede PR1199's cut planner.
The exact concurrent source was inspected at the final submission check;
its results are credited, not silently treated as our discovery.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -I -O -B research/invariant-reader-restoration/verify.py
```

Expected:

```text
PASS_INVARIANT_READER_RESTORATION cases=5832 wrapped_adds=210->150 no_new_kappa
```

The command verifies retained source hashes, recomputes every certificate field,
and compares against [CERTIFICATE.json](CERTIFICATE.json). Required checks use
explicit exceptions and remain active with `-O`. The companion command
`python3 -I -O -B research/invariant-reader-restoration/test_package.py` checks
relocation, deterministic export and deliberate on-disk corruptions. Neither
command regenerates selected or upstream artifacts. `--write PATH` is explicitly
an authoring/export mode, not acceptance against the committed certificate.

## Exact typed interface and proof

Work over the rationals, with all arithmetic exact. Let `z` be arbitrary borrowed
workspace, `y_i` distinct arbitrary output accumulators, and `G_i` fixed invertible
linear workspace maps. A child first performs `y_i += H_i z`, then `z <- G_i z`.
All coefficients are immutable; no output aliases workspace or another output.
Readers are target-independent, and private scratch and tape positions used by
complete child operations are restored. The code specializes `G_i` to permutations
and `H_i` to rows with coefficients in `{-1,0,1}`.

The eager contract follows each child with `G_i^-1`. The deferred contract
omits these restorations and applies `(G_r ... G_1)^-1` once at batch exit. Put
`P_0 = I`, `P_j = G_j ... G_1`. Then:

- Eager output `i` is `y_i^0 + H_i z_0`.
- Deferred output `i` is `y_i^0 + H_i P_(i-1) z_0`.
- Both final workspaces are `z_0`.

Consequently, equality for **all incoming dirty states** is equivalent to

```text
H_i (P_(i-1) - I) = 0     for every i.                    (1)
```

Sufficiency follows by subtraction. For necessity, a nonzero defect matrix has
a nonzero column; the corresponding standard basis workspace is a counterexample.
This is an all-size algebraic proof, not an inference from the finite census.
For permutation prefixes, each reader row must be constant on each cycle of
that prefix. It need not be invariant under every individual `G_j`, and it need
not vanish. The condition concerns the actual chronological prefix.

**One shared output at batch exit.** If all readers update the same accumulator,
only their summed defect must vanish:

```text
sum_i H_i (P_(i-1) - I) = 0.                             (2)
```

For `G_1 = swap(0,1)`, `G_2 = G_3 = I`, and readers `0,e_0,e_1`, the individual
defects are `0,(-1,1),(1,-1)`. Condition (2) holds while (1) fails. If the shared
output is observable after every child, equality of consecutive partial sums
again forces each individual defect to vanish. Thus observability is a material
part of the contract; no general "one reader breaks it" theorem follows.

## Returning arbitrary dirty workspace without exposing it

Reading preserved input state is not by itself a catalytic scratch contract:
outputs must be independent of borrowed dirt. Supply a read-only source `x`
and a complete, exact additive call `B: z += Bx`, independent of the old target.
Its inverse is `z -= Bx`; both restore private scratch. Execute:

1. Pre-read `y_i -= H_i z` for every output.
2. Call `B` to obtain `z_1 = z_0 + Bx`.
3. Execute either compatible reader/permutation batch above.
4. Call the complete inverse `B` after batch restoration.

The output is `y_i^0 - H_i z_0 + H_i(z_0+Bx) = y_i^0 + H_i Bx`, and final
workspace is exactly `z_0`. Source `x` is unchanged. All `x,z,y_i` ports are
pairwise disjoint and excluded from private child scratch. The routing temporary
and source accumulator are **two admitted clean scalars**, separately charged;
no clean workspace row is assumed. Readers of other live state, nonlinear or
rounded B calls, data-dependent permutations and intermediate observation during
the pre-read/load sandwich are outside this contract.

The same proof holds for rows of any common length `L`, with `G_i` replaced by
`G_i tensor I_L` and the corresponding block readers. It does not construct a
selected supplier or discharge the repository's physical recursive interfaces.

## Noncommuting eight-coordinate fixture

Use old-coordinate-to-new-coordinate cycle notation:

```text
G_1 = (01)(23)(45)(67)
G_2 = (0123)(4567)
G_3 = (04)(15)(26)(37)
H_1 = e_0,  H_2 = e_0 + e_1,  H_3 = e_0 + e_2.
```

The first two maps do not commute. `P_2 = (02)(46)` and
`P_3 = (06)(15)(24)(37)`. Each reader satisfies (1); the latter two read
workspace that has actually drifted. Both have nonzero dependence on the
original workspace. The catalytic wrapper uses
`(Bx)_j = x_j + x_((j+1) mod 8)`; B need not be invertible or commute with G.
The certificate spells out gather permutations `new[j] = old[p[j]]`, avoiding
ambiguity between cycle and index-array conventions.

The matrix checker uses dense exact products. The separately implemented
[backend](backend.py) instead composes index arrays, decomposes cycles, emits
scalar instructions and literally loads/unloads its clean accumulator. On every
basis of the 19 arbitrary source/workspace/output coordinates (plus a mixed
case), both complete wrapper programs implement `y_i += H_i Bx`, preserve all
source/workspace coordinates, restore the temporary, and have a working literal
reverse-inverse. This is finite evidence for the actual emitted fixture; the
universal identity is proved above.

## Complete invoice and recurrence

A two-address ADD `d += sign*s`, with distinct ports, expands as
`A += memory[s]; memory[d] += sign*A; A -= memory[s]`. Its source is unchanged,
so A returns to zero. It pays two source reads, one target read, one target
write and three scalar additions/subtractions. The data head traverses
`0 -> s -> d -> s -> 0`, paying `2*s + 2*abs(d-s)` word transitions. The scalar
A is separately located in a fixed arithmetic workspace; arithmetic/read/write
macro costs include their internal access and scratch restoration.

Each permutation cycle is implemented by swaps. A swap uses an initially zero
scalar T and these **six**, fully charged, distinct-port shears:

```text
T += a; a -= T; a += b; b -= a; b += T; T -= b.
```

It returns `(a,b,T)` as `(b,a,0)`. A k-cycle uses `k-1` swaps. Here the forwards
use 14 swaps, eager inverses another 14, and the composed inverse four. There
is no free array copy, hidden permutation, erased scratch or unpaid inverse.
The full wrapper has two 16-ADD B calls and ten reader ADDs.

| Complete wrapper charge | Eager | Deferred |
|---|---:|---:|
| Forward-permutation ADDs | 84 | 84 |
| Restoration ADDs | 84 | 24 |
| Both B calls | 32 | 32 |
| Pre-reads and batch reads | 10 | 10 |
| **Two-address ADD instructions** | **210** | **150** |
| Scalar additions/subtractions | 630 | 450 |
| Source reads | 420 | 300 |
| Target reads / target writes | 210 / 210 | 150 / 150 |
| Data-tape word transitions | 5,864 | 4,504 |

Workspace addresses are 0..7, outputs 8..10, T is 11, and immutable source
addresses are 12..19. A is outside that data tape. The instruction stream has
one fixed-width `(opcode,d,s,sign)` record per ADD; both programs use the same
address width. Each event reads one record and returns the data head. Thus
instruction reads, control dispatch and address decoding must be paid 210 and
150 times, respectively, at the same declared per-record cost. No instruction
or coefficient-access cost is claimed to be zero.

For integer scalar inputs of magnitude less than `2^p`, every workspace value during the
wrapper has magnitude at most `3*2^p`; during swaps it is either one of these
values or zero. An intermediate output is bounded by `9*2^p`, and A loads only
workspace, source or T. Signed width `b = p+5` therefore suffices without
rounding. Allocation includes 20 data words and A, plus instruction storage,
address/control counters and the scratch required by the chosen exact scalar
arithmetic backend. This bound is about this fixture, not a floating-point
precision contract or a fixed-tape multiplication implementation.

For event-count `K`, scalar-add count `S`, word travel `J`, and word width b,
a complete parametrized online bill is

```text
W(program;b) = S*c_add(b) + 3K*c_read(b) + K*c_write(b)
             + b*J*c_move + K*c_dispatch(b, address_width).
```

Here read/write costs include intra-word scans and return to a word boundary;
`c_add` includes arithmetic scratch restoration and scalar register updates;
`c_dispatch` includes instruction-record access, decoding and counter work.
No backend numerical timings are inferred. Online saving for the fixture is
`180*c_add + 180*c_read + 60*c_write + 1360*b*c_move + 60*c_dispatch`.
Startup allocation/zeroing of the two clean scalars is paid in admission `I`.

For a general node, let `C_B^+/-` be complete recursive source-call costs,
`R_H^-/+` complete reader costs, `Q(G)` complete routing costs, `P_S` program and
coefficient preparation, and `D_S` dispatch/control not already included. With
no double counting of these terms, the recurrences are

```text
T_E = I + P_E + C_B^+ + C_B^- + R_H^- + R_H^+
      + sum_i [Q(G_i) + Q(G_i^-1)] + D_E,
T_D = I + P_D + C_B^+ + C_B^- + R_H^- + R_H^+
      + sum_i Q(G_i) + Q(P_r^-1) + D_D.
```

If `C_B^sign(L) = sum_j C_child(j,sign)(L_j) + A_B^sign(L)`, substitute the
**entire** recurrence in both occurrences. All children, coefficient and source
access, frame conversions, copies, private restoration and tape return belong
in those terms. No child is eliminated by this argument. A caller requiring a
new frame or external layout conversion must add it; this fixture stays in one
fixed coordinate layout. Recursive children may not borrow the live rows.

Preparation is not free: composing explicit n-entry permutation descriptors
uses `r*n` index lookups and stores (24 of each here), plus validation, inverse
construction, cycle extraction and instruction emission. General descriptors
are not composable in merely `O(r)` work. Budget `O(r*n*log(n+1))` bit work for
index manipulation, in addition to validation/coefficient preparation and
writing the full instruction stream. The implementation computes the product
in both modes to return admission metadata; a lean eager implementation could
omit those 24 updates. We do not use this avoidable baseline work as a saving.
For `M` invocations of a prepared fixed program, pay `I + P_S + M*W_S`.
For a single call, the extra preparation must be smaller than the displayed
online saving before claiming a total speedup. Neither M nor that tradeoff is
silently assumed. The full parametrized bill makes this boundary explicit.

Directly computing `H_i Bx` can be cheaper than either wrapper in this toy
fixture. This is a legal replacement and correction within a fixed borrowing
interface, **not** a minimum over arbitrary circuits, a claim that a new
supplier is profitable, or a way to increase kappa from operation counts.

## Coverage, failures and limits

A further [separate symbolic checker](independent_check.py), included in the
one-command replay, does not import the matrix criterion or backend execution
engine. It checks all 873 permutations of widths 1 through 6 against the emitted
forward words, then reconstructs both full wrapper maps using integer coefficient
vectors. It independently derives every invoice field and bounds all intermediate
coefficient L1 norms: workspace/T/A at most 3, outputs at most 5, source at most 1.
The conservative integer-width allowance above is therefore sufficient. Its
symbolic-map digest and exact bounds are retained in the certificate.

The finite census exhausts all `2^3 * 9^3 = 5,832` three-child instances with
2-coordinate permutations and reader coefficients in `{-1,0,1}`. Independent
literal state replay on both workspace basis vectors agrees with the matrix
criteria in every case. There are 2,592 compatible distinct-output instances,
2,772 compatible shared-final-output instances, and 180 cancellation-only cases.
This is completed finite coverage, not a new impossibility theorem.

Controls include an incompatible nonzero reader with an explicit basis witness;
a zero-workspace input that hides that defect; omitted final restoration;
incorrect inverse order on a noncommuting example; an omitted reader; missing
catalytic pre-reads that expose dirt; an omitted inverse B that fails restoration;
and invalid/aliased instruction ports. Certificate/package mutations test
rejection of an unpaid operation, source corruption and receipt corruption.

The exact general lemma is proved in prose. Neither the finite replay nor the
second Codex agent's algebraic review is independent human review or a formal
proof in a proof assistant. No selected cold replay was run: this isolated note
changes no supplier, selected certificate, shared generator, upstream source,
review ledger or frozen predecessor evidence. All-size compiler, common-label /
mutable-source realization, hosting, precision/tape and analytic transfer
obligations of the selected multiplication result remain open as recorded there.

## Provenance and credit

Base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`. Assignment seed **50**, generated
from OS randomness, selects recursive interfaces and the three-child/eight-entry
fixture. There is no random search. [CLAIM.md](CLAIM.md) records the three narrow
candidates and overlap decision; [SOURCE-PINS.json](SOURCE-PINS.json) identifies
exact context files and retained sources. The selected result at that base is
`836330098538459/500000000000000000`, from #1094 on #1087; complex binds in that
assembly. We do not reassign its binding supplier or modify its frontier.

Credit Navinor / Aaron Wang with opencode assistance for PR1155's deferral
proposal and motivating reader question. Credit Sagar Thakrar's concurrent #1199 for the same applicability correction
and its distinct checkpoint planner, and his #1012 and
avirazza's #974 for the distinct hosted-assembly cost question; their reported
mass-neutrality is not contradicted by this abstract-interface correction.
Ross Richardson (CubeJerry)'s #889 supplies the shared-B, multiple-output dirty
fanout/echo construction; the pre-read/load/unload wrapper here is an instance
of that established mechanism, not a new batching claim. The additional result
is admitting nonzero readers through intervening workspace permutations using
the exact prefix condition, independently corroborating PR1199. Gareth Davidson's #1057 and woklerx's #1164 concern dirty-pool allocation and
higher-arity echoes, not the reader-defect criterion here. Ross Richardson's
universal-connector work and the repository's preceding dirty-restoration work
retain their own scopes and attribution. No priority claim is made for elementary
linear invariance or echo cancellation.

Prepared for **mightyOil (Philipp)** with substantial **OpenAI Codex assistance**
in mathematics, implementation, verification and writing, including three scoped
Codex subagents. New files are Apache-2.0; retained source credit is in
[NOTICE.md](NOTICE.md).
