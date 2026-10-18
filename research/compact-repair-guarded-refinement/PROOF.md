# Guarded Compact repair refinement

This is a partial-correctness theorem for the extraction, radix passes and
reinsertion in PR2250 `compact.repair`. It supplies one part of the explicit
sequential-repair handoff in PR2378, not its entire `CompletedPrimitive` premise.
The checked code is [Repair.lean](Repair.lean), using Lean 4.34.1 and `Std` only.

## Exact statement

Let `qs` be any finite list of natural-number addresses and let the payload
type `α` be arbitrary. The payload `input q` may depend on every address bit,
including all dirty fields. Let `s`, `sinv`, `t`, `tinv` be address functions,
and `badAt` a Boolean predicate. Assume:

1. `s (sinv q) = q` for every q;
2. `tinv (t q) = q` for every q;
3. `badAt (s q) = badAt q` for every q;
4. `s q = t q` whenever `badAt q = false`.

The raw stream at q is `input (sinv q)`. Extract exceptional records as whole
pairs `(t (sinv q), input (sinv q))`, preserving the order in `qs`. Put the other
payloads, in order, into the good stream. Apply any finite sequence of stable
binary radix passes to the exceptional **whole pairs**. Scan `qs`: at a bad
address require the next exceptional key to equal that address and emit its
payload; at a good address emit the next good payload. Reject missing records,
wrong exceptional keys, or either stream remaining at the end.

**If this scan returns `some out`, then `out = qs.map (input ∘ tinv)`.**
This is `guarded_compact_repair`. The theorem is uniform in `qs`, payload type,
all four functions and the radix-bit functions. No probabilistic or clean-data
assumption occurs. It is conditional on the four displayed laws and actual
successful completion `hcomplete`.

The addresses in the actual program are a complete finite interval. The Lean
statement uses natural-number functions for convenience. A finite-domain
instance can extend the two permutations by identity and the predicate
consistently outside the interval; the displayed global premises then follow
from their finite versions. This extension is not a claim that arbitrary
Python address operations are defined outside their layout.

## Proof structure

`Valid target records` means each pair's value equals `target` at its key.
`fill_correct` proves by induction on `qs` that a valid exceptional stream and
the correct ordered good stream imply the target output whenever `fill`
succeeds. A bad position consumes a matching key, so validity supplies the
right value. A good position consumes the head of the given good stream. At
the empty list, successful completion requires both streams to be empty.

Each `radixPass` concatenates the stable zero-bit and one-bit filters of whole
pairs. `List.filter_append_perm` proves that this is a permutation, and
`radix_perm` composes that fact. `valid_perm` therefore retains the key/value
invariant. This is a **pair-preservation theorem**, not a sorted-order theorem.
No theorem here proves that the radix schedule will make the guard succeed.

For the exceptional records, the key is `t (sinv q)` and the target is
`input ∘ tinv`; hypothesis 2 gives

```
input (sinv q) = input (tinv (t (sinv q))).
```

For a good q, hypotheses 1 and 3 show that `sinv q` is also good. Hypothesis 4
then gives `t (sinv q) = q`, and hypothesis 2 gives `sinv q = tinv q`.
This is `good_inverse_agreement`. The two stream invariants combined with
`fill_correct` prove the result. `guarded_repair` exposes just the already
derived good-inverse agreement when that smaller contract is convenient.

## Binding to the immutable source

PR2250 is pinned at `d404b48a1e7b147556b309497d55089c837dddb2`.
PR2378's handoff is pinned at `5816f94741709e8082e06a2cc9a114ff87411f3d`.
Exact blobs and SHA256 values are in [VENDOR.json](VENDOR.json).

| Source operation | Formal model and remaining interpretation |
|---|---|
| `word.execute(state, layout, True)` | `sinv`; inverse law is a premise, checked on both finite fixtures |
| `word.ideal(old)` | `t`; `tinv=t` for the source toggle, checked on both fixtures |
| `bad.write(bit_key(destination)); copy(source,bad,record_bits)` | `extract` preserves key and arbitrary payload together |
| `stable_radix` in `streams.py` | `radix` and `radixPass`; finite model uses the actual increasing low-bit schedule |
| `holes.read(1)`, `destination==index`, `copy(...)` | `fill`, using the predicate at the scan address |
| `finish()` on bad, good, holes | `fill` rejects leftover data; holes have exactly one entry per address by construction |
| scratch erasure and tape heads | observed in finite source execution, not covered by the Lean list theorem |

The interpretation is reviewed and tested, not a formally verified Python
importer. The Python replay authenticates copied source before executing it.
It gives every address a distinct full-width binary payload, compares the
formal-style list model and unchanged source repair, and also checks the full
source primitive and its second invocation on complete rectangles. Those
finite payload fixtures do not enumerate every possible array.

## Explicit limits and next obligation

The theorem neither proves the raw Compact laws for all parameters nor
proves total successful completion, sortedness, tape semantics, scratch bounds
or runtime. It does not formalize the final highest-bit digit permutation;
that step is checked only in the finite full-primitive replay. It does not
import PR2378's older Mathlib environment or discharge its full completed
primitive contract. The mathematical model is kernel checked; the external
binding to source and the compiler/standard-library trust boundary remain.

To close total repair correctness, prove the actual finite raw inverse and
bad-set laws, the exact key multiset of the holes, and sortedness for the full
address-bit radix schedule. Then establish tape/list refinement including
stream exhaustion and restoration. None of these obligations is treated as
zero cost or as implicit evidence for a complete supplier.
