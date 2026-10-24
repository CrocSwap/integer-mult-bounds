# A four-call compensated two-image interface

Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
Written all-width algebra with exact finite corroboration, not a proof-assistant
certificate, new κ or complete Gaussian supplier.

## 1. Inputs and intended output

Retain the actual base letters of lee-phys's PR4688 and Yiyang's PR4710:
U is CNOT(0→2), V swaps bits 0 and 1, `S e_x=i^popcount(x)e_x`,
`P=SUS`, `Q=SVS`, and

`C=((1+i)/2)I+((1-i)/2)X_0`.

Each base letter g is tensorized individually: `g_f=g^(tensor f)`. For
either `(A,B)=(U,V)` or `(P,Q)`, let

`L_f=A_f+2B_f`, `F_f=C_f L_f C_f`.

On two arbitrary independent inputs x,y we construct exactly

`(x,y) -> (F_f x,F_f^-1 y)`                               (1)

for every positive f. There is no assumed relation between x and y and
no initially zero logical array. The second output is a specified transformed
partner. It is not y restored. The goal is a local completed linear interface,
not two independent canonical Gaussian jobs.

## 2. A finite free inverse, uniform in tensor width

For either pair R=A^-1 B has order four. For the original letters,
`R=U^-1V=UV`; for the repaired letters it is `S^-1(UV)S` with absolute
phases. Hence R_f also has order four. The exact polynomial identity

`(I+2R_f)(I-2R_f+4R_f²-8R_f³)=-15I`

holds at every width. Therefore

`L_f^-1 = sum_(k=0)^3 c_k R_f^k A_f^-1`,
`(c_0,c_1,c_2,c_3)=(-1,2,-4,8)/15`.                     (2)

This formula and the source-prefix invertibility are predecessor results;
they are not claimed as new. All its terms are individually tensorized free
monomial words with fixed rational coefficients. The sum is formed by register
mixing after tensorization. This is not the tensor power of the width-one sum.

For a fixed sum of free words `D=sum_j d_j M_j`, implement the dirty-source
shear `E12(D):(x,y)->(x+D y,y)` one term at a time:

1. Apply M_j to the source y.
2. Add d_j times that source into x.
3. Apply M_j^-1 to restore the source y.

No clean copy is used. Every term sees the same original source y, since it
is restored before the next term. Arbitrary x and y are permitted. Negative
coefficients invert the shear. The same procedure implements E21(D).

## 3. Completed compensated product

For an invertible operator D, define

`W(D)=E12(D) E21(-D^-1) E12(D)
     = [[0,D],[-D^-1,0]]`.

Products act on column vectors from right to left. Since

`W(-I)=[[0,-I],[I,0]]`,

we obtain the exact noncommutative block identity

`W(D)W(-I)=diag(D,D^-1)`.                                (3)

The three shears within each W have palindromic order, so the literal
execution of (3) is: E12(-I), E21(I), E12(-I), E12(D), E21(-D^-1), E12(D).
Use D=L_f and the source-restoring implementations above. Sandwich this
product between two copies of `diag(C_f,C_f^-1)`. The result is

`diag(C_f,C_f^-1) diag(L_f,L_f^-1) diag(C_f,C_f^-1)
 = diag(F_f,F_f^-1)`,

proving (1) at every width. No commuting of C with L or its inverse is used.
Both inputs and both outputs remain explicit throughout the construction.

The elementary kernel satisfies `C²=X_0`, `C⁴=I` and `C^-1=X_0 C`. Thus
each boundary C_f^-1 requires one forward paid C_f and one free X_0,f.
There are two paid forward kernels per boundary, four in total.

The inverse of the completed map uses the same program with the two banks
swapped before and after: `J diag(F,F^-1) J=diag(F^-1,F)`. This implements
the actual algebraic inverse with the same four ideal paid calls and two
additional free bank swaps. It does not make a claim about the inverse of
an approximate child realization.

## 4. Complete ideal-game instruction bill

PROGRAM.json is an explicit straight-line program using only `paid_C`,
individual address letters and ordinary scalar ADDs. The allowed address
letters are U,V,X_0 and the three one-coordinate phases S_j and their
inverses; combined S is not counted as one primitive. Terms of L and L^-1
are expanded fully into those letters. Each phase/permutation applied to a
shear source has a recorded inverse restore. No initialization, COPY or
CLEAR instruction occurs.

| Variant | Paid rank-one C calls | Scalar ADDs | Primitive address applications | Extra bank swaps for inverse |
|---|---:|---:|---:|---:|
| Original U,V | 4 | 11 | 42 | 2 |
| Phase-repaired P,Q | 4 | 11 | 138 | 2 |

The ADD count is three for W(-I), two for each of the two L shears, and
four for the inverse-L shear. Coefficients include the rational denominator
15 of (2); they are not all dyadic. The instruction count and coefficients
are independent of f. In the abstract source engine, fixed rational register
mixing is permitted, but actual exact-grid or rounded native execution needs
its own precision and storage bill.

For the original variant the inverse-L monomial `R^k U^-1` is executed as
U followed by k copies of (V,U). Its length is 1+2k. The four terms and
their restores cost `2*(1+3+5+7)=32` address applications. The two L
shears cost eight more. The two boundary inverse kernels add two X_0,
giving 42. For the repaired variant the same monomial simplifies to
`S^-1 (UV)^k U S^-1`, of length 7+2k, so those terms/restores cost 80.
The two L shears cost 56, and the boundary shifts add two, giving 138.

This is the complete bill in the stated ideal linear game. It is not an
admitted recursion, binary caller, tape implementation or outer moment.
No paid-call saving over separately providing these two nonunitary maps is
claimed. Counting either as a Gaussian helper job would require a new
consumer argument.

## 5. Conditioning and the determinant boundary

The order-four R_f is unitary. Its four eigenvalues all occur for every
positive width, so I+2R_f has singular values 3,1,sqrt(5). Multiplication
by the unitary A_f and C_f does not change singular values. Consequently
both L_f and F_f have largest singular value 3 and smallest 1.
For the complete pair (1), the operator norm and inverse norm are both 3;
its Euclidean condition number is exactly 9, independently of f.

There is also a conservative uniform intermediate norm bound 32 relative
to the full two-bank input norm. W(-I)'s scalar steps have prefix norm at
most four and its completed map is a unitary signed swap. Each partially
completed L shear has norm at most `1+sum|coefficients|<=4`. Each partial
inverse-L shear has norm at most two because its coefficient magnitudes
sum to one. The three large shears therefore have prefix norms bounded by
4,8,32. Address letters and the boundary kernels are unitary. This bound
counts all intermediate term additions, not just completed large shears.
It is an exact ideal norm statement, not a recursive rounding theorem.

PR4991's completed dirty-return obstruction concerns `diag(F,I,...)`.
Here `det F * det F^-1=1`. The transformed partner explicitly supplies the
opposite volume profile, so that obstruction is respected. A local inverse
partner is therefore constructible; whether it is a useful independently
priced target in an actual Gaussian consumer remains unanswered. Since F
has unequal singular values, it is not a scalar multiple of a unitary
Gaussian, even after unitary input/output frame changes.

## 6. Independent intended-map checks

The verifier emits PROGRAM.json and runs a separate primitive interpreter.
Its target oracle builds dense C_f and monomial branch matrices directly
from coordinate entries, multiplies `C_f L_f C_f`, then obtains F_f^-1
by Gaussian elimination. That oracle does not use the polynomial inverse,
the shear decomposition, or the generated source-restoration schedule.

For both variants, all sixteen independent input columns at width one are
checked over Q(i). All 128 independent input columns at width two are
checked over F17 with i=4. Each column is checked against the actual target
and both inverse multiplication orders, giving 288 distinct input columns.
The modular computation is finite corroboration, not a claim that modular
equality proves rational equality at width two. A width-three dirty fixture
also round-trips. The written operator identities prove all widths.

Controls reject an inverse-polynomial sign change, omission of a literal
source-restoring U, relabelling the transformed partner as restored input,
and omission of the fourth paid call from the invoice. Checks remain active
under Python optimization. No finite checks are interpreted as a new κ,
Gaussian supplier admission or a completed five-in-fourteen construction.
