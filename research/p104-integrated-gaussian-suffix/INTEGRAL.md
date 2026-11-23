# Referee report on the Gaussian matched-suffix price

The deterministic upper bound for the complete matched-suffix sum is valid for the two reviewed calendars. The predecessor is ToikY’s #8072 at `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`. The first candidate keeps its offset 8 and lower band 1874. The second installs offset 6 and lower band 1054. Both use weights 5 and 451, upper scale 263772, raw trial $c=17145637307/2^{42}$, and $t=1-c$. My check concerns the finite numerical debit feeding the signed supplier. The five inherited all-size assumptions continue to govern the resulting overall multiplication claims.

## From an issued integer prefix to an integral

Use $s$ for the column offset, $M=2^H$, $H\ge1024$, $K=M^{82}$, $V=M^6$, and $U=2\lfloor M/(1724\cdot306)\rfloor$. A sender label of grade $r$ at even band $e$ issues $P=r(e-s)$ axes. An interior target of grade $k$ at even band $d$ takes $Q=k(d-s)$. Put $z=k/r>1$. The corresponding grant is

    q = floor(w_a π · lower_measure(max(e,zd), min(e+2,z(d+2)))).

The measure encloses the integral of $Vx^{-1-t}$. Here $w_a$ belongs to the sender and $π$ is the share of the particular receiving port. The actual constructor computes this lower endpoint, multiplies by the weight and share, floors, creates disjoint replica intervals, and skips zero grants. The upper endpoint and a ceiling are used for births. See `runtime/transport.py`, lines 13–42, and `runtime/typed_transport.py`, lines 76–101 and 102–155 of the pinned predecessor. The six-column source keeps the same integrals, rounding and disjoint ranges.

For every interior intersection of positive length, $D=re-kd\in(-2r,2k)\cap g\mathbb Z$, with $g=\gcd(2r,2k)$. An actual suffix therefore satisfies

    s(k−r)−2r+g ≤ P−Q ≤ s(k−r)+2k−g.

The sharp pointwise constants also follow from Bézout. For each multiple of $g$ strictly between the endpoints choose even $e,d$ solving $re-kd=D$. Adding a common period makes both bins positive while preserving that equation. Those bounds on $D$ are exactly the positive-overlap conditions. For offset 8, $5r\le4k$ already proves nonnegativity. For offset 6, the maximum over the 51 actual cells of $(2r-g)/(k-r)$ is $94/17$. Both candidates have $P-Q\ge0$ throughout the ideal grid as well as on their nonzero finite grants. This permits multiplication of the upper bound on $q$ by $P-Q$ and extension of the integration domain. The pointwise constant by itself yields a valid, weaker per-cell price.

Write $y=x/z$, and write $a(v)=v-2\lfloor v/2\rfloor$. Up to endpoints of zero mass the $e,d$ overlaps partition the interval $L\le y<U/z$. Each actual pair intersects at most two recipient bands per source band. The coordinate change transforms $x^{-1-t}dx$ into $z^{-t}y^{-1-t}dy$. On its overlap the physical suffix is exactly

    S_s(y) = s(k−r)+k a(y)−r a(zy).

Summing over the actual finite grants bounds their contribution by this deterministic integral on the overlaps. Extending to every $y\ge L$ only adds nonnegative mass. The grade-pair coefficient after summing actual tickets is $D_r p_{rk}$, with $D_r=\sum_a w_a n_{ar}^{paid}$. In fact the share to type $b$ is $p_{rk}w_b n_{bk}^{target}/N_k$, where $N_k=\sum_b w_bn_{bk}^{target}$. The constructor then divides by the number of individual ports in that class. Summing the latter contributions over the real receiving ports and both issuing types gives the claimed weight. Those are the paths in `runtime/grades.py`, lines 39–59 and 96–133.

## The two phases and the infinite integral

Put $b(v)=a(v)^2/2-a(v)$. This continuous periodic function takes values in $[-1/2,0]$, including at the joined endpoints, and $b'=a-1$ almost everywhere. Let $J(y)=k b(y)-(r/z)b(zy)$. Then $J'=S_s-(s+1)(k-r)$ almost everywhere. At $L$, the recipient phase is zero since both installed lower edges are even, so $J(L)\ge0$. The donor phase $zL$ can be nonintegral. Everywhere $J\le r/(2z)$.

For $f(y)=y^{-1-t}$, integration by parts on $[L,T]$ followed by $T\to\infty$ gives

    ∫_L^∞ f J′ = −f(L)J(L) + ∫_L^∞ (−f′)J
               ≤ f(L)(sup J−J(L)) ≤ f(L)r/(2z).

The bounded primitive and decaying density annihilate the top boundary. The locally finite breakpoints give no jumps. Both integrals converge absolutely. As $\int_L^\infty f=L^{-t}/t$, the normalized total obeys

    ∫_L^∞ f S_s ≤ (L^(−t)/t)[(s+1)(k−r) + t r²/(2kL)].

The sharper $(t/L)(\sup J-J(L))$ correction is valid with the same assumptions. Each line controls the weighted total on the extended half-line. A single issued loan can exceed the coefficient in brackets. Conditioning on the occupied finite grants can also change the mean. The proof uses the full mass integral and the downward grant inequality.

## Every other physical charge

Set $C$ to the number of births of one type and band per tick, $j$ to the true paid index, and $B=\max(0,K-jD[e])$. For its list of interior grants $q_i$ and target lengths $Q_i$, the count in `TypedPlan.leaves_per_epoch` satisfies the exact identity

    K C P − B Σ q_i Q_i
    = K Σ q_i(P−Q_i) + K(C−Σq_i)P + (K−B)Σq_i Q_i.

The first term is the matched-suffix charge just proved. The second pays the full field from each otherwise unallocated parent. Its ideal mass is the bottom interval $L\le x<Lz$, summed with the same grade weights. Using $P\le rx$ bounds that ideal sum by $V L^c Ψ$, where $Ψ=\sum D_r p_{rk}r(z^c-1)/c$. The rest is the upward birth error plus the sum of the missing parts of the downward interior grants. A positive overlap rounded to zero is included here. A zero-bound receiving field still has its prescribed opening, action and return. The last term is the lost prefix when late births issue after the last funding tick. Solely bounding it by the whole paid field is conservative. In particular it remains payable when $B=0$.

For either installed $L$, $4(e+2)/5<5e/6$ on the admitted bands. A true occupied recipient has a strictly earlier temporal scale. The constructor assigns distinct ranges per recipient owner. The event tape visits consuming bands after the sender at that tick, retires on schedule, and clears every pending loan. A nested matched job contributes through its own paid events. This identity charges the upstream singleton suffix once. See `runtime/typed_transport.py`, lines 167–253 and 255–269, and `runtime/transport.py`, lines 270–322.

The floor/ceiling estimate remains valid with the current maximum multiplicity 451. For $x\in[1,M]$, the inverse-power routine starts with its grid enclosure for $1/x$. Its lower endpoint is at least $1/(2M)$, and every normalized endpoint $u$ satisfies $0<u\le1$. Each of the at most 42 square roots increases the interval width by at most the factor $\sqrt{2M}$ plus two grid units. Widths from at most 43 products in this interval add, with two grid units per rounding. With grid resolution $2^{-64(H+1)}$, a loose upper bound on the two-endpoint uncertainty even after multiplying by $451V/t$ is $2^{160}M^{-36}<1/4$. The floor or ceiling of a directed endpoint thus differs from the unrounded ideal mass by less than two replicas. There are fewer than $2^{20}\cdot2^{17}$ real source-target label pairs across both types, at most two internal intersections per source bin per pair, and one exterior interval per recipient bin per pair. Actual field lengths are at most $M$ and there are fewer than $M$ bands. These estimates cover the old $2^{46} M^2$ allowance, including the birth ceilings. The per-birth terminal drain is below $2^{20}V/M^4$, since $jD[e]<M^{77}$, total per-tick births are below $2V$, and each has fewer than $2^{19}$ paid fields of size below $M$.

True exterior grants use virtual donors at $x\ge U$ and retain their own lower accounting. Their recipient coordinate is at least $U/516$, and $2\lfloor y/2\rfloor-s>y-10\ge(1-2^{-128})y$ at all allowed $H$. Their actual lengths are at most $258U$. The period $4\lceil M/(4Q)\rceil$, its incomplete tail in $M^2$ rounds, the even upper-band rounding, and the final group of real productive rows all use the predecessor’s charges. The exterior lower bound and the unmatched-parent term each carry the full charge for their own grants. With $\delta=2^{-128}$, the resulting factor on $M^{1-c}$ is bounded by

    (1+δ)(1+1032/263772)(263772L)^c (1+d/L+δ)/(1−δ)^4,

where $d$ is the bounded grade sum divided by $tΨ$. The factor includes the lower-band loss, late births, the exterior, and the incomplete period and group.

## Independent controls and their scope

The verifier reads the predecessor’s actual grade producer, traverses all 88 typed allocations, reconstructs the 51 weighted cells, and tests 1,971 exactly constant phase intervals. Independent rational arithmetic uses the atanh series for the reduced logarithm and the exponential Taylor series, with positive remainder bounds and outward fixed-point rounding. The identity $z^{-t}=z^c/z$ evaluates both integrals through the same positive scalar. It gives the following enclosures.

| Offset and lower band | Fringe coefficient | Complete accounting factor | Upper debit |
|---|---|---|---|
| 8, 1874 | $4.550681666 < d < 4.550681667$ | $1.088033933515 < F_* < 1.088033933516$ | $130699669/2^{30}$ |
| 6, 1054 | $3.539445647 < d < 3.539445648$ | $1.086602588029 < F_* < 1.086602588030$ | $125645/2^{20}$ |

One tick down on the respective stated grids fails each displayed accounting expression. An improved accounting argument could still produce a smaller upper bound on the physical run.

The actual production exponent and the exactly integrated $t=1$ control each ran through literal bounded `TypedPlan.events()` for both offsets. The fixtures included every sender/receiver type combination, late paid events, exterior and zero descriptors, zero integer grants from positive overlaps, and a chain of three nested loan edges. At the production exponent, 4,846 emitted loans were received exactly once and 2,430 issued suffixes exceeded the integrated coefficient. The total for offset 8 was $65,560+2,363,856+703,260=3,132,676$ singleton axes. Offset 6 yielded $51,040+2,445,520+727,400=3,223,960$. These fixtures use small synthetic native grades and the actual compiler and event path. The arithmetic and grade-shape checks use the actual source distributions. The all-size conclusion follows from the integral proof and finite-error bounds.

The registered `price` and `calendar` modes run the independent numerical and event controls against the freshly reconstructed runtimes. The previously observed results are in [referee-price.json](data/referee-price.json) and [referee-events.json](data/referee-events.json); their timestamps are not compared when rerunning. At $H=1024$, `actual_six_grant.py` reconstructs the floor for a specific installed source and receiver from the 65,600-bit quadrature. The physical 96-to-130 edge from band 1642 to 1214 has a 6,117-bit positive grant at sender type 1 paid index 2 and recipient type 1 target index 1. The suffix is 16 with offset 6 and −52 with offset 4. The receiver returns on time and the original paid event can issue during the epoch. See [referee-six-grant.json](data/referee-six-grant.json).
