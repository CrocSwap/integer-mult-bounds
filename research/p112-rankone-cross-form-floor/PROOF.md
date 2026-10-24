# The rank-one two-call P112 COPY floor

## Statement and inherited interface

In the arbitrary directed two-call model of commdata2338's PR2395
(head 361de309e5fc05f83862f0b6c611210eda9837a1), suppose both cross forms
have binary rank one. Every exact root-code factorization has total union
COPY-rank price at least 128. Sixteen separate coordinate terms attain 128.
This includes all pairs whose two minimum support-restricted cross ranks
are zero. This is a written proof over complex coefficient vectors and
binary support-label spaces, not a machine-checked proof or physical bill.

We inherit PR2395's support census, Schur price and coefficient-count
lemmas, and PR2294's independent-call model (Sagar Thakrar, based on alephnan).
Write the actual reader coordinate-support hyperplanes as
U_i = r_i^perp and source hyperplanes as V_j = s_j^perp in F_2^9.
Every nonzero coefficient vector has full support-label span or one of these
hyperplanes; the latter occurs exactly for the coordinate line C e_i.
The 64 within-call ranks are 8, equivalently r_i dot s_j = 1 for every i,j.
All r_i and all s_j are distinct. These finite premises are independently
rechecked from the original P112 root/label table by the verifier.

Let beta01 = u v^T and beta10 = w t^T, with four nonzero binary vectors.
A term's price is the binary rank of the union pairing on its actual spans.
Exactness is sum a c^T = I_16 over C, with ordinary transpose.
Let n count non-pure terms and d count double terms (all four blocks nonzero).
The inherited lemmas give non-pure price >=8, double price >=15,
n+d>=16 and n+mu>=16, where mu is the smaller complex rank of the two
aggregate pure cross matrices R01,R10. Pure terms cost either zero or one.

## 1. Reduce the forms using actual support annihilators

A rank-one cross restriction vanishes precisely when one of its two
functionals vanishes. A nonzero functional vanishes on an actual support
only if it is the corresponding exceptional r_i (reader) or s_j (source).
Thus the minimum cross price is zero iff u is some r_i or v is some s_j;
likewise for w,t. If either minimum is one, PR2395's condition
c01+c10>=min(8,r01,r10)=1 already proves the floor.

Suppose both minima vanish. First consider the mixed orientation
u=r_i, t=s_l. Every double has price at least 16. To see this, restrict its
four nonzero spans to coordinate hyperplanes U_a,V_b,U_c,V_d.
Their diagonal pairings are nonsingular 8 by 8. Under the pairing of U_a
with V_b, the vector representing the functional x -> x dot u is
z=u+(u dot s_b)r_a in V_b. Consequently the scalar in the two rank-one
Schur transfers is

    t dot z = t dot u + (u dot s_b)(t dot r_a) = 1+1 = 0.

The product of the two transfers is zero, so the Schur complement is
invertible and the restricted double rank is 16. This argument imposes no
condition on v,w. The other mixed orientation (v=s_j,w=r_k) follows by
exchanging call0 and call1. This simultaneous row/column block permutation
preserves both the binary rank price and the coefficient identity I_16. Therefore 8n+8d>=128 settles mixed cases.

Any remaining case is either both-right exceptional
v=s_j, t=s_l with neither u nor w exceptional, or its transpose (both-left).
Indeed, if a left exceptional functional coexisted with the other form's
right exceptional functional it would already be a mixed case. It suffices
to treat both-right; transposition exchanges reader/source families and
transposes the exact coefficient identity without changing prices.

## 2. Couple the paid pure counts before considering equality

In the both-right case a zero-price pure 01 term must have source
coefficient in C e_j, and a zero-price pure 10 term source in C e_l.
Their aggregates each have complex rank at most one, regardless of their
number. Let p01,p10 count the positive-price pure terms, and p=p01+p10.
Then

    mu <= 1+min(p01,p10).

If n>=16 the floor is immediate. Otherwise put delta=16-n>=1. The inherited
counts imply d>=delta and p>=2(delta-1). Hence

    total >= 8n+7d+p
          >= 128-delta+7(d-delta)+2(delta-1).

For delta>=2 this is at least128. For delta=1 it is at least128 unless
n=15,d=1,p=0 and every non-pure term takes its minimum price: the unique
double costs15 and the fourteen others cost8. We now rule out exactly this
cost127 equality pattern. Counts alone cannot rule it out.

## 3. Price forces the source factors needed by the endpoint argument

**Double rigidity.** A double of price15 must have both source coefficient
blocks on coordinate lines, say c0 proportional to e_k and c1 proportional
to e_h, where k!=l and h!=j.

If c1 is not coordinate, its source span is full F_2^9. Restrict reader1
to an actual coordinate hyperplane U_b (if its span is full choose any U_b),
and reader0/source0 to coordinate hyperplanes with nonsingular pairing.
A left-kernel vector (x,y) of this 16-row restriction obeys, on source1,

    y + (x dot u)s_j = 0.

Because y is in U_b whereas s_j is not (r_b dot s_j=1), y=0 and
x dot u=0. The source0 equation and nonsingular diagonal pairing then give
x=0. Thus rank is at least16, a contradiction. The c0 argument exchanges
calls and uses t=s_l. Finally, h=j makes beta01 vanish on source1, giving
an invertible block-triangular diagonal restriction of rank16; similarly
k=l makes beta10 vanish. This proves all claims of rigidity.

**Mixed-reader rigidity.** A price8 non-double term with both reader blocks
nonzero and only source1 nonzero has coordinate source coefficient c1.
Otherwise its source span is full. The within-call reader1 span either is
full (already rank9), or is U_b. The nonzero reader0 block supplies the
additional row s_j: u cannot annihilate any actual reader support since
u is not exceptional. As s_j is outside U_b, the row rank is9. This
contradicts price8. The symmetric statement holds for source0.

## 4. The coefficient that cannot cancel

Assume the exceptional equality pattern of section2. There are exactly
8 diagonal-contributing terms in each call: the double plus seven others.
Every non-pure term contributes to at least one diagonal, and the incidence
count n+d=16 is exact. Each diagonal identity is therefore a sum of eight
rank-one matrices. Its eight reader columns and eight source columns are
dual bases over C.

Let the unique double have c0=lambda e_k and c1=nu e_h as above, with
lambda,nu nonzero. Duality implies its reader coordinate (a0)_k=1/lambda
and every other term contributing to diagonal0 has (a0)_k=0.
Consider coefficient (k,h) of the 01 cross block.

* The double contributes nu/lambda, which is nonzero.
* Each other term contributing to diagonal0 contributes zero by (a0)_k=0.
* A remaining non-pure term contributes to diagonal1 only. If its a0 is
  zero it contributes zero. Otherwise it is mixed-reader (c0=0), so price8
  forces c1 to a coordinate line by section3. Its coordinate cannot be h,
  since the diagonal1 source basis already contains the double's e_h.
  It therefore contributes zero at column h.
* All pure 01 terms are free and supported only at source column j!=h;
  pure10 terms do not contribute to this block.

The cross block must be zero by exactness, contradicting its nonzero (k,h)
coefficient. Cost127 is impossible. Together with section2 and the mixed
cases this proves the lower bound for all directed rank-(1,1) forms.
The sixteen coordinate diagonal terms prove sharpness.

## Scope, evidence, and open next questions

New work is the mixed-orientation transfer argument, paid-pure rank coupling,
and equality exclusion using source rigidity and dual bases. The support
classification and generic Schur/incidence bounds are inherited. Finite tests
check actual P112 inputs, a genuine price15 double, exact non-coordinate
endpoint decoders, and controls; they do not enumerate all complex decoders.
No physical chart realization, ownership, setup, precision, recursive cost,
multiplication theorem or selected kappa improvement is asserted.
The rank-(1,2) and higher residual classes require different pure-rank and
multi-double cancellation arguments; this proof makes no claim for them.

Prepared for JoyboyBrian with substantial OpenAI Codex assistance.
New work Apache-2.0; predecessor results retain their attribution.
