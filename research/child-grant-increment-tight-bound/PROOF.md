# Exact local cost of the emitted child-grant increment

Source: thu-nmrc PR6719 head `3bad39ffd4faf7e8cb1bc5b47769cbb28511f797`, shape/producer.py:increment, with the unchanged David Arias PR2776 assembler and counters.emit_rewind. The source already states the exact formula below and the coarse bound18k. This contribution supplies an external actual-emitted-macro check and the sharp uniform homogeneous bound15k. Ordinary binary-counter amortization remains predecessor/classical work, not a new generic arithmetic theorem or a kappa improvement.

## Proposition and exact boundary

An owned local tape has LEFT at0, head1 and either RIGHT alone at1 (temporary zero) or canonical least-significant-bit-first binary digits for n>=1 at1..ell(n), with RIGHT atell(n)+1. Body symbols are exactly ZERO/ONE, the top digit is ONE, and there are no interior markers. Newly reached growth cells beyond RIGHT are owned blank cells. Other fields, tape segments and spectators are outside this region.

Execute the literal increment macro inline, including its rewind, until its following continuation. Count each emitted branch, write, unit move and goto as one transition. No setup, caller-loop instruction, descriptor conversion or wrapper HALT is included. After each valid call, the value is n+1, the head is1, LEFT is unchanged, RIGHT and body are canonical, and no other tape is accessed. The macro does not promise detection or rollback for arbitrary malformed backing.

For k>=1 consecutive calls from temporary zero, the exact count is

    C(k)=13k-7s_2(k)+5ell(k) <=15k,

where s_2 counts set bits and ell is positive binary length. Equality holds if and only if k=4. Thus15 is the smallest coefficient c for a bound C(k)<=c*k for every positive k with **no additive allowance**. This is not an optimal asymptotic-coefficient claim: the exact formula has leading coefficient13 and logarithmic corrections. The macro's counter region visits precisely ell(k)+2 cells over that prefix, excluding untouched backing/spectators and any separate entry preparation.

## Literal path semantics and rewind count

Let t be the number of trailing ONEs at entry. Each such digit executes branch, write ZERO, move right, goto: four transitions, replacing it by ZERO. If the next symbol is ZERO, branch/write ONE/goto take three more transitions. The remaining higher digits and RIGHT are unchanged. The value changes by 2^t-sum_(j<t)2^j=1, and canonicality is preserved. The head entering rewind is t+1.

If the next symbol is RIGHT, all d=t old digits were ONE, including d=0 for temporary zero. Branch, write ONE, move right, write new RIGHT, goto take five transitions. The new high ONE and lower ZEROs represent2^d=n+1. The new RIGHT is written into an owned blank cell atd+2. The head entering rewind is d+2. This explicitly uses the growth-ownership premise; that write is not a promise to preserve occupied hidden backing.

The unchanged emit_rewind first moves left, then repeats a LEFT-test with left movement/goto on non-LEFT, and finally moves right. From head h>=1 with its first LEFT at0, its cost is

    1+3(h-1)+1+1=3h.

It changes no symbol and returns head1. Therefore nongrowth costs4t+3+3(t+1)=7t+6, and growth costs4t+5+3(t+2)=7t+11. These include all source macro return motion. A standalone harness HALT would add one transition per invocation if actually executed; it is deliberately the following stop boundary here.

Each local operation uses the macro's tape parameter, and rewind receives the same parameter. Other tapes are untouched. A fresh-label, valid-tape-index renaming preserves this isolated table and its counts. This does not check every enclosing producer/linked program or its label/input custody.

## Summing exactly and sharpening the source bound

For n>=0, the next increment has

    t(n)=1+s_2(n)-s_2(n+1)

trailing ONEs. Summing n=0..k-1 gives k-s_2(k). Growth occurs exactly when the new positive value is a power of two, so the first k calls have ell(k) growths. Summing the two literal path counts yields

    7(k-s_2(k))+6k+5ell(k)=13k-7s_2(k)+5ell(k).

This is the source's existing exact expression. To sharpen its stated18k envelope, put d=ell(k). Then k>=2^(d-1) and s_2(k)>=1. Consequently

    15k-C(k)=2k+7s_2(k)-5d >=2^d+7-5d.

Let D(d)=2^d+7-5d. Its values at1,2,3 are4,1,0. For d>=3,

    D(d+1)-D(d)=2^d-5>0.

Thus D is nonnegative for all d>=1, with its only zero atd=3. Equality in the bound also requires k=2^(d-1) and s_2(k)=1, hence k=4. Direct substitution gives C(4)=52-7+15=60. Any c<15 fails at this actual prefix. No finite range is used to prove the all-k inequality.

For space, after the first k calls the largest RIGHT position is ell(k)+1. Forward growth and rewinds visit every position0..ell(k)+1 and no position outside. Hence precisely ell(k)+2 counter cells are visited. Rewriting or releasing a cell does not remove its prior visit from this count. This is local counter space, not the complete producer stock/tape envelope.

## Arbitrary starting values and two necessary qualifications

Extend C(0)=0, ell(0)=s_2(0)=0. Starting at an arbitrary canonical n>=0 for k further calls gives the exact difference

    C(n+k)-C(n)
      =13k-7[s_2(n+k)-s_2(n)]+5[ell(n+k)-ell(n)].

An initial-potential term is therefore necessary. In particular, n=2^d-1 has one next call costing7d+11; n=3 costs25. Neither18 nor15 is a universal per-call bound. The actual producer initializes its output counters at temporary zero, which is the required premise for the homogeneous bound; this review does not execute its quotient/product loops to bind their call counts.

Likewise, the arbitrary dirty sentinel tests are outside the visited owned growth region. The macro does not guard or preserve an occupied cell that it must overwrite as a new RIGHT. No claim of arbitrary dirty growth backing or free restoration follows.

## Actual-emission evidence and limits

The shared emitter authenticates the complete producer/machine/counter source bytes, extracts the unchanged top-level increment FunctionDef with its exact four-argument signature, and supplies the original source assembler/constants and emit_rewind. It does not execute producer top-level imports/build, router, source checkers, or the source Machine/Tape interpreter. The constant-size wrapper places HALT precisely at the macro fall-through and a separate reject continuation. Tuple-to-JSON-list conversion preserves every emitted opcode, operand, case and target.

Two separately authored sparse/dense table interpreters use this **shared candidate construction**. They are not independent end-to-end constructors. Their bounded scientific plan covers1024 consecutive from-zero calls, ten independently initialized all-ONE carries through256 bits, exact endpoint/marker/head/sentinel/spectator checks, actual semantic table mutations and strict parser controls. Complete certificates retain every measured row and the actual table. Finite agreement corroborates this literal macro; the written induction above supplies the unbounded result. First-run/normal/optimized/tamper and integrity receipts determine which executions actually passed; none is inferred merely from this plan.

The source's exact formula/emitter and parent counter ABI retain thu-nmrc/David Arias credit. Jose Manuel's binary control, JoyboyBrian's divisor lineage, Ali Romman's PR5829 geometry, and retained stack/codec/return authors remain credited. ToikY with substantial OpenAI Codex and separate AI implementation/proof roles supplies this scoped external audit/refinement, Apache-2.0. Complete child-shape quotient/product/grant counts, linked routing, emitted child consumers, full1000V/100V or94V/13V bills, ownership retirement, H-from-width, ancestor/depth, precision/native/compiler/outer and all five selected assumptions remain outside. No frontier, supplier invoice, selected exponent or full multiplication conclusion changes.
