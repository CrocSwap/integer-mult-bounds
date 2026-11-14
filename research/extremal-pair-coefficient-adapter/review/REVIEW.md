# Independent review of the extremal coefficient adapter

Status: PASS, including the corrected physical-history and shared-pool
lifetime contracts recorded below.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Base `e54523517d0f03e58352e647c403a5af3e525a57`.
Adapter SHA256:
`d2fc45eaca3a23a02a681df93d4412a0e9b48defa0c3800d6aa22a16263c94b6`.
Final reviewed proof hash is recorded in `FREEZE.json`.

## Verdict and independence boundary

The unchanged #6085 scalar contract supplies exactly the isolated calls
needed here. The new adapter's encoded argument construction, precision,
output ordering and ownership compose with A12's selected two-axis
coefficient-error premise, including the matched periodic aliases.
This conclusion retains the stated scalar/Count/Rational/ownership model
and source-parameter admission. It does not assert a complete Gaussian
producer, full source compiler, new kappa or unconditional multiplication.

I independently read the canonical scalar proof and actual exponential,
rational and loader code, and reviewed the new adapter and final error/cost
argument. I checked the frozen actual-source receipt against its exact
arguments and policy. I did not duplicate the author's scalar execution or
claim its predecessor oracle as an independent reviewer implementation.
The only new executed checker here is a small exact-source cleanup/history
surface check, introduced to resolve a concrete ambiguity in the space bill.

`SOURCE-CHECK.json` authenticates the six runtime inputs and five retained
proof inputs, including the original archives. The cleanup methods were
selectively extracted through the exact nested archive chain; the path and
hash of every retained slice appear in `runtime-slices/MANIFEST.json`.
No runtime source was edited and no archive was downloaded for this review.

## Scalar admission and the actual source pair

#6085 quantifies all represented P,F>=1 and rational 0<=f<=F for isolated
Exponentials calls. Its decay branch returns a downward approximation with
error strictly below `2*2^-P`, not necessarily the exact irrational floor.
The Axis and #6099 ProductionPlan guards are not antecedents of that
isolated primitive. The import-time authenticated-runtime guard still is.

For u=alpha^2 and integer `1<s<t<2s`, delta=t-s satisfies
`1<=delta<=s-1`. Hence both `A=2delta+1` and `B=2s-1` lie strictly between
zero and 2s. The four actual rational arguments `uA/s` and `uB/s` are
therefore in `(0,F)` for F=2u. The source geometry is direct: at
`beta_i=-(s-1)/(2s)`, the two exponent differences are
`(rho+beta_i)^2-beta_(i+1)^2=(2delta+1)/s` and
`(beta_i-1)^2-beta_i^2=(2s-1)/s`. No diagonal-similarity transfer is used.

The wrapper computes u, A and B through the retained Count operations on
owned copies. Rational(...,reduce=False) uses the existing exact fraction
ABI, with a copied positive denominator. No gcd is silently omitted from a
default reducing constructor. No host integer, Fraction or oracle result
is injected into the protected source computation.

One shared setup uses P=p+8 and F=2u. The four calls are decay with scale
None, in plus/minus order on axis 1 and then axis 2. Separate power_two(P)
outputs give four exact diagonals. The returned grid Count is a distinct
copy. This binds all eight row-major fields to the declared source factors.

## Error and rank transfer

The raw coefficient error is `<2^(-p-7)`. The stronger A12 source premises
give `w^2>=(16p)^-36`; at p>=4096,
`p>=30+36 log2(16p)` implies `2^(-p-7)<=2^-37 w^2`.
The gap increases with p. This uses the actual retained alpha choice;
the adapter's broader guard `alpha^2<=4p` alone is not a rank-admission
condition.

The source periodization is the exact matched Pi(G) from BILATERAL-LDU,
not every matrix bearing a Gaussian label. Its selected-pair alias error
is at most `4exp(-a t^2/8)`. With t>=32 and a>=1,
`a(t^2/8-4)>=124>39ln2`, so it is at most `2^-37 w^2`.
Adding the strict scalar error proves `<2^-36 w^2` relative to each
selected periodic factor, including exact-one output diagonals. This
closes the particular A12 further-table-error premise with its stated
margin. Tensor materialization and inversion are mathematical consequences
or separate services; neither implementation is provided for free.

The frozen executable packet has p=1, alpha=2, P=9, F=8 and R=251. Its
four arguments are 12/101, 804/101, 12/103 and 820/103, and its output is
`[512,352,0,512,512,355,0,512]`. Both zero coefficients are legitimate for
this broad low-precision producer domain. The packet is explicitly outside
A12's large-p margin domain and cannot certify the rank conclusion.

## Complete local arithmetic and output bill

The explicit guard u<=4p makes X<=32p. The stated bounds on k,H0,c and
`R<=129p+6ceil(log2p)+122<=257p` hold even at p=1. With B the maximum
input bit length, accepted numerator lengths are at most 2B+3 and denominator
lengths at most B. Thus the inherited scalar tariff remains
`O(R^3+(R+B_f)^2)` with `B_f=O(B+log p)`, and four calls plus one setup give
`O(p^3+(p+B)^2)`. Copies, comparisons, products, four diagonal fields and
the nine returned Count records are paid in that bound.

B cannot be dropped from A12's lower bound on s. An additional full-source
upper-size interface is needed for the simpler O(p^3) form. The result is
in the retained encoded elementary-arithmetic model; it is not an emitted
new native ROM or a complete multiplier tariff.

## Correction: physical history and actual revisit work

The first draft permitted arbitrary earlier scratch history while claiming
total storage O(p+B). That conclusion needed a stronger entry condition.
Both lead and independent review identified the gap. The corrected proof
uses fresh private grants, or an explicit current-size entry-history bound,
for its simplified total-space statement. For arbitrary reused blank roles
it keeps `sum_tau max(H_tau,C(R+B))` on the actual owners. Any extra requested
full-history sweep or transport must pay its actual extent.

The exact nested runtime resolves whether a further time term is automatic:

1. Cardinal Count inherits Natural.close, which delegates to its tape.
2. A private Count tape is a Lease; Lease.clear calls the physical Tape.clear
   and ends that lease without deleting or shortening the physical backing.
3. Tape.clear rewinds, erases the contiguous current nonblank prefix through
   RIGHT, stops at the first BLANK and rewinds. It does not scan an older
   already-blank far tail.
4. ScratchPool.acquire/empty and session.erase_marker inspect origin cells.
   They do not scan the old blank capacity either.

For ell nonblank cells through RIGHT and a head at 1, the actual clear costs
exactly `5ell+7` native reads/writes/moves. Earlier blank capacity changes
resident stock, but not that clear cost. A fresh pool starts each tape at
only LEFT/head 1; the stated O(p+B) history bound then follows from the
maximum carrier size during this invocation, not from final output length.

`check_history.py` executes those exact retained method ASTs, with only an
accounting Meter supplied by the checker. Nine cases cover binary lengths
1, 7, 31 and old capacities 1, 257, 65537; the exact clear counts are invariant
under old capacity, while the old backing length remains. Normal and
optimized receipts match. These are cleanup-surface checks, not another
exponential or full-source execution.

A negative control supplies a distant dirty cell beyond an initial blank.
The origin-only pool-empty guard succeeds while that dirty cell survives;
the independent whole-history oracle detects it. This confirms why the
reused-cohort premise must be *blank* and why pool.empty alone is not a
certificate of arbitrary dirty-tail erasure. Such dirty entry histories
are outside the admitted ownership invariant.

## Borrowing, returned owners and final retirement

The successful path preserves the six borrowed Count bodies and canonical
heads. Temporary F/P remain live until all calls end; scalar fields close
before those parameters. Every argument owns copied numerator/denominator
carriers, so its close cannot consume a source parameter. Nine distinct
returned Counts remain live and must be explicitly consumed or retired.

Tables.close retires those outputs. It is necessary, but not by itself
sufficient, for emptying a shared pool: every other live lease must also
have been released by its owner. Borrowed input Counts may themselves be
live leases in that same pool and must remain untouched by this adapter.
The primary fixture creates its input Counts before installing the private
pool, so it correctly observes exactly nine pool leases at return. The
general interface does not infer that global live count. A separate tiny
retained-ABI control verifies that retiring an output preserves a borrowed
live lease and that pool.empty rejects until the remaining owner releases it.

The eager evaluation of several constructors before entering `owned(...)`
does not establish arbitrary allocation-fault atomicity. The final theorem
correctly retains adequate runtime ownership/capacity, successful admitted
execution and its explicit guard-failure scope, excluding malformed tapes,
allocation failures and asynchronous rollback.

## Reproduction and remaining obligations

Run the small independent history check with:

```sh
python check_history.py
python -O check_history.py
```

It is read-only by default; `--write PATH` explicitly records output.
Its source slices are byte-pinned before loading. The author's separate
actual scalar normal/-O receipts were inspected and match; they were not
rerun by this reviewer.

Exact source/primality/alpha admission, source-index acquisition and routing,
arbitrary phases or dimensions, inverse algorithms, payload transport,
global rounded-H identity and whole-caller/fixed-tape compilation remain
separate. The production-plan guard is bypassed locally, not repaired
globally. All five foundational assumptions and the selected kappa remain.
