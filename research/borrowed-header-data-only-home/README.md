# Borrowed native HEADER with DATA-only permanent homes

Inline Gamma6/HOME adapters put encoded metadata inside each scientific
field, tying its extent to E+V. This package supplies a literal fixed-rho
wrapper with a separate immutable borrowed Gamma6 HEADER and a HOME body
containing exactly V scientific DATA bits. Changing header lengths need
not agree, and no padding is added to native DATA.

The original author snapshot is frozen unchanged under implementation/.
Author normal/optimized replay, separate root execution and A's independent
proof/interface audit pass. Final registered portable replay and the outer
freeze are recorded separately; original implementation bytes stay unchanged.

## Supplied boundary and complete costs

Fix native positive rank rho in1..9 at construction. Supply a separate
Gamma6 HEADER for `(f,r,P,S,w,cutoff)` and already-packed complete DATA on
`[P] x [2^f]^9 x [S]`, with r Gaussian coefficients per address, real then
imaginary signed w-bit MSB-first components on one supplied unchanged grid.
`V=2PSr2^(9f)w`; E counts every header bit. The actual core checks
`rho*f<=cutoff`, and every executed C-prefix result must be integral and
fit the width. Endpoint fit alone is insufficient.

F_HOME=V independently of E. The unchanged positive native core retains
all nine slots, spectators, coefficients and exact phase. The wrapper returns
only DATA to the same HOME, preserves the borrowed header/tail and restores
every successful head, private body, guard and native guide. A single-header
graph uses **34 fixed tapes**; the two-header fixture uses **35**, because
both distinct public headers exist at initial entry.

HEADER's native origin is B-relative1. Native DATA/private origins are2,
placing private guards at blank1 and keeping permanent^0 intact. The graph
starts at the already-reserved B1 execution boundary. Its original unreachable
reservation prefix remains in the table and must not execute on HEADER3.
The constructor checks every reachable state for header writes. No typed
reservation is supplied.

Wrapper time is at most256(V+1), with64(V+1) additional visited backing.
Including the unchanged core and any separately charged fixed setup:

```text
T <= Setup_rho + 256(V+1) + 2^24(fV+E+1)
K_final <= K_entry + 2112(V+E+1)
```

K_entry retains all previous larger backing, borrowed headers and opaque
exteriors. E remains charged even though it is outside HOME. B1 full-bank
delivery, operand retirement and reservation have their separate invoice.
The direct fV rate does not establish a faster nonleaf service. Read
[implementation/PROOF.md](implementation/PROOF.md) for exact entry and costs.

## Author execution and separate root evidence

Two complete f1/rho1 author calls reuse the same6144-bit HOME and native
banks with E10/E268 headers, cutoff bit lengths1/130, both supplied at entry.
No host header replacement/producer is counted as physical work. C squared
gives the exact selected-axis swap in2452104 transitions, with12288 HOME
writes and zero borrowed HEADER writes. Checkpoints precede native return
and scatter. Cutoff, short-DATA and late nonintegrality examples leave HOME
unchanged. Emitted faults test returned extent, wrong-home scatter and skipped
private return. Guard-offset detection is a test monitor, not runtime
protection. Rejection cleanup/retry and universal malformed validation remain
outside the contract.

The root separately executes a fresh rho2 packet with f=r=P=1,S=2,w=7,
V14336,E270 and a130-bit cutoff. Its sparse CPU and closed two-axis Gaussian
Hamming kernel use neither the author's CPU nor numerical oracle/fixture.
It checks all25242 native instructions and every reachable state. The full
34-tape run takes13698674 transitions, writes exactly14336 HOME bits after
primitive return, zero earlier HOME bits and zero HEADER bits. Header reads
are exactly cells1..270, so the immediate opaque suffix is not read. All
heads/private bodies/guards/exteriors return and the parked HOME is unchanged.
See [review/root/ROOT-REVIEW.md](review/root/ROOT-REVIEW.md) and its receipt.

A independently compares1373214 retained instructions for all nine ranks
and both header ports. Its separate signed-origin sparse CPU executes three
rho2 calls on the same6144-bit HOME with E12/12308 and header sequence3,34,3.
The larger header exceeds DATA. It takes18592251 steps, writes HOME18432
times and headers zero times, restores all heads/private/exteriors/history,
and rejects both short/long returned extents before scatter. Its separate
reachability check finds0 reachable/8 unreachable header writes. See
review/interface/REVIEW.md. The original review is retained verbatim under
review/interface/original/. PORTABILITY.json discloses only two changes:
accept an implementation argument and replace unconditional receipt writes
with read-only scientific comparison excluding elapsed_seconds alone. No
oracle, CPU or mathematical checks changed. These executions corroborate the
all-input proof; no blind, human or formal-kernel review is claimed.
The roles share and inspect the proposed construction.

## Reproduction

Python3.12 and the standard library, from the repository root:

```sh
python3 -I -B -W error research/borrowed-header-data-only-home/implementation/verify.py
python3 -I -O -B -W error research/borrowed-header-data-only-home/implementation/verify.py
python3 -I -B -W error research/borrowed-header-data-only-home/review/root/check_borrowed_root.py research/borrowed-header-data-only-home/implementation
python3 -I -B -W error research/borrowed-header-data-only-home/review/interface/check_review.py research/borrowed-header-data-only-home/implementation
python3 -I -O -B -W error research/borrowed-header-data-only-home/review/interface/check_review.py research/borrowed-header-data-only-home/implementation
python3 -B scripts/research_package.py --package research/borrowed-header-data-only-home --check-only
python3 -B scripts/research_package.py --package research/borrowed-header-data-only-home
```

Expected author marker is PASS_BORROWED_HEADER_DATA_HOME; root receipt status
is PASS_ROOT_BORROWED_HEADER_RANK2; interface marker is
PASS_INDEPENDENT_BORROWED_HEADER_DATA_REVIEW. Defaults are read-only and compare the
author's frozen receipt; --write explicitly changes that receipt. Runtime
inputs are local and authenticated before imports; fresh required-absent
cache prefixes prevent stale bytecode substitution. VERIFY.json registers
five commands: author normal/optimized, root sparse CPU and interface
normal/optimized, with explicit implementation arguments for both reviews.

Original author FREEZE hash:
`0f3f4bae39a8f630c56799912c41f2babecf0493531e043d6a6e0cb21ef717a7`.
The native core remains frozen by
`5735c401ba981a7af4d3a146eb047d04fa0c87dbf7ed49bd82dc57df8d6cb2ef`.
Original implementation/proof/status/notice/draft bytes are retained exactly.

## Open next questions

TASK.json records concrete remaining interfaces: produce one admitted Gamma6
header from the actual separate nine-Gamma root descriptor and ROW grant;
implement the named source view and inverse packing with its full cost; and
compose complete monomial/MOVE/caller services around this supplied positive
primitive. Each needs real occurrence, owner, grid/prefix and cutoff-policy
binding. Equal DATA volume does not itself implement a coordinate permutation.

## Kappa and credit

No new kappa. The selected value363005817/100000000000 remains under all
five retained assumptions. No source producer, root conversion, view packing,
cutoff derivation/policy, all-MOVE or actual caller admission, faster nonleaf
tariff or multiplier is supplied here.

Prepared for @CubeJerry with substantial OpenAI ChatGPT/Codex assistance.
Worker B supplied the wrapper/proof; root separately checked physical
execution/arithmetic and A supplied the independent interface proof/checker. Credit the unchanged
generic positive core, rank-two/literal phase/CNOT/C lineage, B1 and the
source/root-format work. Retain implementation/NOTICE.md and all upstream
notices. Apache-2.0.
