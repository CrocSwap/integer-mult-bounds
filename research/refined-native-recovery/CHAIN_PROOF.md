# Sharp recovery with mode-preserving parity-I native frames

This is a scoped interface theorem for the literal 112-by-8 integer matrix
in [#5444](https://github.com/CrocSwap/integer-mult-bounds/pull/5444),
`research/precision-state-frontier/FIXTURE.json`. It does not prove physical
reversibility, a selected supplier bound, or a new multiplication exponent.

## 1. Exact statement and source facts

Let R be componentwise nearest-integer rounding, with half ties away from
zero. Let M be the pinned integer matrix and define

    K(z) = z − M R(Mᵀz/52),       z ∈ Z^112.

The following finite identities are inherited from #5444 and rechecked on
the actual fixture by both implementations in this package:

    MᵀM = 56 I8,
    C := ker_F2(M mod 2) = row_F2(M mod 2),
    |C| = 16,     W_C(a,b) = a^8 + 14 a^4 b^4 + b^8.

In particular C is self-dual and contains zero. No claim is made that these
finite source identities prove a statement about other native matrices.

Fix any integer t ≥ 1. For 1 ≤ j < t, let U_j be fixed, known matrices with

    U_j ∈ GL_112(Z),       MᵀU_j = Mᵀ,       U_j ≡ I (mod 2).       (1)

They may fail to commute with K, its linear approximation, or one another.
Define the chain

    z_1 = K(2x),     z_(j+1) = K(U_j z_j),     x ∈ Z^112.          (2)

The factor 2 represents exactly one relative precision bit, introduced
before the first invocation. Every subsequent invocation is on the same
integer grid. There is no hidden refinement between later invocations.
Only the final output y=z_t and a retained tag are available for recovery.

**Theorem.** The exact maximum fiber of (2), for every frame sequence
satisfying (1), is

    A_t = W_C((13^t+1)/2, (13^t−1)/2)
        = (13^(8t) + 14·13^(4t) + 1)/16.                         (3)

The output y=0 attains this maximum. Thus A_t is the smallest fixed tag
alphabet for exact recovery in this declared interface. The minimum packed
binary tag length is ceil(log₂ A_t). These are state-count statements, not
physical storage or execution tariffs.

At t=2,

    A_2                         = 41,588,538,787,713,121,
    A_1 · 13^8                  = 41,608,923,949,414,081,
    A_1 · 13^8 − A_2            =     20,385,161,700,960.

Both counts still require 56 bits. Multiplying isolated maxima is a valid
upper bound, but it is not sharp here. The one-step and same-grid results
remain predecessor work; (3) determines their refined composition in (1).

## 2. A scalar interval lemma that retains the tie convention

For an integer s put

    Q(s) = {q ∈ Z : R((s+56q)/52) = q},
    F_s(v) = v − R((s+56v)/52).

The usual residual inequality gives

    ceil((-26−s)/4) ≤ q ≤ floor((26−s)/4).                     (4)

At the lower residual endpoint −26, the quotient must satisfy q ≥ 1;
at the upper residual endpoint +26, it must satisfy q ≤ −1. These are the
literal half-away rules, not an assumption that rounding commutes with
integer translation at a tie.

The interval in (4) has thirteen integers unless s≡2 mod4, when it has
fourteen. In the latter case its two extreme integers cannot both satisfy
the endpoint rules: the smaller would have to be positive and the larger
negative. Removing the disallowed extremes leaves a nonempty interval
with at most thirteen integers. Therefore Q(s) is consecutive, nonempty,
and |Q(s)|≤13 for every integer s.

If real numbers differ by 14/13, their rounded integers differ by one or
two. Indeed each rounding error has magnitude at most 1/2, so the integer
difference lies between 1/13 and 27/13. It follows that

    F_s(v+1) − F_s(v) ∈ {0,−1}.                              (5)

Also F_s(v)=−v/13−s/52+O(1), so F_s maps Z onto Z. Its level sets are
consecutive, and directly from the definitions

    F_s^(-1)({w}) = w + Q(s+56w).                            (6)

Every level set thus has at most thirteen elements. For any finite integer
interval I, its preimage is again a finite integer interval, of size at
most 13|I|. Iterating gives

    I_t(s) := {v : F_s composed t times sends v to 0}
    is a nonempty consecutive interval,   |I_t(s)| ≤ 13^t.   (7)

At s=0, denominator thirteen excludes half ties, and integer translation
in rounding is legitimate:

    F_0(v) = v − R(14v/13) = −R(v/13).

The preimage of [−h,h] is [−13h−6,13h+6]. Starting from {0} proves

    I_t(0) = [−(13^t−1)/2, (13^t−1)/2] ∩ Z.                (8)

Equations (4)–(8) prove the all-integer statement. The finite scalar
checks in this package corroborate them; the checks are not the proof.

## 3. Exact fiber parametrization for arbitrary outputs

Fix a proposed final output y and write s=Mᵀy. For a potential input,
let T_j be the cumulative quotient still to be subtracted after stage j.
Then T_t=0 and the mode projection at that stage is s+56T_j. This follows
from MᵀM=56I and the mode-preservation condition in (1), which also holds
for U_j^(-1).

Each scalar coordinate therefore satisfies

    T_j = F_s(T_(j−1)),      q_j = T_(j−1)−T_j.             (9)

The possible initial total quotients are exactly the vectors T=T_0 with

    T_k ∈ I_t(s_k) for k=1,...,8,
    y + MT ≡ 0 (mod 2).                                   (10)

Here is a direct proof of sufficiency, including chronology. From a vector
T satisfying (10), compute all T_j by (9) and the corresponding q_j.
Starting at z_t=y, reverse the chain by

    z_(j−1) = U_(j−1)^(-1)(z_j + Mq_j)   for j=t,...,2,
    2x = z_1 + Mq_1.                                      (11)

Every intermediate vector is integral. Since each inverse frame is I mod2,
the last expression has parity y+M∑q_j=y+MT, so x is integral. Mode
preservation proves inductively that the reconstructed pre-kernel vector
has projection s+56T_(j−1). Thus its actual rounded quotient is q_j;
every forward invocation returns the vector prescribed in (11).

Necessity follows by reversing an actual chain. Distinct T give distinct
inputs because

    2Mᵀx = s + 56T.                                      (12)

Consequently (10) is a bijection with the full fiber, not just a necessary
congruence or a volume relaxation. There are no extra quotient-history
tags in this parametrization.

## 4. Counting and sharpness

Let N=13^t, a=(N+1)/2 and b=(N−1)/2. Each scalar interval in (10) has at
most N elements, hence at most a of its preferred parity and b of the
other parity. The possible parity vectors in (10) are either absent or
one coset of C. After shifting the preferred parity vector, an upper bound
on the fiber is the largest value of

    sum_(c ∈ C+z) a^(8−weight(c)) b^weight(c).              (13)

For a≥b≥0 the zero coset maximizes (13). To see this without assuming a
coset classification, expand by binary characters:

    (13) = |C|/256 · sum_(u ∈ C-perp) (−1)^(u·z)
                          (a+b)^(8−weight(u))(a−b)^weight(u).

All unsigned summands are nonnegative, and zero z gives every sign +1.
Since C=C-perp, its checked weight enumerator proves the upper bound
W_C(a,b). This use of code-character duality is classical; it is not
claimed as new mathematics.

For y=0, (8) gives N elements in every coordinate. Because 13^t≡1 mod4,
the symmetric interval has exactly a even and b odd integers. The
congruence in (10) is T mod2∈C. Thus the count is exactly W_C(a,b), and
(11) reconstructs every attaining input for every allowed frame sequence.
This proves (3) and its constructive attainment.

## 5. Actual noncommuting source frames

Use zero-based source row indices. The literal source rows satisfy

    Mᵀv=0,   v=e1+e12−e0−e16,
    Mᵀw=0,   w=e0+e8−e2−e6.

Set U=I+2v e2ᵀ and V=I+2w e3ᵀ. The source coordinates satisfy v_2=w_3=0,
so U^(-1)=I−2v e2ᵀ and V^(-1)=I−2w e3ᵀ. Both satisfy all of (1).
They do not commute with each other:

    UV−VU = −4v e3ᵀ ≠ 0.

They are not merely changes commuting with the native inverse. For the
actual vector h=52e2, direct exact arithmetic gives

    K(Uh)−U K(h) = 8v ≠ 0.

The same witness shows noncommutation with the linear approximation
L=I−MMᵀ/52, because all quotients on this witness are exact integers.
The two-step instance uses U; longer checked chains alternate U and V.
This establishes that the theorem includes genuinely noncommuting frames.
It does not price their physical delivery at a selected caller.

## 6. Effective codec and scope

The implementation computes I_t(s) by taking the two extreme preimages
in (6), never by enumerating 13^t points. It enumerates the at most sixteen
parity blocks in (10), counts each Cartesian product, and uses mixed-radix
ranking/unranking. Equation (11) reconstructs the input and a literal
forward replay checks the result. The largest fiber determines the fixed
alphabet; a specific output may use fewer tags.

The executable supports depths 1 through 8 and the validated integer-shear
interface. This is an operational limit, while the written theorem covers
every finite t and every frame satisfying (1). Arbitrary-precision integer
arithmetic, fixed known source/frame descriptions and full output access
are assumed. Reversible arithmetic, quotient workspace, finite registers,
physical routing, cleanup and complete native/caller tariffs are not
provided. Input-dependent frames, later refinements, mode-changing frames,
and parity-changing frames are outside the theorem.

Theorem (3) resolves a restricted but source-sized family of #5444's mixed
refinement question. The companion PROOF.md determines the optimal two-stage count for the full
mode-preserving class, including parity-changing frames. Mode-changing
frames and nonuniform refinement remain open. All five selected framework
assumptions remain; no new κ.

Prepared for @CubeJerry with substantial OpenAI Codex assistance, including
separate derivation and implementation review. Credit zxv/#5444 for the
precision-state question, general one-step fiber theorem and changing-frame
history result; Ali Romman/#5323 for the same-grid source count; Brian/#5035
for the literal rounded kernel; and the retained native/caller lineage.
New proof and implementation are Apache-2.0. Independent human and formal
proof-kernel acceptance are not claimed.
