# Complete finite cutoff from the true label width

For the fixed multiplier use $R=240$, $t=\log_2\log_2 n$ and the same physical routing, arithmetic and storage. The sharper sufficient endpoint is

$$
 t\ge7{,}519{,}517{,}465{,}920{,}988
 \quad\Longrightarrow\quad
 T(n)\le n(\ln n)^{501/1000},\qquad S(n)\le2^{32}n .
$$

## A rational majorant for the label charge

Use the [true-label native inequality](address-refined-label.md), with $D=2^j$, $Q_j=3j+\lceil\log_2(3j+3)\rceil+2$, $\tau=(y/240-2)/(Q_jD^3)$ and $y=\log_2 e$. At a guaranteed degree $D$ the actual child volume satisfies $(\sigma+2)/s\le(3+E_j/\tau)/D$, where $E_j=[j+\log_2(8Q_{j+1}+1)+3]/Q_j$. The true integer label has $t_0\le D(8Q_{j+1}+1)$ and the same actual $d$ appears throughout the bound. At a larger selected degree the separate charge is at most $17/(8D)<3/D$. These inequalities include all repeated children and restored reserves.

For a rational clock define

$$
 \bar E_j=\frac{j+\lceil\log_2(8Q_{j+1}+1)\rceil+3}{Q_j}.
$$

At $\tau=1,2,4$ begin the three respective slopes $(3+\bar E_j/a)/D$, with $a=1,2,4$. The final slope continues to the next degree band. These slopes dominate the decreasing true density throughout each interval. The direct potential has slope $1/2$ up to $y_A=240(2^{17}+2)$, inside the first $j=4$ interval. Use the $a=1$ slope from that switch.

One has $\bar E_j\le5/6$. At $j=4,5$ the relevant ceiling logarithms are both 8, giving $15/18,16/22$. For $j\ge6$, $Q_{j+1}\le6j$, first at $j=4$ and then by its increments of at most four. Since $48j+1\le2^{3j/2}$ at $j=6$ and thereafter its ratio per increment is below two, the ceiling log is at most $3j/2+1$. Now $Q_j\ge3j+6$, so $j+(3j/2+1)+3\le5Q_j/6$. This also gives $E_j\le\bar E_j$ and proves that every interband switch decreases the slope, from at least $3/D$ to at most $(3+5/6)/(2D)$. The resulting rational piecewise-linear $H(0)=0$ is increasing and concave. Every actual native child thus pays the established quarter even when crossing several degree bands, giving the same physical $5120V\sqrt u\,2^{H(\log_2u)}$ invoice.

## The complete historic test

The [rounded-width Walsh transfer](routing-refined-walsh.md) uses $G(x)=48\Phi(x)+\max(0,\max_{v\le x}[H(v)-(159/4)\Phi(v)])$, with $v\ge0$. This pays the true typed slot movement $m^{17/2}\sqrt f$, every ordinary $m^{45}$ term, and the child quarter with its original full-occupancy reserve. Its [density proof](../S008/PiecewiseDensity.lean) gives $G(t+2)/t$ nonincreasing. Constant and logarithmic prefactors divided by $t$ decrease as well. Therefore checking one left endpoint extends to every later real input, including all future degree bands. The raw small-prefactor invoice, with one binary exponent bit for natural logarithms, is $183+4\log_2(t+2)+G(t+2)$.

The 29 earlier vertices, including zero, and the current point exhaust the continuous maximum. Between them $H-(159/4)\Phi$ is convex. At both adjacent integers the old $j=13,a=1$ vertex supplies the largest contribution strictly. It equals

$$
 w=6{,}201{,}245{,}580{,}657{,}120,\qquad
 H(w)=890362700843914785456/158055205.
$$

Its surplus lies strictly between 610,546,135,040 and 610,546,135,041. The current-point surplus is smaller. Thus the exact test at the two adjacent input scales is

$$
 \frac{t}{1000}>
 183+4\log_2(t+2)+48\Phi(t+2)+H(w)-(159/4)\Phi(w).
$$

| Endpoint | Certified residual interval in units of $10^{-12}$ |
|---:|---:|
| 7,519,517,465,920,987 | $(-325836553,-325836552)$ |
| 7,519,517,465,920,988 | $(53248687,53248688)$ |

The [24-term rational checker](../checks/cutoff.py) uses integer cube roots for every vertex and compares lower and upper enclosures pairwise. The [independent evaluator](../checks/cutoff_independent.py) uses 52 logarithm terms and a $2^{-112}$ cube-root grid. Both certify the displayed signs and the same winning vertex.

## Formal transfer

The [schedule theorem](../S008/LabelSchedule.lean) rebuilds all 29 native rows from the actual integer-scaled label coefficients, validates slope order and intersections, and checks the six supporting continuations used by the enclosing width. The last measured slope extends as an upper bound through every future switch by concavity. Its theorem `S008.Piecewise.LabelSchedule.schedule_natural_clock` proves the leading-one natural-log result for every larger original input from the physical rounded time invoice and its packing inequality. The existing tape machine, child-cost invoices and bank movements enter through the linked written suppliers.
