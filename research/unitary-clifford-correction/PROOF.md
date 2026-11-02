# Exact correction rank with a unitary reciprocal encoder

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written mathematical proof with exact finite corroboration.

## Contract and result

Work over the complex numbers with their standard Hermitian inner product. Put

```
C = ((1+i) I + (1-i) X)/2,   X = [[0,1],[1,0]],
C_h = C tensor ... tensor C  (h factors).
```

Let s>=0, q=2^s, h=s+1 and N=2q. The desired full-space endpoint is
T=I_q tensor C. Every one of the N inputs is arbitrary and independent.
A candidate uses a unitary square encoder E, one child
H=i^u C_h^eta with u in {0,1,2,3} and eta in {+1,-1}, its reciprocal
E*=E^-1, and a left correction F:

```
B=E* H E,       T=F B.
```

No coordinate may be discarded. The correction is a general linear map;
the endpoint in fact forces F=T B*, so F is unitary too. Rank means complex
linear rank on these N coordinates, not recursive rank or instruction count.
If H has eigenvalue multiplicities m_0,m_1,m_2,m_3 at 1,i,-1,-i, then

```
min over unitary E of rank(F-I) = m_2+m_3.
```

Consequently the phase- and direction-optimized minimum is exactly

```
q - 2^floor(s/2).
```

In particular sixteen forward rank-one lanes and one width-five child require
rank twelve. The unrestricted invertible-encoder optimum six is the cited
result of ywz65 / PR2516. The two statements have different encoder domains.
We neither reprove nor independently validate that predecessor's optimum.

## Lower bound for every unitary encoder

C is unitary, has eigenvalues 1,i, and is diagonalized by the real normalized
Hadamard basis. Thus T,H,B are unitary and have fourth power I. Since B is
invertible,

```
rank(F-I) = rank((F-I)B) = rank(T-B).
```

For any operator A define its Hermitian supporting functional

```
Q(A) = ((1-i) A + (1+i) A*)/2.
```

The values of Re((1-i) z) at z=1,i,-1,-i are 1,1,-1,-1.
Therefore Q(T)=I and Q(B)=I-2 P_bad, where P_bad is the orthogonal
spectral projection of B onto its -1 and -i eigenspaces. Its rank is
m_2+m_3. Orthogonality of this projection is where unitary encoding matters.

If v is in ker(T-B), then Tv=Bv. Apply
`<v,(1-i)Tv>=<v,(1-i)Bv>` and take real parts. This gives

```
||v||^2 = <v,Q(T)v> = <v,Q(B)v>
        = ||v||^2 - 2 ||P_bad v||^2.
```

Hence P_bad v=0. The entire kernel of T-B lies in ker(P_bad), whose
dimension is N-m_2-m_3. Rank-nullity proves the lower bound m_2+m_3.
This argument applies to every complex unitary E, including dense encoders;
it is not an extrapolation from sampled encoders.

## Attainment and explicit encoder

Every multiplicity m_j of H is at most q. Indeed, partition the h-bit Walsh
indices into pairs differing in their first bit. Their H eigenvalue labels
are adjacent modulo four, so at most one index in each pair has any specified
label. There are q pairs. Both target eigenspaces have dimension q.

Choose an orthonormal eigenbasis of T and of H. Match all m_0 child
1-eigenvectors to target 1-eigenvectors, and all m_1 child i-eigenvectors to
target i-eigenvectors. Assign the remaining child eigenvectors to the remaining
target basis positions in any order. The map E taking the target eigenbasis
to the assigned child eigenbasis is unitary. Then B and T agree on exactly
the matched N-m_2-m_3 basis vectors and disagree on every remaining one.
Thus rank(T-B)=m_2+m_3, proving attainment. F=T B* is the attaining correction.

Here is a fully specified real encoder without arbitrary eigenbasis choices.
Let W_h[x,y]=(-1)^popcount(x&y), let D be q copies of W_1 on the diagonal,
and let a_j be the child index assigned to target eigenbasis position j.
Target labels are 0,1,0,1,...; child index a has label
u+eta*popcount(a) modulo four. Process target positions in increasing order,
taking the least unused child index of the same label when available.
Fill the unmatched positions with the remaining child indices in increasing
order. If P has P[a_j,j]=1, set

```
K = W_h P D,       E = K/sqrt(2N).
```

K^T K=2N I, so E is real orthogonal. Its columns can equivalently be computed
by adding or subtracting the two assigned Walsh columns in each target pair.
This formula gives the endpoint for every independent input column.

For sixteen lanes take s=4, h=5, u=2 and eta=+1. H=-C_5 has
multiplicities (10,10,6,6), so the construction has correction rank twelve.
Here sqrt(2N)=8, K entries are 0 or +/-2, and E entries are 0 or +/-1/4.
Thus this attaining encoder is Gaussian-dyadic and has condition number one.
The finite verifier reconstructs every entry, checks the exact tensor child
against a separate distance-based formula, proves K^T K=64 I and
H E=E B by integer Gaussian arithmetic, and verifies F B=T and F*F=I.
It does not read or replay PR2516's rank-six witness.

## Phase optimization for all s

Before phase and direction, the multiplicities count h-bit indices by weight
modulo four. If z=(1+i)^h and N=2^h, the four-point root filter gives

```
m_j = N/4 + Re(i^(-j) z)/2.
```

The term at -1 vanishes since h>=1. All adjacent sums are therefore

```
m_j+m_(j+1) = N/2 + Re(i^(-j) (1-i) z)/2.
```

When h is odd, the maximum real part over the four rotations is
2^((h+1)/2). When h is even, it is 2^(h/2). In both cases the largest
adjacent sum is

```
N/2 + 2^floor((h-1)/2).
```

Changing u rotates the four multiplicities; inversion reverses their order.
The best phase therefore minimizes the unwanted adjacent sum to
N/2-2^floor((h-1)/2), giving q-2^floor(s/2). The case s=0 gives zero
and is included. This derivation proves the all-size statement; finite
weight counts only corroborate it.

## Scope and why the encoder hypothesis is essential

A two-dimensional control makes the lost freedom explicit. Set

```
T0 = diag(1,i),
B0 = [[1-2i,-2],[-2i,i-2]].
```

B0 has eigenvalues -1,-i, so it is similar to diag(-1,-i), and T0-B0
has rank one. But B0 is not unitary. Under unitary similarity the theorem
requires rank two. The control illustrates the hypothesis; it is not an audit
of a predecessor's construction or a claim that arbitrary encoders fail.

The result prices only algebraic correction rank. It supplies no physical
linear-form program, recursive tariff, asymptotic runtime gain, precision
policy, changed volume tariff, native caller or selected multiplier.
In particular, rank twelve is not twelve recursive calls. Conversely, it
is not a universal lower bound on encoders that may be nonunitary or on
networks with multiple children, independent input/output maps, clean
subspace promises or discarded outputs. Independent human and formal
proof-kernel review are unclaimed.

## Predecessor credit

ywz65 / PR2516 supplies the sharp unrestricted correction construction and
its explicit physical-boundary question. Arham Tahir / PR1920 supplies the
reciprocal-encoding contract and eigenmultiplicity obstruction. Greer Guthrie /
PR679, Ross Richardson, ToikY / PR1924, Douglas Colkitt / PR665, Jose Manuel
and Cinna Davis / PR1779, Josie Elliston / PR1817, icekylinx, DreamingOfClouds
and the retained Clifford/kernel lineage supply the surrounding context.
Their statements and source bytes are retained unchanged. Walsh bases,
spectral projections, supporting lines and rank-nullity are classical tools;
no global literature priority is claimed for them. The new result is the
exact norm-preserving correction rank in this full-space child contract.
