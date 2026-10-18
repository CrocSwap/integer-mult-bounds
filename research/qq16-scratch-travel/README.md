# Exact QQ16 scratch-sweep head travel

The two scalar sweeps of ywz65's [PR #2709](https://github.com/CrocSwap/integer-mult-bounds/pull/2709)
have the following exact total head travel for every positive integer `N`:

| Placement of all 112 banks on each tape | Closed word-address steps |
|---|---:|
| Bank-major, `address(bank, site) = bank*N + site` | `8564*N^2 + 306*N - 2` |
| Site-major, `address(bank, site) = 112*site + bank` | `9300*N - 432` |

Both execute the same scalar operations at every site. Their difference is
`(N-1)*(8564*N-430)`, positive for `N >= 2` and zero at `N = 1`.
For `N = 2`, the exact bills are 34,866 and 18,168 steps.

One bounded variant also permits linear travel in **bank-major** storage:
replace eight scratch-to-scratch subtractions by restored dirty bridges
through existing Z0 and stream each scalar instruction across all sites.
It costs exactly `11866*N - 2840` address steps and **24 additional unit
ADDs**, with no extra payload array in this model. It requires exclusive
W-bank availability throughout each complete window, rather than releasing
one owner's scratch before processing the next owner.

This is a proved tariff for a specified access protocol. It answers one part
of PR #2709's open movement obligation. It does not price the complete decoder,
establish a minimum over other schedules, or improve the selected supplier or
kappa. In particular, **constructing the site-major layout is not free**.

## Boundary and access protocol

Pin PR #2709 at `d7749c49e967b214537c0bd832e435e177e21d4f`.
Its input is commdata2338's PR #2651, pinned at
`a3b82e6f4ddcf999f8b6dcd3a6dfc3a9543a1533`, retaining ywz65's
PR #2540 `630d557af5088f66b45c447969cee9576600e50b`.
The compressed [literal source word](source-word.json.gz) is a mathematical
input, not an executable dependency. [SOURCES.json](SOURCES.json) records its
original path, commit, Git blob and decompressed SHA256. The verifier imports
no predecessor code. Different gzip containers with the same payload pass.

There are two independently movable word-address tapes, one holding the
112 owned Z output banks and the other the 112 owned W output banks.
Each bank contains `N` aligned physical scalar sites in the same order.
A site can combine an owner index with a payload component index. No X or Y
borrowed input occurs in these two windows. The borrowed output slices are
W0 in the L2 window and W0 through W15 in the F0-inverse window.

For each window, visit sites in increasing order and preserve its literal
scalar instruction order at each site. An ADD reads its source, then updates
its destination; a CLEAR updates its target. Each access touches the named
word address once. Project this ordered access sequence onto each tape.
Count the sum of the two heads' absolute address differences. Each head starts
at address zero and returns there after each window. These are separately
closed windows, not an optimized joint endpoint schedule.

The address model allows one scalar source register and in-place scalar
arithmetic at the destination. G-to-F ADDs read and update two W words in that
order. No extra payload array is needed in this model. A scalar register can
contain a precision-dependent number of bits; this is **not** a finite-control
two-tape implementation or a claim that staging, bit arithmetic, carries,
instruction fetches or in-word scans cost zero. The tariff counts word-address
movement only. A bit-level implementation needs those additional charges.

Aligned scalar access and exclusive disposable W storage are premises, as in
PR #2709's owner-access contract. A common frame label alone does not prove
physical layout or alignment. All banks on a tape use the stated pitch of
112 in the site-major layout, including W16 through W111, which the windows
do not touch. The two layouts represent the same logical values initially;
the comparison excludes the conversion between them.

## Proof and source-bound constants

The zero-based inclusive markers in the pinned word are 633 through 1066 for
L2 and 1172 through 2125 for F0 inverse. Every interior event is a pointwise
ADD or CLEAR. There is no native operation, cover map or owner permutation
inside either body. The verifier validates these facts and field bounds.

Operations at distinct aligned sites touch disjoint cells and commute.
Exchanging only such operations changes the source event-major sweep into
the site-major sweep without changing any site's event order. This proves
equality on arbitrary scalar inputs and disposable dirty output contents.
The final scratch clears and later output clears remain. PR #2709's native,
frame, lifetime and full decoder theorems are inherited, not independently
proved here. The movement calculation itself needs only these scalar bodies.

For one tape, let `q` be its bank-number sequence for one site, let `a` and
`b` be its first and last banks, and let
`V = sum(abs(q[j+1]-q[j]))`. Extracting the literal source gives:

| Window / tape | Touches per site | a | b | V |
|---|---:|---:|---:|---:|
| L2 / Z | 416 | 76 | 107 | 2485 |
| L2 / W | 432 | 0 | 0 | 0 |
| F0 inverse / Z | 912 | 76 | 110 | 4396 |
| F0 inverse / W | 944 | 0 | 15 | 1603 |

Bank-major placement contributes an initial seek of `Na`, `N` within-site
walks of length `NV`, `N-1` inter-site walks of length `abs(N(a-b)+1)`,
and a final return of `Nb+N-1`. Its exact total is therefore

```text
T_bank = N^2*V + (N-1)*abs(N*(a-b)+1) + N*(a+b) + N-1.
```

For `a < b`, integer `N >= 1` gives
`abs(N(a-b)+1) = N(b-a)-1`. Substitution yields
`T_bank = (V+b-a)*N^2 + 2*a*N`.
For `a >= b`, substitution instead yields
`T_bank = (V+a-b)*N^2 + (2*b+2)*N - 2`.
This includes L2/W with `a=b=V=0`, whose bill is `2*N-2`.

Site-major placement contributes an initial seek of `a`, `N` within-site
walks of length `V`, `N-1` inter-site walks of length `112+a-b`, and
a return of `112*(N-1)+b`. Since `0 <= a,b < 112`, every inter-site
distance is positive. Thus

```text
T_site = (V+224+a-b)*N + 2*b-224.
```

Adding the two tapes gives the following exact polynomials:

| Window | Bank-major | Site-major |
|---|---:|---:|
| L2 | `2516*N^2 + 154*N - 2` | `2902*N - 234` |
| F0 inverse | `6048*N^2 + 152*N` | `6398*N - 198` |

Their sum proves the opening result for every positive integer `N`.
Sampling was not used to fit these coefficients. For the prescribed touch
sequence, direct walks between consecutive addresses attain the tariff;
triangle inequality excludes a shorter walk that visits them in that order.
Different site orders, scalar resynthesis, caching and layout choices are
outside this statement.

## Bank-major streaming with a restored dirty bridge

The original word contains exactly eight same-tape ADDs, at source events
1637, 1686, 1735, 1784, 1833, 1882, 1931 and 1980. Each is
`W[k] -= W[k+8]`, for `k=0..7`. Replace it with the following four ADDs:

```text
Z0   += W[k+8]
W[k] -= Z0
Z0   -= W[k+8]
W[k] += Z0
```

For arbitrary initial `(Z0,W[k],W[k+8])=(z,f,g)`, the result is `(z,f-g,g)`.
Thus Z0 restores exactly and need not start at zero. Every ADD uses distinct
source and target in the common current frame. Z0 is an existing owned output.
No native operation or other original instruction intervenes between these
four replacements. The identity is standard dirty workspace borrowing; the
contribution is this exact source-bound application and bill.

Every resulting ADD crosses between the Z and W tapes. Execute the body in
event-major order: for one scalar instruction, sweep sites `0..N-1`, then
perform the next instruction. Each ADD uses the source register for one site
and updates that site's destination before advancing both relevant heads.
The projection onto either tape therefore visits one bank's contiguous sites
for each instruction that touches that tape. Same-tape source/destination
ADDs would invalidate this streaming projection without further storage;
the verifier explicitly excludes them after the bridge rewrite.

This schedule changes the access premise. All W0 through W15 banks must
remain exclusively available across the entire F0-inverse window. Partial
scratch values at many sites coexist between passes. They occupy existing
owned output banks, so no additional payload array is allocated, but their
whole-window ownership and retention are required. Z0 is temporarily modified
between bridge passes and restores before the next original instruction.
This is not the predecessor's one-owner-at-a-time release schedule.

For one tape let `q` now denote the bank sequence projected from one pass
through the rewritten *instructions*, with length `m`, endpoints `a,b`, and
successive differences `delta`. The exact bank-major head travel is

```text
T_stream = N*a + m*(N-1)
           + sum(abs((delta-1)*N+1)) + N*b + N-1.
```

If `delta >= 1`, its summand is `(delta-1)*N+1`. If `delta <= 0`, its
summand is `(1-delta)*N-1`. These identities hold for all integer `N >= 1`,
including zero-length transitions at `N=1`. Thus this tariff is linear
without polynomial fitting. The literal rewritten instruction projections
give:

| Window | Z tape | W tape | Sum |
|---|---:|---:|---:|
| L2 | `2700*N-32` | `864*N-864` | `3564*N-896` |
| F0 inverse | `5412*N-800` | `2890*N-1144` | `8302*N-1944` |

The total is `11866*N-2840`, or 20,892 steps at `N=2`. It has lower travel
than the unchanged site-ordered bank-major protocol for every `N >= 2`;
it costs 158 more steps at `N=1`. This is a comparison of declared protocols,
not a lower bound over other schedules or caching strategies.

Replacing eight ADDs by 32 adds 24 unit ADDs. At the pinned
[QQ16 scalar prices](../joint-query/verify_scalar.py), this adds 192 real
scalar primitives. The complete added local decoder allowance changes from
840 unit ADDs, 832 quarter ADDs and 288 CLEARs, totaling 17,280, to
864 unit ADDs, 832 quarter ADDs and 288 CLEARs, totaling **17,472**.
No native event, cover map or original CLEAR changes. The inherited F0/B1
work remains additional. Scalar primitives and address steps are separate
units; this package does not add them to claim a runtime improvement.
The layout-conversion assumption is avoided by this variant, but whole-window
retention, bit arithmetic, instruction control and surrounding native costs
still need implementation and pricing.

## Reproduce and verification limits

From the repository root, standard-library Python 3.12 or later:

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-scratch-travel
```

The registered replay runs the verifier normally and with optimization, then
four artifact tests. Its result is

```text
PASS_QQ16_SCRATCH_TRAVEL bank=8564*N^2+306*N-2 site=9300*N-432 no_new_kappa
PASS_QQ16_DIRTY_BRIDGE_STREAM bank=11866*N-2840 extra_unit_adds=24 no_new_kappa
```

The verifier derives every coefficient from the authenticated source, checks
literal address walks at `N=1..32,64`, and compares event-major and site-major
exact rational dirty-state execution at `N=2,3,5`. Wrong-site reads disagree.
The bridge variant also derives and checks its linear coefficients against
literal bank-major instruction sweeps, compares every output cell with the
original event-major body, and rejects a wrong dirty-restoration sign.
Controls detect omitted touches, omitted head returns, substituted layouts,
native events inside a scalar sweep, borrowed X/Y access, inactive W slices
and aliased ADD roles. Artifact tests exercise a read-only Git-free export,
source-byte corruption, type-sensitive receipt corruption and a recompressed
identical source payload. Finite tests support the quantified proof above.

No predecessor verifier, actual native kernel, selected full cold replay,
Lean theorem or complete physical caller was checked. The source remains a
pending dependency. Its 224 output banks, sixteen retained early values and
native/scalar invoice remain inherited. Producing and consuming either layout
can change the surrounding native movement bill even when native event counts
stay fixed. There is no whole-construction saving claim.

Implementation bounds are explicit: at most 256,000 decompressed source bytes,
2,415 source events, 2,000 projected touches per tape, 64 literal sites and five
semantic fixture sites. New functions stay below 60 lines. Runtime contracts
remain active under `-O`; warnings are errors in the registered commands.
Power of Ten rule 3 has a bounded managed-runtime deviation here: Python JSON,
integer and Fraction operations allocate dynamically, with those enforced
capacities limiting live data. Replacing this offline verifier with a fixed
capacity native implementation is necessary only if allocation-free execution
becomes a requirement. This does not claim an allocation-free tape program.

## Task, overlap and freshness

The base is canonical main `c3c94c2ea2ebcd5d69d1e51b5fe8a36bf79819f5`,
priority revision 5. The chooser drew recursive interfaces with nonce
`8fbde7a90a030e7b3455c3218d1d828f`. [TASK.json](TASK.json) refines
`joint-query-controller` to this explicit missing access bill. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2617#discussioncomment-18955159)
joins the existing scratch/retention investigation.

Live overlap identified PR #2709 before implementation, so the scratch-reuse
construction was not repeated. Its stated open seeks/staging obligation is
the exact distinction. Complete cached overlap at 18:10 UTC covered 767 open
PRs and 1,334 Discussion records, supplemented by recent live PR/Discussion
and exact dependency reads. Searches for QQ16 head travel, bank-major,
site-major and the predecessor package found no separate tariff. Coverage
does not prove novelty. Final upstream and overlap freshness are recorded in
TASK.json. The family decision is to stop at this cost lemma and its bounded
bridge variant, with no supplier admission or dependent construction campaign.

## Open next questions

Can a complete caller produce and consume the site-major layout without
repaying this local movement difference? Pin one caller's input/native/output
schedule, then price its entry and exit layout conversions under the same
address protocol. The missing complete layout and native-placement ledger
block a whole-decoder comparison. [TASK.json](TASK.json) records this question.
For the bank-major streaming alternative, first check whole-window exclusive
W ownership in that same caller, then price its retention and bit-level
source-register implementation. The two protocols have different contracts;
neither complete bill follows from its address tariff alone.

## Credit

Nick Petalas. New work is Apache-2.0.
Credit ywz65 for PR #2709's conditional slice-access construction and
PR #2540's complete local decoder, commdata2338 for PR #2651's early-bank
coalescing, and the retained QQ16 lineage of Ali Romman, starship-s,
Sagar Thakrar, Ross Richardson and the native/geometry contributors.
Their source and proof claims retain their original attribution and scope.
The contribution here is the source-bound movement tariff and checker.
No independent human or maintainer review is claimed.
