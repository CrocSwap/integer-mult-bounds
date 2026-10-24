# Strided Pauli adapter: layout and supplier audit

Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.

**Result:** the inherited layout does not contain one contiguous f-bit q
digit. A different implementation of the pair gauge uses the existing compact
movement primitive, with cost `O(V((f log p)^tau+1))`. Its address identity is
proved in Lean for every index set. This supplies a written physical adapter
lemma under the inherited complete-range and record-size hypotheses. It does
not supply a new recursive supplier or a new kappa. In particular, the BIT
address-interchange supplier cannot be imported as a Walsh supplier through
one pair gauge.

The frozen predecessor [README](../README.md), `REAL-GAUGE.json`, and pair
algebra remain unchanged. Their contiguous-digit implementation has a
conditional layout premise; this audit replaces that implementation, rather
than declaring that premise true.

## Exact inherited layout

The five copied primary sources in `sources/` are byte-identical Git blobs at
`fbc9ea0249746acca4f504d4fda2b84e0e36cf0d`; the replay also checks that the
working branch's corresponding HEAD blobs match. Their hashes and line counts
are in [LAYOUT-AUDIT.json](LAYOUT-AUDIT.json).

* [05-layers.tex:7-17](sources/upstream/build/sections/05-layers.tex#L7-L17)
  stores `[P] x [2^K]^D x [S]` in lexicographic order, selecting offset rho
  in each K-bit chunk. Lines 105-114 group `e=mf` consecutive chunks into m
  slots with f chunks each. The q-coordinate bits in a slot are therefore
  strided at `rho+jK`; columnwise q-to-axis changes do not gather them.
* [compact-control-layout.tex:18-28](sources/notes/compact-control-layout.tex#L18-L28)
  reserves two front fields and one back field, each with complete ranges,
  and carves `(f-1)G` bits from each. Lines 30-45 split and pad whole rows,
  excluding every compact-field bit from the row index. Each recursive role
  retains the same complete within-row ranges; every operation restores them
  before a scalar operation, child call, or return.
* [02-streams.tex:60-118](sources/upstream/build/sections/02-streams.tex#L60-L118)
  permits splitting on one specified bit into aligned streams, a fixed
  pointwise map, and merging, in O(V) on fixed tapes. It includes counters,
  rewinds, initialization, and erasure. It does not declare a growing bit
  transpose elementary.

Thus the original complement-and-reverse contiguous-digit schedule is not
directly applicable. Choosing a globally different storage order would require
rebinding these row, slot, and compact-field contracts. No such storage change
is made here.

## A uniform implementation without gathering

Let P complement all f selected bits of one slot. Choose an extreme chunk's
selected bit as pivot. Define L to retain the pivot and XOR it into every
other selected bit. All unselected bits and all other fields are spectators.
On Boolean address functions,

```
L^2=I,                  L P L = X_pivot.
S(P)=(I+P)/2+i(I-P)/2 = L C_pivot L,
C_pivot=((1+i)I+(1-i)X_pivot)/2.
```

[Fanout.lean](Fanout.lean) proves the first two identities for arbitrary
index type and pivot, not just a finite test width. The final identity follows
by substituting the inherited C kernel. The same program with `C_pivot^-1`
gives `S(P)^-1`. This construction does not require f even. The separate
real-involution/Walsh formula in the frozen predecessor still requires f even.

Here is the physical extension of the retained selected-bit primitive. Remove
the extreme pivot chunk from the target slot, leaving f-1 consecutive target
chunks. Splitting the pivot chunk into its selected bit and spectator pieces
introduces only a fixed number of formal fields. For f<=2 use the elementary
one-bit/two-bit cases. Otherwise the low `n=f-2` target segments need `nG`
compact bits, no more than the existing `(f-1)G` reservations.

For an earlier pivot, replace every source control `z_i` in
[compact-control-movement.tex:46-69](sources/notes/compact-control-movement.tex#L46-L69)
by the *same* pivot bit z. The dirty four-step identity remains

```
v += 2 z w;  w += v mod 2;
v += z(1-2w);  w -= (v mod 2) xor z.
```

It changes only the target parity and restores w. Its target offsets are
`sum_i 2 z t_i 2^(rho+iK)` and
`sum_i z(1-2t_i)2^(rho+iK)` modulo the target range. Its load/unload offsets
pack the current target parities and their XOR with z. The controls precede
the rotated target after each of the same four compact swaps; the same four
rotations suffice. Repeated controls do not have to be independent address
coordinates.

For a later pivot use the retained later-source procedure
[at lines 72-80](sources/notes/compact-control-movement.tex#L72-L80).
First fan out the old parities of the arbitrary dirty digits u_i. Swap u to
the back field, load **`z sum_i B^i`**, swap back, fan out the new u_i parities,
and undo the load. On the good set every u_i avoids B-1, so adding z causes no
inter-digit carry. Old and new parities differ by exactly z. The two fanouts
therefore yield the desired pivot fanout and restore u, t, and the arbitrary
back field. This costs twelve compact swaps and ten rotations, including the
load and unload. The earlier-source version alone suffices if the extreme
pivot is chosen physically first; the later-source version records that the
other choice does not introduce an ordering assumption.

Generating `sum_i B^i`, reading the one pivot, and producing every packed
offset takes a fixed polynomial in `A=ceil(log2(2V))` tape steps. There are
at most A digits, every exponent and offset has O(A) bits, and ordinary
shift/add arithmetic is sufficient. There is no per-payload-bit scan of this
growing descriptor. The record-paid rotation lemma
[at lines 9-35](sources/notes/compact-control-movement.tex#L9-L35)
charges `O(V+M A^C)` for some fixed C, where V=MR. The inherited record has
R superpolynomial in p and A=O(p), so this charge is O(V).

The guard, exceptional set, and repair are also paid. Use
`G=4 ceil(log2 p)+6`, `B=2^G`, exclude dirty u/t digits equal to B-1, and require
`2B <= g_i < 2^(K-1)-2B` in every low target segment. The repeated source bit
does not change the bad fraction: these tests concern complete dirty ranges
and target guards, not independence of source controls. The ideal fanout
changes only target parities and preserves the bad set. The actual modular
rotations and compact swaps remain bijective everywhere and agree with it
off that set. Therefore the same exact `T S^-1` repair is supported on the
bad records. Its inverse offsets use their current inverse controls and
handle cyclic overflow exactly; stable radix repair costs
`O(V+M A^3+delta M A(R+A))`.
[Lines 82-126](sources/notes/compact-control-movement.tex#L82-L126)
give this argument; the omitted highest target bit is one elementary XOR.
With `delta<=5/(128p^3)`, repair, counters, holes, copying, and cleanup cost
O(V). The retained arbitrary-width chunk-swap calls pay
`O(V((f log p)^tau+1))`, including spectator intervals, padding, and cleanup;
see [lines 128-158](sources/notes/compact-control-movement.tex#L128-L158).

Finally C_pivot is **one actual-bit kernel**, not an f-axis query. Split on
that bit, operate on the aligned coefficient pairs, and merge. Its exact
scale and phase are the old
[05-layers.tex:54-70](sources/upstream/build/sections/05-layers.tex#L54-L70)
kernel. The already checked `PauliPair.lean` program implements it with four
complex ADDs, four signed-power-of-two SCALEs, and one i phase; inversion
replaces i by -i. Prefix row l1 norms are at most four. A constant number of
integer guard bits and one additional fractional bit per executed kernel
suffice for this exact dyadic step. There is no irrational normalization or
division by an odd number. Splitting, merging, and any owned coefficient work
streams cost O(V), including initialization and erasure; they earn no
productive output credit. No extra independent address coordinates are added.
Precision constants for a new whole recursive word still need integration
into that word's total exact-dyadic guard calculation.

## Cost in the actual compiler

For fixed m, the admitted q-to-slot binary map and its inverse use a constant
number of row additions, as specified in
[05-layers.tex:116-139](sources/upstream/build/sections/05-layers.tex#L116-L139).
They cost `O(V((e log p)^tau+1))`, with `e=mf<=d`; see
[compact-control-movement.tex:161-167](sources/notes/compact-control-movement.tex#L161-L167).
The two fanouts and elementary C therefore give this same complete bound for
S(P) in the original q chart. It is **not O(V)**.

Here p is the global coefficient precision, f=e/m the internal axis count,
K=floor(d^c), d=Theta(p^epsilon), and V includes all polynomial records and
retained padding. The record length r=2^Theta(p/d) is superpolynomial;
[05-layers.tex:20-32](sources/upstream/build/sections/05-layers.tex#L20-L32)
states the regime. Complete row reservations survive every recursive role,
so the construction does not require a new growing transpose or a stronger
layout predicate. It acts within active slots, restores reservations and
spectators, and preserves all-zero padded rows at completion.

The parent compiler arithmetic pinned by the receipt has
`kappa=15108879/5000000000`, `tau=1-a`,
`a-kappa=1/175000000000`, and `lambda-tau=1/1400000000000`.
Consequently the logarithmic factor is absorbed by the *existing* strict
tau-to-lambda margin. A fixed number of these adapters per node fits the
same compact-operation overhead recurrence. This checks the cost category;
it does not add target credits, reduce a paid invoice, or improve kappa.
S is a nonmonomial coefficient operation, so extending a whole-job contract
whose endpoint-normalizer alphabet is monomial requires an explicit semantic
extension and matched entry/exit types. That conclusion is not supplied by
the cost calculation alone.

## Why the BIT bound does not transfer

The BIT interface is a different recursive job. In
[DELAYED-COVER-BRIDGE.md:38-77](../../kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md#L38-L77),
the rational projector P describes an address-space partial interchange
`D_P`; conjugating it changes the projector, and `D_P D_(I-P)=D_I` completes
the address interchange. The cover is one odd-local-ring address cover with
one common external weight. These projector ranks do not count complex
Gaussian coefficient axes. The local unit's arbitrary helpers and paid
profile remain conditional on those rational charts and delayed-cover
semantics; see
[PROOF.md:46-53](../../query-thinned-controllers/PROOF.md#L46-L53).

The current finite BIT invoice has 11454 productive fields, 57555 paid calls,
rank surplus 753, and one owned stream reused sequentially. Its complete
target and paid profiles are copied verbatim into the receipt under
`nontransferable_bit_invoice`, with source hashes. These are address-
interchange jobs. They are not an available invoice for Walsh jobs. The
ordinary BIT saving 0.0034 follows after odd-local-ring covering and the atom
adapter in
[PROOF.md:184-203](../../query-thinned-controllers/PROOF.md#L184-L203).

There are two concrete mismatches. First, the completed BIT operation merely
permutes payload addresses. One S before and one S after a permutation have
at most four nonzero coefficients in each output row, even allowing signed
monomial normalizers. A full f-axis Walsh or the even-f realified Gaussian
has 2^f nonzeros per row, already exceeding four for even f>=4. This rules
out the proposed *completed-job* transfer through one pair gauge at each
end. Second, its internal Boolean data gates are not a complex-linear
coefficient program: replacing Boolean XOR by complex ADD does not preserve
their identities. An operator being an involution does not identify these
recursive job types or their productive helper endpoints.

There is already an exact complex-to-normalized-Walsh conversion for all f
in [05-layers.tex:156-178](sources/upstream/build/sections/05-layers.tex#L156-L178):
`H0^tensor f=b^f S_f C^tensor f S_f`, with addresswise i phases and an exact
dyadic scalar. Thus a genuinely admitted arbitrary-input Walsh supplier,
including its independent arbitrary helpers and all endpoint corrections,
would already be relevant without the new pair gauge. Such a supplier has
not been obtained from the BIT address-interchange construction here.

## Verification and reproduction

Run from the repository root in PowerShell:

```powershell
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round6-query-normalizer-20261022/layout-audit/audit_layout.py
```

The fresh receipt binds the pinned auditor, Lean executable, dependency
revisions, audited source, compiled object, and actual output log. Its parser
checks theorem names and the allowed axiom set `{propext, Classical.choice,
Quot.sound}`. Fanout uses only propext and Quot.sound. No custom axiom,
`sorry`, `native_decide`, or kernel bypass is accepted by the source audit.
Lean proves the arbitrary-index fanout identities, not the tape theorem or
the full multiplication theorem.

Finite checks additionally cover 11046 strided address cases, 40960 complete
small compact-control cases with 5120 good cases, and 62208 repeated-pivot
cases with arbitrary good dirty digits. These exercise later-source
load/unload and the preservation of the bad predicate. They supplement the
written extension of inherited tape lemmas; they do not prove an all-size
tape runtime or a new recursive supplier.

## Open next questions

1. **Extend the actual whole-job alphabet with S(P).** This matters only if a
   changed supplier can consume and return the same encoding. A feasible
   first step is to state the input/output types of one p1 or p2 caller,
   replay it on every arbitrary input column, and list every paid child and
   independent helper endpoint. The blocker is the missing matched recursive
   consumer, rather than the strided address identity. Recompute all owned
   streams, fixed constants, and precision guards before giving any credit.
2. **Find a coefficient supplier, not an address interchange.** A feasible
   first step is a complete small arbitrary-input Walsh/Gaussian program
   with an independently usable helper contract, then an exact all-f
   residual-frame lifting argument and invoice. The BIT projector/cover
   construction supplies neither this endpoint nor its child job type. The
   old all-f C-to-H0 conversion can transfer such a supplier once it exists;
   one pair gauge around the current BIT endpoint cannot do so.

This bounded audit is frozen after the documented replay. No supplier or
kappa improvement is claimed by this package.
