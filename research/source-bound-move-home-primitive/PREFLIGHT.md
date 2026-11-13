# Bounded MOVE/home ABI preflight

Canonical main: e54523517d0f03e58352e647c403a5af3e525a57, refreshed by the
parent before this wave. This is a separate package; the frozen B1 dispatcher
and the published native MOVE core remain read-only.

Exact target: one actual selected MOVE24472, public field owner unchanged.
Input to B1 is `Gamma(f)||Gamma(r)||Gamma(P)||Gamma(S)||Gamma(w)||Gamma(cutoff)||DATA`,
all six positive, with F=E+V binary bits and the outside B delimiter `|`.
DATA is the complete packed `V=2 P S r 2^(9f) w` field. The numerical and
cutoff admission are exactly the published native core's supplied premises.
No initializer or actual selected caller is inferred from raw owned zeros.

The core at 3a27ab1d302d13b1ce52411f8a174e7a32baab77 has 31 tapes and 82,813
literal read/write/unit-move/goto/halt locations. It accepts distinct HEADER
and DATA owners. All core origins can be shifted to cell 2: its private guards
then occupy blank cell 1, while B's permanent `^` at cell 0 is untouched.
The source program's public-preserving transaction commits only after every
factor succeeds. On arithmetic rejection, B's HOME has not yet been scattered.
No rejected-bank cleanup/reuse is proposed.

Proposed finite construction: split six Gamma codes by a unary *length* guide,
without decoding their values; copy the remaining binary DATA body separately;
translate the actual core table offline to B graph rules at fixed private ports;
on successful halt repack HEADER and DATA to the same B operand, erase the two
core public copies and return all 31 core heads from offset 2 to B origin 0.
Every parse/copy/repack/reset and shifted guard is a paid graph operation.
A separate private Gamma-length guide uses only O(E) time/space, including a
huge encoded cutoff. No runtime factor callback or integer decode drives the
machine. All f/precision-dependent work remains in the actual core graph.

Optimistic complete successful bill: C(F+1)+2^24(fV+E+1), plus B1's existing
O(R K (F+1)) gather/return bill. Core-table translation has one B graph
transition per retained instruction (read branches remain scanned-symbol
branches); adapter phases add only O(F) local transitions. At a fixed admitted
leaf cutoff, this is linear in the complete F-bit field. Historical capacity
is entry history plus O(F+1) adapter visits plus the core's 1024(V+E+1)
increment; no erased prior capacity is subtracted.

Success test: full nonzero f=1, m=9 packet through actual HOME gather, the
translated complete core, and same-HOME scatter; a second same-F source home
remains arbitrary and untouched. Expected values use a separate exact selected
kernel, and controls cover header loss, guard offset, wrong home and arithmetic
rejection before any HOME mutation. Small parser-only tests include large
encoded cutoff lengths; these do not substitute for the full packet run.

Bounded overlap: GitHub API search `repo:CrocSwap/integer-mult-bounds MOVE header
packed is:pr` returned zero matches (incomplete_results=false); MOVE24472
returned #7430, #7426 and #7462. Those implement the retained source factors
or a different shortened left word, not the B1 single-field ABI. Parent's broad
literal-rounded comparison identified #6996/#7211, whose Count/Tape formats
are distinct. This is a bounded public metadata check, not proof of novelty.

Exclusions: other native operators, all-word generation, faster nonleaf rates,
endpoint scaling, actual caller/initializer admission, numerical-producer repair
and rejected-bank cleanup. Stop with a precise obstruction if shifted origins,
cleanup or complete-field accounting cannot be proved.
