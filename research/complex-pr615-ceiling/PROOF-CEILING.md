# Fixed-supplier, all-dispatch ceiling

The hypotheses are the two exact native words admitted by this package, 72 complete invocations, whole helpers assigned to the inherited owner windows, and the inherited native moment and outer conversion. We relax all timing constraints. A ceiling for the relaxation therefore also bounds valid timed assignments. No claim about other words or proof interfaces follows.

## 1. Native input identities

`check_ceiling.py` reads the freshly rebuilt canonical words and local programs, checks the actual helper widths against PLAN, and independently counts the paid local profiles in both orientations. In width order 4,5,7,8,9, JP8 has counts `(22,48,48,112,274)` and ATM3 has `(62,8,80,92,262)`. Their total helper widths are 4026 and 3942. Write their local paid profiles as L_J and L_A.

There are 112 bins for each owner window: 48 windows of capacity 8, and 32 each of capacities 16, 32, and 48. Total capacity is 387072. If A of the 72 invocations use ATM3, unused capacity is

`I(A) = 387072 - (72-A)*4026 - A*3942 = 97200 + 84*A`.

Each bin's unused capacity is its idle child rank. Splitting an idle remainder into additional children cannot lower the moment used below, since its exponent in rank is between zero and one. Thus using one child per nonempty remainder is a valid relaxation too.

## 2. An integer pattern weight

Give helper widths 4,5,7,8,9 weights -4,-41,-19,-8,3 respectively. The total weights of a JP8 and ATM3 invocation are -3042 and -2046; their difference is 996.

Let M(s) be the largest weight of any multiset of these widths summing to s. Exhaustive integer dynamic programming up to s=48 gives

`M(8)=-8, M(16)=-16, M(32)=-32, M(48)=0`.

Denote these four values by u(C). For a bin of capacity C with remainder r, its used helper pattern has weight at most M(C-r). Define `delta(C,r)=M(C-r)-u(C)` whenever the used sum is attainable. Summing over all bins gives

`-219024 + 996*A <= -215040 + sum(delta)`,

or `A-4 <= sum(delta)/996`. In particular, if every remainder is either zero or 48, then every delta is zero and A≤4.

## 3. The moment comparison includes fragmentation

Fix `b_U = 1628658892827744394867/10^24`, which is one `10^-24` tick above PR615's verified native complex lower endpoint. Set `F(0)=0` and `F(r)=r*(73/r)^b_U` for positive r. This is the inherited native moment numerator. Its denominator is `73*7168`.

The baseline profile H is `68*L_J + 4*L_A + 2032` children of rank 48. For a hypothetical dispatch and packing, subtract its ideal rank-48 idle charge from each remainder. Define

`G(r)=F(r)-(r/48)*F(48)`,

`D=sum_r (L_A(r)-L_J(r))*F(r)+(7/4)*F(48)`.

The difference between its moment numerator and H's is exactly

`(A-4)*D + sum_bins G(r)`.

The rational interval checker proves D<0. Multiplying the weight bound by this negative D reverses the inequality, so the difference is at least

`sum_bins [G(r)+D*delta(C,r)/996]`.

## 4. Every bin contribution is nonnegative

There are only 92 attainable `(C,r)` cases across the four capacities. The checker enumerates all of them. For r=0 or r=48, both delta and G are exactly zero. Every other case has a strictly positive lower interval endpoint for `G(r)+D*delta/996`. The certificate includes every maximizing integer pattern and every rational lower margin. Consequently every dispatch and packing has moment numerator at least H's.

The logarithm and exponential enclosures use exact rational Taylor bounds with outward rounding; there are no floating-point decisions or solver optimality assumptions in this certificate. `code/exact_intervals.py` supplies the enclosures. `EXACT-CEILING.json` records the hashes of both canonical words and both local-program artifacts actually checked.

## 5. Convert the moment obstruction to κ

The checker proves `sum_r H(r)*F(r)/(73*7168)>1` at b_U. All positive ranks are below 73, so this moment strictly increases with b. Thus no admitted profile in this relaxation satisfies the inherited native moment inequality at b≥b_U.

The inherited strict outer constraints imply κ<b/(1+b): its bootstrap exponent is below b, and its positive slack factors only reduce the admissible outer value. Since b/(1+b) is increasing, every value certified through this interface obeys

`κ < b_U/(1+b_U) = 1628658892827744394867/1001628658892827744394867`.

The fine-grid certified κ is `1626010676080313339567/10^24`. Direct rational subtraction places its gap to this ceiling below `51/10^24`. Further progress of practical size therefore needs a change outside this fixed family or interface. The theorem does not claim unrestricted optimality.
