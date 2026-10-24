# A persistent encoded old-kernel preparation session

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## Exact imported source and changed contract

The frozen PR3851 physical Gaussian cohort supplies Axis, Matrix, inverse,
Window, Core, encoded Count/Rational operations and fixed ScratchPool leases.
Its own gaussian_sources.opened authenticates the nested word and branch-free
archives. This contribution preserves those files. It supplies a new owner,
not a change to the selected multiplication construction.

A KernelSession fixes one admitted (s,t,u,w,P) axis for its entire lifetime.
The Axis, its independently rounded kernel values and bandwidth w are immutable
until close. This is an ownership premise: callers cannot modify the private
session bank, Axis fields or cache. Each run takes external encoded window/core
coordinates and target precision p and applies the unchanged source Window
admission predicates. The resulting page is owned by the session and protected
until consumed. Actual source Core.run borrows it and its halo, and returns its
own output under the source contract. The caller must consume that Core output
and call session.consume before asking for the next page. close releases the
Axis, resident cache and pending page and erases every owned origin marker.

The service has1024 preallocated scratch tapes and one page tape. It creates
no physical tape after construction. Count/Matrix objects acquire leases under
the original sealed constructor/OuterScope mechanism. Host counters are
observers and do not control data operations. This inherits the source's
fixed-pool encoded-macro model; it is not a new finite-instruction compilation
of the Gaussian arithmetic or an unconditional word-multiplication theorem.

## Why the cache key is sufficient

Window.prepare_schur constructs each old interior block by self.kernel_entry.
That function uses only the absolute encoded coordinate difference, axis.w,
and axis.kernel at that difference. It returns zero outside the bandwidth.
Thus for a frozen session the block is uniquely determined by its interior
length k, independent of the window's global label, period, similarity weights,
and which cell supplied it. The weights cancel in the old-kernel inverse and
are restored exactly once in the unchanged schur_entry. A principal H inverse
would be a different object and is not substituted.

The single-entry cache is private to that exact construction site. A same-size
arbitrary input matrix is NOT admitted to a general inverse-cache API. The
source prepare_schur code object is retained exactly; its globals are copied
with the sole substitution inverse -> this session's bound private operation.
All other Window methods and globals remain source-identical. In particular
Schur formation, rounding, positive-pivot LU, band checks, local factors, page
layout and close_dense are unchanged. Each session creates one fixed binding;
input parameters do not generate code or add physical tape roles.

On a miss, close the previous resident Matrix before computing the source
inverse. Save an independent encoded Matrix copy of that result. Return the
original inverse to prepare_schur, which may close it normally. On a hit,
return a fresh independent encoded Matrix copy of the resident inverse. Matrix
copies own their Count metadata and both serialized tapes; their entries are
read/written with original encoded get/write operations. No host Fraction or
decoded matrix dictionary supplies data. The source caller cannot close the
resident cache through its returned copy. Only one resident inverse survives
between windows. A changed axis requires closing the whole session and opening
a new one, thereby invalidating the old key.

Induction over inverse sites proves that each returned Matrix equals the source
inverse on the exact old kernel block. Therefore each emitted page is byte-equal
to the source Window page at the same inputs. Copying that page into the owned
output preserves its exact record alphabet and order. Actual Core.run receives
the unchanged page and so has the same endpoint and source approximation
premises. Finite explicit parameters do not inherit the source production
approximation guarantee merely from valid framing. Production-sized pages and
the enclosing tensor/catalogue/halo caller are not executed here.

## Complete paid profile

The cache does not make lookup, copying or storage free. For a sequence of r
windows, enumerate all long-cell inverse requests in source order as j=1..q.
Let k_j be each interior length and M the set of misses under one-entry eviction.
Let A be full source Axis setup; W_i the complete source Window work for window i
excluding only its inverse(block) calls; I_j the corresponding original inverse
cost; C_j the serialized Matrix copy cost; E_j the encoded dimension comparison;
D_j the resident-close cost on eviction. Let F_i include protected page copy,
its later erasure, and parameter head returns. Let Z include session/pool setup,
final resident/Axis disposal, all marker erasure and the fixed-role scans. Let
Q_i be the complete inherited actual Core/halo call and return-disposal cost.
Every term uses the source tape/encoded-arithmetic metric, not a unit-cost host
matrix operation. The session's full cost is bounded by

    A + sum_i(W_i + F_i + Q_i)
      + sum_{j in M} I_j + sum_j(C_j + E_j)
      + sum_{evictions j} D_j + Z.

There is exactly one copy per request: miss-save or hit-return. Block creation,
initial kernel_inverse bank, copying returned blocks into that bank, principal
matrix creation, Schur formation, LU, factor rounding, every page emission and
every Core call remain in W_i/F_i/Q_i. Source preparation without persistence
pays r Axis setups and every I_j. The change removes repeated Axis setups and
hit inversions, while adding the explicitly displayed copy/lookup/retention
costs. There is no claim of a speedup for every short stream, nor that caching
eliminates the full Gaussian setup bill.

For a closed polynomial bound, put B=P+1 for the old dyadic kernel coefficient
bit width. The source minor bound for an inverse of size k is
D=k(k+1)B+k*ceil(log2 k)+2. Its reduced numerators/denominators and intermediate
products have O(D) bits. Source inverse costs O(k^10(B+log(k+1))^3) time and
O(k^4(B+log(k+1))) scratch. A serialized copy performs k² get/read/write calls;
full scans contribute O(k^4 D), and possible rational reduction contributes
O(k² D³). Including encoded offsets and metadata, a conservative copy bound
is O((k+1)^8(B+log(k+1))^3). Comparisons and eviction scans fit that allowance.
Thus the complete changed setup profile is

    A + sum_i(W_i + F_i)
      + O(sum_{j in M}(k_j+1)^10(B+log(k_j+1))^3
          + sum_j(k_j+1)^8(B+log(k_j+1))^3) + Z.

This replaces the source's sum of all inversion allowances by the miss sum,
with all hit/miss copy allowances retained. W_i still includes its own full
source polynomial setup; no cancellation of that term is assumed. Q_i retains
the original online source bound and all supplier hypotheses. The concrete
consumer receipt establishes a nonempty hit stream, not an asymptotic gain for
the complete multiplication construction.

## Ownership and retained backing

Axis and one cached inverse persist; each temporary Window is fully closed
before run returns. The protected output is a separate Tape, never a lease
alias. The immutable-session premise ensures a cache hit never comes from
mutated coefficients or a new bandwidth. Failed run clears its partial output;
source Window closes its temporary fields. A successfully updated resident
cache may survive a later run failure and remains valid for the same frozen
axis. close also works after such a failure. Borrowed window parameter heads
are restored by finally blocks; their contents are never overwritten.

Let m_max and k_max bound the supplied window and interior sizes, Hmax the
maximum bit length of supplied coordinates/metadata, and Pmax the maximum
emitted page length. Explicit finite calls can have large lifted coordinates;
Hmax is not inferred from the axis size or silently omitted. The fixed1024 scratch roles retain the largest
extent each ever held, not merely their current nonblank cells. Charge K0 plus
1024 times a per-role upper envelope for source Axis setup, source Window setup at those sizes and Hmax,
original inverse scratch and the extra O((k_max+1)^4(B+log(k_max+1))) resident
inverse, plus Pmax+O(1024) for output and markers. This conservative sum includes
resident Axis, cache, copied return and active window simultaneously; fixed role
count prevents an r-dependent sum of past capacities. Output consumption erases
bytes but does not release their high-water allocation. All borrowed input
production and halo transport remain explicit caller costs in the complete
profile. No physical rational bit cost is hidden in a host cache.

## Open next questions

A whole catalogue caller must supply its actual window sequence and compare
this complete profile, including miss pattern, persistent storage and halo
transport, with its available budget. More than one retained length could
reduce misses but would require a separately priced encoded directory and
storage policy. No multi-entry or arbitrary-matrix cache is claimed here.
