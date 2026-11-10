# Oracle method prepared before common execution inputs

This planning note was written while awaiting the coordinator's immutable
CONTRACT/CASES/SOURCE-PINS and constructor closure. It contains no execution
receipt and no claim that a program or fixture was built/run. No peer engine,
source Machine/Tape runtime, source checker or copied expected-output function
was read/imported. Shared authenticated original R.build(4,3,1) construction
will be explicitly disclosed when authorized; it is not independent end-to-end
construction.

## Iterative original-index expected mask

For each original root bit index x independently, maintain its current source
shape(A,L,R), fixedH and remaining depth d. At the current node decode only
its mathematical address in the observer:

    a=x//(L*R), low=(x//R)%L, r=x%R.

If d=0, this bit is complemented exactly when low=0; stop with that Boolean
mask. If d>0 and low is neither0 nor1, its bank is untouched by this node and
no descendant is entered for this bit; stop with maskFalse. Otherwise update

    x <- a*R+r,
    A <- A/(L*H), R <- H*R, d <- d-1,

and continue iteratively. The final expected original bit is XORed with this
single Boolean mask. No recursive expected bit-vector transformation is used.

This follows because splitting maps a source coordinate(a,low,r) to selected
bank index a*R+r. For an allowed recursive bank, the whole-high identity
identifies precisely that bank index with the complete child stream at
A_child=A/(LH),R_child=HR. It does not delete or modulo away an ancestor high
coordinate. Every original bit has at most one chosen descendant path; only
its leaf can complement it. Thus the mask requires all preceding low labels
in{0,1} and the final leaf label0, without recursively constructing any child
bit-vector. Original input values do not influence that path or mask.

The same iterative calculation can check a completed child output from that
child's actual entry packet and headers, while remaining purely an observer.
No decoded value, host path or expected bit may be supplied back to the emitted
program or used to select its branch, head or tape.

## Interpreter and restoration plan

Use dense physical symbol arrays and separate touched-position bitmaps, with a
literal finite-PC dispatcher independently authored from the common instruction
contract. Only the source authenticated constructor may be shared. Runtime
source Machine/Tape classes and source checker/observer/expected functions
must never be invoked. Exact read/write/unit-move/HALT/visit semantics and
canonical receipt fields await the common contract.

Before push, retain actual complete nonblank payload cells and exact heads,
plus control/phase. After the corresponding pop, compare actual states exactly;
newly visited blank backing stays in the visit/space accounting rather than
being treated as deallocated. Transfers, observed grants, readonly input writes,
protected changed output, final ownership/head conditions and the full root
endpoint need actual literal observations, not just an expected-output digest.

All finite masks, snapshots, grants and runtime counts remain uncomputed at
this planning stage. Root owns code/data seals, serial firsts, resource evidence,
normal/optimized and actual-packet corruption checks. Finite corroboration will
not replace the prior all-depth source proof, source primitive admission,
physical/native bill, natural-root production or selected assumptions.

Source current PR6719/thu-nmrc, Ali Romman/PR5829 whole-high geometry,
David Arias/PR2776 machine/counter/assembler, Mason Hale and retained
stack/codec/output-before-pop lineage keep their credit. Source-aware OpenAI
Codex-assisted independent oracle plan; no human or proof-kernel acceptance.
Apache-2.0.

## Pre-first implementation seal

The common inputs arrived after the planning note. The independently authored
`oracle.py` now implements that plan without reading a peer engine or source
checker/runtime/observer. No execution, import, compilation or fixture run has
been performed by its author before this seal. The coordinator alone will run
the sealed first attempt.

Each tape uses a physical `bytearray`, a separate visitation bitmap and a set
of nonblank addresses used only to serialize complete states. Physical address
`p` is stored at array index `p+8`; explicit bounds reject underflow rather than
allowing Python negative indexing. Data include the distant spectators; visits
are initially empty, movement charges both old and new addresses, and every
instruction including HALT costs one step. Every write attempt checks the
immutable root packets, prefix/markers/spectators and entire width/depth roles.

All 14 raw sources authenticate by length, SHA256 and Git blob before any
shared source import. The three metadata byte hashes are fixed in the engine.
The sole shared construction is original `R.build(4,3,1)`, called once; the
entire normalized constructed instruction table and metadata must equal the
retained authenticated table. Source Machine/Tape instances and source runtime
steps/runs are never called. The original constructor and table are a shared
dependency, so this is an independent execution model, not independent
end-to-end program production.

Before each push, actual full nonblank states and heads of all K payloads plus
control/phase are retained. Pop compares the complete actual objects, not just
digests. Actual changed output must be captured before retirement and equal
the protected relay before destructive pop. Depth is checked before the
literal return-left move. Every observed node and grant records its actual
bit list and decoded dimensions; the selected bank also equals the literal
whole-high subsequence of the actual parent packet. Final comparison checks
the iterative-mask endpoint on every root bit and all 25 complete cells/head
states. Initial support union persistent visits supplies retained backing.

The five controls mutate the actual instruction list and run the same literal
dispatcher, observers and endpoint checks. The one-edge wrong-H alias is
deliberately accepted only if every healthy semantic gate still passes; the
two-edge version must fail. No expected-control flag substitutes for actual
execution. All digests of canonical objects include the contract's trailing
newline. Default/`--check` recomputes the complete packet and byte-compares it
to actual retained input; `--certificate-out` writes a freshly computed packet.
JSON duplicate keys, floating values and nonfinite constants are rejected.

Forecast: below 128 MiB and within the coordinator's 180-second process cap;
these are unmeasured forecasts until first-run receipts. Only four fixed
fixtures are claimed; arbitrary-input/all-depth correctness, source primitive
admission and natural-root construction remain separate written premises.

Before either first run, the coordinator's static review identified that the
initial control handler caught every `ValueError`, which could misclassify a
resource/address/PC error as an expected semantic rejection. Initial unexecuted
code is preserved as `oracle-PRE-FIRST-v1.py`, SHA256
`2c2fd06b488e35407db8fad77f546ede2d147d999e5bed510280f84b8daf3379`.
The revised code catches only its dedicated `Semantic` class for actual
dispatcher rejection, observed state/ownership and endpoint predicates.
Parser, malformed instruction, PC, step/address/packet caps remain hard errors
and cannot satisfy a negative control. The same pre-first revision bounds
gzip reading to the declared cap plus one byte before accepting decompression.
Neither version had been executed/imported/compiled when this change was made.

