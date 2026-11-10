# Literal clean-bit implementation of the conservative Gaussian pair

This construction implements the exact PR #6509 pair under the explicit stock,
width and input promise below. Its numerical inverse/minimum-error/phase theorem
is credited to Ali Romman; PR #6523's actual MOVE9896 binding is credited to
ToikY. Those results do not supply the kernel-internal elementary cleanup proved
here. Only one pair is implemented, not a full native layer or caller.

## Model and wire contract

Fix an integer width6<=W<=256 and PUBLIC COMPILE-TIME orientation sigma=±1.
Four signed two's-complement W-bit data words contain (a,b,c,d), representing
Gaussian inputs x=(a,b),y=(c,d), with every absolute component<=M=2^(W-6).
Supply14W+6 additional ZERO bits. All data/work operands may be borrowed
exclusively and temporarily written by subroutines. Endpoint restoration is
proved; sources are not read-only at every elementary gate.

Data occupy[0,4W), zero output buffer[4W,8W), and ten W-bit work words occupy
[8W,18W), named SR,SI,DR,DI,CR,CI,NR,NI,YR,YI. Carry is18W; five tags p,ar,ai,nr,ni
are18W+1..18W+5. Total wire count is18W+6. The caller must fund and supply this
clean stock. The circuit does not manufacture zeros from arbitrary dirty bits.

Every emitted instruction is an integer-wire CNOT or Toffoli, with distinct
wires within the gate. Gates act only by controlled target XOR. Thus the whole
word is a globally reversible bit permutation; its literal inverse is the
reversed gate list. Arithmetic correctness and returned-zero stock are proved
on the promised arithmetic domain, rather than asserted outside that domain.

## Credited arithmetic templates and legal embedding

The unchanged PR #3152 scalar emitter supplies a modulo2^W adder with one clean
carry: target+=source, restoring source and carry at its endpoint. Both operand
banks may be temporarily written. Its actual local MAJ/UMA word has2(W-1)
Toffolis and4W-2 CNOTs. Subtraction uses the reverse literal word. This retains
Nick Petalas and Cuccaro-Draper-Kutin-Moulton credit, as reused by Ali Romman6511.

Each template is instantiated on LOCAL source0..W-1,targetW..2W-1,carry2W, within
its unchanged guards and local gate cap. Only afterward are gate wires renamed
injectively into the larger pair layout. A control/target XOR commutes with an
injective renaming; disjoint operand banks and the common carry meet the original
contract. No original width/wire guard is loosened, and the full pair word is
not passed to the predecessor's two-bank validator.

Halving uses the actual public3152 call `circuit(W,'scale',1,2,[('half',0)],[])`.
It emits adjacent three-CNOT swaps, then a final sign-fill CNOT:3W-2 CNOTs.
On bits(v0,...,v_(W-1)) it produces
(v1,...,v_(W-1),v0 XOR v_(W-1)). When v0=0 this is exactly signed division by2.
It is globally invertible even outside that guard; no bit is discarded/reset.
The local HALF gates use only the first W wires, then injectively rename onto
the selected numerator word. Repeated-sign-wire adders are not substituted.

All ten source objects are authenticated before importing exactly the declared
6509 kernel and3152 scalar code. Their exact source bytes are compiled directly,
bypassing cached bytecode; their code/guards remain unchanged. Other retained
source programs are inert context. This is explicit authorized reuse, not a
claim that the construction independently re-proves the generic adder theorem.

## Center and arithmetic evaluator E_sigma

First copy/add/subtract into four work words:
SR=a+c, SI=b+d, DR=a-c, DI=b-d. Four credited add/subtract blocks and4W copy
CNOTs accomplish this. Every loaned source and the carry return after each block.

Starting with five zero tags, compute

p=SR0 XOR SI0;
ar=p AND SR0; ai=p AND SI0;
nr=ar AND sign(SR); ni=ai AND sign(SI).

This is two CNOTs and four Toffolis. If ar=1, SR is odd and therefore nonzero;
its sign bit distinguishes the required +1/-1 center without a zero comparator.
The same holds for ai. Copy ar/ai into bit0 of CR/CI and nr/ni into every higher
bit. The resulting two's-complement words are exactly the source center: zero
when sum parities agree, otherwise the sign of the sole odd component. At most
one center component is nonzero. This uses2W CNOTs.

Copy SR/SI into NR/NI and use three arithmetic blocks on each to obtain

NR=SR-sigma*DI+CR+sigma*CI,
NI=SI+sigma*DR+CI-sigma*CR.

These are the source6509 numerators. Modulo2, DR=SR and DI=SI. The two numerator
parities therefore both equal SR0+SI0+CR0+CI0=0: equal sum parities give center0,
and unequal parities give exactly one odd center component. Thus BOTH halves
meet the actual reversible HALF guard. Apply HALF to NR/NI. Copy SR/SI into
YR/YI and subtract NR/NI. The selected four work outputs now equal the exact
source outputs: first=(NR,NI),second=(YR,YI).

E_sigma retains the input at its endpoint, but leaves other work as garbage.
It uses12 add/subtract blocks, two HALF blocks,10W copy/center CNOTs and the
explicit tag network. Garbage is not erased by a Python assignment or CLEAR.

## Compute-copy-uncompute and in-place output

Define U_sigma(A,B) by E_sigma(A), four-word CNOT copy into B, then the reverse
of EVERY E gate. E never uses B; copying into B does not change its output/work
controls. Hence U preserves A, returns all ten work words/carry/tags to zero,
and maps B to B XOR F_sigma(A), including when B is nonzero. This is the
classical Bennett compute-copy-uncompute principle, not a new generic method.

Starting with B=0, execute U_sigma, swap all4W bits of A and B, then U_(-sigma).
After the swap the state is (F_sigma(A),A). The source conservative map preserves
s=x+y and uses the same center c(s) in both orientations. Its difference update
is d'=sigma*i*(d-c)+c, so the opposite orientation recovers d. Thus
F_(-sigma)(F_sigma(A))=A, and the second XOR oracle returns B to zero while
preserving the desired output in A. All14W+6 owned bits are zero again. The
literal gate-list inverse and this numerical inverse identity are separate
claims; the verifier checks both.

## Headroom, including internal inverse entry

For inputs bounded by N, sums/differences are bounded by2N. Each numerator's
unshifted part is bounded by4N. Since only one center component is nonzero,
partial and final center additions stay within4N+1. The even final numerator
has absolute value<=4N, so each exact half is bounded by2N. The second source
output has the same bound using its complementary (s-d')/2 expression.

Forward evaluator inputs have N=M, so outputs are bounded by2M. The INTERNAL
opposite-orientation evaluator therefore accepts N=2M, not the original M-box.
Its conservative endpoint intermediate bound is8M+1. Since W>=6,M>=1 and the
signed W-bit upper bound is32M, we have8M+1<32M=2^(W-1). All signed arithmetic
endpoints match integer arithmetic without wrap. Ripple-adder temporary bit
states need not represent unchanged signed operand values; their exact modular
restoration contract supplies the endpoint argument. No unsupported public
M-guard is imposed on the reachable inverse input.

## Complete emitted logical bill

For E, twelve adders contribute24W-24 Toffolis and48W-24 CNOTs; the tags add four
Toffolis/two CNOTs, copies/center add10W CNOTs, and halves add6W-4 CNOTs. Thus
E has24W-20 Toffolis and64W-26 CNOTs. The in-place construction contains four
E/E-inverse blocks,8W output-copy CNOTs and12W swap CNOTs. The resulting bill is

Toffoli=96W-80; CNOT=276W-104; NOT=0; gates=372W-184.

Data stock is4W bits, clean stock14W+6, total18W+6. For b=bit_length(18W+5), the
word has2*CNOT+3*Toffoli address occurrences and CNOT+2*Toffoli control incidences.
A fixed encoding with8 bits for W-1,one sign bit,2 opcode bits/gate and b bits
per wire selector has9+2*gates+b*address_occurrences bits. This is an explicit
logical syntax/inventory bill, not a physical routing, decoder or tape tariff.
The largest emitted pair word has95048 gates, below the separate100000 cap.

The primary counts and hashes every actual complete word for all251 widths and
both orientations, checking the derived coefficients rather than replacing
emission with them. GATE-INVENTORY.json retains those502 hashes. GATES.json.gz
retains16 complete expanded words at the eight frozen widths. Its decompressed
values, not regenerated gzip headers, are the cross-environment contract.

## Evidence and remaining obligations

The primary packed-Boolean interpreter checks all14534 promised W6/7/8 cases
for both signs and280 larger signed/parity/boundary cases, comparing the full
four outputs to authenticated6509 arithmetic, every owned bit to zero, and
literal reversed-word recovery of the entire initial state. Wrong orientation
and omitted-uncompute gate-word controls must disagree. The independent oracle's
blind first is only arithmetic/bill expectation; an actual-circuit claim requires
its later separate interpreter to read and execute the submitted expanded gate
data on all cases after both first seals. No peer compiler is imported.

These finite cases corroborate the width-family invariant. Compiler correctness,
source primitive premises, clean-stock funding, physical placement/routing/tape,
full native256-pair lowering, actual caller integration, precision/supplier and
all selected framework assumptions remain distinct obligations. No all-widths
above256, dirty-bank cleaning, dynamic-sign circuit, input-admission checker,
physical acceleration, new generic rounding theorem, κ or frontier change is
claimed. PR6509/6523/3152/6511 and Clear1nsight4017's different lifting circuit,
with retained Cuccaro/Bennett/Barenco/Tekalign/scalar lineage, keep their credit.
