# A sharp four-axis reversible grid map

This contribution was produced by Nick Petalas. Apache-2.0.

## Claim and sources

Let `pi=1+i`, `C=[[i,1],[1,i]]`, and `U=pi^-4 C^(tensor 4)` on
sixteen Gaussian entries. These are the retained native Gaussian conventions,
as in David Ganz / Dugongue's [PR5815, C1-C3](https://github.com/CrocSwap/integer-mult-bounds/blob/f0fcda576df410dc15cd5b8183d4f74d284eba2b/research/gaussian-exceptional-correction/consumer-construction.md).
Ali Romman's [PR6536](https://github.com/CrocSwap/integer-mult-bounds/pull/6536)
asks whether four or more axes have a sum-preserving optimal grid map with an
explicit inverse and practical table. Its three-axis theorem is a cited
predecessor, not a verification target here.

**Theorem.** There is an explicit bijection `F: Z[i]^16 -> Z[i]^16` fixing
zero and preserving the complex sum, such that both

`||F(x)-Ux||_2 <= sqrt(8)` and `||F^-1(y)-U* y||_2 <= sqrt(8)`.

No integer-output map can improve either uniform constant. Scaling every input
and output by a positive grid spacing h multiplies the error by h. The shared
real classification table, including both directions and keys, has a 3,072-byte
packed representation. This is a scoped proof with a finite construction
certificate, not a complete multiplication theorem, physical tariff or new kappa.

## Reduction to two real Walsh maps

Index coordinates by four-bit integers. Let `W_rs=(-1)^popcount(r&s)` and
`D_jj=(-i)^popcount(j)`. Then `W^2=16 I` and

`U=-D W D/4`.

Indeed, `pi^4=-4` and
`i^(4-popcount(r xor s))=D_rr W_rs D_ss`.
The one-axis matrix `C/pi` is unitary and has row sum one, so U is unitary
and preserves the complex sum. All phases and the leading minus sign are kept.

We construct a bijection `R: Z^16 -> Z^16` approximating `W/4` and apply it
separately to real and imaginary components between these diagonal rotations.
For any integer vector z, put `q=Wz mod 4`, with residues in `{0,1,2,3}`.

## The complete finite quotient

Let v_s be column s of W. Modulo four,

`v_s=v_0 + sum_(j:bit_j(s)=1) (v_(2^j)-v_0)`.

This follows from `ab = a+b-1 mod 4` for signs a,b. Each difference has order
two and v_0 has order four. Therefore every q is represented by

`a(t,b)=(t-sum b_j)e_0 + sum b_j e_(2^j)`,

where `0<=t<4` and the four b_j are bits. The 64 keys are distinct: row zero
gives t and row `2^j` gives `t-2b_j mod 4`. This describes the whole quotient,
including all negative and arbitrarily large integer inputs. These elementary
Walsh/Smith quotient facts are prior algebra, not the new contribution.

`construction.py` independently generates the column span modulo four.
`verify.py` generates the displayed 64 representatives and requires equality
of the two key sets. No enumeration of a large input box is used to infer coverage.

## Finite correction certificate

For each key q the certificate supplies an integer offset e(q) satisfying:

1. `e(q)=-q mod 4`, component by component.
2. `||e(q)||_2^2 <= 64`.
3. `sum_j D_jj e(q)_j=0`.
4. `p(q)=W e(q)/4 mod 4` is a permutation of the 64 keys.
5. `e(0)=0`.

The construction first lists a sufficient subset of corrections. For an odd
key, start with components -1 at residue 1 and +1 at residue 3; replace up to
six selected components by their negative triple. For an even key, choose
either sign of 2 at residue 2 and zero at residue zero. Keep zero weighted-sum
corrections and select the least squared norm on each reached quotient edge.
These are candidate subsets, not an exhaustive closest-vector search.

A deterministic breadth-first augmenting-path matching chooses 64 edges.
The certificate checker checks conditions 1-5 directly, independently of the
matching search. It also checks the inverse offsets below, both weighted sums,
all table domains and the claimed norm bound. Thus correctness depends only
on the finite checked predicates, not on completeness or optimality of the
candidate search. The code uses no solver or pending Git object.

The serialized rows, in lexicographic key order, consist of sixteen unsigned
key bytes, sixteen signed forward offset bytes and sixteen signed inverse
offset bytes. Both real components use the same table. The inverse offsets
are indexed by the same sorted key set; no permutation array is needed.
The verifier emits the payload hash and all package-file hashes to stdout.
It does not write or trust a prewritten receipt.

## All-input inverse and error proof

Define `R(z)=(Wz+e(q))/4`. Condition 1 makes it integral. Also `W e(q)` is
divisible by four: e(q) is congruent to `-Wz`, and `W^2 z=16z`.
For an output y, its key is

`Wy mod 4 = W e(q)/4 mod 4 = p(q)`.

Since p is a permutation, that key identifies q. Set

`f(p(q))=-W e(q)/4`, and `R^-1(y)=(Wy+f(Wy mod 4))/4`.

Substitution gives `R^-1(R(z))=z`. Conversely, this formula is integral on
every target class because `f(p)=-p mod 4`; substituting in the other order
gives every y back. This proves bijectivity on the entire integer lattice.
Since `W/4` is orthogonal, `||f(p(q))||=||e(q)||<=8`.
Both real forward and inverse errors are at most two.

Let `R_C` apply R to both components. Define

`F(x)=-D R_C(Dx)`,
`F^-1(y)=D^-1 R_C^-1(-D^-1 y)`.

All rotations and R_C are bijections. The formula proves the literal inverse;
it does not assume an ideal square or fourth-power rewrite for F.
Two real squared errors at most four give total squared error at most eight,
in either direction. The zero offset fixes zero.

The difference `F(x)-Ux` is `-D(e(q_real)+i e(q_imag))/4`.
Condition 3 makes its complex sum zero, so F preserves the exact sum.
Its bijective inverse then preserves that sum as well.

## Sharpness and what improves

Take `x=(2+2i,0,...,0)`. Every real and imaginary component of Ux is a
half-integer, because `Ux_j=-D_jj(1+i)/2`. Any Gaussian integer output has
squared error at least `32/4=8`. The same argument applies to U*.
This lower bound applies to every integer-output rule, including nonbijective
rules. The construction attains it while retaining the inverse and sum.

This answers the four-axis part of PR6536's first open question. If an ambient
tensor has N entries and one group acts independently on sixteen-point blocks,
the aggregate error is at most `h sqrt(N/2)`. In particular, one four-axis group
has half the triangle-inequality bound obtained by two separately rounded groups
of sizes three and one. This comparison uses the predecessor's stated group
guarantees; it does not replay them or assert a complete caller implementation.
Phase covariance, exact fourth power, a physical speedup and optimal whole-call
error are not claimed.

## Executed evidence and limits

The verifier checks all 64 forward/inverse correction rows and all 4,096 pairs
of independent real quotient representatives. Another 64 signed fixtures,
three inputs with 128-, 1024- and 4090-bit components and the sharp witness give
4,164 endpoint fixtures. Each runs both directions, the literal inverse, exact
sum and an independently written direct native-matrix error oracle. Ten controls
reject missing or changed offsets and malformed or oversized inputs.

The executable API caps components at 4,096 bits, keeping its allocation bounded.
For round trips, inputs with at most 4,090 bits leave ample output headroom.
The mathematical formula and written proof quantify over all Gaussian integers;
finite large-word cases do not establish that quantifier by themselves.
No inherited scientific result is audited. Independent human and formal
proof-kernel review are unclaimed. All five selected framework assumptions remain.
