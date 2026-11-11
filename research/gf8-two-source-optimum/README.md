# Exact 140-call two-source GF(8) connector

This contribution was produced by Nick Petalas. It is a scoped mathematical
proof with a finite explicit construction. The two-source scalar-update dirty
connector over GF(8), requesting all 63 nonzero coefficient pairs, has exact
unit complete-call optimum **140**. The lower bound allows arbitrary readout
counts, rather than assuming paired readouts. The explicit axis comparator
uses 142 calls. No supplier admission or new kappa is claimed.

The new step groups Aaron Wang's PR2128 binary walk into two field coordinates,
then transfers the existing all-word tariff argument of Tairitsu-Aya PR2156
and Cinna Davis PR2249 to this field-linear contract. The walk and that counting
argument are credited predecessor work. Unpaidmoon's PR4651 exclusion of
twelve- and thirteen-point difference bases is a cited mathematical dependency,
not a result reverified by this package.

## Contract

Write K=GF(8)=F2[t]/(t^3+t+1). An integer a from 0 through 7 encodes the
coefficients of 1,t,t^2 in its three bits. There are two immutable sources
x0,x1, one borrowed arbitrarily dirty connector z, and 63 distinct arbitrarily
dirty outputs y_v, for v=(u,w) in K^2 other than zero. For arbitrary compatible
K-linear maps B0,B1,A_v, the requested endpoint is

```text
y_v += A_v(u B0 x0 + w B1 x1)
x0, x1 and z unchanged
```

Only these atomic complete calls are allowed:

```text
S(j,a): z += a Bj xj       j in {0,1}, a in K minus {0}
R(v):   y_v += A_v z
```

Calls preserve every other row and restore their private scratch and required
entry/exit heads. Each scaled S call has its own complete price, including
scalar preparation and multiplication. Readouts have coefficient one. The word
is independent of data and map entries. Outputs cannot be read or used as
workspace. There is no connector scaling, source mutation, additional root,
direct A_v Bj call, free conversion or combined readout. The 140 optimum assigns
unit price to every complete call. Unequal physical prices are separate.

This extends Cinna Davis's PR2266 GF(4) scalar-source interface to a different
field and full coefficient demand. It is not the binary six-independent-source
DUO contract: the three basis components of each field source share one Bj.

## Construction and arbitrary-dirt identity

Interpret a six-bit mask as its low three bits u and high three bits w. The
source steps and nonterminal prefixes are Aaron Wang's PR2128 word:

```text
steps     2 16  8 16  1  4 48  4  3  4 32  8  4 16
prefixes  0  2 18 26 10 11 15 63 59 56 60 28 20 16
```

Every step lies wholly in one three-bit group, including 3 and 48. Thus every
step is one legal S(j,a), rather than a bundle of distinct map applications.
There are seven calls to each Bj. The final prefix is zero. The 91 unordered
pairs of distinct nonterminal prefixes contain all 63 nonzero differences.
The verifier enumerates those 91 pairs and emits the first boundary pair for
each mask in its generated receipt.

At prefix q=(q0,q1), the connector is exactly
`z_initial + q0 B0 x0 + q1 B1 x1`. For each v choose prefix boundaries s,t
with q_s+q_t=v, and call R(v) at both. Their incoming dirt terms cancel in
characteristic two. Linearity leaves exactly the specified output update,
with A_v on the left of each Bj. Different readouts preserve z and have
distinct targets, so all pairs can be interleaved in chronological boundary
order. This proves the identity for every row length and every allowed map,
including singular and noncommuting maps. It uses fourteen source calls and
126 readouts, totaling 140. Each elementary update is an involution; reversing
the program restores the full initial state.

For comparison, traverse the reflected three-bit Gray cycle on the first
coordinate, then on the second:

```text
source-0 coefficients  1 2 1 4 1 2 1 4
source-1 coefficients  1 2 1 4 1 2 1 4
```

Its prefixes contain both complete coordinate axes. Every (u,w) is a difference
of two axis points, giving the same 126 paired readouts with sixteen source
calls and 142 total calls. The new verifier constructs and checks this
comparator directly, without running a predecessor program.

## All-word lower bound

Specialize to scalar identity maps and independently variable x0,x1,z_initial.
Any correct word must have zero final source prefix and an even number of
readouts for every output. Each nonzero output needs at least two readouts.
With exactly two, its requested vector is a difference of two source prefixes.
A vector absent from that difference set therefore requires at least four.
This reasoning allows repeated boundary readouts and arbitrarily many calls.

Let b be the source-call count. A closed b-step word has at most b distinct
nonterminal prefixes. Let m be the number of nonzero vectors absent from their
pairwise differences. Every word costs at least `b + 126 + 2m`.

- If b>=14, the bound is already 140.
- If b=12 or 13, PR4651's cited theorem says no set of at most thirteen
  points covers K^2=F2^6 by differences. A smaller set can be enlarged, so the
  theorem covers repeated-prefix paths as well. Hence m>=1. The bills are
  at least 140 and 141, respectively.
- If 0<=b<=11, there are at most b(b-1)/2 nonzero differences. Thus
  `b+126+2m >= b+126+2(63-b(b-1)/2)`. The minimum of these twelve integer
  expressions is 153, attained at b=11.

This is the PR2156/PR2249 counting argument applied to the additive coefficient
group of the field-linear contract. The construction attains 140. The claim depends
on the cited PR4651 set exclusion. Its census and historical suites are not
executed here. Finite construction checks do not independently certify that
dependency or the universal written argument.

## Complete price and storage boundary

Let c_(j,a) be the complete scaled source-call price and r_v the complete
readout price. Let I pay admission and program construction, P pay external
coefficient preparation, and D pay instruction storage/access/dispatch. The
displayed construction has the explicit bill

```text
C = I + P + D
  + c_(0,1) + c_(0,2) + c_(0,3) + 4 c_(0,4)
  + 2 c_(1,1) + 3 c_(1,2) + c_(1,4) + c_(1,6)
  + 2 sum_(v != 0) r_v.
```

No nonunit scalar is free. A tag bit, one source bit and three coefficient
bits encode each S; a tag bit and six target bits encode each R. The actual
140-event stream needs 952 bits, versus 962 for the axis stream, before
framing or external interpreter storage. Boundary order is encoded by the
stream. No runtime pair-lookup oracle is assumed. There are 66 length-L data
rows, or 198L field-data bits, plus each child's separately charged private
scratch and control storage. No extra full row is introduced.

At equal complete call prices the construction saves two calls. It need not
beat the axis word for unequal c_(j,a). Coefficient acquisition, physical
scaled-map services, frames, stock, precision and tape costs are unknown at a
selected supplier. There is no identified real consumer or complete supplier
invoice. The family decision is to finish this local result and stop.

## Reproduction and coverage

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gf8-two-source-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/gf8-two-source-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gf8-two-source-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gf8-two-source-optimum --check-source-history --check-modes
```

An installed CPython 3.12 can replace that interpreter path. The verifier writes
no files. It prints a generated JSON receipt bound to all five package hashes,
the full boundary-pair certificate and the marker

```text
PASS_GF8_TWO_SOURCE_OPTIMUM calls=140 sources=14 readouts=126 dense=399 controls=283 cited_lower_bound=PR4651
```

Checks include all 64 products under two GF(8) multiplication implementations,
1,024 associativity/distributivity instances, seven inverse counts, free
noncommutative map endpoints in both directions and the axis comparator. Dense
replay uses separate polynomial arithmetic, all 396 basis columns and three
mixed dirty states across dimensions one, two and three. It checks forward and
inverse endpoints for all 399 inputs. All 140 call omissions, fourteen changed
source coefficients, 126 changed readout destinations and three malformed
source words must be rejected. Checks remain active under Python -O.

The code has no recursion or subprocesses. Every loop is bounded by the fixed
field, at most 142 calls, 66 roles, matrix dimension at most three or five
package files of at most 200 KB. Every function is below sixty lines.
Python-managed allocation is a Power of Ten rule 3 deviation. Symbolic live
storage has at most four terms per output; dense row storage has at most 198
field entries per state. The declared limits and sixty-second replay timeout
bound this offline verifier. Fixed-capacity storage should be reconsidered if
it becomes an online service. Warning-strict normal and optimized execution
are the available diagnostics; no project Python linter/type checker is
configured for this package.

## Sources, scope and credit

Produced by Nick Petalas. Aaron Wang / navinor PR2128 supplies the fourteen-step
walk. Tairitsu-Aya PR2156 and Cinna Davis PR2249 supply the existing all-readout
counting argument in the binary-source model. Cinna Davis / 1337isnot1337
PR2266 supplies the paid single-source scalar
interface over GF(4). Unpaidmoon PR4651 supplies the cited difference-basis
exclusion and credits Volodymyr Gavrylkiv for the known set-level value. Ross
Richardson PR934/PR943 supplies the dirty-connector and prefix-readout lineage;
Aaron Wang's DUO work retains that lineage. All predecessor credit remains
unchanged. The new field grouping, exact field-linear tariff consequence, price
expression and verifier are the contribution here; the underlying binary walk,
counting argument and difference-basis value are not claimed as new.

SOURCES.json pins the four predecessor READMEs, catalogue and selected-record
context at main e54523517d0f03e58352e647c403a5af3e525a57. The selected result is
#7000, conditional kappa 0.00363005817 under five retained assumptions. The
catalogue's revision-8 assessment predates that selection. This package changes
none of those inputs. TASK.json records the changed card scope and advance
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19540626).

The card's historical orientation control passed with 945 pairings, maximum
coverage 31 and 74 calls. It is not the contribution or a dependency replay.
No other predecessor scientific suite, proof-kernel build, independent human review,
native/supplier replay, physical tape implementation, selected cold replay or
complete multiplication theorem is supplied. Hosted CI is separate from local
checks. Independent human and formal proof-kernel review are unclaimed.
Apache-2.0.

## Open next questions

- Does a source-pinned recursive caller expose this GF(8)-linear boundary at a
  favorable full invoice? First identify the maps and price every scaled source
  event, readout, admission, preparation, dispatch and dirty return. No such
  caller or scalar service is known here.
- What is the optimum with unequal complete scaled-event prices? Begin with a
  real tariff and the displayed fourteen-step and sixteen-step words. The
  unit-call theorem does not settle this comparison.

The questions, relevance, first steps and blockers are also in TASK.json.
