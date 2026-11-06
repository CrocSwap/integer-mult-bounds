# A later cut defeats the dyadic Omega conjecture

Prepared for @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. This is a scoped written proof and an exact finite counterexample;
no independent human or proof-kernel review is claimed.

## 1. Model, statement and source boundary

Use the unchanged balanced reserved-depth word of Chafik Boukhalfa (#628),
as specified by Philippe Van Velzen (#2177, PROOF.md and PROOF3.md).
A height-h call has n=2^h free, noncommuting factors and L_h=4^h leaves.
Its protected source is x, unread target is y, and distinct scratch fields
are z_1,...,z_h. Siblings reuse deeper scratch. Each leaf is
`destination += sign * factor * source`, with different source/destination.
A positive call runs U,V,U',V'; a negative call runs V,U,V',U'. U uses
the lower half of the factors from x to z_1; V uses the upper half from
z_1 to y. Primes denote the exact inverse calls, including reversed leaf
order. A complete call restores scratch and adds its signed ordered
factor product to y on arbitrary input.

At each completed leaf destination allow a distinct formal additive error.
At a later cut, its channel to one register is a polynomial in the free
factors. Channel mass is the sum of absolute integer coefficients after
collecting equal words. Different error channels are kept separate. The
profile is the polynomial whose coefficient of u^j counts nonzero
channels of mass j. Its derivative at u=1 is the total channel mass.
Cuts throughout this proof count **completed leaves**, starting at zero.

The cited source conjecture C1 says its specified cut Omega_n attains the
maximum for every budget of independent errors. The source's finite census
and ywz65's #2735 fixed-cut theorem are credited, not contradicted within
their stated coverage. The latter proves at n=2^h, h>=2,

    O_h = (11*4^h - 11*3^h + 1)/6

at Omega_h, whose cut is (11*4^(h-1)-2)/3 and readout is z_h.
It explicitly leaves global maximality open.

**Theorem.** For every h>=2, in the positive word, read z_2 at cut

    c_h = 4^h - (4^(h-2)+2)/3.

Its total independent-error channel mass is exactly

    K_h = (47*4^h - 68*3^h + 48*2^h - 20)/24.             (1)

Consequently

    K_h - O_h = 4^h/8 - 3^h + 2^(h+1) - 1 > 0          (2)

for every h>=7. Thus C1 is false even restricted to dyadic sizes.
At h=7 (n=128), c_h=16042, z_2 is register 3 under x=0,y=1,z_j=j+1,
and K_h=26144 > 26028=O_h. All 16,384 possible leaf errors are an
admissible budget; only already completed leaves can contribute.

This proves neither a global optimum for K_h nor that n=128 is the
smallest counterexample to C1. It is the first height of this family
with a strict total-mass excess. The factor alphabet, chronology,
restoration and independent-error model are unchanged.

Section 6 further proves the uniform bound
`E_infinity(2^h) <= 2*4^h-3^h` and constructs a family implying
`E_infinity(2^h)/4^h -> 2`. This replaces the conjectured leading constant
11/6 for the global formal total mass, without asserting an exact
finite-size maximizer or changing the multiplication exponent.

## 2. Imported complete-call profiles and inverse pairing

From #2177, every completed-call exit channel has zero source entry and
zero or one signed monomial at each other register. From #2735, let G_j
count complete exit support size, and H_j its subprofile of channels with
a nonzero destination entry. Both are independent of call sign:

    G_0 = H_0 = u,
    H_j = (u+2) H_(j-1),
    G_j = 4 G_(j-1) + (u-1) H_(j-1).                    (3)

In particular

    G_j(1)=4^j,       H_j(1)=3^j,
    S_j:=G_j'(1)=2*4^j-3^j.

Define J_j to count only the nonzero **scratch projections** of these
exit channels. Removing the destination decreases the support by one
exactly for H_j. Precisely [u]H_j=2^j destination-only channels become
zero and must not be counted. Hence

    J_j = G_j + (u^(-1)-1) H_j - 2^j,
    J_j'(1) = D_j := 2*(4^j-3^j).                       (4)

There are no negative powers because H_j is divisible by u, and no
constant term remains. For j=0 this gives J_0=0. Equation (4) is a
projection identity, not erasure of a paid operation.

We also use #2735's inverse-phase partition, following #2177 Corollary I.
If a positive call C with L leaves is followed by q leaves of C^-1,
put p=L-q. At any readout, errors from the first p leaves of C give the
same channels as at its forward cut p. Each remaining C error gives the
same channel as the matching already executed inverse leaf. The latter
leaf has its own independent error as well. Thus the combined profile is

    forward-prefix profile at p + 2 * inverse-prefix profile at q.       (5)

The matching leaf fixes its own destination basis vector, which is why
injection *after* that leaf is compatible with the cancellation. The
factor two counts distinct errors; it is not a superposition of them.
When applying (5) below, every intervening call is explicitly accounted
for by its action on the relevant column or ignored external target.

## 3. Two target readouts

Put p_j=(4^j+2)/3 and q_j=4^j-p_j. At p_j in a positive height-j call,
follow V at every level and finish its final-factor leaf. Read the
call's target. Let Y_j be its error profile. Let Z_j be the profile at
q_j in the negative call, again read at its target. Base values are
Y_0=u and Z_0=0.

By #2177 Lemma P, the positive prefix target row has coefficient one on
the target and a positive monomial on its source and every scratch.
Their factor lengths are 2^j,2^(j-1),...,1, all distinct. The complementary
negative prefix is P_+(p_j) C^-1. Its target/source coefficient is zero;
its target and scratch coefficients are unchanged. (The complete inverse
subtracts precisely the full source-to-target product.)

The following two bridges have **no cancellation**. Read a completed
lower-half exit through the positive upper-half row: every nonzero
exit coordinate contributes one distinct word, giving G_(j-1). Read it
through the complementary negative upper-half target row: the source
coefficient is zero, leaving exactly its scratch projection J_(j-1).
The reading coefficients use upper-half letters with distinct lengths;
exit coefficients use only lower-half letters. Their concatenations
cannot coincide. The analogous reverse-direction scratch bridge uses
distinct lower-half reading words followed by upper-half exit words.
These are free-algebra arguments, without commuting factors.

At the positive readout, full U errors and current V errors therefore give

    Y_j = G_(j-1) + Y_(j-1).                             (6)

At the negative readout, the preceding V and current V' errors pair by
(5); the intervening completed U reads the outer source, which is zero
in V-error columns. The U errors see the scratch-only bridge. Thus

    Z_j = Y_(j-1) + 2 Z_(j-1) + J_(j-1).                (7)

These identities include j=1 and the zero-length q_0 prefix. On taking
derivatives and using a_0=1,b_0=0, they imply

    a_j:=Y_j'(1) = (4*4^j - 3*3^j + 5)/6,
    b_j:=Z_j'(1) = (8*4^j - 15*3^j + 12*2^j - 5)/6.     (8)

Substitution into a_j=a_(j-1)+S_(j-1) and
b_j=a_(j-1)+2b_(j-1)+D_(j-1) proves these formulas by induction.
They are not interpolations of finite data.

## 4. The new chronological cut

Write k=h-2. The cut c_h is in the top V' call, after

    4^(h-1)-p_k = 3*4^k + q_k

of that call's leaves. Thus its V,U,V' phases are complete, and its
final U' is at the q_k prefix. Read z_2, the destination of this U'.
Equivalently, the complementary positive prefix of the top V child
has p_k leaves: it lies in that child's U, at the Y_k target readout.

First analyze this height-(k+1) child in isolation. Its positive-prefix
profile at that register is Y_k. At its complementary negative cut:

- Its U and current U' errors give Y_k+2Z_k by (5). The intervening
  complete V' writes only the external y, never read by the later U'.
- Its V and V' error columns have zero source z_2 and unchanged deeper
  scratch after the intervening complete U, which reads an outer source
  that is zero in these columns. Their external y is ignored by U'.
  Each of the two completed V-type phases contributes J_k through
  the scratch-only reverse bridge. Both signs have the same exit profile.

The child's negative-prefix profile is therefore

    Y_k + 2Z_k + 2J_k.                                  (9)

Now place the child in the top word. The earlier top V and current V'
errors give, by (5) and (9),

    Y_k + 2(Y_k+2Z_k+2J_k).

The intervening top U' reads outer x, zero in every V-error column, so
this pairing is legitimate.

The top U and U' errors contribute two copies of G_(k+1). To see this,
the readout row of the top V' prefix at z_2 is also the row of its
complementary positive prefix: full V^-1 changes only the child's
target row, whereas z_2 is scratch. That row has one monomial on its
source and every scratch field, with distinct lengths 2^k,...,1,0,
and zero on the child's target. It therefore reads **all** of a top
U-type exit support with no cancellation, since the two top factor
alphabets are disjoint. For top U errors the intervening complete V
changes only the ignored outer y. Pairing the complete U with U'
then identifies its retained-footprint columns with the matching U'
exit columns. No scratch is refreshed or relabelled as independent input.

The exact new profile is consequently

    R_h = 2G_(k+1) + 3Y_k + 4Z_k + 4J_k.                (10)

Taking derivatives in (10) and using (3),(4),(8) gives

    R_h'(1) = 2S_(k+1) + 3a_k + 4b_k + 4D_k
            = (188*4^k - 153*3^k + 48*2^k - 5)/6,

which is (1). This accounts for every earlier error class, including
both inverse phases; it does not count errors at unexecuted leaves.

## 5. Strict excess and the finite witness

Let Delta_h be the right side of (2). Its values at h=2,...,7 are
0,-4,-18,-52,-90,116. For h>=7,

    Delta_(h+1) - 3 Delta_h = 4^h/8 - 2^(h+1) + 2 > 0.

Thus Delta_h>0 for every h>=7. Also K_h/O_h tends to 47/44; this is
a comparison of two fixed-cut masses, not a global-maximum formula.

At h=7 the complete profiles are:

| Mass per channel | New cut c_7, z_2 | Omega_7, z_7 |
| --- | ---: | ---: |
| 7 | 2 | 2 |
| 6 | 26 | 29 |
| 5 | 159 | 188 |
| 4 | 626 | 730 |
| 3 | 1822 | 1958 |
| 2 | 4250 | 4122 |
| 1 | 8709 | 7862 |
| Nonzero channels | 15594 | 14891 |
| Total mass | 26144 | 26028 |

The new profile does not dominate at every error budget. Its first
strict win is at budget 15479: mass 26029 versus the already saturated
Omega mass 26028. This prevents replacing C1 by a new unsupported
universal-profile assertion.

## 6. A uniform upper bound and the correct leading asymptotic

Write E_infinity(2^h) for the maximum total channel mass over all cuts,
registers and both orientations. The following upper bound is a direct
consequence of the credited prefix and exit lemmas, rather than an
assumption of C1:

    E_infinity(2^h) <= S_h = 2*4^h-3^h.                 (11)

For a scratch readout, the stronger bound D_h=2*(4^h-3^h) applies.

**Proof.** Fix a positive prefix P at p and its complementary negative
prefix Q at q=L_h-p, so Q=P C^-1 for the complete call C. Transport
*every* full positive-call exit error column through Q. The inverse
partition (5) says their channel multiset is exactly the union of
positive-prefix channels at p and negative-prefix channels at q, one
copy of each. Every entry of Q is zero or one signed monomial (#2177
Lemma L2, applied to the negative call). Thus the sum of their masses
at any row is at most the sum of all full exit support sizes, S_h.
This bounds each of the two nonnegative prefix sums separately and
covers both orientations. In a scratch row, Q has zero target column
because the target is never read; full exit columns have zero source.
Only scratch exit support contributes, giving D_h. This includes the
empty and complete prefixes. QED.

The 47/44 fixed-cut comparison is not the end of the asymptotic story.
For integers m>=1,k>=0, let h=k+m+1. Read z_(m+1) in the positive word
at cut

    c_(h,m) = 4^h - p_k.

In the complementary positive prefix of the top V child, this is m
successive U descents, followed by the positive height-k target readout
at p_k. The case m=1 is the preceding counterexample. Its exact mass is

    6 K_(h,m) = (48*4^m-4)*4^k
              +(-36*4^m-24*2^m+12*3^m+3)*3^k
              +24*2^(m+k)-5.                           (12)

Here is a derivation that retains every error class. The complete exit
channel count in scratch level ell of a height-r call is
`2*4^(ell-1)*3^(r-ell)`: two U target responses give the first level;
each deeper level receives four unchanged child scratch responses.
These are the endpoint counts credited to Adam Gall (#2067) and
restated in #2177. In a prefix row, let d be the sum of these counts
on its occupied scratch columns. All the rows in this construction
have a nonzero source coefficient and distinct reading words, so
cross-half bridges attain this weighted sum without cancellation.

Start with a=a_k, b_0=b_k and d_0=D_k from (4),(8). After the first U
wrapper, the old target is the new first scratch; after each further
U wrapper the readout is deeper scratch and ignores the new first
scratch. Therefore

    d_1 = 2*3^k+4D_k,
    d_j = 4d_(j-1)                    (2<=j<=m),
    b_j = a+2b_(j-1)+2d_(j-1)         (1<=j<=m).        (13)

The forward mass stays a. For b_j, U and its partial inverse contribute
`a+2b_(j-1)` by (5); the two completed V-type calls contribute
`2d_(j-1)` on shared scratch. Their sources are zero and their external
target is ignored. Reading coefficients lie in the lower-half alphabet
and have distinct lengths, while exit coefficients lie in the upper
half; hence these sums are exact, not triangle-inequality estimates.
The first d update adds the occupied new scratch identity; subsequent
ones only multiply older scratch weights by four.

At the final top V' wrapper, the earlier top U and U' each contribute
`3^(k+m)+d_m`: its source column and the occupied scratch columns.
The earlier V and current V' contribute `a+2b_m`. The same disjoint
alphabet and ignored-target arguments of section 4 apply. Thus

    K_(h,m) = a+2b_m+2*(3^(k+m)+d_m).                  (14)

Explicitly solving (13) gives

    d_m = 4^(m-1)*(2*3^k+4D_k),
    b_m = (2^m-1)a_k + 2^m b_k + (4^m-2^m)D_k
          +(4^m/2-2^m)3^k.

Substitution of (8) proves (12). No limiting argument was used to
establish these finite identities.

For each fixed m, divide (12) by 4^h and let k tend to infinity:

    lim K_(k+m+1,m)/4^(k+m+1) = 2 - 1/(6*4^m).

Since E_infinity is at least this explicit cut mass, its liminf is at
least this number for every m. Letting m grow makes the lower bound
approach two. Equation (11) bounds the limsup by two. We obtain

    lim_(h->infinity) E_infinity(2^h)/4^h = 2.          (15)

Equivalently the exact formal peak is asymptotic to 2n^2 along dyadic
sizes, whereas the old fixed Omega cut is asymptotic to (11/6)n^2.
Equation (15) gives the leading constant, not an exact finite-size
maximum, maximizing cut or all-budget profile. It does not assert
simultaneous attainment by physical rounding or native operators.

## 7. What the counterexample does and does not establish

The finite exact witness alone refutes C1 in its stated formal model.
The written argument above additionally supplies all-height profiles and
a family of strict counterexamples and the leading asymptotic of the global
formal total mass. #2735's fixed-cut C2 theorem and the
single-error and maximum-mass-channel bounds are unaffected. This is not
a counterexample to the selected multiplication theorem: C1 is a separate
conjecture, not an adopted selected assumption.

Channel mass bounds operator error for arbitrary contractive factors via
the triangle inequality. No simultaneous realization by the project's
native operators or actual rounding errors is asserted. Internal leaf
errors, inverse numerical implementations, aliasing, precision/tape costs,
and a full rounded caller remain outside this result. All five selected
framework assumptions remain. No new kappa, physical speedup, formal
kernel acceptance or exact finite-size global optimum is claimed.
