# Removing both separated QSELF sites within the existing paid budget

Prepared for **@CubeJerry**, with substantial OpenAI assistance. Apache-2.0.
**No new kappa. Exact formal caller identity; physical and rounded interfaces remain conditional.**

## 1. Exact claim, sources and novelty

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The source is DreamingOfClouds' [#6937](https://github.com/CrocSwap/integer-mult-bounds/pull/6937),
head `a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`,
`research/p104-two-chain-findings/data/caller_efree.json` (Git blob
`5a71ca9f80ced1aeb8a68e97516cab52eb72a52a`). The unchanged local native word
is from [#6936](https://github.com/CrocSwap/integer-mult-bounds/pull/6936),
head `03626137d0bd57f09b0bf9597376183ce6fa9683`.

The E-free root and caller are entirely DreamingOfClouds' work. Its README
reports a QUERY-only gadget with a projected cost loss, while saying the
whole QUERY-only caller was not built. The preceding public package
`CubeJerry/integer-mult-bounds@4e2fd1b6abed49c202a057fd5c73ead0a460f976`,
`research/p104-qself-owned-lowering`, supplies the reproducible formal caller
certificate and an owned QSELF expansion with an explicitly uninstalled new
token registry. Its single-QSELF determinant obstruction expressly leaves
paired source synthesis open. This package supplies a different result: a
whole actual separated interval replacement with the same paid profile and
only existing caller operations. It does not rerun or extend that obstruction.

**Theorem.** Let Q,D_1,...,D_18 be commuting operators on any complex vector
space V, with Q^4=I. Interpret the exact pinned caller with its stated scalar,
QUERY, LAMBDA, IDLE_ONE and joint-contact semantics. Replace zero-based events
457 through 575 inclusive by the 223 events emitted by `replacement.py`.
The resulting 3,095-event caller has exactly the same operator on all 76
independent inputs. It has no QSELF event. The replaced interval uses exactly
three QUERY(-1) events, the same number of rank-one jobs as its former two
QSELF(-1) events and one QUERY(-1). It uses the same public roles and no new
owned role, arbitrary helper, productive credit, or operation type.

This theorem includes all input columns and absolute coefficients in the
commutative operator model. It does not assert success on the same finite
signed or rounded inputs, install a physical compiler/service binding, or
prove the retained scalar and routing rates. Those are separate obligations.

## 2. A three-query identity on four arbitrary fields

Work first in R=Q(i)[q]/(q^4-1). Put x=q^-1 and t=x^2=q^2, so t^2=1 and
x^-1=t*x. The source's actual phase units are

    lambda_s = ((1+s*i)+(1-s*i)*q^2)/2,   s in {+1,-1}.

They satisfy lambda_+*lambda_-=1 and lambda_+^2=lambda_-^2=t. They are
**units, not the projection (1+q^2)/2**. No inverse of a projection or of any
D variable is used anywhere below.

For four arbitrary independent fields (a,b,c,d), perform the invertible
q-even preprocessing

    (w1,w2,w3,w4) = (c, a+d, b+t*c, t*d).

Then perform exactly three generalized query shears in this order:

    w1 <- w1 + x*w2;
    w2 <- w2 + x*(w3-t*w1);
    w3 <- w3 + x*(w4-t*w2).

Each query is one literal QUERY(-1). Its indicated source is made by an even
ADD into the other existing public field, then restored after the query.
The query destination differs from that source, so restoring the source
does not undo the update. Multiplication by t uses two source LAMBDA(+1)
events. A temporary t scaling is undone by two LAMBDA(-1) events. These
scans and field transformations are charged; they are not a free oracle.

After these three steps direct substitution gives

    w1 = c+x*(a+d),
    w2 = x*b,
    w3 = t*c+t*x*d,
    w4 = t*d.

The even postprocessing

    (w1-t*w3, w2, t*w3, t*w4)

therefore returns exactly

    (x*a, x*b, c+x*d, d).

The gadget is a genuine four-input map. In particular d is arbitrary and
restored, and c is arbitrary and receives the prescribed shear. No field is
assumed zero. The emitted word uses 38 existing events: three QUERYs,
26 LAMBDAs, seven ADDs and two SWAPs. The inverse even basis exists over the
entire quotient ring, including q=+/-i. The exact local matrix certificate
checks every coefficient, and a separate unit-basis round trip detects loss
of either q^2 sector.

## 3. Why that gadget replaces the actual separated sites

Use column-vector convention: later operations multiply on the left. Let
S_0 multiply role0 by x, S_19 multiply role19 by x, and let
U=I+x*e0*e1^T be the actual QUERY at event495. Partition the intervening
even source events exactly as follows:

| Block | Zero-based source events | Roles | Content |
| --- | --- | --- | --- |
| E1 | 458..494 | 0..18 | Invertible ADD/SCALE/LAMBDA prefix |
| E2 | 496..544 | 0..18 | Invertible ADD/SCALE/SWAP/LAMBDA suffix |
| B | 545..574 | 19..37 | Other chain prefix, including IDLE_ONE(28,[9]) |

The original complete interval is the matrix S_19 B E2 U E1 S_0.
Every operation in B has support disjoint from every first-chain operation.
Thus B may move to the right of all first-chain factors, and S_19 may move
leftward across first-chain factors. We obtain

    E2 E1 (E1^-1 U E1) S_0 S_19 B.

**B is never inverted.** Its IDLE_ONE multiplies by the unrestricted formal
D9 and may be noninvertible. It moves only across disjoint role supports.
E1 alone is conjugated, and its scalar factors are units.

Let

    s = e1+...+e18,
    w = sum_{k=1}^{18} (-1)^k e_k^T,
    lambda = lambda_+.

Then w*s=0 and w*e0=w*e19=0. Reading the actual E1 events gives

    E1^-1 e0 = lambda*(-e0+s),   e1^T E1 = w.

For example, E1 sends role0 to -lambda_- times its old value, sends each
rolek for 2<=k<=18 to old rolek+old role0, and sends role1 to w applied to
the old roles. Solving E1 v=e0 gives the displayed inverse column; this does
not infer a source relation from a finite input probe. Hence

    E1^-1 U E1 = I + x*lambda*(s-e0)*w.

Writing S=S_0 S_19, the three paid source operations reduce to

    (E1^-1 U E1) S
      = S (I+x*lambda*s*w) (I-lambda*e0*w).

All cross terms vanish because w kills s,e0,e19. This is the source-specific
correction missed by treating the two QSELF sites as an adjacent pair.
The original QUERY contributes the nontrivial independent shear along s.

Now change the first-chain coordinates using only existing even events.
Subtract role1 from each role2..18. Into role2 add (-1)^k times rolek for
k=3..18, then apply LAMBDA(+1) to role2. The new coordinates include

    c = old role1,
    d = lambda*w(old roles).

The other residual roles retain all remaining independent input information.
The inverse first applies LAMBDA(-1) to role2, undoes its signed sum, and
adds the new role1 into roles2..18. Increasing c in these coordinates
increases every original role1..18 by the same amount: its direction is s.

Call this invertible coordinate map P^-1. Its two emitted directions each
cost 34 events. In coordinates (a,b,c,d)=(role0,role19,role1,role2), the
factor I-lambda*e0*w is simply ADD(0,2,-1). The factor
S(I+x*lambda*s*w) is exactly the four-field map in section2.

The complete replacement is therefore, chronologically:

    B; P^-1; ADD(0,2,-1); THREE_QUERIES; P; E1; E2.

Its event count is 30+34+1+38+34+37+49=223. All source events before457 and
after575 remain byte-for-byte equal as parsed records. This construction
replaces the whole separated interval, not merely a same-cut subexpression.

## 4. Formal certificates and failure detection

`interval_certificate.py` is a separate exact sparse-matrix implementation.
It starts with 38 independent interval input generators. Coefficients are
Gaussian rationals, q exponents are reduced only modulo4, and D monomials
are sorted tuples with repetitions retained. The complete two interval
matrices agree in all 180 nonzero endpoint entries. The interval uses D9,
but never specializes it or assumes its inverse or idempotence.

The full generated caller is also replayed by the unchanged public forward
certificate over Q(i)[q,D1,...,D18]/(q^4-1). All 18 D variables remain
formal and all 76 input generators remain independent. It returns the same
76 diagonal monomials as the source. A different unchanged backward-covector
checker uses integer dyadics at q=1,i,-1,-i, with D variables still formal.
Evaluation at all four distinct fourth roots is injective coefficientwise
on this quotient, so these checks are faithful operator certificates, not
sampled D or sampled field-value experiments.

The newly supplied interval arithmetic imports none of those predecessor
arithmetic routines. The reused forward and backward engines are credited;
replaying either alone would be regression evidence, not a new independent
implementation. The proof above derives the identity without their code.

Controls change a query orientation, delete one query, omit the source
conjugation correction, break a t scaling/restoration, repeat D9, contaminate
another independent input, replace lambda with a projection, and remove the
q^4 relation by working modulo q^8-1. Each changes the exact interval matrix.
These controls do not prove minimality of three queries or a general lower
bound for another word.

Induction over the exact source semantics proves that each matrix entry is
the indicated formal coefficient. A homomorphism into the commuting operator
algebra generated by Q,D maps the identity to every V and every collection
of input fields. No dimension bound, sampled numerical values, or rounded
input assumptions enter that exact theorem.

## 5. Complete recursive profile and positive ordinary invoice

Each A event occurs at 96 actual ports. The replacement deletes 192 QSELF
instances, adds 192 QUERY instances, and leaves the former QUERY instances
in the total paid count. Across the full caller, the source has 224 QUERYs
plus 192 QSELFs; the new caller has 416 QUERYs and zero QSELFs. All queries
here have exponent -1, so both complete frame conversions and the return
translation have the same inherited charge per job.

The 18 local native words, their 400 actual main fields per call, and their
1,061 fresh arbitrary helper fields per call are unchanged. The caller still
has 3,952 actual A/B main inputs and 19,098 fresh local helpers. The root
targets are unchanged, with no empty-mask E input restored or credited.
For every rank r, T_new(r)=T_source(r) and P_new(r)=P_source(r). Thus every
signed target/paid moment agrees identically as a function of kappa. The
complete totals remain T=23,050, P=117,846; surplus=1,520; paid rank mass=317,324.

No public role is newly allocated. The temporary linear sources in section2
use already live roles and are restored by ordinary invertible operations.
The existing QUERY contract still needs its copied owned bank and completed
query lifecycle. Three serial query jobs can reuse its fixed inventory; there
are 416 outer query lifetimes overall, the same total as QUERY plus owned
QSELF lifetimes in the baseline. No uninitialized or arbitrary helper is
treated as zero, and no productive target is claimed for query scratch.
All private native workspace, historical backing and parked ancestors remain
charged by the inherited QUERY/LAMBDA/scalar interfaces.

Under the **inherited scalar/routing convention**, the extra 104 A events
cost 104*32*38*96=12,140,544 units. The extra 28 A LAMBDAs receive the
separate conservative charge 28*1,000*96=2,688,000. The eliminated owned
QSELF-specific macro surcharge is 192*128=24,576. Every other term remains.

| Complete conditional invoice | QSELF baseline | QUERY-only caller |
| --- | ---: | ---: |
| Reviewed raw ordinary upper | 796,934,944 | 809,050,912 |
| Separate LAMBDA reading | 11,792,000 | 14,480,000 |
| Per-call 1125 conversion reading | 2,734,992 | 2,734,992 |
| All displayed readings included | 811,461,936 | 826,265,904 |
| Margin below inherited 10^9 cap | 188,538,064 | 173,734,096 |

`complete_invoice.py` reconstructs the unchanged local word and both caller
profiles and checks each changed term. These are conditional scalar/pass
counts, not a new proof of the complete bit-tape tariff. Increased arithmetic
length, temporary coefficients and cross-chain intermediate values require
fresh rounding, signed-width, common-grid and source-placement bounds. There
is no claimed improvement to the accepted kappa or unconditional theorem.

## 6. Remaining obligations and credit

The substitution removes the need for a new abstract QSELF operation in this
exact proposed caller. It does not prove arbitrary-Q synthesis: the gadget
and actual source phase algebra use Q^4=I. It neither changes the selected
certificate nor discharges all native_all_columns, owned_erasure, compiler,
precision_tape or analytic_recovery premises.

Before physical supplier use, regenerate the actual compiler records and
bind the new source occurrences to the existing QUERY, LAMBDA and scalar
providers; prove matching formats and all intermediate signed admission;
reprice complete bit-tape work and historical backing; and propagate errors
through the changed order and additional even operations. Existing opcode
semantics alone do not install an exact source-specific service registry.

DreamingOfClouds receives credit for #6936/#6937, the E-free construction and
prior QUERY-only feasibility suggestion. The public owned-lowering package
receives credit for the prior formal engines, exact semantics/source pins and
full invoice baseline. Its underlying native, caller, compiler and physical
predecessors retain their attribution. The three-query four-input identity,
its exact separated-source reduction, emitted whole caller and new interval
certificate were prepared for @CubeJerry with substantial OpenAI assistance.

## Open next questions

1. Can the regenerated caller satisfy the actual common-format and rounded
   QUERY/LAMBDA contracts at this interval? Start with its 223 new intermediate
   coefficient rows and the actual source compiler; exact operator equality
   does not establish headroom or an error budget.
2. Can the 28 added LAMBDA occurrences be reduced without increasing the paid
   profile or changing arbitrary-input restoration? Preserve this complete
   verified source as the baseline; an isolated two-register identity is
   insufficient. This optimization is outside the present bounded task.
3. Can the resulting existing-op caller be admitted with all native/owned
   dependencies and a complete bit-tape certificate? The inherited tariff,
   literal source registry and universal proof assumptions remain blockers.
