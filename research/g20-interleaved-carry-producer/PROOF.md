# One-pass carry packets for the released G20 columns

Let a column have entries a_i/d, with integer a_i and d in {1,4}. All 3552
released columns have this form. Let q be positive and odd and let 0<=x_i<q.
Set N=sum a_i x_i. The canonical new low digit y is the unique integer in
[0,q) with d y=N modulo q. The required quarter packet is

    k = (4/d) (N-d y)/q.

The packet consumer applies k/4 to the high coordinate. We prove a producer
for k. It does not produce y or move the complete low-type payload.

## Quotient from bounded comparisons

Set L=sum min(a_i,0), H=sum max(a_i,0), U=max(0,H-1). Since x_i<q,
L<=floor(N/q)<=U. For every integer j in [L+1,U], retain one state b_j,
initially zero. At bit position r, read the eight low-digit bits e_i and
radix bit f. Set

    b_j <- floor((b_j + sum a_i e_i - j f)/2).

After r rows, let X_i and Q be the integers represented by those r low bits.
Induction gives b_j=floor((sum a_i X_i-j Q)/2^r). The induction uses the
identity floor((floor(z/2^r)+v)/2)=floor((z+2^r v)/2^(r+1)). At the end,
all integers are complete. Thus b_j>=0 exactly when N>=j q. The quotient is

    u = L + count{j:b_j>=0}.

The per-row input lies in [L-max(j,0), H-min(j,0)]. This interval contains
zero and is invariant under the displayed update. Each comparator therefore
has a fixed finite state set, independent of q and its bit length. For each
low digit, the same update with coefficients (1,-1) has states {-1,0} and
checks x_i<q at the end. The stream must end at the leading bit of q, with
q odd. These checks reject noncanonical or out-of-range inputs.

## Packet from two residue bits

Retain N modulo d and q modulo d from the first two rows. The bit-position
state saturates at two; it is not an unbounded counter. If d=4, each odd
residue is its own inverse modulo four. If d=1, the residue condition is empty.
Let r=N q^-1 modulo d, computed by that fixed residue table. Set

    c = u - ((u-r) modulo d),     k = (4/d)c.

Then u-d+1<=c<=u and N-q c is divisible by d. Also 0<=N-q c<d q, so
(N-q c)/d is exactly y. This proves the packet identity for every valid input,
including q=1. There is no runtime division by q, modular inverse at q, or
stored integer whose width grows with q. Dividing a bounded signed state by
two means a finite transition, not an uncharged arbitrary integer operation.

Compilation checks the source envelope

    -16 <= (L-d+1)(4/d),     U(4/d) <= 12.

Therefore all outputs fit the consumer's five-bit encoding k+16. For the
complete source, at most thirteen threshold comparators are needed. An
explicit encoding of between-row state uses at most 78 bits: the comparator
interval encodings plus sixteen bits for eight input comparisons, two residues,
the saturated phase, the last radix bit and a nonempty flag. This is an upper
bound on logical state, not a minimum physical tape-space result. The current
input symbols, output symbols and fixed column program are separate.

## Access, erasure and consumer costs

The contract supplies nine parallel bit channels, least significant bits first,
with all eight low digits zero-padded to the canonical radix width B. The
producer reads exactly 9B input symbols, returns a five-bit packet, and does
not alter any input. Finite transition logic per row gives O(B) work for each
fixed column. The Python implementation interprets this bounded logic; it is
not a materialized nineteen-tape program or an optimized transition table.

Ordinary controller reset can discard the bounded final state. A reversible
caller must instead pay its own state erasure or recomputation rule. Neither
operation is a free productive helper or a framework-assumption discharge.
The packet is consumed by the unchanged PR5849 kernel. That kernel preserves
the packet and restores its private tapes and physical output owner, with its
retained bounds 468V transitions and 49V visited cells. The producer's cost and
any packet erasure are additional. The code checks actual packet-to-consumer
composition in both orientations, including a nonintegral code at Q=125.

This changes the serialized-input premise of the quarter-carry cut theorem.
It does not contradict that theorem. Constructing the interleaved stream,
returning its heads, packet retirement, the complete high route, low-type
commit and the caller invoice remain open. No kappa is obtained by adding
unpriced access or cleanup operations to this local result.
