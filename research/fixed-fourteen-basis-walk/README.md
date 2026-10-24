# Sharp walk costs for the displayed fourteen-point difference basis

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with exact finite corroboration; no new kappa.** For the literal
six-source prefix set displayed in unpaidmoon's merged
[#4651](https://github.com/CrocSwap/integer-mult-bounds/pull/4651),

```text
P = {0,1,2,3,4,5,6,8,16,24,32,40,48,63},
```

the smallest possible maximum step weight of a fourteen-step closed walk is
four. Its minimum total number of source-map applications is twenty. Allowing
extra intermediate prefixes and arbitrarily many steps cannot lower twenty.
The fixed set therefore cannot match the generic six-source DUO construction's
sixteen source applications, even if arbitrary atomic source bundles are allowed.

This answers the displayed-witness first step of #4651 Open next question 1.
It does not exclude a different fourteen-point basis with steps of weight at
most three. Aaron Wang's #2128 already attains the generic `(140 queries,
142 map additions)` optimum established by Tairitsu-Aya's #2156. Those results
are cited premises, not replayed here. No new generic optimum is claimed.

## Contract

There are six immutable source rows `x_j`, a dirty connector `z`, and 63 dirty
target rows `y_m`, with arbitrary compatible binary linear maps `B_j,A_m`.
The required update is `y_m += A_m(sum_j m_j B_j x_j)`, with sources and
connector restored. The permitted new atomic source call has a nonempty mask S:

```text
B_S: z += sum_(j in S) B_j x_j.
```

It costs one root call and `|S|` source-map applications. An `A_m` readout
costs one root call and one output-map application. Outputs are read exactly
twice and are observed only after completion. No partial sums inside an atomic
call are observable. Every map application is charged, even within a bundle.
These are abstract query and application counts; physical implementation,
dispatch, source/coefficient access, frame changes and hosting are additional.

A source prefix q describes `z = z_initial + sum_j q_j B_j x_j`. A step from
u to v has mask `u XOR v`, hence application cost its Hamming weight. Two
readouts at prefixes u,v produce mask `u XOR v` and cancel connector dirt.
This is Ross Richardson's paired-readout reduction, used as a premise.

## Proof and attaining cycle

Every element of `P` other than 63 has Hamming weight at most two. Therefore
its distance from 63 is at least four. Any fourteen-edge cycle visiting P
has two edges incident to 63, each costing at least four. Its other twelve
edges join distinct points and cost at least one. Thus every such cycle has
maximum edge weight at least four and total application cost at least

```text
2*4 + 12*1 = 20.
```

Both bounds are attained simultaneously by

```text
0,16,48,32,40,8,24,63,5,4,6,2,3,1,0.
```

The two nonsingleton edges are `24 XOR 63 = 39` and `63 XOR 5 = 58`, both of
weight four. All other edges have weight one. The six source occurrence
counts are `(4,4,2,2,4,4)`, so the connector is restored. This proves the
sharp arity and application claims without an exhaustive tour census.

Now consider any finite closed walk visiting every point of P, with arbitrary
extra vertices, revisits, and step weights. Start at zero and retain the first
visit to each other required point, then the return to zero. Hamming distance
satisfies the triangle inequality, so replacing each intervening segment by a
single edge cannot increase its application bill. The resulting fourteen-edge
cycle visits exactly P and therefore costs at least twenty. The displayed
cycle proves equality for the larger walk class. The same lower bound holds
if only some readout boundaries are designated and extra boundaries are ignored.
This shortcut argument concerns application cost; it does not preserve an
arity restriction or root-call count.

## Complete paired-readout word and consequence

The verifier assigns each nonzero mask m the lexicographically first pair of
cycle boundaries with difference m. It puts the two `A_m` calls at those
boundaries. Its free-symbol replay checks all 63 endpoint identities, arbitrary
initial connector state and arbitrary initial target values. Linearity gives
the identity for all compatible source/output maps, including noncommuting
maps. The reverse query word is the inverse.

This costs fourteen source root calls and 126 output root calls, for
`140 root queries`. Twenty source applications and 126 output applications
give `146 map applications`. The sharp fixed-set application floor is four
above the inherited generic DUO bill of 142. Changing the order, adding
intermediate vertices or allowing higher-arity bundles cannot remove that
fixed-set penalty. A different prefix set, coordinate change, output contract
or root architecture is outside the theorem.

The decision is to stop optimizing this literal prefix set under the uniform
application tariff. The generic construction already has a lower bill.
This is a scoped obstruction to using this witness as the next construction,
not a new supplier or a universal barrier to six-source connectors.

## Reproduction and evidence

From the repository root, using the standard library and CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fixed-fourteen-basis-walk
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fixed-fourteen-basis-walk --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/fixed-fourteen-basis-walk/verify.py
```

The first and third commands also work with any installed CPython 3.12 path.
Expected direct marker:

```text
PASS_FIXED_FOURTEEN_BASIS_WALK arity=4 source_apps=20 root_queries=140 map_apps=146 dense_cases=840 controls=163
```

Normal and optimized registered commands regenerate and compare [RESULT.json](RESULT.json),
including five local file hashes. `--emit` writes the generated receipt to stdout.
A separately implemented Held--Karp recurrence over all subsets of the thirteen
nonzero terminals returns no arity-three tour and cost twenty at arities four
and six. Its finite-state counts are recorded in the receipt. It corroborates
the proof; the arbitrary-length claim rests on the written shortcut argument.

The literal word is also replayed forward and backward on every basis input of
70 dirty rows at dimensions one, two and three, for 840 cases. Controls reject
each of the 140 single-call omissions, all twenty omitted source components,
and three malformed cycles. No predecessor census is imported or rerun.
Independent human and formal proof-kernel review are unclaimed. Lean, Docker,
selected cold replay, physical bundle admission and complete multiplication
proof obligations are unrun and outside scope.

Python's managed allocation is a Power-of-Ten deviation. All domains are fixed:
the largest DP has 8,192 rows of thirteen costs, each transition loop has at
most thirteen iterations, and dense replay has at most 210 basis inputs per
dimension. There is no recursion, dynamic code generation or external process
in the verifier. ValueError checks remain active under optimized Python.

## Sources and overlap

Base canonical main is `624de9dc66858af0945e5f8a0942488d62280d43`, priority
revision 7. [TASK.json](TASK.json) records the refined card, evidence and stop
rule. [SOURCES.json](SOURCES.json) pins predecessor READMEs as historical
provenance. They are not replay inputs. The literal set above defines the new
problem. The selected record remains unchanged.

Live open PRs, active Discussions, latest handoffs, recent account submissions,
last-hour account posts, main-tree README searches and merged-term searches
were checked before claiming. The exact displayed set appeared only in #4651
in the main README search. The cached card scan covered 426 open PRs and 3,959
Discussion records, with complete remote pagination; 6,196 sparse local note
paths were omitted. That scan, arbitrary unsearched diffs and unpublished work
are limits on the overlap check, not a novelty certificate.
Claim: [handoff post](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134568).

Credit unpaidmoon #4651 for the literal basis and explicit next question;
Ross Richardson #934/#943 for the paired-readout interface; Aaron Wang #2128
for the generic DUO construction; Tairitsu-Aya #2156 for its generic optimum;
and Volodymyr Gavrylkiv for the known six-dimensional difference-basis value,
as credited in #2156. Cinna Davis #2201 retains the distinct one-Q4 profile
obstruction. No new priority is claimed for Hamming shortcutting or Held--Karp.
The new result is the sharp routing cost and its consequence for this literal set.

## Open next questions

- Can an explicitly priced coordinate change make this same abstract basis
  competitive? First name its source acquisition and restoration program and
  charge every application and conversion. A free coordinate change is not
  covered by the literal-coordinate theorem, and no such paid program is supplied.
- For a caller with unequal source prices, can this set beat another basis
  after all root costs are included? First supply an actual caller and complete
  tariff table. The unit-application result alone does not settle that comparison.
