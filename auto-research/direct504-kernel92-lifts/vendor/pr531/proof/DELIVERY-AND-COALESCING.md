# Same-partition early centers and two-stage cross-face delivery

Prepared for **icekylinx**, with GPT-6 Astra assistance. This note explains
the frozen Round20 local construction in
`evidence/local/FULL-WORD.json.gz`. It is intended to accompany the
final scalar, frame, phase, and global owner certificates, rather than replace
those certificates.

The construction retains the packet programs pinned in PR514 (Dugongue) and
their inherited attributions. PR520 (higherbeing) supplied a useful map of
the delivery problem; no code from that PR is used. The use of an invertible
basis containing coordinate totals on retained source rows is also related
to PR522 (Dugongue). Here the usable rows occur at a different, earlier
frontier, and the improvement additionally requires the new target pairing
and cross-face delivery schedule. Preserve the predecessor's full notices.

## 1. The choice that changes the source frontier

There are fourteen Hamming blocks, each with eight source coordinates.
Within a block `(i,j,k,l)`, the targets split into two parity tetrads. The
previous default own-Y experiment selected the coordinate partition
`(ij | kl)` in one tetrad and `(ik | jl)` in the other. The frozen word
selects **the same partition `(ij | kl)` in both tetrads**.

The first forty source-factory events produce twenty-four pair-partial rows
from the eight sources and sixteen helper registers. The inverse selected
target decoder expresses each own-block target contribution as one of these
pair partials, up to a nonzero dyadic coefficient. Eight pair-partial rows
are needed, one for each target, and each is still at a rank-two frame.

With the same partition in both tetrads, eight of the twelve face additions
avoid all eight needed pair partials. These are the faces from the other two
coordinate partitions. Execute those eight additions first. They leave
eight retired donor rows as well as the eight finished faces. The retired
donors do not include any of the eight pair partials reserved for the own-Y
loads.

The eight retired rows already form an invertible basis of the block's eight
clean source coordinates. The independent finite check in
`audit_same_partition_frontier.py` recomputes their exact rational matrices
directly from the packet inputs, without importing either constructor. In
the supplied packet ordering, **all fourteen determinants equal `1/4`**.
Thus the inverse matrices are dyadic. This is a concrete finite fact, not a
rank assumption about an abstract family of packets.

Raise these eight retired rows to the block's rank-four frame and apply an
invertible change of basis whose first four rows are the four coordinate
totals. Keep the other four basis rows; no information is discarded. Form
the eight global coordinate centers from these block totals at their
rank-eight center frames. Throughout this phase, every target is still at
its required center-scatter level. In the raw word that level is zero; the
entrance-gauged word has the explicitly recorded compatible levels.

The center scatter can therefore occur before any own-Y load. Afterwards,
in B, read the eight reserved pair partials into their targets at rank two,
then finish the remaining four face additions. This schedule is what makes
direct own-Y loading compatible with the center cut.

## 2. Selected keys need no assembled M row

Fix a coordinate pair and a sign. Exactly three Hamming blocks contain that
coordinate pair; call them A, B, and C. Write `f_A`, `f_B`, and `f_C` for
their clean face forms and `F_A`, `F_B`, and `F_C` for their rank-three
binary frames. Each face has two existing copies, one for each of the other
blocks. `A→B`, for example, is the copy of A's face allocated to block B.

A selected key in block B now serves two selected target coordinates, one
from each parity tetrad. It has no ordinary M consumer. Supply its two
targets in opposite orders:

| Target in B | First read, before ordinary M assembly | Second read, after ordinary M assembly |
|---|---|---|
| First selected target | A's copy `A→C` | C's copy `C→B` |
| Second selected target | C's copy `C→A` | A's copy `A→B` |

Both targets receive the required scalar multiple of `f_A+f_C`; the face
normalizations are included in the two coefficients. **Do not assemble
M_B for this key.** Its two designated face-copy registers remain available
for the second reads.

All first reads occur before every ordinary M addition, and all second
reads occur afterwards. There are fifty-six selected keys and therefore
112 first reads. They use 112 distinct existing face-copy registers. The
remaining 112 keys each have two ordinary consumers; assemble their M rows
normally and make one additional M copy per ordinary key.

This differs from the default 504-helper experiment. In that experiment a
selected key also had an ordinary consumer, so its M row was assembled and
the second selected read used the M addition's retired donor. The frozen
same-partition word omits all selected-key M additions and reads both
designated copies without changing their scalar face payloads.

## 3. Why both operands have legal frames

For a selected target in B, let E_B be its rank-two frame after the own-Y
load. The actual packet geometry gives

$$
 E_B\subseteq F_B.
$$

The first read from A's copy uses F_A + E_B, which has rank four. If that
copy later participates in an ordinary M_C addition, it remains legal
because

$$
 F_A+E_B\subseteq F_A+F_B,
$$

and the latter is precisely the native rank-five M_C frame. If both inputs
to an ordinary M have already supplied first reads, each added target frame
is contained in the opposite input's native face frame. Their join is
therefore still the original rank-five M frame.

If C is itself selected for this key, M_C is omitted. A's copy instead
remains a face form until its second read by a target in C. Its extra frame
E_B is absorbed by F_B, the face frame already acquired by that target in
its first read. The second read therefore has frame

$$
 F_A+F_B+E_C,
$$

of rank six. In the corresponding B-target notation, the second-read frame
is F_A + F_C + E_B. Every summand is contained in the receiving target's
final hyperplane.

The independent finite check verifies all 112 own-frame containments, all
112 first-read rank-four joins, and all 112 second-read rank-six joins. It
also checks the 112 ordinary M joins and distinctness of the first-read
copy registers. In this raw schedule, second-read donors have rank three
or four before their reads; none is being silently restored to an earlier
frame.

The existing two-shear selected target decoder and ordinary target delivery
then finish the source contribution. The inverse target output basis is
explicitly included in the word's frame-zero preconditioner.

## 4. Register accounting

No center-copy or selected-M-clone helpers are allocated in the frozen word.
The complete raw helper inventory is:

| Role | Per block | Fourteen blocks |
|---|---:|---:|
| Source packet factory | 16 | 224 |
| Second face copies | 12 | 168 |
| Additional ordinary M copies | 8 | 112 |
| **Total** | **36** | **504** |

The default 504-helper experiment had four early-center copies and four
additional ordinary M copies per block instead. Thus the same-partition
change preserves the 504-helper count while changing the dirty-response
and entrance geometry. It must not be described as a 448-helper word.

Relative to the previous 560-helper layout, the eight separate own-payload
helpers per block disappear, while the number of ordinary M copies rises
from four to eight. The net saving is four helpers per block, or 56 in all.

## 5. Arbitrary dirt and the entrance selection

Copies of one face agree on clean source columns. Their helper-dirt
responses can differ. The new delivery word therefore uses a freshly
computed response matrix, not the previous word's compensation matrix.

All source/helper operations are invertible dyadic elementary operations.
No source/helper operation reads a target register. Every changed delivery
operation adds a source/helper row into a target. Consequently the complete
source/helper subword can be reversed independently of target contents.
Subtracting the new helper response in the prescribed target input basis,
and applying the explicit inverse output basis, handles arbitrary helper
and target inputs. The complete scalar audit binds these matrix statements
to the actual emitted coefficients and register indices.

The frozen entrance selection contains 72 gauged helpers and 80 kernel
pivots, with disjoint roles. Every one has a one-dimensional entrance
frame. The remaining 352 helpers enter at zero. The residual-width
inventory is therefore

$$
 152\times 8\; +\;352\times 9.
$$

Each kernel pivot's newly computed response column is an exact dyadic
linear combination of its specified donor columns. The initial donor
updates cancel that pivot's target response. Each gauge instead performs
its compensation at the stated nonzero entrance level. Their first-frame,
target-level, and center-chain compatibility conditions are part of the
literal frame checks. The helper count, width inventory, and center rank
sum remain explicit; no entrance contribution is treated as a free row.

## 6. Coalescing the actual delivery climbs

The final frame pass preserves every scalar coefficient, operation order,
A/B cut, center frame, target scatter level, helper entrance, and helper
exit. For an addition at frame F, let N_t and N_s be the next fixed/current
frames of its two registers. Replacing F by

$$
 G=N_t\cap N_s
$$

is legal whenever F is contained in G: both previous frames are contained
in F, and G is contained in both successor frames. The analogous
single-register rule applies to a scaling. Explicit barriers enforce the
center and target frames at the A/B cut.

For each candidate replacement, the implementation recomputes the two
adjacent child ranks on every incident register chain. It accepts a change
only if the exact profile is unchanged or its local entropy fee decreases.
This is a finite improvement procedure, not a claim of global optimality.

All 248 accepted promotions in the frozen word occur in B:

| Promotions | Count |
|---|---:|
| First face-read frame, rank 4 to rank 6 | 80 |
| Second face-read frame, rank 6 to rank 7 | 112 |
| Target scaling frame, rank 7 to rank 8 | 56 |

The target scalings move a climb without changing the profile. The total
profile change from the other promotions is

$$
 \Delta H_1=-32,\quad \Delta H_2=-160,\quad
 \Delta H_3=-32,\quad \Delta H_4=112.
$$

The three nonzero per-move fee differences simplify respectively to
`log(4/27)`, `log(27/64)`, and `log(27/256)`, with multiplicities 80, 80,
and 32. All are strictly negative. Thus the signs of the accepted moves
can be checked algebraically, independently of the floating-point discovery
comparison.

With the standard local entropy fee
`Phi_m(r)=r log(m/r)`, the reduction is exactly

$$
32\Phi_m(1)+160\Phi_m(2)+32\Phi_m(3)-112\Phi_m(4)
 =576\log 2-96\log 3
 =96\log(64/3).
$$

It is about 293.785996290393 per invocation and is independent of m because
the rank mass is unchanged. The exact nonlinear moment endpoint must still
be computed from the resulting profile and actual global owner assignment;
the entropy saving itself is not used as a substitute for that computation.

## 7. Frozen local data and verification scope

The final local profile is

$$
 H_1=2028,\quad H_2=752,\quad H_3=156,\quad
 H_4=392,\quad H_5=56,\quad H_6=56,\quad H_7=8.
$$

The word has 112 ports, height nine, 504 helpers, and center rank sum 64.
The rank-mass identity is

$$
 \sum_r rH_r=6240
 =9\cdot504+8\cdot224+64-152.
$$

`SAME-PARTITION-FRONTIER.json` records the fourteen exact retired-basis
matrices and all 112 delivery incidences. Its independent checker uses only
the pinned packet input files and runs in about half a second in the
current environment. `COALESCING.json` records all accepted frame changes
and their profile deltas. The full-word frame pass also checks the center
barriers and equality of all scalar operations before and after promotion.

These local records intentionally have a limited scope. The final package's
separate evidence supplies the arbitrary-column replay, canonical port
transport, targeted recipes for changed frame edges, actual whole-owner
assignment, and exact global moment evaluation. Unchanged predecessor
certificates can be reused with their input identities bound explicitly.
