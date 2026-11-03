# Exact Gray-code replacement of the section enumerator

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped implementation-equivalence proof. Gray-code enumeration
and packed binary columns are classical. James Reed's PR3773 supplies the
scientific consumer and its E8 core result. Neither the geometry nor the
published histogram is a new theorem of this package.

## The computed object

Let c_0,...,c_(s-1) be d-bit binary coordinate vectors. For a d-bit mask m,
the predecessor's expression computes

    h(m) = #{j : popcount(m AND c_j) is even}.

It builds an integer whose set bits are the distinct original root indices
of those j, then takes its population count. Those root indices are distinct
because they come from the bits of a set intersection. Thus the expression
equals h(m). The consumer requires the multiset of h(m) for all nonzero masks.
It still evaluates every core separately, including repeated isomorphism types.

## Packed columns and the invariant

For 0<=i<d define the s-bit column

    C_i = sum_j bit_i(c_j) 2^j.

For a mask m put O(m)=XOR_(i:bit_i(m)=1) C_i. Its jth bit is the parity of
popcount(m AND c_j), by distributivity in F_2. Hence

    h(m) = s - popcount(O(m)).

The binary reflected Gray map is g(t)=t XOR floor(t/2), for
0<=t<2^d. It is a bijection. Its inverse recovers the input bits from the
highest bit downward, since g_i=t_i XOR t_(i+1). Also

    g(t) XOR g(t-1) = 2^v2(t)     for 1<=t<2^d.

To see this, if t has k trailing zeroes, t XOR (t-1)=2^(k+1)-1.
XORing that number with its right shift leaves 2^k.

Start with odd=0=O(g(0)). At step t, XOR C_v2(t) into odd. The displayed
identity proves inductively that odd=O(g(t)). Store
s-popcount(odd) at the ordinary mask index g(t). After the last step,
every output equals h(m), including m=0. Taking Counter(counts[1:])
therefore preserves exactly the predecessor's nonzero-mask multiset.

The proof permits repeated coordinates, zero coordinates, an empty list and
d=0. It does not require the coordinates to span the whole space. The
implementation bounds d to 0..10 and s to 0..256; the identity itself holds
for every finite d and s.

## Whole-consumer substitution

The adapter authenticates the three declared source inputs. It compiles the
same authenticated source bytes after replacing exactly one unique expression:
the assignment of the section Counter. Every other source byte is retained.
The original file location is preserved so its geometry hash and RESULT.json
checks use their original paths. The module is private and its main function
is called explicitly. No source file or persistent module is patched.

The replacement returns the same Counter for every reached input by the
preceding identity. Consequently the per-core equality checks, aggregate,
pair count, source hash check and final result comparison receive the same
values. The complete stdout is unchanged. There is no saved geometry, cached
answer, skipped pair or reuse across processes. The checkout must remain
stable during execution, as the original consumer rereads its result file.

## Exact work counts

For one s-coordinate, d-dimensional core, the replaced expression performs
s(2^d-1) parity evaluations, plus a population count of each constructed
global root mask. The new routine builds d columns with ds one-bit tests,
then performs 2^d-1 packed XOR updates and population counts. It also
validates its input and writes each mask-indexed count once. These are
operation counts, not equal-cost CPU instructions or a runtime lower bound.

The complete reached domain has 3,780 cores with s=24,d=7, established by
the unchanged consumer. The new conformance run records every invocation.
It accounts for 11,521,440 replaced parity evaluations, 635,040 column bit
tests and 480,060 packed updates. It compares all 480,060 nonzero-mask
section counts with direct parity evaluation before any histogram grouping.

## Verification boundary

The written invariant proves the replacement. The exhaustive smaller-list
checks and complete reached-domain comparison corroborate its implementation.
They do not independently validate the predecessor's mathematical conclusion.
Local timings measure the complete scientific consumer in fresh processes.
They do not prove portable performance, native supplier costs, a new kappa,
or any of the selected construction's five framework assumptions.
