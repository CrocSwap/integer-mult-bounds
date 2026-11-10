# A full-state constant-two refinement after the unit pass

Prepared for ToikY with substantial source-aware OpenAI Codex assistance.
Apache-2.0. Constant specialization and block simulation are classical.
The exact predecessor programs, proofs and notices are credited in CREDITS
and bound by SOURCE-PINS. Their original multiplication theorem is a premise,
not a theorem independently re-audited here.

## 1. Fixed caller and comparison

Fix the authenticated producer's fused template with s=t=256 hexadecimal
digits, n=512, p=65537 and 64-bit modular Word RAM. Inputs are arbitrary
admitted digits0..15; owned scratch, temporaries and output cells may start
dirty. Arbitrary exterior memory and both operands are part of the frame.
The ISA is the source's literal one/add/sub/mul/load/store/bltz/accept/reject
model. There is no introduced shift, division or remainder instruction.

Let P0 be that exact emitted producer program. Let P1 be Nick Petalas6802's
authenticated unit refinement applied to P0. Its complete-state correctness,
producer coefficient/setup invariants and executed-initializer/control facts
are cited premises. P1 is the comparison baseline for the NEW refinement.
The existing unit saving is not included in our new saving. No address-
allocation pass, changed instruction tariff or native BIT model is composed.

At a transform butterfly, the producer supplies a residue b with0<=b<p,
ZERO=0, and threshold cells20+i containing p*2^i for i=0..15. VALUE is cell8
and TEMP cell9. A qualified twiddle cell contains exactly2. Data and constant
operands are outside the written scratch/threshold cells. Source allocation
and constant lifetimes, not free memory initialization, supply this contract.

## 2. The complete local replacement

At such a constant-two site the unchanged generic macro is the following
49-instruction literal list (the loop is only notation for its unrolling):

    mul VALUE,b,two_cell
    for i=15,...,0:
        sub TEMP,VALUE,threshold_i
        bltz TEMP,after_copy_i
        add VALUE,TEMP,ZERO

Replace it by four literal instructions:

    mul VALUE,b,two_cell
    sub TEMP,VALUE,threshold_0
    bltz TEMP,macro_exit
    add VALUE,TEMP,ZERO

The first product is z=2b, with0<=z<=2p-2=131072, so it is exact in64-bit
arithmetic. For every deleted group i>=1, threshold_i>=2p>z. Its subtraction
is strictly negative and has magnitude below2^32. The stored modular word
therefore has the intended negative signed interpretation. Its branch is
taken, its copy is skipped, and VALUE remains z. All fifteen groups have
this behavior; none supplies a hidden reduction of VALUE.

Their successive TEMP values are overwritten by the retained final group.
That final subtraction has signed value z-p in[-65537,65535]. The branch
skips its copy exactly when z<p. Both words consequently leave

    VALUE = z             if z<p, otherwise z-p,
    TEMP  = z-p modulo2^64.

In particular TEMP is not always VALUE-p: when the copy executes, TEMP
equals the final VALUE. Retaining its subtraction/branch/copy is necessary
for full memory equivalence. The proof holds for arbitrary incoming VALUE
and TEMP, since MUL and the retained SUB overwrite them before use.

Every other memory address retains its exact incoming word. Both blocks
write only VALUE and TEMP and reach corresponding exits. They need not
have identical intermediate TEMP traces or instruction counts; the theorem
is complete memory equality at block boundaries in the source's sequential
machine, not an interrupt/interleaving or microstep-trace equivalence.

Let delta be1 if2b>=p and0 otherwise. The generic block executes
1+2*15+2+delta=33+delta instructions; the replacement executes3+delta.
It thus saves exactly45 static and30 executed instructions for EVERY
admitted b. The original MUL and last conditional copy remain charged.
No scratch clearing, constant synthesis, setup or exit instruction is free.

## 3. Identifying actual constant-two blocks

The source-bound transformer checks the direct-address instruction grammar,
forward branch targets and terminal accept. Its complete write inventory
recognizes a coefficient cell only if its three writes are one(cell), the
immediately following add(cell,cell,cell), and a final sub(cell,cell,cell).
It checks that each matched use is after both initializer instructions and
that the entire49-instruction macro lies before the clear. There is no
intervening write to that cell. In the authenticated producer, initialization
executes before use and all setup/range facts above hold. These are explicit
premises, not consequences of the grammar check on arbitrary programs.

Only MUL into the retained VALUE cell qualifies. The following entire generic
macro, including each threshold, data operand and old internal branch target,
must match exactly. Operand/scratch alias exclusions apply. Inverse scales
and pointwise products write other fresh cells and are unchanged. Constant
pool reuse elsewhere is not a separate rewrite target. P1's unit blocks and
these coefficient-two blocks are disjoint: their authenticated coefficient
values differ. Their already charged initializers and final clears remain.

Actual coefficient addresses, site counts and emitted-program hashes are
generated evidence, not assumptions silently borrowed from6802's unit census.
The result concerns this one fixed512 template, not every length pair or an
unrestricted constant optimizer. If no qualified site exists, there is no
positive caller saving to report.

## 4. Label relocation and full-program simulation

Partition P1 into qualifying49-instruction blocks and unchanged singleton
instructions. Map each original block entry to its new instruction index.
Every surviving old branch must target an entry represented by this map.
A surviving external branch into ANY removed block interior is rejected.
The new retained BLTZ targets the MAPPED OLD EXIT at old_pc+49; it is not
left at its old numeric offset or relocated twice as a new-coordinate label.

The replaced block's internal high-threshold branches are deleted. Their
behavior on admitted entries is exactly the taken/skipped-copy behavior
proved in section2. The retained final conditional branch exits either
directly or after its copy, in both cases to the mapped next block entry.
Unchanged branches read equal words and therefore take equal outcomes.
Induction over executed blocks establishes equal complete memory at every
corresponding boundary, hence equal final accept, operands, outputs, owned
cleanup and arbitrary exterior values.

Every source butterfly MUL is executed once on every admitted input. In the
pinned producer, control is forward-only and branches skip only optional
reduction/carry updates, not initialization or whole butterflies. The cited
unit refinement preserves this fact at corresponding boundaries. The new
structural matcher alone does NOT prove that fact for arbitrary instruction
lists. Together with these exact source-control premises, if r is the actual
number of qualified sites then the new program P2 satisfies

    len(P2)=len(P1)-45r,
    steps(P2,input)=steps(P1,input)-30r

for every admitted input to this fixed template. All setup, pooled constant
construction/reuse, unaffected butterflies, normalization, carrying, clearing
and charged accept remain. Space addresses and the complete memory frame
remain those of P1. The new invoice is incremental to P1, not a recount of
the unit pass or a claim that the source baseline is globally optimal.

## 5. Evidence boundary and remaining work

The universal implication is this written local range/full-memory proof plus
block simulation under the authenticated producer premises. A new verifier
must authenticate source bytes before import, inspect the emitted fixed
template, compare local literal execution over all65,537residues, and compare
bounded whole dirty-memory fixtures with meaningful structural and semantic
controls. Actual counts, program hashes, runtime and memory are reported only
after observation. Finite operand fixtures are not exhaustive over all256-digit
inputs and do not independently establish the original NTT/multiplier theorem.

The exact original producer, unit transformer and ISA interpreter may execute
as credited components of those checks. That is predecessor code/program
execution, even though the old verification suite is not rerun. Source-aware
related AI proof/code review is not blind, human or proof-kernel acceptance.

There is no all-size paid compiler, native arbitrary-integer multiplication
tariff, selected consumer, physical word-to-bit/routing/storage/precision bill,
or complete supplier admission here. The formal-interface-lemma card remains
CHANGED/partial: no Lean proposition is claimed formalized. All five selected
assumptions remain; no new kappa, frontier/adoption change, global optimum or
merge follows. Credit David Ganz/Dugongue5466, Nick Petalas6802/5886/6435,
tcslib/Anthropic-PBC, Shilun-Allan-Li, Thomas Ahle/FastPoly, Bas Spitters/
CatCrypt, Brett Saiki/mpfx and the retained original notices and lineage.
