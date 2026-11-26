# Computing the actual label transfer and rectangle directory

This is the finite control input to the [two-pass pencil](foundations/uniform-payload-shared-pencil.md). Suppose `m>=4096`, `d>=2` is a power of two, `h=2d-1`, `q=2^t` with `t>=1`, and `N=q^(h*h)<=m^5`. Given `m,d,t` as binary words, the [fixed multitape controller](compiler-controller.md) constructs the original row/column pivot pairing, selected inverse minor, and both membership lists of each actual directed rectangle in at most **`m^60` transitions and `m^34` visited cells**. All ordinary heads return home. The result is an indexed finite descriptor. Payload motion and applying the address maps have separate costs.

## One canonical code per rectangle

A label consists of `h*h*t` bits in a row-major `h` by `h` array of `t`-bit letters. For a pair `(v,w)`, an inner block is either equal or has exactly `d` different letters. All other inner distances invalidate the pair. A supported off-diagonal pair has exactly `d` nonidentical inner blocks. This computes the [binary label matrix](foundations/characteristic-two-label-geometry.md), with all diagonal entries one.

In each differing inner block retain both complete letters at its first differing position. In each subsequent differing letter position, retain both high prefixes through their first unequal **bit** and set all lower bits on each side to zero. Keep equal letters unchanged. The result `(l,k)` is the pair of lexicographically least labels of the rectangle's two sides. The first differing letter in each affected block is recognizable from `l,k`; its entire two letters really are fixed. At the other differing positions the prefixes end with opposite bits. Every free suffix can be chosen independently. Replacing any such suffix therefore preserves the code, and the code specifies both whole Cartesian sides. Visit every supported off-diagonal pair and print it only if it equals its own code. This prints each rectangle once in the correct orientation without sorting or searching a dictionary.

For candidate `z` and side `l` or `k`, each equal-code letter must equal that letter, and the first differing letter must equal the full fixed letter on that side. At each subsequent differing position compare `z` with the chosen side through the first unequal bit of `l` and `k`. This membership procedure also gives each one-coordinate projection and the minimal anchors used by the [geometric lists](compiler-geometry.md).

## The inverse minor in one elimination

Initialize binary arrays `A=P`, `U=identity(N)` and all row flags unused. Scan columns in increasing order. In column `j` select the first unused row `i` with `A[i,j]=1`, when it exists. Mark that row used and append `(i,j)`. For every **other** row `k` with `A[k,j]=1`, XOR row `i` into row `k` of both arrays. Row `i` is fixed during this update. Let `I,J` be the two lists in pivot order.

We always have `A=UP`. Every processed pivot column is a unit vector at its selected row. Previously skipped columns vanish on all unused rows, since subsequent pivot rows also had zero there when selected. At completion the unused rows thus vanish, while the pivot rows are independent. Their number is `rank(P)`. Each selected row of `U` is supported on original selected indices. Each unused row is its own original unit vector plus a combination supported on selected indices. This starts true. Marking `i` places its whole row support in the enlarged selected set, and adding it to another row preserves the two invariants. It follows that `U[I,I]*P[I,J]=A[I,J]=identity`. These square matrices are inverses over the field. The middle-matrix coefficient from source `I_s` to destination `J_p` is `U[I_p,I_s]`. Original labels, inverse orientation and both orders matter to the actual caller.

## Loop and transition counts

All arrays are slices of the same indexed short-word bank. Label comparison and canonization extract a letter by a variable shift and mask, then inspect its at most `t` bits to find the first unequal bit. Scan `h*h` letters holding the first-unequal flag and distances per inner block. Per letter allow 32 word instructions for loop control and addresses, 40 for three word extractions/insertions, 32 for anchor/support flags, 16 per candidate bit, and 32 for final comparisons and updates. Thus `256(h*h+1)(t+1)` bounds a whole pair or membership test. This is at most `5120 log2(m) <= m^2` in the stated domain since `(h*h+1)(t+1)<=4h*h*t`.

| Part | Word-instruction upper bound |
|---|---|
| Parameters and initial arrays | Repeated small products form `h,h*h,N` and the slice addresses. Allocate/initialize flags and binary arrays for at most `128(N+1)^2` operations apart from support testing. |
| Support and anchor codes | All `N^2` pairs, each with one test plus at most 64 operations to store a table bit, advance, and optionally append a code. |
| Both membership sides | At most `N^2` codes, each tested against all `N` labels twice. Bound `2N^3(m^2+64)`. |
| Elimination and extraction | At most `N^3` innermost coordinate visits. Allow 96 operations each for address calculations, four loads, two XORs, two stores and loop control. Extract at most `N^2` inverse entries in the stored pairing order. Total at most `256(N+1)^3`. |

The sum is below `m^19` instructions. Indices and products fit the short words; the directory and matrices use at most `16(N+1)^3 < M` words. Multiplying by `m^37` transitions per instruction and adding initialization is below `m^60`. The `m^34` scratch budget is additive. In the native domain `m^4<=e` and `3^(2e)<=V`, `m^34<=V` by taking logarithms for `m>=4096`.

The [finite replay](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S008/compiler-check.py) independently compares the directory with brute-force adjacency and the inverse with separate selected-minor inversion. The numerical time theorem is a written proof for all legal arities. An end-to-end run at a native adaptive arity would be much larger.
