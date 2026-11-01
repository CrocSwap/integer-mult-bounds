# Independent preimplementation Beneš review

Source context: canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`,
priority revision 7, Cinna Davis PR4100 source
`337d04939571a637aeab54a0f58f54fde811663a`, `CRT.md` Sections 2--4 and
the retained `check_batched_crt.py` Beneš routine. No primary candidate
implementation was read before this review and its separate oracle.

## Quantified sufficient bounds

Let N=2^h, 1<=h<=ell<=p. Values, array offsets, node identifiers and loop
counters use O(p+2)-bit encoded words, choosing their fixed constant after
the arena format is fixed. A number of tapes independent of p,h suffices.

Retain the complete recursion tree in one encoded arena. There are N-1
nodes with widths at least two. (Allowing explicit singleton leaves gives
at most 2N-1.) At depth a, the node widths sum to N. Each node of width n
has 2log2(n)-1 complete n-entry Boolean control tables. Therefore retaining
all node control tables uses exactly

    sum_(a=0)^(h-1) N[2(h-a)-1] = N h^2

Boolean entries. Permutations, inverses, colors and component stacks add
O(Nh) encoded words. Node/frame descriptors add O(Nh) words even with a
generous encoding. Thus fixed-width storage is

    S = O(N(h+1)^2(p+2)) <= O(N(p+2)^3) bits.

Use an explicit serialized continuation/frame stack, or top-down node
generation followed by bottom-up merging. A host language call stack is
not evidence for a fixed inventory of sequential tapes.

At a width-n node, range/distinctness validation can use O(n^2) pairwise
comparisons, replacing the uncharged host `sorted` call. Summing these
comparisons over all nodes gives less than 2N^2. The two-colored graph is
the union of two fixed-point-free involutions, x<->x XOR 1 and
x<->pi^-1(pi(x) XOR 1), hence a union of even alternating cycles. Each
vertex is colored/pushed once. Coloring, inverse creation and child
construction total O(Nh) logical word operations; table assembly totals
O(Nh^2). A sufficient overall logical bound is

    Q = O(N^2 + N(h+1)^2).

Full sequential scans replace every indexed arena access. Bound a scan,
position bookkeeping, arithmetic, clearing and return conservatively by
O(S(p+2)^2) per logical operation. Taking the much looser source envelope
Q<=O(N^2(p+2)^6) therefore gives

    T <= O(N^3(p+2)^11) <= O(2^(3ell)(p+2)^11).

Initialization, finite header markers and final arena clearing/head returns
are O(S(p+2)^2), inside this envelope. A stored control query can scan the
root table, and is also within this bound. There is ample slack under the
source's 2^(4ell)(p+2)^16 expression, but this proves only the isolated
compiler/query implication. It does not certify all source axis controls,
CRT reconstruction, modular inverses, macro inversion or full E evaluator.

## Checks a literal simulator must expose

- Arena/stack capacities must be independent of host object allocation;
  indexes and graph work are encoded on a fixed tape inventory.
- Every indexed read/write, pop/push, validation operation and return is
  charged. Host list/dict accesses can implement a semantic oracle, not an
  uncharged tape primitive. Host integer arithmetic is not constant time.
- Output controls omit their own target bit. The universal bit schedule
  is 0,1,...,h-1,...,1,0. Reversing complete layers implements the inverse.
- If a compiler returns a network, it must copy/protect owned output before
  clearing the private arena. If it returns one query bit, all private
  structures may be cleared while preserving that bit. A returned host
  network must not hide uncharged output storage or head returns.
- A conceptual full-arena scan tariff is distinct from an actually
  executed cell/head model. Counts from a Python host trace must not be
  described as literal sequential steps unless each scan is performed.

## Separate finite semantic oracle

`independent_benes_oracle.py` uses FIFO component coloring, explicit
top-down nodes and bottom-up table assembly. It was written before reading
the primary candidate. It is a semantic oracle using host queues/arrays,
not a tape-cost implementation.

Ordinary replay passed all permutations at N=2,4,8 and 16 deterministic
shuffles each at N=16,32,64: 40,394 permutations, 324,452 endpoint columns,
1,630,756 control columns. Every control omits its target, all endpoints
equal their supplied permutations, and reverse layers invert them.
Swapping child-selector parity fails at permutation (0,2,1,3), input 0,
with wrong output 3 instead of 0. This guards against silent child-port
orientation errors.

## Scope and credit

Cinna Davis supplies the audited source compiler and proposed full bound;
the retained NOTICE preserves the Beneš/CRT and routing lineage. This is
separate-agent OpenAI Codex review, not independent human review or a
formal-kernel proof. No new kappa or selected-frontier change is asserted.

Remaining obligations: authenticate the actual simulator and its complete
operation/arena trace, then separately bind every other component of the
full uniform E evaluator and its production caller.
