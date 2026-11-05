# Exact bill and safe 60(S+K) envelope for the literal grant producer

Source: thu-nmrc PR6719 head `3bad39ffd4faf7e8cb1bc5b47769cbb28511f797`, shape/producer.py:build, using the unchanged David Arias PR2776 machine/assembler/counter. This is an external source-bound proof and actual-program audit of one ordinary descriptor producer, not a new arithmetic theorem or a complete supplier invoice. The source's own producer checks and earlier coarse bills retain their credit.

## Contract and counted object

Fix any integer L>=2 before runtime. Let A,H,R be positive integers with L*H dividing A. Define q=A/(L*H), K=H*R and S=A+H+R. Three distinct tapes0,1,2 contain canonical positive LSB-first binary A,H,R, each with LEFT0, head1 and RIGHT atell(value)+1. Outputs3,4 and work5..8 start blank at local origin0, with head0. All growth reached by the program is owned blank backing; untouched entry backing has a separate bill. The nine roles are distinct physical tapes.

The literal source table P_L=producer.build(L) uses only the fixed L during construction. It obtains A,H,R only from physical runtime headers. Its successful execution returns the original three input packets and heads unchanged, owned binary outputs q and K with head1, and four fully erased scratch tapes with head0. Owned outputs receive no productive credit.

Count every emitted branch, write, unit move, goto and the **actual success HALT** as one transition. Compilation/table generation, input encoding/backing, delivered-output consumption/retirement and child routing are outside this runtime producer bill. This differs from the isolated increment's fall-through boundary, where a following wrapper HALT was excluded. There is no rollback/cleanup promise for rejected malformed inputs.

Write ell(x)=bit_length(x) and p(x)=popcount(x) for positive x. The unchanged positive binary-to-unary helper has exact cost, excluding caller marker installation/final HALT,

    c(x)=24x-7p(x)+15ell(x)+12.

The source increment has exact from-zero prefix cost

    C(x)=13x-7p(x)+5ell(x).

Both expressions are predecessor/classical counter evidence. The latter obeys the separately proved sharp homogeneous15x bound; this does not make15 a per-call bound at arbitrary initial state.

## Functional invariants and full retirement

The program installs the markers of both zero outputs and all four work fields itself. Three conversions produce UNIT^A RIGHT, UNIT^H RIGHT and UNIT^R RIGHT on guides5,6,7. The converter restores each input packet/head1 and leaves its reused work body empty/head1 with LEFT0 still installed. These are the exact canonical helper contract, not free host-decoded integers or a reset performed by the test harness.

For the quotient, after j complete groups the A-guide head has advanced through exactly j*L*H marks and output3 equals j. The fixed loop unrolls L complete scans of the H guide per group. Each H mark requires one A mark and advances both guide heads. Encountering A's RIGHT midgroup rejects. Complete divisibility makes the process end after q positive groups, at A's RIGHT, with output3=q and H's guide at its RIGHT. The binary output starts at temporary zero and is incremented, rather than written from a host quotient.

The product rewinds H, then scans R completely once per H mark. After h whole R scans and r marks of the next scan, output4 equals h*R+r. It starts at temporary zero and finishes at H*R=K; both H/R guides then stand at their RIGHT markers. Source increments return each output head to1. No step reads a decoded host product, variable tape index, coordinate or step statistic.

A literal reverse pass on each guide erases RIGHT, every UNIT and LEFT, stopping at0. The reused conversion work is empty except its LEFT; the final emitted move/test/write removes that marker and halts at0. Thus every visited scratch cell is erased. The two owned output descriptors remain live; this proof does not retire them, clear child payloads or assign their lifetime zero cost.

## Exact transition ledger

Marker installation costs22: five instructions per output and three per other work field. The conversion subtotal is c(A)+c(H)+c(R).

There are M=qL scans of H during division. The first rewind begins at head1 and costs3, while later ones begin at H+1 and cost3(H+1). Each H scan itself costs5H+1. Hence their total is8A+4qL-3H. The quotient also has q+1 group tests, q returns and its complete increment prefix C(q). Its exact subtotal is

    Q=8A+4qL-3H+C(q)+2q+1.

The product's initial H rewind costs3(H+1). Its H tests costH+1. The R rewinds total3K+3H-3R, including the first rewind from1; R tests/advances total3K+H. H advances/returns cost2H. Together with C(K),

    P=6K+10H-3R+C(K)+4.

Finally each guide retirement costs4x+5. The last WORK move/test/erase and success HALT cost4, so retirement including HALT is4S+19. Combining all phases gives the exact producer count

    T=c(A)+c(H)+c(R)+C(q)+C(K)
        +12A+11H+R+6K+(4L+2)q+46.                    (E)

All negative terms and first-rewind savings are retained before bounding. Omitting the success HALT changes(E) by one; adding an unrelated following consumer changes the counted object.

For the smallest L=2,A=2,H=R=1, q=K=1: setup/conversions total193, quotient35, product28 and retirement35. Thus T=291. This planned exact witness is independently checked by the actual literal interpreters; it is not a substitute for their execution record.

## A uniform producer-only bound

Since A>=L*H>=2, its binary length obeys ell(A)<=A/2+1. For d=ell(A)>=2, this follows from A>=2^(d-1)>=2d-2; the latter is equality atd=2,3 and increases thereafter. Also p(A)>=1. Therefore

    c(A)<=63A/2+20.

The retained c(x)<=44x bounds H and R, and C(q)<=15q, C(K)<=15K. Applying these to(E), then qL=A/H<=A and q<=A/2, yields

    T<=56A+55H+45R+21K+66.

Its difference from60(S+K) is at least

    4A+5H+15R+39K-66 >=8+5+15+39-66=1.

Hence T<=60(S+K) for every promised input and every fixed L>=2. This is a safe homogeneous envelope, **not a claim that60 is sharp**. It counts the producer alone; a source statement including actual consumers or linked routing is a different scope.

## Visited local space

Each input visits precisely0..ell(x)+1. Each output visits0..ell(q)+1 or0..ell(K)+1. The three guides visit0..A+1,0..H+1,0..R+1. Reused WORK visits0..max(ell(A),ell(H),ell(R))+1. Movement is unit-step, the marker rewinds never pass LEFT0, and every listed extremum is reached on valid inputs. Therefore the exact sum of distinct visited cells across the nine local tapes is

    F=S+ell(A)+ell(H)+ell(R)+ell(q)+ell(K)
        +max(ell(A),ell(H),ell(R))+18.               (V)

Erased cells remain in this visited total. It excludes untouched backing, not its storage bill. Using ell(x)<=x, q<=A/2, max(ell(A),ell(H),ell(R))<=S and S>=4 gives

    F<=3S+q+K+18 <=(7/2)S+K+18 <10(S+K).

For the small witness F=30. The source's visited interval accounting supplies the same conservative10(S+K) envelope; the present exact ledger retains the distinct local extents and explicit lifecycle boundary.

## Actual-program evidence and remaining obligations

The source-authenticated shared emitter imports the exact four-module producer/machine/counter/router closure and invokes only build(L) at L=2,3,4,7. Router definitions load as an ordinary dependency, but no router builder, linked_split, retire_delivered, original checker or source Machine/Tape interpreter is invoked. A,H,R never enter source construction. Own sparse/dense interpreters execute the emitted table data with success HALT charged.

The planned bounded domain is256 complete-grid cases plus five boundary cases, totaling261. Each must check restored raw inputs, actual canonical outputs, heads, complete scratch erasure, all sentinels, observed steps/visits and actual semantic/parser controls. The implementations share candidate construction and do not claim independent end-to-end constructors. First/corruption/normal/optimized/export/cold/hosted receipts, rather than this planned paragraph, establish which runs passed. The written invariants and ledgers establish all-size implications under the named helper/owned-tape model; finite cases alone do not.

Source functional arithmetic, converter formulas and producer design remain thu-nmrc/David Arias/classical work. Ali Romman5829 geometry, Jose Manuel/JoyboyBrian binary-control/divisor and retained stack/codec/return lineage retain their credit. ToikY with substantial OpenAI Codex and separate source-aware AI implementation/proof roles supplies the external full-program audit and refined local bill, Apache-2.0. H-from-width, actual ancestor/depth descriptors, child payloads/routes/consumers, full94V/13V or1000V/100V compositions, entry/callback/compiler/precision/physical supplier and all five selected assumptions remain outside. No productive/paid supplier profile, kappa, selected frontier or scientific adoption changes.
