# The persistent z4 echo needs one more sufficient fractional guard bit

The unchanged PR1410 persistent pair has a larger chronological ADD-error
amplification than its two separate calls. In the explicit finite rounding
model below, the uniform sufficient guard increases **13 to 14 bits forward**
and **12 to 13 bits in the inverse word**. This closes a numerical implication
left open by the prefix row-L1 30/42 comparison; it does not admit a physical
supplier, set a host precision bucket, or claim a new kappa.

This follows Aaron Wang's [PR2464](https://github.com/CrocSwap/integer-mult-bounds/pull/2464)
precision handoff at `f364b97ff4700147fc06e622b79952b9fe6c4fa8` and Cinna Davis's
[PR1410](https://github.com/CrocSwap/integer-mult-bounds/pull/1410). Their words,
mechanisms, scalar savings, and hypothetical moment calculations are credited.
The new object is the exact **error impulse ledger at every chronological cut**.

## Source-bound result

| Word | ADD / NEG | Exact input prefix norm | Gamma | M | q |
|---|---:|---:|---:|---:|---:|
| Separate forward |1840 / 176|30|431|3990|13|
| Joint forward |1720 / 184|42|703|6945|14|
| Separate inverse |1840 / 176|22|429|3197|12|
| Joint inverse |1720 / 184|22|701|5012|13|

`Gamma` and `M` are maxima over **all registers and all cuts**, not just the
final output. Forward endpoint-only values are Gamma 358/486 and M 2702/4447;
those smaller values cannot be substituted into the all-cut feedback argument.
The unchanged 56 registers all begin with arbitrary exact real values of
absolute value at most B. No dirty workspace is assumed zero or discarded.

The complete separate and joint words contain 2016/1904 signed scalar records.
Their exact canonical word hashes match PR1410's frozen `RESULT.json`. The
pinned PR1391 emitter is reused solely to obtain those literal words; no
predecessor error-analysis code is imported. Both inverse words are generated
by reversing the exact records and negating ADD signs. Every ADD is charged
as a possible error injection; every NEG is explicitly executed and assumed
exact in the named numerical model.

## Precise numerical model and proof

Let `P_i` be the exact prefix map immediately before ADD i, and let d,s be its
destination and source. Define `a_i = ||P_i[d,:]||_1 + ||P_i[s,:]||_1`.
Let `G_c[r,i]` be the signed coefficient with which an additive error inserted
immediately **after** ADD i reaches register r at cut c; it is zero for future
events. The exact constants are

```
Gamma = max_(c,r) sum_i |G_c[r,i]|
M     = max_(c,r) sum_i |G_c[r,i]| a_i.
```

Both are exact induced norms for their respective independent additive-error
boxes. Sparse forward coefficient propagation enumerates every chronological
cut. Only the destination row changes at each event, so maintaining row norms
and updating that row loses no maximum. Source columns and error columns are
kept separate. Signed cancellations are retained before taking absolute values.

A separately implemented reverse covector traversal reconstructs every
coefficient of each reported maximizing row. Direct scalar execution with
adversarial error signs attains Gamma, and with errors `a_i sign(G)` attains M.
These witnesses prove sharpness for **independent error boxes**, not that a
specific floating-point rounding process can realize all signs simultaneously.

Assume each implemented ADD has local error

`|e_i| <= u (|approx_destination_before| + |approx_source_before|)`.

Assume NEG is exact, initial values are exact, and there is no overflow or
other error source. If E is the maximum error over every register and cut,
then `|e_i| <= u (B a_i + 2E)`. Exact linear superposition therefore gives

`E <= u B M + 2u Gamma E`.

When `2 Gamma u < 1`, this proves the explicit all-cut bound

`E <= B M u / (1 - 2 Gamma u)`.

For every integer `b >= 0`, choosing `u <= 2^(-b-q)` and
`2^q >= M + 2 Gamma` suffices for `E <= B 2^-b`. The table gives the least
integer q satisfying this **sufficient inequality uniformly over b >= 0**:
the four exact threshold denominators are 4852, 8351, 4055 and 6414.
This is not a minimum-precision theorem. The bound can be conservative, and a
different correlated-roundoff argument may improve it.

In particular, the forward joint threshold 8351 exceeds 8192, while the separate
threshold 4852 fits below 8192. The extra sufficient bit follows from the complete
error ledger; the prefix amplitude 30/42 alone does not prove it. Integer range,
input inexactness, physical child errors and packed precision buckets are
separate costs and are not inferred from q.

## Reproduce and controls

```sh
python3.12 -I -B scripts/research_package.py --package research/z4-persistent-error-envelope
```

Standard library only. Expected final lines are `PASS_Z4_PERSISTENT_ERROR_ENVELOPE`
and `PASS_Z4_ERROR_PACKAGE`. `verify.py --write` explicitly regenerates the
receipt. All rejection paths remain active under `-O`. On restricted Windows
hosts, set TEMP/TMP to a writable workspace directory for subprocess controls.

The elementary positive control is `x += y; x -= y`: its exact endpoint is
identity but its constant-error endpoint norm is 2 and weighted norm is 5.
Five semantic controls reject endpoint-identity-as-zero-error, using operation
count as the weighted error bill, an undercharged guard, an omitted error event,
and discarding a NEG sign. Minimal relocated replay passes; four actual mutated
receipts/source inputs are rejected, including an omitted inverse orientation,
missing impulse coefficient, understated q and changed emitter bytes.

`SOURCES.json` pins the original emitter, word receipt and documentation with
SHA-256 and Git blobs. `PREDECESSOR.json` pins PR2464's contextual handoff only.
The scientific base is canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
priority revision 4. Picker nonce `da246e0f25daa9f28fc00569c745d313` selected
independent-verification; `TASK.json` records the change from another aggregate
moment check to this missing chronological numerical implication.

## Open next questions

Can a named host charge q=14 forward and q=13 inverse with its actual range,
source-error and child-error models? Bind these local hypotheses to one real
host bucket law before asserting that 192 or 512 bits suffice. The missing
typed child, widened workspace lifetime, physical host and precision/tape law
remain blockers. The structured question is in `TASK.json`.

No selected supplier, source word, frontier, wrapper schedule, or recursive
histogram changes. Native physical execution, host precision admission,
all-size compiler, analytic transfer and formal proof are unrun. This package
does not conclude that PR2464's hosting obligation is its only remaining one.

## Credit

Cinna Davis supplies PR1391's order-four paired frame and PR1410's persistent
pair, extending Ross Richardson / PR1287 and Sagar Thakrar / PR1227. Aaron Wang
supplies PR2464's explicit carry precision handoff. Original emitter attribution
and licenses remain intact. Prepared for **ywz65** with substantial OpenAI Codex
assistance in research, mathematical derivation, code, tests and writing.
Apache-2.0; no independent human review.
