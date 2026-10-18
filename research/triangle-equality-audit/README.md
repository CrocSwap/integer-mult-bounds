# Equality cases and raw observations in rational triangle recovery

**Scoped mathematical audit; no new kappa.** The sharp deletion theorem in
[Sagar Thakrar's PR1284](https://github.com/CrocSwap/integer-mult-bounds/pull/1284)
is correct. This note classifies **all its minimizers**, including six additional
`p=4` minimizers with a `K3,3` attachment, and proves their exact raw-observation
requirements. PR1284 did not claim uniqueness; this is an extension, not a
counterexample to its theorem.

Let `G=K_(2p)` minus the matching `01,23,...`, over any field of characteristic
other than two, with arbitrary edge inputs. Fix the target triangle on
`a,b,c=0,2,4`; matching automorphisms cover every target triangle. Retain its
three edges and delete only nontarget edges. An available raw observation is
the **sum of all retained edge inputs incident to one vertex**. Recovery means
exact recovery for every input, including by arbitrary nonlinear processing.
A deletion removes an input from the allowed family; it is not a free correction.

| Port pairs | Minimum deletions (PR1284) | All labeled optimal retained graphs | Minimum raw observations |
| --- | ---: | --- | ---: |
| `p=3` | 5 | Three: one root attached to `K2,2`, the other roots isolated in the nontarget graph | 6 each |
| `p=4` | 12 | One isolated triangle plus its full induced complement; six rooted `K3,3` attachments | 3 for the isolated case; 8 for each attachment |
| Every `p>=5` | `6p-12` | Unique: isolated triangle plus its full induced complement | 3 |

Counts fix the labeled graph and the target triangle. They are not counts up
to graph isomorphism. Deletion optimality therefore does **not** determine
observation cost at `p=4`. There is no additional minimum-deletion versus
observation-count Pareto benefit there: the isolated minimizer has the same
12 deletions and fewer observations.

## Reproduction and evidence

From the repository root, Python 3.12, standard library only:

```sh
python3.12 scripts/research_package.py --package research/triangle-equality-audit
```

Expected final markers: `PASS_TRIANGLE_EQUALITY_AUDIT`,
`PASS_TRIANGLE_EQUALITY_TESTS`, and
`PASS_REGISTERED_RESEARCH_PACKAGE research/triangle-equality-audit outcome=completed`.
Direct replay: `python3 -I -O -B research/triangle-equality-audit/verify.py`.
`--emit` emits a newly computed receipt; `--certificate PATH` checks another
receipt. Checks do not use Python assertions.

The finite census tests **every** graph with the threshold edge count:
`binom(9,4)=126` at `p=3`, and `binom(21,9)=293930` at `p=4`. For each graph,
the rooted-component criterion is checked against independent ordinary
Gaussian column elimination over `F3`. No seven-class reduction or predecessor
code is imported. The rank test is `rank(H)=rank(J)+3`, where columns are
signless incidence vectors and `J` omits the three targets. This says that
those columns are independent modulo the nontarget column space, exactly the
kernel criterion for recovering all three coordinates.

All 1,984 raw-observation subsets of the ten minimizers are separately tested
by **rational observation-row elimination** and modular column elimination.
Additional controls reject all 99 single deleted-edge restorations, 69 omissions
of necessary observations, ten characteristic-two fixtures, and three
insufficient two-observation examples. The 3,906 second-difference checks for
`3<=p<=64` use the OS assignment seed 64 as the diagnostic endpoint; they are
supporting arithmetic evidence, not the all-p proof. The census checks only
the optimum edge count; the written bound below excludes denser graphs.

[CERTIFICATE.json](CERTIFICATE.json) lists every small minimizer and its
required observations. [test_package.py](test_package.py) adds direct failure
controls for the tempting `p=4` uniqueness inference and for omitting the
matching restriction, plus source/receipt mutations and a minimal read-only
relocation. All engines were written in this one AI-assisted session; this is
not separate human or proof-assistant verification.

## Proof

### Recovery and the relevant component

We recall and credit PR1284's characteristic-not-two argument. A linear
coordinate recoverable from a linear observation map, even nonlinearly, must
vanish on its kernel, hence belong to its row space. For the three decoder
rows, collect their coefficients at vertex `v` in `c_v`. The target equations
force

```
c_a=(1,1,-1)/2, c_b=(1,-1,1)/2, c_c=(-1,1,1)/2.
```

Every retained nontarget edge `uv` forces `c_u=-c_v`. Thus each component of
`J=H-targets` containing a root must be bipartite and contain exactly one
root: an odd cycle forces zero, and two roots have coefficients neither equal
nor opposite. Conversely, alternating each root vector on its bipartite
component and assigning zero elsewhere is an exact decoder. In characteristic
two, adding the same nonzero value to all three target edges gives a kernel
vector, so none of these recoveries is possible.

The union `C` of those three rooted components, with the three triangle edges,
is connected and nonbipartite. Its signless incidence rows are independent:
a dependence assigns coefficients alternating across each edge, and the
triangle forces zero, which propagates throughout `C`. Thus the decoder
coefficients on `C` are unique; all three coefficients at every vertex are
`+1/2` or `-1/2`, hence nonzero. Every raw observation on `C` is necessary,
even to recover any one target. Observations outside `C` have disjoint edge
support and cannot replace one of them. Conversely the alternating decoder
uses only observations on `C`. Therefore the **exact minimum set of raw
observations is the vertex set of C**, for every recoverable retained graph,
not just the optimum cases. No precomputed combinations are granted.

### The retained-edge bound, and its equality conditions

Following PR1284, write rooted component sizes as `s1,s2,s3>=1`, and let `b`
be the number of other vertices. Set

```
h(s)=floor(s^2/4), f(b)=binom(b,2)-max(0,b-p).
```

A rooted bipartite component has at most `h(s)` edges. The residual vertices
contain at least `max(0,b-p)` whole matched pairs, so at most `f(b)` edges.
There are no nontarget edges joining these parts. Concentrating the rooted
sizes, using nondecreasing forward differences of `h`, gives

```
|E(H)| <= 3 + h(s1)+h(s2)+h(s3)+f(b)
       <= 3 + h(2p-b-2)+f(b) = U_p(b),  0<=b<=2p-3.
```

Both terms in `U_p(b)` are convex integer sequences; the differences of `f`
are `b-1[b>=p]`, also nondecreasing. Consequently every interior value lies
below or on the chord between the endpoints. Those endpoints are

```
U_p(0)=(p-1)^2+3,
U_p(2p-3)=2p^2-8p+12,
U_p(2p-3)-U_p(0)=(p-2)(p-4).
```

For `p>=5`, the second endpoint is strictly larger. Every other `b` is
strictly below it by the chord bound. Equality therefore forces `b=2p-3`
and `s1=s2=s3=1`. All allowed residual edges must be present. This is exactly
the unique isolated-triangle graph and proves rigidity for every `p>=5`.

For `p=3`, the first endpoint is strictly larger, so `b=0`. The rooted sizes
sum to six. Their sorted possibilities have `sum h(si)` equal to 4 only at
`(4,1,1)`; the other partitions `(3,2,1)` and `(2,2,2)` give 3. Equality
requires the size-four component to be the complete balanced `K2,2`.
Its root and its mate must occupy one side, and the other two vertices the
other side. There is exactly one choice for each of the three roots: three
minimizers, all with `|C|=6`.

For `p=4`, the endpoint tie is real. The full sequence is

```
b:       0  1  2  3  4  5
U_4(b): 12  9  8  8 10 12.
```

Only `b=0` and `b=5` can attain twelve edges. The latter is the isolated
triangle. At `b=0`, the rooted sizes sum to eight; their sorted possibilities
are `(6,1,1),(5,2,1),(4,3,1),(4,2,2),(3,3,2)`, with `sum h(si)` respectively
`9,7,6,6,5`. Thus equality forces a complete `K3,3` component and two singleton
roots. Choose its root `a` in three ways. In that six-vertex component there
are two complete matched pairs: `a,a'` and the unused fourth pair `d,d'`.
Each pair must lie entirely on one side of the bipartition; the two pairs
cannot lie on the same side of size three. The remaining vertices `b',c'`
must split, one per side. This gives exactly two choices for each root,
hence six attachments, all with `|C|=8`.

An explicit attachment has bipartition `{0,1,3}|{5,6,7}` and isolated roots
`2,4` in `J`. Its nine crossing edges plus `02,04,24` are legal and total
12. It is a concrete counterexample to **extending the p>=5 uniqueness
conclusion to p=4**, not to PR1284's deletion theorem.

## A complete example invoice, not a scalar lower bound

Use PR1284's abstract scalar alphabet: immutable edge sources, dirty output
and helper registers, signed unit ADD, and SCALE by `2` or `1/2`, each at unit
cost. For one helper per required raw observation, use its exact echo

```
H += A X; D += B H; H -= A X; D -= B H.
```

`A` is the raw vertex-incidence map. Every nonzero decoder entry of `B` is
`+1/2` or `-1/2`; each decode scales all active helpers by one half, adds to
all three outputs with the prescribed signs, and doubles the helpers back.
Every source read, both gathers, both decodes, all scales and full dirty
restoration are charged. There are no free COPYs, frame changes, or recursive
children **in this abstract model**; it is not a physical supplier invoice.

| p=4 optimum | Helpers | Source ADDs | Output ADDs | SCALEs | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Isolated triangle | 3 | 12 | 18 | 12 | 42 |
| K3,3 attachment | 8 | 48 | 48 | 32 | 128 |

The checker executes all basis columns of the literal words, including dirty
helpers, outputs and ignored residual inputs, and rejects every one of their
170 single-instruction omissions. These prices establish two explicit
implementations, **not** minimum circuit costs. Direct target access costs
three ADDs in this alphabet. No scalar speedup, physical copied-information
rank, supplier improvement or kappa follows from the graph theorem.

## Provenance and scope

Exact base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The live overlap scan at
selection covered all 803 open PR bodies and 22 Discussion records with their
returned comments; nearest scope is PR1284. The final paginated refresh at
22:35 UTC covered 807 open PRs, 61 Discussion records (threads/comments),
and 327 local records, with no warnings; only PR1284 and this claim matched. Seed **64**, original donor's
adversarial-audit track. The three candidates and bounded stopping rule are
recorded in TASK.json. This is a side result about an abstract changed-field
observation contract, not a discharged selected-supplier transfer obligation.

Credit **Sagar Thakrar (@thakrarsagar), PR1284**, for the rational recovery
criterion, sharp deletion bound, convex bound and echo; this note adds their
equality analysis and the exact observation-set consequence. The reviewed
predecessor head and document hashes are in [PREDECESSOR.json](PREDECESSOR.json).
Credit **woklerx, PR966**, for the prescribed binary triple and paired-port
model, **Sam Sung / the-missionary-company, PR669**, **Joel Pulikkan /
GamingPuzzled, PR231**, and **icekylinx/eumemic**. No literature priority claim
is made for incidence-matrix facts. SOURCES.json pins the retained binary
proof and selected context; no pending-PR code or theorem is needed at replay.

## Open next questions

- Can a native geometry gather only the three required combinations more
  cheaply than the full eight-observation interface? First specify the
  geometry and price source access, deleted-input correction, realization,
  and restoration for the displayed p=4 fixture. Blocker: raw observation
  count is not a physical copy-rank or circuit-cost theorem.
- For a different prescribed target graph with rational observations, do
  deletion minimizers have a similar observation-cost split? First derive
  the exact target coefficient constraints. Blocker: the triangle's forced
  nonzero coefficient vectors need not persist for another target graph.

The selected frontier, all supplier sources and `upstream/` are unchanged.
The existing all-size/compiler, common-label, mutable-source, whole-call
hosting, precision/tape, bit H1-H5 and analytic assumptions remain. Full
supplier replay, hosted CI success and proof-assistant verification are not
claimed. Prepared for **Philipp (@mightyOil)** with substantial **OpenAI Codex
GPT-6 Astra** assistance in mathematics, implementation, checking and writing.
Apache-2.0; no independent human review is claimed.
