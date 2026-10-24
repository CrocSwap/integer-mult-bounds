# A ceiling for every prefix/suffix FULL/QUERY allocation

## Result and scope

Fix the bidirectional local profiles from PR5392:

```
paid P = {1:2193, 2:412, 3:510, 4:127, 5:40}
helper targets H = {4:28, 7:7, 8:47, 9:318}.
```

A full stage has 112 main ports and a fresh block of rank eight. A query stage
costs 112 H1 jobs and has no helper targets. Use the paired path controller
with any integer p >= 1, any split 0 <= a <= p-1, and b = p-1-a. Keep the
first a initial idle windows, all middle idle windows, and the last b terminal
idle windows. Each of the 2p+1 stages can independently be FULL or QUERY.
Specialize D_s=1 at each QUERY stage in both the main and idle products.

**Theorem.** Every invoice in this family has paid moment greater than target
moment for every `0.00302728825 <= kappa < 1`. Thus this entire family fails
the necessary strict moment test in that range. The result includes arbitrarily
many pairs, every split, and all stage masks. It is not restricted to a small
number of changes from the current mask.

This is an upper bound for the invoices defined by (1) and the strict moment
method. A different target list or idle law is outside the theorem. It is
not a lower bound for all native circuits or all multiplication algorithms.
It does not raise kappa. In particular, it does not prove the physical validity
of every masked word, a new compiler bound, or an unconditional multiplication
theorem. We grant the listed diagonal jobs to the entire family. A member that
fails a separate native or endpoint requirement cannot evade this ceiling.

The local profile is a premise supplied by PR5392. The source receipt is retained
byte for byte. The complete source construction and its five framework assumptions
are not re-proved here. PR5398 uses the same recursive profile and reports complete
conditional kappa .00302728823. Its distance from this universal family ceiling
is less than 2e-11. This comparison does not independently admit PR5398.

## 1. Complete interval invoice

Put t=1-kappa, f(r)=r^t for r>0, and f(0)=0. Define

    L(t) = sum_r P[r] f(r) - sum_r H[r] f(r).

Write x_s in {0,1} for the FULL indicator of stage s, and
`n=sum_{s=0}^{2p} x_s`. The local and query part of paid minus target is

    112(2p+1) + (L(t)-112)n.

There are 224 full-path main targets of rank 1+8n. For j=1,...,a, put

    h_j = sum_{s=0}^{2j-1} x_s,    e_j = x_(2j).

For j=a+1,...,p-1, put

    h_j = sum_{s=2j+1}^{2p} x_s,   e_j = x_(2j).

Each j contributes a retained whole idle of rank 8h_j, a main target of rank
`1+8(h_j+e_j)`, and a middle idle of rank eight if e_j=1. Each multiplicity is
224. Zero-rank idles are omitted. The complete difference is therefore

    E(t) = 112(2p+1) + (L(t)-112)n - 224 f(1+8n)
           + 224 sum_j [f(8h_j) + e_j f(8) - f(1+8(h_j+e_j))].        (1)

This includes every lost helper and every changed main and idle factor.
In particular, a FULL even stage restores its middle idle charge. The source
Laurent controller supplies the prefix/suffix products. Substitution of D_s=1
preserves any established source identity; it does not preserve a removed
stage's helper credit.

The verifier compares (1), as separate paid and target histograms, with the
retained literal Laurent controller on every mask for p=1,...,5 and every a.
It also compares the current p16/a7 invoice with the retained PR5392 receipt
and the separate main diagonal in `joint-helper-lattice/CONTROLLER.json`.
These checks bind the general formula to the source family. They are not a
native admission of all p or a proof from finite examples.

## 2. An infinite tail becomes finite

For 0<t<1, subadditivity and concavity give, for h>=0 and e in {0,1},

    f(8h) + e f(8) - f(1+8(h+e)) >= -1.                              (2)

For e=0, use `f(z+1)-f(z) <= f(1)=1`. For e=1, use
`f(z+8+1) <= f(z)+f(8)+f(1)`. There are p-1 summands. Equation (1) gives

    E(t) >= B_t(n) := 336 + (L(t)-112)n - 224(1+8n)^t.                (3)

At `kappa_0 = 0.00302728825`, exact outward rational arithmetic proves

    B_t(96) > 104.185162541469147567554569434096,
    B_t'(96) > 5.188985973480417120924401618389.

Here `B_t'(n)=L(t)-112-1792t(1+8n)^(t-1)`. Since t<1, this derivative
increases with n. Thus every n>=96 has E(t)>0, for every p and split.
The program uses a lower bound for L and an upper bound for the power in
both comparisons. No floating tolerance is used.

It remains to bound p when n<=95. Read the left side in the order
`x_0,(x_1,x_2),...,(x_(2a-1),x_(2a))`. Read the right side from the opposite
end in the same form. The central stage is `x_(2a+1)`. If a side pair has
both indicators zero, delete that pair and reduce p by one. The full-stage
count n and every later partial count stay fixed. The two removed queries
reduce the first term in (1) by 224. The removed summand is

    -224 [f(8h+1)-f(8h)] >= -224.

The deletion therefore cannot increase E. It produces another member of the
same invoice family after reindexing. Repeat until each remaining side pair
contains a FULL stage. Then `p-1=a+b <= n`, so p<=96. Consequently, positivity
for all p<=96 and n<=95, together with (3), proves positivity at kappa_0 for
the unbounded family. This reduction does not claim that deletion preserves
a particular caller's input set; it compares the optimistic invoices needed
for this ceiling.

## 3. Exact dynamic program for the finite part

For a side with q pairs and k FULL stages, let D_q(k) be the minimum sum of
its summands in (1), including their factor 224. The single end stage gives

    D_0(0)=D_0(1)=0.

Append the next odd/even indicators o,e in {0,1}. The recurrence is

    D_(q+1)(k+o+e) = min [D_q(k)
        +224 (f(8(k+o)) + e f(8) - f(1+8(k+o+e)))].                 (4)

The minimum is over all predecessors. This follows directly from the partial
count before the even stage. Induction on q proves that (4) covers every side
mask. States with k>=96 can be omitted because total FULL count cannot decrease.

For p=a+b+1, combine left count l, right count r, and central indicator c:

    112(2p+1) + (L-112)(l+r+c) + D_a(l) + D_b(r)
        -224 f(1+8(l+r+c)).                                       (5)

Discard only totals at least 96. Reflection exchanges a and b, so it suffices
to check a<=b. The program checks p=1,...,96 and 10,290,000 state combinations.
It uses integer bounds on the exact grid 2^192. Positive terms use lower
power bounds; negative terms use upper bounds. Taking a minimum of lower
bounds remains a lower bound, so interval overlap cannot create a false
positive certificate. The minimum certified lower bound is

    E(t) > 0.000000014914967918767741908079.

It occurs at p=16, a=7, with eight FULL stages on the left, nine on the right,
and a FULL central stage. The receipt retains the exact rational bound and
the minimum for each p. Independent exhaustive mask enumeration through p=5
agrees exactly with the integer dynamic-program minima.

The interval engine is the unchanged rational logarithm/exponential engine
from `higher-moment-strictification`. The dynamic program is new. Neither is
a solver result, and no SciPy or floating arithmetic is used for acceptance.

## 4. Extend the ceiling to all larger savings

It is not enough to reject one value of kappa. We now show that no larger
value can become favorable in this family.

First delete zero/zero side pairs as above, at the t under consideration.
If n=0, (1) gives E(t)=112, which is positive. Otherwise n>=1. Normalize (1)
by 8^t. In a reduced side pair, h>=1 if e=0, while h>=0 if e=1. Its normalized
summand is

    h^t + e - (h+e+1/8)^t.

For h>=1 its derivative in t is negative, because `z^t log z` strictly
increases for z>=1. For h=0, reduction forces e=1, and the derivative of
`1-(9/8)^t` is also negative. The normalized full-path target term has negative
derivative, since n+1/8>1. The query term is nonnegative and nonincreasing.

Finally the local term is strictly decreasing after the same normalization:

    L(t)/8^t = 2193(1/8)^t + 412(1/4)^t + 510(3/8)^t
             + 99(1/2)^t + 40(5/8)^t
             - 7(7/8)^t - 47 - 318(9/8)^t.

Its only positive derivative term is less than `7 log(8/7) < 1`. The negative
term from `2193(1/8)^t` alone has magnitude at least `2193 log(8)/8 > 274`
on 0<t<1. Thus the local derivative is negative. All terms in E(t)/8^t are
nonincreasing, and this local term is strict when n>=1.

Therefore a reduced invoice that is positive at t_0=1-kappa_0 remains
positive for every 0<t<=t_0. For an unreduced invoice at such a t, its reduced
invoice has no greater cost and is positive by the result just proved. This
establishes the theorem for the whole interval `kappa_0 <= kappa < 1`.

## 5. What must change to improve the bound

This theorem fixes the local paid/helper profiles, the rank-eight stage blocks,
the rank-one query price, and the prefix/suffix idle law. It does not cover a
new native circuit, a new productive/helper contract, another connection graph,
different idle incidence, coded recursive outputs, or another compiler method
that does not use this necessary moment test. It also does not certify the
exact supremum between .00302728823 and .00302728825.

The previous two-stage screen in PR5393 and the fixed 144-exchange invoice
ceiling in PR5397 have narrower domains. This proof adds unbounded p, every
split, every FULL/QUERY mask, and a whole saving interval. More decimal places
of the p16 root are not the contribution.

Credit: Cinna Davis for the paired path and query controller; Ali Romman for
the owned/transposed local profile; Cao Yifan for the native source; zxv for
the interval engine and invoice preflight; Chris R for the earlier controller
screen and independent admission work; Dugongue for the frames and related compiler work;
Jacob Alan Sussman and the retained native, compiler and analytic contributors.
New proof and verifier by Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. Independent human or formal-kernel review has not occurred.

