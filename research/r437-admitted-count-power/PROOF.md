# Original admitted NODE through the complete fibre Count

JoyboyBrian, substantial OpenAI Codex assistance, Apache-2.0. Adapted verification
setup from JoyboyBrian #4987. Original caller, cardinality, physical words and
stock/compiler mechanisms retain the credit in README.md and predecessor notices.

## Exact contract and changed implementation

Inputs are a valid immutable source Ring with modulus q^w, compiled integer
q>=2 and w>=1, an encoded nonnegative exponent Word E, and an owned canonical
Count V. Borrowed words enter at the original caller's agreed canonical heads.
The Ring/modulus/exponent and all unrelated dirty state are borrowed.
Count.multiply_small(q), source Counter and Word division are the actual
original primitives; the radix loop retains its original arithmetic and guards
with corrected opt-in cleanup on a rejected intermediate quotient. Runtime Word.inspect or decoding of E,w,V is forbidden.
The required endpoint is V_out=V_in*q^(w E), with borrowed bytes/heads restored
and all owned cache/Counter/numerical backing erased. This is a positive valid-
context contract. Initial Tape/Counter/Word construction and the underlying
primitive-owned allocation contracts must succeed; resource exhaustion and
primitive internal allocation failures are not a general rollback guarantee. It does not roll back partial output Count writes if the
original Count primitive itself fails.

The original multiply_atom_power traverses radix_power(ring,q) for every one
of E iterations. Each traversal divides the same unchanged modulus by q until
one, validates the exact remainder and copies/frees its own numerical operands.
No iteration modifies the borrowed Ring/modulus/exponent. Its yielded length is
therefore exactly w on every traversal. The original Count modification word is
precisely w*E repetitions of multiply_small(q), in that order.

The adapter performs the original radix_power division/validation loop once and writes one ONE marker per yielded
step on an owned sequential Tape, followed by RIGHT. It never decodes w into
host control. An actual source Counter copies E. For each Counter iteration,
the cache is read sequentially, each ONE invokes the unchanged Count primitive,
and RIGHT causes a rewind and original Counter decrement. Induction on the
Counter iterations proves the identical full Count modification word and the
required endpoint, for every valid finite input. Source q/carry finite-control
assumptions remain inherited; no new unit-cost arithmetic claim is introduced.

The owned cache is created before the try and cleared in its finally. The source
Counter is assigned only after successful creation and closed in the same finally.
The opt-in validation loop also releases quotient/remainder if the original
prime-power guard rejects: the frozen original generator checks that guard
before freeing those two new Words. Its copied modulus/divisor are released
in finally. Thus invalid radix validation and a failing Count operation release the adapter's
cache/Counter. A Count exception may retain its own partial output writes; general
failure rollback is not claimed. Cached validation is performed even when E=0,
so malformed contexts may reject earlier than the original no-op branch. This
is outside the stated valid-context equivalence, and is tested explicitly.

## Actual source binding and completed NODE boundary

The original source is the exact Machine.node in the authenticated R437 source
closure, inherited through #4987. bridge.py parses its AST and retains every
statement before the assignment to peeled. Only fresh_rows.quotient is replaced
by the already credited #4794 opt-in quotient and multiply_atom_power by the
adapter above. All other globals and statements are unchanged. In particular
these original statements execute:

    total = Unsigned(self.indices).times_small(self.size, 2)
    multiply_atom_power(fibre, total, self.context.ring, self.context.q)
    self.indices.free(total)
    complete = Count.product(fibre, self.count("suffix"))
    fibre.close()
    self.save_count(complete, "fibre")

The AST prefix hash and exact statement count are in RESULT.json. This is a
literal source cut before payload peel, not a reimplementation of the NODE
arithmetic. Root checked_entry authenticates original source handle/key, precision,
field, root size/history and stock before invoking the encoded continuation.
The context view is tied to that admitted metadata but its expensive full
Context/codebook constructor is not executed. An authenticated view is not
claimed as proof that the full constructor/caller has run.

For the unchanged q=2^127-1 root e=n=64,w=2,h=0, original precision is
L255/I8/Q520213. Unused and leading Counts are 9475, gap=suffix=1. The original
completed saved Count is exactly 9475*(q^2)^128, of bit length 32526. A read-only observer wrapping the actual call records one invocation, two
Word divisions and all 256 Count multipliers; these counters never control the
algorithm and the wrapped methods are restored in finally. All 256
Count multipliers remain paid. Two actual original Word divisions validate the
radix once instead of 256 original divisions. The adapter saves the completed
Count on the original fibre role before the first payload operation. The
root Count, original Program, old directory and unrelated dirty Count173/Word37
retain bytes and heads. The actual Count output persists only until explicitly
owned disposal; no teardown is used to conceal a failed borrowed-state test.

## Costs, evidence and limits

The new cache occupies w marker cells plus terminator/boundary and rewinds for
each exponent iteration. It pays w original radix divisions once, every source
Counter action, every original Count multiplier, all unary-cache reads/moves,
and cleanup. Record/index/residue counters and visited backing are reported
for the complete source prefix and fixture construction/disposal separately.
No huge integer is read as a runtime arithmetic oracle. Independent host integer
arithmetic observes completed outputs only; fixture construction and the inherited
large quotient divisor preparation remain explicit separate costs.

This is source-bound semantic completion and finite admitted execution. It does
not provide a total fixed binary-TM tariff, a runtime asymptotic improvement,
full Context/GL64 directory construction, payload, original peel, stock/precision
admission for all descendants, compiler or supplier/outer admission. The old
#4987 90.505-second interruption and this complete run are distinct diagnostics;
wall times across revisions/environments are not a proved speed comparison.
The exact reduction from 256 to two original divisions follows from the bound
source word and immutable valid Ring, rather than measured wall time.
