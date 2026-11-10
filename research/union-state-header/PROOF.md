# Exact minimum header width

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract

Fix integers L>=2 and g>=1 and shared sorted sets E_i contained in
{0,...,L-1}, with a_i=|E_i|. A coordinate vector x has g entries in that
range. The legal tag is either the sentinel g or an axis i with x_i in E_i.
The flags, canonical boundary ordinals and flag count are determined by x
and the shared sets. An unflagged ordinal is zero. This is the full legal
header domain of Mihir Srivastava's PR4583, including sentinel records
outside the sparse union. There is no restriction on the payload.

A record has a fixed two-bit marker 01 followed by a fixed number of data
bits. The decoder knows L, g and every E_i, but receives no record-dependent
side information or previous record state. Records must decode individually
and exactly. We optimize width within this contract, without a locality,
time or fixed-tape requirement. Context storage is outside that width.

## Theorem

The number of legal headers is exactly

    N = L^(g-1) (L + sum_i a_i).

Their minimum fixed width, including the marker, is

    H* = 2 + ceil(log2 N).

Writing h=ceil(log2 L) and b=ceil(log2(g+1)), it satisfies

    H* <= 2 + gh + b.

Compared with PR4583's separate-field width

    H_old = 2 + 2gh + g + 2b,

this saves at least gh+g+b bits at every allowed context. All flags,
ordinals, count, tag, active-round choice, prefix keys and keep decisions
remain exactly recoverable. This is a representation theorem, with no
claim about physical time, tape travel or the full multiplication theorem.

## Counting and lower bound

Partition legal headers by tag. The sentinel block has all L^g coordinate
vectors. The block tagged i has a_i choices for coordinate i and L choices
for every other coordinate, hence a_i L^(g-1) states. Blocks are disjoint
because their tags differ, even when the same coordinate occurs in several
blocks. Summing proves the formula. Flags, ordinals and count add no states,
since they are determined by the coordinate and shared context.

A width-H record with marker 01 has at most 2^(H-2) distinct bit strings.
Exact decoding requires distinct legal headers to have distinct strings,
including headers sharing coordinates but having different legal tags.
Therefore 2^(H-2)>=N, giving the stated lower bound for every encoder,
including nonlinear encoders. The conclusion does not apply to variable
lengths, joint compression across records or an additional side channel.

## Attaining construction

Order the blocks as sentinel, axis 0, ..., axis g-1. The sentinel block
starts at zero. Axis i starts at

    L^g + L^(g-1) sum_{j<i} a_j.

Inside the sentinel block use the ordinary lexicographic base-L coordinate
index. Inside axis i's block replace x_i by its zero-based ordinal in E_i
and use radices L at the other coordinates and a_i at coordinate i.
For digits d_j and radices r_j, the mixed-radix index is computed by starting
v=0 and replacing v with v*r_j+d_j in coordinate order. Induction gives a
bijection to the integers from zero through product(r_j)-1. An empty axis
block is skipped and never requires division by zero.

Add the block offset to obtain an index k in [0,N). Store k in exactly
ceil(log2 N) binary bits after 01. Decode by selecting its block, subtracting
the offset and repeatedly taking quotient and remainder by the radices in
reverse order. For an active block, select x_i from E_i at the recovered
ordinal. The mixed-radix bijection and disjoint block intervals prove both
inverse identities. Unused binary indices k>=N are rejected.

Given the recovered coordinate, sorted-set membership and rank recover every
flag and ordinal, hence the count. The round-r active axis is the r-th set
flag, for zero-based r<count. The line key is the preceding coordinate
prefix together with the active ordinal. A keep decision is count>r+1.
Retagging re-encodes the same coordinate with that active axis. These are
semantic operations; they make no assertion about in-place reversibility
or preservation of an arbitrary previous tag.

Finally a_i<=L implies N<=(g+1)L^g<=2^(b+gh). Thus ceil(log2 N)<=b+gh.
Subtracting this upper bound from H_old gives the uniform saving. For
L=16, g=4 and each E_i={0,15}, N=98,304, so H*=19 while H_old=44.

## Scope and implementation

Enumerative coding, mixed-radix conversion and the pigeonhole principle are
classical. The contribution is their exact application to this full legal
union-header domain and the new bounded reference codec. The prior field
codec and its scientific checks are not replayed or audited here.

The written construction holds for arbitrary finite contexts. codec.py
implements it within explicit capacities of 32 axes, L<=2^4096 and 128
entries per boundary set. It never enumerates the coordinate box. Boundary
queries use the supplied sorted lists. The bit-width theorem does not charge
those lists, arithmetic temporaries, rank/select access or decoding travel.
In particular, the old tag-only update is replaced by a possible whole-index
rewrite. Identical contexts may share code words; context boundaries remain
required. Some bit changes produce another legal state, so this format is
not an error-detecting code.

The universal claim rests on this written proof. Finite execution corroborates
only its declared domains. No physical caller, selected-frontier change,
new kappa or discharge of the five inherited assumptions follows.
