# Exact projector-call cost of a square-zero coupling

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and boundary

Let `N` be an `R x R` binary matrix with `N^2=0`, and put `q=rank(N)`.
Let `g` be a fixed nonidentity involution. Work in the full formal group
algebra `F2[C2]`, with `C2={1,g}`, and write `Q=1+[g]`. Thus `Q!=0`
and `Q^2=0`. The required full endpoint is

```
D_N = I + Q N.
```

All `R` input roles are arbitrary. A paid call is `I+Q P`, where `P=uv^T`
is a binary rank-one idempotent, equivalently `v^T u=1`. Arbitrary constant
binary invertible scalar maps may occur freely anywhere. Any finite number
of additional arbitrary dirty roles may be used, but they must be restored
with no residual couplings. On those enlarged roles the required endpoint
is `I+Q (N direct-sum 0)`.

The exact minimum number of paid calls is zero when `q=0`. For `q>0` it is

```
L(q) = q+1, if q is odd;
       q+2, if q is even.
```

Equivalently, it is the smallest even integer strictly greater than q.
No bound is placed on the original word length, finite workspace dimension
or placement of free scalar maps. Other address labels and clean or discarded
workspace are outside the theorem.

The identity `product_j (I+Q A_j)=I+Q sum_j A_j` is inherited from
ywz65's [PR2716](https://github.com/CrocSwap/integer-mult-bounds/pull/2716).
That package implements each nilpotent rank-one term with two address calls.
The new result determines the exact cost of jointly compiling a square-zero
matrix of arbitrary rank into the original idempotent-call alphabet.

## Remove free scalar maps

For a constant invertible scalar matrix S,

```
S (I+Q P) = (I+Q S P S^-1) S.
```

Conjugation preserves binary rank-one idempotence. Move every free scalar
factor to the right. The complete word becomes a product of paid calls
followed by one scalar matrix S. Apply augmentation `[g] -> 1`: every paid
call and the required endpoint augment to I, so S=I. Consequently every legal
word gives

```
N direct-sum 0 = sum_(j=1)^L P_j.                 (1)
```

To read off this equality, compare the coefficient of the formal basis
element `[g]`. This uses `g!=1`. Conversely any such sum gives the entire
formal endpoint, since Q is central and Q^2=0. No nonfaithful representation
is used to certify endpoint equality. The normalization is the standard
register-model argument, not a new result claimed here.

## Lower bound

Equation (1) implies `L>=q` by rank subadditivity. Each binary rank-one
idempotent has trace one. A square-zero matrix has trace zero: for example,
`trace(N^2)=sum_i N_ii^2=trace(N)` over F2, since off-diagonal terms cancel
in pairs. Thus (1) also implies L is even.

It remains to rule out L=q, even after arbitrary dirty padding. Suppose
`N direct-sum 0=UV`, where U has the q image columns u_j, V has the q
functional rows v_j, and every diagonal entry of VU is one. Since UV has
rank q, U has full column rank and V has full row rank. Choose a left
inverse A of U and a right inverse B of V. Square-zero gives

```
0 = A (UV)^2 B = VU,
```

contradicting those diagonal entries. Therefore L>q. Together with even
parity this proves `L>=L(q)`. Padding changes neither rank nor square-zero,
so this proof includes every finite restored dirty workspace.

## Construction for odd rank

First take the canonical square-zero matrix on 2q coordinates,

```
N = sum_(i=1)^q e_i f_i^T,
```

where the distinct coordinates e_i span its image and the coordinates f_i
are their chain preimages. Let `h=sum_i e_i^T`, a row functional supported
on the image coordinates, and let `u=sum_i e_i`. For odd q use the q+1
rank-one matrices

```
P_i = e_i (h+f_i^T), for 1<=i<=q;
P_* = u h.
```

Every P_i is idempotent because `(h+f_i^T)e_i=1`. Also `h u=q=1` in F2,
so P_* is a nonzero rank-one idempotent. Their sum is N, since
`sum_i e_i h=u h` cancels P_*. Consequently the q+1 legal paid factors
have full product `I+Q N`.

At q=3 this replaces six factorwise calls by four. In coordinate order
`e_1,e_2,e_3,f_1,f_2,f_3`, the factors are specified by

```
u_1=100000, v_1=111100;
u_2=010000, v_2=111010;
u_3=001000, v_3=111001;
u_*=111000, v_*=111000.
```

Here strings list coordinates left to right, rather than integer bit
significance. The two target blocks are arbitrary dirty inputs; the map is
`e_i <- e_i + (1+[g]) f_i`, with every f_i unchanged.

## Even rank and arbitrary matrices

For positive even q, split the q chains into blocks of sizes q-1 and one.
Both sizes are odd. Apply the preceding construction separately on the two
blocks. This uses `(q-1)+1 + 1+1=q+2` legal calls and gives their direct-sum
endpoint. Unused coordinates remain untouched.

For any square-zero N, choose an image basis e_1,...,e_q and choose preimages
f_i with `N f_i=e_i`. Their 2q vectors are independent: applying N to a
linear dependence first kills all preimage coefficients, then independence
of the e_i kills the rest. Extend them to a basis by vectors in ker N.
This is possible because the image is contained in ker N. Thus N is
binary-similar to the canonical chains plus zeros. Conjugate every constructed
projector by that same binary basis. Rank-one idempotence and the complete
projector sum survive, and the number of paid calls stays L(q).

These basis maps specify legal projector factors. They do not require clean
initial values or erase any initial role. If an implementation admits only a
coordinate reflection, each projector can be implemented by a scalar basis
change, one reflection, and the inverse scalar change, as in PR2716. Those
scalar operations must be separately charged in a physical comparison.

## Scope of the improvement

PR2716's factorwise construction uses 2q address calls for a rank-q
square-zero coupling. The new optimum saves `2q-L(q)` calls in the same
optimistic formal idempotent-call model. It first saves two at q=3. The
lower bound concerns one fixed involution label; extra address operations
may change it. It does not identify formal calls with recursive child rank.

The result supplies neither a native reflection supplier nor a complete
scalar, frame, routing, precision, hosting, stock or tape invoice. No new
multiplication bound follows. The universal quantifiers rest on this written
proof. The finite shortest-path and full-operator checks are corroboration;
independent human and formal proof-kernel review are unclaimed.

Credit ywz65/PR2716 for the arbitrary-coupling product and implementation
motivation; Adam Gall/PR1911 for the dihedral register context; eumemic/PR288,
Ali Romman/PR468, woklerx/PR1443, Gareth Davidson/PR1333 and the retained
register-model lineage. PR2716 also credits Arham Tahir/PR1589 and Cinna
Davis/PR2290 for enlarged-coupling precedents. No literature-priority claim
is made for matrix rank, trace, square-zero normal form or idempotent sums.
