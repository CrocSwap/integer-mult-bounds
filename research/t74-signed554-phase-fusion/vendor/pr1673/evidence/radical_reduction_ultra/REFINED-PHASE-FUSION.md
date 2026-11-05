# A narrower positive route: fuse retained phase-cell interiors

Status: a complete parameter ledger for a concrete conditional transfer. It avoids the unresolved normalized-erasure adapter. It still requires the new shallow in-place structured-matrix circuit to be integrated with the retained fast tensor supplier and a grouped sparse boundary gather. No new selected certificate is asserted.

## Construction

Keep the already reviewed phase-cell Schur decomposition, with

```
d=p^epsilon, u=alpha^2=Theta(p^r), w=Theta(p^((1-r)/2)),
0<r, epsilon+r<1, epsilon>(1-r)/2.
```

The positive r may be arbitrarily small; it eventually dominates the old logarithmic lower bound on u. Thus this route can retain the established diagonal-dominance, rounded H, local inverse, and Schur residual proofs. The stronger fixed-a theorem is not needed here.

Within each no-gap phase cell, the interior matrix is exactly

```
A=diag(a_j) G diag(a_j)^-1,
G_ij=G_(i-j), log(max a_j/min a_j)=O(u d).
```

The retained G is a symmetric truncated Gaussian Toeplitz matrix with `||G-I||<1/8`; hence G and G^-1 are uniformly conditioned. Apply its inverse by the new shallow in-place low-displacement circuit, rather than summing the two Gohberg-Semencul branches. The circuit's Toeplitz coefficients and Schur generators are precomputed. This is the algebraic connection to the new in-place work; the old source proof did not provide such a tensor-fusible circuit.

Fuse

```
g=p^beta, beta=1-epsilon-r-zeta,
```

axes at a time, with fixed zeta>0. The total diagonal similarity guard is
`O(g u d)=O(p^(1-zeta))=o(p)`. Polylogarithmic circuit depth and bounded polynomial factor growth add only `O(g polylog p)=o(p)` bits. Every completed group has polynomial norm; error is allocated at the completed-group boundaries, preserving the retained O(p)-bit record model.

### Dyadic interiors without exponential padding

Inside a phase cell, repeatedly choose the largest power of two K such that `K+2w` fits the remaining interval, while its remaining length exceeds 4w. Make a piece of length K+2w, designate w endpoints on each side as boundary, and use its K remaining indices as the interior. The leftover interval of length at most 4w is all boundary.

The remaining length at least halves on each step. Thus there are O(log d) pieces per original cell, every interior has dyadic length, and the total boundary size grows by only O(log d). No padding by a factor two per tensor axis is used. Schur fill still joins only the two w-sized endpoint groups of a piece, so its scalar bandwidth remains O(w). Distinct dyadic size classes require only O(log p) circuit schedules; inactive axes use identity stages.

### Boundary arithmetic

Let R denote the number of spectator right-hand sides, which eventually exceeds every polynomial in p. Batch them in groups of w. Every dense w-by-w block multiplication in the banded forward/backward solve, the border correction, and the boundary/interior couplings then costs O(w^omega) scalar products for w right-hand sides, omega=log_2(7)<2.8081. The retained no-pivot factors are precomputed; Strassen creates only polynomial intermediate growth in w, hence O(log p) extra guard bits. Use the existing global residual argument to bound the completed solve error.

There are O(s*w*log(d)/d) boundary rows per axis. Consequently the total boundary arithmetic over all d axes is

```
O(V * w^(omega-1) * polylog(p)),
```

where V counts p-bit data volume. This includes H_BI and H_IB couplings; doing those couplings scalarly would incorrectly reintroduce V*w^2.

### Five stages separate fused interiors from sparse corrections

For the interior/boundary order write H=[A B; C D] and S=D-C A^-1 B. The exact identity

```
H^-1 = diag(A^-1,I) [I -B;0 I] diag(A,S^-1)
       [I 0;-C I] diag(A^-1,I)
```

is verified by multiplication. Thus the only full-interior stages are A and A^-1. The two shears use original banded B and C, whose support is within O(w) of each artificial cell boundary. The middle factor splits into the commuting interior A and boundary S^-1.

For a g-axis group, collect the union U of the O(w log d)-wide endpoint slabs. Its volume is O(V*g*w*log(d)/d). All sparse shear and boundary stages preserve this union; outside it they are identity. Process the g axis operators sequentially on U, without g scans of the full V data. Even a deliberately loose movement cost is

```
O(V*g^2*w*polylog(p)/d) per group,
O(V*g*w*polylog(p)) over all d/g groups.
```

Add one full scan per group to gather/scatter U, for O(V*d/g). This is below the proposed fused interior cost at the displayed parameters. Dense boundary arithmetic is still batched as above and costs O(V*w^(omega-1)*polylog p); scanning inactive entries in U is included in the movement bound.

The union-slab gather/scatter and the evaluation of its piece catalogues must be implemented in the retained macro-routing model. The address fields have polynomial length and g*polylog(p)=o(p), but that observation alone is not a tape routing proof. Importantly, the cost budget now tolerates a sequential factor g on the **sparse union**, so the required route is weaker than a fully fused boundary solver.

## Paid exponents

Let q be strictly below the supplied complex saving and below the bit saving. The proposed dominant costs, normalized by V, are

| Component | Power of p | Saving |
|---|---:|---:|
| Main transform with deferred reservations | 1-epsilon*q | epsilon*q |
| Fused Gaussian interior / convolution groups | epsilon-q*beta | 1-epsilon+q*beta |
| Group bit routing | epsilon-a_bit*beta | 1-epsilon+a_bit*beta |
| Sparse group scans | epsilon-beta | 1-epsilon+beta |
| Boundary algebra | (omega-1)*(1-r)/2 | 1-(omega-1)*(1-r)/2 |
| Sequential operations on sparse union | beta+(1-r)/2 | (1+r)/2-beta |

Every entry has an explicit cost source above. The similarity/normalization condition is `epsilon+r+beta<1`. The old full-axis scan Vd is not part of the claimed implementation; until its replacement is proved, this remains conditional.

Ignoring arbitrarily small zeta and strict absorption margins, balancing the first two rows gives

```
epsilon=(1+q-q*r)/(1+2q),
beta=(q-(1+q)*r)/(1+2q),
kappa=q*(1+q-q*r)/(1+2q).
```

This is feasible for `0<r<q/(1+q)`. Its improvement over the old same-q balance is

```
kappa-q/(1+q)
 = q^3/((1+q)*(1+2q)) - q^2*r/(1+2q) > 0.
```

Thus positive r is compatible with a strictly larger exponent, while retaining the old phase-cell analytic hypotheses.

One explicit arithmetic target uses

```
q=0.001675462576808103522925,
r=0.000001,
zeta=0.00000001,
epsilon=(1+q-q*(r+zeta))/(1+2q),
beta=1-epsilon-r-zeta,
kappa=epsilon*q-0.00000000001.
```

It yields

```
epsilon = 0.9983301313358845139763404147924773...
beta    = 0.0016688586641154860236595852075227...
kappa   = 0.0016726647643531934852000135266363...
```

The proposed kappa exceeds the selected 0.001672660197076918 by about 4.5672763e-9. Its boundary saving is greater than 0.09595, its sparse-scan saving is greater than 0.0033387, its sparse-union saving exceeds 0.49833, and the bit saving is strictly larger than q. This target is deliberately **not** promoted: the new circuit/supplier integration and grouped sparse tape route must first be proved.
