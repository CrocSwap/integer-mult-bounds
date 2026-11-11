# Exact four-source uniform paid-clean tariff

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Use Ali Romman's [PR #5372](https://github.com/CrocSwap/integer-mult-bounds/pull/5372)
paid clean-row contract, extending Cinna Davis's #1954 and the connector lineage
of Ross Richardson's #943. There are four immutable sources x_j, arbitrary
incoming outputs y_m for all fifteen nonzero four-bit masks, and one paid owned
row c. Allocate and zero c once. Subsequently allow only complete calls

```
B_j: c   += B_j x_j                 j = 0,1,2,3
A_m: y_m += A_m c                   m = 1,...,15.
```

The spaces are nonzero finite-dimensional F2 vector spaces with compatible
linear maps. Each complete call satisfies its own scratch/head restoration
contract. The original dirty connector is untouched. No output is read, no
source changes, and no observer inspects intermediate outputs. At exit c=0 and

```
y_m(out) = y_m(in) + A_m sum_{j in m} B_j x_j.
```

A finite word must work for every choice of maps and data. It may depend on
prices, but cannot rely on a particular map identity. Further zeroing, another
row, source feedback, output feedback or a fused map call changes the contract.

Let each complete source call have uniform price b>0 and each complete output
call uniform price a>0. The new exact map-call optimum is

```
OPT(b,a) = min(8b + 23a, 16b + 15a).
```

The eight-source-call branch is optimal when b>=a; the sixteen-source-call
branch is optimal when b<=a. They tie at b=a. The componentwise-minimal
**total-count pairs** (source calls L, readouts R) are exactly

```
(8,23), (10,21), (12,19), (14,17), (16,15).
```

This is a frontier of two aggregate counts, not a classification of the nineteen
individual call counts or the full heterogeneous-price question in #6254.
Add the common allocation, zeroing, release and admission bill. Constant uniform
per-call charges can be included in a and b; word-dependent physical costs need
a separate analysis. No physical supplier or new kappa follows from this result.

## Lower bound for every finite word

The source-mask reduction and the one-versus-two-readout observation are from
#5372. We apply them with four sources and show attainment of their sharp
tradeoff, including the previously uncovered b>a region.

Specialize all maps to identity on a common scalar coordinate. Independent
source bits then make c's formal coefficient a vertex p of F2^4. Each B_j call
toggles coordinate j, so the source word is a closed cube walk from zero. Every
source must occur to supply its singleton output. Its occurrence count is even
because c is restored for arbitrary independent inputs. Consequently L is even
and L>=8. This argument applies to any unbounded finite word, including words
that revisit vertices or read an output more than twice.

Let V be the set of visited vertices and k=|V|-1 its number of nonzero vertices.
The initial and final vertices both equal zero, so k<=min(L-1,15). Every output
needs a readout. A target m outside V needs at least two, since one readout adds
only one visited mask. Thus

```
R >= k + 2(15-k) = 30-k >= max(31-L,15).
```

For 8<=L<=16 this gives

```
bL + aR >= 31a + (b-a)L.
```

The minimum of this affine expression on [8,16] is the smaller of its endpoint
values, 8b+23a and 16b+15a. For L>=16, positivity and R>=15 give the lower bound
16b+15a directly. This proves the displayed lower bound for all positive real
prices and all finite legal words. The specialization lower-bounds the generic
contract; it does not lower-bound a particular degenerate map assignment.

## Attainment for arbitrary compatible maps

Use the source word

```
0,1,0,2,1,3,2,3
```

where a label j means one B_j call. Its prefix walk is

```
0,1,3,2,6,4,12,8,0.
```

There are seven distinct nonzero visited vertices. Read their seven matching
outputs once. Read each of the other eight outputs at the following pair of
visited vertices:

| Target | Readout vertices |
|---|---|
| 5 | 1,4 |
| 7 | 1,6 |
| 9 | 1,8 |
| 10 | 2,8 |
| 11 | 3,8 |
| 13 | 1,12 |
| 14 | 2,12 |
| 15 | 3,12 |

Each pair XORs to its target, so there are 7+2*8=23 readouts. At prefix p,
induction on the actual source calls gives c_p=sum_{j in p} B_j x_j. Linearity
then gives A_m c_u + A_m c_v = A_m sum_{j in m} B_j x_j whenever u XOR v=m.
Schedule each readout at its chosen vertex's first arrival. Outputs are never
read, so these writes do not affect later source operations. The owned row
returns to zero; arbitrary initial outputs, sources and original dirty state
have the required endpoint. No inversion, commutation, square dimension or
nonsingularity of any map is needed.

The sixteen-call attainer is #5372's classical reflected Gray cycle. It visits
every nonzero mask once and reads each output once, giving (16,15). Neither the
Gray cycle nor its clean-row use is claimed as new.

For completeness, these source words attain each intermediate total-count pair:

| L | Source word | R |
|---|---|---|
| 8 | 01021323 | 23 |
| 10 | 0102010323 | 21 |
| 12 | 010201030203 | 19 |
| 14 | 01020103010213 | 17 |
| 16 | 0102010301020103 | 15 |

Each is a simple closed walk with L-1 nonzero vertices and contains the seven
nonzero vertices of the eight-call attainer. Therefore every omitted target
still has a two-vertex representation. Read visited targets once and omitted
targets twice to obtain R=31-L. These finite walk properties can also be checked
directly from the displayed words. The code generates the literal map calls.

The lower bound covers every even L>=8, and any L>16 pair is dominated by
(16,15). The five attained pairs therefore form the full aggregate Pareto
frontier. Its intermediate pairs tie only at a=b; they are not uniquely exposed
by a strictly positive uniform price pair. No claim is made that the eight-call
cube word itself is a new Gray-code or universal dirty-connector construction.
The new result is this exact paid-clean four-source tariff and its count frontier.

## Finite corroboration

The universal lower bound above supplies the real-price and unbounded-word
quantifiers. The self-contained checker additionally enumerates source-walk
states (position, visited set) with a shortest possible completion of at most
sixteen calls. Zero is always visited, giving at most 16*2^15 states. Breadth-first
search merges only identical states, whose subsequent possibilities agree.
A state at length l and position p is pruned only when l+weight(p)>16, since
weight(p) is the exact minimum number of cube edges returning p to zero.

For every closed visited set, the checker independently computes minimum
readouts by both a group-graph breadth-first search and a 0/1 subset-XOR dynamic
program. Repeated use of the same visited mask cancels over F2, so subset-XOR
suffices. Each output can use its own optimal subset because outputs are never
read. A visited set's shortest source walk and these readouts can be combined by
placing writes at the first corresponding visits. The Gray attainer dominates
all words longer than sixteen under positive uniform prices. Thus this finite
reduction represents every potentially optimal word without a hidden cutoff.

The generated receipt reports 190231 walk states, 20769 closed visited sets,
20440 spanning closed visited sets, the five minimal pairs, 147 exact price
comparisons, 4880 literal rectangular-map executions and 174 rejecting controls.
The rectangular executions use 3-by-2 source maps, 2-by-3 output maps, sixteen
map fixtures including zero maps, every one of 44 incoming basis bits, zero and
sixteen mixed input states. Counts are executions, not exhaustive enumeration
of all maps. Deleting any emitted call from the five schedules is rejected;
four malformed source words are also rejected. All checks survive -O.

## Implementation limits

The verifier has no recursion, subprocesses, dynamic code generation or file
writes. All loops have fixed finite domains. The walk queue/distance map hold
at most 16*2^15 states, the visited-set domain is at most 2^15, each additive
search has sixteen vertices, and every source word has at most sixteen labels.
Functions stay below sixty physical lines. Explicit exceptions preserve
invariants under optimization. The receipt hashes package files and verifies
both live predecessor input hashes; historical source validation is separate.

Power of Ten rule 3 deviation: CPython and its standard library allocate during
these finite offline checks. The fixed domains above bound live collections;
fixed storage after initialization is not claimed. Rule 10 limitation: no
static type checker or linter is required by the standard-library environment.
Warning-strict syntax/AST inspection and normal/optimized registered replay are
the available diagnostics. No shared build configuration changes.

Physical map lowering, provisioning, routing, descriptors, ownership admission,
precision/tape, recursive hosting and the full signed supplier bill remain open.
The five selected assumptions are unchanged. No predecessor scientific replay,
selected cold replay, Lean, Docker, independent human review, formal proof-kernel
acceptance or complete multiplication theorem is claimed.
