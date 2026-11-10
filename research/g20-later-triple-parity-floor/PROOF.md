# A consistent-payload obstruction for one later G20 capture

This is a scoped proof with an exact finite certificate. Its new statement
concerns helpers `H = {297, 465, 591}` of the frozen PR5708 word. It does not
recheck the predecessor's native word, frame semantics or earlier census.

## Contract

Use the PR6113 B1 capture alphabet, following the later-reinjection question
in PR6117. Every source outside H remains arbitrary and independent. Own the
three helpers and surrender their productive targets, of ranks 8, 4 and 8.
The predecessor's 48 already owned fields start at zero. Keep the scalar
schedule and native maps fixed. A paid query can be deleted only when its
entire payload is identically zero. Other call ranks remain unchanged.

The candidate has three arbitrary native permutation-linear payloads A, B, C.
Replace helper 297 by A immediately before event 6292, helper 465 by B before
6296, and helper 591 by C before 6622. Event indices are zero based. All three
events are ADD reads of the respective helper. Permit every earlier write
into 297 to be discarded, and keep it zero until its injection. Its first
read is event 6292, so this is the maximal unread leading clearing permitted
by the model. Keep earlier propagation from 465 and 591, including their reads
at events 0 and 6129. This is the changed premise relative to first-read
capture. The third helper extends the proposed joint-dead pair {297, 465}.

Grant the availability and delivery of these payloads and all final cleanup
at zero cost. In particular, no native proof of these grants is needed for
this negative result. Trailing erasure of the captured helpers cannot remove
further paid calls after their last uses. Additional changes of schedule,
other replacement times, extra injections, partial target splitting and
rank reduction of nonzero queries are outside this contract.

## Necessary constant-input equations

Specialize each retained public input outside H to its own independent
constant bit. A native address permutation fixes constants. Hence Q and
ZERO_Q do not change a constant response, ADD is XOR, and ERASE gives zero.
Native permutation-linear injected payloads are also constant on these inputs.
Grant their responses to be three arbitrary vectors a, b, c of binary source
coefficients. This enlarges the possible payload set.

Represent a wire by its fixed source-coefficient vector v and a three-bit
mask d specifying which of a, b, c occur. A removed query must satisfy

```
d_0 a XOR d_1 b XOR d_2 c = v.
```

If d is zero and v is nonzero, the query cannot vanish for every public
input. If both are zero, count the query as removable even if its full native
payload is not zero. In this relaxation, the exact event replay partitions
all 2,846 paid queries into:

- 2,828 with zero dependence and nonzero fixed response;
- one automatically removable query, event 6291 of rank 1;
- 17 queries with nonzero dependence, each with a distinct equation.

[RESULT.json](RESULT.json) records every equation, its exact binary label and
its query index/rank. These labels come from the new three-replacement replay.
No saved predecessor census is used as an oracle.

## Complete consistency optimization

For any three payload responses, let S be its set of satisfied equations.
Choose an independent basis of their masks in F2^3. This basis has size at
most three. Every equation in S follows from the basis with the same XOR of
right-hand sides. Thus enumerating the 834 subsets of at most three of the
17 equations, rejecting inconsistent ones and taking their implication
closures, upper-bounds every possible payload assignment.

The first finite oracle performs this enumeration by binary elimination.
It finds 274 distinct implication closures and 31 rank histograms. The
maximum removed rank, including the free rank-1 query, is 13. A separate
oracle exhausts all 131,072 subsets of the 17 equations. It constructs each
subset's complete mask-to-label span, accepts precisely 292 consistent
subsets, and obtains the same maximum 13. These are complete finite domains,
not search cutoffs or sampled payloads.

The certificate gives three explicit binary payload responses attaining the
relaxation maximum. Their removable queries are exactly events 6291, 7802,
7943 and 8340, of ranks 1, 5, 5 and 2. This proves sharpness of the parity
relaxation. It does not assert that full native payloads attain those four
deletions. Every actual deletion pattern satisfies the relaxation, so its
removed paid rank is at most 13.

Optimizing each dependence class independently instead gives rank 20. Those
separately chosen right-hand sides need not come from the same a, b, c.
The verifier rejects this inconsistent upper estimate as a certificate of
rank 13. The consistency constraint is the new step beyond the looser
separate-class screen.

## Complete local signed comparison

Write t = 1-C, where 0 <= C <= 1/100. Every paid rank r is a positive integer,
so r^t <= r. Removed tariff is therefore at most 13 throughout this interval.
The surrendered productive tariff is 2*8^t + 4^t. The exact integer inequalities

```
8^99 * 5^100 > 39^100,
4^99 * 10^100 > 39^100
```

prove 8^(99/100) > 39/5 and 4^(99/100) > 39/10. Monotonicity in t gives

```
2*8^t + 4^t > 2*(39/5) + 39/10 = 39/2.
removed tariff - surrendered tariff < 13 - 39/2 = -13/2.
```

Unchanged paid and productive terms cancel. Any added physical charges only
increase the loss. The candidate cannot improve this local signed invoice,
even under the zero-cost grants. This rejects the named later-capture
continuation without asserting an optimum for other triples, other schedules,
all G20 mechanisms or integer multiplication. It supplies no new kappa.

## Verification boundaries

The replay authenticates the exact word and frames with SHA256, reads the
three target ranks, reconstructs the parity equations, checks both finite
oracles and verifies the integer power comparisons. Normal and optimized
Python execute the same explicit contracts. The generated receipt binds the
input files and verifier bytes. Five control groups cover erased labels,
incompatible separate-class optima, a wrong injection read, an understated
target debit, and inconsistent equations.

No predecessor native replay, supplier admission, independent human review or
formal proof-kernel review is claimed. The five framework assumptions remain.
The proof deliberately grants physical availability instead of validating it.

The verifier uses managed Python allocation. Its live domain is fixed by two
hash-authenticated inputs: 685 wire rows, 14,794 events, 17 equations, masks
with at most three variable bits, at most 834 basis candidates and 131,072
subset candidates. No recursive calls or unbounded search are used. Each
function is shorter than 60 lines. The immediate callbacks in the rejection
controls have four fixed local targets and no retained lifecycle.
