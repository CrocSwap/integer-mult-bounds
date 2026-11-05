# Pre-first static review of complete producer emission

**PASS: no source-closure, ABI or counting mismatch found.** This is a static
review of BUILD/emitter.py and the root PROOF.md before the planned first
scientific executions. No source import, compilation, constructor, interpreter,
table generation or scientific program was executed by this reviewer. The
separately sealed full producer proof remains independent of later fixture data.

## Authenticated import closure

The emitter hashes all four files before loading any of them: producer.py,
machine.py, counters.py and router.py. The relative layout is consistent with
the actual producer's HERE-based loader: source/producer.py resolves its
inputs/PR6719 dependencies to the three paths authenticated by the emitter.
It does not substitute a source file from an ambient checkout or old module.

Loading the producer executes its actual finite module-import setup and defines
its functions. That setup loads machine first, then counters, then router.
Consequently the latter two modules' imports of machine/counters bind the
fresh authenticated dependencies, not arbitrary prior public aliases.
The pinned counter/router top levels define their routines; they do not run
their builders or interpreters. Producer loading does not call linked_split,
retire_delivered or build; the emitter later calls only producer.build(L).
Source Program/Assembler construction is required and is within this emission
scope. No source Machine or Tape object/run is called.

The three public aliases machine,counters,router are saved and restored in
finally, including the formerly-absent case. The private producer module entry
is retained as ordinary Python construction metadata; this is not restoration
of every import-cache side effect or a physical tape/resource guarantee.
Compilation and its host module bookkeeping remain outside the runtime bill.

## Actual tables and boundary

The emitter checks the source role constants are exactly0 through8, and its
alphabet is exactly the retained seven symbols. It passes only L=2,3,4,7 to
the actual producer.build function and requires nine tapes in each result.
No A,H,R value enters source construction. They must remain actual runtime
binary tape inputs of the independently interpreted programs.

The result carries each actual entry and entire instruction tuple. The JSON
roundtrip only serializes tuple/list structure; it does not rewrite opcodes,
targets, symbols or movements. No synthetic HALT or continuation is inserted:
the producer's own success HALT is present and must be charged. This is the
correct difference from S7's isolated-increment stop-before-wrapper convention.
The fail/reject instructions are retained, not replaced by successful halts.

This is shared candidate construction for the primary and oracle, not two
independent source compilers. Their literal simulation, fixtures, sentinels,
rejection controls and actual certificates still need their own execution
and review evidence. No such future pass is inferred from this static check.

## Root proof consistency

The root PROOF.md matches the independently derived phase ledger:

    T=c(A)+c(H)+c(R)+C(q)+C(K)
       +12A+11H+R+6K+(4L+2)q+46.

It charges setup22, exact counter calls, first-rewind savings, all quotient/
product tests and jumps, complete guide/work retirement and the success HALT.
It uses the positive/divisibility and owned-blank-growth premises explicitly,
preserves input/output/scratch heads and markers, and promises no malformed-
input rollback. The planned smallest witness291 transitions and30 visited
cells agrees with that written calculation; actual execution is separate.

The60(S+K) argument uses c(A)<=63A/2+20, c(H/R)<=44H/R and C<=15k,
then qL<=A and q<=A/2. Its remaining difference is positive on the admitted
domain. The exact nine-tape visited-expression and conservative10(S+K)
envelope are also consistent. Neither60 nor the visited bound is claimed
sharp, and neither is a linked/consumer1000V/100V or complete supplier bill.

The proof correctly distinguishes the finite four-L/fixture plan from the
all-L arithmetic/loop proof and names remaining physical/compiler/native/
precision/outer/framework obligations. No whole supplier, productive tariff,
kappa, frontier, human or proof-kernel acceptance follows.

No correction is required before the planned firsts for the reviewed emitter
and proposition. Later code/closure changes require a new review binding.
thu-nmrc and David Arias retain producer/machine/counter authorship; remaining
source lineage remains as credited. This separate source-aware AI static review
used substantial OpenAI Codex assistance. Apache-2.0.
