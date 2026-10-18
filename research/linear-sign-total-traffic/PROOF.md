# Exact logical tape traffic for the PR2753 sign

Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.

This independently prices David Arias's `linear_sign.py` at PR2753 head
`7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`, including its inherited
Jose Manuel/PR2697 Tape, Word, Counter and copy implementations. The exact
exports and original paths are in EXPORTS.json; predecessor attribution is
preserved in sources/PREDECESSOR-NOTICE.md. The routine and inherited code
are unchanged. The predecessor's permutation and source-movement results
are credited, not claimed as new here.

## Domain and measured interval

Let M>=2, B,S>=1, V=BMS and L>=bit_length(M)+1. The source is a complete
Boolean tape [B][M][S] with LEFT at physical zero and head initially one.
The borrowed before/suffix words are little endian, with exactly one high
zero margin: d_B=bit_length(B)+1 and d_S=bit_length(S)+1 digits before RIGHT.
All numerical words use L digits. The modulus, numerical one, arena template
and borrowed extents start with head one. Numerical capacity suffices for
the three extra words; recycled slots are erased as required by Arena.zero.
All private Tape objects are fresh.

Traffic means precisely the sum of logical Tape/Word reads, writes and unit
head movements. It starts at sign_address entry and ends after its successful
return, including the finally clause. It includes numerical allocation
*initialization scans* and disposal, every private countdown tape, source,
output and the borrowed extent tapes. Initial Ring/extent/payload construction,
inspection by the checker and eventual caller disposal of the returned output
are outside this interval. Physical allocation, blank capacity, Python heap
work, observer storage and placement among a fixed number of physical tapes
are outside this metric. This does not price the full caller or its compiler.

The literal Ring constructor requires L=bit_length(M)+1. We first give a
formula for the slightly wider sign interface above, then state the linear
bound only for the literal canonical Ring domain.

## Fully drained countdown lemma

For an encoded unsigned integer n with d digits, d>=max(1,bit_length(n)),
Counter(word), exactly n decrement calls, and close cost

    C(n,d) = 15n + 14d - 5 popcount(n) + 36     if n>0,
    C(0,d) = 14d + 40.

This includes reads/movements on word itself. That word is preserved with
head one. Counters are counted once even though another module holds a
reference to their Tape.

Here is a direct source-operation proof. For n>0 put k=bit_length(n).
The constructor's copy, trimming of d-k high zeros, finished test and rewind
cost 14d-4k+15. For zero it trims every digit, reinstates the canonical zero
and RIGHT, then rewinds, costing 14d+23. Counting a successful decrement of x
from a canonical counter at head one gives this table:

| x | Exact traffic |
| --- | ---: |
| x=1 | 18 |
| x=2^t, t>=1 | 5t+14 |
| x not a power of two, t=v_2(x) | 5t+10 |

The last two cases differ because only a power-of-two decrement shortens the
counter at its RIGHT delimiter. Each low zero flipped to one adds five units,
including its contribution to the rewind. Summing over x=1,...,n gives

    15n - 5 popcount(n) + 4k + 4.

Indeed sum_x v_2(x)=sum_(j>=1) floor(n/2^j)=n-popcount(n), and there are k-1
powers of two greater than one. The final zero tape always costs 17 to clear,
including both clear's rewinds. Adding constructor, decrements and close
proves the formula, including the separate n=0 branch. No amortization
constant is inferred from sampled runtimes.

## Exact composed sign formula

Write p(S)=4 for even S, 12 for S=3 mod 4, and 15 for S=1 mod 4. These are
the exact one_bit_suffix probe costs on a canonical margin encoding. Let

    J = 4B(M-2) + (BM if S!=1 else 0).

Then all successful sign traffic is exactly

    T = 68L+107                         numerical setup and disposal
        +4(d_B+d_S)+14                  positive extent validation
        +9V+4B(M-2)S+10                 payload, skips, check and rewinds
        +BM p(S)                        suffix probes
        +C(B,d_B)                       outer countdown
        +2B C(M-2,L)                    long forward-skip countdowns
        +B C(M-1,L)                     nonzero-slice countdowns
        +J C(S,d_S).                    all suffix countdowns

The all-parameter proof is a count of the literal loops:

- Each of B outer rows copies M slices. There are 2(M-2) forward skip slices
  and 2(M-2) backward skip slices per row. Thus there are 4B(M-2) movement
  suffix counters. Copy adds BM suffix counters exactly when S!=1; the
  single-bit branch has none. Every one of these counters drains completely.
- Every copy probes one_bit_suffix once, hence BM probes. The low two bits
  determine the three costs p(S); the S=1 encoding takes the 15 branch.
- Copies charge five payload operations per bit. Skips charge 4B(M-2)S.
  The terminating BLANK test costs one. Successful source rewind costs
  2V+3, output rewind 2V+3, and the final source rewind three. This totals
  the payload term above. It also recovers the predecessor's already checked
  source-movement identity (6M-8)BS+4.
- positive_extent, including msb and its rewinds, costs 4d+7 per extent.
- Arena.zero costs 9L+12. Literal two adds 13 to that. Each of the two
  distinct-word subtract_exact calls costs 22L+29, including its output
  initialization. Each of the three eventual free calls costs 5L+8.
  Their sum is 68L+107. The operands are restored, and exactly these three
  temporary slots are freed.

This is an identity in integer parameters, with no search-domain cutoff.
M=2 is covered: both long skips and all backward skips are empty, but their
zero-valued Counter constructors/normalizations/disposals still cost work.
The formula retains those costs rather than deleting an empty loop's setup.

For completeness the endpoint follows directly from the same traversal.
After copying zero it reaches slice M-1. Each copy advances S cells and each
nonfinal pair of backward skips retreats 2S, reaching the next smaller
nonzero slice. After slice one the last long skip reaches the next row.
Thus output origin (b,x,s) is (b,-x mod M,s), with within-slice order unchanged.
The source is never written, and both payload heads return to one. This
recalls the predecessor endpoint; the new result is its total traffic invoice.

## Uniform canonical bound and why word width matters

For the literal Ring domain L=bit_length(M)+1<=3M/2 and d_B<=2B, d_S<=2S.
The exact countdown formula yields

    C(B,d_B)<=83B,  C(S,d_S)<=83S,
    C(M-2,L)<=56M,  C(M-1,L)<=56M.

The zero branch of the last inequalities follows from 14L+40<=41M;
the positive branch is no larger than 15M+14L+40<=56M. Consequently the
four countdown terms together are at most

    83V + 168V + 415V = 666V.

Here J<=5BM and S>=1. Numerical work is at most 156V, extent validation
15V (use B+S<=V), payload 18V (V>=2), and probes 15V. Hence

    T <= 870V < 2048V.

The reported 2048 is a convenient uniform bound, not an optimum. All
constants and the canonical-width premise are explicit. q need not be a
prime for this local statement: the routine ignores q and only needs M>=2.
Adoption in a prime-power caller still needs that caller's own contracts.

One cannot remove the width premise. The isolated sign interface with
M=2, B=S=1 and L=1024 has T=113035, exceeding 2048V=4096, while keeping
its endpoint and eight source movements. The production Ring constructor
rejects that padding; this is a premise control, not a production bug.

A separate in-memory mutation replaces the fixed two backward skips by
move_slices(source,two,suffix,-1). It preserves the endpoint and source
movement count but creates a padded residue-width Counter once per nonfinal
nonzero slice. In the M=65, B=S=1 fixture, total traffic increases from
24,454 to 35,353 while source movements stay 386. Its additional setup is
Theta(B(M-2)L); allowing M to grow under canonical widths restores a
log M factor. Endpoint/source-movement checks alone accept this defect;
the exact total-traffic identity rejects it. The original PR2753 checker
already guards the related 3B residue-counter setup invariant; we retain
that credit. Our independently derived identity prices every counter and
numerical operation, rather than replacing that earlier control.

## Evidence and remaining obligations

verify.py executes authenticated source bytes directly, bypassing bytecode,
and observes every created record tape plus the numerical arena's shared
meter once. Its provenance instrumentation attaches the actual last source
position to each output write; it does not replace copy or sign execution.
No numerical inspection method is allowed during runtime. Closed formulas
live separately in traffic.py and import no production arithmetic.

The receipt covers 387 complete countdowns with n=0..128 and three padding
choices, 150 signs / 24624 addresses, source/head/numerical-live restoration,
three malformed inputs, the padded-width premise, the padded-two regression,
a wrong-backstep permutation mutation and a corrupted source export.
These finite executions corroborate the written all-parameter proof; they
are not themselves the proof. Assertions are not used as acceptance gates.

No full caller/selected GL64 payload, exceptional-path complete counter
cleanup, physical allocation/compiler, stronger H2 route/leaf implementation,
supplier admission, full multiplication theorem or new kappa is established.
The successful local logical-time contribution is O(V); a full fallback
still needs its remaining operations and their complete charges.
