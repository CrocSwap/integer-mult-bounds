# Independent mathematical and finite audit

**Outcome: PASS for the exact contract and finite domains stated below.**
The written proof has no identified material gap. The independently implemented
finite checker agrees with the forest optimum on every tested complete-tariff
assignment. This is an automated specialist review with a written derivation,
not independent human review, formal-kernel verification, hosted CI, a measured
physical supplier or a new kappa claim.

Reviewer: OpenAI Codex, GPT-6.1 Sol Max, assisting Ross Richardson.
Standard speed was configured; the runtime server tier was unobserved.
Run `trial-continuation-20261017T031528Z`; shared worktree base
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`.
The reviewer owns only this file and `independent.py`, imported no primary or
predecessor executable code, and did not mutate Git, the owner clock or Goal.

## Exact reviewed sources

SHA-256 pins at review:

| File | SHA-256 |
| --- | --- |
| `PROOF.md` | `1c73b56222dbd63a2230a23c00ce4b822eaa3aa7cdd4c5d6ba9975b98857b289` |
| `verify.py` | `21eaa12b3fcdb7470b89faaa4f5bccd5aeeaeca2ace5052b67e5a292bb18ee63` |
| `cut_check.py` | `ebf40d332d32b6da13c227dc6896368c6b8f33b6bd041e0870302a0ba5b54d27` |
| `README.md` | `dae5277016949f17bc55191e34a5f9470475b94ed679c843217973711ce2a341` |
| `independent.py` | `844e4728441bea5d8874012ca570cb2dc77e5ab9beeb5a2b421ec1a57a4367a9` |
| predecessor `research/dirty-anchor-tradeoff/PROOF.md` | `ba2fd83c22f57bd7658550067c9da4331fa84c22f8fa611eb0717bceac03f764` |

The predecessor is identified as PR3063 head
`3f384b8b7daccb2c8e12013fd81a738202ce0f8d`. It explicitly excludes
source-dependent ADD prices. Its destination-only theorem is used only in its
original model. The earlier external written audit is retained in the run's
`independent-cut-review.md`; the present finite implementation was completed
before reading the primary verifier's implementation.

## Written proof review

The model is a finite fixed straight-line word on exactly q independent dirty
rows over F2^w, with arbitrary independent common p. Complete P calls preserve
their disjoint read-only sources, and ADD(dst,src) has its directed stationary
price c_dst,src. Every output must retain its own dirt exactly. No extra row,
free transformation, observation, adaptive choice or hidden private symbol is
allowed. Finite positive prices are essential premises of the stated cost model.

The oracle-free subset argument is sound. Zero incoming ADDs cannot create the
required common coefficient. For exactly one incoming ADD, specialize p and all
private symbols to zero: every full dirt prefix remains invertible, so an outside
source row is outside the entire current S-row span. Outgoing feedback cannot
break that fact. The incoming gate changes that span and subsequent internal
ADDs cannot restore the original coordinate span. The proof correctly separates
this dirt projection from the arbitrary-p argument.

In the finite ADD-occurrence multigraph, these cut inequalities are precisely
the hypotheses of the prescribed-root Edmonds theorem for the repeated root
sets O,O. Parallel occurrences are distinct arcs. Two occurrence-disjoint
branchings each cost at least the cheapest forest rooted exactly at O, giving
the complete ADD lower bound 2 f(O). At least one paid P occurs on every actual
P destination, while positive extra multiplicities cannot reduce the bill.
Independent private symbols require their own calls, so their separate fixed
bill is valid even with arbitrary interleaving.

The children-before-parents preparation and literal reverse pass attain the
bound with exact dirt preservation. Reversing the order really can fail on a
chain; it is not an innocuous scheduling convention. The augmented graph-only
super-root reduction is a correct optimizer identity, without creating a
physical helper.

The graph theorem was checked directly in Attila Joo,
[Edmonds' Branching Theorem in Digraphs without Forward-infinite Paths](https://arxiv.org/pdf/1705.00471),
printed pp. 1-2: finite prescribed root sets are permitted, and the multigraph
convention admits parallel arcs. Its mathematical truth remains an external
dependency, rather than a consequence of these finite checks.

## Independent finite method and complete coverage

Each state is a tuple of q bit masks, one row of coefficients for each output.
The low q bits encode all original dirt symbols and bit q encodes p. Thus the
target is exactly `(e_i+p)_i`, not merely a desired common-value vector. The
generator alphabet is every P_i followed by every directed ADD(dst,src).

Breadth-first closure constructs the full finite coefficient-state Cayley
graph. A separate exhaustive enumeration of binary matrices uses the direct
Leibniz determinant modulo two, then attaches every p-coefficient vector.
These two state sets must agree exactly, independently of the expected counts.
Dijkstra settles the entire graph for every price assignment and allows all
finite word lengths, arbitrary multiplicities, feedback and cancellation.

Separately, enumerate every parent function, reject all rootless cycles and
retain exactly the directed rooted forests. No primary optimizer is imported.
Compute their minimum declared complete bill and compare it with unrestricted
Dijkstra on every tariff assignment.

| q | Actual GL size | Actual affine states | Generators | Price assignments | Rooted forests |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 2 | 1 | 2 | 1 |
| 2 | 6 | 24 | 4 | 16 | 3 |
| 3 | 168 | 1344 | 9 | 512 | 16 |

Every oracle price independently ranges over **{1,7}**; every directed ADD
price independently ranges over **{1,3}**. All **530** unrestricted optima equal
the independently computed forest optimum. Of these, **460** are strictly
cheaper than all-direct calls: 12 at q=2 and 448 at q=3. Exactly **192** q=3
cases require mixed root counts (strictly between one root and all roots);
there is no alternative optimal single-root or all-root forest in those cases.
All **20** enumerated forest echo words also have the exact full affine target,
one P per root and two occurrences of each directed forest edge.

The graph size check concerns finite q<=3. Because the coefficient maps act
coordinatewise, these same fixed-word identities hold for every width w>=1
within this exact XOR alphabet. Exhaustion over private-oracle words, q>3,
arbitrary real tariffs, other alphabets or physical implementations is not
claimed. The all-parameter cost theorem instead uses the written proof.

## Defect-sensitive controls

* A one-wave P_0 followed by fanout has common coefficient one everywhere but
  dirt rows `(1,3,5)` instead of `(1,2,4)`. It is rejected by the full endpoint.
* Parent-first chain preparation restores dirt but gives common coefficients
  `(1,1,0)`, so the deepest output is wrong and the word is rejected.
* The disconnected parent function `(None,2,1)` has a root and one incoming edge
  per nonroot, but includes a cycle. With its cheap cycle prices the invalid
  relaxation costs 5, whereas the genuine forest and unrestricted optimum are
  both 103. The parent function is rejected.
* Transposing the directed price lookup changes the chain problem's optimum
  from 5 to 103. Both graph and forest optima for the wrong model are checked,
  showing that agreement within the wrong direction convention is insufficient.

For mu=(1,100,100), c_10=c_21=1 and all other directed ADD prices 100,
unrestricted Dijkstra confirms the exact chain optimum **5**, versus best
single-root star **203**, best multi-root height-one forest **103**, and all
direct calls **201**. The actual five-gate chain word is also checked symbolically.

## Execution evidence and historical correction

Final execution used Python 3.14.6, standard library only, with all checks active
under `-O`. The actual child command was

```text
python3 -O /Users/ross/git/math/worktrees/trial-continuation-20261017T031528Z/research/dirty-anchor-edge-tariffs/independent.py --output /Users/ross/git/math/.research-automation/runs/trial-continuation-20261017T031528Z/independent-final.json
```

It was launched through `subprocess.run(..., check=True, timeout=120)` using
the same Python interpreter, completed successfully in approximately 0.53 s,
and wrote the absent output exclusively. Without `--output`, the checker emits
deterministic JSON and writes no result file. No Python `assert` is used.

Final result SHA-256:
`9d139d8aa6bc8ec2d3c5f98875f471f5f06cdb6aba518afa7247179203851c3c`.
The complete per-tariff comparison-row digest is
`536be170fd404ed540e606ae9dd6aaa9fc9942a1fd07f189042230ce4d37df61`.

An initial {1,2} cube passed but was identified as weak before submission:
mu_i<=2<=2*c_ij permits the all-direct endpoint to attain every optimum.
That cube was replaced by the stronger independent price axes above. Its
historical output remains unchanged at the external `independent-first.json`,
SHA-256 `c87b9ea75f233033e84eac9f436f4d0acefc89cf9c1c8763eb784b32b683b0cf`;
it records the earlier source hash
`72caeaed5dcf3c694d84ff799937110d8c0182d1346fffd92747472fcd0d9f7a`.
It must not be presented as execution of the strengthened final checker.

The primary PROOF.md, README.md, verify.py and its imported cut_check.py were
inspected at the hashes above. Their stated construction, source direction,
private-symbol handling, finite scopes and controls agree with this audit. The
final primary verifier serializes the full cut result to a temporary boundary
and calls the original `control_result`, retaining the original four defect
controls as well as its six semantic/pricing controls. The README's primary
coverage counts agree with the declared loops; the cut crossing count also
agrees with the preserving-subspace matrix count (4+288+46080=46372).
The reviewer did not independently rerun the primary verifier: its execution
remains the owner's separate validation obligation. Any material change to a
reviewed file requires renewed review of the affected claims and checks.

## Remaining mathematical implications

No material proof or checker issue remains within the declared scope. Binding
the complete directed tariffs to a legal recursive caller still requires actual
source access, routing, frames, precision, scratch and head-return costs, and any
outer moment or kappa comparison needs the full recursive accounting. This
abstract tariff optimum alone establishes none of those physical obligations.
