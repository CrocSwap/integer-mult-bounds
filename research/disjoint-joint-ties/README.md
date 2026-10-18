# Ten further historical complex helper roles saved by root traversal

At h=22, changing the order in which root contraction channels are built
reduces Curtis Dransfield's [PR863](https://github.com/CrocSwap/integer-mult-bounds/pull/863)
disjoint-triple circuit from **30,708 to 30,698 additions**, and its compiled
embedding from **32,248 to 32,238 paid roles**. This is a finite historical
complex-supplier construction, **not a new kappa**. The original retained
circuit has 31,929 additions, so the cumulative saving is 1,231; only ten are new.

Base: `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`. The selected certificate at
this base is PR942's conditional T37 result,
`kappa=1661960547713947/10^18=0.001661960547713947`. Its actual construction
and maintainer review were consulted. The historical supplier studied here
has a saving around 4.38e-9 and is far behind that selected result. No selected
supplier, owner assignment or outer assembly is replaced or composed.

## Reproduce

Standard-library Python 3.10 or later, from the repository root:

```sh
python3 -B research/disjoint-joint-ties/verify.py
```

Expected final line:

```text
PASS_JOINT_ROOT_CONSTRUCTION additions=30708->30698 paid_roles_saved=10 no_new_kappa
```

This rebuilds every field of `CERTIFICATE.json`, independently reconstructs
six nominated circuits, verifies physical frames, and runs nine tests.
`audit.py --write` deliberately regenerates the certificate. The wrapper
runs inherited assertion checks with optimization disabled even when invoked
with `-O` or `PYTHONOPTIMIZE`; its children ignore Python environment flags.
No third-party dependencies, network or pending-PR checkout is needed.

## Bounded search and the evidence-driven pivot

OS-random seed **25** assigned the complex-supplier track. Three candidate
tasks, the claim, overlap findings and stopping rule are recorded in
`SPRINT.json`. No pinned coordination issue was found.

The first experiment completed all **16 subsets** of the four tied balanced
root channels `(0,0),(1,1),(2,2),(3,3)`. The best remained PR863's 30,708.
Changing both nondegenerate ties gives 31,808; that is a completed scoped
negative result, not an impossibility theorem. The extreme channels do not
change the generated DAG in any of the 16 checked recipes.

One bounded pivot then changed the **root output-cardinality traversal**.
All 24 permutations of `j=0,1,2,3` were crossed with the four subsets of
`(1,1),(2,2)`: **96 recipes**, with fixed point order, fixed `i` order,
unchanged descendant plans, balanced summation trees and first-decomposition
support interning. This changes the search class, rather than repeating
PR863's at-most-one-flip scan with more samples.

Six recipes attain 30,698. Seed 25 chooses index `25 mod 6 = 1` in their
enumeration, giving root `j` order **`(1,2,3,0)`**, with just `(1,1)` reversed.
The certificate records all 96 results and exact DAG hashes. Together the
initial and final domains verify **265,619,200 integer coefficient positions**,
including forbidden zeros. There is no claim of optimality outside this
finite class. Point permutations, changed descendants and other h values
were excluded by the stopping rule.

## Exact map and physical admissibility

For source and target triples S,T, the desired coefficient is 1 if S and T
are disjoint and 0 otherwise. Each root channel is a tensor product of two
disjoint-subset maps; applying its factors in either order gives the same
integer map. Different j blocks contribute to different output cardinalities,
so permuting their construction order does not change output summation order.
It changes which decomposition is retained when a support is first interned,
and therefore can change the reachable DAG after pruning.

Every recipe checks acyclicity, disjoint additions, exact supports and output
coefficients, plus the actual reversible physical-slot embedding. The selected
circuit checks every physical frame transition in both orientations. The
inherited phase enclosure lemma applies to any disjoint-triple DAG: ancestor
and reachable-target ground unions are disjoint, supplying the same nested
source-line, coordinate and target-complement frames. Explicit residual bases
are additionally constructed at h=8 and h=10.

The separate `independent.py` imports no repository code. It uses a bottom-up
recurrence, tuple-indexed generic factor contractions and a separately written
support interner. Full output maps and exact node hashes agree for h22 original,
PR863 comparator, selected traversal and simultaneous-tie control, and the
selected h8/h10 variants. Independent implementation is AI-assisted evidence,
not independent human review or a formal proof of the multiplication theorem.

For the signed scalar invocation, the retained side and central maps satisfy
`J M C + D G = I`. Their coefficients on intersection size k are respectively
`1/2` for k=0, `-1/2` for k=2, zero otherwise, and `(k-1)/2` centrally.
The retained twelve-operation signed cancellation restores arbitrary dirty
helpers and sources while adding x to y; reversing signs gives its inverse.
All independent dirty source, target, side and centre columns are checked at
h8 in both directions. Eight dense dyadic h22 probes supplement that written
linear argument; they are not an all-column h22 proof.

Failure controls reject invalid recipes, changed coefficients, overlapping and
cyclic additions, missing source access, wrong injection sign and an omitted
mixer gate. Source bindings are checked on every replay.

## Complete historical cost

Before the larger traversal replay, the complete predecessor invoice was
priced. No extra adapter, source access, helper or recursive child is needed.
The compiled mixer count is checked against
`M=2c+2*choose(h,2)*LeaveOneCircuit(h-2).additions`, with `C=J=4v`.
All four mixer/inverse occurrences, access, injection and restoration cost
`4M+2C+4J+18v` per signed invocation. All `3v^2` tensor invocations are charged.

| Quantity | PR863 | New traversal |
|---|---:|---:|
| Disjoint additions c | 30,708 | 30,698 |
| Disjoint paid roles | 32,248 | 32,238 |
| Intersection-two roles | 17,094 | 17,094 |
| Total side roles | 49,342 | 49,332 |
| Centre roles | 23 | 23 |
| Mixer additions M | 86,364 | 86,344 |
| Source accesses C / injections J | 6,160 / 6,160 | 6,160 / 6,160 |
| Complete signed invocation bound | 410,136 | 410,056 |
| Three-stage scalar bound | 2,918,035,612,800 | 2,917,466,428,800 |
| W | 241,452,596,000 | 241,405,164,000 |
| s | 2,570,987,137,857,600 | 2,570,482,081,921,600 |

Here `v=1540`, `m=10648`, `L=3600088800`, and deficit `W*m-s=104350400`
stay fixed. Ten fewer roles reduce W by `2v^2*10=47432000`, s by
`2mv^2*10=505055936000`, and the complete scalar bound by
**`24v^2*10=569184000`**. Joins, the 23 centres, intersection-two helpers and
all recursive children remain charged. The certificate recomputes rational
saving enclosures, `E=64(W+m+1)^3`, positive scalar/node slack, `s<m^5`,
and the stopped recurrence `A(e)<=s A(e/m)+E`.

The current selected complex supplier binds its assembly, but this historical
supplier does not approach it. This result is useful as a concrete circuit
and reproducible sharing mechanism, with no proposed selected-bound change.

## Provenance and remaining obligations

`SOURCE-PINS.json` binds the 16 executable/proof/test inputs and records
selected-state context separately. Historical source:
`1a74950ce5074b848243ba89d8022fbadba66105`. PR863 comparator head:
`6c0ed3975fda8f0190b34f1b1bbedb33a925d339`. The complete adaptation and
contributor credits are recorded in `NOTICE.md`. `upstream/` is unchanged.

Uniform all-size compilation, common-label/mutable-source realization,
whole-call hosting, precision/tape and analytic transfer remain inherited
assumptions. Selected U8/T37 transport, hosted precision invoices and outer
assembly are not implemented here. No full repository replay, Lean proof,
hosted CI pass or measured multiplication runtime improvement is claimed.
