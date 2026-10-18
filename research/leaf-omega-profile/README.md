# The dyadic Omega cut has an exact channel profile

This proves the **fixed-cut** profile formulas conjectured in Philippe Van
Velzen's [PR2177, PROOF3, C2](https://github.com/CrocSwap/integer-mult-bounds/pull/2177).
For the balanced dirty word on n=2^h factors, h>=2, let c_j count the
nonzero independent completed-leaf channels of free-algebra mass j at its
specified Omega cut. Then

    c_h=2,  c_(h-1)=4h+1,
    c_(h-2)=4h^2-2h+6  (h>=3),
    sum_j j*c_j = (11*4^h-11*3^h+1)/6.

A polynomial recurrence below gives **every** c_j, not just these three
coefficients. This completes C2 at the named cut. It does **not** prove C1,
the separate conjecture that no other cut or register has a larger profile.
In particular the displayed total is not asserted to be the global E_infinity.

## Source and model

The unchanged source is `research/leaf-destination-transport-bound/` on
canonical main `b62dcc58a6beecfcae79627042bf9c48d0e71e6f`. Original PR2177
head: `2cbbb48d3b580e018312278c97b63817de963be7`, Philippe Van Velzen
(`philippeVV`), with substantial Claude assistance disclosed there.
`SOURCES.json` pins its two proofs, README, exact leaf generator and Omega
checker. The source's numerical profile conjecture and finite checks retain
their priority, including its already proved leading count c_h=2. The new
contribution is the structural recurrence proof of the complete fixed-cut
profile and the remaining closed formulas.

Use PR628's reserved-depth balanced dirty word. A height-h call uses 2^h
free noncommuting factors; a leaf is `y += s*f*x`. At an internal call,
let U be the positive call on the lower half of the factors, from x to the
depth scratch z, and V the positive call on the upper half, from z to y.
Positive order is U,V,U',V'; negative order is V,U,V',U', where primes mean
the exact reversed, sign-negated leaf word. All children reuse deeper scratch.
The source proves that a complete call adds its signed ordered product to
the destination and restores all scratch; its source is never written and
its destination is never read.

Inject a separate formal additive error at each completed leaf destination.
A channel is the noncommutative polynomial transporting one such error to
the chosen later register. Its mass is the sum of absolute coefficients.
Different error symbols remain distinct even if their channel monomials
coincide. All profiles below count only nonzero channels. These algebraic
masses bound operator errors under the source's contraction hypotheses;
no simultaneous physical rounding trajectory or norm attainment is claimed.

Write z_1,...,z_h for scratch levels and f_0,...,f_(2^h-1) for factors.
Omega_h is the source cut: in a positive top call, enter V', keep entering
V' down to a size-two negative call, finish its U leaf, then read z_h.
For h>=2 its prefix has

    3*4^(h-1) + (2*4^(h-1)-2)/3

leaves. Cut positions in the proof are counts of completed leaves; the
source's zero-based last-leaf index is one less.

## 1. Complete-call exit profiles

For a height-h call of either sign, define

    G_h(t) = sum over all leaves t^(exit support size),
    H_h(t) = the same sum restricted to nonzero exit destination.

The source's Lemma L1 says each exit coefficient is zero or a signed
monomial, and the source register is zero. Thus support size is also total
exit mass. The following profile recurrence is sign-independent:

    G_0=H_0=t,
    H_h=(2+t) H_(h-1),
    G_h=4 G_(h-1)+(t-1) H_(h-1).                 (1)

**Proof.** A V or V' injection has zero at that child's source z. Later
complete phases leave its exit column unchanged. Its parent destination is
nonzero exactly when its child destination is. There are two such phases.
For U and U', their child's destination is z. Exactly one is *y-keeping*:
U' in a positive call and U in a negative call. After that phase, the
parent's y becomes minus the upper-half product times the child's z.
It is nonzero exactly when the child's destination is nonzero, and adds
one new support position. The other U phase exports no y. Complete later
phases preserve deeper scratch. Hence four copies of G_(h-1) acquire one
extra support position on precisely H_(h-1), and the y-nonzero subprofile
is two unchanged copies plus one shifted copy of H_(h-1). This proves (1),
including that the profiles do not depend on the orientation. No exit
coefficient cancellation is discarded: these are the source's exact exit
columns, with the sole new y entry previously zero. QED.

It follows that H_h=t(t+2)^h and G_h(1)=4^h. Differentiating (1) at t=1
gives, with S_h=G_h'(1),

    S_0=1, S_h=4 S_(h-1)+3^(h-1),
    S_h=2*4^h-3^h.                             (2)

## 2. Two complementary prefix cuts

For h>=1 define two profiles, both read at z_h:

* A_h: a positive call, descend through V to size two and finish its V leaf.
  Its prefix length is p_h=(4^h+2)/3.
* B_h: a negative call, descend through V' to size two and finish its U leaf.
  Its prefix length is q_h=(2*4^h-2)/3.

Thus p_h+q_h=4^h. Their base profiles are A_1=B_1=t. At either base cut,
only the U leaf contributes to z_1; the V leaf writes the ignored y.

**Prefix row lemma.** Both cuts have the same ideal input row at z_h.
Its parent-y coefficient is zero, and it has one positive monomial on the
source x and on each scratch z_l. Index the source by l=0. The coefficient is

    f_(2^h-2) ... f_(2^h-2^(h-l)),  0<=l<=h,

where l=h gives the empty word. Its lengths are 2^h-1,2^(h-1)-1,...,0,
all distinct.

**Proof.** For h=1 the row is z_1+f_0*x in either orientation. A_h lies
after a completed U and inside V; B_h lies after completed V,U and inside
V'. The subcall row ignores its destination y, so the completed outer V
does not affect it. In both cases the completed U substitutes
z_1 -> z_1+(f_(2^(h-1)-1)...f_0)*x. Apply the induction hypothesis on the
upper-half subcall. Its source coefficient has length 2^(h-1)-1, and
multiplication by the lower-half product gives the displayed x coefficient.
The other scratch coefficients are inherited. The prefix lengths follow
from p_h=4^(h-1)+p_(h-1) and q_h=2*4^(h-1)+q_(h-1). QED.

**No-cancellation bridge.** Feed a complete lower-half U or U' exit column
into either upper-half prefix row from this lemma. The result has exactly
as many monomials as that exit column has support positions. Indeed each
nonzero exit entry is a signed monomial using only lower-half letters;
its readout coefficient uses only upper-half letters. Those upper-half
prefixes have different lengths, so their concatenations are distinct.
No assumption about distinctness of the lower-half monomials is needed.
Consequently the exact channel profile for that full phase is G_(h-1).

## 3. Inverse-phase partition and the full recurrence

Let a positive child have leaves L_1,...,L_N, and follow it by a prefix of
its inverse of length q=N-p. Fix a final readout. For an error injected
after L_i, subsequent exact cancellation gives two cases:

* i<=p: its transported channel is exactly the positive-prefix channel
  from after L_i to the cut after L_p.
* i>p: its transported channel equals the channel injected after the
  matching executed inverse leaf L_i^-1.

The latter identity uses that a leaf and its inverse leave their own
destination basis vector fixed: they read a different source. The inverse
prefix also has its own independent errors. Therefore the joint profile
is the early positive-prefix profile plus **twice** the inverse-prefix
profile. These are separate channels, not a superposition of their symbols.

At B_h the earlier full V and current partial V' have p=p_(h-1) and
q=q_(h-1). The intervening complete U reads the outer x, which is zero in
every V-error column, so it changes none of those columns. The inverse
partition therefore gives A_(h-1)+2 B_(h-1). The intervening U's own
errors give G_(h-1) by the no-cancellation bridge. Similarly, A_h has one
completed U and an A_(h-1) prefix inside V. We obtain, for h>=2,

    A_h=A_(h-1)+G_(h-1),
    B_h=G_(h-1)+A_(h-1)+2 B_(h-1).             (3)

Finally let O_h be the Omega_h profile, h>=2. Its V/current V' channels
again give A_(h-1)+2 B_(h-1), since the intervening U' also reads only the
outer x, zero in V-error columns. U' channels have profile G_(h-1).
Each U channel pairs with the matching leaf of the complete inverse U':
the intervening complete V writes only outer y, which the final prefix
row ignores, and U' does not read y. The same inverse cancellation makes
their readout channels identical. Thus the U channels give another copy
of G_(h-1), with independent error symbols. Therefore

    O_h=2 G_(h-1)+A_(h-1)+2 B_(h-1)
       =B_h+G_(h-1).                          (4)

Equations (1),(3),(4), with A_1=B_1=t, are an exact recurrence for the
entire fixed-cut profile. For example O_2=2t^2+9t and
O_3=2t^3+13t^2+36t. They are not inferred by fitting those examples.

## 4. The conjectured formulas

Let a_h=A_h'(1), b_h=B_h'(1). From (2),(3), including their base a_1=b_1=1,

    a_h=(4^(h+1)-3^(h+1)-1)/6,
    b_h=(2*4^(h+1)-9*3^h+1)/6.

Substitution verifies each expression in its recurrence; (4) then gives

    O_h'(1)=b_h+S_(h-1)=(11*4^h-11*3^h+1)/6.

For completeness, (1) gives the leading coefficients of G_k:
`[t^(k+1)]G_k=1`, `[t^k]G_k=2k+1`, and
`[t^(k-1)]G_k=2k^2+2` for k>=2. The first two also hold at k=1.
Equations (3) give, for k>=2, the two leading coefficients of A_k as
1,2k and of B_k as 1,2k+2. Inserting these in (4) yields precisely
2,4h+1,4h^2-2h+6. At h=2 use O_2 directly. All lower coefficients are
computed by the same proved polynomial recurrence.

The theorem is about the specified free-algebra channel mass at one cut.
It supplies a witness lower bound for the global mass census, and a precise
local independent-defect bound at that cut. It supplies no all-cut upper
bound, physical precision necessity, correlated-rounding theorem or kappa.

## Reproduction and falsification

Standard-library Python 3.12, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/leaf-omega-profile
python3 -I -B scripts/research_package.py --package research/leaf-omega-profile --check-only
```

The primary replay authenticates source bytes before extracting their exact
generator/Omega functions, checks complete literal A/B/Omega profiles and
the recurrence, and compares the full typed `RESULT.json`: 23 literal
profiles through h=8 (n=256), 16 exact prefix rows, and recurrence formulas
through h=100. A separately generated word and forward column interpreter
check 682 complete-call exit columns in both orientations and 646 cut
columns through h=4, without using the reverse row engine. Actual wrong
inverse order, preceding cut and wrong-register controls fail. A matched
U/U' pair has independent mass 2, while opposite shared injections cancel,
preventing the independent-error premise from being silently discarded.
Finite checks corroborate the written proof; they do not establish it by
census. Seven export test groups cover Git-free optimized read-only replay,
all five source corruptions, a source-execution sentinel, typed receipts,
fresh/existing outputs and unknown options. Both Python 3.12.14 and 3.14
passed those standalone export tests. Historical Git provenance is checked
by the registered metadata check; standalone exports verify live inputs.
Default replay writes nothing; `--output NEW.json` refuses an existing file.

## Decision, provenance and remaining obligations

The independent-verification picker selected `independent-moment`, nonce
`e6469585a99688f2231fdc0cfe6faac6`; the prescribed binding baseline passed.
This is a changed scope following the source's explicit C2 handoff.
[Claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2177#issuecomment-6199634961).
`TASK.json` records freshness and overlap limits. Selected/frozen files are
unchanged; the selected conditional kappa remains untouched.

**Decision: close C2 at the fixed cut; keep C1 open.** The next consumer is
the all-cut accumulation analysis, which may use this exact profile as a
candidate witness. Further larger Omega censuses are unnecessary for these
formulas. Proved here: the recurrence, all-height profile and its mass.
Inherited: exact dirty-word semantics and free-algebra contraction bound.
Unknown: universal maximizing cut, internal leaf errors, correlations from
actual rounding, aliasing, complete precision charges and supplier admission.
Unknown costs are not zero. No Lean, native, selected cold replay, hosted CI
or independent human review is claimed.

## Open next questions

Does Omega dominate every other cut's channel profile (C1)? Start with a
structural comparison between arbitrary prefixes and the complementary
profiles above; a larger finite census alone cannot close that obligation.
Any use as a physical precision lower bound additionally needs an admissible
operator/error realization, rather than free-algebra mass alone.

Credit Philippe Van Velzen/PR2177 for the exact word analysis, conjecture,
and censuses; woklerx, Charles Bethin/PR1416, Arham Tahir/PR1374 and PR2067,
Hanson Sun/PR1085, and Chafik Boukhalfa/PR628 for the retained lineage.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
