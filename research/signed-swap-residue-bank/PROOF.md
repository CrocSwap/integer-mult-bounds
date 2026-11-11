# A smaller forward bank by signed exchange

## Contract and cited input

Let `1 <= a,b <= 12`. The caller supplies both residues before drawing coins.
It requests two independent Bernoulli outputs with parameters `a/13,b/13`.
Coins are independent fair bits, with no free initial random state.

zxv's [#6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072)
supplies the following input theorem. Its fixed-parameter dyadic decision graph
returns labels `00,01,10,11` with weights

```
w(a,b) = ((13-a)(13-b), (13-a)b, a(13-b), ab), denominator 169.
```

At every depth `k`, the number of completed label-`i` binary prefixes is
`floor(2^k w_i/169)`. This saturates the fair-prefix lower bound and attains the
optimal expected draw count. Its periodic representation has 312 pending states
and four terminal labels, hence 624 nine-bit targets, or 702 bytes. These are
cited predecessor results. The present verification does not rerun its law,
mean catalogue or optimality verifier.

The new contract permits changing which output a particular coin tape returns.
It retains the requested joint law and, as shown below, the original stopping
time on every coin tape. It is a forward logical contract only.

## Theorem

All 144 requested pairs can be served from 21 unchanged canonical source tables,
a 144-byte selector and fixed output logic. Their transition and selector payload
is exactly 14,886 bytes. The resulting sampler has the requested independent
product law, the cited optimal expected draw count, and the original first
stopping depth on every finite or infinite coin tape.

This is a constructive upper bound. No global minimum ROM size, physical tariff
or reversible implementation is asserted.

## Canonicalization and the output map

Put `c=min(a,13-a)`, `d=min(b,13-b)`, and let `u=min(c,d)`, `v=max(c,d)`.
The representatives are exactly `(u,v)` with `1 <= u <= v <= 6`. There are
`6+5+4+3+2+1=21`. Independent complements give four pairs on each diagonal
representative; complement and exchange give eight on each off-diagonal one.
Thus the orbit sizes are six fours and fifteen eights, totaling 144 pairs.
These are precisely the orbits under these specified operations, not a minimum
number of tables under arbitrary sampler redesigns.

Draw `(U,V)` from the canonical `(u,v)` source table. Exchange its coordinates
when `c>d`, then complement its first coordinate when `a>6` and its second when
`b>6`. Call this bijection `F`. Independent complements and exchange preserve
independence and give the two required parameters. More explicitly,

```
w(a,b)[F(i)] = w(u,v)[i]  for i=0,1,2,3.
```

For each depth `k`, relabelled completed prefix counts therefore equal
`floor(2^k w(a,b)[j]/169)` for every requested label `j`. This proves the full
joint law and transfers the cited depth-optimal expected-bit bound. It uses no
floating point, finite draw cap or assumption about an actual inverse caller.

## Pointwise stopping times

Permuting the four weights preserves their residue sum at every binary phase.
It therefore preserves the pending-node counts `n_k` and the total number `D_k`
of terminal children at the next level. The literal source rule orders all
terminal children before the pending children. At node `j` with coin `t`, put
`l=2j+t`. If `l<D_k`, the path stops; otherwise its next pending index is
`l-D_k`. Both decisions depend only on `D_k`, not on the ordering of labels.

The canonical and requested source graphs consequently have the same phase/node
enumeration and pending transition on every coin. Induction preserves every
first stopping time, including nontermination and phase wrapping. The terminal
labels themselves need not agree. For example, on the seven-coin tape `1111100`
the requested `(12,2)` source table returns `01`; the canonical `(1,2)` table
with its first bit complemented returns `10`. Both stop at depth seven.
Thus this construction does not preserve every original coin-to-label function.

## Packed representation and exact inventory

The first 144 bytes, in `(a-1)*12+b-1` order, contain `8*i+flags`. Here `i` is
the canonical table index `0..20`; flag bits 2,1,0 request exchange, first
complement and second complement. All codes are below 168. Each subsequent
702-byte table stores its 624 targets consecutively, least significant bit
first, nine bits each. Targets `0..311` are pending states and `312..315` are
terminal labels. Every source root is state zero, so no entry-pointer table
or representative-name table is needed at runtime.

The total is `144 + 21*624*9/8 = 14,886` bytes. The bank retains an eight-bit
selector and a nine-bit local state, at most 17 logical control bits. The
selector is retained through terminal relabelling. Random tape, cursor, output
storage, code, headers and physical access are outside this payload count.

The constructor emits exactly those bytes. The checker checks all 144 selectors
against the four requested integer weights, the eight output permutations, and
every selector/state/coin lookup, `144*312*2=89,856` checks. Terminating and
unfinished fixtures exercise the new runtime; they do not re-establish the
predecessor's probability theorem. The lookup identity lifts by induction to
every finite tape and hence to pointwise first-stop behavior.

## Limits and code constraints

The finite `run` helper accepts at most 4096 supplied coins. It is an executable
finite-prefix interpreter, not a cap on the mathematical sampler. Longer paths
follow from the transition proof. Worst-case stopping time stays unbounded.
Restored coins would remain correlated with a retained output. No reversal,
freshness restoration, physical selector/lookup or native/caller bill follows.
No selected assumption is discharged and no new kappa is claimed.

The new code is nonrecursive. Constructor loops have at most 21 tables, 312
states and two coins; validation has 144 selectors and the same state bound.
Fixture traversal visits at most 312 states per table. Every new function is
below 60 physical lines. ValueError contracts remain active under `-O`.

Power-of-Ten deviations are confined to the verifier. Rule 3 cannot prohibit
Python's managed allocations. Source tables, fixtures and all working
collections have the fixed finite bounds above; byte output capacity is fixed
before packing. Python object overhead is not a physical storage certificate.
Rule 8 uses one dynamic load because the pinned predecessor is a standalone
script in a directory whose name is not an ordinary import identifier. Exactly
the SHA256-authenticated source bytes are compiled, bypassing bytecode caches;
only its `make` constructor is called. Its CLI verifier is never called. If the
predecessor later exposes a stable importable constructor, a new package can use
that interface. Rule 9's indirect calls are that single fixed constructor and
the finite negative-control lambdas; no external callback is accepted. Normal
and optimized warning-strict execution, static compilation and the finite
controls check these boundaries. No project-wide diagnostic change is needed.
