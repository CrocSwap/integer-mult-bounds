# Independent mathematical check

This review concerns the fixed Gaussian-integer lifting word in
`vendor/period-PROOF.md`, not a different lifting construction. The period
theorem and its authorship remain inherited from that source. The review was
prepared with GPT-6.1 Sol, independently of the main checker's lattice-basis
intersection code. `independent.py` imports neither the main checker nor the
vendored implementation. Files are Apache-2.0.

## Assumptions and all-rank result

Let `V = Z[i]^(2^r)`, and use componentwise Euclidean floor. Let `C_j` be
the ideal pair operation on address bit `j`, and let `U=C_(r-1)...C_0`.
Let `Gamma` be the full translation group described in the vendored period
theorem: every paired difference at each forward ideal entrance is in
`2 Z[i]`. In particular, these prefix conditions imply every ideal prefix
is integral. Define

```
Lambda = Gamma intersection U Gamma.
```

For every integer `r>=0`, this is the largest `U`-invariant additive
sublattice **contained in Gamma**. The forward floor word equals `U` on
`Lambda`, and its literal inverse equals `U^-1` there. Both preserve
`Lambda` exactly. These are written all-parameter proofs below; the finite
index computation is separate, and no formal-kernel proof is supplied.

For a pair, `C^2` swaps its two addresses. Different address-bit stages
commute, so `U^2=S`, where `S` complements every address bit, and `U^4=I`.
Every address-XOR permutation commutes with every ideal stage and preserves
each paired-difference constraint, up to changing its sign or its pair
label. Consequently `S Gamma=Gamma`. Thus

```
U Lambda = U Gamma intersection U^2 Gamma
         = U Gamma intersection Gamma = Lambda.
```

If `K subset Gamma` and `U K=K`, then `K subset U Gamma`, hence
`K subset Lambda`. Even the weaker assumption `U K subset K` gives equality
because `U^4=I`, so the same maximality follows. This argument is about
sublattices of the stipulated period group; it is not a maximality result
for every possible exactness domain or every possible caller encoding.

On `Gamma`, every floor operation divides an even Gaussian difference by
two and is exact, so the literal forward word equals its ideal word.
For `y=U x` with `x in Gamma`, literal bijectivity gives
`L^-1(y)=x=U^-1 y`. This proves inverse exactness on `U Gamma`, and therefore
both assertions on `Lambda`. No small rounded residual is erased.

## Why reverse prefix parity is exactly U Gamma

For a given bit `j`, write `H_j` for the integral vectors with all
bit-`j` paired differences in `2 Z[i]`. Since the ideal output difference
is `i` times the input difference, `C_j` is an automorphism of `H_j`.
Its inverse is `C_j^-1=S_j C_j`, where `S_j` swaps addresses on bit `j`.

If a forward admissible trajectory starts in `Gamma`, its ideal reverse
trajectory traverses the same integral states, and the condition at each
inverse entrance holds by the output-difference identity. Conversely, an
admissible inverse trajectory reverses to an admissible forward one.
Therefore the inverse-prefix parity lattice is exactly `U Gamma`.

The inverse trajectory uses `-i` stages in reversed bit order. Replacing
those stages with `+i` stages only inserts an address-XOR permutation on
already visited bits at each prefix. Such permutations preserve the next
paired-difference test. Thus the reverse-order `+i` prefix lattice is also
`U Gamma`. This does not assume access to PR3046's inverse basis.

## Caller closure and explicit failures

`Gamma` and `Lambda` are `Z[i]` modules. Whole-array `ADD` and subtraction
preserve `Lambda`, as do global negation and multiplication by `i`. They
also preserve all address-XOR permutations. Global complex conjugation
preserves both lattices: if `U_k` is a forward prefix, then

```
U_k conjugate(z) = S_<k conjugate(U_k z),
```

where `S_<k` complements the already visited address bits. This preserves
the next parity condition. The same argument works for reversed prefixes.

This yields a literal reversible local macro for `x,y in Lambda`:

```
L(x);  y += x;  L^-1(x).
```

It implements `(x,y) -> (x,y+U x)` with two completed transforms and one
whole-array ADD, using no private helper. All intermediate complete arrays
are in `Lambda`, and `x` is restored literally. Arbitrary dirty values are
allowed **within this lattice**, not throughout the original integer grid.
This is a local operation count, not a complete recursive cost theorem.

Single-coordinate updates do not have this closure. The exact axial test,
valid for every `r>=1` and every address `a`, is

```
t e_a in Lambda  iff  t in (1+i)^(r+1) Z[i].
```

Indeed, after `k` stages a spike has `2^k` nonzero entries, each equal to a
Gaussian unit times `t/(1+i)^k`. At the next stage each is paired with zero.
The required even difference is therefore equivalent to divisibility of
`t` by `(1+i)^(k+2)`. The strongest test occurs at `k=r-1`. This argument
does not depend on the order of the visited bits, so it applies to both
forward and reverse lattices. For real integer `t`, the smallest positive
allowed value is

```
q_r = 2^ceil((r+1)/2).
```

At rank 7 the axial subgroup is `16 Z[i] e_a`. The all-ones array is in
`Lambda`, while adding one of its coordinates to a single target coordinate
changes another valid array by `e_a`, which is not in `Lambda`. In-place
`x[a] += x[b]` likewise fails on the all-ones array. Adding an external
single-coordinate constant is safe exactly when that constant obeys the
axial divisibility test.

Local Gaussian phases also fail. Changing one coordinate of the all-ones
array from `1` to `i` or `-i` violates the first paired-difference parity
test. Changing one coordinate from `1` to `-1` leaves a displacement
`-2 e_a`, which fails for every `r>=2`. At rank 1, coordinate negation does
preserve the lattice. More directly relevant to a structured phase word,
let `Q_j` multiply every address with bit `j=1` by `i`. Applied to all ones,
earlier forward stages are the identity, and stage `j` sees `(1,i)`.
Thus `Q_j` fails to preserve `Gamma` or `Lambda` for every `r>=1` and every
`0<=j<r`. No assumption about arbitrary point phases is needed for this
failure witness.

Quarter-SCALE preserves the fixed lattice exactly on entrance domain
`4 Lambda`: for `x in Lambda`, one has `x/4 in Lambda` if and only if
`x in 4 Lambda`. Integral output alone does not suffice. Take
`x=max(4,q_r) e_a`; it belongs to `Lambda` and is divisible by four
coordinatewise, but `x/4` fails the axial test. At rank 7 this is simply
`16 e_a -> 4 e_a`. More generally no nonzero sublattice of an integral
grid can be closed under arbitrarily repeated division by four: iterating
it on any nonzero vector eventually gives a noninteger coordinate.
A changing grid or staged sublattice contract may avoid this obstruction,
but its precision, adapters and restoration must be charged.

## Independent finite index calculation

The check forms all integer congruence rows for both actual forward `+i`
prefixes and actual inverse `-i` prefixes. A difference test after `k`
completed stages has denominator `2^k`; its evenness condition is an
integer congruence modulo `2^(k+1)`. Scaling every row to the common modulus
`2^r` gives a homomorphism `A:Z^(2^(r+1)) -> (Z/2^r)^m` with
`ker A=Lambda`. The lattice quotient is therefore exactly `image A`.

The independent routine computes that image by modular Smith elimination.
At every step it chooses a nonzero pivot of least 2-adic valuation `v`,
normalizes its odd unit, and clears its column by invertible row operations.
Clearing the remaining entries in its row by column operations leaves the
lower-right block unchanged. The image factor contributed is
`Z/2^(r-v)`. This is a different calculation from successive index-two
changes to a basis for the primal lattice.

Reproduction, from this package's checkout root:

```
python3 research/p104-invariant-lifting-lattice/independent.py
```

The exact finite outputs are:

| Rank | log2 index Gamma | log2 index Lambda |
| ---: | ---: | ---: |
| 1 | 2 | 2 |
| 2 | 6 | 7 |
| 3 | 15 | 17 |
| 4 | 34 | 39 |
| 5 | 75 | 87 |
| 6 | 161 | 187 |
| 7 | 343 | 401 |

At rank 7 the independent quotient decomposition is

```
Z^256/Lambda = (Z/16)^4 x (Z/8)^29 x (Z/4)^91 x (Z/2)^116.
```

This restricts the period domain by another 58 index bits relative to
`Gamma_7`. It is not a claim of 58 physical storage bits spent, or 401
physical bits saved, or any particular scalar/recursive runtime saving.

The script also checks the following finite domains and controls:

* Every binary real-coordinate input at ranks 1 and 2: respectively 16 and
  256 vectors. Direct rational-prefix membership agrees with the modular
  constraints, and admitted vectors pass forward/inverse literal checks.
* All 256 two-by-two matrices modulo four: modular Smith image cardinality
  agrees with direct enumeration of all 16 input vectors for every matrix.
* At every rank 1 through 7: the axial threshold, coordinate ADD failure,
  local and half-address phase failures, integral quarter-output failure,
  and exact forward/inverse operations on an admitted nonzero spike.
* At rank 2: duplicating the forward constraints instead of including the
  inverse constraints gives index exponent 6, while the correct common
  lattice gives 7. A bounded search finds an explicit vector in `Gamma`
  outside `Lambda`, whose ideal image leaves `Gamma`.
* All 625 rank-one pair inputs in `{-2,-1,0,1,2}^4`: the 313 members of
  the larger state-exactness lattice described below have exact literal
  forward and inverse operations and ideal images in that lattice.

The index computation is exact finite integer linear algebra. Only the
small binary-cube and modulo-four validations are finite exhaustive
enumerations over all inputs in their stated domains. Nothing here is a
formal-kernel certificate or an exhaustive finite check of unbounded
integer vector membership; the lattice calculation and written proofs
provide those separate forms of evidence.

## Scope, broader exactness domains, and unresolved costs

Do not omit the `Lambda subset Gamma` premise in the maximality claim.
Already at rank 1, the larger lattice

```
K = {(a,b): a-b in (1+i) Z[i]}
```

has index 2, is `C` invariant, and has `P=C` and `P^-1=C^-1` on it. The
pair floor defect is `(h(Im(a-b))-h(Re(a-b)))*(1-i)/2`; it vanishes when
the two parities agree, whereas translation rigidity requires both to be
even. The pair `(a,b)=(1,i)` is an explicit member of `K` outside `Gamma`,
so the phase failure witness above refutes the chosen period-lattice
entrance contract, not the equality of the literal and ideal output on
that particular state. Thus the full period lattice can be strictly
smaller than a useful state-only exactness lattice. No all-rank optimal
state-exact lattice is proved by this package. This rank-1 observation is
an elementary scope counterexample, not a larger-kappa claim or a new
accepted frontier.

Finally, choosing a lattice basis `B` and storing arbitrary logical data
as `B z` changes the corresponding logical transform to `B^-1 U B`.
An implementation of that conjugated integral operation does not by
itself implement the original physical/native `U` interface at the same
price. A favorable complete caller must pay encoding/decoding, required
intertwining or native adapters, precision and range, entry of arbitrary
dirty data, nonpreserving coordinate/phase/scaling operations, and the
recursively charged children. The local macro proves none of these costs
small. The rank-7 common-lattice index and exact local interface therefore
do not establish supplier admission, an improved recursive recurrence, or
an exponent saving.
