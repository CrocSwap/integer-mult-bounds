# Independent dense-tape execution audit

This oracle executes four authenticated complete child-shape producer tables, for fixed low types 2, 3, 4 and 7, on the 261 cases in the frozen CASES.json. It is a separately authored dense-list interpreter. It does not call the source Machine or Tape simulation, read the new primary implementation, or use primary observations to construct its certificate.

The table construction is shared with the primary. The authenticated emitter imports the four pinned source modules and calls the original producer.build(L). A, H and R are runtime tape data, not constructor arguments. The source router definitions are imported as part of that closure; router construction, source interpreter execution and full linked-consumer execution are excluded. This is independence of execution and endpoint validation, not independent end-to-end construction of the candidate tables.

## Dense state and dispatch

Each of nine tapes is an allocated dense list with an integer head and explicit observer extent. The observer includes the marker at -1, the far UNIT guard at 8192, and every position that the frozen cases can visit. Exceeding the observer is an error, rather than silently treating unobserved backing as available. The three input counters use canonical positive little-endian binary with LEFT at zero, bits starting at one and RIGHT after the highest ONE. Inputs start with head one; all output and work heads start at zero. Output/work storage is supplied blank except the two guards.

The dispatch loop directly implements branch, write, move, goto, halt and reject from the actual serialized instruction rows. A branch uses the current symbol and the row's explicit default target. A write changes exactly one current cell. A move records both its start and destination, then checks the observer extent. Goto changes only the program counter. Every executed instruction costs one, including successful HALT. Rejection raises a dedicated exception carrying the actual reject instruction index. This full-program convention deliberately includes HALT; it is distinct from the preceding increment-only audit that stopped before a wrapper HALT.

Visit sets begin with all nine supplied initial heads and record branch/write positions and both ends of moves. A case's space is the sum of the nine numbers of distinct visited positions, not the number of nonblank cells or the span between the outermost visits. Each row retains all nine [minimum,maximum,count] triples and heads. Its endpoint digest binds the complete list of nine objects containing the head and every sorted nonblank [position,symbol] pair, including guards. Canonical hashing uses sorted object keys, compact ASCII JSON and no trailing newline.

## Positive checks

For every frozen valid case [L,A,H,R], the interpreter runs the actual selected table and checks the two positive canonical outputs q=A/(LH) and K=HR. It compares all original input cells byte for byte and restores their heads to one. Both output heads must be one. All four work tapes must contain only the unchanged guards and have head zero. Every guard on every tape must retain its original symbol. Thus a residual cell on any observed backing position fails, even if the numerical output is correct.

The independent resource check uses measured dispatch and visits: steps <=60(S+K), space <=10(S+K), with S=A+H+R. It does not obtain those measured numbers from the primary's exact-cost expression. The small witness is taken from the actual case row [2,2,1,1] and must give outputs [1,1], 291 steps and space 30. The remaining universal statement is supplied by the written proof; these finite measurements alone do not establish it for arbitrary inputs.

## Ten controls

Four controls mutate the actual emitted L=2 table. Replacing the first ONE write on output port 3 by ZERO must produce q=2 instead of 3 on [2,6,1,1], while retaining a structurally readable endpoint. The corresponding output-port-4 mutation must produce K=2 instead of 3 on [2,2,1,3]. Replacing the last BLANK write on work port 8 by LEFT must leave a concrete symbol at work origin zero and fail the full scratch-blank endpoint check. Reversing the last positive input-port-0 move must leave its head at -1 and fail input-head restoration. These are execution controls, not flags inferred from finding the instruction rows.

Three invalid fixtures run the original table through the raw interpreter: nondivisible A=3,H=2 with L=2; a positive input with an extra high ZERO before RIGHT; and an occupied work origin. Each must reach an actual dedicated source REJECT instruction. A host fixture constructor does not reject these conditions first. No rollback property is asserted for rejected executions. The final three controls reject duplicate JSON keys, a float token and a Boolean substituted for a proof integer. Unexpected exceptions do not count as intended controls.

## Admission and retained certificate

The oracle binds the exact three metadata hashes in its source. FILES.json must enumerate exactly thirteen paths: primary, oracle and shared emitter; CASES, SCHEMA and SOURCE-PINS; and the seven pinned source objects. Every file's current bytes are checked. All table indices and proof integers exclude Booleans. The JSON loader rejects duplicate keys, floats and nonfinite constants. The retained certificate must have the exact schema keys and typed vectors. Default execution regenerates every table, case row, endpoint digest, control and bound, then compares the entire canonical certificate with ORACLE.json. --certificate selects a different retained certificate for the same comparison. Only explicit --emit writes a certificate.

The source implementation and its counter/stack/codec lineage retain their existing authorship and license. The new interpreter is an external audit with substantial OpenAI Codex assistance. It does not recost a full supplier, admit a physical backend, establish a frontier or kappa change, or verify all production/router/linked-call obligations.

## Pre-first status

This code and note were prepared without executing, importing, compiling or evaluating the candidate, source constructor or peer implementation. Root owns the authorized first execution, immutable first receipts and subsequent normal/optimized checks. The unmeasured planning allowance is under 180 seconds and under 256 MiB for the frozen finite domain; actual resources must be reported from that run, not this estimate.
