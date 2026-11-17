# Exact independent-radical tariff on a cheap directed cycle

This scoped written proof was produced by Nick Petalas. Apache-2.0.

## Contract and result

Let `R = F2[e,h,z]/(e,h,z)^2`, with maximal ideal `m=(e,h,z)`.
The three independent dirty rows and disjoint preserved source belong to
`R^w`, for any positive width w. Require

    A_i = a_i + lambda_i p,       lambda=(e,h,e+h+z).

The only gates are fixed input-independent operations

    P_i(b): A_i += b p,           price mu_i > 0;
    E_ij(a): A_i += a A_j,        price c_ij > 0, i != j.

All coefficients are available, with coefficient-independent, stationary
prices. Zero gates may be deleted. Every original dirt column must return.
There are no extra rows, observations, clearing or free basis changes.
The three cycle edges `0 -> 1 -> 2 -> 0` cost c. Set `mu=min_i mu_i`.
Assume `mu >= 6c` and every reverse edge costs at least `6c`.

**Theorem.** The exact complete abstract price is `2mu+6c`.
In particular, insertion prices 100, cycle prices 1 and reverse prices 100
have optimum 206. This is not a physical tariff or a multiplication theorem.

The demand, contract, incoming-row return lemma and two-unit-insertion
argument are credited to lee-phys #6210. We restate those short arguments
for a self-contained proof. The new step is the six-ADD lower bound with
cycle edges, its matching word and the resulting price cone. No predecessor
numerical result or verifier is rechecked.

## Preliminary facts

Every element of R is uniquely `a+u`, with `a in F2` and `u in m`.
Its units have a=1; every nonzero nonunit lies in m. For `u in m`,
`R u={0,u}`, and units act on u as the identity. In particular `m^2=0`.
The three demands form a basis of m over F2.

Track the three dirt columns and source column in a 3-by-4 matrix. Its dirt
part is invertible at every cut and returns to identity. A nonzero incoming
ADD cannot occur exactly once at a row. Indeed, before that sole ADD its
dirt row is the original standard row. Restoration would force the added
multiple of the sender's current dirt row to be zero. Multiplication by the
inverse current dirt matrix would then force its nonzero coefficient to
be zero. Thus a used receiving row has at least two incoming ADDs.

A one-insertion word is impossible. Its final source column is an invertible
matrix column times the inserted coefficient beta. If beta is in m, the
three demand coordinates lie in the one-dimensional space `{0,beta}`.
If beta is a unit, reduction modulo m gives a nonzero column, whereas every
demand is in m. Both contradict the target.

With exactly two insertions, both inserted coefficients must be units.
If just one were a unit, reduction modulo m would again give a single
nonzero invertible-matrix column. If neither were a unit, the final demand
coordinates would lie in the F2-span of their two radical coefficients,
contradicting the three independent demands. These are #6210's arguments
specialized to this ring.

## Two insertions require at least six cycle ADDs

Suppose a two-insertion, cycle-only word has at most five nonzero ADDs.
By the incoming-row lemma, some row receives no ADD.

If the insertions enter different rows, every insertion row needs an ADD:
otherwise its final source coefficient is its sole unit insertion. The
third row also needs an ADD, since its demand is nonzero. Each then needs
at least two, a contradiction. Hence both insertions enter the same root i.

The other two rows j,k must receive ADDs. If i also receives any, the total
is at least six. Thus i receives none. Relabel cyclically so the only
remaining directions are `i -> j -> k`. Write beta,gamma for the inserted
units. Root i's source coefficient takes values `0,beta,lambda_i`, since
`beta+gamma=lambda_i`. Row j's dirt is always `e_j+a(t)e_i`.
Both j and k receive at least two ADDs.

### If j receives exactly two ADDs

Their coefficients are equal to some nonzero a, by restoration of j.
Its final source is `a(s+t)`, where s,t are the root source coefficients
at its two ADDs. Their sum is one of `0,beta,gamma,lambda_i`.

The first value gives zero. The last gives either zero or lambda_i.
Neither is lambda_j. The remaining values are units, so obtaining the
radical lambda_j requires `a in m`, and then `a=lambda_j`. Every intermediate
source coefficient at j is consequently in `{0,lambda_j}`. Every source
contribution delivered to k is in the same ideal. This cannot give the
independent lambda_k. Thus j cannot receive exactly two ADDs.

### The only remaining case is three ADDs at j and two at k

Let the three nonzero coefficients at j be a,b,d, with `a+b+d=0`.
No proper nonempty subset of these three coefficients sums to zero:
a singleton would be a zero gate, and a zero pair would force the third
to be zero.

The two coefficients at k are equal to a nonzero v, since the coefficient
of the original dirt j is always one in row j. Between the two k ADDs,
let Delta a be the change in j's dirt coefficient of i and Delta s its
change in source coefficient. Restoration and the target require

    v Delta a=0,        v Delta s=lambda_k.

If v is a unit, `Delta a=0`. The preceding subset observation means either
none or all three j ADDs occur between the k ADDs. In the former case
Delta s=0. In the latter Delta s=lambda_j. Thus k gets zero or lambda_j,
not lambda_k.

If v is a nonunit, it is a nonzero radical. The two equations force
`Delta a mod m=0` and `Delta s mod m=1`. But the three j ADDs contain either
zero or two unit coefficients, because their total is zero modulo m.
Root i's residue is one exactly between its two insertions. Final j has
residue zero, so either both unit j ADDs fall in that insertion interval,
or neither does. Over any time interval, j's source-residue change is
therefore either zero or equal to its dirt-residue change. In the interval
between the k ADDs that change is zero, contradicting `Delta s mod m=1`.

These cases exhaust every cycle-only word with two insertions and at most
five ADDs, regardless of their interleaving or coefficient values.

## An attaining word

Choose any root i and put `j=i+1 mod 3`, `k=i+2 mod 3`. In chronological
order define

    Q_i = E_ji(1+lambda_j), E_kj(lambda_k), E_ji(1).

Its matrix is `I+N`, where

    N = lambda_j E_ji + lambda_k E_kj + lambda_k E_ki.

All entries of N lie in m, so `N^2=0`, `Q_i^2=I`, and
`Q_i e_i=e_i+lambda_j e_j+lambda_k e_k`. The word

    P_i(1+lambda_i), Q_i, P_i(1), Q_i

restores every original dirt column. Its source column is

    (1+lambda_i) Q_i^2 e_i + Q_i e_i
      = lambda_i e_i + lambda_j e_j + lambda_k e_k.

Every coefficient is nonzero. The word has two source insertions and six
cycle ADDs, for price `2mu_i+6c`. For root zero it is

    P_0(1+e), E_10(1+h), E_21(e+h+z), E_10(1),
    P_0(1),   E_10(1+h), E_21(e+h+z), E_10(1).

The unused third cycle edge is still available to competing words.

## Complete tariff

A correct word needs at least two insertions. With at least three,
its cost is at least `3mu >= 2mu+6c`. With exactly two and a reverse ADD,
its cost is at least `2mu+6c`. With exactly two and only cycle ADDs,
the proved six-ADD lower bound gives the same price. Choosing a root
with minimum insertion price attains it. This proves the theorem.

## Exact finite corroboration

The verifier independently enumerates all order-zero gate skeletons with
at most five cycle ADDs and exactly two unit insertions, including arbitrary
zero-residue ADD coefficients. No symmetry or heuristic pruning is used.
A 3-by-4 binary matrix is the order-zero state. Each gate's radical part
adds a linear generator to its first-order response; existing generators
propagate by the binary row operation. Since `m^2=0`, this expansion is exact.
Each radical coordinate has an independent copy of the same linear system.
The target's three radical coordinate columns span the entire pure-source
subspace. A closing skeleton can realize the target if and only if all
three pure-source basis matrices lie in its response span.

A layer is merged only when its constant matrix, response subspace and
both gate counts coincide. These determine every future transition and
solvability. The search allows zero-valued nonunit ADD coefficients, an
overapproximation harmless for exclusion. All two-unit insertion locations
and all six cycle ADD residue types are included. Seven finite transition
rounds cover all such words. None is solvable. This corroborates the written
five-ADD exclusion; it is not a proof-kernel certificate.
