# FANIN4 stream identity and cost

## Model

Let L be a positive integer. There are four read-only source tapes containing
x0,...,x3 in F2^L and one writable target tape z in F2^L. The five tapes are
aligned in one fixed coefficient order and begin at head position zero.
One lane transition reads a source bit and advances that tape by one cell.
The target lane transition reads z[i], writes its updated bit, and advances
the target by one cell. A complete call returns every participating head to
zero. Reads, writes, head steps, bit XORs, call records, and reference fields
are charged separately. There is no scratch or frame conversion.

For this package, L=4 and the coefficient space is F2[C2^2]. All source maps
are the identity, so the connector request is exactly z <- z + sum_j xj.
The + symbol is coefficientwise addition in characteristic two.

## Correctness

The singleton schedule applies z[i] <- z[i] + xj[i] for j=0,1,2,3 in four
complete passes. Since the xj are read-only, their values do not change.
The final target lane is z[i] + x0[i] + x1[i] + x2[i] + x3[i].

The fused schedule scans lane i once across all five tapes. It reads z[i] and
each xj[i], then applies four binary XOR gates to z[i] before advancing. Thus
the same final lane value is obtained. Every source is unchanged. Repeating
the fused map adds the same unchanged sum to z a second time and restores the
original target. All five heads return by L reverse head steps.

This proves the map for arbitrary dirty sources and target and every L. The
exhaustive L=4 verifier checks 2^(5L)=1,048,576 joint states. The verifier
also checks the inverse, all head positions, the source values, the exact
resource ledgers, and failure controls.

## Resource accounting

For s sources, L coefficients, and one ordinary source-update record per
singleton call:

| Resource | Singleton sequence | Fused scan |
|---|---:|---:|
| Reads | 2sL | (s+1)L |
| Writes | sL | L |
| XORs | sL | sL |
| Forward head steps | 2sL | (s+1)L |
| Return head steps | 2sL | (s+1)L |
| Call records | s | 1 |
| Source-reference fields | s | s |
| Target-reference fields | s | 1 |
| Scratch | 0 | 0 |
| Frame transitions | 0 | 0 |

For s=4, L=4 these evaluate to reads 32/20, writes 16/4, XORs 16/16,
head moves 64/40, records 4/1, source-reference fields 4/4, target-reference
fields 4/1.

Let r,w,h,p,d1,ds,t be nonnegative prices for one data read, one data write,
one head step, one XOR, one singleton record, one fused FANIN-s record, and
one target-reference field. The singleton-minus-fused cost is

    (s-1)L*r + (s-1)L*w + 2(s-1)L*h + s*d1 - ds + (s-1)t.

The XOR and source-reference terms cancel. If records have uniform price
d1=ds=d, this simplifies to

    (s-1)(L*r + L*w + 2L*h + d + t).

Any one-time opcode-table or source-frame conversion expense F is subtracted
from the saving. In the fixed aligned-frame stream instance F=0; an external
supplier must price its own instruction encoding and frame conversion before
claiming a net gain.

## Scope boundary

The construction realizes one identity-map FANIN4 update in a fixed aligned
coefficient frame. It does not establish that a current recursive supplier
emits these four source roles in the same frame, that the operation can be
used in a full mask-cover word at lower total cost, or that any global
multiplication exponent improves. The abstract query/addition limits from PR
#2249 remain intact because all four source XORs are charged.
