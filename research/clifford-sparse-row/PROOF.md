# A sparse reconstruction formula at Clifford width 13

Fix one Gaussian-dyadic unitary representative `U` of each four-qubit
Clifford scalar coset. For normalized columns `(vec(U)/4)^(tensor 13)`
write `c_U` for the input mixture coefficients. The width-13 proof
recovers the matrix `M_S = sum_(U over S) c_U U` for each symplectic
action `S`, then returns `Tr(U* M_S)/16`. Here we compile its group
algebra identity into **4,265 signed reads for one complete matrix
M_S**, shared by its 256 coefficient outputs.
[Width-13 source, sections 1–4](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md)

## Measurement coordinates

Use `V=F₂⁸` with Z in the low four bits and X in the high four bits,
and write `G=Sp(V)`. The seed of six unphased Weyl labels is
`T=(0,Z1,Z2,Z3,Z4,X4)`. Its affine Bell orbit is `G/C`, where `C`
is the order-eight group of controlled-Z shear products on the
first three qubits. In this orbit, the ordered input/output tuple pair
`(g_in T, g_out T)` selects the set `g_out C g_in⁻¹` of symplectic
actions. All tuple images here use the **affine Bell action**.

Given a normalized observation vector, multiply by `4^13`, view it as an
operator on thirteen registers, and take the matrix block between these
six-pair Bell input and output tuples. The other register gives a 16-by-16
block. With `w_in,w_out` the respective XORs of the six Weyl labels,
multiply by `W_(w_out)` on the left and `W_(w_in)⁻¹` on the right.
Apply the transport phase `j_in / j_out` from section 2 of the cited
proof. Explicitly, if `U W_t Uᵀ = θ_U(t) W_(L_S t)` and
`U W_v U* = γ_U(v) W_(Sv)`, then for a transporter g of the seed use
`j_g = (product_(t in T) θ_U(t)) / γ_U(XOR(T))` for any Clifford lift
of g. The phase is constant on each transporter coset. Thus the corrected
block returns the **sum** of the M matrices over the selected set.
The averaging factor 1/8 is accounted for below. On an arbitrary
off-image observation the same instructions define a linear block read.

## Compress the two character sums

Let `A=Sym₄(F₂)` be the abelian group of 1,024 shears fixing the
Z-Lagrangian pointwise. We use additive notation for its masks, and
write `e_J=|J|⁻¹ sum_(j in J) j` and
`e_Q=|A|⁻¹ sum_(a in A) χ_Q(a) a`.
The source proof assigns each character Q an isotropic three-plane W
and a factor d, with `d e_Q e_(C_W) e_Q = e_Q`. Here
`C_W=g C g⁻¹` for a transporter taking the first three Z directions
to a basis of W. Its generators from two independent basis vectors
u,v send y to `y + <y,u>v + <y,v>u`.

Group characters by the actual plane W. For a fixed W let
`H=A∩C_W`, `N=N_A(C_W)` (its normalizer within A), and
`h=|H|, k=[A:N], m=[A:H]`. Every character assigned to W is trivial
on H. In the double sum with factors a,b replace a by `x+b`. The
product of character signs is `χ_Q(x)`, and the group term becomes
`x e_(b C_W b⁻¹)`. Conjugation depends only on `b mod N`.
Translation depends only on `x mod H` because b commutes with H.
Consequently

```text
d e_Q e_(C_W) e_Q
  = d/(m k) sum_(x in A/H, b in A/N) χ_Q(x) x e_(b C_W b⁻¹).
```

For a raw eight-element coset **sum**, let
`F_W(x) = sum_(Q assigned to W) χ_Q(x)`. The resulting coefficient is
`d F_W(x)/(8 m k)`.

- **All-Z W.** Here `C_W <= A`, so h=8, k=1, m=128 and d=1.
  The coefficient of the read is `F_W(x)/1024`.
- **Mixed W.** Write `W=P + span(ℓ)`, with P a two-plane in the
  Z-Lagrangian and ℓ its chosen nonzero pure-X covector annihilating P.
  The source proof gives `H=Λ²P` of order two and d=4. For p in P
  the basis change `T_p=I+pℓᵀ` gives a complement to H in C_W.
  A shear B normalizes C_W exactly if
  `T_p B T_pᵀ + B` lies in H for all p in P. With `v=Bℓ` this difference is
  `pvᵀ + vpᵀ + (ℓᵀv)ppᵀ`. If v lies in P it belongs to Λ²P.
  Conversely a nonzero p forces `ℓᵀv=0` by the zero diagonal of H.
  The remaining alternating matrix belongs to Λ²P for every p only
  if v lies in P (take p nonzero and examine its image when v is
  outside P). The linear map B↦Bℓ is onto the four-dimensional
  Z-Lagrangian: in a basis adapted to ℓ it is the last column of a
  symmetric matrix, which can be chosen freely. Hence k=4, m=512,
  and the coefficient of each read is `F_W(x)/4096`.

The compiler uses the source verifier's lexicographic plane selection.
For each plane it chooses a single binary basis by scanning its points
in ascending order. Replacing one basis of the same plane by another
does not change C_W. It evaluates F_W by a length-1,024 signed Walsh
transform and drops zeros. For a surviving pair x,b the transporters are

```text
input_map  = b g
output_map = S (x+b) g
```

where S is the desired output fibre. The term therefore measures
`S x b C_W b⁻¹`. Division by 1,024 suffices for the emitted integers,
since every nonzero mixed F_W used here is divisible by four.
This denominator is attained by the fixed compiled row. The program
does not claim a minimum denominator or a sparsity lower bound for all
possible decoders.

Two blocks with the same affine tuple input and output would select
the same subset of G. The verifier expands every emitted coset as
eight actual binary matrices and checks that all subsets are distinct.
The available coefficients sum over each of their group elements to
exactly the single chosen indicator. This supplies an independent direct
certificate for the resulting list, without relying on Fourier
orthogonality inside its final test. Choosing one Bell pair of tuples
to represent an equal coset sum is valid on the mixture image. On general
noise the chosen block coordinates define this particular decoder, whose
norm is computed below.

## Counts and Euclidean bounds

For the identity fibre the seven all-Z planes contribute 17 reads and
the fifteen mixed planes contribute 4,248. The 34,120 group terms
encounter 8,304 distinct group elements. The signed numerator sums are
1,024 at the identity and zero at each other one. All other target fibres
use the same list with its outputs left-translated by S.

For raw-sum coefficients `a_t = numerator_t/1024` the certificate gives

```text
sum_t |a_t| = 25/2,        sum_t |a_t|² = 1/8.
```

For a fixed U over S, the final trace against `U*/16` has Euclidean row
norm 1/4 on a matrix in the Frobenius norm. The left/right Weyl and scalar
phase corrections are isometries, and the normalized observation supplies
the factor `4^13`. The Bell basis change is unitary. Since distinct reads
occupy distinct ordered input/output blocks, they are orthogonal as
functionals. This gives the exact squared norm of a scalar output row
of the compiled decoder, `(4^13/4)² / 8 = 2^45`.

For a simultaneous norm bound group terms by their actual input Bell
tuple i, and put `m_i = sum_(t with input i) |a_t|`. There are 67 such
inputs. Their absolute numerator masses are as follows.

| Absolute numerator mass | Number of input tuples |
| ---: | ---: |
| 128 | 29 |
| 192 | 10 |
| 224 | 8 |
| 240 | 8 |
| 288 | 12 |

A fixed term of seed output o sends the normalized matrix coordinates
`Y_(j,i)` to one matrix at each S by reading `Y_(So,i)` and applying
unitary entrywise-block corrections. As S ranges over G, every j in the
orbit occurs |C|=8 times, by orbit-stabilizer. Thus, before restoring
normalization, this map has operator norm at most √8 on Frobenius direct
sums. For fixed i the weighted sum of terms has norm at most `√8 m_i`.
Across different i the input domains are orthogonal. Cauchy–Schwarz
bounds their combined norm by `sqrt(8 sum_i m_i²)`. Within each output
fibre, taking all 256 traces against the orthogonal representative
matrices jointly multiplies the Frobenius norm by 1/4. Therefore the
full normalized decoder satisfies

```text
||B_13||₂ <= 4^12 sqrt(8 sum_i m_i²) = 4^12 sqrt(1319/64) < 2^27.
```

At f>13 apply the width-13 map on the first factors and the identity
on the remaining ones. In each output component next contract the
remaining factors against its own unit-norm target row. The latter
direct-sum operation has norm at most one, so the bound persists.
These estimates concern a specific finite linear operator. Its block
count assumes access to the indicated Bell-coordinate projections.
Acquisition from physical storage and the complete multiplier cost
require their own accounting.

The width-13 result and its coset readout are due to apoursh, building
on Ali Romman's Clifford/Bell work and the character and Pauli lineage
of Nick Petalas and alephnan. Fourier compression and Walsh transforms
are classical. Prepared by **apoursh** with substantial OpenAI Codex and
separate agent assistance. Apache-2.0.

## Transport phases in the executable read list

The program fixes a lift for each binary transvection with nonzero axis `p`. Write `q(p)=x_p·z_p mod 2`, `P=i^q(p) W_p` and `U=(1+i)(I+iP)/2`. For ordinary conjugation, a commuting label is fixed with phase one. An anticommuting label has image `t+p` and phase `i^(1+q(p)) (-1)^(z_p·x_t)`, from the product `iP W_t`. To obtain the Bell action multiply the conjugated Weyl on the right by `U U^T`. This is `−W_p` if `q(p)=0` and `iI` otherwise. Tracking the six Bell phases and subtracting the ordinary phase for the XOR of the labels gives the transport exponent modulo four. The opposite signs of the input and output exponents in the read list undo the block phase.

The executable reduces a symplectic matrix to the identity one column at a time. For current and desired labels `u,v`, already fixed columns span `F`. The vector `u+v` pairs to zero with `F`. If `<u,v>=1`, the transvection along `u+v` sends `u` to `v`. For distinct orthogonal labels choose an intermediate `h` pairing to one with both and having the same pairings as `u` with `F`. These linear constraints are consistent. Neither `u` nor `v` belongs to `F`; if `u+v` is in `F` the two requested values sum to zero, matching `<u,u+v>=0`. Nondegeneracy realizes the resulting functional. The two transvections along `u+h,h+v` fix `F` and put that column in position. Reversing the reduction realizes the specified transporter. The self-check also reconstructs the affine label offsets by quadratic parity. The literal matrix tests cover both types of transvection and off-identity target phases.
