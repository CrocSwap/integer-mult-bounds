# Written review of the complete nine-tape producer

**Conditional proof/static-source PASS.** On the declared valid entry domain,
the literal producer returns the stated grants, preserves the three inputs,
erases and rewinds all four scratch tapes, and has the exact time below.
The proposed producer-only bound `T<=60(S+K)` holds; the proof actually leaves
at least one transition of slack. No sharpness of60 is claimed.

Source: thu-nmrc PR6719 head `3bad39ffd4faf7e8cb1bc5b47769cbb28511f797`,
shape-producer.build(L), increment, retained counters.emit_binary_to_unary/
emit_rewind and machine grammar, with the canonical counter proof. This is
a source-aware independent written count, not a program/import/compilation,
table execution, finite interpolation or proof-kernel result.

## Domain and notation

Fix L>=2 at compilation. Let A,H,R be positive integers with A divisible
by L*H, and set

    q=A/(L*H)>=1,  K=H*R,  S=A+H+R.

All nine roles are genuinely distinct physical tapes. Inputs0,1,2 are
canonical positive LSB-first binary A,H,R, with LEFT0, body beginning1,
RIGHT after the high ONE and heads1. Outputs3,4 and scratch5,6,7,8 start
genuinely blank at0 in all regions the algorithm will use. Future growth
cells are owned blank cells, not live data hidden beyond a marker. Source
machine symbols and one-transition-per-instruction semantics are retained.

The output counters begin as temporary zero, RIGHT alone at1 after LEFT0
installation. The following time excludes physical input preparation and
later output consumption, but includes every instruction of this producer,
including its success HALT. Malformed-input rollback/cleanup is not promised.

## Counter component and setup

An output marked_blank call costs5: blank test, LEFT write, move, body blank
test, RIGHT write. A scratch call costs3: blank test, LEFT write, move.
There are two output and four scratch calls, giving exactly22.

For a positive N, the retained binary-to-unary component preserves its binary
source and returns its unary head1 with N UNITs and RIGHT, leaving WORK empty
apart from LEFT0 at head1. This follows by copying the source, counting down
the copy and shrinking its top marker at powers of two; every unary mark is
appended for one positive countdown state. The source is never written.

The exact source count is

    c(N)=24N-7popcount(N)+15ell(N)+12.

Its static decomposition checks as follows. Copy and both rewinds cost
12ell(N)+10. A non-top-shrink decrement with t=v2(m) costs7t+14; a top
shrink above1 costs three more. At m=1, counting its two work-clear steps
in the14 base leaves terminal unary RIGHT/rewind/goto cost3N+5.
There are ell(N)-1 nonfinal top shrinks and sum(v2(m),m=1..N)=N-popcount(N).
Thus the decomposition is

    12ell+10 +7(N-popcount)+14N+3(ell-1) +3N+5,

which gives c(N). This reconstructs the stated predecessor formula; neither
the component nor binary countdown is claimed as a new arithmetic method.

The three conversions use distinct unary destinations5,6,7 and reuse WORK8,
which is restored at each return. They cost c(A)+c(H)+c(R). All unary heads
are1 on completion. The original input bytes/markers and heads are preserved.

## Quotient phase, with its first-rewind saving

Before each output increment, the source scans exactly L full H guides,
advancing A's unary head once per H mark. A mark costs5: H test, A test,
two moves and goto. Each scan has one final H-RIGHT test. An incomplete
group rejects rather than incrementing; on the divisibility domain exactly
q groups consume A=q*L*H marks and produce q.

There are qL H scans. The first rewind starts at head1 and costs3; the
remaining qL-1 start at H+1 and cost3(H+1). Their sum is
`3qL(H+1)-3H`. The scan bodies cost qL(5H+1). Group tests cost q+1 and
the post-increment group gotos cost q. With the exact from-zero increment
cost C, the quotient phase is therefore

    T_Q=8A+4qL-3H+C(q)+2q+1.

It ends with A's and H's guide heads at RIGHT. A_child is canonical q with
head1. H and R are positive, so all uses of their guides are nonempty.

## Product phase

The initial H rewind from H+1 costs3H+3. Outer H tests cost H+1.
R is rewound H times: first from head1, then from R+1, costing
`3H(R+1)-3R`. The K pairs each cause an R test, R move and inner goto,
besides the increment itself; H terminal inner tests add H. Advancing H
and returning to its outer test costs2H. Consequently

    T_P=6K+10H-3R+C(K)+4.

The product invariant after h full scans and r marks in the next is output
h*R+r. At completion it is K=H*R, canonical with head1. H and R guide
heads are both at RIGHT. The A guide remains at its earlier RIGHT.

## Complete retirement and exact producer time

Retiring a guide with N marks, starting at RIGHT, costs4N+5: three initial
RIGHT-test/erase/move instructions, four per UNIT and two at LEFT. It clears
every marker/UNIT and ends at0. All three cost4S+15. WORK has only LEFT0
at head1, so its move-left/test/write costs3 and leaves it blank at0.
The success HALT adds1. Total retirement including HALT is4S+19.

The complete valid producer count is therefore

    T=c(A)+c(H)+c(R)+C(q)+C(K)
       +12A+11H+R+6K+4qL+2q+46,                         (E)

where `C(k)=13k-7popcount(k)+5ell(k)`. All constants and first-scan savings
are included. This boundary differs from the isolated increment's exclusion
of a wrapper HALT; here the actual producer HALT is charged once.

## Proving the proposed60 envelope

For every positive N, ell(N)<=N and popcount(N)>=1 give c(N)<=44N.
Since A>=L*H>=2, the stronger bound

    c(A)<=63A/2+20

also holds. Indeed ell(A)<=A/2+1: for d=ell(A)>=2 use
A>=2^(d-1)>=2(d-1), with the latter established from d=2 and induction.
Substitution and popcount(A)>=1 give the displayed c(A) bound directly.

The separately proved sharp isolated bound C(k)<=15k, together with
qL=A/H<=A and q<=A/2, turns(E) into

    T<=56A+55H+45R+21K+66.

Its difference from60(S+K) is at least

    4A+5H+15R+39K-66 >=8+5+15+39-66=1.

Thus T<=60(S+K), uniformly over the full admitted domain. This is an
all-size inequality derived from exact phase counts, not a fitted census.
It does not claim that60 is the best possible full-producer coefficient.

## Exact local visited space and final ABI

Each input descriptor visits its interval0..ell(N)+1; the conversion and
rewind reach both ends. The two outputs visit0..ell(q)+1 and0..ell(K)+1.
The three unary guides visit0..A+1,0..H+1,0..R+1, including retirement.
WORK visits0..max(ell(A),ell(H),ell(R))+1. There is no below-origin motion
on the valid marker invariant. Their full-execution visited spans sum exactly to

    E_space=S+ell(A)+ell(H)+ell(R)+ell(q)+ell(K)
               +max(ell(A),ell(H),ell(R))+18.

This is a sum over nine distinct physical tapes and counts erased cells
as still visited. It is not the current nonblank support or a claim that
inaccessible entry backing has been deallocated.

Using ell(N)<=N, q<=A<=S and max ell<=S gives
`E_space<=4S+K+18`. Since S>=4 and K>=1,18<=4(S+K), so
`E_space<=8S+5K<=10(S+K)`. Thus the source visited-space envelope is valid,
with its explicit marker/extent premises.

At the successful HALT, inputs0,1,2 retain their bytes/markers and heads1;
outputs3,4 contain canonical positive q,K and heads1; scratch5,6,7,8 are
physically blank throughout their visited owned regions, including LEFT and
RIGHT markers, with heads0. The outputs remain live owned descriptors, not
free productive targets. Future retention or erasure is separately paid.

## Remaining boundary and attribution

This is a written proof of the nine-tape producer on its valid marked-entry
domain, with the retained exact counter component and source machine semantics.
It is not an execution/custody certificate, complete malformed-input recognizer
or rejection rollback theorem. No linked_split, retire_delivered, consumer,
router, codec/stack,1000V/100V bill, H-from-width production, arbitrary-depth
descriptor/caller, physical supplier, tariff/kappa, compiler/precision/outer
result or discharge of the five framework assumptions is established here.

thu-nmrc/PR6719 retains the producer/increment/formula and child-grant
implementation credit, with substantial OpenAI Codex assistance. David Arias/
PR2776 retains the machine, assembler, binary-to-unary and rewind framework;
Ali Romman/PR5829 and the retained lineage keep whole-high geometry and prior
interface credit. Exact loop counting, binary carries and these inequalities
are classical. This source-aware external written AI review adds a scoped
contract/count/envelope check, not generic arithmetic novelty, independent
human acceptance or a proof-kernel certificate. Apache-2.0.
