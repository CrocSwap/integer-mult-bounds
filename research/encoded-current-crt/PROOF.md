# Current child coordinates, encoded CRT reconstruction and offsets

JoyboyBrian; substantial OpenAI Codex assistance. Apache-2.0.

## Exact source question and boundary

The source is Cinna Davis's PR4100 `CRT.md` section 1 and the `balanced`
function in its pinned `check_batched_crt.py`. At one balanced node the left
child has **already been transformed**. Its coordinates y_i obey

`k_A = y_i P_i (mod s_i)`, `P_i = product_(j<i) s_j`.

They are not the original mixed-radix digits. The frozen `decode_group`
recovers the unique k_A in [0,S_A), S_A=product s_i, from these congruences.
For successive right moduli t_j it uses offset

`c_j = k_A * inverse(S_A product_(h<j)t_h, t_j) (mod t_j)`.

The right coordinate x_j becomes (x_j+c_j) mod t_j if x_j<t_j, and remains
x_j otherwise. If any left coordinate is invalid, the entire node instead
uses k_A=0. The synchronized mixed-width caller retains this same offset
and endpoint, with each declared padded width preserved. A complete native
payload permutation or Beneš-table implementation is not asserted here.

Inputs to `produce` are two distinct, uniquely framed borrowed record tapes.
A record is ROOT followed by two full P-bit unsigned words, each WORD_END,
then RECORD_END. RIGHT terminates each stream; LEFT occurs only at cell zero.
The left records are (s_i,y_i), the right records (t_j,x_j). Both groups are
nonempty. All numeric words use the same pre-existing P>=4 source arena,
capacity 64, with at most eight borrowed live words at entry. Stream heads
enter at one. The arena initialization template is borrowed. Other borrowed
numerical words need not have an initial head and are never read or rewound.

Every modulus exceeds one, all moduli in both groups are pairwise coprime,
and the complete product is strictly below 2^(P-1). Coordinates are arbitrary
P-bit unsigned integers; individual declared physical widths are an outer
caller premise. These hypotheses imply all intermediate prefix products
fit with a zero high bit. They are checked by the encoded arithmetic: a
nonunit inverse or overflowing/high-bit product rejects. Finite framing
errors inside uniquely framed tapes reject; missing/duplicate framing is
outside this entry contract, not an arbitrary malformed-stream theorem.

Outputs are owned full-width k_A and S_A words, an owned sequential stream
of (offset,updated-right-coordinate) records, and one finite validity flag.
The two input tapes preserve every byte and return heads to one. All
non-output numerical registers and their visited backing are erased. The
output stream returns its head to one. On rejection all newly owned
numerical and output state is erased, while the input streams and unrelated
borrowed numerical state remain unchanged. This is scoped numerical
ownership, not general rollback for malformed source primitive internals,
process termination or allocation failure outside the admitted inventory.

## A separately admitted arithmetic interface

The frozen `words.Ring` constructor requires its modulus to have **exactly
one** leading zero margin bit. Consequently, modulus 5 in a seven-bit arena
is rejected, although it is a legitimate CRT modulus. This package neither
changes that guard nor constructs a Ring by bypassing its initializer.
`Arithmetic` does not call Ring at all. It implements modular operations
from the retained unsigned bit-tape primitives under a new explicit domain:

`1 < M < 2^(P-1)`, `0 <= a,b < M`.

`admit` checks M>1 and reads the high bit, restoring the head before testing
it. Additional leading zero bits are allowed. Modular addition forms a+b
and subtracts M exactly once when necessary. Because a+b<2M<2^P, no carry
can escape. Subtraction returns a-b if nonnegative, otherwise a+M-b; the
same margin applies. Multiplication scans a private copy of b from its
most significant allocated bit, repeatedly doubling modulo M and adding a
when the next bit is one. Induction on the scanned prefix gives a times
that prefix modulo M. Leading zero padding changes neither value nor
correctness. Every borrowed operand returns its head before the operation
returns; copying the scanned operand also makes operand aliasing safe.

For inverse, use ordinary Euclid on r0=M,r1=a, with coefficients t0=0,t1=1
maintained modulo M. After quotient q, use the encoded q mod M and set
`t2 = t0 - (q mod M)*t1 (mod M)`. Therefore r_h=a*t_h modulo M throughout.
The positive remainders decrease; every two divisions reduce a remainder
by at least a factor two. The loop ends at gcd(M,a). If it is one, t0 is
the inverse; otherwise return None. This includes a=0 and composite M.
No host integer gcd, exponentiation or value decoding is used at runtime.

The separate unsigned product scans a private copy of one factor, doubles
its accumulated value and adds the other factor for a one bit. All partial
products are nonnegative and no greater than the final product. Therefore
an admitted final product cannot overflow an intermediate word. The final
zero-high-bit check preserves the reserve required by later division. The
source Unsigned restoring division needs this zero high bit, not the
stronger Ring constructor's exact significant-bit position. Its existing
premises are consequently satisfied without weakening a source guard.

## Reconstruction from actual current coordinates

Maintain prefix S and k with 0<=k<S, initially S=1,k=0. At a left record
(s,y), pairwise coprimality makes v=S^-1 mod s exist. Set

`t = (y mod s) - (k mod s)*v (mod s)`,
`k' = k + S*t`, `S' = S*s`.

Then k' is congruent to k at every earlier modulus, and
`k' = S*y (mod s)`, precisely the new locally scaled residue condition.
Also 0<=k'<S*s. By induction and CRT uniqueness this is exactly the frozen
`decode_group` result, not a different convention. A finite flag remembers
whether every y<s. If not, the final lower word is replaced by zero, exactly
as the actual source node disables its whole right-child shift.

For the discriminator, original digits (1,2) at moduli (5,7) have k_A=11
and current transformed coordinates (1,5). The recurrence returns 11.
At right modulus 13 the inverse of 35 is 3, so the offset is 7. Treating
(1,5) as original mixed-radix digits would give 26 and offset zero. Both
current coordinates are individually valid; a range check cannot repair
that convention error. Tekalign's `crt-address-streams/crt_offsets.py`
already produces encoded offsets from **original** lower coordinates for
a different triangular caller. That work and its paid-router contract
retain credit. This package does not claim the first encoded CRT offset.

## Complete right-node numerical consumer

Copy S_A for the owned result and retain encoded prefix S=S_A. For each
right record (t,x), compute c=(k_A mod t)*(S mod t)^-1 modulo t. If x<t,
return x+c modulo t; otherwise copy x unchanged. Then multiply S by t
before the next record. This is the exact whole padded-rotation endpoint
used by the frozen balanced node. In particular, a padded right coordinate
is not reduced modulo t. An invalid left coordinate yields c=0 for every
right record, including later ones. Even an invalid right coordinate does
not remove its modulus from the prefix for later offsets.

All arithmetic reads data through source bit operations; `Word.inspect`
is disabled during the full fixture invocation. The producer receives no
Python list of moduli, decoded coordinate, host integer offset or numeric
loop count. Literal 1 and record tags are compile-time finite constants.
Groups and word lengths are traversed by markers. Runtime `times_small`
is never called with a decoded modulus. The actual consumer here is the
encoded address update; physical payload routing and complete table/ROM
construction remain outside scope.

## Ownership and a uniform local bound

At entry snapshot the fixed numerical ownership flags, with at most eight
borrowed live roles. The arena has exactly 64 role slots, independent of P
and axis count; allocation bookkeeping is finite control over those slots,
not numerical-value access. Every primitive returns its operand heads.
At success preserve only the two explicitly owned result words. In the
finally block erase each other newly live slot and rewind the two borrowed
descriptor streams. On error also clear the possibly partial output tape.
This never rewinds unrelated borrowed words, so their arbitrary entry
heads remain unchanged. Direct inspection of the live schedule bounds
newly simultaneous numerical words by 24: the worst point is one Euclid
iteration inside a left or right record, with descriptor/current-prefix
words, four Euclidean state words, and the restoring-division/modular-
multiplication scratch. Thus at most 32 slots are live, below 64; neither
axis count nor P allocates another physical tape. The output stream is one
sequential role. Historical arena backing is bounded by its fixed slots.

Here is an explicit conservative **source-tape** bound. Put U=P+2. Count
finite-alphabet cell reads/writes/unit moves and finite-control operations;
fixed-slot bookkeeping is included as a bounded scan. The source routines
in `words.py` contain only bit carries and marker loops. Their loop bodies
give the following upper bounds, including initialization, erasure and
head returns. Arena/input framing construction before entry is separate.

| Operation | Upper bound |
|---|---:|
| zero/copy/free/compare | respectively 128U, 256U, 64U, 128U |
| unsigned add/subtract/shift | 512U |
| unsigned restoring divmod | 4096U² |
| new remainder or full unsigned product | 8192U² |
| modular add/subtract | 2048U |
| modular multiplication | 16384U² |
| modular inverse, including nonunit exit | 131072U³ |

For example, restoring division has P iterations; one iteration allocates
and shifts a remainder, compares, possibly subtracts, frees superseded
words and writes one quotient bit. Its body is below 2048U operations and
its setup/return is below 2048U, hence the displayed 4096U² bound.
Modular multiplication has P iterations with at most two modular additions
and their erasures. Euclid has at most 2P+1 iterations; each combines one
division, one remainder reduction, one modular product, a subtraction and
fixed erasures, bounded by 32768U². Its setup/exit therefore fits 131072U³.
These are upper bounds derived from loops, not measured timings.

Each left or right record costs below 262144U³ including parsing, its
inverse, every other arithmetic operation, serialization and temporary
erasure. If there are m left and t right moduli, each is at least two and
the complete product is below 2^(P-1), so m+t<=P-2. Final stream rewinds,
cleanup of at most 32 slots and the two output-word handoffs leave the
complete invocation below

`2^20 * (P+2)^4`

source-tape/control operations. This includes numerical and record-stream
traffic. The verifier records these two lanes separately and compares their
sum with the bound; it does not infer the universal bound from samples.
Constant-alphabet encoding into literal binary tapes and full control-table
compilation are not executed here, so this bound is **not** substituted
unconditionally for the bit-step E(p,ell) of another implementation.
A uniform finite-alphabet compiler, pre-entry arena/descriptor production,
whole ROM construction, global repair and all other caller charges remain
named obligations. There is no speedup or new kappa claim.

## Evidence and retained limits

The independent verifier checks every modular operand pair for moduli
2..15 and all unit/nonunit inverses there, the original Ring rejection
and new-interface acceptance, all 64 width-three left coordinate pairs
for (5,7), mixed valid/padded right fields and four complete original
balanced-root calls after both children transform. Source references use
the frozen `decode_group`, `rotation` and Beneš functions; all host integer
arithmetic stays in the verifier. Four original mixed-width Caller fixtures
also compare each offset port and full level row endpoint at declared widths
(4,4,4,5). The module invocations receive newly encoded source-derived
fixtures at these boundaries; an uninterrupted physical whole-tree program
is not supplied. Actual producer faults misinterpret
current coordinates, omit the preceding right modulus, or reduce padded
coordinates; independent endpoint checks reject each. Noncoprime inputs,
insufficient capacity, empty groups and malformed tags exercise cleanup.

This proves one numerical producer/consumer module with explicit source
arithmetic domains. It does not construct the full Context, parameter
encoding, reservoir movement, ordinary callee, ROM/Beneš producer, raw
compact macro, sparse repair, physical payload map, selected supplier or
multiplication theorem. Source retention, local tests and independent AI
review are not scientific acceptance or formal proof-kernel verification.
