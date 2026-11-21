# Ordered transport and tensor support

Let \(I\) be the 18,906 labelled productive occurrences and \(J\) the 104,904 labelled paid occurrences in the literal 36-call BIT word. Their ranks are \(k_i\) and \(r_j\). Let \(D_j\subseteq I\) bound the support of the full field of paid occurrence \(j\) as a linear function of the independent productive fields.

The support is regenerated from the exact source. In each normalized inner chart, initialize every original public field to its own independent symbol and every private field to zero. `ADD` adds over the binary field, `SWAP` exchanges, an owned `CLEAR` retires, and `MOVE` changes chart while retaining the normalized combination. The chart action and its matching inverse act linearly on the full field, so changing to physical coordinates introduces no new independent input. At each `LOCAL` the two raw main input vectors are read from the exact outer group-ring state, and each helper remains its own labelled input. The group ring tracks the head and disjoint body involutions. Its outer result is checked on all 38 independent roles. The union of the input supports is a conservative bound. It permits extra incidences when two physically transformed summands might cancel. At `QUERY` the issued job is a copy of the actual source role. At `IDLE_ONE` it is the actual role field. Distinct chronological paid occurrences stay distinct, including when their ranks and supports happen to agree.

Write \(c_0=0.003890115286594461129996943\), \(t_0=1-c_0\). Dividing the checked integer amounts by \(10^{30}\) gives a nonnegative matrix \(F_{ij}\) such that

\[
\sum_j F_{ij}\ge k_i^{t_0},\qquad \sum_i F_{ij}\le r_j^{t_0},\qquad
F_{ij}>0\Longrightarrow i\in D_j\text{ and }k_i\ge r_j.
\]

The checker rounds every productive entry up and every paid entry down using the independent outward log/exp engine. Paid occurrences of the same rank and same permitted dependencies may be collected for certificate storage. Dividing each aggregate entry evenly among the identically funded occurrences reconstructs the matrix on the original ordered occurrences. The checker verifies that each target's outgoing mass pays its entire rounded demand, no paid group is overspent, and every used arc is allowed. In particular incidence means agreement with the computed supports, and rank order is tested before an arc is admitted. The certificate uses 86,730 such paid groups and 114,266 nonzero entries.

For \(c_0\le c\le1\) choose \(t=1-c\). Rescale row \(i\) by \(k_i^{-(c-c_0)}\). Its outgoing sum still covers \(k_i^t\). On each used arc, \(k_i^{-(c-c_0)}\le r_j^{-(c-c_0)}\), so the incoming sum still fits \(r_j^t\). Tensor powers of the rescaled matrix preserve both inequalities. For a tuple of paid requests \(\mathbf j\), every incoming tensor arc belongs to the Cartesian set \(\prod_{a=1}^v D_{j_a}\).

The chronological tensor interpreter binds an independent productive field to each labelled tuple. At an earlier depth it receives the real paid fields before a child runs. Each exact completed child acts on its assigned field and restores the other fields. Induction through the raw continuations bounds the support at a leaf by the Cartesian product of the individual raw supports. A certificate based on this support rule can omit a paid tuple if the Cartesian product is disjoint from the retained productive set \(A\subseteq I^v\). Charge the full rank of every other paid tuple. This is the compiler class considered here, even if a stronger algebraic test were to prove some other field zero.

Summing outgoing mass over \(A\) and then bounding the cost of its receiving paid columns gives

\[
\sum_{\mathbf i\in A}\prod_{a=1}^v k_{i_a}^t \le
\sum_{\mathbf j\, :\, A\cap\prod_a D_{j_a}\ne\varnothing}\prod_{a=1}^v r_{j_a}^t.
\]

For \(0\le t\le1\), every actual split of a positive rank only increases its cost. Paid remainders, integer fringe axes, phase restoration, and compiler costs can only add charges. Thus no positive surplus is possible in this support-based class at the stated exponent or higher, for any finite positive power or productive subset. The result concerns this class of certificates, with other support proofs and native operator changes outside its scope.
