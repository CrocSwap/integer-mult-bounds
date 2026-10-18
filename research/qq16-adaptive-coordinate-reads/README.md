# QQ16: adaptive coordinate reads still need 66 ports

**Scoped proof and exact finite premises; no supplier or new κ.**
On the rational hidden-input family of
[PR2354](https://github.com/CrocSwap/integer-mult-bounds/pull/2354), every
deterministic reader that always recovers the original selected A defect
needs **at least 66 distinct source-port reads on every input**, even when
its port choices and stopping time depend arbitrarily on earlier reads.
The same statement holds almost surely for a randomized reader that
terminates and is exact with probability one for each rational input.

There are **exactly 45 possible read sets at a successful 66-read leaf**.
All contain these 22 ports:

```text
1,2,3,4,5,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109.
```

The other 44 reads choose all but one of 45 explicitly listed ports.
PR2354's attaining set is one choice. Port 77 can replace any of 44
specified members of that set. The sets and the exact recovery relation
are in [RESULT.json](RESULT.json), fields `eligible_optimal_ports`,
`optimal_omissions`, and `coordinate_relation`.

The fixed-set threshold and underlying rank-66 family are credited
predecessor results. The new delta is the adaptive/zero-error implication,
the complete classification of optimal terminal read sets, and explicit
family decoders for all 45 sets. Exact rechecking of the rank is a premise
check, not a claim to have discovered that rank independently. The claim
is in [discussion #2205](https://github.com/CrocSwap/integer-mult-bounds/discussions/2205#discussioncomment-18942816).

## Exact observation contract

Use the actual 8-by-112 rational centre matrix R, selected sets A and T,
and ordinary 96-port set U from the retained
[QQ16 packet](../joint-query/README.md). Let r_p be column p of R and
b_p the first local chart axis of port p. For an owner d in the finite
regular cover group G, put

```text
f_b(d) = bit_0(d b), interpreted in Q,
V = ker(R_U) subset Q^96,
h_p(d) = c_p f_(b_p)(d),       c in V,
H(c)(d) = sum_(p in U) r_p c_p f_(b_p)(d).
```

The fields are constant in payload coordinates. This is the exact
first-axis family of PR2093/PR2326/PR2354. The actual routes obey
`rho_s(p)b_p=e_(9+8(s-1))`, so `B_s h=0` for every s=1,...,8 and every
owner whenever `R_U c=0`. The original selected input is
`X_A=-P_(0,A)H(c)`, with `Y_A=-X_A`, `X_U=h`, `Y_U=0` and all other
fields zero. The selected section is invertible: the packet has
`R_A R_A^T=4I`. Recovering this original A defect is equivalent to
recovering H(c).

Under the credited ordered F0/B1 maps, F0 leaves `X_U=Y_U=h` and all
selected fields zero. B1 leaves only `Y_U=h`. The retained ordinary tail
has zero selected/completed-X/history observations and finally places h
in the former-Y endpoint, which is outside the permitted observation
contract. This inherited family argument is explained in this account's
[PR2326](https://github.com/CrocSwap/integer-mult-bounds/pull/2326) and
PR2354; this package rechecks the route and rank premises but does not
replay their full native schedule.

Here a reader can request any **complete initial ordinary array** h_p,
one port at a time, without modifying it. It can retain all responses,
perform arbitrary computations, choose the next port adaptively, and
stop based on its transcript. The unmodified QQ16 observations above may
be supplied for free; they are zero throughout this family. Repeated
reads count only once. No other input-dependent information, header,
dense query, source preprocessing, or changed physical call is available.
In particular, this theorem does not assume that a complete dense
`B0 h` array has one scalar's information.

For each p the function f_(b_p) is nonzero at a certified actual owner.
Thus h_p is equivalent to the one rational scalar c_p: the complete
array is determined by c_p, and reading a nonzero entry recovers it.
The oracle model grants that scalar for free. It is a favorable
information relaxation, with no charge for native access or retention.
The claim concerns this side-effect-free reader, not arbitrary physical
adaptive interventions inside the QQ16 word.

## Transcript-fiber theorem

Let V be a finite-dimensional vector space over a field F. Let H be a
linear target and let q_1,...,q_N be scalar linear query functionals on V.
An exact deterministic oracle algorithm receives no input-dependent
information except answers to adaptively selected q_i. It terminates
with H(c) for every c in V. Its internal computations and output map
need not be linear, continuous, or bounded in cost.

Fix any input c and its finite terminal transcript, and let S be the set
of queried indices. Write `Q_S=(q_i)_(i in S)` and `K_S=ker(Q_S|V)`.
For every v in K_S, the run on c+v has exactly the same transcript.
Indeed, its first query is the same; if the histories agree through a
step, its next query or stopping decision is the same. Every query on
the fixed path lies in S and has the same answer on c and c+v. Induction
reaches the same leaf and output.

Exactness on both inputs therefore gives

```text
H(K_S)=0,      ker(Q_S|V) subset ker(H|V).                 (1)
```

Consequently H factors through Q_S and

```text
|S| >= rank(Q_S|V) >= rank(H|V).                          (2)
```

This holds for **every terminal path**, not only the zero-input branch
or the worst case. Conversely, a fixed S satisfying (1) admits a linear
decoder for H; define it on Q_S(V) using H(c), which is well-defined by
(1). Adaptive choice cannot manufacture information about a direction
in the terminal query kernel.

For QQ16 the checked rank is 66, so (2) excludes every path with fewer
than 66 distinct port reads. The original fixed 66-port set attains
family decoding, proving a sharp threshold in this oracle contract.

### Zero-error randomization

Assume one input-independent probability space of random seeds. For
each c in the **countable** rational space V, the reader terminates and
returns H(c) with probability one. Intersect these full-measure events
over all c in V. Countability gives a common full-measure set of seeds
for which the deterministic seeded reader is total and exact on all V.
The preceding theorem applies to each such seed and every input.
Thus at least 66 distinct reads are required almost surely, and the
expected count on each input is at least 66.

The statement includes the optimal-set classification below on every
66-read path for these seeds. It makes no bounded-error assertion and
does not silently interchange an uncountable family of probability-one
events. Input-dependent advice or side channels violate the contract.
The all-input assertion is for V over Q; it does not claim the same
pathwise minimum on an arbitrary finite, bounded coefficient promise.

## Source-bound finite premises

Group the ports by their first axes. If C_b is one group, let
`L_b(c)=sum_(p in C_b) r_p c_p`. H factors through the direct sum L of
these group maps. The actual source has 47 groups. The axis-2 group C
has 30 columns and rank eight; all other groups have independent
columns, 66 columns in total. Hence `rank L=74`.

Vectors supported on C with `R_C c_C=0` form a 22-dimensional subspace
K of V and have H(c)=f_2 R_C c_C=0. Also `dim V=96-8=88`. Therefore
`rank(H|V)<=88-22=66` for the **whole owner array**.

For a matching lower bound, the verifier constructs an integer basis
N of V and evaluates H on the 17 actual owners used by PR2354:
identity and `rho_1(p)` for p=0,...,15. The resulting 136-by-88 matrix
has a 66-by-66 integer minor with determinant

```text
174085318024506601157689344.
```

The receipt includes the minor, its original row and basis-column
indices, and a digest of the reproducibly constructed basis N. Exact
rational elimination selects it; fraction-free integer elimination
checks the determinant with every division checked. This is a direct
certificate on V, complementary to the predecessor's rank-74 certificate
on the whole coefficient space. A nonzero evaluation minor proves a
lower bound for the complete owner map; the matching upper bound is the
all-owner factorization above. No independence of formal bit functions
or sampled-owner extrapolation is assumed. We have proved

```text
rank(H|V)=66,       ker(H|V)=K.                           (3)
```

## All 45 optimal terminal sets

If an exact leaf has |S|=66, (1), (3), and rank-nullity imply
`ker(Q_S|V)=K`: both kernels have dimension 22. In particular, every
queried coordinate must vanish on K. The exact source census gives:

* Every coordinate outside C vanishes on K, since K is supported on C.
* Each of the 29 coordinates in `C minus {77}` varies on K. The receipt
  supplies a kernel vector with that coordinate nonzero, and deleting
  its R_C column leaves rank eight.
* Coordinate 77 vanishes on K. Deleting that column reduces rank to seven.

Thus every optimal S is a 66-subset of the 67-element set
`J=(U minus C) union {77}`. The single dependence among these 67
coordinate functionals on V is particularly simple. Set

```text
w=(-1,0,1,0,1,0,1,0),
alpha_p=(w r_p)/(-4),             p in U minus C.
```

The checker verifies that w annihilates `R_(C minus {77})`, while
`w r_77=-4`. Therefore `R_U c=0` gives

```text
c_77 + sum_(p in U minus C) alpha_p c_p = 0.              (4)
```

Exactly 44 of the 66 alpha_p are nonzero, all in `{1/2,-1/2}`. The
original 66 coordinates `U minus C` are independent on V: H factors
through them and has rank 66. Thus (4) spans the entire dependence
space on J. Removing one coordinate q from J leaves an independent
66-set exactly when its coefficient in (4) is nonzero. This gives
**45 sets**: omit 77, or omit one of those 44 ports. Omitting one of
the other 22 ports leaves query rank 65 and cannot recover H.

The verifier checks all 67 candidate ranks separately. Any 66-read
adaptive leaf outside J is already excluded by its explicit nuisance
vector in K. Together these arguments exhaust all `choose(96,66)`
possible read sets without enumerating them. Adaptivity may choose
among the 45 successful leaves, but cannot reduce the count or use a
29-coordinate nuisance direction at an optimal leaf.

### Explicit attaining decoders

Let S0=U minus C. Since all unread first axes equal 2 and R_U c=0,

```text
H(c)(d) = sum_(p in S0) r_p c_p [f_(b_p)(d)-f_2(d)].     (5)
```

This is an all-owner identity. It reconstructs H from the 66 scalars in
S0, without reconstructing the 30 unread coefficients. If a successful
set omits q in S0 and reads 77 instead, use (4) to obtain

```text
c_q = [-c_77 - sum_(p in S0 minus {q}) alpha_p c_p]/alpha_q
```

and apply (5). Every division is by a nonzero rational. The verifier
checks (5) on all 88 kernel-basis vectors and all 136 evaluation rows,
and checks every exchanged decoder on all 88 basis vectors. Its formal
proof covers every owner. Finally apply `-P_(0,A)` if the requested
output is the original selected A input rather than H.

These are family decoders only. They do not establish recovery on a
different hidden family or arbitrary QQ16 inputs, legal native final
reads, a restored physical controller, or any favorable recursive bill.

## Reproduction and evidence boundary

Python 3.12 and the standard library suffice:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-adaptive-coordinate-reads
python3 -I -O -B research/qq16-adaptive-coordinate-reads/verify.py
```

The direct replay prints:

```text
PASS_QQ16_ADAPTIVE_READS defect=66 optimum=66 optimal_sets=45 nuisance_coordinates=29 controls=11 no_new_kappa
```

The replay is read-only. `--emit NEW_PATH` creates a receipt exclusively.
The whole canonical receipt, including JSON scalar types, must agree.
Source bytes and the consumed archive member are authenticated before
arithmetic; main-file pins and Git blobs are in [SOURCES.json](SOURCES.json).
No pending-PR executable is required or imported.

The 11 rejecting controls include a singular minor, wrong determinant,
identity-owner/routing shortcuts, an omitted attaining coordinate,
wrong decoder sign, the false 65-read and unique-set claims, a wrong
kernel-constant assertion, a singular exchanged read set, and a JSON
type mutation. A separate exhaustive decision-tree control over 16
binary inputs considers every adaptive branch choice (147 distinct
cells): two pair-parity targets with five scalar queries require three
reads even on average. A dense vector query reduces that toy count to
one; a nonlinear OR target permits shorter paths. These controls expose
the observation and linear-target hypotheses; they do not prove the
rational infinite-domain theorem.

All results are author-checked, with substantial AI assistance. The
proof is written mathematics, not proof-assistant formalization. The
rank, route and decoder checks do not reexecute native QQ16 children,
the full selected supplier, all-size precision or the outer multiplier.
The count 66 is neither per owner nor a recursive-rank/native-line
tariff. No selected-frontier change or independent human review is claimed.

## Open next questions

1. **Which of the 45 family-optimal sets has a favorable native access
   bill, and does it detect other hidden families?** The new classification
   narrows that search to a finite list. All 45 sets omit the same 29
   ports `C minus {77}`. A separate hidden-input witness supported there
   would defeat all 45 sets at once. First check that precise support
   and the full ordered observations, then price any surviving change.
   Family sufficiency is the blocker; the complementary second-axis
   investigation tests the original set. That separate witness is not
   checked or incorporated into a stronger bound by this package.
2. **What quantitative bound holds for bounded-error readers?** The
   zero-error countable-intersection argument does not answer it. First
   specify an input distribution and success criterion and derive a
   distributional decision-tree bound. Arbitrary rational inputs have no
   preferred uniform distribution, so an unstated average-case model
   would not be meaningful.

Structured questions and the task card are in [TASK.json](TASK.json).

## Credit and exact predecessors

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

* **kyzer1023, PR2354**, head
  `308ebc7405303bb7ed91b012bb705949c6091a16`: whole-owner rank 74,
  defect 66, the 17-owner certificate idea, and the fixed-set family
  threshold. Its exclusion of adaptive reads is the changed premise here.
* **commdata2338, PR2326**, head
  `fb7d64cd4a51c49bc56920305b0aca64011a420c`: coordinate-access contract,
  eight-dimensional identity-owner defect, and the threshold handoff.
* **Adam Gall, PR2093**, head
  `8b21a900eb520e4f11ea177b310f66316f8e8983`: common-axis rational
  bit-function family, initial A cancellation and retained-tail argument.
* **Ali Romman, PR1969**: local QQ16 contracts, actual route packet,
  native frame conventions and original lost-query witness.
* **Cinna Davis, PR2216/PR2268**, and **EdDiboi's parallel fixed-set
  parity-subspace work**: the shear/tap question and complementary
  fixed-coordinate threshold evidence. The selected-shear acts trivially
  on this family and is not charged as a new construction here.

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority
revision 4. The selected result and all frozen inputs are unchanged.
Retain the QQ16 [NOTICE.md](../joint-query/NOTICE.md) and original
construction lineage. New proof and code are Apache-2.0. OpenAI Codex
did the derivation, implementation, checking and writing; no independent
human review is claimed.
