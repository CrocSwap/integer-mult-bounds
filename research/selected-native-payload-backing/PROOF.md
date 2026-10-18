# Native payload backing at a suspended packet action

Fix an odd prime q, w>=1, M=q^w, and positive integer spectator extents U,G,S.
Inputs use the source's canonical binary widths and margins. Execution succeeds,
the complete source starts at head 1, and the coefficient callback satisfies the
source's numerical ownership contract. No observer, factory or external owner
captures private payload arrays. These are source contracts, not selected
supplier admission.

The source pins and byte-identical exports are in SOURCES.json. The primitive
bodies are PR2697's `vendor/stream.py:add_pass` and `vendor/bitstream.py`.
The comparison is PR2753's `linear_sign.py:sign_address`, with the same unchanged
word, record and counter dependencies. PR2566 already proved complete digit
costs, at most 3F additional live payload bits, and a reusable physical lane
schedule. We retain that credit. The result below refines the distinct metric
of exact retained array lengths in these reference bodies and supplies the
payload component left separate by PR2882.

## Metric and boundary

F=U*M^2*G*S for ADD and atom swap; F=U*M*S for sign. The input Tape belongs to
the suspended caller, so its entire backing is excluded from the private count.
Count `len(tape.cells)` over distinct private payload Tapes, including a pending
returned result, LEFT markers, and cleared entries. Count only payload Tapes
created by the literal constructors in the named primitive bodies. Counter and
Natural tapes, fixed-width numerical words and templates, callback records,
programs, source extents and enclosing Layout objects are separate categories.

This is reachable array length. It is not occupied nonblank content, bytearray
allocator capacity, Python heap size, implicit blank head positions or a physical
last-borrower/reuse theorem. Scratch leaves this cohort only when its last source
reference disappears. `Tape.clear` erases without shortening its bytearray.

Every counted Tape starts with one LEFT. A fresh output containing f payload
bits has length f+1. All outputs are fresh and distinct from the borrowed input.
Every routine only reads or moves the borrowed source, restores its content and
head, and returns a complete F+1 output at head 1. Surrounding caller backing
therefore remains fixed throughout the action, as PR2882 requires. This is a
source inspection of these primitives, not an assertion about arbitrary callbacks.

## Exact private maxima

```text
ADD                         2F+3
atom swap, w=1              2F+q^2+1
atom swap, w>=2             3F+q^2+2
original digit sign, w=1    3F+4
original digit sign, w>=2   3F+q+2
PR2753 linear sign          F+1
```

These are exact maxima under the stated successful fresh-array contract.
They include the returned result. They do not include the borrowed input again.

**ADD.** The split pass creates left, right and output. Left and right partition
F bits, so their combined retained length is F+2. The merge appends F bits to
output, whose length is F+1 at the last append. Both split arrays remain live
through their subsequent clears. Thus 2F+3 is attained. Before the merge, output
is a single LEFT; during it output grows monotonically, so nothing exceeds that
cut. The coefficient callback's arrays are outside this payload cohort.

**One digit permutation.** A digit swap has q^2 buckets; complement has q.
Write b for that bucket count. Each bucket has F/b bits after splitting.
All buckets stay referenced by the bucket list during the full merge and cleanup,
so their total retained length stays F+b. Output grows to F+1. Excluding the
borrowed input to this one digit routine, its peak is exactly 2F+b+1.
Clearing buckets cannot justify replacing their lengths by one before they leave
scope. Bucket headers are counted even when only one bit occupies a bucket.

**Whole atom swap.** Every digit routine handles the same total F, despite the
changing digit extents. The first digit reads the original borrowed source, so
its private maximum is 2F+q^2+1. At every later digit the outer `current` is a
private F+1 intermediate. It remains live until the following digit has returned
and the explicit clear finishes. At that digit's last output append the maximum
is therefore 3F+q^2+2. Afterwards `following` and `current` alias the new output;
they do not contribute two copies. The old intermediate has no remaining source
owner after that assignment. Natural/cardinality preparation adds no payload
Tape. For w=1 only the first case exists; for w>=2 the second cut is attained.
This induction applies to arbitrary w without counting all past outputs together.

**Original sign.** The complement loop has the same argument with b=q. Its first
pass peaks at 2F+q+1; later passes peak at 3F+q+2. The final `translate_one` holds
the incoming owned F+1 intermediate, two split arrays totaling F+2, and its F+1
output. This attains 3F+4. For w=1, it exceeds the digit cut because F>=q gives
`3F+4 > 2F+q+1`. For w>=2 and q>=3, the later complement cut 3F+q+2 exceeds
3F+4. The outer `following` aliases the incoming intermediate at translation;
it is not an additional F+1 object. Its retained reference does keep that one
intermediate alive through the translation, including its explicit clear.

**Linear sign.** PR2753 creates exactly one payload Tape, output. All slice
movement and counting uses the borrowed source and non-payload words/counters.
Output grows monotonically to F+1, which is attained at its final append.
PR2753 owns the algorithm and its earlier time/endpoint argument. This proof
adds the exact payload-array accounting, without repricing its other categories.

## Restricted composition with PR2882

Retain PR2882's domain: N>=1 complete F-symbol prefixes, at least two primitive
passes, borrowed backing K>=NF+1, preflight/fresh prefix backing Q>=2, and
complete directory backing D>=1+N(Q-1). Its structural caller-cohort maximum is

```text
B = K+(2N+1)F+4+D+2Q+max(Q,F).
```

At an action interior after j<N completed prefixes in primitive pass t, its
suspended caller contribution is

```text
C(t,j) = K+[t>0](NF+1)+(jF+1)+(F+1)+D+2Q
       <= K+2NF+3+D+2Q = C_max.
```

The final `(F+1)` is borrowed local. The pending native result belongs to the
private cohort until return, then becomes caller `changed`; these are the same
array. Therefore, for A_payload from the table, the caller-plus-native-payload
cohort has upper bound

```text
max(B, C_max + A_payload).
```

For a mixed sequence use each action's own A_payload or their maximum. This
formula bounds this explicitly restricted union. It does not substitute
A_payload for PR2882's **total** action-private A. A complete A must also bound
all excluded private categories at the same cut. If their simultaneous total
is at most H, `A <= A_payload+H` is sufficient. Independent sharp peaks do not
prove that this sum is sharp, nor that a fixed selected trace attains the bound.
No caller/storage or physical-wrapper campaign is started here.

For N=2,F=9,K=19,D=7,Q=4, B=92 and C_max=73. Actual native peaks give the
restricted upper bounds 94 for a 9-bit ADD, 105 for the 9-bit original sign,
and 92 for the 9-bit linear sign. Thus B alone does not pay for every native
payload interior. A structural caller peak and an action scratch peak must be
joined at the same phase, with the returned output counted once.

## Finite evidence and proof limits

The checker authenticates exports before loading source, and executes source
bytes directly rather than reading adjacent bytecode. A Tape subclass observes
literal payload allocations and every payload write/clear. It stores weak
references and integer size witnesses, so it does not retain private Tapes or
alter their arithmetic, payload branches or tape methods. Constructors in
bitstream and linear_sign are payloads; the three direct constructors in
stream.add_pass are payloads. Counter/Natural constructors are excluded by their
source call sites. This classification follows the pinned source, not arbitrary
future implementations.

Sixty complete fixtures cover q=3,5, w=1,2,3 in the recorded combinations and
unequal/one-bit spectators. Twenty-two origin-bit-plane executions recover every
source address in four q=3,w=2,U=G=S=1 macro domains. They corroborate the written
lifetime induction and exact endpoint maps on those domains. They do not turn a
finite test into an all-parameter proof. Controls exercise undercounted buckets,
missing incoming intermediates, missed final translation, weak-reference
retention, invalid domains, mutated source/inventory, preloaded source modules,
boolean receipt substitutions and accidental receipt overwrite.

Exception cleanup, complete numerical reserve, non-payload record lifetimes,
physical tape placement/erasure/movement, the full selected GL64 caller, stronger
H2 time contracts, outer borrowing/padding, supplier admission and multiplication
transfer remain outside this result. There is no new kappa or formal-kernel proof.
