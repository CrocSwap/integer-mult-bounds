# Uniform complete-prefix leaf/consumer composition

Fix q,w, a valid encoded Layout with finite fibre length v, a complete original
directory with p=C*H prefixes, and source/target Boolean packets of p*v bits.
The source directory producer supplies canonical complete prefixes in the same
order as those packets. All borrowed heads enter at 1. Inputs occupy distinct
roles. The unchanged trace factory yields the same closed finite leaf sequence
for every prefix. Its coefficients depend only on that prefix, the same Program
and encoded context, and return owned words while restoring borrowed state.
An optional observer must be read-only. These are source-level hypotheses,
not consequences of finite samples. Equality means payload and borrowed logical
Program/Fields state, excluding meters, allocation order, and global callback
logs. Deterministic Specifications memoization may change bookkeeping; it does
not change coefficients or borrowed logical bytes.

For primitive t and prefix i, let T_t,i be its local payload map. In the pinned
packet_engine.run, every primitive reads exactly one prefix and v bits, invokes
`action` on that local tape, then appends exactly v output bits. It reads no
other prefix payload. The callback uses that complete prefix; controller's
restored Program/Fields reads and owned numerical work establish the stated
no-cross-prefix-effect contract on successful valid inputs. trace.leaf reads
geometry only and retains chronological ADD/swap/sign order within each prefix.
Thus the original primitive-major schedule is the direct product of maps
T_t,i. Operations on different prefix payloads commute, even when their
coefficients are correlated through a shared borrowed Program: their Program/Fields
logical dependency is shared and unchanged. Deterministic cache population and
meter increments need not agree between the schedules. Reorder only across i, never
across t within i. This proves that prefix-major execution produces the same
p complete local returns for every Boolean source packet and every such context.

The literal episode.xor_packet independently loops old_count, context.highs,
then v bits, emitting return XOR dirty_target. It changes neither operand and
restores heads. It is therefore the product of local pointwise XOR consumers.
Applying each local consumer immediately after its complete local leaf return
commutes with all other prefix computations. The new adapter's encoded product
check establishes p=C*H; complete-source/target/directory consumption checks
exclude silently omitted or extra prefixes. It does not infer canonical
producer contents merely from equal counts. The complete directory remains an
input; no directory serialization or reserve-absorption result is claimed.

After each prefix, clear its owned return and all local copies, then continue.
Only the final consumer output grows to p*v bits. No intermediate whole-child
returned packet is created. At most one v-bit child return reaches the consumer
at a time. Local primitive workspace, source/target copies, accumulated output,
complete borrowed directory, Program, metadata and callbacks remain paid.
Repeated per-prefix trace setup is extra work, not free; output serialization
and every visited/erased backing cell remain part of the invoice. Logical
liveness does not establish a fixed-tape allocation/reuse or physical-space
improvement. The claim is functional composition and a changed lifetime
boundary, not uniform runtime savings, supplier admission or a new kappa.

For the full high cube, take H=(q^(w-1))^(m*m) and the complete output of the
unchanged directory.produce. Its enumeration order and repeated old prefixes
are inherited. The same proof applies for every finite H without a sampled
high-fiber argument. The actual R437 corroboration uses the two q3,w2 prefixes
of #4793; it does not physically enumerate H=3^4096 or prove root reachability.
#4927's directory/metadata absorption audit and #4854's quotient are separate.

The adapter adds exception-safe local raw-prefix parsing and bit-copy counters;
these front-end structural failures restore its owned state and borrowed heads.
The uniform positive theorem assumes valid callback/primitive contracts. It
is not a repair of every malformed-input cleanup path in frozen inner modules.
General arbitrary callback failure inside an inherited primitive remains open.

Credit: Jose Manuel / David Arias's retained packet/callback/consumer sources;
Chris R / Clear1nsight #4176; #4793 nonzero-high finite payload; original compiler,
word arithmetic and source lineage retained in SOURCES.json. New adapter/proof:
JoyboyBrian, substantial OpenAI Codex assistance, Apache-2.0.
