# Independent count-bit formula derivation

Route C, S002, 2026-11-25. This independently checks the count-bit mechanism
sent by Route A during the final research wave. It is a positive formula
construction in characteristic two, valid on Boolean spectral indicators.
It is not a formal multilinear formula for the elementary symmetric
polynomial in independent indeterminates.

## CBF1. Carry formulas with charged copied-tree size

For Boolean bits x_i,y_i and incoming carry c_i, characteristic-two
addition is given by

    c_0=0,
    s_i=x_i+y_i+c_i,
    c_(i+1)=x_i y_i+(x_i+y_i)c_i.

These expressions give the bit and carry of the ordinary integer sum.
The previous carry occurs exactly once in the formula for the next carry.
Every use of an operand-bit formula is nevertheless copied and charged.

Let T_(r,k) bound the number of nodes in an actually unfolded formula for
bit k of a balanced sum of `2^r` input digits, each digit taking values
0,1,2. Its two initial bits are independent degree-one variables; all
other initial bits are constant zero. Padding unused digits by zero is
allowed. The formula need only compute bits through k.

If a_i,b_i are the sizes of the two child bit formulas, the displayed
carry recurrence has size

    size(c_i)=1+4i+2 sum_(j<i)(a_j+b_j),
    size(s_i)=3+4i+a_i+b_i+2 sum_(j<i)(a_j+b_j).

Since every formula has at least one node, these imply

    T_(0,k)<=1,
    T_(r,k)<=8 sum_(i=0)^k T_(r-1,i),
    T_(r,k)<=8^r binom(r+k,k).                         (CBF1)

The last step follows by the hockey-stick identity. In particular the
formula is polynomial in m when `r=ceil(log2 m)` and `k=O(log m)`. A naive
bound `(Ck)^r` loses the repeated-summation structure and is unnecessary.
The size here is the copied-tree size, not the smaller size of a circuit
that shares the child bits.

## CBF2. Syntactic degree and constant offsets

Give each initial bit variable syntactic degree one. Inductively, every
bit k has degree at most `2^k`. Indeed the two inputs at position i have
degree at most `2^i`, and if c_i has degree at most `2^i`, each summand of
c_(i+1) has degree at most `2^(i+1)`. The bit s_i has degree at most `2^i`.
The initial high bit has degree one, which only improves this bound.

Add the constant integer `(-u mod 2^t)` by one more instance of the same
adder, keeping the lowest t bits. The result is the bit string of
`c-u mod 2^t`, and the same syntactic-degree bound holds. The constant
operand adds no variable degree. Applying (CBF1) for one more level gives

    size(bit_k(c-u)) <= 8^(r+1) binom(r+k+1,k).          (CBF2)

This is valid for negative c-u as well; it represents the residue, without
ever dividing a query expression by an integer.

## CBF3. Low binomial coefficients from low bits

For every integer n, including negative n, and `0<=h<2^t`,

    binom(n,h) mod 2 = product_(j: bit_j(h)=1) bit_j(n mod 2^t).
                                                               (CBF3)

One direct proof uses formal power series over F2. The identity
`(1+T)^(2^t)=1+T^(2^t)` makes `(1+T)^n mod T^(2^t)` depend only on
`n mod 2^t`, also for negative integer exponents because 1+T is a unit.
Expanding the binary representation of the nonnegative residue gives
`prod_j(1+T^(2^j))^(bit_j(n))`, proving (CBF3).

Set `t=ceil(log2(D+1))`. A copied product of the selected bit formulas
therefore evaluates `binom(c-u,h) mod 2` with syntactic degree at most

    sum_(j: bit_j(h)=1) 2^j = h.

Summing h=0,...,D preserves maximum degree D. The actual formula size is
at most

    (D+1) [t(8^(r+1) binom(r+t,t-1)+1)+3]+2.           (CBF4)

For `m>=2` and `1<=D<=m`, this is bounded, for example, by
`2^15 m^8`. This deliberately loose absolute polynomial bound charges all
copies, all selected-bit products and both scalar coefficient operations.

## CBF4. Application to order-three spectral queries

Let omega be a primitive third root in F4. At a spectral tuple, the
commuting order-three query C_j has eigenvalue `omega^(k_j)`. For a shift
beta_j, the two expressions

    I_(j,v)=sum_(a=0)^2 omega^((beta_j-v)a) C_j^a,
    v=1,2,

are exactly the Boolean indicators of `k_j+beta_j mod 3=v`. Each is
affine in the allowed individual query powers `1,C_j,C_j^2`.
Use them as the low and high input bits of the digit
`k_j+beta_j mod 3`. Its ordinary integer value is in {0,1,2}.

For any integral u and D define the source interpolation expression

    P_beta = omega^(u-sum beta_j)
       sum_(h=0)^D (omega-1)^h binom(c-u,h) mod 2.       (CBF5)

Equations (CBF1)--(CBF4) construct a polynomial-size characteristic-two
formula of syntactic query degree at most D for this function. At every
spectral tuple its value is in F4. If `u<=c<=u+D`, the ordinary binomial
identity gives `P_beta=omega^(sum k_j)`. Outside that interval the formula
still gives the known original finite-field predictor value.

The formula is not required to agree with a formal multilinear symmetric
polynomial away from the Boolean indicators. The full-rate cyclic formula
compiler proves its factorization identity formally for the supplied
formula; it can then be evaluated at these actual query operators. Since
the order-three queries are simultaneously diagonalizable over F4, the
pointwise spectral identity proves the required operator identity.

Consequently the established compiler yields D affine pencil stages and
width at most `D^S` with `S<=2^15 m^8`. With all `3^m` shifts and fixed
duplication, the logarithm of the independent width is polynomial in m.
Common roots, coordinate algebra, Hermite tables and actual generation
therefore have the single-exponential-in-polynomial-m profile proved in
the existing cyclotomic generator audit. This meets the representation
premise IP4 for the original constant-tail choice `D=O(sqrt(m))`.

This conclusion uses the accepted cyclic factorization and generator
lemmas, the original count-tail bound, and the separately reviewed
order-three closure. It does not infer full-rate evaluation from the
adder circuit alone: the copied formula and its syntactic degree are
the inputs to that full-rate lemma.

The construction is nonmultilinear. Thus a lower bound restricted to
formal multilinear formulas, or to a flat sum of products, does not apply.
The finite exact verifier is recorded separately. Final global admission
remains with the session lead and the independent composition review.
