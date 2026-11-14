# Literal arbitrary fixed native offset in the Gamma6/HOME ABI

## 1. Prior scope and quantified statement

Canonical context is e54523517d0f03e58352e647c403a5af3e525a57. PR #7428 at
1dbdaa414cfe4a4a0f015e88a04b52e146566786 already implements the first-slot
translation X0, including actual descriptor production, complete-record
reversal, same-owner return and successful cleanup. Its25-tape translation
and retained13-tape reversal are unchanged here. The original proof is
retained as reference/translation/PROOF.md, exact Git blob
5c6325471aaed465737491870443f063c821b7a0. No new reversal, numeral conversion,
translation algebra, physical Gaussian-monomial theorem or faster tariff is
claimed. The new object is the fixed arbitrary-offset literal composition
and owned Gamma6/HOME return.

Fix a construction-time integer b in0..511, representing a vector of F2^9.
It is not an encoded runtime parameter. Supply positive f,c,P,S,w,cutoff in
six canonical Gamma codes on HEADER. Let E5 count the first five codes and
E=E6 count all six. DATA is the complete lexicographic array
`[P] x [2^f]^9 x [S]`, with c complete Gaussian coefficient records per
address, real then imaginary, each component w raw MSB-first bits. Thus
`V=2PScw2^(9f)`, `F=E+V`. This permutation works at every positive w;
there is no arithmetic or signed-headroom requirement. Any common quantum
or interpretation of those component bits remains unchanged.

The complete V-bit body ends in a blank. Owners are distinct; heads start
at their supplied origins, required private windows/guards are blank, and
opaque exteriors/earlier history remain charged. Supply the usual Gamma6
owned HOME entry after typed reservation when using that layer. No source
owner selector, input producer, new ownership credit or full caller is
inferred from this entry contract.

**Theorem.** For each fixed b the emitted31-tape four-symbol program sends
every source address `(a0,...,a8)` to

`(ai XOR [bi*(2^f-1)])_(i=0..8)`.

It copies each complete coefficient/component bit without alteration and
preserves P/S spectators, header/cutoff, width, owner identity, opaque
exteriors and quantum. Every head returns and every private body/guard
retires on success. One outer transaction installs the complete result on
the original DATA owner only after all factors return. No failure cleanup,
interruption/retry or general malformed-input theorem is asserted.

With fixed program/origins supplied, complete successful bounds are

`T_core <= 2^20(fV+E+1)`,
`K_final <= K_entry+256(V+E+1)`.

The35-tape Gamma6/HOME adapter adds128(F+1) time and64(F+1) historical
backing, giving320(F+1) total increment, and returns exactly F bits to the
same supplied HOME. General B1 bank delivery/return is separately charged
at O(R_bank K_bank(F+1)). Fixed program/table construction, authentication
and origin provisioning have a fixed Setup_b charge if not already supplied.
No encoded size is decoded into a host runtime loop or graph generator.

## 2. Why the unchanged five-field parser accepts Gamma6

This compatibility is already an instance of #7428's explicit opaque-tail
theorem: its section2 permits opaque data immediately after the fifth code.
The code provides a direct refinement. `compile_translation` calls Gamma
exactly five times for f,c,P,S,w, then immediately `trace_return(HEADER)`.
Each header step advances exactly one bit while extending HTRACE. Therefore
all HEADER reads lie at offsets0..E5-1. The final step visits offset E5,
which may be the first cutoff bit, but does not read or write it.

The trace return branches only on its private trace and moves HEADER back
one cell for each consumed bit. It reads/writes no trailing header cell.
All later descriptor production uses the captured unary guides. The
retained reversal receives PDESC/RDESC/BDESC/DATA and private roles, never
HEADER. Final producer cleanup likewise has no HEADER operation. Hence the
sixth Gamma field is unchanged, regardless of its represented value or
length; HEADER returns to its original origin. The unchanged CNOT word
parser also reads just these first five fields and trace-returns, as in
the frozen Gamma6 rank2/positive joins.

The original translation bill is4096(V+E5+1) with32(V+E5+1) private backing.
Replacing E5 by the larger E is a valid bound. The HOME splitter additionally
reads and copies the complete sixth code using a guide for its bit length,
not a unary expansion of the numerical cutoff. Its O(F+1) work remains paid.
This permutation has no positive-child cutoff branch and does not assert
rho*f<=cutoff. The sixth field is preserved format, not a newly enforced
leaf admission condition.

## 3. Fixed conjugator and exact all-column action

For b=0 no component runs; the outer original-owner transaction is the
identity. For b nonzero let p be its least supported coordinate. Construct
a fixed chronological CNOT word G:

- If p>0, first exchange slots0 and p using `(0<-0 xor p),
  (p<-p xor0),(0<-0 xor p)`.
- For every other supported coordinate j, append `(j<-j xor p)`.

The slot exchange sends e0 to ep. All following gates leave its p bit1
and set exactly the other supported coordinates. Thus G e0=b. If p=0,
the initial exchange is absent. Every CNOT is an involution, so reversing
the word gives G^{-1}. If b0=1 the word has popcount(b)-1<=8 gates; if
b0=0 it has3+popcount(b)-1<=10. No minimality claim is made.

Chronologically execute G^{-1}, X0, G. For one nine-bit column x this gives

`G(G^{-1}x XOR e0) = x XOR G e0 = x XOR b`.

The retained generic CNOT body applies its fixed slot pair to all matching
f columns in the unchanged nine-slot geometry. The retained X0 complements
every one of slot0's f bits. Therefore the same identity holds separately
on each actual column. Equivalently, every supported full slot is XORed
with2^f-1. All other native bits and complete P/S/coefficient/component
factors remain spectators. There is no address-space enlargement or
changed f header.

Every component is a pure permutation of complete records and has scalar
phase exactly1. The construction changes no sign, Gaussian component, bit
order within a record or grid. It accepts the most-negative signed bit
pattern because it never negates an arithmetic value. In the source ket
convention `|x> -> i^q(x)|G_source x XOR b>`, this X_b is applied after the
source binary map; its coordinate bit i denotes output packed slot i.
This observation fixes the intended offset convention but does not bind a
complete source monomial or MOVE.

## 4. Literal relocation, owner return and helper reuse

The old first-slot translation remains the same1878-location graph. The
two fixed CNOT words use immutable rank2 `compile_word` and unchanged
generic `cnot_columns`. Word generation is an offline function of b; no
runtime branch reads b, chooses p, loads a matrix or computes a jump.
For b=1 the word is empty and both CNOT modules are omitted. Otherwise one
reverse word, one X0 body and one forward word execute, at most20 CNOTs.

The outer transaction clones original DATA once to WORK and restores its
head with TRACE. Immutable `insert` maps component HEADER0 to original
HEADER, component DATA1 to WORK, and private t>=2 to t+2. Fixed PC labels
are relocated and successful halt becomes a one-step continuation goto.
Thus every runtime operation is read/write/unit move/goto/halt. The largest
component port is26 from the CNOT module, mapping to28;31 ports are retained
for compatibility with the shared native cohort. Unused ports stay blank.

Each completed component preserves HEADER, returns its public factor DATA
to origin and clears private bodies/guards. Therefore the same private
owners can be reused by the next component. Module commits affect only
WORK. After all components succeed, one V-bit final copy commits on original
DATA, erases WORK and records/restores both heads. WORK/TRACE guards then
retire. No component can write original DATA through its relocated ports.
Structural checks confirm this before the final commit for15 mask templates.

HOME uses the retained six-code split/return with native origins at
B-relative2, blank guard1 and permanent^ at0. Core ports map injectively
to3..33; GUIDE is34. On success unchanged header and transformed body are
repacked, all split copies erase, and all35 heads return to their B origins.
B1 scatters only after primitive return, to the same immutable HOME. This
is a supplied owned operand; the parked productive fixture is unchanged.

## 5. Complete successful invoice and retained history

Use the credited complete translation bound
`T_X<=4096(V+E5+1)<=4096(V+E+1)` and generic fixed-word bound
`T_G(k)<=1024 k f(V+1)+8192(V+E+1)`, including all descriptor acquisition,
full body/bit copying, actual arithmetic-free record routing, returns and
retirement. Let k<=10 be this b's fixed conjugator length. The complete
nonzero-offset sum, allowing two word envelopes even when k0, is

`4096(V+E+1)+2048k f(V+1)+16384(V+E+1)+31V+27`.

With f(V+1)<=2fV and V<=fV this is bounded by

`(4096k+20511)fV+20480E+20507`
`<=61471fV+20480E+20507<=2^20(fV+E+1)`.

The zero-offset transaction costs31V+27 and also fits. The full cutoff
syntax is charged by E and the HOME overhead. There are no unpaid supplied
reversal descriptors: X0 physically produces P,2^f and2Scw2^(8f), including
unary expansion, linear-time unary/binary conversion, complete record
reversal and descriptor retirement. No helper, outer copy or return is an
oracle callback or an unpriced recursive child.

Incremental private visited backing is at most32(V+E+1) for X0,
64(V+E+1) per fixed binary word and8(V+E+1) for WORK/TRACE. Summing rather
than refunding completed factors gives168(V+E+1)<256(V+E+1). The identity
uses only the outer increment. HOME adds64(F+1), giving the stated320(F+1)
envelope. Fixed setup/program storage and B1 full-bank delivery remain
separate charges. K_entry retains every older visited region and opaque
owner allocation. Shorter successful calls reuse erased current bodies
without refunding previous maxima. Changed origins require actual interval
unions and paid transport corridors.

This is a direct O_b(fV+E) routine. It does not inherit the faster selected
nonleaf monomial tariff, establish amortization in a full recurrence, bind
the source recipe/owner, or supply a producer of the Gamma6 ABI.

## 6. Evidence and exact limitations

The algebra checker independently evaluates every nonzero b on all512
addresses:261632 conjugation/inverse pairs, all512 masks including identity,
and an actual maximum conjugator length10. It does not compile512 large
graphs for code-coverage credit. Fifteen emitted mask templates, including
every single coordinate, identity, full511 and maximum-word510, pass port,
PC, unit-move and no-early-original-write checks.

Five complete retained-X0 runs use five-field prefix length11 and Gamma6
cutoffs with bit lengths1,2,64,513,4097. A read observer records HEADER
read offsets exactly0..10 and head maximum11 in every run; no HEADER write
occurs. All five take exactly681487 steps, return the expected complete
8192-bit raw permutation and restore all25 heads/private bodies/exteriors.
These observers never affect execution control.

The full-offset511 packet uses all512 addresses with distinct10-bit real
labels and imaginary labels including the minimum signed value. Its10240
DATA bits return against direct address-XOR oracle in13648484 transitions,
with10252 final HOME writes only after complete primitive return. A mixed
far-slot b264 packet exercises slots3 and8 plus two outer rows, three
spectators and two Gaussian coefficients. It returns36864 DATA bits in
28973166 transitions with37004 final HOME writes. Identity and smaller
same-owner reuse also pass; earlier guide history remains charged. All35
heads/private bodies/guards/exteriors restore on successful complete runs.

Actual graph mutants remove the last conjugator gate (returning offset255
instead of511), or reorder the block as G^{-1},G,X0 (returning offset1).
Both complete cleanly but fail the correct XOR oracle. A changed retained
translation source byte rejects at authentication. Normal and optimized
author replays compare exact receipts. These are finite evidence; the
all-size result uses the preceding invariants and inherited helper proofs.

No full large-f DATA execution is claimed here; the original first-slot
predecessor already includes a complete f2 fixture, credited as inherited
evidence. No generic source monomial dispatcher, all-MOVE implementation,
full owned lifetime, caller admission, selected rate, assumption discharge
or new kappa follows from this isolated bit-permutation interface.
