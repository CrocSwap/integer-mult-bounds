# Reverse transfers lower the universal F2 connector threshold from eight to six

**Exact enlarged-alphabet result; no new kappa or selected supplier.** For five
read-only sources and all 31 nonzero output masks, with each source and reader
operator called exactly twice, the two-root arbitrary-dirty connector needs
**exactly six transfers** when both directions of root XOR are available.
The complete witness uses **78 root calls: 10 B + 62 A + 3 C + 3 D**.

This answers the explicit reverse-transfer question in Hanson Sun's
[PR1615](https://github.com/CrocSwap/integer-mult-bounds/pull/1615): its sharp
**eight-transfer** theorem is for the one-way alphabet, not this one. The new
word uses the nontrivial six-step loop `(CD)^3 = I` in `GL(2,F2)`. In particular,
B0, B1, B2 and B3 each change physical ports between their two calls; importing
the old one-way fixed-source-port lemma would incorrectly discard the witness.

The lower bound is a written moving-frame reduction followed by two exact,
independently structured Python censuses of **2,102,100 reduced candidates**
at four transfers. Neither census finds full coverage. This is a finite
computational proof of the specified interface, not a proof-assistant theorem
or a lower bound for all multiplication algorithms.

## Exact interface

The five independent input rows `x_j`, 31 output rows `y_m`, and two connector
rows `z0,z1` are length-L arrays over F2 and initially arbitrary. Each `A_m` and
`B_j` is an arbitrary fixed exact linear map of compatible dimension. They
need not commute, be invertible, or satisfy any special identities. The target is

```
y_m += sum_{j in m} A_m B_j x_j,  m=1,...,31;
all x_j, z0 and z1 restored.
```

The only complete root calls are

```
B_j(p): z_p += B_j x_j       A_m(p): y_m += A_m z_p
C: z0 += z1                 D: z1 += z0
```

Every B and A occurs **exactly twice**. The sole new operation relative to
PR1615 is D. Physical ports may differ between occurrences, but their complete
prices are charged separately. All calls restore their private scratch and
required head/frame state; data, connectors and other live rows are excluded
from child scratch. There are no free permutations, root scalings, copies,
resets, combined queries, direct `A_m B_j` calls, source mutation or output
feedback. Readouts are not observed until the batch finishes.

## Lower-bound reduction

### 1. Normalize by the dirty-root frame

Let `G_t` be the two-by-two matrix mapping the two independent initial dirt
rows into the current roots after the transfers so far. It is invertible.
In normalized coordinates, a source call on port p toggles

```
u = G_t^{-1} e_p
```

in the coefficient column for the formal independent increment `b_j=B_j x_j`.
Full restoration requires `G_final=I`. With exactly two occurrences of B_j,
the two nonzero normalized injection columns must therefore be equal. Write
this fixed direction as `u_j`, one of `1=(1,0)`, `2=(0,1)`, `3=(1,1)`.
Physical ports need not agree. Let `q_j(t)` be whether B_j has occurred an odd
number of times. A physical reader at that cut has dirt row
`r=e_p^T G_t`, and its source part is

```
sum_j (r dot u_j) q_j(t) b_j.
```

Two reads of one arbitrary A_m cancel initial connector dirt **if and only
if** their rows r are equal. Their source-coefficient difference must then be
m. These are necessary and sufficient conditions: distinct A_m targets commute,
so all chosen paired reads can be inserted at their respective cuts. Generic
necessity can already be tested by independent source/dirt bits with identity
maps; arbitrary linear maps then obey the same formal identity.

### 2. Only two source directions need consideration

Each nonzero row r annihilates exactly one of the three nonzero columns. If
all three directions occur among the `u_j`, no paired readout can contain all
five sources. Thus the required mask 31 excludes that case.

If all sources use one direction, every reader sees either zero or the full
source-prefix vector. The possible masks are contained in the differences of
a ten-toggle path in which every label occurs twice. Ross Richardson's credited
945-pairing result bounds that set by 31 masks, including zero. Both pairing
generators here independently reproduce its full histogram from the pinned
certificate; this inherited result is not claimed as new.

It remains to consider exactly two distinct directions u,v. Partition the five
sources into nonempty J and K accordingly. The three possible reader rows see
respectively the **full**, **J-only**, and **K-only** prefix vectors. If Q is
the set of ten-toggle source prefixes and `Delta(Q)={a XOR b:a,b in Q}`, every
realized mask is in the favorable relaxation

```
Delta(Q) union projection_J(Delta(Q)) union projection_K(Delta(Q)).
```

In particular every mixed J/K mask must be in `Delta(Q)` itself. Enumerating
all 945 canonical paired source words and the 15 unordered nonempty partitions
(J never contains source4) leaves exactly **175 word/partition pairs** whose
relaxed union covers all 32 masks. A second implementation forms sets of source
labels and projects vertices before taking differences; it obtains exactly
the same 175 pairs and canonical digest. No transfer-placement assumption is
used in this filter. Each survivor is tested for all six ordered choices of
(u,v), so no normalized direction or physical port is suppressed.

### 3. Four transfers have only two loop types

A transfer acts as a transposition on the three nonzero vectors, so an odd
number cannot restore G. Every shorter even loop can be padded at exit with
cancelling CC pairs. It suffices to exclude exactly four transfers.

Of the 16 binary transfer words of length four, six restore G. Up to cyclic
rotation and exchange of the two physical root names, they are `CCCC` (orbit
size 2) and `CCDD` (orbit size 4). This classification is independently checked
by direct matrix action. Cyclic rotation applies to the entire restoring B/T
skeleton, not merely to the transfer letters: changing the start cut changes
the dirt basis invertibly and adds the same affine source shift to equal-dirt
reads, which cancels in their difference. Thus restoration and mask coverage
are unchanged. Source relabeling preserves universality as well.

For each representative there are `C(14,4)=1001` weakly increasing transfer
cut tuples among the eleven source-word cuts. For every candidate, both engines
check whether each injection direction is available on a physical port, retain
both roots at every cut, and compare every equal-dirt readout pair. The totals are

| Transfer representative | Word/partition pairs | Ordered directions | Cut tuples | Candidates | Maximum covered |
|---|---:|---:|---:|---:|---:|
| CCCC | 175 | 6 | 1001 | 1,051,050 | 31/32 |
| CCDD | 175 | 6 | 1001 | 1,051,050 | 31/32 |

The primary engine aggregates normalized prefix masks over transfer phases.
The second derives injection ports from **backward suffix columns** and replays
literal seven-bit root expressions; it never uses the first engine's
readout-dot-product or segment tables. Full admitted counts and coverage
histograms agree and are retained in [EVIDENCE.json](EVIDENCE.json). These are
counts in a sufficient exhaustive *reduced decision domain*, not a count of all
labeled physical schedules or symmetry orbits. Together with odd parity and
padding, this excludes every transfer count below six.

## Six-transfer construction

Here `Bj@p` means a complete B_j call into physical root p. The skeleton is

```
B0@1 C B1@1 D B2@0 C B0@0 B3@0 D B1@0 C B4@1 D B3@1 B2@1 B4@1
```

Its normalized source directions are `(2,3,2,2,2)`. The transfer cuts in the
source word `(0,1,2,0,3,1,4,3,2,4)` are `(1,2,3,5,6,7)`. Every source is
restored, both dirty roots return exactly, and the equal-dirt differences cover
all 32 masks. For each nonzero mask the certificate records two explicit
`[cut,physical_port]` readouts and the expanded **78-call word**. The all-size
arbitrary-linear-map identity follows from the normalized readout formula;
finite dense tests alone are not being used to infer it.

The primitive fixture gives B_j exactly j+1 distinct factors, in application
order, and gives each A_m one factor. A balanced dirty echo for `F=last first`
executes `first(source,w), last(w,target), inverse(first), inverse(last)`;
inverses reverse every leaf. Its fully charged leaf counts at lengths 1..5 are
`1,4,10,16,28`. Thus the new word has **180 factor calls + 6 full-row transfers**,
three borrowed child rows, and 41 arbitrary dirty data rows overall. All 46
factor maps are distinct. A free noncommutative replay checks every initial-row
symbol, every factor order, all output masks and scratch restoration in both
orientations. Dense F2 fixtures at widths 1,2,3 include nonsymmetric,
noncommuting and singular maps, all input basis columns and mixed dirty states.

## Complete price and what is not claimed

Let `c_F^p(L)` be a complete child price on physical port p, including coefficient
and source access, local arithmetic, target update, private restoration,
head returns and required entry/exit frames. Let `sigma_C`, `sigma_D` be the
complete prices of the two full-row transfers. Let H include all parent work
not already inside those calls: admission and reservation, coefficient
preparation, instruction construction/storage/read/dispatch, layout and routing,
and final restoration. The actual 78-call word has bill

```
T6 = H6 + sum_{B occurrences} c_Bj^p
        + sum_{A occurrences} c_Am^p + 3 sigma_C + 3 sigma_D.
```

B0..B3 use each port once; B4 uses port1 twice. All A ports and both orientations
are explicitly retained in the certificate. There is no free port rebinding.
At equal complete child prices c and transfer prices sigma, this becomes
`H6+72c+6sigma`. Against the old one-way endpoint `H8+72c+8sigma`, it saves
`2sigma-(H6-H8)` only under equal port-price assumptions. Against the old
one-root 74-query repair, the favorable condition is

```
6 sigma + (H6-H1) < 2c,
```

rather than the old eight-transfer condition. With unit prices and equal H,
78 exceeds 74: fewer transfers do not by themselves make a useful paid supplier.

One concrete conservative backend is exact dense bit-matrix application in a
fixed one-head layout, with 41 length-L rows and 46 L-by-L matrices. Set
`S=41L+46L^2+O(1)`. A factor call can compute each target dot product in one paid
clean scalar bit, update the target, and recompute to restore the bit. Its
complete bound is `O((S*(4L^2+L+1)+L^2)*log(L+2))`, including naive travel,
coefficient/source reads, index/control work and head return; scalar admission
and instruction storage are charged in H. A transfer scans corresponding source
and target bits, XORs them, clears scalar loading work and returns the head,
with bound `O((S*(3L+1)+L)*log(L+2))`, plus its instruction access. Reverse
transfers have the same conservative bound in this fixed layout. The reserved
scratch rows start arbitrary. This is a deliberately slow legal implementation
bound, not a measured tape trace or an asymptotic improvement over dense maps.

No occurrence of this multi-output batch inside the selected supplier is
identified. Whole-call hosting, common labels, port realization, precision,
compiler/tape integration and outer analytic transfer are not supplied. The
selected kappa remains `836330098538459/500000000000000000`. Extra or odd A/B
multiplicities, more roots, other transfer families and specialized maps are
outside this incidence-minimal theorem.

## Reproduce and controls

Python 3.12, standard library only, from repository root:

```sh
uv run --python 3.12 --no-project python -I -O -B research/bidirectional-five-source-connector/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/bidirectional-five-source-connector
```

Expected focused output:

```
PASS_BIDIRECTIONAL_FIVE_SOURCE minimum_transfers=6 root_calls=78 eligible=175 four_transfer_candidates=2102100 engines=agree factor_calls=180 dense_cases=522 no_new_kappa
```

`verify.py --emit` regenerates the canonical JSON payload on stdout. The committed
receipt contains no runtime, machine path or compression-dependent hash.
Every single root-call deletion and every physical port/transfer-direction flip
is rejected, as are a wrong factor, omitted child leaf, aliased scratch,
clean-input-only readout and unequal normalized injection directions. Exact
source pins are enforced, with source-corruption controls; a changed evidence
count is rejected. Cyclic and physical-port-swapped witness controls corroborate
the symmetry reduction. No assertions are needed, so optimized Python retains
these checks. The wrapper registers the entire lower-bound census, not only the
positive witness; no native compiler or network access is required for replay.

Both displayed commands were exercised on CPython 3.12 on 2026-10-14. The focused
optimized replay printed the line above; the registered replay repeated it and
finished with `PASS_REGISTERED_RESEARCH_PACKAGE` and `outcome=completed`.
No full repository suite, selected cold replay, formal kernel or GitHub CI pass
is claimed. The package does not modify any selected construction.

## Sources, attribution and scope distinction

Base `e112d71c8d7bb32435debcc54df932593dd8223a`; independently drawn seed
`628ce1c7a4abbbac17914cb067826ef4`, recursive-interfaces. The entire chooser output
is [SELECTION.json](SELECTION.json). The pre-computation budget, refined card
and stopping rule are retained in [TASK.json](TASK.json). Exact local Git blobs
and SHA256 bindings, live predecessor heads and overlap coverage are in
[SOURCES.json](SOURCES.json). Claim:
[Discussion2049](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-18931173).

Credit Ross Richardson / PR943 for the inherited one-root obstruction and
74-query repair; woklerx / PR1438 for the two-root interface; Gareth Davidson /
PR1498 for the one-way port and four-transfer argument; Hanson Sun (bbMisk) /
PR1615 for the sharp one-way eight-transfer theorem and reverse-transfer
question; Cinna Davis / Discussion1412 for the earlier eight-transfer word;
Sagar Thakrar / seed58 for the independent reduced one-way census. Their
one-way constructions are positive controls, not resubmitted as new results.
Cinna Davis's PR1675 concerns arbitrary characteristic-zero signed shears for
a different three-by-three target; its three-shear theorem does not settle the
F2 six-step braid used here. The concurrent round3 signed four-shear classifier
is likewise a different ring, target and incidence count.

New work by Adam Gall with substantial OpenAI Codex assistance in derivation,
experiments, independent-implementation controls, packaging and writing.
Apache-2.0. Two code paths by the same AI-assisted contributor are not
independent human review. No frozen package, selected record or shared index is
modified.

## Open next questions

1. **Can an actual selected-supplier seam meet the complete tariff?** A native
   example could turn this abstract saving into useful work. First identify
   five reusable source factors and all required output maps, then measure or
   prove both port-specific child prices and `3sigma_C+3sigma_D+Delta H`.
   Blocker: no such supplier instance or hosting contract has been exhibited.
2. **Which six-transfer witness is cheapest at unequal physical port prices?**
   Minimal transfer count is not minimal completed cost. First supply a concrete
   port-price table, then enumerate the remaining six-transfer universal words
   using the normalized-direction filter and minimize the full occurrence bill.
   Blocker: meaningful physical prices, not an uncharged unit-call objective.

Structured versions are retained in TASK.json.
