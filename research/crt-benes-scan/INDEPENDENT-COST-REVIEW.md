# Independent cost review: retained Beneš compiler

Reviewer: OpenAI Codex, acting independently of the primary implementation.
Source credit: Cinna Davis's retained `research/unconditional-batched-crt/CRT.md`
full-scan simulation argument and `check_batched_crt.py::benes` at canonical
main `12fa8c5c844be21bfefb38a19503fbd867a11244`.

This is an audit of a conditional numerical compiler/query interface. It is
not a numerical CRT evaluator, payload permutation implementation, production
placement certificate, native/outer theorem, or independent human review.
Finite Python results are not an asymptotic cost proof.

## A constructive uniform simulation bound

Let `n=2^h`, `1<=h<=ell<=p`, and `B=p+2`. Input is a fixed-width encoded list of
exactly `n` integers, each with `O(B)` bits, together with encoded parameters.
An implementation validates that the list is a permutation of `[0,n)`. The
cost bound is for this bounded encoding; an unbounded malformed byte stream
is not silently included in the same input-size claim.

A single finite-alphabet multitape machine can implement the following
simulation, with a tape count independent of `p`, `ell`, and recursion depth.

1. Store every recursive node in one flattened work region. Reserve each
   node's permutation, inverse, color vector, explicit pending-vertex stack,
   child vectors, result layers, and a constant number of frame descriptors.
   A complete binary tree determines the capacities from `h`; it is not a
   separately supplied circuit or per-size advice. At depth `d`, the total
   wire count is `n`. Keeping each node's complete result costs
   `O(n(h-d))` entries at that depth. Thus all levels need `O(n B^2)`
   fixed-width slots, including conservative descriptor and temporary space.
   Each slot, including its address/type encoding, needs `O(B)` bits, so a
   work region of `W=O(n B^3)` bits suffices. This also accommodates the
   `O(log W)=O(B)`-bit global slot addresses.
2. Implement host recursion as a depth-first state machine whose pending
   node, child phase, indices, and saved loop state live in those descriptors.
   Push/pop and table copies are ordinary encoded reads/writes. No new tape
   appears at a child call, and recursion/garbage collection is not free.
3. Avoid assuming a unit-cost `sorted`. At each node, range-check every image
   and compare every pair for duplication. For a node of size `m`, this is
   `O(m^2)` word actions. Across all nodes,
   `sum_d 2^d(n/2^d)^2 < 2n^2`. The coloring loop pushes a vertex only once,
   processes two incident edges when it pops it, and therefore takes `O(m)`
   word actions, apart from validation. Building child vectors is `O(m)`.
   The output has `2 log2(m)-1` tables of length `m`; merging child tables
   therefore uses `O(m log m)` word actions. Across all nodes the latter is
   `O(n h^2)`. A bound of `O(n^2 B^3)` elementary register/array actions is
   ample for all loop management, encoded-address calculations and copies.
   This loose allowance is not a measured finite-fixture count.
4. Replace each indexed array access by a complete sequential traversal of
   the work region, plus return to its marked beginning. Decode/compare a
   fixed-width slot address and increment the scan counter using at most
   `O(B^2)` bit steps per visited encoded bit, an intentionally loose bound.
   Keep the target address and read/write word on fixed scratch tapes. Thus
   every abstract access, including descriptor access and stack access,
   costs at most `O(W B^2)=O(n B^5)` bit steps. Any schoolbook arithmetic on
   the `O(B)`-bit registers also fits this allowance. Sequential scan/return
   moves every physical head; a symbolic reset or free random access is not
   used.
5. Query a table by the same scans. A requested switch lookup or following
   all `2h-1` layers adds at most `O(B)` such accesses, after reading/validating
   its encoded query arguments. Direct and inverse address-map evaluation
   can compile the inverse permutation as another bounded invocation or
   follow the involutive layers in reverse. Copy any promised output to
   its owned output region, then erase the work region and return all heads.
   Allocation, output copying and cleanup are bounded by the same costs.

The resulting conservative compiler-plus-query time is

```
O(n^2 B^3) * O(n B^5) = O(n^3 B^8),
```

and workspace is `O(n B^3)` bits, in addition to the promised input and owned
output. Since `n<=2^ell`, this is below a fixed multiple of
`2^(4 ell)(p+2)^16`. Up to `O(p)` separately compiled axis controls still cost
`O(2^(3 ell) B^9)` and fit the same generous envelope. Reuse the work region
between those invocations. This latter statement does not supply their
numerical offsets or prove the full CRT arithmetic routine's bound.

## Pitfalls the primary proof must exclude

- Array length and table entries are encoded bits, not unit-cost Python
  integers, tuples or arbitrary record labels.
- `sorted`, dynamic allocation, tuple comprehensions, recursive calls and
  list indexing need the explicit lowering above or another paid lowering.
- `run_network` table queries must pay for the current encoded address and
  return heads after each scan; table lookup is not an oracle.
- Validation, inverse construction, DFS initialization, copying result layers,
  reading input parameters, allocation, erasure and head returns must be
  covered. Output preservation/ownership must be stated explicitly.
- Invalid-permutation rejection is part of the numerical compiler. Correct
  network behavior on all padded record labels is a different finite semantic
  property. Neither result proves that a source guard or target placement is
  production-valid.
- Any query/compilation certificate must say which executable source bytes it
  authenticates. Finite counts are evidence of that implementation's behavior;
  they do not quantify the asymptotic simulation constant.

Conclusion: no obstruction was found to a uniform finite-alphabet sequential
simulation inside the retained generous envelope. The explicit construction
above supplies a conditional bound for this compiler/query component. Its
mechanism is the predecessor's full-scan argument, not a new routing method.

## Review of the submitted tagged-arena construction

I separately read the submitted `verify.py`, `PROOF.md`, `README.md` and
`RESULT.json`. Its more specific all-node record census is
`J=N(h^2+3h+1)`, with five fields of width `w=4p+8` per record. The three
per-node arrays contribute `3Nh`, all result layers contribute `Nh^2`,
and the shared explicit DFS stack contributes `N` records. The stated
`B=5wJ` arena length, field widths and global-offset bound are sufficient.
Constant-depth nested loops need a fixed number of scalar roles, not a
host recursion stack. Candidate/supplied key buffers, all loop counters,
parameters, values and arithmetic temporaries fit the stated fixed bank.

Independently counting the modeled operations gives:

- One arena access: `(14J+1)w` arena actions and `(12J+24)w` key-tape
  actions, summing to `(26J+25)w`.
- Arena initialization and complete erase/return: `6B` actions.
- Modeled protected permutation reading/return: `3Nh`; serialized network
  writing/return: `3(2h-1)N`.
- One complete network query, owned bit and returns: `3(2h-1)N+3`.
- Pairwise-validation comparisons: `N^2-N-Nh/2`, plus `Nh` first reads.
- Nonleaf construction: `20N(h-1)` arena accesses. This counts `11m`
  coloring/stack accesses, `2m` inverse accesses, and `7m` first/last/child
  accesses at a node of size `m`; component-start and discovery counts
  cancel their dependence on the number of connected components.
- Leaves: `3N/2`; bottom-up merging: `2N(h-1)^2`; root loading and output
  serialization together: `2Nh`.

These sum exactly to the implementation gate
`A=N^2+2Nh^2+(37Nh-35N)/2`, independently of the finite fixture receipts.
Its bound `O((A+J+1)B(p+2)^2)=O(N^3(p+2)^7)` is a valid conservative
written lowering. The more general bound above is deliberately looser.
Both fit the retained generous envelope, including at most `O(p)` repeated
component invocations.

The final interface explicitly bounds canonical parameter encodings and
fixed-width query fields; arbitrary leading-zero streams are excluded.
Header decoding, host pre-admission length/format checks and bounded scalar
microcode are paid by the written lowering. They are not claimed as
executed tape-transition evidence. The modeled query now checks every
network byte for binary format. Successful calls preserve protected inputs,
serialize their owned output before clearing private work, and return heads.
Owned queried-bit and compiler-output tapes are fixed reusable physical
roles; retaining many answers requires separately paid transfer/storage.

I found no material correctness, encoding, cost or output-ownership defect
in this component after those clarifications. Normal and optimized Python
replays are recorded in the accompanying portable receipt. They corroborate
the explicit arena implementation; the asymptotic argument is the written
construction, not an inference from their operation totals. No literal
finite-state transition table or proof-assistant verification is supplied.
