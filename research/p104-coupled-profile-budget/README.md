# Coupled P104 helper-history budget

**A sharp fractional relaxation, not a correction circuit or new kappa.**

Nick Petalas's [PR2640](https://github.com/CrocSwap/integer-mult-bounds/pull/2640)
leaves a concrete handoff: apply all seven crossing constraints to the *same
complete helper histories* before another construction attempt. This package
solves that cost relaxation, also imposing the credited two departures per
source and two arrivals per target. It includes all 256 positive compositions
of nine and the whole original channel bill. The resulting optimal primitive
saving threshold lies strictly between

```text
0.0023596069 < a_relax < 0.0023596070.
```

The certificate has a feasible fractional profile at the lower endpoint and
nonnegative rational dual multipliers excluding **every** profile at the upper
endpoint. The checker needs no LP solver. It verifies all 256 dual inequalities
with outward rational cost intervals, not floating-point sign decisions.

This does **not** close the P104 route at the selected complex saving
`67018507072324140917/40000000000000000000000` (about 0.00167546).
Even the integer relaxation with **137 histories (1,7,1) and 71 histories
(1,1,1,1,1,1,1,1,1)** satisfies every capacity/floor constraint and has moment
below 0.998430351 at that saving. Geometry, chronology and coefficients of such
a network are unconstructed. These necessary inequalities alone cannot reject
it; their favorable value does not establish feasibility or a supplier.

## Exact scope and model

Use the frozen 104-port source and target paths from Rohan Arun's PR1972,
retained in Chafik Boukhalfa's native PR1991 package. The added network reads
immutable X, writes additively to Y, and uses rational equal-frame operations
on arbitrary dirty helpers with monotone ZERO-to-FULL lifetimes. Targets and
the original channel's helper/private roles cannot be read by the correction.
Source-dependent initialization, descents, changed original paths and
cross-frame ADDs are excluded. Reusing a physical helper counts a new lifetime.
Restoration is required at FULL. The original owned private-copy disposal
contract remains inherited, not replaced by strict-zero erasure.

The pricing screen assumes `m=73`, `W=832/9` families per call, a nine-stage
four-pair 104-port template, centre charge 56 and total rank mass
`72W+56=6712`. All additional helper lifetimes are hosted on that fixed family
inventory; a feasible owner map is **not** supplied. Every remaining rank unit
is optimistically assigned to fractional rank-51 idle children. The inherited
halving guard allows 51, since `2*51^2 < 73^2`. Actual idle packing and all
additional scalar, physical, routing and precision charges can only worsen
this declared screen. Changed coverage or a different template needs a new
model. No bound for every P104 architecture or multiplication algorithm follows.

The channel's original profile has mass 2368:

```text
1074 H1 + 58 H2 + 86 H3 + 104 H4 + 48 H5 + 24 H6 + 8 H7 + 8 H8.
```

Thus at most 4344 rank units remain for correction plus idle. Each complete
new helper history has mass nine. These are transport/ideal-idle costs only,
not a complete supplier invoice.

## Proof and certificate

Write a history as stops `0=d0<d1<...<dj=9`, with jumps `r_i=d_i-d_(i-1)`.
There are exactly `2^8=256` histories, indexed by the eight internal-stop bits.
For cut k, its unique crossing `u<=k<v` has capacity

```text
A[k,h] = 0                       if u=0 or v=9,
         2^(7-(v-u))              otherwise.
```

PR2640's monotone dependency-path argument and affine odd source/normal
alphabets give the necessary inequalities

```text
sum_h A[k,h] x_h >= b[k],
b = (4656,4656,4672,4680,4672,4656,4656).
```

Every nonzero residual coefficient has a dependence path crossing the cut on
a new helper after both original-source and original-target bypasses are
removed. A rank-r crossing admits at most `2^(7-r)` source/target pairs.
The same history must supply its capacities at all seven cuts; optimizing each
cut with an unrelated history would not establish this coupled relaxation.

Hiroki Kumazaki's PR2353 proves two arrivals into each distinct target
hyperplane. ywz65's PR2614 proves two departures from each distinct source
line even after all later-readable demands are removed. Since a nested
history visits at most one line and one hyperplane, also impose

```text
sum_(h visiting dimension 1) x_h >= 208,
sum_(h visiting dimension 8) x_h >= 208.
```

The checker independently reconstructs the seven bypass censuses, the
later-read-aware intersection equal to each initial source line, and the
rank-eight residual span at each target. These support the credited written
network proofs, which are not formal-kernel theorems or network enumerations.

Let `c_r(a)=(r/73)^(1-a)`, `q_h(a)=sum_(r in h)c_r(a)-9*c_51(a)/51`, and

```text
C(a) = sum_r BASE[r]*c_r(a) + (4344/51)*c_51(a).
M(x,a) = (C(a) + sum_h x_h*q_h(a))/W.
```

Minimize M subject to the nine inequalities, `x>=0`, and `9*sum(x)<=4344`.
Fractional histories and ideal idle are favorable relaxations. At `a_lo`, the
six-history primal in [CERTIFICATE.json](CERTIFICATE.json) satisfies all nine
inequalities *with equality*, has 208 lifetimes and 2472 idle rank units, and
has moment less than one. Its complete local profile is

```text
{1:17855/9, 2:59, 3:259/3, 4:104, 5:48, 6:24, 7:9136/63, 8:8}.
```

The six complete histories and their multiplicities are:

| Mask | Ordered jumps | Multiplicity |
|---|---|---:|
| 129 | (1,7,1) | 8632/63 |
| 159 | (1,1,1,1,1,3,1) | 1/6 |
| 191 | (1,1,1,1,1,1,2,1) | 1/2 |
| 249 | (1,3,1,1,1,1,1) | 1/6 |
| 253 | (1,2,1,1,1,1,1,1) | 1/2 |
| 255 | (1,1,1,1,1,1,1,1,1) | 4388/63 |

At `a_hi`, the certificate's nine rational multipliers `mu>=0` satisfy
`sum_i mu_i*A[i,h] <= q_h(a_hi)` for **every** history. Therefore any feasible x
satisfies `sum_h x_h*q_h >= sum_i mu_i*b_i`. The checker uses lower enclosures
for each positive child cost and an upper enclosure for the subtracted idle
cost. The resulting lower bound on M exceeds one. Dropping the upper lifetime
constraint in this dual argument is favorable and hence safe. No solver status
or tolerance is trusted.

For each feasible x, M is strictly increasing in a: the equivalent complete
profile has nonnegative local/idle counts and ranks below 73. Consequently
the two witnesses bracket the supremum of savings admitted by this relaxation.
The certificate establishes sharpness to the displayed interval; it does not
claim that one optimizer is optimal for every a. Under the inherited transfer,
its conditional planning cap is `kappa < a_hi/(1+a_hi)`, about 0.002354053.
This is a complex-side ceiling; the unchanged bit supplier would bind earlier.

## Reproduce and checked evidence

Python 3.12 or later, standard library only, from the repository root:

```sh
python3 -I -O -Werror -B research/p104-coupled-profile-budget/verify.py
python3 -I -O -Werror -B research/p104-coupled-profile-budget/test_verify.py
python3 -B scripts/research_package.py --package research/p104-coupled-profile-budget
```

Optional certificate regeneration, with JSON on stdout and no file changes:

```sh
python3 -I -O -B research/p104-coupled-profile-budget/propose.py
```

The direct replay is read-only, Git-free and network-free. `--out NEW.json`
writes the complete verified receipt exclusively to a fresh path. Source hashes
are checked before the inherited interval module is imported.
[EXPECTED.json](EXPECTED.json) records both strict margins and all finite counts.
The interval arithmetic is inherited from Douglas Colkitt's ceiling package;
it is not independently reimplemented here. The certificate proposal used a
separate exact rational two-phase simplex in `propose.py`; its output matches
the committed certificate. Primary replay imports no optimizer or predecessor
executable. Its arithmetic inequalities suffice to verify the result without
reproducing that search. The behavioral suite separately reruns the proposer.

Seven behavioral groups cover a separately recursive history inventory, the
positive certificate, an invalid all-cheap profile, dual overpricing and zero
dual, an overstated saving/negative multiplicity, unchanged optimized Git-free
export, source-before-import rejection, receipt/duplicate-key faults and
exclusive output. Local Windows CPython 3.12.10 registered replay and
CPython 3.14.6 direct replay pass. Native phases,
the complete 280-input channel identity, a physical correction, owner/routing
and residual costs, precision, all-size lifting and selected cold replay are
not recertified. No human, hosted-CI or proof-assistant review is claimed.

## Open next questions

Can geometry or chronology rule out the apparently affordable coupled
profiles, rather than only their marginal cut capacities? First pin a single
candidate history collection and assign actual nested subspaces and demanded
source/target pairs, preserving the two endpoint obligations. A finite
incompatibility certificate or a compatible assignment would distinguish
the missing geometric constraint from a cost failure. Rational coefficient
compatibility, arbitrary dirty restoration and a complete consumer/owner bill
still block supplier admission. See the structured question in TASK.json.

Family decision: finish this cost audit and **stop**. This passing relaxation
does not authorize treating unknown costs as zero or expanding a construction
campaign. Reopen only with a specific geometric/chronological constraint or
a fully stated producer/consumer boundary and priced obligation ledger.

## Attribution and source status

This is a new coupled cost certificate, not new crossing or endpoint floors.
The pending predecessors are read and credited at exact heads:

- Nick Petalas / PR2640 `2a5b9d72371211eac1288b690bc2739a97132439`:
  all seven cut constraints, affine capacity proof and this handoff.
- ywz65 / PR2614 `a4a2a1c734283272691b1083c819e98e7d757f20`:
  later-read-aware source-departure implication.
- Hiroki Kumazaki / PR2353 `2704eadf6b5205d4b965e9c6fc6dce28b89783cf`:
  explicit monotone model and relay-safe target-arrival implication.
- Nick Petalas / PR2604 `f234bd0e5dca545aacbaaa457bd606e17de95baf`:
  legal dirty (1,7,1) carrier and correction of uniform shape exclusion.
- Philippe Van Velzen: original 208 floor, relay design and favorable pricing
  screen, including `f3b0853f` window-bill and `fac9e821d31bc199b49e8ed463074a50d1264311`
  relay-v2; no predecessor construction or optimization is claimed here.

Retain Rohan Arun / PR1972, Chafik Boukhalfa / PR1991, Adam Gall / PR1940,
Josie Elliston / PR1071, Ali Romman / PR1125 and the geometry/compiler lineage.
Immutable main inputs and historical provenance are in [SOURCES.json](SOURCES.json).
Pending proofs were source-inspected; their finite premises are separately
reconstructed here. None is silently promoted to a reviewed supplier.

Prepared for Arham Tahir with substantial OpenAI Codex assistance in mathematics,
implementation, verification and writing. Apache-2.0. No subagents were used.
