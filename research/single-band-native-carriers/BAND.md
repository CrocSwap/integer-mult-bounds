# One finite band of native tensor calls

Let a native instruction have ambient rank \(A=a^v\), productive occurrence ranks
\(k_i\), and chronological paid occurrence ranks \(r_j\). Occurrences with the
same rank keep different labels. Both physically realized #8027 words satisfy
\(k_{\min}\ge2r_{\max}\). Each job at a paid cut carries its full owner's
current basis and its ordered active axes. In that basis, disjoint subsets give
commuting tensor factors. A completed axis has order dividing four.
The full native program must implement that action on its simultaneous
independent productive fields. The new construction calls that program.

Write \(t=1-C\) with \(0<C<1\), \(T=\sum_i k_i^t\), \(P=\sum_j r_j^t\),
and suppose \(P\le(1-\epsilon)T\). For the compact binary and both positive suppliers the 128-factor strict moment surplus exceeds \(2^{-14}\). They keep productive tuples of rank at least \(16^{128}\), split every paid tuple at the cap \(12^{128}\), and use \(L=2^{15}\). For the high-rate binary supplier with 228 factors set \(C=17108907955/2^{42}\). Keep all productive tuples of rank at least \(15^{228}\) and split each paid call at \(12^{228}\). Its strict surplus exceeds \(2^{-34}\) and it uses \(L=2^{35}\). For example, outward dyadic moment intervals with tilts \(19/64\) and \(31/64\) give a normalized debit less than \(1-131151226/10^{18}\). Each installed word has \(L\epsilon\ge2\) and \(k_{\min}/r_{\max}\ge 2\).
The algorithm accepts any integer \(L\ge 2\). The price theorem below uses
\(L>2\) and \(L\epsilon\ge2\).

## Finite geometry and integral loans

For target rank \(n\), set \(n'=4\lfloor n/4\rfloor\), \(m=n'/4\) and
\(U=m/A\). A stopped rank \(U<L\) costs \(n\) elementary jobs and does
not generate a raw table. Otherwise choose the least integer \(G\) with
\((k_{\min}/r_{\max})^G>U\). At each paid prefix \(p\) and productive suffix
\(a\) with \(|p|+|a|=G\) set

\[
x(p,a)=\prod_{j\in p}r_j\,\prod_{i\in a}k_i/r_{\max}^G .
\]

Use the real raw program with \(c(x)=\lfloor x\rfloor-1\) integral columns
exactly where \(L\le x\le U\). Then \(Ac(x)\le m\) and \(c(x)\ge1\).
The first layer has every \(x>U\). The last has every \(x\le1\).
If \(U\ge L k_\min/r_\max\) then at least one layer has an active unit.
Follow occurrences with paid rank \(r_{\max}\) and future rank \(k_{\min}\).
Their only ratio per step is \(r_{\max}/k_{\min}\). At the first crossing
of \(U\) the result is greater than \(U r_{\max}/k_{\min}\ge L\).
For a narrower range the compiler directly tests for a nonempty band and
serves an empty band by elementary axes. All funded fixed ranks below use
the sufficient inequality.

There is a unique edge from \((p,(i,a))\) at cut \(j\) to port \(i\) of
\((p j,a)\). If their virtual columns are \(y,x\), then
\(r_j y=k_i x\), with \(y\ge2x\). For two active endpoints,

\[
0\le r_j c(y)-k_i c(x)<2k_i .
\]

Indeed \(z-2<c(z)\le z-1\). For the lower bound use \(k_i\ge2r_j\).
The child borrows the first \(k_i c(x)\) ordered axes from the parent's
actual request. Its select operation preserves the full basis, including the
other coordinates. Satisfy each remaining axis in the same basis before the
suspended parent resumes. The difference above counts all those leaves.
The payload remains on the same owner. Its arbitrary complement is present
during the entire child and every later leaf.

If an active child has no lender for a port, its unique potential parent's
\(y>U\). Allocate a real external incidence of actual size
\(s'=k_i c(x)\) and virtual size \(s=k_i x=r_j y>U\). Then
\((1-2/L)s\le s'\le s\) and \(s'\le m\). If an active lender has no child
for a cut, its virtual \(e=r_j y=k_i x < k_{\max}L\). Fulfil the entire
actual request with \(r_jc(y)\le e\) elementary axes.
These cases include cuts incident to empty time layers.

For any fixed chronological path, different active units have disjoint owner
pools. External slots are disjoint. At a paid cut one parent gives one job
to at most one child. A new private field has a fresh owner. This proves the
owner statement by induction. Open each group's native continuations in the
specified source order. At each paid cut obtain the exact jobs from all
current continuations, visit the next paid path, and restore all incoming
requests including their residual axes. Resume the raw words after the cut
returns. Empty layers with active descendants must still run those descendants.
A terminal child can perform its leftover leaves before returning. In the
iterator a job outside every consumer is disjoint from their owner pools at
this cut, so it can also complete after those consumers.
band_compiler.py computes the incidence plan. epoch_tape.py emits a complete epoch and replays its serialized stream at each outer round.
It never forms a job from an owner identity alone. Each subjob selects axes
from its typed parent. The underlying powered source remains responsible for
closing each raw adapter, including all of its temporary fields.

Each terminal or residual axis calls the actual recursive leaf service. At a
fixed complex rank this is a whole bundle of consecutive physical windows.
It performs the saved group's operation on its complete owner. At a fixed
binary rank it consumes the actual line projector and full complement chart.
No subset is treated as a free move. The completed operations on two
disjoint parts commute in the enclosing job's basis. They need not commute
with a pending native adapter. For that reason all restoration is inside
that parent's suspension.

## Normalized paid price

Let \(S\) sum \(s^t\) over all external occurrence ports, and \(E\) sum
\(e^t\) over all terminal cuts before the replication of a round. Summing
all active node identities \(Tx^t-Px^t=(T-P)x^t\) gives exactly

\[
S=E+(T-P)\sum_{\mathrm{active}} x^t .
\]

Equal virtual edge terms cancel with the same labeled edge. The actual
integral cardinalities can differ. Write \(D=(k_{\max}L)^C\).
Each terminal costs at most \(D e^t\) because \(e<k_{\max}L\).
The sum of residual leaves charged to a given child costs at most
\(2\sum_i k_i\). For every \(x\ge L\),
\(D(k_i x)^t/k_i \ge L\), since \(k_i\le k_{\max}\).
Consequently the residual sum is at most
\((2/L)DTx^t\le D(T-P)x^t\). The whole actual leaf count of one
copy-round is at most \(DS\).

Let \(q_s\) be the least power of two with \(q_ss'\ge n'\).
The retained fourth-order row selector covers each coordinate once or five
times on that owner in its \(q_s\) successive rounds. It has exactly \(s'\)
distinct axes per invocation. Let \(R=\max_s q_s\) and allocate
\(h=\sum_s R/q_s\) independent slots per copy. Then
\(B=2^{\lceil\log_2(15h)\rceil}\) productive owners and
\(z=\lceil B/h\rceil\) complete copies satisfy
\(B\le zh<(16/15)B\). Open every padded owner on an independent zero
field, serve all rounds, and check/retire it on the restored zero
output. Finish the \(n-n'\) missing axes on each productive owner.
For each occurrence,

\[
q_s s^t
=\frac{q_ss'}{n'}\,\left(\frac{n'}s\right)^C\,\frac{s}{s'}(n')^t
\le \frac{2(4A)^C}{1-2/L}(n')^t .
\]

Thus the normalized number \(F(n)\) of downstream elementary jobs satisfies

\[
F(n)\le n-n' +\frac{32}{15(1-2/L)}
(4A k_{\max} L)^C (n')^{1-C}.
\]

This pays the actual number of terminal and residual requests. The estimate
applies to the nonempty band. A power-of-two production rank has no tail.
A sufficient binary physical price includes the outer factor \(32\). A
complex physical price includes the outer factor \(2\). All finite losses
in the band price are constants in bits once the true native word is fixed.
For \(C=2043/2^{19}\) on the positive side, \(a=153\), largest true productive rank 129 and \(L=2^{15}\), the log of the *full* normalized prefactor including the outer two is below
\(1+5/4+C\lceil\log_2(4(153\cdot129)^{128}2^{15})\rceil=1236735/131072<10\).
Here \(32/(15(1-2/L))<9/4<2^{5/4}\). For the compact contract
\((C-\kappa-5g)H_M=10.238984947821875\), with \(\kappa=0.00387992803556\), \(H_M=610000\) and \(g=10^{-14}\). For the high-rate contract priced in [PR #8029](https://github.com/CrocSwap/integer-mult-bounds/pull/8029) the same complete allowance is \(10.5568951935\), with \(\kappa=0.00389011519729\) and \(H_M=1600000\). The physical binary charges, including factor 32, are bounded by 14 bits for the compact 128-factor rule and 19 bits for the high-rate 228-factor rule. The participating binary ranks and previous-stage movements have their separate recursive price calculation. Numerical moves and generation below are also separate from \(F\).

## Installed epoch and fixed-head generation

For each production carrier \(N=2^H\), the conservative test \(H\ge512v\) holds. The strict words have \(v\in\{128,228\}\), \(A<2^{8v}\), and \(W\le2^{16v}\) productive labels. The binary program has 18,906 productive raw labels, 104,904 paid raw labels and total paid raw rank 285,600. For 228 factors let \(P_\#\) count the actual chronological slots after splitting. A tuple of rank \(r\) uses \(\lceil r/12^v\rceil\le1+r/12^v\) slots. Summing over every ordered tuple gives
\[
W+P_\#\le18906^v+104904^v+(285600/12)^v
\le147610^v<2^{18v}.
\]
This counts distinct occurrences, including every final partial block. Since \((5/4)^{13}>2^4\), the high-rate binary step gives \(vG<13H/4+v\). Hence the number of candidate units, including rejected ones, is bounded by
\[
\sum_{d=0}^G P_\#^d W^{G-d}
\le(W+P_\#)^G<N^{18(13/4+1/512)}<N^{60}.
\]
For either 128-factor supplier use \(W+P_\#<2^{29v}\), counting all raw tuples and splits up to the ambient rank. Since \((4/3)^5>4\), the lower step gives \(vG\le5H/2+v\) and the same binomial sum is below \(N^{75}\). Across all three installations the numerator and denominator of any virtual column have fewer than \(27H+2\) bits by \(A^G<2^{8vG}\). All later common bounds use \(N^{75}\) candidates, at most \(N^{76}\) external sources, \(R\le N\), \(h\le N^{77}\), \(B\le N^{79}\), and \(z\le30\). This construction has one fixed rank per program with no smaller-rank compiler group at a terminal.

Use binary odometers to visit ordered labels, paths and owners. The installed epoch records one relative selector per external port, typed loan descriptors, native opens, paid issues, closes and complete finishes. The native subprogram, its factor words and the retained plan accompany the epoch. At round \(j\) the interpreter computes the absolute owner and its ordered axes from the recorded base, size and period. Native opcodes run in the held iterator. An issued job stays in its returned basis. A finish performs every residual elementary call. The file records each operand count and variable-length base-128 nonnegative operands. The following budget even counts explicit expanded selector, native, leaf and empty-prefix visits at all rounds.

A powered-word unit needs fewer than \(2^{64}(v+1)2^{28v}<N\) basic records. Each selected tuple or fringe can list at most \(N\) coordinates. At most \(N^{75}\) units contribute. The empty prefixes add at most \(G N^{75}\) visits. At most \(P_{\#}N^{75}\) terminal sink invocations test their paid label list once each. These quantities give fewer than \(N^{80}\) structural records per copy-round, including masking and fringe work. There are at most \(30N\) copy-rounds. Including owner cleanup gives fewer than \(N^{82}\) records. Each count, leaf total or index has fewer than \(100(H+1)\) bits. A path or selector with its full tag uses fewer than \(N^3\) bits. Its serial generation by schoolbook integer arithmetic with copied selector tuples takes fewer than \(N^7\) logical accesses per record. Full enumeration of the rejected candidates and initial tables also has fewer than \(N^{89}\) accesses. All preparation and emission therefore use fewer than \(N^{90}\) indexed logical accesses.

One pointer-free implementation keeps the unsorted keys and values on tape, with delimiters and a second rewrite tape. Read and compare the saved key during a sequential search. Copy the updated records to the return tape, then erase the old tape. Use the same searches for the active ancestor set and owner bindings. Even if every access permanently saved a fresh \(N^3\)-bit entry, the complete retained plan, both temporary copies, selectors, fixed instructions and epoch stream fit within \(D_0=N^{96}\) cells. At most \(D_0^2\) head moves suffice for one complete search/update. Allow a further factor \(D_0\) for initialization, rewinds and erasure. The complete structural installer therefore uses fewer than \(N^{380}\) transitions and \(N^{96}\) cells. For the finite numeric factor expansion the predecessor allows four full pairwise copy passes over the structural store per record. Ten powers of the structural size bound that stage by \(N^{960}\). The constant number of distinct streams, raw source materialization, finite Gauss–Jordan and scalar generators, writes, cursor arithmetic and scrubbing fit \(J=N^{1024}\) at each carrier under the same fixed-interpreter convention.

Every active execution has its own next byte offset, iterator map, loan map and payload frames. A recursive call can share the same installed program head. The parent records the next offset after it has decoded the entire record. The resumed parent seeks to that byte position before decoding its next record. Each seek, including a rewind at a round boundary, costs at most the installed byte length. A serial scan over the retained owner descriptors implements frame lookup. The saved offset, fixed key and serialized logical binding fit the \(J\) envelope. Moving the program head and even rescanning and copying a fixed descriptor store per operation cost \(O(J^2)\) local fixed work. The ordinary \(O(J^{11})(1+C_{\rm prev})\) and positive/outer \(O(J^{12})\) fixed work allowances already pay multiple full byte-stream scans at each op. Full payload transfers, positive child calls, raw numerical gates and high-coordinate transposes retain their separate physical costs. All invocations reuse the same read-only image. Fields and their in-progress owners remain private to the individual activation.

A chain has only \(G\) band stages. Each stage opens at most \(v\) raw
contexts on a single causal branch of a field. A completed terminal or
residual subset is again its exact tensor Clifford. No sequence of completed
subsets contributes fresh mass or denominator debt to the exterior. The
recomputed \(148/436\)-bit allowances per raw context therefore use
\(K\le v(G+1)\) in place of the former \(v(H+1)^2\).
At \(H\ge512v\), \(872K<N\). The remaining precision, genuine owner
stock, all high values, the outer numerical service and its complete
restoration have their separate multiplier bills.

For the reproducible exposed-window witness, choose any active unit at
the *smallest paid depth* of the entire schedule. Every input of that unit
is external, as all smaller depths are inactive. Its retained repeated
rank-129 raw root is therefore a real external source. Iteration zero,
replica zero assigns it a productive owner at offset less than \(h\le B\).
Its source rank \(c\,129^{128}\) lies in \([3,m]\). The predecessor's
three-address gap and raw destination calculation apply verbatim at this
unit and force a genuine whole-window ordinary interchange on the
numerical data.

## Finite verification

check_band.py independently reconstructs both halves of each virtual edge
with exact Fraction arithmetic and compares the width, terminal, fringe
and total costs at 90 band and stopped-rank cases. A separate product of
order-four coordinate maps changes a full-field shear and swaps dependent
coordinates between paid cuts. It checks the entire owner's transformed
state every time its issuing chart resumes. The two-target, nonzero-fringe
case ran 15,840 native instances, 15,114 noncommuting cut changes and
115,200 single-axis jobs. An independent weighted-swap oracle over
the integers modulo 27 ran 71,104 leaves, including the nonempty fringe
and all three final axes. The tagged two-factor powered toy exercised
1,280 raw frames, 2,048 private owners and 768 nonzero centre visits.
The large production inequalities above are proved from the source word.
The finite tests use smaller concrete words and do not execute a full
production-dimensional epoch.

The physical epoch checker nested a complete rank-323 call inside a partially processed loan of another call using the identical installed program file. Each call used 128 independent lanes. The program contained 1,456 records in 8,481 bytes. The first call suspended at byte 654, the second ended at byte 8,481, and the first resumed by a measured seek back to byte 654. Both calls restored every external chart and all private fields. Together they read 271,392 opcode bytes and moved 271,392 bytes of seek distance. These measurements apply to this concrete small word.
