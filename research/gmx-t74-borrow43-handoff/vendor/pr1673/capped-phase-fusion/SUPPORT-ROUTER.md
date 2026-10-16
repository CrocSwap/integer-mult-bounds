# Coordinate routing measured by moved support

This is a conditional extension of the retained compact arbitrary-source
router. It uses the same equal-width chunk interchange with cost
`O(V H^(1-a))`, original fixed-tape modular rotations, counters and sparse
radix repair. It changes the packed-control length from the full address span
to the number of active target positions. No computed-key sort of the full
input is assumed.

Let a supplied permutation of `n=O(p)` binary address coordinates move at
most `k` positions. The stream is a complete binary rectangle, with arbitrary
preceding fibers and following payload. In the regime used below,
`n/(k log p) -> infinity`; short remaining cases can use the retained
full-span router, since `n=O(k polylog p)` there. The conditional cost is

```
O(V (k+1)^(1-a) polylog p + poly(p)).
```

All other coordinate positions return to their original values. This is a
support bound, not a bound on how far a moved coordinate travels.

## Unequally spaced target lemma

Put `B=2^G`, `G=4 ceil(log2 p)+6`, and `K=64G`. Take target positions
`j_0<...<j_(r-1)` whose guard intervals `[j_i,j_i+K)` are disjoint and
within the target field `y`. Sources `s_i` are distinct, are outside the
complete target set, and may be anywhere else in `y`, including guards.
Use packed control fields `u,t` of length **H=rG**, not `ceil(n/K)G`.
Write `u_i,t_i` for their base-B digits and `z_i=u_i mod 2`.

The four updates are exactly

```
y += sum_i 2 z_i t_i 2^j_i
t += sum_i y[j_i] B^i
y += sum_i z_i (1-2t_i) 2^j_i
t -= sum_i (y[j_i] XOR z_i) B^i.
```

Packed t addition is ordinary modular addition, as in the retained gadget.
The two t updates are implemented by shuttling t through the back control
field; no later-to-earlier controlled operation is assumed for free.

For a good address require `u_i,t_i != B-1` and

```
2B <= floor(y/2^(j_i+1)) mod 2^(K-1) < 2^(K-1)-2B.
```

Within one guard block, if z=0 the two target updates vanish. If z=1,
writing its initial low bit as e, the first addition changes the block by
2t. The packed t update changes that control digit to t+e, without carry.
The second addition changes the block by `1-2(t+e)`. The net change is
`1-2e`, so precisely its low bit toggles, and every guard bit returns.
The final t update subtracts e and restores t. The guard margins contain
each intermediate displacement. Disjoint guard blocks therefore evolve
independently. **The argument uses no equality between the gaps j_(i+1)-j_i.**

Let F denote these four updates. Execute F; load
`u += sum_i y[s_i] B^i`; execute F; unload by the same quantity. Completed F
fixes every non-target bit. Consequently each source has the same value at
load and unload, even when it lies inside a guard. The net target toggle is
`y[s_i]`, and all packed controls return. Sources in the target set are
excluded exactly as in the retained simultaneous-shear theorem.

Every elementary rotation is bijective on *all* addresses. Its inverse uses
the current controls in reversed order. The ideal XOR shear preserves the
good predicate, and agrees with the actual permutation on every good
address. Bijectivity therefore makes both good and bad sets invariant. The
same correction `T(S^-1(current address))` sorts only the bad holes.

The union bound is

```
bad density <= r [2/B + 8B/2^K] <= p [2/B + 8B/2^K].
```

Thus the retained repair budget, including O(p)-bit keys and resets, still
applies. Only r active control digits exist; unused geometrical gaps create
neither control digits nor recursive interchanges.

## Arbitrary support and tape charges

Factor the supplied coordinate permutation into two involutions on its
support, hence two matchings with at most k endpoints. The three XOR stages
for a matching have disjoint source and target sets. After temporary field
placements, color each target by its **current** position modulo K. Each
color has disjoint length-K guards. The last K positions contain at most K
targets and use the retained exact elementary CNOT construction.

For an entire matching use the uniform bound H0=kG before any placement.
Three disjoint reservoirs of 3H0 bits can be chosen when the remaining
span is at least 9H0. Partition matching
edges by avoidance of those three reservoirs exactly as in the retained
proof: an edge meeting both first two reservoirs avoids the third. Place
the chosen reservoir into two front H0 fields and a back H0 field using a
constant number of original equal-H0 interchanges. Recompute target/source
positions after these placements, and only then form the residue colors.
For a color with r targets, its r active control digits occupy the first
rG bits of each field; the remaining high digits are inactive. This avoids
any circular dependence between field placement and residue-class size.
The proof and good-set density use only the active digits. Undo every
placement after the class.
There are O(K) colors and a constant number of classes, so the recursive
interchange cost is bounded by

```
O(V K (kG)^(1-a)) = O(V k^(1-a) polylog p).
```

Rotation scans are O(V) each. Their sparse target list and arbitrarily long
zero gaps are a polynomial-size descriptor. To pay this descriptor with
short coefficient records, set `ell=ceil(log2 p)^2`. If
`n>2(k+1)ell`, a gap outside the moved support contains a contiguous ell-bit
field S disjoint from the actual last ell bits. Use an original equal-ell
interchange A to move S to that actual suffix. Route the conjugate
`A pi A^-1` on the n-ell prefix only, then undo A. The conjugate fixes the
suffix pointwise because pi fixed S. Choose every dirty control reservoir
inside the prefix after this interchange, then recompute positions and
residue colors. Thus no control operation touches the enlarged record.
Its 2^ell complete values absorb the polynomial descriptor work; no data
is padded or duplicated. If `n<=2(k+1)ell`, the retained full-span bound
already gives `O(V (k+1)^(1-a) polylog p)`. The placement itself costs only
O(V polylog p). This explicit suffix-conjugation bookkeeping was
independently supplied in `work/inplace_algebra_ultra/SUPPLIER-SUPPORT-AUDIT.md`.

## The gather uses only S union T

Let S list the k selected low-coordinate bits in the desired tensor order,
and T list k consecutive destination slots. Send S bijectively to T. Send
the remaining domain slots `T\S` bijectively to the remaining output slots
`S\T`, and fix everything outside `S union T`. This explicitly extends the
requested gather to a coordinate permutation supported on at most 2k bits.

The other coarse-coordinate bits can be scrambled by this extension. Their
order is retained and described by the inverse permutation; **no stable
compaction of all coarse fields is performed**. A coarse neighbor address
can be decoded, incremented in its logical axis, then encoded in this
physical coarse order when constructing a sparse correction key.

## Evidence and boundary

`check_sparse_shear.py` checks all 32,768 addresses for targets 0 and 6 with
guard length 5, including 512 good addresses, inverse composition and every
bad repair. It also checks 4,000 arbitrary/constructed-good addresses with
unequal gaps 9 and 11 and sources inside guard fields. `check_halo.py`
checks three explicit support-at-most-2k gather permutations.

These controls support the algebra; the cost argument above is the
all-size conditional transfer. It retains the original bit-supplier,
equal-width interchange, fixed-tape and common-label hypotheses. It does
not upgrade an arbitrary full computed-key sort to a fast router.

Sources: the retained reports `compact-arbitrary-source-routing.md` and
`review-arbitrary-routing.md` under
`work/integer-mult-current/references/semantic-bulk/rad20/reports/`.
