# Independent review of the signed native exponential table

Reviewed exp_table.py read-only. This is a mathematical and finite-word review,
not Lean verification or independent human peer review. Apache-2.0;
Dugongue with substantial OpenAI Codex assistance.

## Verdict and one scope correction

The approximation scheme is sufficient for the stated strict 2^-p error under
its declared dyadic-input/range contracts. The construction uses O(log n)-bit
words, but its table contains J+1=Theta(n^(1/4)log n) words along the growing
parameter sequence. It does NOT have O(log n) total memory words. Arithmetic
scratch outside the stored table is O(1) words. Each query executes at most
833 Taylor iterations, hence constant work for the fixed bounded c,C family.

## Parameters

Let ell=bitlength(n+2)>=2, 1<=c,C<=8, k=c+4C<=40,

    p=c*ell, hbits=floor(ell/4), h=2^-hbits,
    J=C*ell*2^hbits,
    d=8(k+64)+1, an odd integer at most 833,
    jbits=bitlength(J+1), dbits=bitlength(d),
    P=k*ell+jbits+dbits+32, S=2^P.

An input argument is exactly the signed dyadic integer argument/2^fraction_bits,
with 0<=fraction_bits<=P and absolute value at most C*ell. These are actual
input-domain restrictions, not consequences of arbitrary list entries fitting.

## Taylor truncation holds for every n, without runtime factorials

The alternating exp(-x) remainder for 0<=x<=h after odd degree d is between
zero and h^(d+1)/(d+1)!. We prove this is at most 1/S.

For ell>=8, hbits>=ell/8 and therefore

    hbits*(d+1) >= (k+64)*ell.

A convenient bound is jbits<=2ell+4: C*ell<=8ell<=2^(ell+2) for ell>=2,
and multiplying by 2^hbits followed by the harmless +1 gives that inequality.
Also dbits<=10. Hence

    P <= (k+2)*ell+46 < (k+64)*ell.

The h power alone already gives a tail at most 2^-P; ignoring the factorial
only weakens the estimate.

For 2<=ell<=7, J<=112, so jbits<=7 and P<=7k+49. Put m=d+1, an even integer.
The last m/2 factors of m! are at least 2, so

    m! >= 2^(m/2) = 2^(4k+257) >= 2^(7k+49) >= 2^P,

because k<=40. Again the omitted h factor only strengthens this bound.
Thus the check() factorial inequality has an all-input proof; no factorial
construction or unbounded factorial integer is needed by the native algorithm.

## Floor recurrence and downward seed

For x/S=theta in [0,h], let u_i=theta^i/i!, t_0=S and

    t_i=floor(t_(i-1)*x/(S*i)).

Set epsilon_i=u_i-t_i/S>=0. Then

    epsilon_i <= (theta/i)epsilon_(i-1)+1/S.

In the alternating sum, pair consecutive errors instead of adding their
absolute values independently. For every odd i>=3,

    epsilon_i-epsilon_(i-1) <= 1/S,

and for every even i,

    epsilon_(i-1)-epsilon_i >= -1/S.

Also epsilon_1<=1/S. Therefore the floored degree-d polynomial differs from
the exact degree-d alternating polynomial by between -(d-1)/(2S) and
(d+1)/(2S). Adding the <=1/S Taylor remainder yields a conservative absolute
polynomial error <=(d+3)/(2S).

Subtracting d+2 integer grid units as done in q makes q/S <= exp(-h), while

    0 <= exp(-h)-q/S <= (2d+4)/S.                         (1)

The clamp at zero is inactive: exp(-h)>=exp(-1)>1/3, whereas S exceeds
2^32*d by the precision definition, so the right side of (1) is far below
1/12. In particular q>S/4>0. Terms are nonincreasing for theta<=1, so every
integer alternating partial sum used by poly lies between 0 and S; its actual
SUB operations need no negative intermediate.

## Row propagation and residual query

Let R_0=S and R_j=floor(R_(j-1)*q/S). The downward seed and downward products
give

    0 <= exp(-jh)-R_j/S <= j(2d+5)/S.                    (2)

This follows inductively by one multiplication discrepancy plus its <1/S
rounding. For a query magnitude a, write a=jh+t, 0<=t<h; at the exact upper
endpoint a=C*ell, j=J and t=0. Thus the row index is always in [0,J].

The residual poly has error <=(d+3)/(2S), and both row/poly values are in [0,S].
Multiplying and flooring once more shows that its returned v obeys

    |v/S-exp(-a)| <= (J+1)(2d+8)/S
                    < 2^(jbits+dbits+2)/S
                    <= E=2^(jbits+dbits+4)/S.            (3)

The strict middle inequality uses d>=553, so 2d+8<4d. The +4 envelope is
slightly stronger than the proposed +5 envelope and leaves an additional
bit of slack for the positive-argument reciprocal below.

## Positive-argument reciprocal and final rounding

Let u=exp(-a), where 0<=a<=C*ell. Since exp(1)<4,

    u > 2^(-2C*ell).

Substituting P in (3) gives E=2^(-p-4C*ell-28), so E<u/2. Consequently v>0,
v/S>=u/2, and

    |1/(v/S)-1/u| <= 2E/u^2 < 2^(4C*ell+1) E.

The literal floor(S^2/v) adds less than 1/S to the normalized reciprocal.
Thus the total pre-final-rounding error is strictly less than

    2^(-p-27)+1/S < 2^(-p-26).

For nonpositive arguments no reciprocal is taken and (3) is smaller still.
Nearest rounding from P fractional bits to p adds at most 2^(-p-1), proving
strict final error below 2^-p. This covers zero and both signs. It does not
justify a relative error contract; the established bound is absolute.

## Bounded words, setup and query complexity

All poly/row multiplicands are between 0 and S, so their products are <=S^2.
A denominator S*i is at most S*d. The reciprocal numerator is exactly S^2,
which needs 2P+1 bits. The positive reciprocal value is at most
S*2^(2C*ell+2), well within the chosen 2P+32-bit word because P>=4C*ell.
The argument shift is at most C*ell*S, the exact endpoint row J exists, and
P>hbits ensures all shifts are nonnegative. Final-rounding addition has the
same sufficient width margin. A common global machine word width must cover
this subroutine's 2P+32 and all other caller subroutines/addresses.

There are J+1 stored rows and constant-size row steps. Computing the initial
poly and a query residual poly each takes d<=833 iterations. Since
2^hbits<=2^(1/4)(n+2)^(1/4), setup is O((n+2)^(1/4)log(n+2)), each query is
O(1), and total stored memory is O((n+2)^(1/4)log(n+2)) words. Word width is
O(log(n+2)). No Decimal or factorial is called by construction/query; both
occur only in the independent finite check().

No mathematical implementation correction was required. Documentation should
retain the stored-table memory bound and the precise dyadic/range contract.
