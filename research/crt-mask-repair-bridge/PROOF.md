# Scanner-owned CRT mask consumption / disposal contract

Scope: one repaired switch layer of Cinna Davis's #4100 `CRT.md` §4, one target. The narrow
addition is consumption of the actual #4208/#4201 scanner-owned mask by marker-driven repair,
with disposal/head-return gates. Correctness below instantiates the inherited #2250/#4328
repair argument under an explicit key premise; it is not a new repair algorithm or endpoint.
It neither executes key arithmetic on tapes nor closes the full caller or its asymptotic cost.

## Setting

Address space `A = {0,1}^L`, `L = 12`, `x = (u:2, t:2, y:8)`, MSB first. `S` is the literal
compact macro (ten shears), `T` the ideal controlled switch `y -> y xor (f(y) << j)`,
`good` the #4100 predicate (digits `u,t != 3`, the `K-1 = 5` bits above target `j` lie in
`[8,24)`). Facts used from predecessors (not re-proved here):

* (F1) `S` and `T` are bijections of `A` preserving `good`, and `S = T` on `good`
  (#4100 `check_compact_crt.py`; universal argument #4169 PROOF.md for a source `f` omitting
  its targets).
* (F2) `S^-1` is computed at the CURRENT `y` by running the ten shears in reverse with negated
  offsets (#4169). Hence `T o S^-1` is computable at one address without a table.
* (F3) The unchanged #4201 scanner outputs `mask[q] = 1` iff `q` is bad, from the stencil
  produced by the unchanged #4208 producer, with exact invoices
  `T_prod = 33H+25K+38Y-6G-J+12B+335` and `T_scan = 8ML+15M+13L+18`.
* (F4) Extraction, full-key stable two-bucket radix reinsertion and erasure are inherited
  from #2250/#4328; #4328 supplies the CRT tariff, not a new result of this package.

## Prior physical repair and the distinct boundary

Jose Manuel's #3055 at `9dc841c9a101435fdd15e0f7623bf16b6d0363e9`,
`research/physical-complex-compact/PROOF.md` §§4–6 and `compact_streams.py`, already implements
encoded current-inverse destination keys, physical hole flags, stable two-bucket radix
repair, hole-key equality checks and disposal. His #3608 at
`c6020096322012f7cc41236c3ac15a6b6cd3f8b9`, `research/physical-sparse-xor-batch/PROOF.md`
and `sparse_engine.py`, implements encoded variable-pair control and reuses that repair
with owned-work return. These are physical-repair prior art, not merely host-array sketches.
Their resource arguments use long actual records to absorb polynomial control work;
they do not supply consumption of the CRT #4208/#4201 scanner-owned mask at `R = Θ(p)`.
See [README's exact-head comparison](README.md#exact-head-comparison-and-retained-credit)
for source links. This package claims that mask-consumption/disposal interface only, not
first physical repair, a new algorithm, a new endpoint or a new asymptotic tariff.

Let `raw` be the stream after the macro: `raw[S(x)] = payload(x)`. Goal: `final[T(x)] = payload(x)`.

## Contract of `bridge.repair`

Tapes (fixed roles): `stencil, mask, counter, data, good, bad, b0, b1`. Inputs: `stencil` and
`mask` are the producer/scanner's own output tapes, `data` holds `raw` as `LEFT, (R,v)^M, END`,
`counter, good, bad, b0, b1` are physically blank (`LEFT` then `BLANK`). Key premise
(K): `key_function(addr)` returns `T(S^-1(addr))` as `L` bits for every `addr`.

Postcondition: `data = final` (same length); `mask, stencil, counter, good, bad, b0, b1` are
physically blank apart from permanent `LEFT`; all heads at `LEFT`; the key function was
called once per marked address and on no other.

## Proof

**Counter.** `init_counter` writes `0^L END` (one `0` per stencil atom, so `L` is carried by the
stencil, never by a host integer). `advance` runs to `END` and applies the scanner's own
carry; it returns "wrapped" exactly after `2^L` increments, and the program raises if
"wrapped" disagrees with the mask `END`. So at the k-th loop iteration the counter spells
`k` (MSB first) and the mask cell read is `mask[k]` (mask and address space have equal length).

**Split.** For `k` with `mask[k]=0` the record of `data[k]` is appended to `good` and no key is
read. For `mask[k]=1` the record and then `key_function(k)` (the address read off the counter
cells) are appended to `bad` as a block `R, key^L`. No other path touches `key_function`.
Hence `good` is the subsequence of `raw` at good addresses, `bad` the blocks at bad addresses
in address order, each carrying `key_k = T(S^-1(k))`.

**Keys permute the holes.** By (F1), `S^-1` and `T` both preserve bad = complement of good, so
`k -> key_k` is a bijection of the bad set onto itself (also: `raw[k]` is the payload whose
ideal destination is `key_k`, because `payload(x)` sits at `S(x)` and `x = S^-1(k)`).

**Radix.** One pass moves each block, stable, to `b0` or `b1` by the LAST key bit, rotating that
bit to the front of the key, then concatenates `b0 b1` into `bad`. After pass `i` the blocks are
stably ordered by original bits `b_0..b_{i-1}` (LSB first) and the key is the rotation of the
original by `i` places. This is the textbook LSD argument with the dropped bit re-attached.
After `L` passes the keys have their original orientation and the blocks are ordered by the full
key, with all keys distinct (keys are a permutation of the holes). The stencil is the pass
counter (`L` atoms), not a host integer.

**Reinsertion.** The `r`-th smallest key is the `r`-th smallest bad address (the keys are
exactly the bad set). Walking addresses in order with the counter, a bad address takes the next
sorted block and the program compares its key bits with the counter bits, raising on any
difference; a good address takes the next `good` record. Thus `final[k] = payload(x)` where
`T(x) = k` for bad `k` (the block whose key is `k`), and for good `k` the record
`raw[k] = payload(S^-1(k))` with `T(S^-1 k) = k` by (F1) (`S = T` on good and `S^-1(k)` good).
Both streams end together or the program raises. So `final = T`-image of the payloads. QED.

The reinsertion key check is necessary but NOT sufficient for correct keys: any bijection of
the holes passes it (`ideal_of_current`, `inverse_only`, `stale_source`, `guarded_identity`
keys all pass or fail it without the payloads being right). Correctness of the repair therefore
rests on premise (K); the verifier exercises these four wrong keys, counting a mode as detected only where it changes
some hole key (equivalent fixtures are recorded as such).

**Ownership/erasure.** `erase` reads to `END`, blanks every cell including the allocated `END`,
and rewinds. `repair` ends by erasing `mask` (consumed), `stencil` (consumed), `good`, `bad`,
`counter`, and each pass erases `b0, b1`. Each role is then physically `LEFT, BLANK*`, so the
private roles can be reused by a later producer/scanner/repair invocation; the verifier asserts
blankness before every reuse. `data` is overwritten in place cell by cell (no extra length).
This local postcondition does not imply an uninterrupted all-tape inter-layer data handoff.

**What a skipped clear costs.** Marker-driven reads stop at `END`, so stale cells beyond a
rewritten marker are not read by the next layer; skipping a clear is therefore a *state/
ownership* defect that does not change that layer's output, and it is caught by the physical
blank gate, not by the payload comparison. The verifier states this and detects it by the gate.

## Cost (explicit model)

One action = one read, write, or one-cell move of the finite-alphabet cell/head model; a record
cell additionally counts `R = 12` bit-widths in the observer bit meter. With `M = 2^L`, `N` holes:

* producer `T_prod` and scanner `T_scan` exactly as in (F3), unchanged;
* init `O(L)`; split `O(M L + N L)` (counter advance and address read are `O(L)` each) plus
  `N` key-call interfaces of `O(L)` actions each;
* sort: `L` passes, each `O(N L)` actions (each block is scanned, its last key bit fetched and
  the block rewritten), i.e. `O(N L^2)`; erase of buckets `O(N L)` per pass;
* reinsertion `O(M L + N L)`; final erasure `O(M + N (L+1) + L)`.

The verifier reports exact observed counts per phase and per invocation. Key ARITHMETIC
(the host `key_function` body: ten shears, a Beneš table lookup and an ideal switch) is not
charged and is not on tapes; only the address-read/key-write interface actions are charged.
CRT.md's `E(p,ell)` and #4377's counting proof remain a conditional allowance, not payment
for the executed host callback. No #4377 tape evaluator is plugged in here. The displayed
local repair accounting does not establish a new `O(V)` tariff for this implementation.

## Limits

* Macro `S`, the raw stream and ideal-layout oracles, and the inter-layer payload handoff
  are host-built. Within each repaired-layer invocation, producer/scanner and the remaining
  repair actions are tape programs, with the host key callback explicitly excluded.
* The geometry is the unary one-target family of #4208 with the fixed `u2,t2,y8`; many-target
  ordering and binary/transported geometry are not covered.
* `key_function` is not a tape program (stated above). The AST guardrail is a review aid.
* The existing #4169 ten-layer fixture already supplies the 4096-payload / 29,440-hole
  forward/inverse endpoint and current-state inverse keys. Here it is **ten separate repaired-layer
  invocations**, not an uninterrupted all-tape caller: host code extracts each output and
  populates the next raw data tape, despite reuse of blank private roles.
* These finite invocations exercise the interface; the algebraic statement is the inherited
  repair argument above for every `(L, f)` satisfying (F1)-(F3) and (K), not a universal
  tape-evaluator, full-construction or multiplication theorem. Outcome remains `partial`.
