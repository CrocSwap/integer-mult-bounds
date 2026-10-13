# Two-sided CK compensation: 8,798 real primitives beyond target forests

**Finite complex-supplier circuit construction; no new κ.** On the historical
PR626 CK provider, a signed target forest followed by disjoint signed helper
shears reduces the frame-zero compensation from 8,704 to **2,541 additions**.
The complete local programs save **75,318 real-component primitives each**.
This is **8,798 beyond the 66,520 saving of the target-forest class alone**.

| Complete scalar program | Original | Two-sided | Saving |
|---|---:|---:|---:|
| Forward | 224,938 | 149,620 | 75,318 |
| Inverse transpose | 224,986 | 149,668 | 75,318 |
| Scalar macros, either orientation | 21,936 | 15,773 | 6,163 |

These are exact circuit counts, not elapsed-time measurements. Every source
access, coefficient preparation, target/helper basis change and restoration,
private clear, and unchanged scalar operation is charged. The paid recursive
histogram, all non-scalar events, helper inventory and physical frames are
unchanged. All 492 helpers restore at the complete local endpoint. The positive
prefix bounds rise from 40/62 to **41/65 bits**, within the inherited **192-bit
local allowance**; no unchanged global precision invoice is asserted.
The maximum exact symbolic denominator powers remain **3 forward and 8
backward**, checked at every literal primitive, including transient work.

## Reproduction

From the repository root, with Python 3.10+ and its standard library:

```sh
python3 -I -B research/complex-ck-two-sided/verify.py
```

Expected final line:

```text
PASS_CK_TWO_SIDED target_edges=106 helper_pairs=112 cases=128524 saved_real=75318 additional_vs_target=8798 columns=716+9 orientations=2 controls=10+25 no_new_kappa
```

The default command checks the committed recipe and receipt without rewriting
them. It recomputes the whole search, replays both complete original/candidate
programs with Fraction arithmetic and a separately implemented integer-dyadic
checker, and runs the unchanged native emitter and frame/wrapper auditor in a
temporary directory. `--record` deliberately replaces this package's recipe
and expected receipt only after all mathematical checks pass. The package has
no third-party dependency and works when invoked outside the repository.

`RECIPE.json` specifies all target edges, helper pairs, costs and census hashes.
`EXPECTED.json` binds both literal primitive words, complete scalar counts,
prefix bounds, native paid profiles and control results. The accompanying tests
exercise source/receipt corruption and the separate arithmetic implementation.

## What is new, and what is inherited

David Awad's [PR807](https://github.com/CrocSwap/integer-mult-bounds/pull/807)
changes the CK helper basis alone. @dd-hemant's
[PR816](https://github.com/CrocSwap/integer-mult-bounds/pull/816) changes its target
basis alone, following Sricharan Vagvala's rational target pairs in #749 and
Oscar Fennell's binary target forests in #759. This contribution **reprices and
constructs helper changes after the target transformation**. It does not add
the two earlier independent savings. The row and column mechanisms interact:
the two-sided saving is 75,318, not 66,520 + 35,872.

No pending implementation is imported. The target forest has the same 16,364
component-primitive price as PR816; seed 38 selects a particular tied forest.
The additional evidence is the complete, explicitly restored two-sided circuit
and its literal checks. The separate checker uses a different Prim algorithm
to confirm the target-only floor and independently redoes the helper census.
No joint optimum, best matching, or asymptotic improvement is claimed.

The exact base is **`f567884aeb8851b6e794af1184119a3bfbe1e631`**. At this base the
selected conditional result is PR799, **κ = 0.001661634653669567**. The experiment
intentionally uses the retained PR626 CK checkpoint, pinned to
`660de893d27bb7abd1d5b01b1640207528a5c851`, with PR622 source
`f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`. It does not transport the result to X4.
`SOURCES.json` records exact source digests, the historical SPEC binding, and
pending predecessor heads. Compressed inputs are checked by their decompressed
payloads; their original container digests are retained as provenance only.

## Bounded search and scope

The OS-random track seed is **38**. The search is exhaustive over **12,544**
signed/root target edges and then **128,524** ordered helper-pair/sign choices
on that selected target forest. **1,525** helper choices have positive complete
savings. One deterministic greedy pass selects **112 disjoint pairs**.
SHA-256 of seed 38 and a candidate breaks equal-price ties. All target edges are
priced; Kruskal stops after completing its tree. The helper pass stops after
examining every profitable sorted candidate; all pair scores were computed.
There is no time cutoff or omitted part of this finite domain. The helper-pair space is assessed on the transformed
matrix, so this is not a repeat of the helper-only search with another seed.

The result permits arbitrary data, target and helper inputs, plus arbitrary
private centers and coefficient work on entry. In the forward compensation
panel helpers are restored; in the inverse-transpose panel their prescribed
change is `h <- h - C^T y`. Both complete programs restore their helper inputs.
The private centers and work erase via the inherited charged clears.

Adopting this alternative compensation syntax in the production constructor,
rebinding artifacts, and refreshing the complete global owner/invoice/assembly
remain separate work. The paid child profile and recurrence exponent do not
change. Uniform compilation, common-label/mutable-source realization, whole-call
hosting, precision/tape and analytic transfer remain inherited assumptions.
The scalar projection ignores non-scalar child action; the unchanged native
checker separately validates finite frames, wrappers and child counts. This is
not a proof of the full multiplication theorem or a cold construction replay.

See [PROOF.md](PROOF.md) for the circuit identity and complete price,
[VALIDATION.md](VALIDATION.md) for executed checks, and [NOTICE.md](NOTICE.md)
for attribution and substantial AI-assistance disclosure.
