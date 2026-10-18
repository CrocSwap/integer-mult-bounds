# Complete interface bill and a matched dense integer realization

The saved transfers are paid work. Twelve child queries alone is not a full
cost comparison. Both words reserve the same two arbitrary-dirty roots.

## General ports and tariffs

Let c_F,r,+ and c_F,r,- be complete positive/negative query prices for operator
F at root port r, including coefficient/source access, arithmetic, target
updates, private scratch restoration, routing, frame conversion, head return
and child dispatch. Set q_F,r = c_F,r,+ + c_F,r,-. Let t_a price a complete
one-way pass z += a*w with the same obligations. Let I,P,D pay input/layout
admission, coefficient preparation and remaining program/control work.

```
new = I_new + P_new + D_new
    + q_A0,z + q_A1,z + q_A2,w + q_B0,w + q_B1,w + q_B2,z
    + 2 t_-1 + 2 t_+1.
old = I_old + P_old + D_old
    + q_A0,z + q_A1,z + q_A2,z + q_B0,z + q_B1,z + q_B2,w
    + 4 t_-1 + 2 t_2.
```

The old word is PR1637's literal six-pass construction. It is not assumed
that changed ports have equal prices. If prices are port independent and
t_+1=t_-1, the operational saving is exactly 2*t_2 before differences in
I,P,D. This is a strict circuit improvement at those tariffs; there is no
global cost optimum claim among words with additional child queries.

## Complete recursive lowering

For F=L R in application order, use a disjoint dirty row s and perform
R(x,s), L(s,y), inverse(R)(x,s), inverse(L)(s,y). An inverse reverses every
instruction and its sign. Private descendants exclude all six data rows,
both roots, and the active ancestor row. Siblings reuse scratch only after
restoration. Thus

```
C([f]) = complete leaf cost + leaf dispatch;
C(F) = 2 C(R) + 2 C(L) + node dispatch;
h([f]) = 0; h(F) = 1 + max(h(R), h(L)).
```

At B lengths 2,3,4 and A lengths 5,6,7, balanced splits give 4,10,16,28,40,52
leaf calls. Both root words contain each operator twice, hence exactly 300
factor calls. The new word adds four root passes; the old adds six. Both
require three private child rows in addition to the two roots, eleven mutable
rows including sources and outputs, and 27 distinct read-only factor matrices.
The verifier executes both expanded programs over all eleven independent dirty
symbols with free noncommuting factors, including every inverse/restoration.
There is no hidden initialization, full-array copy or recursive child.

## Declared dense integer tape model

For an explicit finite realization, supply the 27 dense L-by-L integer factor
matrices and eleven length-L integer rows. Place rows at offsets 0..11L-1,
then matrices consecutively in B0,B1,B2,A0,A1,A2 factor order. Every primitive
starts and ends its data head at cell zero. A factor update visits, in order,
each coefficient, source entry and target entry, for every output/input pair;
it updates the target by that one product. A root pass visits w[k],z[k] for
each k. This is deliberately literal, with one target update per matrix term.
Root doubling costs an additional doubling before accumulation.

Both programs use the same fixed layout and widths. Owned scalar operand/work
registers and counters are admitted and initialized once, and work is cleared
after each term/pass entry; these are scalar words, never a free full row.
The invoice counts one product-work clear per update. If operand latches need
additional loads/clears, charge the same fixed per-visit tariff in both traces.
The new trace has no more visits or operations of any listed kind.

At length L, both use 300L^2 coefficient reads and multiplications. The old
uses 300L^2+6L source reads, target read/write pairs, additions and work clears;
the new uses 300L^2+4L of each. The old has 2L root doublings, the new zero.
Factor-query signs occur equally often in both programs; root negations fall
from 4L to 2L. Literal expanded instruction records fall from 306 to 304.

With f the zero-based matrix index and source/target rows p,q, independently
summing the visits gives the factor head movement

`(2f+1)L^4 + (21-2 min(p,q))L^3 + 2(q+1)L - 2`.

Each root pass w->z costs `2L^2+14L-2`. After including every changed child
port (not only deleting two passes), the complete polynomials are

```
old: 9636 L^4 + 2068 L^3 + 12 L^2 + 5580 L - 612
new: 9636 L^4 + 2044 L^3 +  8 L^2 + 5560 L - 608
saved:          24 L^3 +  4 L^2 +   20 L -   4.
```

The saving is positive for every integer L>=1: its value at 1 is 44, and
all nonconstant coefficients are positive. A separate literal tracer checks
both full invoices at L=1,2,3,4,8,16, rather than assuming port equality.
These are exact operation counts, not measured runtime or a native supplier
invoice. INDEPENDENT.json retains every counted field and finite prefix norm.

## Width, preparation and control costs

For initial mutable entries bounded by X>=1 and factor entries bounded by
H>=1, one factor call increases the largest magnitude by at most 1+LH;
a root shear a increases it by at most 1+|a|. A common bound covering both
complete chronological words is

`B = X * 2^4 * 3^2 * (1+LH)^300`.

Use signed width `w = 1 + ceil(log2(B+1))` for rows and enough scalar product
width for H*B as well. The candidate alone has the smaller bound with the
factor 3^2 removed, but no narrower physical allocation is claimed. Arbitrary
Q/C precision is outside this integer example. Bit-level multiplication,
addition, loading and clearing are paid at their actual w-bit tariffs.
Counters/address records use O(log(L+2)) bits plus fixed role/matrix indices.

I pays validation and an initial scan of 11L+27L^2 data/coefficient cells,
owned scalar initialization, program loading and required final head positions.
P pays construction of any supplied matrices; it is identical for both words
on the same input. D pays instruction reads and selection, 300 dense-loop
dispatches, four versus six root-loop dispatches, every loop increment/test,
address calculation and scalar cleanup. A fixed-width interpreter can charge
the same per-iteration/control tariff, with 304 versus 306 root-level records
and no increased loop count. No schedule oracle is used: the words are fixed.
Any external layout or frame adapters must be added to I and to the actual
port tariffs. The declared realization needs none because all rows share the
stated dense interface; it is not evidence those adapters are free in PR1094.

Selected-supplier common-label realization, whole-call hosting, precision/tape
integration and outer analytic assembly remain separate. No bit/complex
binding switch, changed moment, new kappa or multiplication runtime follows.
