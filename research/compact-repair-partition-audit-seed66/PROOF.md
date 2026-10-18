# Independent exceptional-repair batches: endpoint before tariff

This audits the final aggregate-partition question in ywz65's PR2476,
`32e88ddfd111b93fbcfb306514397cf406e4d5d4`, against Jose Manuel's actual
PR2250 word at `d404b48a1e7b147556b309497d55089c837dddb2`. The predecessor
does **not** claim that an arbitrary partition admits independent repair.
We identify the additional endpoint condition, give an exact source-bound
obstruction, and prove the conditional aggregate tariff. No new κ.

## 1. Precise partition contract

Let Ω be a finite record-address set, S its raw permutation, and T its desired
permutation. Records have arbitrary contents. Assume a sufficient exceptional
set E satisfies T(E)=E and S=T on Ω\E, as in PR2250's original guard.
Bijectivity implies S(E)=E. The repair permutation on **post-raw addresses** is

    P = T ∘ S^-1.

It fixes every address outside E and permutes E. Give Ω a disjoint partition
{C_i}. An independent cell repair may use all current records of C_i and
fresh local work, but cannot read another cell's payload or receive information
depending on it. It must write only C_i and return the result there. This is
a semantic contract, not an assertion that gathering C_i is free.

**Partition criterion.** Independent cell repairs implement P for every
payload if and only if P(C_i)=C_i for every cell. Equivalently, each cell is a
union of cycles of P. Since P fixes Ω\E, it suffices to test the exceptional
addresses; one need not require that S or T separately preserve each cell.

*Necessity.* Suppose q∈C_i but P(q)∈C_j with i≠j. Take two post-raw payloads
that agree on C_j and differ only in one bit at q. Repair on C_j has identical
inputs in the two executions, but the required output bit at P(q) differs.
This is impossible without communication. Arbitrary post-raw payloads are
legitimate because S is a permutation. This argument also rules out nonlinear
local computation and arbitrary local scratch under the stated no-information
contract; it does not rule out an additional cross-cell routing pass.

*Sufficiency.* P restricted to C_i is a permutation. Label each exceptional
record currently at q by the full destination key P(q), sort those records
inside C_i, and reinsert them into that cell's exceptional holes in address
order. Its keys are exactly E∩C_i, without duplication. Good records stay in
place. This is the same keyed endpoint argument as PR2250, applied to an
invariant cell. Sorting and access still have to be paid.

This is a proof for all finite Ω and partitions. The finite permutation census
in the verifier supports the statement; it is not the proof.

## 2. Exact repair orbits of the literal two-slot word

The one-digit saturation law and the order of repeated **raw** words are
already proved by @martinxxx9 in PR1108, head
`b76bb2853be4e7001508582b10913e32ad7aba9f`. We credit that algebra below,
include the selected offset explicitly, and apply it to the different
permutation P=T S^-1 and its independent-cell contract. We claim no new
raw defect or improved guard. John-Michael Smith's PR763 already checks
whole-fibre repair using unchanged source/back fields; our obstruction
concerns subdividing the mutable target.

Use the **earlier-source**, f=2 (n=1) PR2250 word, before its separately
executed highest selected-bit operation. Let G≥1, K≥G+4, 0≤ρ<K, and define

    B = 2^G,       M = 2^(2K),       u = 2^ρ,       h = 2Bu.

The wide target is y∈[0,M), the dirty compact digit is t∈[0,B), and z is
the source bit at position ρ. Other source bits and the front/back compact
fields are spectators of the completed raw word. The source's two load
operations use swaps with the back field; at their endpoints these are exactly
the following four modular updates:

    y ← y + 2ztu          (mod M)
    t ← t + bit_ρ(y)      (mod B)
    y ← y + z(1−2t)u      (mod M)
    t ← t − (bit_ρ(y) XOR z)  (mod B).

Let a=bit_ρ(y) on entry. The first update adds a multiple of 2u, so preserves
a and all lower bits. Put c=1 if t=B−1 and a=1, otherwise c=0. The loaded
digit is t+a−Bc. The net target displacement is

    zu(1−2a)+hzc,

and the final target bit is a XOR z. Thus the last update restores t modulo B,
and the literal raw endpoint is

    S(y,t,z) = (T(y)+hzc mod M, t,z),   T(y)=y XOR zu.

This derivation includes overflow; it never applies an unbounded-integer
identity where the source uses a finite digit. The unchanged actual source
executor is separately checked against these four modular updates.

For a post-raw target q, a=bit_ρ(q) XOR z. Consequently its exact repair is

    P(q) = q−h mod M,  if z=1, t=B−1 and bit_ρ(q)=0;
           q,         otherwise.                             (2)

All other address fields are fixed by P. The active fibre t=B−1 is entirely
exceptional under the **original** sufficient guard. No new guard is assumed.
For f=2 the formula also proves that the other conservatively marked bad
addresses need no movement unless they satisfy the condition in (2).

On the active half of the target range, P preserves q mod h and bit_ρ(q).
Since h divides M, each of its cycles has exactly

    L = M/h = 2^(2K−ρ−G−1)                                  (3)

elements. Each permissible residue modulo h gives one such cycle. There are
h/2 active cycles, and M/2 fixed points on the inactive target parity. A cell
containing any active address must contain its entire L-element cycle if it
is to be repaired independently. This is sharp: the cycles themselves work.

In particular, **every proper dyadic contiguous target partition fails**.
For any 0≤b<2K, partition by floor(q/2^b). The address q=0 is active, but
P(0)=M−h. Here h≤M/16 because K≥G+4 and ρ≤K−1. Thus P(0) lies outside the
cell [0,2^b) even for b=2K−1. In contrast, partitioning by q mod h is valid.
The raw map S flips bit ρ and can move between these valid repair cells:
requiring S-invariance would incorrectly reject this positive example.

These results concern this specific source family and a no-communication
repair interface. They are not lower bounds for a globally routed repair,
other compact words, different exceptional predicates, or the whole supplier.
We do not assume every legal f=2 parameter occurs in a selected recursive run.

### Seed-66 witness

Choose G=4, K=8 and ρ=66 mod 8=2. Fix front compact value 3, source word 4,
dirty digit t=15 and back compact value 11. The actual source code gives

    post-raw target:       0
    raw preimage target:  65412
    repaired target:      65408
    h=128, M=65536, L=512.

So a half-range batch containing address 0 needs to export its record to
the other half. On this entire target fibre the exact cycle inventory is
64 cycles of length 512 and 32,768 fixed points. This is a counterexample
to independent contiguous batching, not a defect in PR2250's global repair.

## 3. The aggregate tariff does not require a small bad fraction in each cell

Keep complete records of one common length R. Let a complete adapter pass
contain M records, B_E exceptional records, and a common valid key/control
bound A (global keys remain permitted inside every cell). The source tariff is

    Q(M,B_E;A,R) = MR + MA^3 + B_E A(R+A).

For any disjoint exhaustive partition, put M_i=|C_i| and B_i=|E∩C_i|.
Counting records once gives the exact identity

    Σ_i Q(M_i,B_i;A,R) = Q(M,B_E;A,R).                       (4)

It holds regardless of the largest local bad fraction B_i/M_i. If the
global hypotheses R≥A^3 and (B_E/M) A(1+A/R)≤1 hold, the sum is at most
3MR. Empty cells can be skipped. If local valid bounds A_i≤A are used,
monotonicity gives the same upper bound rather than equality.

For example M=1024, R=32^3, A=32 and B_E=4 give a global tariff/volume
ratio 17409/8192 < 3. A cell consisting of precisely the four exceptional
records has ratio 1089/32 > 3. These are exact accounting numbers, not a
claim that this toy shape is a complete selected call. The key bound is
sufficient for the global addresses and ceil(log2(2MR)).

Equation (4) says nothing about the correctness of independently repairing
the cells. Section 1 supplies that missing condition. Conversely, local
invariance does not ensure cheap access, preservation of complete records,
or bounded repetition. A low-residue cell is generally noncontiguous.
In particular, PR2250's `repair` routine expects its complete `Layout`; it
cannot simply be called on an arbitrary subset. To turn (4) into a runtime
bound, a cell implementation must satisfy the tariff with one uniform
primitive constant. Cell-address enumeration, any extra keys and all
partition-specific preparation must be included or charged separately.

If records are visited repeatedly, the exact sum instead counts each record
with its visit multiplicity. In particular, repeatedly visiting exceptional
records cannot be charged using the bad fraction of their original parent
range. The verifier retains a same-total-visit-volume countermodel. Splitting
each R-bit record into R one-bit records changes MA^3 to MRA^3, which is
PR2476's separately credited fragmentation obstruction.

### Conditional connection to the recursive bound

PR2476 already proves the weighted-tree potential bound from the selected
histogram and moment. Retain its parent-level density, long-record admission
and recursion. Suppose a complete repair pass is replaced by an invariant
disjoint partition preserving R and a common A, and each cell's repair
obeys c Q with a common constant c independent of the cell and depth. Its
total tariff is unchanged by (4), so the predecessor's repair-only bound,
multiplied by c, remains

    c (1000000000/5333) J V d^(99733167/100000000).

Here J counts complete aggregate adapter passes per node, not their number
of cells. This conclusion inherits the predecessor's source/recurrence,
uniform primitive constant, complete parent guard range and long-record
admission. The new partition dispatcher, its metadata, gathering, merging,
cross-cell communication if needed, and parking/return work are additional
obligations. Their cost is **not** hidden in (4). No moment engine or full
selected supplier is independently reverified here.

## 4. Scope and evidence

The unbounded results are the partition proof, modular derivation, cycle
count and tariff identity above. The machine checks include all dirty digits,
both source bits and all target addresses for four fixed nonempty-guard
shapes; actual original sequential payload execution for two smaller legal
all-bad shapes; and separately implemented keyed-reinsertion and permutation
oracles. The small all-bad fixtures test endpoints, not asymptotic admission.
The partition dispatcher in the test harness uses Python groups and is not
presented as a fixed-tape implementation or timed algorithm.

The source word, guard, one-digit saturation law, keyed sorting, tariff and
selected recursive bound remain predecessor work. Our addition is the
partition endpoint criterion applied to the actual repair, its resulting
orbit obstruction, and the
conditional partition-accounting connection. Substantial OpenAI Codex
assistance was used; no independent human review or formal proof is claimed.
Apache-2.0. Attribution is collected in NOTICE.md.
