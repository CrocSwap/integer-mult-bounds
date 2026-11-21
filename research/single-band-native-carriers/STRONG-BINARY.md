# Physical binary word with 111 ports

The general ordinary service uses the 111-port circuit of Ali Romman in
[PR #8027](https://github.com/CrocSwap/integer-mult-bounds/pull/8027).
Its literal 39,600-instruction graph is
[pinned here](https://github.com/aliromman/integer-mult-bounds/blob/fb9b6a7b0d27da1cf98430893a3016bf811e2aa4/research/p104-live-relative-gain/BINARY-CANDIDATE.json.gz).
The compressed SHA-256 is
`74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326`.
The expanded SHA-256 is
`b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69`.
The binary source module supplies this graph to the bank interpreter,
the image and kernel frame generators, and the ordered productive and
paid lists. It retains the 36-call outer binary word and the physical
bank operations of [PR #7914](https://github.com/CrocSwap/integer-mult-bounds/pull/7914).
Clear1nsight supplied the predecessor mixed-rank compiler. The 111-port
word extends the punctured E8 circuit. The
[source notice](https://github.com/aliromman/integer-mult-bounds/blob/fb9b6a7b0d27da1cf98430893a3016bf811e2aa4/research/p104-live-relative-gain/PARENT-NOTICE)
credits its predecessors. The new supplier binding, strict prices and
full exact chart check use substantial OpenAI Codex assistance.

## Native action on arbitrary fields

Work on one simultaneous ternary component. For a diagonal unit weight
matrix A, head h, tail t and a projector P, set d=t−A⁻¹h. Write D(P) for
the address permutation that takes (h,t) to (h+APd,t−Pd).
The new difference is (I−2P)d. It follows by substitution that
D(P)D(Q)=D(P+Q−2PQ) when P and Q commute. In particular, D(P) is its
own inverse, disjoint chart axes commute, and D(P)D(Q)=D(Q−P) when
PQ=QP=P. These equalities hold over every required cyclic ternary
ring. The common reduction lets them act on all component sizes at
once. Finite coordinate products with the identity on each column
and on all remaining positions preserve the identities.

Let P_i be the projector onto the first dim(i) columns of the table
for frame i. The exact checker constructs all 636 projectors over the
rationals with denominators coprime to three. For every one of the
2,352 distinct MOVE and helper endpoint pairs it verifies both products
of the smaller and larger projectors equal the smaller projector. It
constructs a full invertible eigenbasis for their positive difference
at the stated rank. For each of 111 main pairs, the first input has a
rank-one head H, the second input has the zero projector, the first
output has the identity projector, and the final second projector is
I−H. The same checker verifies both the emitted chart word and its
inverse on the full basis. Its 44,825 forward factors have scale and
addition numerator and denominator magnitudes at most 20, including
their inverses. Each scale is a unit at three. These facts apply the
existing physical operations at every modulus and on every admitted
geometry. They also apply to Kronecker extension by the column identity.
The compiler preserves all spectators when it lifts a chart.

At a register in frame i store D(P_i) applied to its normalized
field. INIT installs zero. MOVE uses the positive difference above.
ADD combines fields in a common chart. SWAP exchanges the two actual
register images and their current chart labels. CLEAR scrubs its
entire owned bank. Exact propagation of 630 independent binary basis
vectors through all instructions gives (x,y+x) on the 111 main pairs
and identity on all 408 separate helpers. It checks every chart label,
live register and allocation. All 3,433 private clears see a nonzero
symbolic form. Each of these fields goes through the paid bank scrub.
Specialized public zero helpers have a different lifetime. They remain
live through the source word and return zero before retirement.

At one main port write B=I−H for this stage. Removing the input gauges
and installing the output gauges gives (D(B)x, D(I)x+D(B)y).
After its joint frame placement this has the form
S(x,Qx+y), where S is the stage body and Q is its disjoint head exchange.
The exact checker executes the full outer circuit over formal binary
sums of all 38 role inputs with monomials in the 19 commuting
involutions. A LOCAL uses that pair formula. QUERY adds Q times a
borrowed field and returns it for its charged retirement. Each IDLE_ONE
applies its listed stage product. ADD and SWAP act on the actual roles.
All 38 resulting expressions equal the one desired diagonal monomial
on the original role, with the required head and every named stage.
The 111 chart placements and inverses thus deliver every labelled field.
The 36 copies of all 408 helpers contribute separate productive ports.
Their omitted grades in the powered rule still receive full zero
fields and every original instruction. The 18,906 productive and
104,904 paid labels are generated from this same source.

## Two strict powers

Let T(t) and P(t) be the respective sums of true ranks to power t for
the 36-call word. For v equal to 128 or 228 run the full chronological
v-fold product. The productive cutoff is k^v, with k=16 at v=128 and
k=15 at v=228. Serve every paid
rank in lexicographic, disjoint blocks of size at most 12^v.
The full ambient is 134^v and the maximum productive rank is 127^v.
At a split the child receives the active coordinates in the current
complete physical chart. The outside change of basis remains live
until all blocks return. The executed primitive permutations commute
on these axes, including for an arbitrary dirty field, so all these
calls implement the one requested projector. The producer and graph
forms are independent of either operand.

Put t=1−C and z=19/64. Use w=13/32 at v=128 and w=31/64 at v=228.
The high tail of a paid rank R>12^v costs at most 2R^(t+z)/12^(vz),
since z≥C. With K<k^v, the credited
mass lost at a discarded productive rank is at most
k^(vw) K^(t−w). Divide the source debit by T(t)^v. Including every
split and loss, its upper bound is

    α^v + 2γ^v + λ^v
    α=P(t)/T(t), γ=P(t+z)/(12^z T(t)), λ=k^w T(t−w)/T(t).

The checker uses an outward integer grid of size 2^128. At a root
it takes floor(sqrt(lo·grid)) and floor(sqrt(hi·grid))+1. At a
positive multiplication it rounds each end outward. All exponents
are dyadic rationals, so the indicated products of iterated roots
enclose the true moments. The final powered bounds use exact
rationals. A second reader constructs its histograms directly from
the raw MOVE records, 36 LOCAL calls, helper endpoints and caller
diagonal. It uses the positive series for log and exp with rational
geometric remainder bounds and an independent 2^112 grid.
It gives surplus strictly greater than 117686113386034/10^18 and
131151226/10^18, respectively. For the second profile, putting the
old cutoff 16^228 back into the same tail certificate makes its debit
exceed one. Pricing the raw word at 0.0038901152866 also gives a
strict deficit before any target loss or split. The powered paid mass
at the stated prices is at most (1−ε) times the retained
target mass since that target mass is itself at most T(t)^v.

| v | C | certified ε | band cutoff L | bits funding 32F/N^(1−C) |
| ---: | ---: | ---: | ---: | ---: |
| 128 | 2039/524288 | 2⁻¹⁴ | 2¹⁵ | 14 |
| 228 | 17108907955/4398046511104 | 2⁻³⁴ | 2³⁵ | 19 |

For the last column the dyadic carrier has no uncovered axis.
Its multiplier before the two moment powers is at most
32·(16/15)·2/(1−2/L)<72. With A=134^v and K=127^v, the checker compares
72^10000 (4 A K L)^39 with 2^(10000 d) for the displayed debit d.
Here C<39/10000. This includes both period and dummy owner costs,
the terminal elementary rank charge, and the worst covered leaf.
Both powers have strict separation kmin/rmax≥(5/4)^v>2. Let
P0=104904 be the number of true raw paid locations. Their rank sum
is S=285600. The number of paid blocks is at most P0^v+(S/12)^v,
by summing the actual block ceilings over all tuples. S<12P0, and
there are at most 18906^v productive tuples. Thus the total number of
port choices for a level is below 3P0^v<2^(18v). Since (5/4)^13>16,
the horizon satisfies vG≤13H/4+v. The syntactic enumeration has at
most (W+Pslots)^G<2^(18v) N^(117/2) units, including rejected ones.
All rational virtual column numerators and denominators have O(H) bits.
The outer charged tape generation still enumerates syntactic candidates,
rejected units, true banks and requested leaves.

## High-rate component widths

The current conditional comparator is
[PR #8029](https://github.com/CrocSwap/integer-mult-bounds/pull/8029),
at commit `a9dbc75e68e8c645df425adc489234d22df67f8d`. Its four-stage
ordinary rate is 0.003890115197377. Its complete claim is
0.00389011519729 with five stated premises. The high binary construction
funds that same ordinary rate in six cold stages. The stage logarithms
are 25,000,000, 160,000,000, 1,000,000,000, 6,000,000,000,
36,000,000,000 and 224,000,000,000. The last binary entry logarithm
is 267,185,100,786. The largest binary rank logarithm is
1,057 times smaller than in the earlier fully costed
[PR #7981](https://github.com/CrocSwap/integer-mult-bounds/pull/7981).
The complex supplier and outer geometry have their own entry conditions.

For the high-rate profile use ρ=1/250, η=39/10000, R_i as in the
staged machine, w=max(R_i,ceil(e^ρ)), g=ceil(e^η). Since η<ρ, g≤w.
The balanced physical components attain widths u−1 or u, with
g/2≤u≤g. With c≤e/w coarse columns and m=ceil(w/g) components,
mc≤2e^(1−η). Also m≤2w^(1−b_prev) for b_prev≤η and w≤e.
Thus both the balanced scans and genuine full-width stopped return
retain the staged tariff at any b_i<min(η,(249 C_i+b_prev)/250).
The coefficient setup still has w≤e≤(2u)^258, as 10000/39<258.
This keeps the explicit 6,000,000-bit allowance for its variable
polynomial where that allowance is used.

The quotient row bound at t=log₂ e is
k≤1+6(3+t/H)N² 2^(ηt). Its sufficient starting exponent is now
T=ceil(10000(2H+64)/9961)<3H. For t≥T the slope
(1−η)log(2)>1/4 gives 1+(t−T)/4≤2^((1−η)(t−T)).
Multiplying this inequality by the paid row bill gives k<e/64.
The six simultaneous reserves total less than e/4. The direct regime
uses the same independent owner divisor. Width and floor criteria
for entering a true native call use ρ, so their old formula is valid.
Root unplacement and cleanup fit e^(1−b_i) since η<1−b_i.
At the same cofinal width, the new high profile's upper bound on the
logarithm of the quotient reserve contains e^0.0039. Relative to the
earlier physical e^0.00388 bound it has an extra factor e^(1/50000).
The new H reduces its fixed coefficient at a quantified entry. Those
cofinal bounds do not imply a uniform reserve improvement at all e.
