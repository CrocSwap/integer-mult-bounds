# Fanout with a limit on unfinished outputs

**Recursive-interface scheduling tool and scoped optimum; no new kappa.**
PR889 shares source computation across a dirty fanout. Its minimum words can
leave several outputs unfinished at once. This package emits a schedule with
at most W unfinished outputs and permanent commits, for any k >= 0 and W >= 1.
It needs exactly

```
N_B = 2 ceil(k / (2W)) complete shared-source calls,
N_Ai = 2 complete calls per output.
```

These counts simultaneously minimize every positive fixed, sign-symmetric
query bill in the stated alphabet. The five-output, cap-two fixture costs
**404 primitive child calls versus 716 for separate restored outputs**. The
unconstrained optimum costs 300, but needs at least three unfinished outputs.
All three use four borrowed dirty rows. The cap concerns output availability;
it is not a physical-memory reduction or a measured speedup.

Reproduce with Python 3.11+ and the standard library:

```sh
python3 -I -B research/bounded-pending-fanout-seed53/verify.py
python3 -I -O -B research/bounded-pending-fanout-seed53/test_package.py
```

The first prints `PASS_BOUNDED_PENDING_FANOUT`, 529 family cases, 189 dense
cases, 14 rejected controls, and leaf counts 404/300/716. The second prints
`PASS_BOUNDED_PENDING_PACKAGE`, five rejected file corruptions, identical
regeneration and an isolated optimized relocation pass. `schedule.py` prints
the exact committed certificate to stdout and never overwrites a file.

## Contract

Fix distinct full length-L arrays x, z and y_0,...,y_(k-1), all initially
arbitrary. Fixed exact characteristic-zero additive linear maps A_i and B
need not commute or be invertible. The requested endpoint is

```
x unchanged; z unchanged; y_i += A_i B x.
```

The only root queries are `B^s: z += s B x` and
`A_i^s: y_i += s A_i z`, with s equal to +1 or -1. Each query preserves
its source and unrelated data, restores its private work, returns its tape
heads, and has an increment independent of the old target. Negative queries
are complete inverse shear words. No combined output query, direct product
query, extra root connector, free copy, frame change or overwrite is allowed.
All source/output rows are excluded from child scratch.

An output becomes unfinished on its first A_i query. An explicit commit is
allowed only after the output equals its requested final value for arbitrary
initial data. After commit, no later query may touch that output. At every
root or primitive boundary, at most W outputs may be unfinished. The emitted
commits occur at complete child returns, never partway through a child.
A consumer may read committed outputs; this package does not price or execute
the consumer. Unstarted outputs retain their original values. Committed rows
remain reserved here; no reuse as recursive scratch is assumed.

The word is fixed independently of data. The lower bound requires universal
correctness for admissible maps and inputs, and characteristic zero. Special
maps, finite-characteristic torsion, approximate or nonlinear maps, callbacks
which alter x/coefficient state, and other query alphabets are outside it.

## Why the cap forces the shared-source bill

Use PR938's exact coefficient representation at every prefix:

```
z = z_initial + q B x,
y_i = y_i_initial + e_i A_i z_initial + f_i A_i B x.
```

A B query of sign s changes q by s. An A_i query of sign s changes
e_i by s and f_i by s*q. Final correctness requires q=0, e_i=0 and f_i=1.
These requirements already follow by specializing to integer scalars with
identity maps and varying x and z_initial independently.

Discrete summation by parts gives

```
1 = f_i(final) = - sum_over_B_queries s * e_i(before that query).
```

Indeed, each A_i event contributes q*delta(e_i) to both delta(e_i*q)
and delta(f_i); each B event contributes e_i*delta(q) to delta(e_i*q).
The endpoint product e_i*q is zero at both ends. Thus every output must
have nonzero e_i at some B event. Such an output is necessarily unfinished:
before its first query e_i=0, and at and after a valid commit e_i=0.
At most W outputs can be charged to any one B event. Therefore k <= W*N_B.
Restoring q=0 requires equally many positive and negative B calls, so N_B
is even. Hence N_B >= 2 ceil(k/(2W)).

Each output needs at least one A_i query for f_i=1, and a zero signed total
requires at least two. This argument allows arbitrary extra A queries,
nonzero excursions of q, idle delays and any output order. It is not restricted
to the emitted two-readout words or to PR938's minimum-word census.
For k=0 the empty word is optimal.

## Attaining schedule and commits

Partition the ordered outputs into consecutive groups of at most W. Start
q=0. Alternate B signs +1,-1,+1,... across the groups. For a group G and its
sign s, emit

```
for i in G: A_i^(-s)
B^s
for i in G: A_i^s; commit i
```

The two values read from z differ by s Bx. Each output increment is
`-s A_i z_before + s A_i(z_before+s Bx) = A_i Bx`.
All outputs in G commit before any output in the next group opens. The
connector alternates between z_initial and z_initial+Bx. If the number of
groups is odd, append one B^- query after their commits. The total is
`ceil(k/W) + (ceil(k/W) mod 2) = 2 ceil(k/(2W))` B queries.

The lower bound and this construction prove the minimum query bill

```
Q_min = 2 sum_i c_Ai + 2 ceil(k/(2W)) c_B,
```

for positive complete prices equal between signs and fixed across states and
ports. This is optimal in the stated alphabet, not over arbitrary circuits.
Word selection, admission and representation conversion remain separately
charged. Their costs are not optimized by this theorem.

## Complete recurrence and fixture

Let c_F(L,w) include every source/coefficient access, full-row child operation,
target update, local frame adapter, private-work restoration, per-query dispatch
and head return, with a common fixed price for both signs. Let P_F pay reusable
coefficient preparation, I pay admission/layout, and D pay group/control and
stored-program construction/access not already in c_F. Then the emitted bill is

```
C = I + sum_F P_F + D + N_B c_B + 2 sum_i c_Ai.
```

No full-row volume is divided by the output count. If an external representation
needs copies or frame changes, their cost belongs in I or c_F. The abstract
schedule emits none. Output observation is optional and separately paid.
The list emitter uses O(k+N_B) root records and a commit table of k indices.
A streaming dispatcher instead maintains an output index, group endpoint and
one sign, charging O(k+N_B) index/branch events on O(log(k+W+2))-bit counters.
It still pays each referenced factor descriptor and each emitted child.

For factors in application order, split F into right prefix R and left suffix
S. On a new dirty child connector w, emit R(x,w), S(w,y), inverse(R)(x,w),
inverse(S)(w,y). With each child already restored/head-returning:

```
C([f]) = complete leaf price plus leaf dispatch,
C(F) = 2 C(R) + 2 C(S) + node dispatch,
h([f]) = 0; h(F) = 1 + max(h(R), h(S)).
```

The literal inverse reverses all primitive instructions and negates their
signs. Balanced contiguous splits have h(n)=ceil(log2 n) and
ell(1)=1, ell(n)=2ell(floor(n/2))+2ell(ceil(n/2)). Siblings reuse only fully
restored private scratch. Peak dirty rows are `1+max_F h(F)`, where the one
is the root connector. Recursion/control metadata and private leaf work are
additional. No clean full-length row is assumed.

Seed 53 chooses k=5, W=2, B of seven factors and A lengths 2,3,4,5,6.
Their exact balanced prices are 52 and 4,10,16,28,40. There are 27 independent
primitive operators, six external rows and four dirty rows.

| Schedule | Peak unfinished outputs | B queries | A queries | Primitive calls |
|---|---:|---:|---:|---:|
| Cap two | 2 | 4 | 10 | 404 |
| Unconstrained optimum, arranged at its minimum peak | 3 | 2 | 10 | 300 |
| Separate fully restored outputs | 1 | 10 | 10 | 716 |

The cap-two schedule saves six complete B calls against separate restoration.
It costs two more B calls than the unconstrained optimum. All programs and
commit positions are literal in CERTIFICATE.json. The separate comparator is
deliberately the usual per-output restored call, not the optimum at cap one;
the theorem gives six B calls and 508 primitive calls for k=5,W=1.

For a concrete exact realization, supply the 27 dense integer L-by-L matrices
and ten mutable rows, with entries initially bounded by H and D respectively.
Compute each dot product in an admitted clean scalar accumulator, update its
target and uncompute the dot product using the unchanged source. Restore loaded
coefficient/source/product temporaries as well. This pays two dot-product passes,
including 2L^2 products, 2L^2 accumulator additions, L target additions and
at least 2L^2 coefficient and source reads per leaf. Temporary loading/clearing,
index arithmetic and instruction traffic are additional, not free erasures.

Place the data/coefficient words on one tape of S=10L+27L^2 word cells and use
separate scalar/control work. A direct move-to-address implementation with
reloads/unloads can use at most 16L^2+4L+2 addressed data visits per leaf,
including its final head return; each move spans at most S cells. Its paid
bit-time is bounded by
`O(S*(L^2+1)*w + L^2*M(w) + L^2*w*log(S+2))` plus instruction access,
where M includes clean multiplication workspace/cleanup. A sufficient common
signed width for all three programs is
`2+ceil(log2(max(1,D,H)))+716*ceil(log2(1+L*H))`.
This follows from the per-leaf infinity-norm growth factor 1+L*H and also
bounds dot-product intermediates. Initialize and restore the O(1) scalar words
and O(w) arithmetic work in I and the leaf price. Input matrix production is P.
These are conservative implementation bounds, not a physical tape benchmark
or an improvement to the selected supplier.

## Independent checks and limits

The scheduler's search space is empty: it emits a proved formula and fixed
construction. The verifier does not import predecessor executables. Its free
noncommutative module keeps all ten arbitrary input rows, verifies every commit,
all 46 complete child boundaries, the full map and literal inverse. At each
child return it checks the intended ordered product and every restored private
row; other external ports are forbidden throughout the child. Its dense integer interpreter independently
checks every basis column and a mixed dirty input at L=1,2,3 for all three
expanded programs, 189 forward cases and their inverses. The family check covers
k=0..32 and every W=1..max(1,k), 529 cases, including rational query prices.

A separately written breadth-first reachability checker covers every shorter
word and finds minima 4,6,6,10,8 for (k,W)=(1,1),(2,1),(2,2),(3,1),(3,2).
Its state is q, the number of unopened outputs, the multiset of active pairs
(e_i,f_i), and the number permanently committed. It considers both signs for
every active query and B, opening under capacity, and either committing or
keeping an active output when its pair reaches (0,1). Sorting active pairs is
a label-symmetry quotient preserving reachability; no labelled-word counts
are claimed. There is no heuristic pruning. It stops at the first complete
endpoint. This finite check supports, and does not replace, the written bound.

Controls reject premature root/leaf commits, excess pending capacity, missing
connector restoration, sign changes, wrong factors, unpaid leaves, aliases and
invalid domains. A nonlinear scalar control returns 7 instead of 1 when
A(z)=z^2, x=1 and z_initial=3; linearity is essential. Package controls mutate
actual files and test a changed producer together with its regenerated bad
certificate, so comparison to a frozen certificate is not the only guard.
One additional control swaps zero-based primitive positions 79 and 80 across
a child return. The full dirty endpoint, literal inverse and all commits still
pass, but the per-child restoration checker rejects it. Thus those final-state
checks alone would not establish the required recursive interface. This is a
control on this package's emitted word, not a defect attributed to a predecessor.

PR889 is credited for the interface/commutator and unrestricted weighted
minimum. PR938 is credited for the exact coefficient state and every equality
case. Its two-B equality words already imply that unrestricted optimal work
can be arranged with ceil(k/2) pending outputs. This package claims that fact
only as inherited context. The addition is an emitted scheduler, commit checker
and all-word lower bound below that capacity, including longer words. PR982
and PR1103 change output borrowing and remain distinct.

The selected base is `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`, with PR1094's
conditional kappa `836330098538459/500000000000000000`, bound by the complex
supplier. No occurrence of this abstract fanout has been physically admitted
inside that supplier. Compiler/common-label realization, hosting, full-row
volume, external precision/tape integration and outer analytic assembly remain
unresolved or inherited. Finite checks are not a formal multiplication theorem,
an independent human review, a new kappa, or a speed claim.

See CLAIM.md for the rejected F3 line and single bounded pivot, SOURCES.json
for original Git/SHA256 pins, and NOTICE.md for preserved credit and license.
