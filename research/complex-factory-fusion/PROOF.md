# Circuit, substitution and complete cost

## 1. Exact circuit and restricted shift minimum

The input is the complete PR924 factory on eight arbitrary registers. Keep
its 26 ordered ADD pairs. Move all original diagonal factors to the output
by conjugation. The output factors, in wire order, are

`(2, 2, 2, 1, 1, -1, 2, -2)`.

Write each normalized ADD as `y_t += sigma*2^e*y_s`. Its sign is `sigma`.
Represent wire r physically as `x_r = 2^p_r*y_r`. To implement this ADD by
one unit signed ADD, its two exponents must satisfy

`p_t = l_j, p_s = l_j + e`.

For consecutive uses a and b of the same wire, let their offsets be u and v.
The necessary shift distance is `|l_b-l_a-(u-v)|`. Include the start exponent
zero and the required final exponent as fixed boundary uses. The eight wire
paths produce 60 such terms. The objective is the sum of their distances.

`CIRCUIT.json` contains 26 integer levels and a signed integer flow on these
60 edges. For every edge ab let its offset be c_ab and flow be f_ab. The
checker verifies `|f_ab| <= 1` and zero divergence at all 26 variable nodes.
Thus, for every real level vector l, and hence for every integer vector,

```
sum |l_b-l_a-c_ab|
 >= sum f_ab*(l_b-l_a-c_ab)
  = -sum f_ab*c_ab
  = 9.
```

The supplied integer levels attain nine. No floating-point solver result is
trusted. The optimum is valid for arbitrary integer scale levels, not just
the levels zero and one used by the witness. Two output wires also require
a negative sign. With signs transported by the same diagonal conjugation,
each needs at least one sign change. The witness uses two.

The resulting word has 26 unit ADDs, nine doubles/halves and two negations.
A final clear gives 38 primitives with the required arbitrary-work boundary.
This minimum concerns the fixed ordered pairs, diagonal conjugation and
unit-ADD class just defined. It is not a minimum over arbitrary circuits,
new pairs, reordered ADDs, extra work, or another complementary basis.

The primary checker uses exact `Fraction` rows to compare all nine input
columns against the original macro circuit. The ninth column is arbitrary
private coefficient work. It is erased only by the charged final clear.
It also checks the inverse, inverse transpose and transpose. Their complete
eight-register maps are equal to the corresponding original maps.

## 2. Temporary sources and the actual frame boundary

PR681's pinned extractor identifies fourteen disjoint windows in the original
PR622 word. Its unchanged binder checks their original 87-operation template.
The constructor replaces each with the pinned PR924 map and rebuilds the
entire non-target inverse cleanup. The original transport, native checks and
emitter then run on this complete changed word.

In each emitted orientation, `locate` finds every main and cleanup interval
by exact ordered scalar operations and register IDs. It requires 28 disjoint
matches. An interval may contain only these scalar operations and climbs.
Each internal climb must act on a register not yet used in that interval,
and must end at the interval's scalar frame F. Such a climb commutes left
past the preceding scalar operations, since none touches its register.
The verifier moves the same climbs, in the same order, to the interval entry.
No climb is removed or added. Their complete non-scalar order is unchanged.

After this move all eight registers have frame F. A register without a moved
climb must already have F: it has no frame change before its first checked
use. There is no other operation or outside consumer inside the interval.
The new primitive circuit touches only these eight distinct registers and
clears private work at its end. This admits the temporary source scales at
the actual program boundary, even for the three wires that are source data
rather than dirty helpers. It does not assume that source data are read-only
inside a block whose complete source transformation is already admitted.

For completeness, let T_F be the fixed invertible operator of frame F.
Physical and scalar register values satisfy `h_r = T_F*x_r`. A unit ADD
satisfies `h_t +/- h_s = T_F*(x_t +/- x_s)`. A double, half or sign change
commutes with T_F. A clear gives `0 = T_F*0`. Therefore any exact scalar
identity on the eight registers lifts to their common physical frame. This
argument uses the entire matrix, not only the rows used for the delivery.
At the exit, every outside consumer and the complementary source basis see
exactly the old values. The inverse cleanup and the dual orientation use
the exact inverse and inverse transpose of the same primitive word.

The complete replay is separate from the local Fraction check. It uses sparse
integer rows on a `2^256` grid. Every halving checks exact divisibility.
It checks all 716 logical input columns, eight arbitrary center columns and
one arbitrary coefficient-work column. The data shear is exact, all 492
logical helper columns are restored, and all private columns are erased.
The physical helper residuals remain the original width-nine children;
restored logical dirt does not mean an unpaid physical identity.

The common-frame checks run at every actual primitive. All original frame
endpoints, child ranks, phase events and adapters remain. The unchanged phase
checker verifies the changed native word's edge set, including global phase.
Its 1,879 fresh edge checks and 1,231 pinned reused checks are stated separately.

## 3. Adapter and source-access accounting

The compiler takes the original 32-macro interval as one admitted block and
uses the checked 37-operation scalar implementation inside it. It does not
submit 37 new macros to the old per-macro invoice. The 26 ordered binary
operand pairs are unchanged. Every new non-ADD operation is a scalar on one
of the same registers.

A scalar multiple commutes with a register's coordinate permutation and
linear phase adapter. It can run directly in that register's current physical
coordinates. It needs no alignment with another register. Thus the new unary
source scales require no new frame conversion, child, phase adapter, owner
chart or borrowed family. The original binary operand interfaces and all
32 macro adapter reserves can be retained. The preceding common-frame proof
shows why no intermediate Fourier conversion is needed. A Fourier frame
operator is not being assigned the cheaper monomial-compiler price.

This is the changed compiler rule relative to the fixed per-macro gauge floor.
That floor correctly rules out adding a separately billed logical SCALE.
It does not rule out the explicit joint primitive implementation here.
The emitted primitive word, boundary identity and unchanged non-scalar
inventory certify this refinement. The legacy emitter itself is unchanged;
it supplies the logical contract, which the new checker implements.

Every actual double, half, negate, add, subtract, copy and clear is counted.
An ADD or subtract reads two operands; a unary operation or copy reads one;
a clear reads none. The checker also reports the complete operand-read count.
There is no extra public helper and no private source cache in the candidate.
The existing work family remains in the stock bill and its exit clear is paid.
The two real components are charged separately.

## 4. Strong comparison and precision

PR696 and the pinned PR999 lowerer are executed on the complete raw words.
They tie at 123,320 forward and 123,336 backward. The verifier also checks
that PR999 emits exactly the old 73-operation word on every factory variant.
This equality is specific to this raw word, not a claim about PR999's other
CK/JP8 inputs.

PR1032 gives exact minima 46/46/48/48 for a just-in-time coefficient cache
on all one-scale magnitude placements. The historical cache comparison here
reproduces those values on the original PR924 placement. Work can remain live
between additions and is cleared once at exit. These savings are prior work.

The strong comparison also permits repeated unit additions and a temporary
source scale followed by an ADD and the inverse source scale. The source is
restored before the next macro. For each fixed original macro, the dynamic
program has the full exact work row as its state. Its routes are:

- Copy the current source into work, shift work, then add or subtract work.
- If the cached row is an exact signed binary multiple of the required row,
  shift work and use the appropriate ADD sign.
- Apply the coefficient with repeated unit additions when it is an integer.
- Scale the source, add or subtract it, then restore the source.

A SCALE macro has its original paid unary implementation. At each step,
all routes produce the same data rows. Therefore only the work row and cost
are needed to compare future routes. The program keeps a shortest prefix
for each such row and pays one exit clear from arbitrary incoming work.
The minimum in this declared per-macro route class is 44 in every orientation.
Each emitted winning word is checked on all nine arbitrary columns.
This is not an unrestricted arithmetic circuit minimum.

A second finite census considers all 39,424 one-scale magnitude placements
in each orientation. It permits the same direct routes but uses a narrower
cache rule: the cached row must have the same source-version label, up to a
signed binary scale. Each ADD gives its target a fresh label. Unary scales
change only the exponent; they do not change the label. A state is the cached
label and its exponent. A fresh copy or a cache shift produces the required
source state; a direct route retains the old cache. These are all transitions
in this stated class. The fixed scale costs and final work clear are added.
Signs have no effect on this cost because either unit ADD sign is available.
This census also has minimum 44 in each orientation. Its unique magnitude
placement is the original PR924 placement. It does not identify different
source versions whose exact rows happen to be proportional, allow arbitrary
extra scales, reorder ADDs, or search other topologies.

Outside each factory, both the strong comparison and candidate choose the
shorter of PR999 and signed repeated additions followed by a work clear.
The only strict replacements have coefficient magnitude two or three.
They save 304 real-component primitives per complete orientation here.
These elementary routes and their CK application are credited to PR1036.
They are applied equally and are excluded from the new circuit's extra gain.

The candidate costs 38 per component in all four cases. It permits source
scales to persist across original macro boundaries, within the checked full
factory boundary. The complete-call saving over the strong comparison is

`14*2*(44-38)*2 = 336` in each orientation.

The local exact row-l1 peaks are 12, 8, 10 and 11; their depths are 1, 2, 2 and
1. The old peaks are 12, 8, 10 and 12. Complete-program positive replay also
checks the actual incoming rows and magnitudes. Its bounds remain 39,090 and
1,301,331, with fractional depth two. These fit the inherited local reserve.
The global prefix recount below retains the larger 512-bit allowance.
Exact replay and these bounds do not prove a rounded physical execution or
remove the inherited precision and exact-recovery assumptions.

## 5. Fixed banked repetition and all remaining charges

Use the existing nine-stage, eight-replica dedicated-bank host. Its data calls,
224 data owners per call, phase references, recipe, bridge signs, idle children
and execution order are pinned. No new owner arrangement is sought. The verifier checks that the data-port
order and all data entry/exit frames match the retained host. Replace only the helper count by the raw supplier's 492 and bind each literal call to
its checked complete primitive program and native/phase contract.

For stage s and helper h, use family `7168 + 492*s + h`. Replica r uses its
nine-axis chart `[2,r]`, with axes `9*r` through `9*r+8`. These eight blocks
are disjoint. They cover axes 0 through 71. Pay the one-axis complement 72
once per bank. Each complete call has 716 distinct owners. All 35,424 helper
roles and all 4,428 complements are listed and checked. Dirty helper inputs
may be correlated: the complete local map was checked on every input column.

There are 7,168 data families, 4,428 bank families and 11,596 live families.
Reserve another 492 tableau families, eight center families and two coefficient
families, giving 12,098 physical families. The serialized schedule includes all
72 local sweeps, 72 bridges, idle sweeps, terminal operations, bank complements
and the final translation of every live family. The audit checks each field
against the retained schedule after the literal replica expansion.

The complete paid profile is

```
rank:   1       2      3      4      5     6    8    16   32   48
count: 150156  54720  21600  12096  12096 3168 5952 3584 3584 3584
```

It has 270,540 children and mass 843,948. The mass deficit is exactly 2,560.
All raw helpers start at zero and end at FULL, so there is no residual wrapper.
The unchanged data-phase and dedicated-bank realization remain inherited.
This audit does not replace them with a new all-size hosting proof.

Use the original conservative invoice with

```
C = 64*74^3 = 25934336
M = 15456; K = 3472; n = 716; centers = 8
A = 16*(M+K+n+centers) + 64*73 = 319104
local_bound = max(P_forward,P_backward) + A*C
```

The candidate local bound is 8,275,750,476,016. The original outside adapter
reserve is 1,527,568. It includes source/data access, helper interfaces, idle
children, complements, bridges, shifts, moves, all live families and physical
stock. The same reserve is used for all compared lowerings.

The host uses 40 forward and 32 backward calls. Hence its extra saving over
the strong comparison is `72*336 = 24192`. Its complete per-cover-vertex
bound falls from 635,470,496,884,300 to 635,470,496,860,108. The saving is solely
in the actual scalar primitive sum; no reserve is removed to create it.

The original cover-size formula then gives physical stock of 2,642 bits,
router size of 7,984 bits, literal size of 35,284 bits and row coefficient
16,469. The strict local, logical, router, literal, mass, precision, tape, row,
halving and prefix guards all pass. The prefix requirement is 206 bits; the charged allowance
is 512 bits. Every numerical quantity is recomputed by `host.py`.

No homogeneous child-cost term is improved. The selected assembly, bit supplier
and exponent are unchanged. Transport to other factory maps, helper inventories,
owner schedules or optimized suppliers requires a separate admission.
