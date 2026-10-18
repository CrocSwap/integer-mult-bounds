# Exact query minima for five-source parity hyperplanes

## Statement

Work over \(\mathbb F_2\). There are five read-only source rows \(x_j\), a
dirty connector \(z\), and a distinct dirty output row \(y_m\) for each mask
in

\[
 S(n,b)=\{m\in\mathbb F_2^5\setminus\{0\}: n\cdot m=b\},
 \qquad n\ne0,\quad b\in\{0,1\}.
\]

Every output asks for

\[
 y_m\longmapsto y_m+A_m\left(\sum_{j=0}^4m_jB_jx_j\right),
\]

where the \(A_m\) and \(B_j\) are arbitrary fixed linear maps. All data,
connector, and target rows may be dirty. The connector must be restored, and
the source rows cannot be changed. Allowed complete calls are
\(z\mathrel{+}=B_jx_j\) and \(y_m\mathrel{+}=A_mz\). Charge each complete
call one unit, including its fixed-size query record and dispatch. The
certificate supplies the factor-one instance for this unit tariff; no
helper, frame change, extra copy, or private scratch is used.

Under this contract, the exact minimum query count is

| Output family | Number of families | Minimum queries |
|---|---:|---:|
| \(b=0,\;|n|=1\) | 5 | 38 |
| \(b=0,\;2\le |n|\le5\) | 26 | 40 |
| \(b=1,\;1\le |n|\le4\) | 30 | 42 |
| \(b=1,\;|n|=5\) (odd-weight masks) | 1 | 44 |

Here \(|n|\) is Hamming weight. The total is 62 affine hyperplane families.
Each family has a source walk and two readouts per output, except the
odd-weight family, whose exact minimum is 44 because no restored ten-toggle
source walk covers all sixteen odd masks.

## Boundary-difference identity

For a source word \(w\), let \(q_t\in\mathbb F_2^5\) be the source-toggle
prefix after \(t\) calls, with \(q_0=0\). At that boundary,

\[
 z_t=z_0+\sum_j(q_t)_jB_jx_j.
\]

Two \(A_m\) calls at boundaries \(s,t\) cancel the arbitrary initial
connector and add

\[
 A_m(z_s+z_t)
 =A_m\sum_j(q_s+q_t)_jB_jx_j.
\]

Thus a pair of readouts realizes mask \(m\) exactly when
\(m=q_s+q_t\). Every witness in the certificate supplies one such boundary
pair for each requested output mask. Every source label occurs an even
number of times, so the connector returns to its arbitrary initial value.
The identity is valid for arbitrary linear maps, including singular and
noncommuting maps; it is not limited to the scalar replay used by the checker.

## Exact lower bounds and the exceptional family

Every active source must be toggled an even positive number of times to
restore \(z\), hence at least two calls. Every nonzero output target requires
an even positive number of readouts to cancel its dependence on dirty \(z_0\),
hence at least two calls. For a normal of weight one and \(b=0\), only four
source coordinates occur; all other families have five active sources.
These give the table's counting lower bounds 38, 40, and 42.

For \(n=11111\), \(b=1\), the output set is the sixteen odd-weight masks.
Any ten-call restored source word uses each of the five sources exactly
twice. Up to relabeling sources, these words correspond bijectively to the
945 perfect matchings of ten positions. The exact enumeration in
`CERTIFICATE.json` shows that every such word misses at least one odd mask;
the largest odd-mask intersection has size 15. With ten source calls, at
least one target therefore needs four readouts, raising the query lower bound
from 42 to 44. If a source word has more than ten calls, restoration parity
forces at least twelve, which also gives a 44-call lower bound. The
twelve-toggle witness covers all 32 differences, so two readouts suffice for
each of the sixteen targets and attain 44.

## Constructions for all 62 families

The 945 canonical ten-toggle words are exhaustively generated and tested
against the ten normal-weight/parity representatives. Coordinate permutations
carry each representative to every normal of the same Hamming weight. For
\(b=0, |n|=1\), the four-source word

```text
1 2 1 2 3 4 3 4
```

covers the fifteen nonzero masks in that four-coordinate hyperplane. The
other ten-toggle witnesses and the twelve-toggle odd-family witness are:

| \(|n|\) | \(b\) | Canonical normal | Source word | Queries |
|---:|---:|---:|---|---:|
| 1 | 0 | `00001` | `1 2 1 2 3 4 3 4` | 38 |
| 1 | 1 | `00001` | `0 1 2 1 0 2 3 4 3 4` | 42 |
| 2 | 0 | `00011` | `0 1 2 0 1 2 3 4 3 4` | 40 |
| 2 | 1 | `00011` | `0 1 2 0 3 2 4 3 1 4` | 42 |
| 3 | 0 | `00111` | `0 1 2 0 3 1 4 3 2 4` | 40 |
| 3 | 1 | `00111` | `0 1 2 0 3 1 4 2 3 4` | 42 |
| 4 | 0 | `01111` | `0 1 2 0 3 4 1 3 2 4` | 40 |
| 4 | 1 | `01111` | `0 1 2 0 3 1 4 2 3 4` | 42 |
| 5 | 0 | `11111` | `0 1 2 0 3 1 4 2 3 4` | 40 |
| 5 | 1 | `11111` | `2 0 2 1 2 0 3 1 4 2 3 4` | 44 |

The source walk is independent of data values. The output readout boundaries
are included for every mask and every one of the 62 normal/parity pairs in
`CERTIFICATE.json`.

## Scope

This is an exact result for the fixed binary connector alphabet, unit complete
query cost, five source labels, and affine-hyperplane output families. It is
not a bound for arbitrary output-mask sets, changed alphabets, nonlinear
operations, or a particular multiplication supplier. It establishes no new
selected frontier value or \(\kappa\).
