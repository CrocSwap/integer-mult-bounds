# The selected event ledger implies the conditional height recurrence

This is a source-bound application of the arithmetic lemmas in AAAmirinu's
PR #2327 to Jose Manuel's PR #2287. The latter proposes the recursive
construction; this note independently fills its finite event-accounting
premise. It does not prove a physical compiler or the selected native
operator equalities. Exact source heads and unchanged copies are in
`SOURCES.json`. The claim is in discussion #2253.

## 1. Statement and retained hypotheses

Fix integers p >= 2, d >= 1, and an incoming height t >= 0. A coefficient
has height t if it lies in 2^(-p-t) Z[i] and has modulus at most 2^t.
The same component bound applies to real arithmetic temporaries. Use the
literal R480 words and selected T16 caller in the pinned PR1094 archive.
At a node of width e, write e = 73 f + delta, 0 <= delta <= 72.

The assertion is conditional on these execution semantics:

1. Each selected positive rank-r event executes exactly one child on r f
   axes. Completed children implement the declared C tensor (or inverse)
   on arbitrary input arrays, restore spectators and return on the same
   grid. Their endpoint increases height by at most r f. This is the
   ideal, well-founded endpoint premise of PR2287; we do not infer it from
   the child's rank or a numerical test.
2. The proposed depth-first interpreter executes the supplied local word
   once for each selected call and cover class. It includes every positive
   idle remainder once. Only one complex child is unfinished at a time.
   Native monomials, alignments, translations, selection and scatter have
   the stated permutation/quarter-phase semantics. Their implementations
   introduce no additional interpreted coefficient arithmetic.
3. Scalar operations use PR2287's pinned `Grid` arithmetic. Copy, clear and
   parking have their stated byte-preserving or zeroing effects. All
   coefficient scratch is closed before a recursive call. Arbitrary bit
   interchange work is not interpreted as coefficients until its completed
   return. This note does not prove that physical dispatch/parking contract.
4. A direct leaf executes the elementary C kernels sequentially. Root
   reservations use only the specified disjoint selected axes; normalization
   is the section 8 formula of PR2287, with no intermediate rounding.

Let

    Gamma = 2^1296 product_(i=1)^36 (2^(2i)-1),
    s = 1041408 Gamma,  E = 2^100000,  B = s+E,
    C0 = 2^210000.

Then every interpreted coefficient and coefficient temporary in a width-e
recursive call has height at most t+2Be. The reservations and normalization
fit the retained layer bound t+(2B+18)d < t+C0 d. For the root t=0, one
grid with Delta=C0 d, fraction width p+Delta and signed word width
p+2Delta+3 implements the stated arithmetic exactly, including its shift
extent checks. Neither a new exponent nor a smaller production guard is
claimed.

## 2. What the executable ledger binds

The checker authenticates the selected archive and seven individual members.
It compares the local words with the embedded provider and the SHA256 in
each actual call. It does not import `bounds.scalar_charge`,
`caller.schedule`, the producer's rank profile or their aggregate results.
Every local event and caller event is assigned a closed-alphabet rule.
Unknown events fail. Native ranks are compared with directed recipe records;
idle ranks are compared with the actual pending suffix lengths. These are
source bindings, not new proofs of the recipe identities or hosting geometry.

The two 24,767-event words each contain 3,494 recursive children of total
rank 5,586. The 482-event caller dispatches 80 forward and 64 backward
words, 144 bridges, 160 idle sweeps, and its terminal monomial operations.
Thus there are 3,566,448 local events per cover class. The 35,840 original
idle deadlines contain 7,526 positive remainders. Zero-rank deadlines
still carry their source translations; the height rule is zero, not an
authorization to omit those operations.

The reconstructed positive-child histogram is

    rank:  1       2      3      4      5      7  8     48
    count: 349604  60192  62585  20448  11808  7  1152  4866.

It has 510,662 children and rank mass 1,041,408 per cover. For height
accounting this mass is multiplied by Gamma, never divided by the number
of live families W=14,336. The time recurrence has a different volume
normalization. No claim about the sharp necessary height follows from this
deliberately global maximum bound.

All 6,088 stored local monomial records have invertible 9-by-9 binary
address matrices, integer binary offsets and phases i^P with integer P.
Consequently their mathematical maps, inverses and columnwise lifts
preserve coefficient denominators and modulus. The finite check establishes
this shape, not the correctness of a tape implementation or equality to a
desired native operator. Cover permutations and Pauli alignments retain the
corresponding semantic hypotheses in section 1.

## 3. Scalar, leaf and normalization charges

We use the already proved PR2327 prefix bounds, credited also to Gareth
Davidson's earlier PR1282 Horner analysis. For a reduced scalar c=n/2^k,
write b=bit_length(|n|). A SCALE, or an ADD whose two inputs have height h,
has all coefficient temporaries and its completed output at height at most

    h + max(b,k).

The n=0 case has b=k=0. For nonzero n the unsigned Horner multiplier never
exceeds |n|, and 1+|n| <= 2^b controls the final ADD. Horner leaves the
input denominator unchanged; its final division adds at most k denominator
bits. One must distinguish that denominator bound from the temporary
magnitude bound h+b: the required extra reserve is their maximum, rather
than charging only the final coefficient magnitude. Negative numerators
and the source's non-normalized fraction spellings are reduced exactly.

The actual finite totals are:

| Item | Prefix increment sum | PR2287 conservative charge |
| --- | ---: | ---: |
| One forward word | 30,232 | 145,372 |
| One backward word | 30,179 | 145,420 |
| All local calls per cover | 4,350,016 | 20,936,640 |
| 32,256 signed bridge ADDs per cover | 32,256 | 258,048 |
| Complete scalar total per cover | **4,382,272** | **21,194,688** |

The source's local charge is 2b+k+4 and dominates max(b,k). Its bridge
allowance is eight per ADD; the sufficient increment is one. Each bridge
has 112 X ADDs and 112 companion Y ADDs. COPY/CLEAR, signed exchanges and
quarter phases add zero height. Prefix hashes in `RESULT.json` bind the
ordered cumulative local and caller ledgers, without materializing Gamma
cover classes.

Maximum local scalar shifts are 16 forward and 7 backward. The executable
controls run all 332 distinct actual coefficients through the pinned
arithmetic against independent rational outputs and inspect every allocated
temporary. They are finite application checks, not the quantified proof.
For example the source coefficient -65537/2 has an unsigned Horner prefix
65537 on input 1; its final magnitude is only 65537/2. On input 1/16 its
output is -65537/32, so ignoring the denominator charge fails too.

One C or inverse-C kernel has endpoint increment one and temporary increment
two. Sequential application of u >= 1 elementary axes therefore has endpoint
increment u and prefix increment at most u+1 <= 8u. This proves the direct
leaf allowance for any leaf width, including the global cutoff leaves.
For u=0 there is no kernel and no increment. The initial remainder of an
internal node costs at most delta at its endpoint and delta+1 <= 73 in
its own prefixes. The retained slack 32*73=2336 is more than sufficient.

Writing D=2j+o, the normalizer uses an optional (z-iz)/2, a quarter phase
and a shift by j. Its prefix increment is at most j+o=ceil(D/2); every
normalization shift is at most d. These are the actual closed normalizer's
operations, not D separately rounded record passes.

## 4. The chronological induction, including parked values

Consider the ideal exact arithmetic first. Let A(e) be a monotone upper
envelope for the additional height in an unfinished width-e call. This
definition makes the notation A(48f) legitimate; monotonicity of the
actual executed program's height is not assumed.

At any parent program point, each previous child has completed. Under the
endpoint hypothesis its contribution to the current maximum is at most
its width r f, regardless of how large its unfinished prefixes were.
The scalar contributions are nonnegative prefix increments. Thus just
before any child begins, the height is bounded by

    t + delta + f*(sum of preceding child ranks) + preceding scalar charge.

This bound also covers every stored copy and every parked coefficient:
those values were created at earlier program points and are preserved
while the child runs. It does not assign a numerical interpretation to
arbitrary bit-work strings. At most one active child adds an unfinished
envelope; all other children contribute their completed endpoint widths.
In particular, the *analysis* may improve a child's bound at return while
the stored grid and its exact bits remain unchanged.

Summing over every cover class gives a valid, loose bound on every prefix,
including local scalar temporaries and the final parent endpoint:

    A(e) <= A(48f) + s f + H',
    H' = 4382272 Gamma + 2336.

The executable exact integer comparison proves

    H' <= 21194688 Gamma + 2336 < E.

The two nontrivial charge magnitudes have respectively 2650 and 2652 bits;
E has exponent 100000. This verifies the proposed finite allowance from
operations, rather than from a copied summary. An omitted child, another
scalar alphabet or an implementation that performs additional coefficient
arithmetic would invalidate this particular binding.

Strong induction on width now gives A(e) <= 2Be. A leaf satisfies it since
8 <= 2B. At an internal node, f >= 1, every child has width at most 48f < e,
and

    A(e) <= 2B*48f + s f + E
          <= (96B+s+E) f
          <= 146B f
          <= 2B e.

Here E <= E f and 2B(73-48) >= s+E are exact inequalities. A direct proof
can replace A(48f) by max_(r<=48) A(rf); the same induction applies and
needs no monotonicity assumption at all. The ideal completed C-tensor
endpoint continues to have increment at most e, not 2Be, for use by its
parent. The endpoint correctness is the separately retained semantic
induction, not a consequence of this bound.

At the root, at most d disjoint reserved axes are processed individually.
Their prefix allowance is at most d+1. The recursive core has width at
most d. The H0 normalization adds at most ceil(D/2) <= d. These contributions
fit the predecessor's conservative additional 18d for d >= 1; the small-D
all-elementary fallback does too. Thus the retained exact inequality
2B+18 < C0 yields the stated whole-layer bound. This concerns one specified
layer invocation, not an uncharged sequence of independent layer calls.

## 5. Root-grid exactness and shift extents

Set Delta=C0 d, F=p+Delta and w=p+2Delta+3. All relevant heights are
strictly below Delta. A component of height h has an integer encoding N
on this grid, with |N| <= 2^(F+h). Since w-1=F+Delta+2, signed headroom
is strict for both signs, including all Horner and kernel scratch.

For a scalar denominator 2^k, the Horner numerator still has denominator
dividing 2^(p+h_input). The charged result height includes h_input+k,
which is below Delta. Hence its encoded numerator is divisible by 2^k;
also k <= Delta < w. Kernel halving has the same property with k=1 and
the completed kernel denominator charge. The normalizer's optional half
and final j shift have their separately charged denominator increments;
j <= d <= Delta < w. Zero shifts satisfy the extent test as well.

Consequently all divisions discard only zeros and meet the actual
`Grid.divide` syntactic extent guard. Combined with headroom, the pinned
arithmetic simulates the ideal procedure exactly. Child returns neither
round nor re-encode: exact endpoint cancellation may restore divisibility
on the unchanged root grid. Only the permitted final truncation is outside
this exact prefix argument.

## 6. Evidence and limits

The executable result is a finite source certificate plus exact integer
inequalities. The all-width assertion is the written conditional induction
above. The verifier has no random search, floating-point acceptance,
moment solver or imported ledger implementation. It does execute pinned
predecessor arithmetic as the subject of finite rational-oracle checks.

No discrepancy was found in PR2287's stated height allowance under the
listed semantics. This result does not establish native recipe identities,
common-label realization, hosting/owner geometry, full physical payload
execution, row/tape admission, actual work lifetime, time bounds, outer
Gaussian/FFT/recovery transfer, a Lean theorem or an unconditional integer
multiplication result. The small coefficient tests are not an execution of
the selected O(73,2) payload. Those distinctions are essential to the claim.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New material is Apache-2.0. Predecessor sources and notices are unchanged.
