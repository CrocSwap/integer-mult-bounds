# Chronological numerical fields at the whole-high boundary

Prepared for @CubeJerry with substantial OpenAI Codex assistance. The machine,
arithmetic, cover geometry and numerical evaluator retain the predecessor
attribution in NOTICE.md. This is a local implementation and composition result,
not a completed selected multiplication theorem. **No new κ.**

## 1. The two actual orders

All source paths, exact bytes and commits are in CUSTODY.json. The geometric
predecessor is #5829, `delayed-cover-batch-allocation/PROOF.md`. The physical
source is #6719 at `e4e52d6ba2c805fa78bb57778c3b7bbc064edba5`. Its
`recursion/core/recursive.py`, `Builder.compile`, passes the shape producer's
`R_child=H R_parent` grant to each actual child. The source proof gives

\[
 a_{\rm parent}=(a_{\rm child}L+\ell_{\rm child})H+h_{\rm child},\qquad
 r_{\rm child}=h_{\rm child}R_{\rm parent}+r_{\rm parent}.
\]

Consequently, after j descents, a body with base-fibre extent F and C=j+1
high matrices has physical ordinal

\[
 r=F\sum_{i=0}^{C-1}h_iH^i+f,\qquad 0\le f<F.
\tag{1}
\]

The oldest high matrix is the least significant high factor. The current high
matrix is the most significant. Remaining stock gives an outer repetition of
this complete body. This statement uses the fixed width of the pinned stopped
recursion: H is constant along the path. No changing-width extension is claimed.

The unchanged numerical `directory.py`, `produce`, instead loops over each
old physical prefix and then over every new matrix. `Odometer.advance` changes
the last row-major matrix entry first. `produce` appends the old chronological
records before the new record. Repeated application therefore enumerates
chronological tuples with the **newest** high matrix varying fastest. The
source-order streaming replacement in #5055 deliberately preserves that order.
For two fields its ordinal is h0 H+h1, rather than h0+H h1.

Neither source is wrong under its own contract. #6719 explicitly excludes the
numerical evaluator, and #5055 preserves its own caller's layout. The demonstrated
failure is the proposed direct composition that pairs equal directory and
whole-high payload ordinals without changing the field producer. A permutation
of field *values between physical fibres* is not a permissible relabelling of
global slots inside one descriptor.

## 2. The isolated physical port

Fix an odd radix q>=3, dimension N>=1 and finite source-code width Q>=1 before
execution. Primality is unnecessary for the producer and remains required by
the inherited local-ring consumer. Let

\[
 c=q^{w-1},\quad m=N^2,\quad H=c^m,\quad
 \lambda=\operatorname{bitlength}(q^w)+1,
\]

where runtime w>=1. A nonempty chronological list of C source codes is supplied
as Q little-endian bits and WORD_END for each code. C is not decoded into native
control. Runtime F>=1 is the base-fibre extent. The borrowed arbitrary Boolean
payload has length V=P F, where P=A H^C and A>=1. The payload, w and F use the
exact #6719 three-bit logical-symbol codec and declared physical local markers;
their entry heads are at the first logical data symbol. The caller owns the
code list and supplies the correct source-label association. Codes have no
numerical interpretation inside this producer.

`producer.build(q,N,Q)` emits one finite table on thirteen tapes, independent
of w,C,F,A and V. Four are the borrowed width, codes, fibre descriptor and
payload. Nine owned roles start blank at declared origins. A complete success
visits every fibre in physical order. At its single documented `ready` PC it
exposes exactly C chronological raw-field records on PREFIX, with its head on
the first data cell immediately to the right of its local marker. Each field
is the unchanged numerical record format:

    Q source-code bits; WORD_END;
    m canonical high digits, each lambda bits then WORD_END;
    RECORD_END.

The physical alphabet is a fixed bijective renaming of `records.py`'s symbols.
There is no numerical decoding in that renaming. A consumer matching N=64 can
read the emitted record through the unchanged `Fields` class; other N require
their matching dimensional consumer. The emitted table's ready instruction is
a literal jump to its continuation. It executes **no numerical callback**.

The payload has merely been read at this port. Its bytes and head, both input
headers, and the chronological codes are restored on complete return. All
owned symbols and local markers are erased. Previously visited backing is
still counted. Successful execution is the theorem's domain; arbitrary malformed
input rollback and an interrupted numerical consumer are not supplied.

## 3. Construction and all-size correctness

The first two literal decoders copy w and F into owned binary words, preserving
the three-bit source packets. The unchanged #6719 `high_program(q)` physically
computes c from w. The program copies c, multiplies the copy by the fixed q,
and appends one high zero. Thus it obtains the exact word extent lambda without
receiving a template or modulus-length oracle. It pads c to this extent and
zeros the copied word to form the extent template. Source binary-to-unary code
produces a guide of exactly F marks. Its positive canonical-input checks remain.

For each code encountered, the initializer copies its Q bits and creates m
zero words by scanning the template, followed by their delimiters. This STATE
tape has the numerical consumer's chronological record order. The initializer
counts fields only by reaching the physical end of the code list.

At each fibre, the program copies STATE to PREFIX, rewinds both, reaches ready,
erases PREFIX, and consumes exactly F encoded payload bits using the guide.
It then increments the last matrix-entry word in the **first chronological
field**. Ripple carry is binary. A finite three-state comparator scans that word
and padded c together from low to high: its state is the most significant
unequal-bit comparison encountered so far. Thus it returns the exact comparison.
An increment below c finishes; equality to c resets the word to zero and carries
to the preceding row-major entry. Overflow of all m entries carries to the
next chronological field. Overflow of the final field leaves every digit zero.

Induction on matrix digits proves that field i represents

\[
 h_i=\sum_{k=0}^{m-1}G_i[k]c^{m-1-k}.
\]

Induction on field carries then proves that, at fibre ordinal t, field i has
`h_i=floor(t/H^i) mod H`. The chronological code stored beside it never changes.
This is exactly (1), including every high matrix, every old global age and every
outer stock repetition. At c=1 all digits reset on every advance; each complete
cube has one element and the same argument applies.

The payload terminator is accepted only at a complete cube boundary. It rejects
an empty input, a partial F-bit fibre or a partial high cube. Every successful
return therefore contains a positive whole number of cubes. The consumer port
does not need a supplied numerical H, field count, prefix index or row count.
There is no vector indexed by a runtime address, host iterator, host recursion,
runtime tape selection or per-depth tape creation in the emitted program.

There is no reset compaction: all chronological records remain present even
when a later UNIT descriptor makes earlier numerical fields dead. The numerical
evaluator can skip their arithmetic under its inherited rule while still finding
later fields at their original global slots.

## 4. Complete producer cost and retained backing

Write ell_w=bitlength(w), ell_F=bitlength(F), e_q=bitlength(q), and

\[
 B=Q+2+m(\lambda+1),\qquad S=CB.
\]

S is the complete numerical-prefix symbol count, including codes and every
delimiter. The following bounds count the actual branch, write, unit move,
goto and halt instructions, rather than Python elapsed time:

| Phase | Sufficient transition bound |
|---|---:|
| Header decoding, inherited c production, padded cap/template | `1000(e_q+1)(w+1)^2 + 100(ell_F+1)` |
| F guide, its retirement, decoded-F retirement | `100(F+ell_F+1)` |
| State initialization and eventual retirement | `100(S+1)` |
| One complete PREFIX copy, rewinds and erasure | `25S+40` |
| One encoded payload fibre, guide return | `25F+20` |
| One complete field-carry operation and state return | `100S+100` |
| One next-fibre/end inspection | `10` |
| Final borrowed-payload rewind | `10V+10` |

These constants are intentionally loose. They are checked by expansion of the
emitted primitive loops. The three-bit branch has three symbol branches, four
unit moves and one final jump. PREFIX copying uses six instructions per symbol;
its two full rewinds add at most six per symbol. Clearing adds at most seven
per symbol including its return. The guide loop has fewer than twenty-five
instructions per payload bit including its amortized return.

For one attempted digit, ripple and its return use at most `7 lambda+8`
instructions. The comparison, both returns and control use at most
`11 lambda+11`; resetting a digit adds at most `7 lambda+5`. The preceding-word
seek adds at most `3 lambda+5`. Initial/final scans and code skips within a
field add at most `6m(lambda+1)+Q+10`. Even if every digit of every field carries,
the complete advance and whole STATE rewind fit `100S+100`. No average-case
carry assumption is used here.

For the inherited high producer, the binary-to-unary countdown costs at most
44w by its retained proof. Multiplication by fixed q processes a word of at
most `k e_q+1` bits at the kth multiplication; only a carry below q enters
finite control, and draining it takes at most e_q further bits. Summing the
linear scans for k<w, including width-guide erasure, gives the displayed
quadratic setup allowance. Copying, the additional fixed-q multiplication,
the high-zero margin, padding and literal header decoders fit its remaining
slack. The F conversion uses the same retained countdown argument. All
tables/compilation are fixed once q,N,Q are fixed; their construction is not
included in the runtime interpreter counts and is not claimed free in a final
compiler-admission theorem.

Since ell_F<=F and P>=1, these phase bounds imply the uniform explicit invoice

\[
 T_{\rm producer}\le
 10000(e_q+1)(w+1)^2+1000P(S+F+1).
\tag{2}
\]

It includes descriptor production, every code/word scan, payload access,
rewinds, repeated occurrences and erasure. A numerical consumer's work is
excluded, explicitly: substituting a restoring finite subroutine at ready
adds the sum of its actual occurrence costs, its fixed interface transitions,
and its workspace. Six coefficient preparations at an ordinary three-ADD leaf
remain six unless another proved algorithm removes them; #4008/#4059's
distinction is retained.

For valid complete isolated execution, every visited interval is explicit.
The borrowed encoded width, F and payload spans contain respectively
`3 ell_w+7`, `3 ell_F+7`, `3V+7` cells. The code list occupies `C(Q+1)+2` cells.
The nine owned spans, in role order W,F,CAP,TEMPLATE,W_GUIDE,WORK,F_GUIDE,STATE,
PREFIX, contain

    ell_w+2, ell_F+2, lambda+2, lambda+2, w+2,
    max(ell_w,ell_F)+2, F+2, S+2, S+2.

Every one of these cells is actually visited. Initialization or its first
complete pass reaches the far endpoint, and local rewind reaches the marker.
No instruction crosses the marker. There is no intermediate word longer than
its stated span: in particular, cap production precedes padding, and the
template reaches its maximum only after the additional high zero. Reuse of
WORK gives a maximum, not a sum of historical word widths.

Thus the additional owned visited backing is exactly

\[
 K_{\rm owned}=2S+2\lambda+w+F+\ell_w+\ell_F+
                 \max(\ell_w,\ell_F)+18,
\tag{3}
\]

and the full isolated visited-cell count is exactly

\[
 K_{\rm isolated}=3V+2S+2\lambda+w+F+4\ell_w+4\ell_F+
                  \max(\ell_w,\ell_F)+C(Q+1)+41.
\tag{4}
\]

Previously occupied/visited backing and any consumer inventory remain in
K_entry. Translated local origins change neither count. Completed calls at
the same fixed origins reuse the maximum of these spans; erasure does not
subtract their visited cells. This is a direct count of this producer, not a
new geometric-space theorem or a restatement of #6879.

### When the local invoice is O(V)

The isolated #6719 shape domain permits arbitrary depth, width and F. Equation
(2) is retained on that full domain; a uniform local O(V) conclusion does not
follow merely from the address bijection. For example, at w=1,F=1,A=1, the
single emitted prefix has C records, so a producer that materializes that
prefix must write Omega(C) symbols although its payload has one bit.

A sufficient inherited numerical-source condition is a fixed root coupling
`w=ceil(e^a)` with a>0, `C<=b0+b1 log2(max(2,e))`, and a complete amortizing
fibre `F>=q^(w-1)`. Then for w>=2, `log2 e<=a^-1 log2 w<=a^-1 w`, so
`S=O_(q,N,Q,a,b0,b1)(w^2)`. The elementary factorial bound
`w^2/q^(w-1)<=8` makes S/F uniformly bounded. Setup is absorbed into F as well,
and (2)-(3) give O(V) time and `K_entry+O(V)` additional retained backing.
The coupled w=1 case has bounded e and hence bounded C. This is the existing
complete-fibre absorption mechanism, credited to #2310/#2386; the new input
is the actual port invoice, not another proof of that general mechanism.
The final selected caller must still establish these hypotheses at its
actual invocation. They are not inferred from a finite q=3 trace.

## 5. The actual natural-root connection

`join.py` retains #6719's complete natural-root constructor and its authenticated
20,897-instruction core table. The original 31,821-instruction root table is
constructed unchanged. Four explicit entry instructions are redirected: parent
push, parent pop, leaf and final halt. Each displaced original instruction is
executed at its relay or restored continuation. All other source instructions
and their branch destinations remain unchanged.

Ten additional fixed roles suffice: one source-code stack and the producer's
nine owned roles. Its width and F inputs are wired directly to the actual
borrowed root width and R_body packets; the payload input is the actual current
leaf bank 0. The different physical BASE markers on the root headers are
explicit compile-time decoder parameters. No host observer supplies their
values or copies a decoded descriptor back into execution.

Before each actual source CALL, the stack appends code 0 or 1 according to the
source's physical phase bit. At the matching RETURN it physically removes that
last code. At a leaf it temporarily appends current code 0, rewinds the complete
list, executes the field producer, and removes only that temporary code. The
stack is erased at final root return. Its codes name the retained toy grammar's
two fixed sites. They do not claim to be a compiled selected GL_N catalogue.
Replacing these finite labels with an actual caller's source-code vocabulary
requires the final compiler/source binding.

Induction over the original CALL/RETURN structure gives exactly j ancestor
codes on entry to depth j, in chronological order. Appending the current code
therefore gives C=j+1, while the original generated body is `H^(j+1) F` and
remaining row stock supplies its outer multiplicity. Sections 2-3 apply to the
literal live bank. Restoration permits the original source continuation to
resume with exactly its old tapes, heads and bytes. Induction over completed
returns proves the original bit-complement endpoint on every original tape
for every admitted finite depth, with all ten added roles erased at root return.

This does not infer the ordinary BIT endpoint from a bit-complement fixture.
The actual numeric consumer remains a separate service. The complete new bill
is the sum of (2) over actual leaf occurrences, plus O(Q) work at each code
push/pop, the leaf code-list rewind and end seek, and constant root setup/close.
The code-list scans are at most O(S) per leaf and can be added explicitly to
the leaf allowance. Numerical subroutine calls are not present in this table.
Source recursion/router/frame work is retained unchanged and fully paid by
the predecessor, rather than being relabelled as the isolated producer tariff.

The added code stack visits exactly `C(Q+1)+2` cells at maximum depth C-1.
Together with (3), this gives the new role backing for this fixed-depth source
grammar; source backing and borrowed markers remain charged separately. No
per-child physical tape is allocated. All completed siblings reuse these roles.

For the exact L=4,q=3,N=1,w=2,d=2,T=F=1 root, the joined table has 32,748
instructions and 37 tapes. It executes all four real leaves and all 108 complete
chronological prefixes. Its 1,539,296 transitions equal the original 1,449,116
plus 90,180. The ten added roles visit 107 cells; total additional visited
backing is 109 cells because two borrowed header markers were not visited by
the original source execution. These finite values corroborate
the preceding induction; they are not an extrapolated all-size constant.

## 6. A numerical mismatch using the unchanged evaluator

The separate numerical experiment uses the exact pinned `controller.py`,
`records.py`, `words.py` and `matrices.py` without changing their numerical
code. It constructs a legal **synthetic** 64-dimensional rank-one fixed
vocabulary. This is not a selected source-catalogue occurrence. Both template
preparations are the identity, with projector `E_1=diag(1,0,...,0)`.
All coordinates except 0 and 63 are identity. The two low charts, including
one nonzero high entry at (63,63), have the blocks

\[
 g_0(h)=\begin{pmatrix}1&1\\1&2+3h\end{pmatrix},\qquad
 g_1(h)=\begin{pmatrix}1&2\\1&1+3h\end{pmatrix}
 \quad\text{over }\mathbb Z/9\mathbb Z.
\]

Their determinants are respectively 1+3h and -1+3h, hence units for all h in
{0,1,2}. Both leading projector pivots are units modulo 3, so the rank-one
Good branch is valid for every lift. Direct two-by-two inversion gives

\[
 p_0(h)=\frac{2+3h}{1+3h}=2-3h,\qquad
 p_1(h)=\frac{1+3h}{-1+3h}=8+3h \pmod9.
\]

The actual Program has root extent 262144, root unit 1, and two Good rank-one
steps, giving extents 4096 and then 64. Coordinate zero selects pivot zero at
both steps, so its incoming weight is

\[
 A_0=p_0(h_0)p_1(h_1)=7+3h_0+6h_1\pmod9.
\]

There is also a third, current field with its own source code. `Callback.weight`
must not read that current field; `Fields.read` enforces the inherited scope.
All three records are supplied directly from a literal emitted PREFIX through
a readonly, unit-move alphabet adapter. `Word.inspect` is disabled during the
actual callback. Prefix and Program bytes/heads and numerical ownership are
checked at the completed callback endpoint.

The first row-major high increment changes exactly matrix entry (63,63). At
physical fibre ordinal one, (1) therefore gives `(h0,h1,h2)=(1,0,0)` and A0=1.
The unmodified chronological directory order instead gives `(0,0,1)` and A0=7.
The actual unchanged numerical evaluator returns these different values.
This is a coefficient counterexample to the proposed direct order identification,
not merely a difference in artificial integer labels. For example, an intended
weighted interchange applied to a unit tail basis value distinguishes the two
coefficients immediately.

The literal 64-dimensional producer runs only to its second prefix in each
arm. Its full high domain is `3^12288`, which is not executed. The retained finite
payload prefix has a valid extension to the admitted complete stream, and every
observed instruction precedes access to that extension. No terminal or full-cube
claim is made for these prefix executions. Complete production and cleanup are
separately tested on finite N=1/2 cubes and a full N=64,w=1 cube. The all-size
proof, rather than multiplication of these finite cases, connects the scopes.

## 7. Remaining obligations

The new result supplies physical raw-field production with the correct payload
order, global ages, codecs, return semantics and bill. Inherited numerical
arithmetic, source matrix preparation and Good/Pair/UNIT semantics retain their
own assumptions and credit. The old shape table still has a bit-complement leaf.

A final selected caller still needs its exact source-code/Program producer,
low-class and route orientation binding, a paid numerical-service insertion,
ordinary BIT/Gaussian payload semantics, complete stock and precision invoices,
and its outer parameter/payload producer. The selected frontier and all five
framework assumption statuses are unchanged. Independent scientific admission
is separate from author-side AI proof review and finite machine replay.
