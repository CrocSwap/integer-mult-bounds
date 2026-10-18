# Removing the last exceptional bins by doubling PR3018

A literal 86-row journal moves 50 helper roles after interleaving two copies of
[PR3018](https://github.com/CrocSwap/integer-mult-bounds/pull/3018)'s allocation.
It removes all four exceptional `[4,8,9,9,9,9]@48` bins at `T=148` and strictly
lowers the complete conditional recursive moment. The certified endpoint rises
from

```text
[0.0017290342130642563095108, 0.0017290342130642563095109]
```

to

```text
[0.0017290353460708281979174, 0.0017290353460708281979175].
```

The gain is between `1.1330065718884065e-9` and `1.1330065718884067e-9`.
This closes about 73.01% of PR3018's remaining fractional-packing gap.
It is a finite allocation and moment improvement under the inherited supplier
model, not a new admitted multiplication exponent. The selected result is
unchanged.

The source words remain Marius-Paul Dumitrean's
[PR2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979), head
`be191346391661f4d35fc0d1508d0a6029572576`. The preceding journal is Nick Petalas'
PR3018 at `ca7113157d7c959fdfa9d7cd17ef92d3877070d0`.
The base is canonical main `d8e0f83f00191df62174b641e9fff055c357f641`, priority
revision 6. See [source pins](SOURCES.json), [task and limits](TASK.json),
[the journal](EXCHANGE.json), [the exact receipt](RESULT.json), and
[the canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18979815).

## The construction

First apply PR3018's journal to the pinned PR2979 fill. For each old call
`order[t] = [s,r]`, put `[s,r]` at new time `2t` and `[s,r+74]` at new time
`2t+1`. Copy every old role `[t,h,o,c,p,z]` to

```text
[2t,   h, o,    c, p, z]
[2t+1, h, o+74, c, p, z].
```

Provider dispatch follows the same rule. This preserves the stage order of each
replica. Every source event of a replica retains its order; half-open source
windows transform with its local-call times. The copies have distinct owner
names, so they have no cross-copy physical-family collisions. Each bin initially
contains exactly its old helper pattern. Thus the doubled complete profile is
exactly twice PR3018's profile, with the same normalized moment.

The journal then realizes this twelve-bin identity. The suffix is capacity;
each number inside brackets is one indivisible helper width.

```text
old                                      new
2 [7,8,8,9]@32                           4 [4,9,9,9]@32
2 [9,9]@32                               1 [7,7,9,9]@32
4 [9,9,9]@32                             2 [8,8,8,8]@32
4 [4,8,9,9,9,9]@48                       1 []@32
                                         4 [9,9,9,9,9]@48
```

Each side has eight capacity-32 bins, four capacity-48 bins, and the same count
of every helper width. Eighteen same-width augmenting paths realize the required
placements. Other bins can exchange equal-width roles while retaining their
patterns. The 86 edits comprise 50 location changes and 36 additional offset
changes for compaction. Every edit has an exact preimage; no solver is needed
for replay. The journal's `targets` identify the twelve changed-pattern bins.

The whole allocation has 1,332 calls, 543,456 roles and 298,368 bins. The finite
physical namespace is `132,608 + 408 + 8 + 91 + 2 = 133,117`. The 91 private
buffers are shared across sequential calls as in the source contract; their
names are not dropped from the invoice. This doubles the replica-dependent
storage, rather than claiming a free storage improvement.

The complete new paid profile is

```text
{1:3291372, 2:940392, 3:318948, 4:143856,
 5:27416, 8:10656, 32:1, 48:56380}.
```

It includes every local child and every idle remainder. In particular, the new
empty capacity-32 bin contributes one paid rank-32 child. The rank mass is
`9,633,024 = 65,088 * 148`. The retained owner's historical physical field uses
72 private buffers and therefore reports `133,098`; the exposed total above
charges the actual 91, just as PR2979 and PR3018 do.

## Exact improvement proof

Let `H_r(b) = r * (73/r)^b`. Relative to the doubled baseline, the complete
unnormalized moment changes by

```text
Delta(b) = 4 H1(b) + 4 H3(b) - 4 H5(b) - 2 H14(b) + H32(b).
```

Its signed rank mass is zero. Factor `Delta(b) = 73^b * f(b)`, where

```text
f(b) = 4 + 12*3^(-b) - 20*5^(-b) - 28*14^(-b) + 32*32^(-b).
```

We have `f(0)=0`. The positive atanh series, with
`z=(y-1)/(y+1)` and `1<=y<=2`, gives

```text
L(y) = 2*(z + z^3/3 + z^5/5)
L(y) <= log(y) <= L(y) + 2*z^7 / (7*(1-z^2)).
```

Range reduction by powers of two certifies the rational bounds

```text
1.09 < log(3) < 1.10
log(5) < 1.61
log(14) < 2.64
3.46 < log(32) < 3.47.
```

For every `0<=b<=1/100`, use `exp(-x)>=1-x` on the negative derivative
terms and `exp(-x)<=1` on the positive terms. Then

```text
f'(b) <= 20*(161/100) + 28*(66/25)
         - 12*(109/100)*(989/1000)
         - 32*(173/50)*(9653/10000)
       = -1711767/125000 < 0.
```

Therefore `Delta(b)<0` for every `0<b<=1/100`. This proof does not depend on
the unchanged local profile. Both roots lie inside this interval. The reused
PR3018 directed-integer engine encloses every logarithm, exponential and
bisection decision with explicit tails; it certifies both root brackets above.
The normalization is `73*896*T`, with `T=74` or `148` as appropriate.

The inherited fixed-inventory fractional cap is
`[0.001729035764875516181444, 0.0017290357648755161814441]`.
The new endpoint realizes at least `0.99999975778` of that cap, leaving
`[4.188046879835265e-10, 4.188046879835267e-10]`.
No integral optimality or independent recertification of that fractional optimum
is claimed.

## Reproduction and evidence

Python 3.12 and its standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/rank7-doubled-residual-exchange
```

The registered replay authenticates inputs, reconstructs PR3018 and its exact
doubling, applies the new journal, checks all placements and complete invoices,
runs the retained owner engine, certifies the strict root gain and analytic sign,
and rejects nine semantic controls. Four behavioral groups add a separate
sorted-interval owner/idle recount, target-pattern checks, source-byte rejection,
clock and owner-folding mutants, exact root values and the paid-empty-bin control.
The sorted recount shares the source-window table but uses neither occupancy
bit masks nor the predecessor owner checker. It is not a separately written
proof of the event-window derivation.

`geometry.py` is derived from PR3018's checker with only its explicit replica
and role capacity bounds extended and its bound comment updated. The two files
in `vendor/` are byte-exact PR3018 sources. Exact upstream blobs and original
and local hashes are retained in SOURCES.json. Reusing those checkers is not
claimed as independent implementation of their mathematics.

Discovery used bounded SciPy integer-pattern nominations, then a same-width
augmenting-path construction. The T74 nomination tied; it is not a proof that
T74 cannot improve. The T148 proposal was re-certified using literal integer
placements and rational bounds, not the solver's floating objective or status.
SciPy is unnecessary for verification.

## Scope and expansion decision

This result narrows the open larger-replica question in PR3018. It stops after
one strict finite gain; it does not start another search round. The boundary is
the source's ordered whole-helper widths, physical-family exclusions, source
windows and compact-prefix bins. The words, local operations, endpoint widths
and 91-buffer cleanup contract are unchanged. Every child and unused remainder
is charged by the finite accounting model.

Proved here are the doubled chronology, literal owner legality under that
boundary, complete finite rank bill and strict moment improvement. The source
word/native width contracts remain inherited. Full scalar/native/warp execution,
arbitrary-dirty restoration, physical backing/movement, precision/prefix/tape,
complete supplier/outer release and all-size/compiler implications are unrun for
this T148 allocation. Their unknown costs are not assigned zero.
[PR3021](https://github.com/CrocSwap/integer-mult-bounds/pull/3021), head
`217edac2ebfa6250536bd6df153de14901a69395`, now reports a fresh finite release
for the PR3015+3018 composition. That complementary T74 release does not bind
this new T148 allocation and is not validated here. There is no claim of a new
admitted supplier or selected kappa.

## Open next questions

1. Can the source's fresh native/admission/outer chain accept this exact T148
   order and journal-derived fill? This is the next test that can promote the
   finite gain to a conditional supplier improvement. Start by exporting the
   `doubled` and `apply` outputs, rederive all T-dependent physical/prefix
   constants, and retain the paid rank-32 child. The source environment and
   inherited physical/all-size obligations remain blockers. Old receipts do not
   bind these new artifacts.
2. Does Jeremy Kothe's PR3015 restore edit compose with this allocation? Its
   reported unchanged widths suggest a separate compatibility test, not a free
   numerical addition. First compare both literal width vectors and local bills,
   then replay the changed words and the full invoice. PR3021 is now a public
   starting point for that composition. Its edit and release are not checked
   here and cannot certify the different T148 artifacts without a new replay.

## Credit and implementation choices

Nick Petalas contributes the doubled-replica exchange journal and sign proof.
PR3018 supplies the predecessor journal and interval/owner checks. Credit
Marius-Paul Dumitrean for PR2979, Mason Hale, Jeremy Kothe and Jeremy Diviney for
the word/frame/extraction lineage, Yiyang Lu for chronological flow and
realization, Tekalign for owner-window conventions, Ross Richardson for
PR2987/3010's complementary packing audits, Dugongue, icekylinx, themilkman216
and the retained geometry/native/owner contributors. Apache-2.0. Substantial
automated assistance was used; no independent human or formal-kernel review is
claimed.

Build the Lever led to a replayable journal rather than a solver-only claim.
Prove It Works required complete literal geometry and paid-moment checks before
keeping the candidate. Power of Ten led to bounded replicas, journal sizes,
replay loops and checks active under optimization. Python's managed allocations
are a documented deviation from fixed allocation, bounded by 148 replicas,
1,332 calls, 543,456 roles and 298,368 bins. The retained comparison module is
executed dynamically only after its source digest passes; its target is fixed.
It retains its old coding style without an unrelated rewrite. Rejection
callbacks have fixed synchronous targets. Warnings are errors in validation;
Ruff checks correctness, imports and modernization. Repository-wide typing or
style enforcement is not introduced.
