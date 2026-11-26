# Executable elementary lists for a rectangle endpoint

Use the actual star geometry of [B2](foundations/explicit-dyadic-geometry.md) in ambient dimension `D=2(2+h q^h)`, with `a=D-2` early and `a` late reserves. Assume the [label parameters and directory](compiler-labels.md) and `D<=m`. Every individual basis, rectangle basis or endpoint reserve preparation below uses at most **`16D` elementary operations**. A composition of two such bases (including conversion of the rectangle’s displaced spare coordinates to fixed positions) uses at most **`48D` elementary operations and `96D` child exchanges per grouped call sequence**. The query-specific lower-triangular change uses at most **`5D` lower shears**, including occupied early and late reserves, with no spatial child. For the inverse, reverse the operation list, negate each shear coefficient, reciprocate each diagonal scaling, and keep every exchange.

## List convention

Primal coordinates are `e,z,F_(a,u)`, followed by their duals. The active basis columns are formed by `column_i += c column_j`, unit diagonal scalings, and coordinate exchanges. If the basis is made from identity by right multiplication `M=E_1 … E_s`, a column vector is acted upon in reverse order `E_s,…,E_1`. Thus the corresponding coordinate shear changes its `j` entry by `c` times entry `i` when constructing an address action from that column update. The inverse applies the inverted factors in forward order. This transposition of source/target indices for **column construction** is required for the physical list. The lower map below is stated directly on address values and follows its written order.

Every reordering of at most `2D` named slots, with unnamed spectators fixed, is implemented by placing the correct entry in each wrong position by one exchange. This uses at most `2D-1` exchanges and works with arbitrarily many intervening spectator fields. It applies in particular to permutations within early reserves and moving `E` into prescribed late spare positions. Reversing list order describes a physical inverse, preserving all originally occupied data.

## Three basis constructors

* **Individual endpoint.** Starting with the ambient columns, replace `z` by `z+sum_a F_(a,v_a)` in `h` additions. For columns `X=e,Y=z_v`, produce `(e+z_v)/2,(e-z_v)/2` by `X+=Y, Y*=-2, Y+=X, X*=1/2, Y*=1/2`. Reverse orientation, if prescribed, by exchanging the two pair columns. For every untouched coordinate `c` subtract its two projections onto the pair columns with two column shears. Use a final permutation to the prescribed order. This uses `h+5+1+2(D-2)+2D <= 6D+2 <=16D` operations. Constants for each projection appear below.
* **Common rectangle.** Its source and destination minimal anchors `l,k` come from the directory. Replace each nonanchor feature by its difference with its side anchor, with one column shear for each star. Then form `g=-2z−sum_a(F_(a,l_a)+F_(a,k_a))` in the old `z` slot using one scaling and `2h` additions. Choose the least differing outer coordinate `a0` and its source anchor as the distinguished pivot. In that feature slot form `r0=−g/2+sum_a(F_(a,l_a)−F_(a,k_a))/2`: first scale the distinguished column by `1/2` and add the other anchor terms and `−g/2`. Only unchanged anchor columns are read. Common-side repetitions cancel or can be omitted. Form the pair `(e+r0)/2,(e-r0)/2` using the five-operation butterfly. Reorder to `(C_R, reference pair, E)`. All nonanchor feature pivots, `g`, and the distinguished pivot are distinct. This uses at most `D+(1+2h)+(2h+2)+5+2D <= 8D+8 <=16D` operations. Moving displaced inactive spares to their designated fixed positions can add at most another `2D` permutations when composing with a full common layout.
* **Reserve-only endpoint.** In the `D−2` individual complement coordinates first form the stars as above. Form `A=sum_a(F_(a,l_a)−F_(a,k_a))` in the distinguished feature slot using its original coefficient +1 and at most `2h` other additions. At a source replace it by `A+2 sum_a s_(a,v_a)`; at a destination use `−A+2 sum_a t_(a,v_a)`. Missing anchor stars are zero. These are the actual individual-complement coordinates of `g`. Permute to the chosen `C_R,E` order and exchange the `E` slots with equally many occupied late reserves. At most `D+2h+1+h+2D+D <= 8D` operations. Only early/late reserve coordinates participate, so the same list serves every query of this incidence.

B2 proves these columns are bases over the dyadic integers and give the correct common address. Every explicit scalar in the lists is a signed power of two, including its inverse at the fixed radix 3. A shear contributes at most two spatial child exchanges, a field transposition one, and a diagonal none when using the [physical primitive](address-dyadic.md) or the equivalent separately counted diagonal. Skip every zero coefficient instead of asking for its inverse. Adjacent shuffles of identical spectators do not occur.

## The post-preparation list on actual coordinates

Let `sigma=+1` on a source and `−1` on a destination, `r_i=sigma z_v`, `x_i=(e+r_i)/2`, `y_i=(e-r_i)/2`. Write `Delta=r_i-r0` in the explicit star-and-cross basis. At a source, `Delta` is the sum of its active source stars. At a destination, `Delta=g−sum` of its active destination stars. Thus at most `h+1` of its coefficients are nonzero, all +1 or −1.

Post-preparation the occupied early slot with value `A_c` corresponds to `p_i(c)=c−<c,x_i>x_i−<c,y_i>y_i`. For every such slot directly perform the two lower shears

    H -= <c,x_i> A_c
    N -= <c,y_i> A_c

where `H,N` are the chosen two main fields. Use these updated values for the rest of the list. For each nonzero component `Delta_k` perform

    late[k] += (Delta_k/2) H
    late[k] -= (Delta_k/2) N.

Indeed `H x_i + N y_i = H x_0 + N y_0 + (H−N) Delta/2`. All other active and spectator coordinates retain their own values. The nonzero pairing data are as follows.

| `c` | `<c,x_i>` | `<c,y_i>` |
|---|---:|---:|
| primal `F_(a,u)` with `distance(u,v_a)=d` | `−2 sigma/d` | `2 sigma/d` |
| `e*` | `1/2` | `1/2` |
| `z*`, or `F*_(a,v_a)` | `sigma/2` | `−sigma/2` |

All unlisted entries vanish. This is immediate from `B(e,e)=B(z,z)=2`, `B(F_(a,u),F_(a,v))=−4 Far(u,v)/d` and the primal/dual identity block. There are at most `2|C_R|+2(h+1) <=5D` lower shears. No product of upper triangular elementary maps is hidden here. The signed shear numerators and denominators in reduced form have magnitude at most `max(2,d)`; diagonal values before inverting are among `−2,−1,1/2`. All formulae act without reducing any occupied coordinate's range.

## Generating the list on fixed tapes

On demand, form the two side tests for one outer position by reading the stored anchor bits. Enumerate all `h q^h` primal feature labels. For each feature, a single [membership-word comparison](compiler-labels.md) determines its side, anchor and nonanchor flag for the corresponding coordinate. Retain flags and slot numbers on the short-word tape. For a requested endpoint, enumerate the `D` coordinates to form the early list, the two pairing coefficients and the active stars; a Hamming test touches at most `h` letters. To generate the final permutation, store current and desired names and, for each wrong slot, search at most `2D` slots to place its desired value. Use at most `128(D+1)^2` operations for loops, slot/address arithmetic and all exchanges here, plus `8(D+1)(m^2+128)` for the membership, pairings and local emissions. Three complete lists including a separately recorded inverse and displaced spare permutation therefore fit `m^6` word instructions and `m^4` words in the shared controller at `D<=m,m>=4096`. The short-word physical bound gives fewer than `m^44` transitions including initialization even if the controller recomputes a list on every request. Larger row multiplicities never enter these finite loops.
