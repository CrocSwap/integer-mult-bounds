# Sharp live payload/key storage for the selected BIT owner route

This closes one storage component of Jose Manuel's pending [PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697), pinned at `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. Its complete first-node caller leaves route temporaries as `O_q(v)+O(V/W)` and total numerical reserve open. Here the unchanged `route_packet` has an exact live-content peak, including its borrowed input:

```text
w > 1:  2v + 3H(R+J)
w = 1:  2v + 2HR + HJ
```

These are proved for the source routine's well-formed successful runs. Eight complete small fixtures attain the formulas when executing that same routine. This is a component certificate and a scoped caller corollary. It does not establish a total reserve, admit a supplier or change kappa.

Coordination: [Discussion2319 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18954841). Base main `b5ea56e0a5ac4552166253b1fa4be0753bb38c30`, priority revision 5. The selected record remains unchanged.

## Contract and counted storage

Let q be an odd prime, d the fixed matrix dimension, w a positive payload precision, and `cap=q^(w-1)`. Set

```text
H = cap^(d*d)                complete high matrices per old prefix
C >= 1                      physical old-prefix count, repetitions retained
R >= 1                      payload symbols in one high-matrix fibre
t = HR                      one complete high cube
v = CHR                     one packet
J = d*d*(ell+1)              serialized route key
```

Here ell is the actual residue arena's fixed binary word length, including its supplied padding. Each of the d*d key words contributes ell binary symbols and one WORD_END delimiter. No minimal encoding assumption is needed. The compiled route must act bijectively on the complete high cube and satisfy the retained source context/word-margin contracts. Every factory invocation creates a fresh, distinct, initially empty tape. The input is exactly v contiguous binary payload symbols and is retained unchanged.

The count is the number of simultaneously nonblank payload and embedded-key symbols on route tapes, excluding each tape's LEFT marker. Cleared symbols cease to contribute even if the Python bytearray remains allocated. Numerical arena words, counters, context, fixed compilation, tape markers, provenance dictionaries and other Python heap capacity are excluded. This is deliberately narrower than occupied tape volume or process memory. The source's exact abstract tape semantics and ordinary ownership discipline are premises.

## Lifetime proof

Write `K=H(R+J)=t+HJ` for one decorated cube. Its content has a fixed length independent of key values, bucket balance, route chart or input bits.

In `partition`, the current decorated cube retains K symbols. During bucket filling, the two buckets have combined content at most K; the separate key scratch has at most J symbols and the following output is empty. Thus the total is at most `2K+J <= 3K`, since H and R are positive. During bucket concatenation the key scratch has been cleared, while the buckets, current input and growing following output contribute at most 3K. At the final appended output symbol they contribute exactly 3K. The buckets are only cleared in `partition`'s finally block. Clearing current occurs later in `route_cube`, after partition returns.

During decoration, `route_cube` has at most K decorated symbols, plus numerical scratch excluded above. During key stripping it retains the decorated input and grows a pure output of size at most t, giving at most `K+t <= 3K`. A partition therefore determines its sharp internal peak when cap>1. There is at least one partition because d>=1, ell>=2 and cap>1. If cap=1 there are no partitions, H=1, and the sharp internal peak is K+t at completion of key stripping.

For old prefix p, numbered 0 through C-1, `route_packet` retains its original v-symbol input, the already completed outer output of length pt, and a separate local cube of length t while `route_cube` runs. Consequently for cap>1 its peak is

```text
v + pt + t + 3K <= 2v + 3K.
```

Equality occurs in the final partition of the final old prefix, before any bucket or current cleanup. The copy from the returned pure cube into the outer output has at most `v+pt+3t <= 2v+2t`, below that peak. For cap=1, replace 3K by K+t and obtain `2v+K+t = 2v+2t+HJ`, attained at the final prefix's key-stripping completion. The final result and borrowed source each have size v; all other counted content is cleared.

This proves both universal equalities for the fixed routine, rather than a lower bound for every possible routing algorithm. Different disposal timing or a different route can change the result.

## Consequence for the caller's gather/route/return/scatter phases

In PR2697, let N be the number of low GL classes, W the number of family streams, `V=WNv`, and r the number of staged roles. Its stated selected values are W=28416 and r=661. Treat these as the caller's authenticated geometry; this package does not replay the full selected catalogue or node.

When the last role is gathered and routed, r-1 completed packets remain alongside the route input. During inverse routing, all r staged packets remain, but one is already included in the route's borrowed-input charge. Thus both phases are bounded by

```text
(r+1)v + 3H(R+J).
```

Scatter has a different overlap. All r staged packets and the returned packet of size v survive while `selection.scatter` builds a replacement whole family of size Nv. The old family is already counted among the W live families and is cleared only after scatter returns. Hence gather, routing, return and scatter, apart from the retained source/peeled/family streams, are bounded by

```text
(r+1)v + max(Nv, 3H(R+J)).
```

`Node.run` retains at most 3V in protected input, peeled output and live family streams during those phases. Final merge can add a full V before cleanup. A joint bound for these phases and final merge is therefore

```text
max(4V, 3V + 662v + max(Nv, 3H(R+J))).
```

This excludes literal local-word execution, COPY, residual/primitive interiors, peel interiors, directory production, counters and numerical/control storage. In particular COPY can briefly retain 661 roles, a cloned input and a returned private packet, 663v before residual-internal work. The displayed phase bound must not be applied to that interval. No historical `5V+19v` reserve or complete-node allocation is imported.

## Replay and evidence

Use Python 3.12 with only the standard library:

```sh
python3.12 scripts/research_package.py --package research/selected-route-live-volume --check-only
python3.12 scripts/research_package.py --package research/selected-route-live-volume
python3.12 -I -O -B research/selected-route-live-volume/verify.py
```

`SNAPSHOTS.json` records exact PR2697 paths, Git blobs and SHA256 hashes. The verifier checks all 16 snapshots before importing any retained code. Twelve required runtime modules are retained byte-for-byte, together with the caller proof, driver, node and attribution notice. These runtime bytes came through PR2569; their inherited notices and dependencies are preserved. The new checker changes no source file or route operation. It supplies a measuring Tape factory and temporarily replaces only the route's private key-tape constructor.

The eight fixtures use q=3 or 5, d=1 or 2, w=1 through 3, C=1 through 3 and R=1 through 5. Each exercises the complete declared high cube, up to 625 matrices. The 1,298 Boolean positions carry independent origin labels through actual copy operations. A separate integer modular-multiplication oracle checks every output origin and bit. Both partitioned and nonpartitioned cases attain the proof's exact peak. A direct scan of every retained measuring tape independently counts the first attained peak, and the exit census checks source preservation, head reset and cleared temporaries.

Seventeen behavioral checks reject input/output-only budgets and premature current/bucket disposal budgets for all eight fixtures, then exercise a nonbinary payload failure with preserved borrowed input and erased owned payload buffers. Seven integrity groups cover a Git-free optimized replay, corrupt route/record/driver snapshots, a bool-for-integer receipt mutation, overwrite refusal and internal-output refusal. The receipt is checked with exact type-sensitive JSON comparison. To regenerate, use `--write-result` with a new path outside the package and compare it with RESULT.json.

Validation passed on macOS arm64 with CPython 3.12.15 through the registered launcher and its seven integrity groups, and on CPython 3.14.8 with optimized assertions disabled and warnings treated as errors. The six repository replay-selection tests passed. Separate internal proof/source review also passed the optimized replay, integrity checks and exact source comparisons; no independent human review is claimed.

The general theorem is the written lifetime proof. The tests are finite implementation evidence, including arbitrary Boolean origins on small cubes. They do not execute the enormous selected GL64 domain or prove the inherited native/compiler semantics. ValueError cleanup is checked for contiguous tapes without internal BLANK holes. Arbitrary exception cleanup and numerical scratch cleanup on malformed inputs are not claimed.

## Verification design and deviations

Build the Lever led to a retained-source replay and literal write counter instead of a hand-counted receipt. Prove It Works led to exact permutation/origin checks and an independent peak census on the actual route. No production code is changed.

Power of Ten inspection covers the new verifier, tracker and integrity command. There is no recursion. New fixture execution is fixed at eight contexts with at most 625 high matrices, 3 prefixes and 5 fibre symbols. The receipt comparator stops after 20,000 nodes; integrity subprocesses have 90-second timeouts; registered commands have finite 120-second timeouts. New functions remain below 60 physical lines. Executable contracts remain enabled under -O. Syntax validation and warning-as-error replays are run; no separate static type checker or linter is installed.

Rule 3, memory allocation: Python and the retained tape interpreter allocate during execution. Scope is this finite offline verifier. The fixed fixture list bounds all tapes, keys and origin dictionaries; the tracker retains cleared tapes for the independent census, so its own memory must never be used as the theorem's storage measure. Each successful fixture closes its arena and clears source/result. Follow-up if extending the domains is to calculate a new allocation cap before changing the fixed fixtures.

Rules 8/9, instrumentation: the inherited factory interface and one temporary routes.Tape replacement provide two explicit measuring-constructor targets. The context manager restores the original target on every exit. This is checker-only instrumentation, with bounded targets and no dynamic code evaluation. Follow-up for production use would be an explicit upstream observer interface, outside this component's scope.

Frozen predecessor code retains tape-terminated loops, dynamic Python allocation and methods exceeding one page. Rewriting them would destroy the byte-exact subject of this audit. Their execution is bounded here by the finite complete cubes, fixed word lengths and registered timeouts; no repository-wide Power of Ten compliance is asserted.

## Open next questions

1. What explicit reserve covers the residual and primitive interiors alongside this caller phase bound? Start with one PR2697 residual ENTER/RETURN, retaining its input, output and the 661 role buffers. Missing lifetime bounds for its directories, counts, coefficient pages and leaf work still block total reserve admission.
2. Can early bucket disposal or avoiding a local cube reduce this routine's peak without changing its complete-fibre semantics? First propose a changed literal ownership schedule and check it against the same origin and peak tests. This is an optimization opportunity, not needed to retain the present audit. A new route requires its own proof and source pin.

## Credit and scope history

Nick Petalas prepared this component audit. Jose Manuel/jmbarrancoml supplied PR2697's first-node caller and PR2569's source packets, routes and selected lineage. ywz65 supplied PR2590's cubic setup correction and PR2688's separate directory-storage component. The retained NOTICE.md credits the stream and tape framework, Douglas Colkitt, the selected hosting/word contributors and the source527/compiler lineage. Their construction and code are not claimed as new here. New work follows the repository's Apache-2.0 license.

This follows the live total-live-volume handoff rather than the task picker's initial complex-mechanism suggestions. TASK.json declares a changed scope from the selected-stock-envelope card's complete stage recurrence to one actual pending caller component. PR2688 handles a different component. No family expansion, formal-kernel or independent human verification, full supplier replay, selected cold replay or new exponent is claimed.
