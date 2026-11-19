# Exact entry from denominator 52 to the paired arithmetic core

## Source and exact scope

JoyboyBrian's PR6096 proves that modes zero and one of the retained
112-owner inverse reach all 2,704 floor-residue pairs `(a,b)` modulo 52,
already with owner coordinates in {-1,0,1}. Its actual kernel collects all
eight mode numerators before rounding. This package uses that source-bound
nonadaptive arithmetic window. It does not repeat the kernel proof or its
physical accounting.

For `0 <= a,b < 52`, consider the ordered joint dyadic decision graph with
weights

```text
w = ((52-a)(52-b), (52-a)b, a(52-b), ab),    sum(w) = 2704 = 16*169.
```

The order is 00,01,10,11. At each depth, the first child indices become
leaves in that order, as in zxv's PR6072 construction. The question is an
exact interface question: after four coins, can the complete unfinished
pool use the existing PR7755 arithmetic core with one fixed pair
`1 <= c,d <= 12`, one unit phase modulo 169, unchanged label order and
unchanged live-node indices?

Exactly **2,304 pairs** can do so. These are precisely the pairs for which
neither a nor b is divisible by 13. Each has a unique core pair and phase.
The 2,304 inputs use 1,560 distinct entry recipes; uniqueness is per input,
not a claim that different inputs always require different recipes.

| Actual residue class | Pairs | Result after at most four coins |
| --- | ---: | --- |
| Neither residue divisible by 13 | 2,304 | Unique entry to the existing nonzero-pair core |
| One residue zero, the other not divisible by 13 | 96 | Endpoint tail; outside that core contract |
| One residue in {13,26,39}, the other not divisible by 13 | 288 | Four nonzero multiples of 13; no such core entry |
| Both residues in {0,13,26,39} | 16 | No unfinished tail |

This classifies the stated complete-pool interface. It does not exclude
different controllers, output maps, endpoint dispatch or state recodings.
No physical prefix circuit, gate bill for entry, complete supplier or new
kappa is supplied.

## Four-coin reduction

Put `r_i = w_i mod169`, with representatives in [0,168]. At depth four,
the completed label-i prefixes number `floor(w_i/169)`. The remaining
number is `n = sum(r_i)/169`, an integer from zero through three. Each
remaining live index corresponds to one four-coin prefix, in order.
An earlier leaf consumes fewer than four coins. Pair (0,0) returns 00
without a coin.

For every later depth, the integer part of `w_i/169` cancels from the
binary digit difference. The tail therefore has the same four digit
streams as the residues r over denominator 169. Its live count at tail
depth t is `sum(2^t*r_i mod169)/169`. This is a complete pool with n entry
nodes; it must not be replaced by a fresh single-root sample without a
proof. Conditioning on unfinished prefixes can change the output law.

## Formula and uniqueness

Suppose 13 divides neither a nor b. Inverses below use the indicated
modulus. Set

```text
c = 10*a mod13,       d = 10*b mod13,       1 <= c,d <= 12,
theta = a*b*(c*d)^(-1) mod169.
```

Here 10 is the inverse of 4 modulo 13. Both c and d are nonzero, so theta
is a unit modulo 169. It satisfies `theta = 16 mod13`. For the core
weights `v=((13-c)(13-d),(13-c)d,c(13-d),cd)`, we have

```text
theta*v11 = ab                         (mod169),
theta*(v10+v11) = 13*theta*c = 52*a     (mod169),
theta*(v01+v11) = 13*theta*d = 52*b     (mod169).
```

The total weight is zero modulo 169 on both sides. These four identities
give `theta*v_i = w_i mod169` for every label. Doubling preserves them at
every later step. The leaf labels, live indices and next phase therefore
agree on every ordered coin suffix.

To prove uniqueness, any such embedding must have row and column sums
`theta*c = 4a mod13` and `theta*d = 4b mod13`, while its last entry gives
`theta*c*d = ab mod13`. All factors are nonzero. Divide the product of the
first two equations by the third to obtain `theta = 16 mod13`. This fixes
c and d as above. The last entry then fixes theta modulo 169.

The number 2 generates every unit modulo 169: its 156 powers are distinct and
close at one. The verifier checks this complete orbit. Thus every theta
in the formula is a reachable source phase. Its phase index is 4 modulo
12. Exactly thirteen phase offsets occur in the census. The complete
source live pool at that phase has n nodes, so every entry node lies in
the unchanged arithmetic circuit's verified domain.

## The other 400 pairs

Every component of a nonzero-pair core weight is a unit modulo 13. A unit
phase preserves this property. If both original residues are divisible
by 13, all four w values are divisible by 169, and the tail is empty.
If exactly one residue is zero, the nonempty tail has two zero components.
If exactly one residue is a nonzero multiple of 13, all four tail values
are nonzero multiples of 13. None of these nonempty tails can equal a
unit-phase nonzero-pair core signature.

The counts are `48^2`, `2*48`, `2*3*48` and `4^2`. These are exact input
classes, not frequencies for actual inverse inputs. The endpoint cases
may use a different dispatch. The mixed cases may use a different graph.
Neither option is priced or excluded here.

## Entry has its own inverse boundary

Let U be the number of unfinished prefixes at depth three, and n the
number at depth four. There are `D = 2U-n` leaf children in the fourth
step. For a continuing child j and its retained coin u, the entry-specific
inverse is

```text
old_node = (j + D - u)/2,       u = (j+D) mod2.
```

This formula is checked for all 4,428 eligible entry nodes against literal
prefixes. It is not in general the core's cyclic predecessor formula.

The actual source witness `(a,b)=(1,1)` shows the difference. Its first four
weights are `(2601,51,51,1)` and its tail is `(66,51,51,1)`. The unique
core pair is `(10,10)`, at phase 120, whose source phase index is 136.
Prefix 1111 reaches entry node zero. Its fourth step starts from phase
eight, node zero and coin one. But the same core output, phase 120 and
node zero with coin one, has the cyclic predecessor phase 60 and node one.
The retained core's inverse recovers that cyclic predecessor.

Consequently, an autonomous transition that merges these two distinct
input packets into the same output packet while clearing all workspace
cannot be reversible. This is a scoped collision, not an impossibility
of a reversible sampler. A separate entry/return protocol can use the
formula above and distinguish the boundary through its existing counter,
owned marker or other stated control. No new per-step history or minimum
number of additional bits is proved. The source's inside-tail cleanup
does not, by itself, pay or validate this boundary protocol.

## Complete evidence

The classifier checks all 2,704 actual source realizations from the pinned
mode columns. A second inventory reads every leaf emitted by all 144
unchanged source graphs. It reconstructs each phase's four residues from
the complete 156-digit repeating binary words. This gives 22,464 distinct
core phase signatures without using the new embedding formula. Exhaustive
lookup agrees with that formula and with every rejection class.

All 43,264 literal four-coin prefixes have the exact completed label counts
and ordered unfinished nodes. All 1,437,696 eligible tail edges over one
complete shifted period agree with an independent denominator-2704
integer-floor calculation. The checked algebra extends this agreement to
every later period. The full unchanged PR7755 verifier runs as a separate
process, including its 89,856 forward/inverse circuit edges and its retained
fixed-pair verifier. The entry collision, phase-one-reset control and four
invalid residue controls are explicit.

The source-domain kernel's complete fixture suite and the selected cold
replay were not run. Source construction, interface arithmetic and circuit
replay are separate evidence. No physical preparation, parameter loading,
wire/tape access, output retention, stopping storage, conditional freshness
or complete native invoice is supplied. All five framework assumptions
remain unchanged. Independent human and formal-kernel acceptance are unclaimed.
