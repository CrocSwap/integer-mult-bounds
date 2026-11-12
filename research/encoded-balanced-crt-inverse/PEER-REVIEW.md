# Independent proof, control and cost review of the encoded CRT inverse

Reviewer: `/root/tape_dispatch`, separate from the author, with OpenAI
assistance for @CubeJerry's research run. Date: 2026-11-11.

## Outcome and scope

**PASS for the stated source-relative theorem and source-model resource
bounds. No blocking proof or control defect found.** The review preserves
the documented distinction between encoded source operations and an emitted
literal binary machine, and between the address-state inverse and a payload
converter or selected outer-caller implementation. No new kappa follows.

This review read the changed frontend and producer, the entire proof, and the
unchanged frontend, endpoint writer, owner, entry adapter, word arithmetic and
record routines. It independently traced the symbolic control and lifecycle
invariants and checked the cost/space sums below. It did **not** rerun the
author's tests or use them as proof. The orchestrator's separate numerical
inverse/CRT-idempotent execution is complementary evidence, not an experiment
performed by this reviewer.

The reviewed frozen package is `work/analytic_recovery/encoded_crt_inverse`
on scientific base `e54523517d0f03e58352e647c403a5af3e525a57`:

| File | SHA256 |
| --- | --- |
| `inverse_frontend.py` | `0e5f4c9450372c90000f5ebf3c22dfbe7241dd53da9ae9bcce310af859b009ef` |
| `inverse_producer.py` | `6acdebee7134fbc8e2d121060286bd05e7282900da8a28a78c80937dde7ea178` |
| `PROOF.md` | `edbeb16bd8d088ab75b73b22adf5fc8aeef1ec93e8333bf74d4ad8e7f2f3d51f` |

Static authentication independently matched all nine exported inputs by
byte length, Git blob and SHA256 against `INPUT-PINS.json`. A byte comparison
also confirmed that the producer is exactly the original source with the two
declared credit comments and its one add-to-subtract replacement. No author
file was edited.

## 1. Reverse topology and the half-size invariant

The base `_shape` leaves the unary depth word `ONE^k RIGHT`, half-size one,
the first axis marked STEP, and all relevant heads at one for d=2^k. The new
constructor moves the depth head once, explicitly calls the **base** doubling
method for each remaining ONE, sees RIGHT and rewinds. Therefore it makes
exactly k-1 doublings and initializes H=d/2. For d=2 it makes none. Explicit
base-method dispatch prevents the new halving override from running during
bootstrap.

At a level, unchanged `NodeEntry` scans exactly two H-axis blocks and records
only the next start via VALUE. `_advance` either moves STEP to that marker or
finishes the level, advances depth by one token, and invokes the override.
The override scans H unary tokens with a finite parity flag and emits H/2
tokens. The even/nonempty checks are valid: a transition is needed only when
another depth token remains, which means H>=2. The old half stream is cleared,
the temporary is copied back, both delimiters are manufactured explicitly,
and the temporary is cleared. All heads return to one.

The resulting widths are d/2,d/4,...,1, with increasing aligned starts at each
level. Their node counts are 1,2,...,d/2, summing to d-1. No new Port, per-level
inventory, decoded level, start or host node list enters this construction.
The inherited temporary is empty after each base doubling and each halving,
so the next append is to blank space. Its older erased suffix is not rescanned
or discarded.

## 2. Subtraction and current-left reconstruction

The inherited reconstruction loop maintains a prefix product and adds

    prefix * ((x_i - lower*prefix^-1) mod s_i)

to `lower`. The new value is below `prefix*s_i`, preserves the earlier
congruences, and is congruent to `x_i*prefix` modulo s_i. This proves the
current-coordinate congruences used in section 2 of the proof. Even if a left
coordinate is padding, its arithmetic uses its reduced digit, so intermediate
capacity remains valid before the final `left_valid` branch sets lower to zero.

The right prefix includes every preceding right modulus, independent of
coordinate validity. The inverse changes only the final rotation to
`(canonical-offset) mod modulus`. For fixed current left coordinates, this
is exactly the inverse of the old positive rotation on valid right values;
padded right values are copied unchanged. The offset record remains the same
positive offset, which is correct because the writer skips that field and
copies the separately serialized updated value.

The modular subtraction seam is safe in both branches. For 0<=u,v<s, direct
subtraction is nonnegative when u>=v. Otherwise `(u+s)-v` lies in [0,s), and
u+s<2s<2^P_G, so the inherited word addition cannot overflow. It needs at most
two newly live words, then frees the intermediate. The old add-and-reduce
branch also permitted two words at its peak. Borrowed operand heads return
through the same raw arithmetic methods. Thus neither the inventory bound nor
the inherited linear modular-primitive class is enlarged.

Each node fixes its left coordinates; nodes within a level have disjoint
support and controls. Consequently reversing the level order and inverting
the right rotations gives both composition identities on the full padded
rectangle. A globally invalid input need not be fixed by every lower node;
the proof correctly avoids that stronger false assertion.

## 3. Staging, retired commits and exact physical restoration

The unchanged writer stages the complete next logical source while the current
numerical lease remains live. It writes only the staging role and restores
source/result/guide/axis/half heads before returning. `lease.close()` consumes
the numerical output, retires guide/canonical input/guard data, releases the
bank and advances the topology. Only then can `commit()` write the staged
source. The final-node case is valid even if topology has already retired:
commit requires only source and staging.

All source headers, widths, moduli and delimiters are copied unchanged. Only
the prescribed coordinate fields differ. The staged source has exactly the
same logical extent, so commit writes within existing source backing and does
not grow or replace it. It never accesses the historical nonblank tail after
RIGHT. The next numerical entry reads coordinates from the actual committed
source, including after undoing the root; it does not reuse earlier left
coordinates or a cached reconstruction.

Projection remains valid with subtraction. Every updated valid value is below
s_i<2^h_i, and every unchanged padded value is below 2^h_i. Their higher
P_G-h_i bits are zero, precisely the writer's existing checked projection
condition. There is no signed output or extra field to transport.

## 4. Precision shrinkage followed by regrowth

The proof correctly separates level boundaries from successive nodes. For
widths (2,2,3,3), the reverse sequence is exactly 11,5,7. In general the
minimum width m is at least two, and an n-axis level has minimum precision
1+nm while the next level has maximum 1+(n/2)(m+1). The asserted strict
cross-level decrease by at least n(m-1)/2 is correct. It does not imply
within-level monotonicity.

I checked the actual entry/owner methods for the required regrowth. Every
guard is rebuilt from the current unary guide; RIGHT is placed at the current
P_G+1, not at the far end of historical backing. Each numerical word uses the
current template and current RIGHT delimiter. `Word.msb`, `erase`, arithmetic
loops and `Port.clear` stop at current symbols. They do not use the historical
last allocated cell as the current precision.

On retirement, every live current word and its delimiter are erased. Any
older suffix was already erased on its previous retirement. Hence decreasing
11 to 5 exposes only blank old tail, and increasing 5 to 7 reuses blank cells
without a stale delimiter or digit. This induction also explains why retirement
need not scan the whole largest historical extent at every smaller node.
The bank's local blank checks alone would not prove the invariant; the
producer/entry erasures supply the missing global induction.

## 5. Complete time and capacity accounting

The new half-size work is linear in its processed unary lengths. Bootstrap
lengths sum to less than d/2; descending input lengths sum to less than d.
The displayed loops perform a fixed number of symbol operations per token,
including temporary copies, rewinds and `clear`. The conservative 1024(d+2)
additional raw-action allowance is sufficient. The old writer/frontend
2^18(M+2)^2 envelope therefore fits within the new 2^19(M+2)^2 raw allowance.
The unknown finite-control refinement constant C_inv is explicitly retained.

The new subtraction uses only a comparison, one or two inherited linear
word operations, and at most one intermediate-word erasure. It stays inside
the existing modular subtraction tariff and the old two-temporary-word
envelope. The numerical proof may therefore retain its structural degree
bound; the new 2^21(P_G+2)^4 allowance is conservative. There is no basis here
to cancel any entry, owner-release or source-copy occurrence.

I independently recomputed the writer sum. At n-axis level, the groups
partition the widths, so their total n(P_G+2) is 3d+nA. Summing n=2,4,...,d
gives exactly

    3d log2(d) + 2A(d-1).

There are d-1 complete M-sized source stagings/commits. With A>=2d and
M=2+3A+4d, these are quadratic source costs. For the numerical terms,
P_G+2<=3nm and the geometric cube sum is less than 8d^3/7. Thus the stated
fourth-power total is less than (648/7)A^4. The squared total is O(A^2).
These calculations establish the complete O(A^4) source budget as stated,
not a new multiplication rate.

The 63-role numerical history expression has the correct inventory: one
guide, two canonical source streams, 56 numerical words plus one template,
and three padded/result streams. The eight protected guards and seven
topology roles are additional, and the staging role brings the total to 79.
Every term bounds a maximum for its physical role across the full invocation;
precision shrinkage does not delete old backing. The new half-size temporary
stays within its old d+2 allowance.

The staging allocation is at most M stored cells but can visit head index M.
The proof explicitly distinguishes M allocated cells from M+1 visited cells,
and does not relabel this mixed predecessor backing model as a literal binary
space certificate. That qualification is necessary and correctly retained.
An arbitrary source history is separately charged by K_source. Two fresh
invocations retain both 79-role inventories: K_source+2D and 158 private
histories. Reusing one inventory is not established or silently credited.

## Acceptance boundary

The result is accepted under the stated successful linear-use lifecycle,
valid source framing/coprimality/width promises, clean initial private
inventory and pinned numerical/entry/owner source contracts. Arbitrary dirty
acquisition, stale borrowed handles, malformed-input rollback, crash recovery,
same-bank restarting, payload routing, common global-row choreography and
selected caller admission remain outside the theorem.

The proof appropriately claims a finite-symbol **source-relative** evaluator
and source-operation costs. It does not supply an emitted common binary
instruction table or numerical value for C_inv. The independent numerical
checker may strengthen executable evidence, but it does not change this
computational-model boundary. No further author correction is requested by
this review for the pinned snapshot.
