# Paired BIT schedule bound at the fixed target

Keep the exact 38-role clean endpoint in the selected #7001 paired BIT
caller, its 18 independent body variables, the retained native invoice
per LOCAL, and the rank-one QUERY and body-only distinct-stage IDLE
tariffs. Allow arbitrary placement and invertible constant bases and
additional auxiliary roles initialized and restored to zero. The native
count and its stage multiplicities may vary. The signed paid moment is
strictly negative at κ = 0.0040075385047236 throughout this family.

## Rank conditions

Normalize each factor at q=1 and all body variables equal to 1, and
conjugate its derivative by the accumulated constant prefix. The
target stage derivatives E_s are the pinned diagonal projections on
public space A. A LOCAL contributes a rank-two stage projector P
and a square-zero rank-one head defect N with PN=NP=N. QUERY gives
a square-zero rank-one head defect. An IDLE serving s gives a rank-one
stage projector.

Let n be the number of LOCALs and q_count the number of QUERYs.
The complete head derivative factors as UV with n+q_count rank-one
terms and restricts to the identity on A. V embeds A into the
fixed space of VU, so rank(I−VU)≤n+q_count−38. Each diagonal
pairing of VU is zero by square-zero, forcing q_count≥39−n.

A stage is saturated when its serving ranks sum to rank(E_s).
In a saturated stage, the images of all its projectors form a
direct sum equal to im(E_s), by the full ambient rank and the exact
clean restriction. They annihilate one another, since E_s is the
identity on that sum. Each LOCAL head defect stays inside the
column and row support of E_s. The head terms of any a same-stage
LOCALs give a principal identity block of size a in I−VU.

The 81 opposite-arm pairs have the same two common root coordinates,
0 and 19, in their diagonal E_s supports. For opposite stages with a
and b LOCALs, the principal block of I−VU has diagonal blocks I_a
and I_b. Both cross blocks factor through the two root coordinates,
so the Schur complement has rank at least b−2. If a and b denote
the actual largest multiplicities in the two arms, then at full
saturation

```text
q_count ≥ max(0, 39−n, 38−n+max(a,b,a+b−2)).
```

## The price of IDLE masks

Write f(r)=r^(1−κ). For fixed per-stage demands d_s, nested masks
{ s : d_s ≥ j } minimize the moment. For every k their k longest
lengths sum to ∑ min(k,d_s), an upper bound for any k masks.
Concavity of f gives the cost lower bound.

Each saturated IDLE projector crossing arms has its image and row on
the two root coordinates. At most two cross incidences can serve a
stage. Splitting a mask of x left stages and y right stages costs
111[f(7x)+f(7y)−f(7(x+y))]. By concavity and the decrease of f(r)/r,
this is at most h(x+y), with h=111[2f(7)−f(14)]/2. Consequently the
optimal separate-arm bill minus 36h is a lower bound for any
grouping. The computation encloses all powers and sums with outward
rounding to 22 decimal places.

## Higher multiplicities

The nine half-ranks in each arm are 2 through 10. At saturation
a half-idle demand at capacity c has bounds max(0,c−a)≤d≤c if the
arm's largest LOCAL multiplicity is a. Given n_arm LOCALs, the
sum of the half-demands is 54−n_arm.

To minimize the separate-arm bill, start with the lower demands.
Allocate the remaining increments in order of increasing depth
among all columns, respecting their caps. At every mask length
cutoff k, the marginal increase in ∑ min(k,2d) is first two,
possibly one, then zero. This same allocation maximizes the
sum for every k, giving the least nested cost. The table relaxes
actual maxima a,b to upper bounds only for this IDLE price. It
charges the QUERY lower bound for the declared actual maxima.

There are 331 feasible count/max cells per arm. Across the
108,832 paired cells with max(a,b)≥3, the highest directed signed
upper is −28.3066209237471478769601. For exactly 36 LOCALs it is
−46.0926684363776335553730. The 272 legal ordered one-slot transfers
also fail individually. All two-slot transfers introducing a higher
multiplicity are included in the grouped bound.

## Zero, one or two LOCALs per stage

Here write m=36−n. At saturation with a stage retaining two LOCALs,
the head identity block gives q_count≥m+4. Suppose each arm has a
stage with two LOCALs and two cross IDLE incidences. In each such
stage the cross IDLE images and rows span the two root spaces.
Both LOCAL defects then have column and row only on the private
coordinates of that arm. The four terms across the two arms
give a four-by-four identity minor, requiring q_count≥m+6.
Thus at q_count=m+4 at least one arm has at most one cross
incidence per stage retaining two LOCALs. The total is at most
min(36,27+m).

The original IDLE masks attain the separate-arm nested minimum.
Each additional incidence increases it by at least
δ=111[f(63)−f(56)]. Two additional incidences and one paid QUERY
per retirement cost at least 2.92315928489496 more than the saved
net native moment. This exceeds h. Hence the upper at q_count=m+4
is greatest at m=0 using 27h and is below −2.36106060201144.
With q_count≥m+5 the extra 111 units dominate all 36 cross
incidences. If every stage has at most one LOCAL, the first 18
retirements increase the nested separate-arm minimum by four
rank-63 masks. At q_count≥m+3 and with all 36 cross incidences
granted the upper there is below −28.64227303907207. Each further
retirement only decreases this upper.

## Extra incidence and excessive native count

Every stage needs at least rank(E_s) serving dimensions. If any
stage has excess, there are at least 217−2n IDLE incidences
for n≤108. Grant arbitrary grouping into masks of up to 18 stages
and charge only q_count≥max(0,39−n). Concavity permits a lower bill
using full masks and one remainder. Across 0≤n≤108 the best
signed upper is −161.1964987524476534781450. For n≥109, even
granting every IDLE and QUERY free, the root productive moment
minus the native net debit is strictly negative and decreases
with n.

The remaining mechanisms change the native invoice, the endpoint,
the LOCAL or QUERY operator, the IDLE tariff, or the recursive
admission proof. The replay authenticates the exact #7001 caller,
receipt and interval engine, reconstructs the original paid and
productive profiles, and checks the exact integer price cells.
It also compares the greedy allocation against 96 small
bounded-demand fixtures.

Credit DreamingOfClouds, CubeJerry, zxv and the retained #7001
authors for the paired BIT source. [#7160](https://github.com/CrocSwap/integer-mult-bounds/pull/7160)
supplies independent-stage saturation and the 36-LOCAL rank bound.
[#6984](https://github.com/CrocSwap/integer-mult-bounds/pull/6984),
[#6800](https://github.com/CrocSwap/integer-mult-bounds/pull/6800)
and [#6825](https://github.com/CrocSwap/integer-mult-bounds/pull/6825)
supply related fixed-window and rank-factorization methods. The
two-LOCAL retirement argument was independently audited in Round 7.
OpenAI Codex and subagents materially assisted the proof, replay
and independent rank and price checks.
