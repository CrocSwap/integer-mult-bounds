# Eight owner residues determine the rounded inverse input

This is a scoped proof for the fixed integer map from zxv's
[PR #5444](https://github.com/CrocSwap/integer-mult-bounds/pull/5444).
The source matrix, its Gram identity and the quotient-fiber method are
predecessor inputs. The new contribution is the selected row certificate,
the sparse injective lattice and its direct residue decoder. The proof and
certificate were produced by Nick Petalas. Apache-2.0.

## Statement and boundary

Use the exact 112 by 8 integer matrix M in the pinned
`research/precision-state-frontier/FIXTURE.json`, in its original owner and
mode order. Let R round each component to the nearest integer, with half
ties away from zero. The unchanged map is

```text
K(z) = z - M R(M^T z / 52),       z in Z^112,
M^T M = 56 I_8.
```

Owner indices are zero based. Put

```text
S = (5, 33, 49, 53, 62, 65, 97, 108),
Lambda_g = {z in Z^112 : 2^g divides z_i for every i in S}.
```

**Theorem.** K is injective on every fixed residue coset of Lambda_5.
Equivalently, the 112 integer outputs K(z) and the eight residues
`(z_i mod 32)_(i in S)` determine every integer input z uniquely. There
is a direct exact decoder with eight scalar interval selections. Within
this fixed equal-bit observation family, five bits per selected owner
are necessary and sufficient for recovery of every integer input.

In particular K is injective on Lambda_5, which strictly contains
`32 Z^112`. The coordinate-lattice index is `2^40`, compared with
`2^560` for the uniform sufficient lattice in #5444. These exponents
measure input-lattice restrictions. They are not physical storage or
runtime savings. The forty-bit residue channel is also larger than the
predecessor's thirty-bit optimal packed same-grid recovery tag.

## The row certificate

Let A consist of the selected rows of M, in S order:

```text
 1  0  0  1  1  0  0 -1
 0  0  1  1  0  0 -1  1
 0  0  1  1  0  0  1 -1
 0  1  0  1  0  1  0  1
-1  0  1  0  0 -1  0  1
 1  0  0 -1  1  0  0  1
 1  0  0 -1 -1  0  0  1
 0  0  1 -1  0  0  1 -1
```

The following integer matrix H satisfies `AH=HA=2I`:

```text
 1  0  0  0  0  0  1  0
 3 -1 -3  2  2 -2  1  2
 0  1  0  0  0  0  0  1
 0  0  1  0  0  0  0 -1
 0  0  0  0  0  1 -1  0
-2  1  1  0 -2  1 -1  0
-1 -1  2  0  0  1  0 -1
-1  0  1  0  0  1  0 -1
```

Thus `A^-1=H/2`. In addition `det A=-16` and every entry of
`M A^-1` is integral, so these eight actual rows form an integer basis
of the complete row lattice. The injectivity argument needs only `HA=2I`.
All these fixed matrix identities are checked exactly by the verifier;
separate rational elimination checks the inverse and determinant.

## Injectivity

Suppose `K(z)=K(z')=y` and `z_S=z'_S mod 32`. Define

```text
q = R(M^T z/52),   q' = R(M^T z'/52),   s = M^T y.
```

Then `z=y+Mq`, and the rounding condition implies
`|s_j+4q_j| <= 26` for every mode j. The same holds for q'. Consequently
`|q_j-q'_j| <= 13`. This weak closed bound is enough; the exact half-tie
endpoint rules cannot enlarge it.

The selected residue equality gives `A(q-q')=32t` for some integer vector
t. Multiplication by H gives `2(q-q')=32Ht`, hence every component of
`q-q'` is a multiple of sixteen. Its absolute value is at most thirteen,
so `q=q'` and therefore `z=z'`. This proves the theorem on every residue
coset, without enumerating the unbounded input domain.

## Direct decoder

Given y and a vector r of eight residues in `[0,32)`, compute

```text
b = r - y_S,
v = H b,
a_j = (v_j/2) mod 16,
s = M^T y.
```

For a valid pair every v_j is even, because `Hb=2q mod 32`. If a v_j
is odd, reject. Each q_j must lie in the closed interval

```text
ceil((-26-s_j)/4) <= q_j <= floor((26-s_j)/4)
```

and must satisfy `q_j=a_j mod 16`. The interval has real width thirteen,
so it contains at most one integer in that residue class. Select that
integer if present and check the exact equation
`R((s_j+56q_j)/52)=q_j`, including the half-tie convention. Then set
`z=y+Mq` and check both `z_S=r mod 32` and `K(z)=y`.

A valid encoded pair passes every check and returns its original z.
The final checks reject an invalid pair whenever it has no preimage.
Each mode requires one interval selection, with no fiber enumeration.
The implementation is an exact integer reference, with a 4096-bit
operational input limit. The mathematical theorem has no magnitude limit.
No bit-operation, tape, reversible scratch or cleanup cost is asserted.

## Sharp equal-bit threshold

Let `u=(1,...,1)` in Z^8. Every actual row of M has even row sum, and
M has full column rank. The two distinct inputs

```text
z_0 = 48 M u,       z_1 = 56 M u
```

both belong to `16 Z^112`, and therefore to Lambda_g for every `0<=g<=4`.
Using the source Gram identity,

```text
R(M^T z_0/52) = R((672/13) u) = 52u,
R(M^T z_1/52) = R((784/13) u) = 60u.
```

Both outputs equal `-4 M u`. Thus K fails to be injective already on
the zero-residue coset when only four or fewer bits are supplied. The
five-bit construction separates this pair. The coordinate vector e_0
belongs to Lambda_5 but not to `32 Z^112`, which proves strict enlargement
of the uniform sufficient domain.

The threshold is for these fixed eight owners with a common bit count.
No optimum over different subsets, unequal bit allocations, nonlinear
observations or global packed tags is claimed.

## Scope and credit

This is an input-lattice and observation theorem for the unchanged integer
map K. Writing an input as `D x` with a nonuniform diagonal D does not
establish that `K(Dx)` is the same physical inverse in an anisotropic output
format. D need not commute with the linear inverse. A physical caller must
derive its actual lattice or pay for observations and eventual restoration.
No supplier, signed-invoice gain, new kappa or selected-frontier change follows.

Credit zxv #5444 for the lattice-fiber formulation, matrix fixture and unequal
precision question; Ali Romman #5323 for the sharp same-grid recovery theorem;
David Ganz #4929 and Dillon Amburgey #4933 for the native matrix/caller lineage;
and Brian / JoyboyBrian #5035 for the rounded kernel. Those results are cited,
not independently audited here. Their original files and notices are unchanged.
Independent human and formal proof-kernel review are unclaimed.
