# Mandatory complete-field passes in the current serial monomial

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This is a scoped implementation lower bound. **No new kappa, supplier
admission, general algorithm lower bound or multiplication lower bound.**

## 1. Claim and exact source

Fix the actual `SerialProvider` at public CubeJerry commit
`2ec95e06c2a16e73f9da9a8fe41912710135daaf`, with its unchanged current
monomial adapter and literal `CodedPort` implementation. The retained
sources and public paths are in `DEPENDENCIES.json`. The canonical base
is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

Let f>0 be the parent column count and V the length in PHYSICAL BITS of
the complete coded public numerical field, excluding its left marker and
blank frontier. For any successful admitted serial invocation on the
unchanged complete format, its public field alone incurs at least

```text
4 f V        physical unit moves,
(4/3) f V    physical reads,
f V          physical writes.
```

V is a multiple of three. These are simultaneous coordinatewise lower
bounds obtained by selecting disjoint mandatory instructions. Additional
work is nonnegative. No operation-time measurement or earlier upper bound
is used to derive them.

This applies in particular to the fixed, nontrivial, actual selected
#6030 MOVE event9896 entrance/right monomial, from raw record
`("MOVE",236,3,7,False)`. Its matrix rank is nine and constant phase is1.
The selected raw MOVE's positive child rank1 is a DIFFERENT parameter;
the source right/left monomials each act on nine chart coordinates.
The verifier regenerates this literal recipe from the exact retained
selected word and canonical Clifford constructor. This does not port or
replace the proposed #6936 catalogue.

## 2. Four complete traversals, independently of numerical input

The literal serial loop first prepares its private header iterator, then
calls `self.native.run(self.field,self.view.context)`, advances the
iterator and repeats until `finished`. The unchanged PREPARE saves f,
sets column=0 and emits the first one-column view. NEXT increments the
encoded column, returns `ready` while column<f and `finished` at equality.
Thus successful return includes exactly f completed monomial invocations.
There is no all-zero-field shortcut, caller-dependent batch skip or
replacement of the native object between columns.

Every one-column adapter call unconditionally executes `import_field`,
the retained engine, and `export_field`, in that order. Let S=V/3 be the
number of virtual numeric symbols, including component delimiters.
`import_field` consumes every signed data bit and both component
delimiters of every record until the physical field frontier. It calls
`field.move(1)` once per symbol and appends one guide marker per symbol.
Its `rewind_field` consumes all S guide markers and calls `field.move(-1)`
once per marker. This is a full advance followed by a full return.

On successful exact-format return, `export_field` writes and advances
over every returned data bit and every original delimiter. It checks the
same complete frontier, then invokes `rewind_field` on the same S guide
markers before clearing the guide. This is another full advance and
return. The source geometry/tensor map preserves the number and width
of records; success explicitly checks the matching complete frontier.
The numerical values, including a zero payload, do not alter these loops.

Each successful ordinary `CodedPort.move` makes one physical read and
exactly three physical unit moves. A right move from a blank cell may
materialize additional code, but in these four field traversals every
step begins on a complete existing body symbol, or is a valid return
from the frontier. The backward direction also has one read and three
moves. None crosses the local LEFT marker. Four S-step traversals hence
give at least 4S reads and 12S moves, namely `(4/3)V` and 4V per column.

Every virtual symbol in the successful export receives one `field.write`,
including each delimiter. The literal write has three physical writes,
so this contributes 3S=V physical writes per column. Reads, moves and
writes internal to `read`/`write`, native codecs, raw bridge copies,
phase computation, permutations, private header creation, counters,
engine setup, source construction and retirement are omitted positively.
Historical backing cannot provide a negative credit. Summing f calls
proves the three inequalities for arbitrary successful admitted inputs.

This is a statement about the actual fixed implementation, not about
the mathematical monomial's intrinsic complexity. Identity and zero data
can have cheaper alternative algorithms; this code still scans them.

## 3. An admitted infinite local descriptor family

The following is a family at the ACTUAL SERIAL MONOMIAL ABI, not a claim
that a global compiler currently produces it. For each integer f>=128,
fix the same actual rank-nine right recipe and choose

```text
outer=rows=stock=1,  h=2,  one complex coefficient per record,
d=selected_axes=p=D=9f,  remainder=0,
K=G=1, rho=0, H=f,
active_start=u=2f, entry_start=2f,
back_start=z=11f, within_bits=a=12f,
record_bits=6(h+1)=18, row_bits=18*2^(12f),
q0=qF=qB=0, cutoff=145.
```

The 23 descriptor fields use the canonical encoding; h is the public
component width, not an additional header field. Unused fields are stated
explicitly; they are not asserted to satisfy unconsumed global producer
identities. Supply the entire field of `2^(12f)` records, both h-bit signed
components zero, valid local markers and exact blank frontier. Supply
the fixed actual provider's full disjoint, blank private inventory; retain
and price its historical backing as required by the predecessor.

The consumed guards hold:
`(f-1)G=f-1<=H`, `2H=u`, `u+9fK=z`, `z+H=a`,
`rho<K`, `9f+remainder=selected_axes<=d`, and `0<=remainder<9`.
The row equality and `record_bits=6r(h+1)` hold with r=1; h>=2 and
all required positive quantities are positive. Therefore the exact
parent monomial geometry is admitted. Its one-column views have
`f'=1,K'=f,rho'=j,selected_axes'=9` for 0<=j<f and still act at
`u+if+j`. All19 other fields, complete record extents and spectators
remain unchanged. The per-call back suffix becomes f bits, accounted
as additional coefficients; it is not dropped from V.

Every intermediate signed permutation/quarter-phase maps zero to zero.
Zero is strictly between -2^(h-1) and 2^(h-1), so all signed phase
guards succeed. No exact-half/grid promise is needed by this monomial.
The frozen provider's completed format, permutation and lifecycle
contracts remain inherited premises; the arithmetic family checks do
not create a new physical simulator proof. No huge field is allocated
or run in this package.

Here the physical field length is `V=18*2^(12f)` and its delimiter-free
signed payload length is `Vraw=4*2^(12f)`. Thus `V=(9/2)Vraw`; changing
between those two COMPLETE-field conventions loses only a fixed factor.
The native header dimension really is `d=9f`; it is neither the number
of records `2^a` nor the positive child rank1. No extra f is hidden by
renaming an already f-multiplied comparison volume.

The family even meets the previous long-record upper simplification:
its one-column R1=2hr*2^(a-z)=2^(f+2), M1=2^z and
`A1=2+z+ceil(log2(R1+1))=12f+5`. At f=128,
`2^(f+2)>=(12f+5)^6`. The ratio on increasing f is
`2/(1+12/(12f+5))^6>1`: for f>=128, the parenthesized term is at most
`1+12/1541<129/128`, and `(129/128)^6<2` by exact integer arithmetic.
This proves the long-record inequality for all f>=128, not just tested
members. The canonical descriptor length E is O(f): the largest field,
row_bits, has 12f+5 bits and all other fields have O(log(f+1)) bits.
Hence `(E+1)^4+Q=O(V)` for the fixed finite inventory Q. The lower bound
does not rely on these upper absorption conditions, but is not defeated
by their absence on this example.

## 4. Conditional supplier consequence and cutoff boundary

Here T denotes the literal physical unit-move count, or the raw
read/write/unit-move action count which dominates it. For this local
implementation and family, no fixed C and epsilon<1 can satisfy
`T<=C V d^epsilon` on every f: the mandatory move count gives

```text
T / (V d^epsilon) >= 4 f / (9f)^epsilon
                    = 4*9^(-epsilon)*f^(1-epsilon) -> infinity.
```

Canonical simultaneous multitape steps are a different metric. If a step
can perform at most P of these physical unit moves, with fixed P, the
corresponding implication is `T_TM>=4fV/P`, not automatically `4fV`.
The exact conversion/simulation contract must be supplied; its fixed
factor does not change the divergent power of f.

The same asymptotic conclusion holds with Vraw or any comparison volume
uniformly Theta(V), and with any fixed conversion factor between literal
physical unit moves and the proposed cost metric. If the comparison volume has
already been multiplied by f, or d is exponentially larger than f, this
argument does not establish that displayed rate obstruction. Those
parameter mappings must not be silently changed.

**This does not refute the current direct-leaf wrappers' contract.**
SerialProvider and its monomial adapter never consume `cutoff`; the
family stores the fixed value145 without using it. The later protected
direct/rounded MOVE wrappers separately require parent f<=cutoff (an
older direct route also required r*f<=cutoff). With a fixed global
cutoff t, these wrappers only admit bounded f, and their O(fV) work
can be absorbed in an O_t(V) leaf constant. The above infinite family
is not thereby an admitted full-MOVE/nonleaf family.

The useful exclusion is precise: reusing THIS serial implementation as
a full supplier uniformly over a producer-admitted unbounded regime
f=Theta(d), with comparable complete-field volume, cannot establish a
sublinear power of d by changing only fixed tariffs or constants.
Actual producer admission, its volume and dimension identities and the
global cost conversion remain separate obligations. No global
assumption, selected exponent or accepted certificate is changed.

## 5. Novelty, evidence and open next questions

The public serial predecessor proves the positive implementation and
an upper invoice, explicitly retaining repeated setup and O(fV) cost.
Its cited current Compact binding warning is expressly an upper-bound
implication limit, not an algorithmic lower bound. This package adds the
mandatory four-traversal lower theorem, an explicit unbounded admitted
local family, and the fixed-cutoff limitation. Original monomial work
including CrocSwap/integer-mult-bounds#3087 and #4172 and the public
current monomial/serial adapters retain full credit.

The checker authenticates source bytes, regenerates the one actual
selected recipe, checks the four-traversal call structure and literal
coded primitive costs, verifies bounded family arithmetic, and rejects
missing rewind, invalid reservations, false volume and false cutoff
scope controls. It does not execute a numerical monomial or prove the
universal theorem by finite sampling. The traversal and induction
arguments above carry that quantification.

**Open next questions:** bind f,d,V and cutoff to one actual full
supplier/exporter domain, or devise a different implementation that
avoids per-column complete-field import/export. A source-bound batching
construction must still pay its actual phases, routing and cleanup;
the lower theorem does not rule out such a construction.
