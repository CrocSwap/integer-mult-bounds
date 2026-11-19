# Character check on the marked Lagrangians

For each of the 81 ordinary conjugacy representatives in the pinned class data, compute the permutation character by counting its fixed points on pairs $(L,v)$, where $L$ is Lagrangian and $0\ne v\in L$. Each invariant $L$ contributes $|\ker(S-I)\cap L|-1$ and every other $L$ contributes zero. The count is the same on both ordinary classes in the fused packet. This calculation tests fixed flags directly, independently of the classification of relative positions of two marked Lagrangians.

For a rationalized character $\chi_B$, its norm squared is the number of irreducibles in its Galois packet $B$. Take its character inner product with the fixed-flag character, divide by this norm, and obtain the multiplicity of each constituent. The action on all 34,425 flags decomposes as follows.

| Ordinary degree | Multiplicity | Normalized Gram eigenvalue |
|---:|---:|---:|
| 1 | 1 | $470624175/2^{32}$ |
| 51 | 1 | $22846598775/2^{32}$ |
| 119 | 1 | $359889075/2^{31}$ |
| 135 | 2 | $1132984125/2^{32}$ |
| 918 | 2 | $15074084025/2^{33}$ |
| 1190 | 2 | $5790052125/2^{33}$ |
| 2856 | 1 | $2289090375/2^{30}$ |
| 3400 | 1 | $6597966375/2^{34}$ |
| 4200 | 1 | $1068242175/2^{31}$ |
| 5712 | 1 | $29452962825/2^{35}$ |
| 13600 | 1 | $35251991775/2^{35}$ |

The scalar is the fixed-space central kernel evaluated on the ordinary character, as in #7816. All listed constituents are rational, and their multiplicity-weighted degree sum is 34,425. Their squared multiplicities sum to 20, the number of orbitals. The 11 distinct positive scalars give exactly the minimal polynomial's roots, each simple, since a central operator is scalar on each irreducible. In particular the inverse on this whole flag module can be represented by a polynomial of degree at most ten. The weighted sums of the scalars and their reciprocals also agree with the independently computed traces: each trace is 34,425 times the corresponding diagonal orbital entry.

The smallest common odd denominator of the **full inverse matrix on flags** is 4,073,770,240,465,467,939,271,875. All 20 orbital entries have denominators dividing it. One entry on flags at distance one with distinct marks contained in the common intersection already forces the entire denominator. This is the unrestricted flag inverse before restriction to the particular singleton right-hand sides in the mixed problem. [Fixed-flag character and exact denominator replay](flag_spectrum.py) · [Orbital convolution and mixed inputs](POINTED.md)
