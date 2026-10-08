# Independent compact-control transfer review

Campaign `20261007T222521Z`, immutable clock
`2026-10-07T22:25:21Z` to `2026-10-08T08:25:21Z`.

The new compact-control movement, complete-field layout, exceptional repair,
and generalized guard arguments pass this independent review within the
retained manuscript interfaces. No mathematical counterexample was found.
This is a positive conditional transfer assessment, not formal verification
of a complete multiplication machine or independent certification of every
unchanged analytic lemma.

The separately acquired input is CrocSwap/integer-mult-bounds commit
`6e564879f51ae16f23d392e9e196c605f36d90df`, committed
2026-10-08T00:27:54Z, titled "Publish conditional compact-control bound beyond
2^-34". Its notes are attributed to Douglas Colkitt, October 7, 2026. The
campaign's original commit `bcd4ebde8692383539f8a48734e5fbf3a18a32c2` remains
unchanged. GitHub data was accessed with `gh`; neither immutable checkout
was executed through a certificate-writing entry point.

Primary texts reviewed are the pinned [movement argument](https://github.com/CrocSwap/integer-mult-bounds/blob/6e564879f51ae16f23d392e9e196c605f36d90df/notes/compact-control-movement.tex),
[complete-field layout](https://github.com/CrocSwap/integer-mult-bounds/blob/6e564879f51ae16f23d392e9e196c605f36d90df/notes/compact-control-layout.tex),
[general guard](https://github.com/CrocSwap/integer-mult-bounds/blob/6e564879f51ae16f23d392e9e196c605f36d90df/notes/compact-control-guard.tex),
[independently sized complex network](https://github.com/CrocSwap/integer-mult-bounds/blob/6e564879f51ae16f23d392e9e196c605f36d90df/notes/independent-complex.tex),
and their combined manuscript patch. The retained elementary-stream,
arbitrary-width interchange, complex residual, and complete-layer contracts
were checked directly in the original source included with that input.

## Independent exact evidence

[review_compact_controls.py](../code/review_compact_controls.py) reconstructs
the written address permutations without importing any upstream control
implementation. [Run 20261008T012900Z](../runs/20261008T012900Z-review-compact-controls/)
used one Python 3.14.4 process, seed 109, and finished in 27.92 seconds with
36,764 KiB maximum resident memory measured by `/usr/bin/time -v`.

| Check | Exact result |
|---|---:|
| Addresses in eight complete small rectangles | 139,264 |
| Adversarial carry/borrow and guard boundary addresses | 207,360 |
| Nonempty-good-set addresses among boundary checks | 57,600 |
| Boundary cases requiring a nontrivial correction | 53,184 |
| Complete reserved-field configurations | 52 |
| Mixed-cardinality row split checks | 764 |
| Small-dimension fallback checks | 2,108 |
| Exact bad-fraction cutoff comparisons, p=2..2048 | 2,047 |

Both source orders, rho=0 and rho=K-1, both inverse identities, the omitted
highest selected bit, digit values 0/B-2/B-1, and both sides of each guard
endpoint were checked. The small exhaustive rectangles deliberately have
empty good sets: they certify global bijection, inverse arithmetic and
stable exceptional-record reinsertion even when every address is bad.
The separate boundary cases supply nonempty good sets. These are finite
address/permutation controls, not a simulation of the tape scheduler.

## Record-paid rotations on fixed tapes

A controlled rotation has a target after every field its offset uses. Fix
the prefix, split its target range at the modular offset boundary, append
the two pieces to two tapes, and merge them in opposite order. Offsets are
recomputed on the same prefix in the merge. This copies every payload bit
a bounded number of times.

If the stream contains M records of R bits, each prefix fiber contains at
least one complete record. Hence there are at most M fibers. Full control
reads, offset arithmetic, descriptor copies and resetting local counters
can be charged O(A^C) per fiber, where A=ceil(log2(2MR)) and C is fixed.
The resulting cost O(MR+M A^C) does not assume unit-cost arithmetic or an
offset oracle. When A=O(p) and R exceeds every fixed polynomial in p, the
second term is O(MR), uniformly within a fixed parameter family.

The retained ripple-counter proof pays increments/decrements by the number
of consecutive counts, with a width term for initialization. A suffix reset
is charged to that suffix's copied bits. It does not reread a growing axis
descriptor at every payload bit. A fixed number of collapsed prefix,
target, intervening and suffix lengths suffices. Arbitrary positive
mixed-cardinality prefix/gap/suffix fields are explicitly permitted by the
chunk-swap interface; none must be a binary power. The original proof also
explicitly allows a padded row count that is not a radix power.

## Dirty compact identity and correction

For a source bit z, target segment v, and dirty integer w, the four updates
are v+=2zw, w+=parity(v), v+=z(1-2w), and
w-=parity(v) xor z. If a is the original parity, their net action is
v+=z(1-2a), w unchanged. Packing the w digits gives four rotations and four
compact swaps when the source precedes the target. For a later source, two
such identities with an intervening source-bit load into a second dirty
field give ten rotations and twelve swaps. Each rotation's controls precede
its target in the current physical layout; swaps return the declared layout
before the next stage. The independent checker asserts this order.

Only the first f-1 selected positions use the packed construction. The
remaining highest selected position is an elementary two-bit XOR. The guard
segment after the last packed parity ends immediately before that omitted
position, including at rho=K-1.

Write B=2^G. A good address excludes digit B-1 in every loaded temporary
field and requires 2B<=g_i<2^(K-1)-2B in each target guard. A temporary
digit load therefore cannot carry into its neighbor. Intermediate target
displacement is at most 2B, and each completed identity leaves its guard
unchanged; the second later-source identity starts with the same guard.
This proves the desired map on the good set and restoration of arbitrary
temporaries. It does not assert the integer identity on bad addresses.

The actual modular sequence S is globally bijective. The ideal selected-bit
map T preserves the bad set, and S=T on its complement. Thus S also
preserves the bad set. The required correction is T S^-1 applied to the
current bad addresses. Its inverse offsets must be computed using the
current inverse controls. Extract bad records and mark their holes, compute
distinct destination keys, stably radix-sort those records, and reinsert
them into those holes. This proves exact correction, including modular
overflow cases, on a fixed number of tapes.

Uniform complete fields give
delta<=min(1,(f-1)(2*2^-G+8*2^(G-K))). With
G=4 ceil(log2 p)+6, f<=p and K>=G+4 ceil(log2 p)+10,
delta<=5/(128p^3). The whole local repair cost is
O(V+M A^3+delta M A(R+A)). Superpolynomial R absorbs address arithmetic;
the exceptional sorting term is O(V/p^2). Extraction and reinsertion remain
O(V) **at every node**. They are included in the volume-weighted recurrence.
No invalid global estimate using an exponentially small 2^-K exception
fraction is transferred to this gadget.

## Complete fields through recursion

The first q0 chunks form only the row index. The next qF chunks supply two
complete H=dG front fields, and the final qB chunks supply a complete H-bit
back field. Remainder bits are spectators. All reservations are existing
coordinates; no new independent address coordinates or record multiplicity
are introduced. At each call, carve (f-1)G bits from these fields and retain
their unused bits as spectators.

Padding adds whole rows, including every front/back/control/active/spectator
field and the polynomial record. At depth j the row count is divisible by
W^(k0-j). Splitting u=Wg+w sends a complete row to role w and gives every
role exactly 1/W of the parent volume, with identical complete within-row
fields. The resulting mixed-cardinality g prefix is allowed by the retained
interchange and streaming interfaces. Scalar gates see aligned coordinates.
Compact temporaries are restored before a gate, child, or returned result.

The unchanged common-frame identity makes each completed invocation C on
its active axes and identity on every other coordinate, on all physical
roles including dirty scratch. It therefore commutes with the earlier
kernels on reserved axes. Reassembly and signed exchange correction return
every original row individually. A whole padded zero row is zero at this
completed boundary and can be deleted. No intermediate zero-scratch
assumption is used.

Parking, restoring and clearing streams on the fixed stack tapes is paid
by the current logical volume. Record width is unchanged by row splitting;
only the number of records decreases. All calls retain A=O(p), fixed field
count and the same superpolynomial record suffix. The setup absorption thus
holds throughout recursion, not only at the root.

## General guard and separate complex arity

The generalized depth bound keeps E additive in
A(e)<=s A(e/m)+E. Stopping at e<d^beta gives at most
(1-beta)log_m d+1 internal levels. Using s<m^5 and the leaf bound 8e
gives A(e)<=9(s+E)^2 d^(5-4beta). Base-m pieces and the disjoint reserved
axes add the factors and 18d term stated in the note, yielding
C1=5-4beta+zeta and the displayed C0. Every compact operation only permutes
complete encodings; temporary bitwise combinations inside a swap are never
used as coefficients. The new movement causes no numerical rounding or
denominator growth. Epsilon*C1<1 keeps the guarded coefficient width O(p).

At h25 the original complex construction has L=10,315,500,000 and
N=12,167,000,000. Its phase interface requires **L<N**, which holds; the
stronger L<N/2 needed by the additional source rank in the rational bit
interface fails and is not used. Each complex scalar matrix entry is
(intersection-1)/2 plus its side correction, giving exactly the identity.
The inverse middle schedule restores dirty scratch and makes the signed
exchange. All triple lines have binary norm one. Residual complements of
one/two neighboring triples have unused coordinate units because support
has size at most six. Earlier/future tensor indicators have support 3^j<h^j.
Tensoring these witnesses proves every nonzero residual is nonalternating;
the retained nondegenerate decomposition gives orthonormal bases. No
even-ground matching condition is needed for this original complex network.

The bit network supplies arbitrary-width swaps with exponent tau. The
complex network supplies its own fixed m,W,s, residual frames and endpoint
phase corrections. The recursion uses the former's swap exponent and the
latter's row split and branching. Equality of their arities is absent from
the physical layout and assembly contracts.

## Limits and reproduction

The original finite-bit, analytic resampling, exact-recovery and uniform
machine interfaces remain conditional dependencies. The tests above do not
implement a full Turing machine or prove an unconditional integer
multiplication theorem. The new argument is attributable to the separately
pinned upstream draft; this review supplies scrutiny and discriminating
checks, not a novelty claim.

From the RaD root, with the pinned checkout obtained via `gh`, reproduce:

```bash
python3 -B research/integer-multiplication-bounds/code/review_compact_controls.py \
  --reference /path/to/upstream-compact-control-6e564879 \
  --output /fresh/path/compact-controls.json
```

The source checks the exact revision and refuses an existing output. The run
protocol records source/input hashes, the actual interpreter and seed. Its
compact certificate is retained with the run; the full external log is
listed in that protocol. [The independent assembly review](review-compact-assembly.md)
separately checks the new recurrence, the advertised 83/10^12 witness, and
the campaign's stronger finite/phase composition.
