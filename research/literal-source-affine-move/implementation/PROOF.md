# Generic fixed monomials and actual affine MOVE24476

## Source, prior scope and statement

Canonical main is e54523517d0f03e58352e647c403a5af3e525a57. Its selected
archive `research/shared-wire-split-composition/data/final.json.gz` has
Git blob74563a7867d9d762b6588f65362369668841bb3e,350722 bytes, compressed
SHA2562b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883 and
canonical word SHA25691429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097.
Event24476 is `[MOVE,727,3,470,false]`, with complete frames3=[] and
470=[75,137,265]. The ordered operator is U=T470 T3*. The Boolean records
private-owner metadata, not inverse orientation; it is false here.

The source compiler gives U=L(C0 C1 C2)R, with positive
C=1/2[[1+i,1-i],[1-i,1+i]]. RECIPE.json retains every source parameter.
R has offset5 (output/native slots0,2) and constant phase2; L has offset
and constant0. Fixed words have26 right and33 left CNOTs. bind_source.py
authenticates/reextracts the whole archive and optionally recompiles this
pair. Its separate explicit-check Gaussian/Pauli engine certifies full
matrix and absolute phase against original frame circuits, using the
credited signed-generator/separating-column lemma. All1024 binary columns
are checked too. Wrong offset/phase/inverse controls reject. Only the
optional canonical assertion-based compiler rebind requires normal Python;
the independent acceptance and numerical replay work under -O.

Existing literal MOVE24472 already has right offset1 AND phase1. This is
not the first nonzero-offset/phase MOVE. The new scope is generic fixed
nine-coordinate monomial composition and this different multibit-offset
rank3 source binding. #6978 already proves rank-rf/coded-child algebra and
the selected proofs already give the all-f algebraic lift; neither is new.

Supply positive f,c,P,S,cutoff, width w>=2 and six canonical Gamma codes
(f,c,P,S,w,cutoff), length E. DATA is the complete lexicographic
[P]x[2^f]^9x[S] array with c Gaussian coefficients per address, real then
imaginary, each signed w-bit MSB-first on one unchanged common quantum.
Let V=2PScw2^(9f), F=E+V. c is not native rank. All owners are distinct,
heads begin at origins, required private bodies/guards are blank, and
opaque exteriors/previous backing remain separately charged.

Require3f<=cutoff, actual right/left complete phase rotations to fit w bits,
and every output of each actual3f C-axis prefix to be integral on the same
grid and fit w bits. Final fit alone is insufficient. The concrete leaf's
w+2 temporary numerator and exact-half/range guards remain unchanged.

**Generic monomial theorem.** For fixed invertible binary9x9 G, b in0..511,
alpha inZ4^9, symmetric Q with alpha_i mod2=Q_ii, and a inZ4,
compile_monomial emits its all-column monomial under its actual signed-phase
promise, with complete original-owner return,31 tapes, time2^24(fV+E+1)
and historical increment512(V+E+1). All recipe values are offline constants.

**Actual MOVE theorem.** compile_move emits one138933-location31-tape
four-symbol graph for U^(tensor f). It checks the joint cutoff, preserves
all header/width/grid/spectator/owner data, returns heads and retires private
work on success. One original-owner transaction encloses all factors.
There is no original DATA write until all components return; finite valid
cutoff/numerical failures preserve original DATA. Failure cleanup, general
malformed-input termination, interruption/retry and failure reuse are unclaimed.

Complete successful bounds are T_core<=2^25(fV+E+1) and
K_final<=K_entry+2048(V+E+1). The35-tape HOME adapter adds128(F+1) time and
64(F+1) backing, hence2112(F+1) total increment for this actual recipe.
General B1 full-bank gathering/return/backing retains its separately paid
O(R_bank K_bank(F+1)) contract. Fixed program construction/authentication,
storage and origin provisioning are setup charges if not supplied.

The fixture has two already supplied public homes: parked input and source
role727. productive_count=2 is bookkeeping for those initial fields, not a
proof of global selected productive stock or new productive credit. No
typed INIT727, actual large-bank selector, job packing or caller producer
is built. Private=false does not supply such a producer invariant.

## Monomial order, constant phase and complete geometry

Write q(x)=sum alpha_i x_i+2sum_(i<j)Q_ij x_i x_j mod4. The source convention
is |x> -> i^(a+q(x))|Gx xor b>, with q on input and b on output coordinates.
On f columns the exponent is a*f+sum_l q(x_l). The generic list executes
one complete phase for this exponent, then G, then X_b. Moving only scalar
i^(a*f) into the first pass is exact since it commutes with both permutations;
the input-dependent q is not moved. Q's diagonal is not counted twice.

The retained initializer scans unary f, appends one zero to each of nine
counters per mark and advances its four-state mode by a. Its mode is a*f
mod4. The retained synchronized counter algorithm supplies sum q(x_l) on
complete rows and c/P/S fields. It performs the net unit phase directly,
without introducing separate serial negations for each source phase record.
Twenty-eight actual prefix probes cover all a and f=1,2,3,4,5,16,65;
a2,f2 gives0 rather than a once-per-call2. The invariant proves all f.

Fixed binary Gaussian elimination emits chronological G; reversing CNOTs
gives its inverse. A nine-coordinate word has at most99 gates (at most9
three-gate swaps plus9*8 row additions); identity omits the word. The
unchanged affine emitter has fixed H e0=b and chronological H^-1,X0,H,
one reversal and at most20 CNOTs. Every numerical component retains original
f and9f geometry. Its first-five-field parser accepts the unchanged sixth
cutoff as opaque data, as already proved in #7428/prior Gamma6 joins.

The actual list is: joint3f guard; right complete phase including2f;
right26-CNOT G; right offset5 (one CNOT on either side of X0); C0;
S01,C0,S01; S02,C0,S02; left complete phase; left33-CNOT G. Every Si is
three exact phase-free CNOTs, hence Si C0 Si=Ci. The central product is
C0 C1 C2 and the total order is L C3 R with its exact absolute phase.

Each fixed row addition acts on matching native bits of each f-column;
each Xi complements its entire slot; each phase sums the same per-column
polynomial. Their individual coordinate actions prove the arbitrary-f lift,
including every complete P/S/coefficient/component spectator. This tensors
products of fixed operators, not sums or exterior register coefficients.

## Guard, transaction and helper invariants

The unchanged fixed-rank guard multiplies captured f by3 with carry0..2
and q=ceil(log2(3)) leading positions, canonically repacks and compares to
the actual binary cutoff. It retains original unary f/header. Its inherited
65536(V+E+1) envelope explicitly includes3q padded-parser rewind steps.
The potentially huge cutoff is never expanded to its numeric value.

The whole core clones original DATA once to WORK, records TRACE and restores
the original head. Component HEADER0 remains original HEADER, DATA1 maps
to WORK, private t>=2 maps to t+2. PC labels are relocated injectively;
successful halt becomes local goto. Every runtime instruction is local
read/write/unit-move/goto/halt. Leaf port28 maps to30, so31 tapes suffice.

Every successful component returns public factor heads and erases private
bodies/guards, enabling reuse of the same27 module-private owners. Internal
commits alter only WORK. After all succeed, one V-bit copy writes original
DATA, erases WORK, restores heads and disposes WORK/TRACE guards. Rejection
can dirty scratch but cannot reach an original write before this commit.

HOME splits six codes/full DATA at B-relative2, blank guard1, permanent^0;
native ports map to3..33 and GUIDE is34. Successful repacking returns the
identical header and transformed body, erases copies and restores all35
heads before B1 scatter. Parked field and opaque exteriors are preserved.

The unchanged affine.py and join.py share an engine directory whose manifest
is the exact frozen affine manifest: all21 central pins plus five extra
translation/proof pins. Both original manifests/proofs/freezes are retained.
This installation changes no source bytes; regenerated predecessor graph
checks pin the same emitted tables under the shared manifest.

## Numerical promises and retained common-root corollary

The phase body rejects requested negation of a most-negative component;
copy/permutation of it is allowed. The C body retains actual w+2 numerator
rows and exact parity/range guards. No scaling, rounding or new grid is
installed. A simple sufficient reserve is input divisibility by2^(3f),
maximum M and2^(3f)M<=2^(w-1)-1. Unit phases/permutations preserve magnitude
and divisibility; each C axis spends at most one divisibility bit and grows
component maximum by at most2. Induction proves all actual prefix promises.
This stronger sufficient condition is not asserted for a selected producer.

The unchanged note in reference/prefix-bridge/ conditionally applies existing
#7000 review section5, blob3dd1af2285e597676725e85ad4f65e7ad326d695. If an
actual producer supplies the retained complete D-bit root row, all source
coefficient/grid/mass/height/exterior-context premises and a correct injective
9f-bit view retaining complementary root bits, completed exact prefixes
retain the same grid/range: y=sum c_nu U_nu x_nu implies
Vy=sum c_nu(VU_nu)x_nu in the same Gaussian-dyadic Clifford class. Its format
has fractional bits p+D and width p+h+2D+3. This is an application of the
retained theorem, not a new precision or producer theorem.

Partially written words, mixed scan buffers, accumulators, descriptors and
scratch need not be Clifford images and are excluded. Fully assembled and
committed components may inherit preceding/next complete-prefix bounds;
private arithmetic still needs its independently proved widened-helper
bounds. An arbitrary packet on a chosen grid does not supply the root-row
invariant. Packing/view/header/owner production, cutoff, helper validity,
cost/history and caller/nonleaf admission remain explicit. The included
bridge/review are disclosed AI review, not human or proof-kernel acceptance.

## Complete successful bill and rolewise history

Each local read/write/unit move/goto/halt costs one. Credited complete
envelopes include descriptors, copies, seeks, arithmetic, returns/retirement:

| Component | Complete ceiling |
|---|---|
|Joint guard|65536(V+E+1)|
|Fixed k-CNOT word|1024k f(V+1)+8192(V+E+1)|
|Nine-coordinate complete phase|65536(E+65V+1)|
|Positive first-slot C|65536(fV+E+1)|
|X0 with descriptor production/reversal|4096(V+E+1)|
|One outer transaction|31V+27|

A generic monomial has one phase, matrix word k<=99, and if b nonzero two
offset words of length<=10 plus X0. Its complete sum including outer staging
is at most4532255fV+94208E+94235, below2^24(fV+E+1). Use f(V+1)<=2fV and
V<=fV. Private increments sum phase256+matrix64+affine160+outer8=488<512,
times(V+E+1).

Actual24476 has73 CNOTs in8 words:26 right,33 left,2 offset,12 central
swaps. It has2 phase passes,3 C leaves,1 X0,1 guard and1 outer transaction:

`65536(V+E+1)+1024*73*f(V+1)+8*8192(V+E+1)`
`+2*65536(E+65V+1)+3*65536(fV+E+1)+4096(V+E+1)+31V+27`.

This is at most9000991fV+462848E+462875, below2^25(fV+E+1). No child,
offset descriptor, full copy, arithmetic or return is a free callback.
It is direct fV work; no faster nonleaf tariff or recurrence amortization
follows. History sums guard64+8words*64+3leaves*64+2phases*256+X0*32+outer8
=1320, below2048 times(V+E+1). Retired factors are not refunded. K_entry
includes older/opaque regions. Shorter clean calls at fixed origins retain
old maxima; new origins need actual interval unions/paid corridors. HOME
adds128(F+1) time/64(F+1) backing; B1/setup/program charges stay separate.

## Executed evidence and limits

The138933-location table passes all port/PC/unit-move bounds and has no
original DATA WRITE before commit. The139100-state HOME graph executes all
512 addresses at f1,w8, dense components divisible by8. The original-frame
oracle uses T470 T3*, not emitted factors. It returns in48976485 steps with
8206 final HOME writes only after primitive return; all35 heads/private
bodies/guards/exteriors restore. Visited increment143757 retains older history.

The f1,cutoff2 case rejects at189419 steps without public writes. A source-
constructed input completes right monomial,C0,S01 at21526897 steps with its
whole intermediate WORK checked, then C1 rejects an odd numerator at21833563
steps with zero HOME writes. Failure cleanup/retry is unclaimed. An executed
wrong-constant graph returns exactly i times the correct f1 answer. Changed
retained source bytes reject. Normal/-O replays compare exact receipts and
28 physical constant*f probes. The all-size proof is the preceding invariant
argument, not finite interpolation. No full f2 MOVE, all6310-event dispatcher,
owned lifetime, actual producer/view, recursive caller, assumption discharge
or new kappa is claimed.
