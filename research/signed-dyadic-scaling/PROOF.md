# A complete physical signed-dyadic scaling interface

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This is a written uniform finite-program proof with exact finite
corroboration, not a proof-kernel or complete supplier theorem.

## 1. Contract, including the original physical owner

Let P,Q,S be arbitrary positive integers, with Q odd, and V=PQS. Three
preserved canonical positive LSB-first binary descriptors encode P,Q,S.
The owner tape has V Boolean symbols in lexicographic [P]x[Q]x[S] order,
between distinct LEFT/RIGHT markers, with its head on the first bit.
The desired address permutation sends (p,x,z) to (p,a*x modQ,z), for
a in {2,1/2,-1,-2,-1/2}. Inverses are taken modulo odd Q; at Q=1 all
five maps are the identity. No runtime inverse calculation is free.

For each coefficient there are two fixed programs on fourteen tapes and
seven symbols. The out-of-place program preserves the owner, fills a
separately owned blank output, and returns its head to the first bit.
The in-place program transforms the ORIGINAL owner tape, preserving its
markers and returning its head. It does not relabel another bank as the
owner. Both preserve every descriptor, all unused tape contents/heads and
every coordinate spectator. Eight assigned private tapes must initially
be completely blank, at arbitrary independently translated origins.
Every private cell, marker and head returns to that same blank state.
Invalid input rejection has no cleanup guarantee. Inspecting one origin
does not certify an unbounded private tape is empty; emptiness is a premise.

The only executable operations are a scanned-symbol branch, one-cell
write, unit head move, fixed jump, halt and reject. Every executed
instruction costs one transition. Assembler parameters choose one of ten
fixed tables; no extent, coefficient magnitude, payload, callback, host
index or arithmetic operation is supplied to the assembler at runtime.

## 2. Runtime setup and the two buckets

Retained PR2776 binary-to-unary macros convert P,Q,S to three independent
unary counters, preserving all binary descriptors and returning the
temporary binary work interval blank. Checking Q's first binary symbol
is ONE enforces oddness; conversion enforces positive canonical encoding.

For doubling/half, scan the Q unary marks once, alternately appending a
mark to length counters A and B, beginning with A. Since Q is odd, the
counter lengths are m+1 and m for Q=2m+1. The final right marker is accepted
only in the odd state. For negation skip the first Q mark and copy the
remaining Q-1 to A's length counter; B's length is zero. All loop tests,
marker writes and head returns are literal instructions. There is no
binary division, rounded reciprocal or free split index.

Each record consists of S opaque Boolean bits. The retained `_copy_record`
copies them in their original order using an S-counter. Consumption writes
BLANK on each copied bucket bit. Segment and prefix loops are finite
unary loops on their own tapes; rewinding them is paid, not a host reset.

## 3. Doubling and inverse half

For every prefix, gather its first m+1 records into bucket A and its
last m records into B. Complete the gather over ALL P prefixes before
writing any owner bit. The two buckets together contain exactly V bits.
Write their end markers and rewind them.

The sorted output for multiplication by2 is A0,B0,A1,B1,...,A_m.
Indeed the first source range maps to even output indices 0,2,...,2m;
the second maps to odd indices 1,3,...,2m-1. The m-pair loop uses B's
unary length, then copies one final A record. Every bucket cell is
consumed once, all S positions inside a record remain in order, and
prefix order is preserved.

The inverse half program gathers alternating records into A and B,
then emits A's complete m+1 records followed by B's m. It is the exact
inverse permutation, including Q=1 and arbitrary suffix/prefix extents.
The required 1/2 coefficient is therefore implemented without preparing
the large integer (Q+1)/2 or invoking a unit shear that many times.

## 4. Negation without reversing record bits

Gather the whole owner, in source order, into bucket A. For each prefix,
copy its record0 directly. Scan forward Q-1 records to that prefix's
end. For each of Q-1 remaining records, move back S cells, copy that
record FORWARD while consuming it, then move back S cells again. The
successive emitted record indices are Q-1,Q-2,...,1. The source cursor
then lies after record0; scan forward Q-1 complete records to the next
prefix. Each scan is an actual nested unary counter loop.

This emits 0,Q-1,...,1 while preserving the order of all S bits within
each record. All traversals stay within the current prefix. At Q=1 the
three Q-1 loops are empty and only record0 is copied. The reused bucket
cursor never relies on a consumed bit's value; its motion is controlled
by the preserved counters. No stale tail survives beyond its final head.

## 5. Original-owner installation and signed composition

For in-place operation the gather source and final output are the SAME
physical tape. Its full contents have already been copied into A/B
before any overwrite. After gathering, explicitly rewind the owner
to its first bit, then overwrite every bit from the buckets. Consumption
and final erasure clear the owned buckets, including markers. The owner
retains the same LEFT/RIGHT positions and returns its original head.
No bank swap, source retirement, borrowed zero original owner or alias
oracle is assumed. This costs the extra full owner rewind and all bucket
storage/cleanup shown below. Only the assigned temporary buckets are clean.

For -2 and -1/2, link the completed positive program to an in-place
negation of its result. Every intermediate private tape is already
completely blank and returned; descriptors are preserved. For an
out-of-place first stage the second transforms that output tape, leaving
the original source untouched. For an in-place first stage it transforms
the same original owner again. The linked HALT becomes one fixed GOTO,
with no change to its transition charge. Negation commutes with doubling
and its inverse, so these are exactly the requested signed coefficients.
The ten coefficient/interface programs are fixed finite tables.

## 6. Complete transition bound

PR2776's positive conversion costs
24n-7 popcount(n)+15 bit_length(n)+12 <=44n. A rewind from a right
marker after h symbols costs3h+3. A length-l segment costs at most
(11+consume)Sl+10l+4. A record copy costs at most
(11+consume)S+4. These formulas include all local branches and unit moves.

For either one-stage program the following deliberately conservative
ledger is uniform. Each P,Q,S,PQ,PS and positive constant is bounded by V.

| Executed block | Bound |
| --- | ---: |
| Initialize eight private regions and optional output | 27V |
| All three binary conversions | 132V |
| Runtime odd-Q check | V |
| Build split or Q-1 counters and return Q counter | 20V |
| Full gather, all prefix/segment/copy loops | 40V |
| Check source end, mark and rewind both buckets | 12V |
| Extra original-owner rewind in the in-place case | 6V |
| Full emit, including all negative cursor scans | 110V |
| Output/source returns, final end checks and all erasure | 100V |
| Final halt | V |

The sum is449V, below600V per base stage. Two stages therefore cost at
most1200V, below the stated2048V allowance. We retain the larger integer
allowance rather than identifying measured fixture maxima with a proof.

Here are explicit counts for the nontrivial loops. Alternating split setup
costs8Q+6 and Q-1 setup8Q+2, both at most20Q. A paired prefix copies Q
records, rewinds its m-counter, and has at most3m+1 loop transitions.
Summing two segments or the paired loop and the P-counter gives the40V
gather and110V emit rows. For negation, one forward/backward record walk
costs at most7S+4, including a complete S-counter rewind. At a prefix the
initial seek, reverse-copy and final cursor restore cost at most
40QS-28S+38Q-22, including length-counter rewinds and the first record.
The P loop adds6P+4, giving at most40V+38PQ-28PS-16P+4,
which is bounded by82V and therefore by the110V ledger row. This also
covers Q=1, where all nontrivial walks are skipped.

Before clearing Q_COUNT the program explicitly seeks its right marker;
the doubling/half paths otherwise leave that unused counter at its first
symbol. This final seek is at most3Q+1. Every nonblank private cell is
then at or to the left of its current head. The retained eraser costs
4h+2 from relative head h. The bucket bits total V; unary lengths total
at most P+2Q+S; binary work is blank at its first cell. Their complete
erasures cost at most4V+4P+8Q+4S+48. Adding the Q seek, both possible
owner/source returns, end-marker/check instructions and halt is covered
by the100V row. No cleared region is removed from the space bill.

The bounds are source instruction counts, not host simulator runtime.
No coefficient-dependent number of whole-array shear invocations occurs.

## 7. Visited space, including both signed stages

Let B be the sum of the three descriptor bit lengths and M their maximum.
For a signed two-stage program, one bucket can grow to V in the negation
stage, while the other retains the earlier visited interval of at most V.
Source and optional separate output contribute at most2V. Unary-counter
visited lengths are bounded by P+3Q+S; the binary work interval by M.
All fourteen tape origins, markers, descriptors and unused head positions
are covered by

    4V + P+3Q+S + B+M +32 <=45V <64V.

This is a visited-interval union bound, including erased intermediate
buckets and counter tails. Independent tape translations do not change
the lengths. Arbitrary unused tape data are preserved and never inspected;
their unvisited far-away cells do not become allocated working space.

## 8. Actual source boundary and the family decision

The actual source PROGRAM has80 unit_scale sites with coefficient counts
24,24,16,8,8 for2,1/2,-1,-2,-1/2. Its interpreter updates one high
coordinate by `high[a]=high[a]*z modR`, preserving every other field.
Our binding authenticates that exact assignment and every literal site.
For the full high-coordinate fibre Q=R=q^(w-1), the source's odd-prime
premise makes Q odd. Group every earlier coordinate into P and every
later coordinate into S; low/header/ROW/payload spectators are opaque
members of those complete fibre extents. The new kernels implement
that exact coordinate permutation for any such supplied complete stream.

The source proof gives N=8f and10Nf=80f² scaling sites across both routes.
If site j has full volume V_j, their completed scaling cost is at most
2048 sum_j V_j transitions, with sequentially reusable private capacity
at most64 max_j V_j. At one common volume V this is163840 f² V. These
large sufficient constants are positive charges, not an optimized native
invoice. Descriptor GENERATION and the full packet-layout producer are
not supplied by accepting their canonical inputs.

The rest of the source family remains explicitly unresolved:224f²
ordered shifts (160f² later-target and64f² earlier-target),80f² ordinary
high swaps,2N² low-controlled carries, two finite low-type commits, one
canonical native invocation, low-cache generation/copy/clear and ROW
padding. Each borrowed swap retains two raw-body calls, three body
additive maps, an older-high interchange and complete ROW lifetime.
Whole#4814 compilation, primitive composition in the complete owner bank,
P3 reserve/recurrence/stock/precision/thresholds and supplier/outer
admission remain unknown. Unknown tariffs are not zero.

Decision: NARROW to completion of this entire physical operation inventory.
Do not infer a whole-route improvement or another automatic construction
round. A next task must select a different named missing contract and its
full allowance. No paid call, selected certificate or kappa changes here.

## Evidence versus proof

All odd Q, all positive P/S and arbitrary payloads follow from the unary
invariants and the explicit loop ledger. Finite tests include both
execution engines, every interface/coefficient, exact actual-Q125 source
sites with compressed spectators, full owner inverse roundtrips and
semantic/physical controls. They do not materialize the actual complete
high cover or prove the remaining caller contracts. The dense interpreter
and sparse machine are retained PR2776 implementations, reused as two
disjoint execution engines, not claimed as new independent code.
No independent human or formal proof-kernel acceptance is claimed.
