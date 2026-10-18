# Sharp four/five-source boundary for universal dirty connectors

**Recursive-interface construction and exact finite exclusion; no new kappa.**
One fixed source-toggle path supports every binary output pattern on at most
four sources, using each active source and output operator exactly twice.
For five sources, no ten-toggle path has that property: an exhaustive,
independently implemented census of all **945** canonical pairings has maximum
coverage **31 of 32** masks. An explicit twelve-toggle path covers all 32.

Consequently the batch with five sources and one output for each of the 31
nonzero masks has exact optimum **74 complete queries** in the model below.
The support bound of 72 is unattainable; parity rules out 73. This adds a
universal source-path criterion and its first failure boundary to
[PR934's three-by-three result](references/PR934-README.md), rather than
repeating its target-by-target search.

```sh
python3 -I -O -B research/universal-connector-boundary/verify.py
```

Expected:
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
Python 3.10+ and the standard library suffice. [CERTIFICATE.json](CERTIFICATE.json)
contains all three literal query words and both recursive leaf expansions.
[EXPECTED.json](EXPECTED.json) records exact verification coverage.

## Exact interface

Let x_j, y_i and z be distinct length-L arrays over F2, all arbitrarily dirty.
The fixed maps B_j and A_i are exact F2-linear maps of compatible dimension;
they need not commute or be invertible. Sources and coefficients are read-only.
The requested operation is

    y_i += sum_j M_ij A_i B_j x_j;    x_j and z unchanged.

Only complete calls `B_j: z += B_j x_j` and `A_i: y_i += A_i z` are allowed.
The straight-line query word may depend on M, but not on the data contents.
Each call preserves other rows, restores all private scratch and returns its
tape heads to the agreed entry positions. Its behavior is independent of the
old target contents. All data rows and z are excluded from child scratch.
Targets cannot be observed until the batch completes. There are no free
copies, combined queries, extra root connectors, changes of frame or role,
overwrites, direct A_i B_j calls, or other data operations in this alphabet.

Bounds concern a schedule correct for arbitrary admissible operators and
inputs. Specialized zero maps, operator relations or restricted inputs may be
cheaper. The construction is characteristic-two and linear; a nonlinear
readout or ordinary addition in odd characteristic does not inherit it.

## Paired readouts are differences of source prefixes

Project a full query word onto its B calls. Let q_t be the subset of source
labels occurring an odd number of times in the first t calls; q_0=0. At that
boundary,

    z = z_initial + sum_j (q_t)_j B_j x_j.

Two calls to A_i at boundaries s,t cancel A_i z_initial and contribute exactly
the row q_s XOR q_t. Thus the available row masks are

    D(w) = {q_s XOR q_t : s,t are boundaries of the source word w}.

This condition is sufficient for any number of output rows: place each pair
at its chosen boundaries. Different A_i calls commute because their targets
are distinct and they do not change z. Repeated masks are harmless. The source
path is fixed; the positions of output readouts depend on the requested M.

It is also necessary when each A_i occurs twice. One may specialize to L=1
and all A_i=B_j=identity, with independent source and dirty bits. This proves
the mask condition without assumptions of operator independence. The same
specialization forces every B_j count even to restore z, and every A_i count
even to remove connector dirt. Active rows/columns therefore require at least
two calls each. All valid generic schedules have even total length.

## Universal four-source construction

The source word

    B0 B1 B0 B1 B2 B3 B2 B3

has prefixes `0,1,3,2,0,4,12,8,0`. Its prefix set contains the full two-bit
subspace on coordinates 0,1 and the full two-bit subspace on coordinates 2,3.
Every four-bit mask is the XOR of one point in each subspace. Hence D(w)=F2^4.
This is an all-size argument about the output count, not a census of four-by-
four matrices. Nonzero rows need two distinct boundary values; zero rows need
no calls. Delete inactive B labels to project the same construction onto fewer
active sources. Therefore every matrix with at most four active columns
attains the lower bound `2*(active rows + active columns)`, also for arbitrary
positive fixed complete prices on those operators.

The certificate's simultaneous all-15-nonzero-row instance uses 38 queries.

## Exact five-source boundary and repair

Any ten-call restored path using all five sources contains each label twice.
Rename labels by first occurrence. The resulting words correspond bijectively
to perfect matchings of ten positions, of which there are `9*7*5*3*1 = 945`.
Renaming permutes coordinates and cannot change full-mask coverage.

The generator recursively emits restricted-growth words. The independent
checker instead pairs the least unmatched endpoint with each possible partner
and labels a matching only after completion. This exhausts every matching once
by induction on the remaining endpoints. Both implementations compute the
complete coverage set and agree on its sorted-record SHA256 and histogram:

| Size of D(w) | 16 | 19 | 21 | 22 | 23 | 24 | 26 | 28 | 31 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Canonical paths | 42 | 120 | 180 | 56 | 45 | 220 | 110 | 150 | 22 |

None covers 32 masks. This is a complete computational exclusion of this
finite class, with an explicit reduction from the query model. It is not a
proof-assistant theorem or an impossibility result for other circuit models.

The word `B0 B1 B2 B0 B3 B1 B4 B2 B3 B4` covers every mask except 21 (10101).
There are two complete repairs in the certificate:

1. **Repeat a source twice more.** The fixed word
   `B2 B0 B2 B1 B2 B0 B3 B1 B4 B2 B3 B4` covers all 32 masks. Each output is
   read twice; B2 is called four times, the other sources twice. Twelve is the
   minimum source-call count for a fixed universal five-source path with paired
   readouts: ten is excluded, and restoration permits only even counts.
2. **Read the missing output twice more.** Keep the ten-call path and give mask
   21 four readouts. Since only 21 is missing, choose achieved nonzero a and
   b=a XOR 21; b is achieved too. Their two pairs of prefix values cannot share
   a value, or 21 itself would be a two-prefix difference. The four readouts
   therefore realize 21 while cancelling dirt. All other rows use two.

For the explicit matrix with rows 1,...,31, both repairs use 74 queries. Any
72-query schedule would use every operator exactly twice, contradicting the
945-path exclusion; odd 73 is impossible. This proves the claimed unit-cost
optimum within the stated alphabet. It does not assert that every five-column
matrix needs 74 calls, or that every subset of output masks needs a surcharge.

## Complete cost recurrence

Let c_F(L) be the complete cost of an additive call and its inverse at fixed
ports, including coefficient/source access, arithmetic, target updates,
private scratch restoration, head returns, and required entry/exit frames.
Take the larger orientation cost if necessary. Let P_F pay reusable coefficient
preparation once, I pay input admission/initial layout, and D pay root instruction
storage, reads and dispatch. For the all-31-output matrix define

    C_base = I + sum_F P_F + D + 2 sum_j c_Bj + 2 sum_i c_Ai.
    C_extra_source <= C_base + 2 c_B2.
    C_extra_output <= C_base + 2 c_A20.  (Output index 20 has mask 21.)

The displayed B word can be relabeled to repeat any desired B_j. These are
priced constructions, not a general weighted optimum. D must be evaluated
for the actual word; both have 74 root calls. No frame change or copy is
required by this interface. A caller needing conversions must add their cost.
For arbitrary output count, admit the explicit M by scanning its entries and
use the fixed, at-most-32-mask boundary lookup to place each output's readouts.
Charge that scan, program construction and its O(log(output count))-bit role
indices in I and D; output-dependent scheduling is not a free oracle.

For F composed of d factors in application order, use a balanced contiguous
split F=L R and a distinct dirty connector w. Execute R(source,w), L(w,target),
reverse(R), reverse(L), including every leaf in each inverse. Then

    C([f]) = complete leaf cost including dispatch;
    C(F) <= 2 C(R) + 2 C(L) + paid node dispatch;
    ell(1)=1; ell(d)=2 ell(floor(d/2))+2 ell(ceil(d/2));
    h(1)=0; h(d)=1+max(h(floor(d/2)),h(ceil(d/2)))=ceil(log2 d).

The batch requires `1+max_F h(d_F)` full borrowed dirty rows, plus any private
leaf scratch. The initial 1 is z. Siblings reuse scratch only after restoration.
The inverse duplicates calls, not peak storage. All 36 source/output rows stay
reserved in the five-source example. No clean full-length row is assumed.

The literal fixture sets the five B factor lengths to 1,2,3,4,5 (leaf prices
1,4,10,16,28), and all 31 A lengths to 1. It uses four borrowed dirty rows and
46 distinct primitive operators. Free noncommutative replay checks the entire
182- and 200-leaf programs, arbitrary scratch, factor order and inverse.

| Complete schedule | Root queries | Primitive leaf calls | Borrowed dirty rows |
|---|---:|---:|---:|
| Separate column stars | 170 | 278 | 4 |
| Separate row stars | 222 | 1950 | 4 |
| Universal twelve-source-call path | 74 | 200 | 4 |
| Ten-source-call path, one four-readout output | 74 | 182 | 4 |

Both star comparators are literally replayed and priced with the same factors.
This comparison excludes changing the product factorization, specialized maps,
and other echo architectures. Leaf counts do not include a claim of physical
runtime or a faster selected supplier.

For a concrete, deliberately slow implementation of every primitive, supply
46 dense L-by-L bit matrices and 40 mutable L-bit rows on one data tape, with
separately charged instruction/control storage. The data
region has S=40L+46L^2 cells. To update one target entry, visit each coefficient
and source bit, accumulate its dot product in a clean scalar bit, XOR the
target, then repeat the dot-product accumulation to restore that scalar to
zero. Admit and initialize O(1) clean scalar work bits in I; no clean full row
is needed. Return to the origin after each complete leaf. Per leaf this pays
2L^2 coefficient reads, 2L^2 source reads, L target reads/writes, 2L^2 ANDs and
2L^2+L XORs; head travel is at most S*(4L^2+L+1), with an additive O(1) scalar
work area and constant-factor bit-gate bookkeeping. Pay scalar initialization,
loop/index arithmetic and an instruction tape with one operator/source/target
record per leaf and O(log L) counters. Charge initial matrix/input validation
and any external matrix preparation in I and P. Scratch rows are part of the
40 rows and remain arbitrary. This is an explicit complete implementation
bound, not a measured tape trace or a subquadratic dense-matrix claim. The
displayed counters are arithmetic/data-access macro counts; temporary-bit
loading/unloading, control and instruction work are additional. A loose complete
per-leaf bound is O((S*(4L^2+L+1)+L^2)*log(L+2)) plus instruction-record access.

## Verification, provenance and remaining obligations

The two enumeration methods agree on all 105 four-source and 945 five-source
canonical paths. Independent dense replay checks all basis inputs and mixed
dirty states at L=1,2,3 for nine schedule/bank combinations (six distinct banks,
with the same banks shared by the two five-source repairs), including nonsymmetric and
noncommuting maps: 789 forward and 789 inverse cases. This is finite matrix
evidence; the general linear identity is the prefix argument above. Eleven
mutation controls address restoration, readout order/destination, target masks,
scratch, unpaid children, aliased ports and factor order. Package checks add
relocation, deterministic regeneration and on-disk corruption rejection.

Discovery base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`. The accepted conditional
frontier at that base was 1661634653669567/10^18, #799 with #589/#555. Before
submission, main advanced to `47481c89fd30a43f8f882eb4b391e89c29273fd0`, selecting
PR890 at 1661957774647029/10^18. Its selected certificate, T21 construction and
maintainer review were inspected; this branch was fast-forwarded to that
submission base before final checks. Both contexts are pinned separately.
Concurrent PR938 counts minimum one-source fanout words; it does not supply
this multi-source universal-path boundary. No selected
certificate, supplier, review ledger, shared generator or upstream file changes.

No instance of this abstract multi-output interface is claimed inside the
selected supplier. Common-label/mutable-source realization, frames and owner
admission, full-row charging, compiler/tape integration, precision and outer
analytic assumptions remain uninstantiated. In particular, this result cannot
establish which supplier binds after integration or a new kappa. See
[SOURCES.json](SOURCES.json), [CLAIM.md](CLAIM.md), [NOTICE.md](NOTICE.md) and
[VALIDATION.md](VALIDATION.md) for exact provenance, scope and handoff.
