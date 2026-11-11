# Two paid exits and two causal splits

The source is exact [#7161](https://github.com/CrocSwap/integer-mult-bounds/pull/7161) at
`e3f8d39c43b07063dfc5b800f71c5d21015259e6`. Roles 988 and 991
both enter at chart 3 and return at rank-eight chart 245. Extend both
returns by a paid rank-one MOVE from 245 to 127. The enlarged group has
618 arbitrary helper coordinates on the common `(3,127)` boundary.
The signed caller is exact [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
at `07a76c5e2738882c0cb322278e56f6cae3c9885d`.

## Guarded directions

The literal cuts are 45,614 at chart 1091 with pivot 998, and 58,854
at chart 245 with pivot 988. A cut is the position before the event with
that zero-based index. The witness preserves the complete order of the
original events. The first prefix and guarded suffix use eight gathers
and seven injections. The second prefix is the difference of roles 988
and 991, and the second suffix is half their difference.
[WITNESS.json](WITNESS.json) gives every role, cut and coefficient.

In normalized coordinates let $C$ have the two prefix rows and let $D$
have the two suffix columns. The replay computes every coordinate,
including outside the group, all final owned roles and the actual
pre-COPY destination guard. It checks $CD=I_2$. The first injection
changes the values of 988 and 991 by the same coefficient 8 at the
second cut. The second gather therefore has zero response to the first
injection, for every value of the first new input. The second injection
occurs after all first gathers.

## Arbitrary-input construction

The literal scalar basis $B$ has pivot rows $C$ and maps the columns of
$D$ to the corresponding pivot units. The first set of row operations
reduces the first column and sets the first pivot row. Orthogonality
puts the transformed second row and column in the complement of that
pivot, where the remaining operations reduce them. Apply $B^{-1}$ at
chart 3 and $B$ after both charged exits reach chart 127.

At each cut, a live pivot value $v_i$ is transferred to the continuation
and its retiring field receives $x_i$, the gathered original pivot
input. A separate owned buffer holds $z_i-x_i$, where $z_i$ is the
arbitrary new continuation input. The guarded suffix adds
$d_i(z_i-x_i)$. The emitted program preserves the live value $v_i$ even
when it differs from $x_i$. The equality of the two late donor responses
ensures the second gathered value is still $x_2$. Applying the final
basis gives $x+e_{998}(z_1-x_1)+e_{988}(z_2-x_2)$ on the continuing
group. The retiring fields return $x_1,x_2$ at charts 1091 and 245.
All four added owned lifetimes clear explicitly.

## Complete invoice

The two exit extensions change two targets from rank eight to rank nine.
The first retirement replaces one rank-nine target by ranks four and
five. The second replaces one by ranks eight and one. Thus the literal
per-native change is `T1 +1, T4 +1, T5 +1, T8 −1, P1 +2`. The signed
caller charges the change in all 17 native occurrences. Rank surplus
stays 1,424. For $p=1-C$ in $(0,1)$, the change in the signed moment per
occurrence is $4^p+5^p-8^p-1>0$ by strict concavity. The exact compiler
and outer receipt separately bounds the realized conditional price.

The same five framework assumptions govern the conditional bound.
These cover all-column native maps, owned erasure, the compiler,
precision and tape bounds, and analytic recovery. The source and
finite application checks give a candidate for maintainer review.
