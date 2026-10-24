# Three character values already force six calls

Let C have character spectrum {1,i,-1}. For any finite complex role space,
let N be square-zero of rank three. Require the complete endpoint

    S(z) = I + (z-1)N,  z in {1,i,-1}.

Every input coordinate, including every helper, is arbitrary and dirty.
Allowed free gates are constant invertible complex role matrices. Each paid
gate applies C or C^-1 to one role. The constants are shared across characters.
The minimum number of paid calls is six.

This settles Open next question 1 in Richard Hoekstra's PR1318. Its normalization,
direction-span split and target-image loop method are inherited and credited.
The new observation is that the independent-direction exclusion needs only the
two active values i and -1. No fourth character is required.

## Normalize and split

At z=1 the product of constant gates must be identity. Absorb the constants into
conjugations to write a k-call word as

    F(z) = R_k(z)...R_1(z),
    R_j(z) = I + (z^epsilon_j-1)a_j b_j,
    b_j a_j=1, epsilon_j in {+1,-1}.

These rank-one idempotents need not be self-adjoint. This normalization is the
one in PR1318 and allows arbitrarily many restored dirty helpers. Rank(F-I)<=k
and det F(i)=i^(sum epsilon_j)=1. Thus k>=3 and k is even. Any word with fewer
than six calls must have exactly four, with all signs equal or two of each.

Put Y=im N and V=span(a_1,...,a_4). Then Y is contained in V, dim Y=3,
and N vanishes on Y. Hence dim V is three or four. If dim V=4, the restriction
N|V factors through V/Y, so rank(N|V)<=1.

## Independent directions: the new two-value exclusion

Choose a_j=e_j for j=1,...,4, extending to a basis of the entire role space.
Later factors change only their own rows. Row one of the endpoint forces

    (z^epsilon_1-1)b_1 = (z-1)N_row1.

If epsilon_1=-1, dividing by z-1 gives N_row1=-z^-1 b_1 at both z=i and -1.
The two scalars differ, so b_1=0, contradicting b_1 a_1=1. Thus epsilon_1=+1.
Apply the same argument to F^-1=S^-1=I-(z-1)N, with the directions in reverse
order. It forces epsilon_4=-1. In particular both all-equal sign patterns are
excluded. The only remaining patterns are ++-- and +-+-.

For ++-- put g=z-1 and d=b_2 a_1. The first two endpoint rows give

    N_row1=b_1,
    N_row2=b_2+g d b_1.

The values g(i) and g(-1) differ. Hence d b_1=0, so d=0 and N_row2=b_2.
In the first two columns these two rows have determinant
b_1 a_1 * b_2 a_2 - b_1 a_2 * b_2 a_1 = 1.
Thus rank(N|V)>=2, a contradiction.

For +-+- row two instead gives

    N_row2 = -d b_1 + z^-1(d b_1-b_2).

Again the two active values force b_2=d b_1. Idempotence gives
1=b_2 a_2=d b_1 a_2, so d is nonzero. Direct multiplication, now as an identity
for every nonzero z, yields

    R_2 R_1 = I+(z-1)M_1,
    M_1=(a_1-d a_2)b_1,  M_1^2=0, rank M_1=1.

The inverse word has the same alternating sign pattern. Its first pair
therefore gives R_3^-1 R_4^-1=I+(z-1)M_tilde. Inverting this square-zero
shear gives R_4 R_3=I+(z-1)M_2, where M_2=-M_tilde has rank one and square zero.
Consequently

    F(z)=I+(z-1)(M_1+M_2)+(z-1)^2 M_2 M_1.

At z=i and -1, divide F(z)-S(z) by z-1 and subtract. This gives M_2 M_1=0
and then N=M_1+M_2. Its rank is at most two, the final contradiction.
This is the new exclusion that closes the three-value question.

## Directions spanning Y: the inherited loop method at two active values

For completeness, the PR1318 target-image argument is written with its actual
sample points. Restrict all factors to Y, where their product is identity.
Every a_j lies in the span of the other three. Otherwise a covector annihilating
the other three detects a nonzero jth rank-one update after an invertible prefix,
contradicting identity on Y. The unique dependency therefore uses all four.
Write a_1=e_1,a_2=e_2,a_3=e_3 and a_4=(c_1,c_2,c_3), with all c_j nonzero.
Let f_j=b_j|Y. From R_3 R_2 R_1=R_4^-1, row one says

    (z^epsilon_1-1)f_1=(z^-epsilon_4-1)c_1 f_4.

Evaluation at i and -1 forces epsilon_4=-epsilon_1 and f_1=c_1 f_4.
Row two excludes epsilon_2=epsilon_1, since it would give
f_2+(z^epsilon_1-1)(f_2 a_1)f_1=(c_2/c_1)f_1 at two distinct scalars,
forcing both f_2 a_1=0 and f_2 a_1=c_2/c_1.
Thus epsilon_2=-epsilon_1 and f_2=-(c_2/c_1)f_1.
The determinant on Y forces epsilon_3=epsilon_1. The first pair is a shear;
substituting it in R_3 R_2 R_1=R_4^-1 and comparing the two active values gives
f_3=(c_3/c_1)f_1. Rescale the directions and use them as coordinates to obtain

    a_1=e_1, a_2=e_2, a_3=e_3, a_4=e_1-e_2+e_3,
    f_1=f_2=f_3=f_4=(1,1,1).

For each outside input column the remaining covector entries are arbitrary
complex beta_1,...,beta_4. Write B(z) for its outside-to-Y transfer and
H(z)=B(z)/(z-1), t=z^-1. Direct multiplication gives the following inherited
canonical coefficient formulas.

For +-+-:

    H_1=t beta_1+(1-t)beta_2-(1-t)beta_3-t beta_4,
    H_2=-beta_2+(1-t)beta_3+t beta_4,
    H_3=t(beta_3-beta_4).

Equality H(i)=H(-1) forces beta_1=beta_2 and beta_3=beta_4. Every constant
transfer column lies in span(e_1-e_2), which has dimension one.

For -+-+:

    H_1=-beta_1+(1-t)beta_2-(1-t)beta_3+beta_4,
    H_2=t beta_2+(1-t)beta_3-beta_4,
    H_3=-beta_3+beta_4.

Equality forces beta_2=beta_3. Every constant transfer column lies in
span(e_1,e_2-e_3), which has dimension two. Neither pattern can have rank three.
The argument applies to any finite number of outside and helper roles because
the same image bound holds separately for every outside column.

## Attainment and scope

For one source x and target y use C on x, then y+=x, then C^-1 on x,
then y-=x. The endpoint is x restored and y+=(C-I)x for arbitrary dirty x,y.
Apply this independently to three pairs: six calls attain the bound. Every
rank-three square-zero N has this canonical shear form after a constant basis
change. The six-call construction therefore covers every N in the theorem.

This is a scoped written proof. The checker corroborates its two-value
coefficient constraints, canonical image bounds and literal six-call endpoint
using exact Q(i) arithmetic. It is not exhaustive enumeration of arbitrary
complex projectors, a proof-assistant formalization, or a multiplication theorem.
Other phase functions, extra character-dependent gates, clean-input contracts,
physical tariffs and supplier admission are outside the theorem.
