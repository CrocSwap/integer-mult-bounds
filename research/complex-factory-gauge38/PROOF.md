# Two coupled scale moves and a restricted gauge optimum

Prepared for **@CubeJerry** with substantial OpenAI Codex assistance.
Apache-2.0. The matrix and 34-gate predecessor are Alluri's PR681;
the primitive lowering is Sagar Thakrar's PR696.

## The useful 34-macro construction

Number the predecessor's gates from zero and its eight registers from zero.
Keep all 28 ordered additions, all six scales, their frames, and their signs.
Make precisely these edits:

| Original gate | Edit |
| --- | --- |
| 16: double register 0 | Delay until immediately before original gate 31 |
| 22: double register 1 | Delay until immediately before original gate 32 |
| 26: add `2 * register 6` into register 1 | Change coefficient to 1 |
| 30: add `-register 0 / 2` into register 3 | Change coefficient to -1 |

The delayed doublings are paid and executed; neither is dropped. Between the
old and new positions, the affected physical register contains half of its
old value. At original gate 25, both registers 0 and 1 have been halved, so its
unit addition needs no coefficient change. At gate 26 only the destination
is halved, requiring coefficient 1; at gate 30 only the source is halved,
requiring coefficient -1. Restore each doubling before its next interaction
with an unscaled register. All other interactions are unchanged. This proves
the complete boundary map for arbitrary correlated inputs, without clean data
or helper assumptions.

Under the original Horner lowering, each changed coefficient falls from five
to four real operations: **128 to 126** for the whole block. Under PR696,
each falls from four to two operations, including the private-work clear:
**81 to 77**. Each single doubling move alone is cost-neutral (128/81);
their composition is a strict improvement. This crosses a plateau that the
predecessor's strictly improving single-scale pass does not cross.

The inverse reverses the sequence and inverts each gate. Inverse-transpose
swaps addition source/destination and negates its coefficient, retaining gate
order and inverting scales. These transformations preserve each per-gate
cost, and preserve complete-map equality. All four orientations are checked
on eight arbitrary input columns plus arbitrary coefficient-work dirt.

## An exact bound for the broader rescaling class

The class fixes the 28 ordered additions and the two original negations.
Only positive powers of two may be inserted, moved, split or combined along
the eight wires; additions are conjugated accordingly. Initial and final
wire scales are the identity. Both original negations remain charged, even
when combined with a positive scale. No addition is removed/reordered, no
new register is introduced, and coefficient work is cleared after each
addition using the specified original or PR696 lowering. Changing the
negation scheme, sharing coefficient work, alternative primitive lowerings,
and different addition topologies are outside the class.

For each addition, create two vertices, one per participating wire. Join
successive appearances of a wire, using a common fixed boundary vertex 0.
The original intervening scales give each wire edge an integer offset `e`.
An addition from source vertex `u` to target vertex `v`, with coefficient
`±2^e`, gives another edge. The graph has **57 vertices and 92 edges**.

Let `g[0]=0` and let every other `g[v]` be an arbitrary integer. The physical
wire at that appearance stores `2^g[v]` times its original value. Every edge
has residual `r = e + g[v] - g[u]`. A wire edge costs at least `|r|` shifts;
multiple intervening shifts cannot beat their net absolute exponent by the
triangle inequality. An addition has coefficient `±2^r`. Conversely the
constructor emits every such gauge assignment and restores all boundaries.

The exact original-Horner cost is

`4*28 + 2 + sum_edges |r|`.

For PR696 a unit addition costs two, and a nonunit power-of-two addition
costs `3+|r|`. Its total cost is therefore

`2*28 + 2 + sum_edges |r| + number_of_nonunit_additions`.

`CERTIFICATE.json` supplies a signed integer flow `y` with `|y[e]| <= 1`
and zero divergence at every vertex, and integer potentials `g`. Thus, for
**every** gauge assignment, including ones outside any finite search box,

`sum |e + g[v] - g[u]| >= sum y*(e + g[v] - g[u]) = sum y*e = 9`.

The potential terms cancel by flow conservation. The supplied potentials
attain 9 and make all addition residuals zero. Hence the class minima are
exactly **123 original-Horner primitives and 67 PR696 primitives**. The
verifier establishes feasibility and equality using integers only; floating
point solver success is not evidence for the bound. Inversion and
inverse-transposition biject this class with its corresponding orientation,
so the same cost bound applies to all four orientations.

The 67-primitive witness uses 38 scalar macros. **77 is not claimed to be the
optimum under a 34-macro budget.** The bounded MILP nominates the useful
77-primitive witness; exact verification establishes its feasibility and cost.

## Physical boundary, full composition, and complete local cost

PR681's observer freshly reconstructs all fourteen literal raw-constructor
windows. Their original templates are identical under the pinned register
relabelings; the observer checks all distinct physical entry and exit frames.
The changed program uses the same eight registers in each same-frame window.
The full raw word is spliced in descending index order, and its full inverse
cleanup is rebuilt. No helper, copy, source access, wrapper or child is omitted.

Fourteen windows, their inverse cleanups and two real components give the
additional PR696 saving `14 * 2 * 2 * (81-77) = 224` per orientation. Original
Horner saves 112. Every macro's source reads, initialization, shifts, signed
accumulation and work clear are charged by the literal primitive stream.

The unchanged native auditors verify all 716 data/helper columns, common
frames, wrappers and the paid profile. A new exact primitive-row interpreter
also includes eight arbitrary private-center inputs and arbitrary coefficient
work: **725 input columns**, in each of six complete scalar projections
(baseline, useful candidate, and unconstrained control; both orientations).
It checks the required shear, restored helpers and cleared private work.

The retained invoice uses `C=64*74^3=25,934,336` and
`A=16*(M+children+registers+centers)+64*73`. Here
`M=15,512`, `children=3,472`, `registers=716`, `centers=8`, so `A=320,000`.
The useful candidate retains every one of these quantities. Its original
Horner local bound falls by 112; substituting the counted PR696 primitives
into the same formula reduces the bound from **8,298,987,643,784** to
**8,298,987,643,560**, exactly 224. This is an explicit local recount, not an
executed global invoice or production integration.

The 67-primitive control adds 112 macros per full invocation. Its extra
1,792 adapter units cost `1,792*C`, exceeding its 784 primitive saving.
The corresponding PR696 local bound rises by **46,474,329,328**. A smaller
scalar count alone is therefore insufficient here. The control is a valid
circuit with a worse complete local price, not a failed identity test.

## Precision and theorem boundary

For all four local orientations, the positive endpoint matrices agree and
every new positive prefix row is componentwise bounded by an old one.
For the useful full candidate, exact scalar row-l1 peaks stay **124 forward /
107 backward**, and the maximum reduced dyadic denominator stays **4** in
both directions (two fractional bits). The inherited positive prefix bounds
stay **68,417 / 1,649,462** and the charged local payload remains 192 bits.
These are exact scalar checks; they do not prove rounded recursive precision.

All fourteen raw windows pass, but later gauge/cold-end/provider recipes are
not rebuilt with this edit. Whole-owner hosting, Clifford phase lowering,
global invoices and the outer assembly are not rerun. The fixed paid profile
provides no exponent improvement. Uniform compilation, common-label and
mutable-source realization, physical hosting, precision/tape, exact recovery
and analytic transfer remain inherited assumptions. **No new κ**, no global
circuit optimum, and no formal proof of the multiplication theorem are claimed.
