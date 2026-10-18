# Exact dirty-boundary costs with partial output observations

**Finite interface certificate; no new supplier or kappa.** In the model below,
observing only part of the output first lowers the optimal adapter cost at
three fixed calls. Among all 4,808 instances of lengths one through three,
100 have a strict saving over observing both outputs at every cut. The largest
gap is **one versus three paid XOR adapters**, with an exact dirty-state witness.
Every improving instance has one output with zero net final update. Among the
1,824 instances with nonzero final updates to both outputs, there is no saving
from weakening the observations in this domain.

This answers a finite optimization question excluded by the earlier
[fully restored cut planner](../reader-restoration-cuts-seed53/README.md).
It does not repair an error in that planner. The result distinguishes an
observation boundary from a requirement to restore the entire state there.
The claim is in [discussion #2007](https://github.com/CrocSwap/integer-mult-bounds/discussions/2007).

## Exact model and comparators

There are four distinct binary coordinates `(d0,d1,w0,w1)`, all arbitrarily
dirty. A fixed child, indexed by `(o,s,t)` in `{0,1}^3`, performs in this order:

```
d[o] ^= w[s]
w[t] ^= w[1-t]
```

Equivalently, `C(B,G):(D,W) -> (D+B W, G W)`, where B is one of four elementary
two-by-two matrices and G is either elementary workspace shear. These two G's
do not commute. The eager reference immediately reverses each child's workspace
shear; its data increment after i children is `(sum_{j<=i} B_j) W_initial`.

An adapter is exactly one of six scalar XORs: the two workspace shears, or
`d[o] ^= w[s]` for any o,s. Every adapter costs one, including entry preparation,
correction and final restoration. Arbitrary finite words of adapters are allowed
before the first child and after each child, but **never inside a child**.
There are no output-to-workspace gates, output-to-output gates, extra registers,
copies, erasures, free relabelings, or clean-input assumptions.

After all adapters at each interior cut, a mask 1, 2 or 3 observes respectively
`d0`, `d1` or both. Only those rows must equal the eager reference at that cut.
The observer does not change the state or choose subsequent children. There are
no observers inside an adapter word. At the final cut, **all four coordinates**
must equal eager execution, including both incoming workspace values.
Future output rows may be prewritten while they are unobserved.

The main comparison changes only these observation masks. The full-observation
optimizer has the same six adapters and may also carry noncanonical workspace;
it must present both correct data rows at every cut. A second, narrower comparator
enumerates every contiguous partition, with no entry adapters or output repair.
At each chosen cut it requires correct data and restores workspace by a shortest
word in the two workspace shears. It also checks any prescribed observations
inside an uncut interval. This is the exact two-by-two matrix analogue of a
fully restored partition plan, not a claim about the earlier diagonal fixture.

Fixed children cost two XORs each. The complete cost **in this declared scalar
model** is therefore `2*n + minimum_adapter_cost`. Other gate alphabets and
ways to replace, split or skip a child are outside this optimum.

## A sharp noncommuting three-call witness

Choose children `(0,0,0), (1,0,1), (1,0,0)` and masks `(3,1,3)`.
Only the second cut hides `d1`. Insert the single adapter `w1 ^= w0` after
the first child. With arbitrary initial `(d0,d1,w0,w1)=(x,y,a,b)`:

| Completed boundary | Candidate state | Eager data required there |
| --- | --- | --- |
| Child 1 and adapter | `(x+a, y, a+b, a)` | both: `(x+a,y)` |
| Child 2 | `(x+a, y+a+b, a+b, b)` | only `d0=x+a` |
| Child 3 | `(x+a, y, a, b)` | all four coordinates |

All sums are in characteristic two. This works on arbitrary dirty bit streams
coordinatewise, without allocating a temporary. The eager reference uses three
restoring XORs, and even the more general full-observation optimizer needs three.
The complete fixed-call bills are seven and nine XORs: fourteen versus eighteen
scalar data reads and seven versus nine writes, with the same four stored scalars.
The single adapter can also be placed after child 2; these are the only two
one-adapter words in this fixture. It is not an eager return at either location.

Here is a direct proof of the sharp costs, separate from the census. Write U
for `w0 ^= w1` and L for `w1 ^= w0`. With no adapter, workspace ends at ULU,
not I, so at least one adapter is necessary. The displayed word attains one.
Each workspace shear is an odd permutation of the three nonzero binary vectors.
The three child shears have odd product. Thus any restoring program uses an
odd number of workspace adapters. A program with at most two adapters must use
exactly one workspace adapter, and at most one data adapter. Checking its four
possible boundary positions, the workspace adapter must be L between child 1
and child 2, or between child 2 and child 3. Both choices already give the correct
final data, but their second-cut `d1` differs from eager by b. A single data
adapter adds a nonzero row of the current invertible workspace matrix to one
output; that contribution persists to the final output because no operation
reads D into workspace or mixes outputs. It cannot fix the intermediate error
while retaining the final endpoint. Hence full observation needs at least three
adapters; eager execution attains three. Literal enumeration rejects all 385
boundary words of length at most two under full observation.

The unchanged final `d1` is material, not hidden. If these toy children may be
opened or replaced, their overall endpoint is simply `d0 ^= w0`; the fixed-call
bill is not an unrestricted circuit optimum or a new multiplication algorithm.

## Why the finite search proves the stated minima

Every permitted prefix has the unique form

```
W = P W_initial,      D = D_initial + Q W_initial,
P in GL_2(F2),        Q in Mat_2(F2).
```

There are exactly `6*16=96` states. The representation is faithful on all dirty
inputs: the full four-by-four matrix is `[[I,Q],[0,P]]`. Each of the six adapter
edges updates exactly this matrix. Every allowable word is a path in this graph,
and every path is an allowed word. Nonnegative unit costs mean cycles can be
removed, so no length cutoff on adapter words is needed.

Starting at `(I,0)`, the primary solver computes a shortest adapter closure,
applies the next fixed child, computes another closure, and removes states with
incorrect observed rows. Induction on the child index shows its labels are
exactly the minimum costs for all admissible prefixes. Requiring `(I,sum B_i)`
at the final cut proves the claimed minimum and supplies an attaining word.

A separately written engine instead uses literal four-by-four bit matrices and
a chronological layered graph. Adapter edges cost one; mandatory child edges
cost zero after subtracting the common fixed-child bill. It checks observations
before advancing to the next child and runs 0-1 BFS. It does not use the primary
state encoding, generator table, shortest-word routine or optimizer. Both
engines agree on every instance. A second literal enumeration independently
checks every restored-partition price. All 4,808 primary attaining words are
replayed on all 16 dirty Boolean inputs, for **76,928 complete executions**.

The instance count is
`8 + 8^2*3 + 8^3*3^2 = 4,808`.
There is no quotienting by symmetry, seed selection, random sampling, tolerance
or floating arithmetic. The complete cost census is:

| Children | Partial min | Full-observation min | Partition min | Instances |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 1 | 1 | 8 |
| 2 | 0 | 0 | 0 | 48 |
| 2 | 1 | 1 | 2 | 48 |
| 2 | 2 | 2 | 2 | 96 |
| 3 | 1 | 1 | 1 | 2,016 |
| 3 | 1 | 1 | 3 | 288 |
| 3 | 1 | 2 | 3 | 52 |
| 3 | 1 | 3 | 3 | 48 |
| 3 | 2 | 2 | 3 | 1,964 |
| 3 | 3 | 3 | 3 | 240 |

Thus 100 instances improve specifically because of partial observations, of
which 48 use both noncommuting workspace shears. There are separately 2,400
improvements over the restricted partition comparator. Those larger counts
must not be attributed solely to weakening observations.

[RESULT.json](RESULT.json) records these counts, the witness, a canonical hash
of every cost row, a separate hash of all attaining words, source checks and
controls. Hashes compact the receipts; the verifier recomputes the mathematics.
Ten failure controls address omitted/wrong/moved adapters, newly observed output,
unpaid work, data-correct but workspace-wrong endpoints, changed readers and
invalid declared boundaries. The zero-workspace false positive demonstrates why
clean-only testing would miss an error. All checks remain enabled with `-O`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -O -B research/partial-observation-boundaries/verify.py
python3 scripts/research_package.py --package research/partial-observation-boundaries --check-only
python3 scripts/research_package.py --package research/partial-observation-boundaries
```

Expected main line:

```
PASS_PARTIAL_OBSERVATION_BOUNDARIES instances=4808 states=96 partial_gains=100 productive_gains=0 dirty_inputs=76928 controls=10 no_new_kappa
```

Normal replay is read-only. `--write-result NEW_PATH` creates a fresh receipt
exclusively; it does not overwrite one. The registered replay also authenticates
historical catalogue/selected-record provenance and every declared live source.
Four package-integrity tests exercise real source/receipt corruption, refusal
to overwrite an existing result, and optimized read-only relocation from an
empty working directory.

## Scope, provenance and credit

Base: `1ff9c501b624ec354e1330b1b9be571a6adba9cb`. Chooser nonce:
`86e84927a2ed518696c231e449d50f59`; revision 3; recursive-interfaces;
`persistent-boundary`, scope key `73c0a233e7e1abdccbfe`. [TASK.json](TASK.json)
declares a **changed** scope: this is a finite abstract replacement interface,
not a selected-supplier call pair. It prices a precise checkpoint relaxation
with noncommuting workspace maps, rather than asserting a recursive saving.
[SOURCES.json](SOURCES.json) pins the predecessor notes by base, Git blob and
SHA256; no predecessor solver is imported or frozen package modified.

Credit Aaron Wang/Navinor's PR1155 for restoration coalescing, Adam Gall's
`observer-safe-restoration` for the exact terminal/prefix defect criterion, and
Sagar Thakrar's `reader-restoration-cuts-seed53` for the fully restored interval
planner. These remain valid in their declared domains. The extra contribution
here is the observation-constrained 96-state optimum, its complete small-domain
census, sharp witness and independently implemented checks. No priority is
claimed for linear cancellation, shortest paths or dynamic programming.

Nearby PR1930 (Cinna Davis), head `11cb2266f7e99279c440a301ea4b862587a9afa2`,
uses output-to-source prefix chains, a different contract. PR1155's contextual
head at entry was `d7d50406fbdc7ac4141ba454b2e2440dc74942db`; neither pending PR
is an implementation dependency. This account's PR1414/1491/1495/1496 concern
paid coordinate-address calls in formal group algebras; the present gates are
scalar boundary XORs and those address-call results are not repeated.

No source-level selected caller, recursive rank profile, physical instruction
dispatch or routing tariff, hosting, precision/tape, contracting recurrence,
selected cold replay, Lean theorem or multiplication-exponent improvement is
established. A bitstream implementation multiplies payload XOR/read/write counts
by its length but still must pay and validate control, transport and hosting.
No complex kappa claim is made, so the incumbent packing-cap calculator is not
being applied to this different interface model.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New work is Apache-2.0. Source attribution and licenses are retained. Independent
implementation checks are not independent human review.

## Open next questions

- Does a specified admitted supplier contain a mandatory call chain with this
  observation pattern and noncanonical workspace contract? Map an actual pair
  or triple of complete call boundaries to the model and charge every adapter,
  owner, frame and transport obligation. The missing source-bound caller and
  permission to hide the intermediate output are the blockers to adoption.
- At four calls, can partial observations lower cost when both final output
  update rows are nonzero? The same 96-state solvers can exhaust the 110,592
  length-four instances. This would test the exact boundary of the negative
  three-call census; it is outside the present registered domain, and a positive
  toy result would still need the physical binding above.
