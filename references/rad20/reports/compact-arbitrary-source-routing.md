# Arbitrary-source compact shears and coordinate routing

This is a new conditional movement argument. It generalizes the independently
reviewed later-source compact gadget to sources anywhere outside the active
target set. Finite address controls pass, including a counterexample to an
unmasked variant. Independent mathematical review is pending. No bulk
resampling improvement is asserted by this report.

The intended contract is a complete rectangular stream
`[P] x [2^n] x [R0]`, with bit volume V, n=O(p), total address length O(p),
and the same coefficient records as before. P may have arbitrary positive
cardinality. The requested permutation acts on the n named binary coordinate
slots, identically in every P fiber, and is described by polynomial work in p.
The accepted original equal-width, arbitrary-gap chunk interchange has cost
O(V*(H^tau+1)), tau=1-a. This contract and the original fixed-tape machine
interfaces remain conditional inputs. The conclusion is a coordinate
permutation cost O(V*p^tau*polylog(p)+poly(p)), including useful short-record cases.
The additive supplied-map/setup term is absorbed by the superpolynomial
full-tensor volume in the intended applications; it is explicit in the
general contract.
This is not arbitrary sorting of records by unrelated computed keys.

## A masked later-source gadget

Use fields u,t at the front, y in the middle and b at the back of the binary
word. Each temporary field has H bits. Put B=2^G and choose spaced target
positions j_i=rho+iK in y. Only indices i in a fixed ACTIVE set are used.
For each active i choose a distinct source position s_i in y, outside the
entire target set of this simultaneous XOR stage. Sources can be inside
guard fields or at inactive selected positions. The shear is
`y[j_i] <- y[j_i] XOR y[s_i]`; it fixes every other bit and every temporary.

For an active control z_i=parity(u_i), define F_u by the four updates

```
y += sum_ACTIVE 2*z_i*t_i * 2^j_i
t += sum_ACTIVE y[j_i] * B^i
y += sum_ACTIVE z_i*(1-2*t_i) * 2^j_i
t -= sum_ACTIVE (y[j_i] XOR z_i) * B^i.
```

The two t updates are executed by interchanging t with b, rotating b,
and restoring the interchange. Consequently every rotation's controlling
fields are before its target: y updates read only u/t; b updates read y/u.
The packed t update is ordinary modular integer addition, with the stated
carry guards, rather than independent digit-wise arithmetic.

Let A(y)=sum_ACTIVE y[s_i]*B^i. Execute F_u, load u+=A(y) by shuttling u
to b, execute F_u again, and unload u-=A(y) by the same shuttle. This uses
ten rotations and twelve compact interchanges. On a good address F_u changes
only active target parities, fixes all source/guard bits and restores t.
The second F therefore reads the same source bits as the load. Since
parity(u_i+A_i)=parity(u_i) XOR A_i, the two toggles give exactly the
specified shear, with u,t,b restored. No source-value reading occurs during
an incomplete four-update identity.

The good set requires active u_i,t_i != B-1 and
`2B <= floor((floor(y/2^j_i) mod 2^K)/2) < 2^(K-1)-2B`.
The quotient is the K-1-bit guard just above y[j_i].
Under these tests none of the temporary digit updates carries, and the y
updates remain inside their own guarded K-bit segments. Inactive digits
are never read or changed by the identity. A y target within its last K
bit slots is handled separately by an elementary exact XOR.

Masking is essential. At G=1,K=5,width(y)=10,ACTIVE={0},s_0=5, take
`(u,t,y,b)=(2,0,264,0)`. The ideal map fixes this good address. If both
four-update identities also toggle the inactive selected bit5, the actual
output is `(3,0,265,0)`: both a wrong active output and unrestored u. The
masked implementation returns the required `(2,0,264,0)`.

## Repair and tape cost

Each elementary modular rotation is globally bijective since all its
controls precede its target. Reversing the complete operation sequence,
negating rotation offsets and recomputing controls from the current address
gives its inverse even on bad addresses. The ideal shear T preserves the
bad predicate: it fixes every guard and temporary digit. The constructed
bijection S equals T on the complement of the bad set. Thus S maps the
good set onto itself, and necessarily maps the bad set onto itself too.

Extract current bad records, assign each key `T(S^-1(current_address))`,
stably radix-sort the distinct keys and reinsert into their marked holes.
This is the accepted local repair argument. All source positions, ACTIVE
flags and modular controls are computable in polynomial time in p; a
polynomial-size descriptor is permitted and is not reread for every payload
bit. Sorting keys have O(p) bits. For at most p active targets the density is

```
delta <= p*(2*2^-G + 8*2^(G-K)) <= 5/(128*p^3),
G = 4*ceil(log2(p))+6, K=64G.
```

Each controlling prefix fiber contains at least one complete enlarged
record, so there are at most M fibers. The fixed-tape rotation scan therefore costs O(V+M*poly(p)); the
superpolynomial record length absorbs descriptor arithmetic. The repair
scan costs O(V+M*poly(p)+delta*M*p*(R+p)), which is O(V). The original
amortized scan counter is retained. Each invocation pays its own extraction
and reinsertion scan; no globally exponentially small exceptional-set
estimate is used.

## Scratch reservoirs and matchings

Suppose first that the binary word has n>=64G bits. Set
`H=ceil(n/K)*G`. Then H<=n/32, so n>=9H. Choose three disjoint reservoirs

```
R_k = [2kH,(2k+2)H) union [n-(k+1)H,n-kH), k=0,1,2.
```

Each has exactly 3H bits and consists of two front H fields and one back H
field. Partition a matching's edges: E0 avoids R0; E1 consists of remaining
edges avoiding R1; E2 consists of edges meeting both R0 and R1. E2 has one
endpoint in each of those sets and avoids R2. There is no duplicated edge.
Use the corresponding untouched reservoir for its edge class.

At most three ORIGINAL disjoint equal-H chunk interchanges place R_k in
u,t,b. The endpoint coordinates are in the intervening y field. These
interchanges are undone after the whole class; every original named scratch
bit is restored. The requested edge swaps use three directional XOR shears,
whose complete source and target sets are disjoint in each direction.
Splitting target positions by residue rho modulo K gives O(K) masked gadget
calls, with at most H/G active digits per call. The last K positions use
O(K) elementary XORs. To implement one without assuming a superpolynomial
record, use at most two original one-bit interchanges to place its source
and target at the first two binary slots. In every P fiber the CNOT is the
fixed four-quarter permutation 00,01,10,11 -> 00,01,11,10. Interchange its
last two adjacent complete quarters, then undo the placement. These are
original fixed-block scans, not arbitrary prefix functions with unabsorbed
O(M*poly(p)) arithmetic. Their cost is O(V) with the original amortized
counters. Global parameter/map setup remains polynomial in p and is
separately amortized by the full tensor volume. Thus the elementary
contribution is O(V*polylog(p)).

The O(K) compact calls cost O(V*K*(H^tau+1)), hence
O(V*n^tau*polylog(p)). Scratch placement and restoration cost no more.
For n<64G use elementary XORs throughout, at polylogarithmic volume cost.

Every permutation is the product of two involutions. On a cycle c_j take
`A(c_j)=c_-j` and `B(c_j)=c_(1-j)`, so B(A(c_j))=c_(j+1).
Each involution is a matching plus fixed points. All edge partitions,
residue classes and layout changes have polynomial descriptions in p and
can be generated on a fixed number of work tapes. This proves the claimed
movement cost when the original record length is already superpolynomial.

## Paying descriptors with untouched spectator records

CRT/resampling coefficient records themselves have only O(p) bits. They
cannot silently be used as superpolynomial records. Suppose a relevant
axis width ell=Theta(p^(1-epsilon)), for fixed epsilon>0. If n>3ell choose
untouched spectator fields S0=first ell bits, S1=next ell bits and
S2=last ell bits. Apply the same three-way matching partition with S fields.
For each class move its untouched S field to the actual suffix with one
original disjoint equal-ell swap; S2 is already there. Restore this placement
after the class. The enlarged record has length `R=R0*2^ell`, which is
superpolynomial in p. No coordinates or payload records have been added.
The source and target sets for this class avoid its spectator field.

Apply the scratch-reservoir construction to the remaining n-ell prefix.
All its endpoints lie there. Layout interchanges cost
O(V*ell^tau), and the prefix routing costs O(V*p^tau*polylog(p)).
The placement swaps are legal even for 3ell<n<4ell; taking S2 at the suffix
avoids partial-overlap errors. The same convention for the last three H
reservoir fields avoids overlap at n=9H. These placements use only the
accepted old interchanges, so the argument is not circular.

If n<=3ell, the elementary matching method costs O(V*n), bounded by
O(V*p^(1-epsilon)) and therefore O(V*p^tau) provided epsilon>a. This
holds for all current parameter rows. Small finite p thresholds and residual
prefixes with fewer than64G bits use the same bounded elementary fallback.

## Finite evidence and end-to-end boundary

[compact_arbitrary_source_routing.py](../code/compact_arbitrary_source_routing.py)
imports no compact producer. The fresh residue run
[20261008T0221Z](../runs/20261008T0221Z-arbitrary-routing-residues/)
passes3072 complete addresses including512 good addresses,17496 adversarial
addresses in243 families including3888 good cases,4079 nontrivial repair
cases,5912 complete permutation decompositions,1294 matching partitions,
33 scratch layouts and918 spectator placements. Nonzero rho and rho=K-1,
inactive-position sources, packed digit overflow and guard endpoints are
included. Complete small streams are repaired by independent stable radix
passes. The unmasked counterexample is retained. Wall time1.09 seconds,
peak RSS22324 KiB, no swaps. Source SHA256 is
`ad6aafb2c1bd89e5b333bbcabd5460600f3f24737649ea2e7cd06986635bb297`.
The earlier rho-zero source and output are preserved separately.

This can replace a known coordinate permutation in the FFT/CRT assembly.
It does NOT replace d independent Gaussian resampling exposures by one
permutation. Those calls remain charged using their actual support and
record widths. Hypothetical bulk-resampling exponent rows require a new
locality/halo/precision/fixed-tape transfer and independent review. Likewise
the movement claim itself awaits independent review before inclusion in a
current strongest multiplication certificate.
