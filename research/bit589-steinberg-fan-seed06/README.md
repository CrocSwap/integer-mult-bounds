# Adjacent corrective expansions cannot improve PR589's bit rank bill

**Scoped computer-assisted negative result. No new κ.** An extra XOR can
sometimes let a wire skip an intermediate frame, reducing recursive work.
For the 316 adjacent three-wire chains specified below in PR589, this does
not help: every legal three-gate corrective expansion has the same or a
higher complete rank bill. The intermediate frames may be arbitrary rational
subspaces, including ones absent from the supplied frame catalogue.

This is independent, narrower evidence for PR933's remark that its inverse
expansions are neutral. The new evidence is a rational flag reduction and an
integer concavity certificate for **all exponents `0 < a < 1`**, checked again
by a separately written integer implementation. It is not a claim that
Steinberg expansion, or this obstruction, was first suggested here.

| Completed coverage | Exact result |
|---|---:|
| Elementary gates in the fixed phase-A word | 2,130 |
| Eligible adjacent pairs | 316 |
| Corrective orders (three per pair) | 948 |
| Feasible rational rank triples | 1,671 |
| Schedules with exactly the baseline paid profile | 982 |
| Schedules with strictly higher concave cost | 689 |
| Improving schedules | 0 |
| Distinct local histogram deltas | 19 |
| Full scalar replays, forward and inverse, on 661 dirty columns | 1,898 |
| Explicit full-word ADD bill, with literal cleanup rebuilt | 24,305 → 24,307 |

The last line counts the additional A gate **and** its inverse in C. The
nine COPYs, their ranks, all source accesses, all 439 helpers and the physical
hosting remainder are retained. No new supplier is proposed for adoption.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -I -B research/bit589-steinberg-fan-seed06/verify.py
```

Expected final line:

```text
PASS_BIT589_STEINBERG_FAN pairs=316 orders=948 rank_schedules=1671 improving=0 controls=8 no_new_kappa
```

This rebuilds every certificate field, checks the complete local scalar words
in both directions with explicit COPY/ERASE, checks the retained global
histogram, runs eight controls and invokes `independent.py`. The latter imports
no producer, tuner, frame optimizer or primary verifier. It uses primitive
integer row elimination, coefficient-kernel intersection dimensions, all
eight Boolean inputs to derive the three corrective orders, and sorted-rank
majorization. The primary geometry uses rational RREF and orthogonal
complements; its cost check uses integer truncated-rank sums.

Additional admission tests and the registered hook are:

```sh
python3 -I -O -B research/bit589-steinberg-fan-seed06/test_package.py
python3 scripts/research_package.py --package research/bit589-steinberg-fan-seed06
```

The 18 tests include altered source bytes, missing coverage, duplicate orders,
false intersection dimensions, same-mass false histograms, forged slacks,
missing scatter reads, omitted cleanup and invalid frame containment.
Recompressed certificates are accepted by decoded content. No assertion is needed for scientific checks;
optimized Python does not remove them. See [VALIDATION.md](VALIDATION.md) for
executed commands and limitations.

## Exact scope

Flatten each phase-A gate's source list in its **stored order**, preserving
its frame. Choose two **adjacent** elementary gates on exactly three distinct
registers, where exactly one gate writes a source read by the other. There
are 316 such pairs; none touches a retained total. Other two-register or
commuting pairs are outside this class.

Over F2, with distinct `i,j,k`, the identity is

```text
j ^= k; i ^= j  =  i ^= j; i ^= k; j ^= k.
```

The correction `i ^= k` commutes with each of the other two gates. It may
therefore occur first, middle or last while the original pair is reversed.
The opposite chain orientation is included too. These are precisely the
three permutations of this corrective gate and the reversed original pair
that reproduce the old map. No gate is moved across a surrounding contact.

Each new gate may have its own rational subspace of Q^8. Every wire must
follow nested subspaces from its preceding fixed contact to its following
fixed contact. All other frames and operations, including the phase-B word,
scatter, start/final frames and COPY frames, are fixed. C is rebuilt as the
literal reverse of the z-destination A/B gates at the full frame. There are
no new registers or uncharged recursive calls. Final movement to the next
fixed contact is included in every local histogram.

The source stores C as the reverse of compressed multi-source gates, keeping
their sources in stored order. Sources added to a common target commute.
The verifier checks this grouped reversal and the full C/final frames before
using the equivalent elementary reversal. Splitting or reversing those
same-frame commuting additions changes neither their count nor the rank bill.

The arbitrary-rational model is a relaxation of the finite bitE8/1 frame
catalogue and of any additional realization requirements. Excluding gains
in this relaxation also excludes them in those narrower models. This does
not assert that every rational frame is physically admitted by the compiler.

## Why finitely many ranks cover every rational frame

Fix one of the 948 corrective orders. Its operand pairs are the three edges
of a triangle. Consecutive gates share a register, so their frames satisfy
`F1 ⊆ F2 ⊆ F3`. Write `P_r` for a wire's preceding frame and `Q_r` for its
following fixed frame. Define actual rational subspaces:

```text
L1 = sum of P_r for the first gate's two operands
L2 = sum of P_r for all three operands
U2 = intersection of Q_r for all three operands
U3 = intersection of Q_r for the last gate's two operands.
```

The verifier checks `L1 ⊆ L2 ⊆ U2 ⊆ U3` exactly in every case. Both original
gates have the same frame, which is a witness between L2 and U2; the independent
checker verifies its actual containment as well. These intersections are
computed as vector subspaces, not intersections of the listed root-line sets.
A test exhibits an intersection with no common listed line and positive rank.

Every legal schedule necessarily satisfies

```text
dim(L1) <= d1 <= d2 <= d3 <= dim(U3)
dim(L2) <= d2 <= dim(U2).
```

Conversely, extend a rational basis successively along
`L1 ⊆ L2 ⊆ U2 ⊆ U3`, and let `Fj` be its first `dj` vectors' span.
These frames satisfy all entry, inter-gate and exit containment requirements.
Thus the enumerated integer rank triples characterize exactly the nested
rational-subspace relaxation, with no coefficient-height restriction. Any
actual frames of the same ranks have the same paid rank increments.

The certificate lists each pair, its entry/exit frames, the four flag
dimensions, every rank triple and its full affected-wire histogram. The
1,671 triples are **rank classes**, not 1,671 sampled rational frames.

## Exact cost proof, including the retained fallback

Let `n_r` be the candidate's affected-wire histogram and `b_r` the old one,
including the exit climb. Both have the same total rank because movement
telescopes along each wire. For each integer `t=1,...,8` the certificate checks

```text
S_t = sum_r (n_r - b_r) min(r,t) >= 0;   S_8 = 0.
```

For any concave tariff `f` on the integer ranks with `f(0)=0`, put
`s_t=f(t)-f(t-1)`. The exact identity

```text
f(r) = s_8 r + sum_{t=1}^7 (s_t-s_{t+1}) min(r,t)
```

expresses the cost difference as a nonnegative combination of the S_t;
the rank-mass term cancels. For `f(r)=r^(1-a)`, `0<a<1`, all seven coefficients
are strictly positive. A nonzero equal-mass histogram difference has some
nonzero S_t. Hence the 689 nonidentical schedules are strictly worse for
every such exponent; the other 982 have identical profiles. This proof uses
no floating-point price, uncertified root search or numerical tolerance.

The selected local profile remains
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`, with mass 5,129 including the
nine rank-seven COPY calls. The pinned nine-stage model has

```text
H = 288 * local + {2:13920,4:14208,6:14208,7:21312,42:288}
m = 64, W = 28416, deficit = 10272.
```

Its main moment is `sum H_r (r/64)^(1-a) / 28416`.
The pinned additional charge is
`32*64*sum(H_r)*64^a / (10^16*28416)`. Since `S_1` is the change in child
count, this additional charge cannot decrease either. Fixed remainder and
positive scaling preserve the inequality. Therefore none of these expansions
can raise the exact bit moment root under that retained contract. The
certificate binds the baseline histogram to PR589's receipt; it does not
rerun the hosted supplier or claim a new root approximation.

As a positive control, another legitimate boundary flag permits
`{1:4} -> {1:2,2:1}` with gate ranks `(0,1,2)`. Its `S_1=-1` is detected.
Thus the result is specific to the pinned word's contacts, not a universal
claim that adding a corrective XOR never helps.

## Pins, overlap and attribution

Base: **`92da4d718f1d4cf8de4e6ee947ddc7b180ce1c31`**. The selected record at
this base gives conditional κ **0.001672660197076918**, PR1094, with the
unchanged PR589 bit supplier on PR555. The complex side binds. The historical
selected record is provenance only and is not a live replay input here.

Runtime source files and their Git blob/SHA256 pins are in
[SOURCES.json](SOURCES.json). In particular, PR589 is pinned at
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`; its word has SHA256
`e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`
and decoded SHA256
`5642fd0e35a1acc11acff8d0c08350c1617e95f310d4d35ad63a651f9eeeba0b`.
There are no third-party Python dependencies.

Credit to **DreamingOfClouds** (PR589), **eumemic** (PR555/R420 interface and
the historical complex rank-five expansion), **Dugongue** (PR541/548 trace
and Steinberg mechanisms), **Rohan Arun** (PR542 and the cost/assembly
lineage), and **SethBurkart123** (PR886 fixed-word frame optimum).

**Ian Libânio's [PR933](https://github.com/CrocSwap/integer-mult-bounds/pull/933)**,
head `b9348c6907516e55dc07e135ad4d7a480d4f9840`, already studies relocations,
interacting relocation pairs and 3→2 rewrites with exact reframing. Its
inverse-expansion control and statement of neutrality are acknowledged.
The present contribution corroborates the adjacent 2→3 portion with a
different proof and independently implemented rank oracle, allows arbitrary
rational intermediate spaces, and proves a simultaneous all-exponent
concavity inequality. It fixes surrounding contacts rather than globally
reframing the word, and does not claim to subsume PR933. No PR933 code is used.
PR1345, PR1382 and PR1413 concern further transport censuses; the selected
operation adds a new corrective gate. No priority claim is made.

The final refresh also checked **flemhhh's PR1048**, a paid-profile and
transport/3→2 audit, and **Hanson Sun (@bbMisk)'s PR1520**, a concurrent
seven/eight-XOR tradeoff for the different restored J3 block's positive
envelope. Neither is used as a premise or replay input. The latter reinforces
the need to distinguish an extra XOR's scalar cost, precision cost and paid
frame profile; this package only excludes a gain in the stated PR589 rank model.

Assignment seed **6** was drawn once with OS randomness. The three considered
tasks, selection rule, local claim and access/coverage limitations are in
[CLAIM.json](CLAIM.json); [TASK.json](TASK.json) declares the change from the
catalogue's broader new-register question to this incumbent side result.
Public PR searches, active Discussions and handoffs were inspected. API
posting is unavailable under the donor's workflow; no remote claim was posted.

Prepared for **@CubeJerry** with substantial **OpenAI Codex** assistance in
research, implementation, proof and writing. The two implementations do not
constitute independent human review. New work is Apache-2.0 under
the repository license; no predecessor source files were modified or vendored.

## Limitations and open obligations

This is a computer-assisted theorem for the precisely defined local
relaxation, not formal proof-assistant verification or a multiplication
theorem. It excludes neither nonadjacent rewrites, global reframing alongside
the expansion, repeated interacting expansions, alternative flattening orders,
new helpers, nor changes to COPYs, geometry or hosting. Precision, native
5/9/11-stage replay, hosted emission and outer assembly are not rerun, because
no candidate survives the favorable rank budget. The selected construction's
all-size/compiler, common-label/mutable-source, hosting, precision/tape and
analytic assumptions remain unchanged.

## Open next questions

One justified follow-up is a **nonadjacent** corrective expansion that changes
the intervening contact pattern. Start with one explicitly pinned interval,
derive its complete paid boundary budget and check overlap with PR933/PR1345
before computation. The obstruction here does not cover that geometry;
construction and full supplier admission would still be required for a gain.
The structured next question is in [TASK.json](TASK.json).
