# Independent review: fixed binary raw-context owner census

**Decision: ACCEPT the stated one-bank owner census and its conditional beta=2 corollary.**

Reviewer: a separate OpenAI Codex research worker for Jerry, independently of
the author worker and its checker. Source construction and interpreter credit
remain with Ali Romman's PR #8042 and the inherited binary graph/caller.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.

Reviewed source head: `dfd25d553a843a946ca0b94130a5ff8943e98fdd`.
Reviewed author `PROOF.md` SHA256:
`672289a9a52ffdc710b4ff037c03c7149097fb99a9083ba9da62021edc77c97f`.

## Accepted statement

Let B be the productive external owners installed in a fresh
`binary_receiver.Receiver.compiled` invocation. For the fixed raw word put
q=104904 and C_* = sum_e count[e]*(104904*delay[e]+1). Throughout a successful
production Plan, including opening, closing and allocator substeps, the live
owner count and that fresh allocator's capacity are at most B+22339*C_*.

The same reasoning applies to a successful schedule with this literal word,
finite nonnegative replica counts and the descending power-delay/loan
contracts. Thus 22339*C_* <= B is sufficient for the one-bank beta=2 premise.
The census theorem alone does not establish that inequality at all production
heights. The analytic join is a separate proof/review; the selected kappa and
unrelated premises are unchanged by this review.

## Source binding and independent exact census

The reviewer authenticated all 11 retained files and compared both decoded
JSON objects with their authenticated gzip payloads. Reading the dispatch
chain in binary_receiver.py, raw_binary_stage.py, strong_binary.py,
raw_binary.py and tagged_sources.py confirms BinaryWord and ActiveCatalogue
use the same graph/caller functions without a rank argument. The powered
helper is outside that dispatch. Columns/rank change geometry, not inventories.

The checker scans register liveness directly from JSON and imports none of
the author's checker or census code. It obtains:

| Item | Independent result |
| --- | ---: |
| Public registers | 630 |
| Inner instructions | 39600 |
| Inner INIT / CLEAR | 3433 / 3433 |
| Inner ADD / SWAP / MOVE | 29301 / 630 / 2803 |
| Outer LOCAL / QUERY / IDLE_ONE | 36 / 4 / 32 |
| Root ports / diagonal entries | 111 / 38 |
| Fixed input targets / paid resumes | 18906 / 104904 |
| True inner private peak | 3433 |
| Private peak at paid cuts only | 2803 |
| Private allocation lifetimes across one raw word | 124032 |

The final quantity is 36*3433+4*111, a lifetime total, not a simultaneous bound.

The final inner MOVE is at instruction 29029, while the larger private peak
occurs at instruction 35534. The last outer paid branch is LOCAL at event 761.
Thus the raw context really reaches the larger peak during its closing
resume, after removal from Plan.decode's live dictionary. Paid cuts alone or
registered dictionary entries would undercount this source.

## Mathematical audit

Each of the 18906 input bindings creates at most one owner; external jobs and
pending loans reuse an existing owner. The entire native register trace bounds
private ownership. QUERY and LOCAL are serial branches, and each QUERY clone
is retired before the next port, so the additional peak is max(3433,1). This
gives 22339. Matching routes, XOR and SWAP use work tapes rather than bank
owners. Leaf recursion is separately charged to other banks/work storage.

Charges follow allocation origin. Installing a loan in another context does
not allocate. For birth b in band e, [b,b+q*delay[e]] includes opening zeros,
suspended private owners, the closing native tail and zero retirements. At a
tick there are at most count[e]*(q*delay[e]+1) inclusive birth slots. Summation
proves the bound without estimating Measure.mass.

Strict decrease between powers of a base D0>=q gives q*D_child<=D_parent.
The child closes before the next parent resume. In the equality case,
close-before-paid order and ascending-band closes put the child first even
when the parent also closes. Descending-band opens collect same-tick loans
after issue. Induction down the finite band order covers forwarding an
ancestor owner, so no owner outlives its origin interval.

At completed allocator calls, live and vacant indices partition the range
below capacity. Free-first allocation increases capacity only when no vacancy
exists. Capacity therefore equals the historical maximum completed live
count. An in-flight owner at intermediate statements is already covered by
the current context or initial B fields.

### Correction made during review

The first draft asserted the partition at every statement and equality with
live count whenever capacity increases. Literally capacity increments before
live.add, and live.remove precedes the vacant append. The author corrected
this to completed-call invariants and explicitly charged the in-flight owner.
The coefficient and bound did not change. The frozen proof hash above includes
this correction.

## Independently executed evidence

The checker uses its own register scanner and a calendar made by enumerating
all births, paid resumes and closes and sorting their event keys. It compares
that calendar exactly with the unmodified retained Plan.events. The retained
Plan.decode then runs against an instrumented owner machine that deliberately
allocates more private owners in its closing tail, exposing removal before
retirement.

The 36 bounded fixtures cover q in {2,3,4}, delay base q or q+1, epoch lengths
1,5,100 and two loan policies. They include private-owner loans and forwarding
of an input owner, with three simultaneous generations holding one ancestor
owner. There are 5088 contexts, 25440 exact calendar records and 90232 observed
owner states; 1948 borrowed-origin bindings are checked. The instrumentation
observes 6956 opening and 37484 closing transient states, and 444 states where
counting only registered contexts underestimates the required bound.

These are protocol tests of the exact source event/decode kernels, not
production-sized Plan constructions or a replacement for the all-size proof.
Replica counts, links and external source descriptors are injected. Measure
and the analytic Plan constructor are intentionally not run.

The checker extracts the unmodified allocator methods from the retained AST
and executes them on byte tapes: 252 legal allocation/retirement histories of
length 10, comprising 3496 calls across explored prefixes, plus actual clone
copying and free-first reuse. It verifies OwnerBanks inherits those methods
unchanged. AST call-surface checks bind the allocator operations in the inner
and outer raw interpreters.

Negative controls reject a missing CLEAR, public INIT destination, dead
operand, paid-cut-only undercount, registered-context-only undercount, a delay
base too small to return a loan, and reversed same-tick close ordering. A warm
allocator with capacity 10 but one live owner rejects resetting history to
current live usage; a retired-owner read also fails.

Normal and python -O runs give byte-identical evidence, SHA256
`5bc6f15fa36a23d27085ff01c8db145a7740dbb824c5d6ba12d1d6ec5820e9e3`.
The independent checker does not use assert for enforcement. Evidence contains
deterministic exact counts; replays write stdout or an external temporary file,
leaving frozen receipts unchanged.

## Limits and integration

Acceptance concerns owner identities in one fresh compiler bank, conditional
on a successful source invocation. It does not prove physical byte capacity,
work-tape counts, chart arithmetic, zero-output semantics, total visited
storage across recursive ancestors, or supplier admission. Those belong to
their respective source and composition theorems.

This review does not certify all-size numerical enclosures for count[e], the
largest-delay growth exponent, or the final sufficient inequality for beta=2.
Any accompanying arithmetic corollary has its own independent review. The
fixed coefficient closes the raw-owner census component only.

For a previously used physical backing role, keep the maximum of its earlier
reserved bytes and the current field volume times the proved owner bound. A
fresh logical OwnerBanks object does not reset the visited history of a reused
physical head. The author's explicit entry-history limitation is necessary.

Integrate this review with the owner-census appendix at the exact source and
proof pins above. Finite or bounded test success alone does not establish the
separate analytic join or remove any selected premise.
